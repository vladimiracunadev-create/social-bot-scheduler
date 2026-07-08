//! ================================================================================================
//! EMISOR ZIG (Case 18: Zig -> n8n -> Crystal (Kemal) + Neo4j)
//! ================================================================================================
//! Zig es un lenguaje de sistemas sin recolector de basura, con gestión de memoria explícita. Este
//! emisor lee posts.json, y reenvía los posts no publicados al webhook de n8n usando el cliente HTTP
//! de la stdlib (`std.http.Client.fetch`, API de alto nivel de Zig 0.13). Modo dry-run si no hay
//! WEBHOOK_URL.

const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();

    const webhook: ?[]const u8 = std.process.getEnvVarOwned(alloc, "WEBHOOK_URL") catch null;
    defer if (webhook) |w| alloc.free(w);

    const raw = try std.fs.cwd().readFileAlloc(alloc, "posts.json", 1 << 20);
    defer alloc.free(raw);

    const parsed = try std.json.parseFromSlice(std.json.Value, alloc, raw, .{});
    defer parsed.deinit();

    var client = std.http.Client{ .allocator = alloc };
    defer client.deinit();

    for (parsed.value.array.items) |post| {
        const obj = post.object;

        const published = if (obj.get("published")) |p|
            (p == .bool and p.bool)
        else
            false;
        if (published) continue;

        const id = obj.get("id").?.string;
        const text = obj.get("text").?.string;
        const channel = if (obj.get("channel")) |c| c.string else "default";
        const scheduled = if (obj.get("scheduled_at")) |s| s.string else "";

        if (webhook == null) {
            std.debug.print("[DRY-RUN] Post {s} reenviado.\n", .{id});
            continue;
        }

        var body = std.ArrayList(u8).init(alloc);
        defer body.deinit();
        try std.json.stringify(.{
            .id = id,
            .text = text,
            .channel = channel,
            .scheduled_at = scheduled,
        }, .{}, body.writer());

        const res = client.fetch(.{
            .method = .POST,
            .location = .{ .url = webhook.? },
            .headers = .{ .content_type = .{ .override = "application/json" } },
            .payload = body.items,
        }) catch |err| {
            std.debug.print("[ERROR] Fallo reenviando {s}: {any}\n", .{ id, err });
            continue;
        };

        if (@intFromEnum(res.status) >= 200 and @intFromEnum(res.status) < 300) {
            std.debug.print("[OK] Post {s} aceptado por n8n ({d}).\n", .{ id, @intFromEnum(res.status) });
        } else {
            std.debug.print("[ERROR] n8n respondió {d} para {s}.\n", .{ @intFromEnum(res.status), id });
        }
    }
}
