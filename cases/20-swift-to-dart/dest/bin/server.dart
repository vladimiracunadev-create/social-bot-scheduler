// ==================================================================================================
// RECEPTOR DART/SHELF (Case 20: Swift Vapor -> n8n -> Dart Shelf + Firebase/Firestore emulator)
// ==================================================================================================
// Dart no solo es Flutter: con Shelf es un backend server-side compilado a binario nativo (AOT).
// La persistencia es el **emulador de Firestore** de la Firebase Emulator Suite, accedido por su
// API REST v1 (documentos con "fields" tipados). Colección: social_posts.
//
// Cumple el contrato REST homogéneo del laboratorio: /webhook, /errors, /logs, /health, /.

import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as shelf_io;
import 'package:shelf_router/shelf_router.dart';

final String emuHost =
    Platform.environment['FIRESTORE_HOST'] ?? 'firebase-emu-20:8200';
final String project = Platform.environment['FIREBASE_PROJECT'] ?? 'demo-lab';
String get base =>
    'http://$emuHost/v1/projects/$project/databases/(default)/documents';

const _json = {'Content-Type': 'application/json'};

Response _ok(Object body) => Response.ok(jsonEncode(body), headers: _json);

Future<Response> _health(Request _) async =>
    _ok({'ok': true, 'engine': 'firestore-emulator'});

Future<Response> _webhook(Request req) async {
  final body = jsonDecode(await req.readAsString()) as Map<String, dynamic>;
  final id = body['id'] as String?;
  final text = body['text'] as String?;
  if (id == null || text == null || id.isEmpty || text.isEmpty) {
    return Response(422,
        body: jsonEncode({'ok': false, 'error': 'id y text son obligatorios'}),
        headers: _json);
  }
  final channel = (body['channel'] as String?) ?? 'default';
  final doc = {
    'fields': {
      'id': {'stringValue': id},
      'text': {'stringValue': text},
      'channel': {'stringValue': channel},
      'created_at': {
        'integerValue': DateTime.now().millisecondsSinceEpoch.toString()
      },
    }
  };
  // PATCH sobre un documentId concreto = upsert en Firestore.
  final r = await http.patch(Uri.parse('$base/social_posts/$id'),
      headers: _json, body: jsonEncode(doc));
  if (r.statusCode >= 200 && r.statusCode < 300) {
    return _ok({
      'ok': true,
      'message': 'Post persistido en Firestore (emulador)',
      'case': '20-swift-to-dart'
    });
  }
  return Response(502,
      body: jsonEncode({'ok': false, 'error': r.body}), headers: _json);
}

Future<Response> _errors(Request req) async {
  stdout.writeln('Error en DLQ: ${await req.readAsString()}');
  return _ok({'ok': true, 'message': 'Error registrado en DLQ'});
}

Future<Response> _logs(Request _) async {
  final r = await http.get(Uri.parse('$base/social_posts'));
  final logs = <String>[];
  if (r.statusCode == 200) {
    final data = jsonDecode(r.body) as Map<String, dynamic>;
    final docs = (data['documents'] as List?) ?? [];
    final rows = docs.map((d) {
      final f = (d as Map<String, dynamic>)['fields'] as Map<String, dynamic>;
      String s(String k) =>
          ((f[k] as Map?)?['stringValue'] as String?) ?? '';
      final ca =
          int.tryParse(((f['created_at'] as Map?)?['integerValue'] as String?) ?? '0') ?? 0;
      return {'id': s('id'), 'channel': s('channel'), 'text': s('text'), 'ca': ca};
    }).toList()
      ..sort((a, b) => (b['ca'] as int).compareTo(a['ca'] as int));
    for (final row in rows.take(20)) {
      logs.add(
          '[${row['ca']}] FIRESTORE | id=${row['id']} | channel=${row['channel']} | text=${row['text']}');
    }
  }
  return _ok({'ok': true, 'logs': logs});
}

Future<Response> _dashboard(Request _) async {
  final f = File('public/index.html');
  return Response.ok(
      await f.exists()
          ? await f.readAsString()
          : '<h1>Dashboard no encontrado</h1>',
      headers: {'Content-Type': 'text/html'});
}

void main() async {
  final router = Router()
    ..get('/health', _health)
    ..post('/webhook', _webhook)
    ..post('/errors', _errors)
    ..get('/logs', _logs)
    ..get('/', _dashboard);

  final port = int.parse(Platform.environment['PORT'] ?? '8080');
  final server = await shelf_io.serve(router.call, '0.0.0.0', port);
  stdout.writeln(
      'Receiver Case 20 (Dart/Shelf + Firestore emulator) escuchando en :${server.port}');
}
