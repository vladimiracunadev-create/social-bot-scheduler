defmodule Case11.Publisher do
  @moduledoc """
  ==================================================================================================
  EMISOR ELIXIR (Case 11: Elixir -> n8n -> Erlang/Cowboy + Mnesia)
  ==================================================================================================
  Emisor sobre la BEAM que lee la cola de posts (posts.json) y reenvía los vencidos al webhook de
  n8n. Sin dependencias externas: HTTP vía `:httpc` (inets) y (de)serialización con el módulo `:json`
  de OTP 27. En un despliegue real este módulo viviría dentro de un árbol de supervisión Phoenix,
  emitiendo por `Phoenix.Channel`; aquí lo mantenemos como un publisher directo para el laboratorio.

  Modo dry-run: sin WEBHOOK_URL, los envíos se simulan por log.
  """

  @posts_file Path.join([__DIR__, "..", "posts.json"])

  def main(_args \\ []) do
    :inets.start()
    :ssl.start()

    webhook = System.get_env("WEBHOOK_URL")

    posts =
      @posts_file
      |> File.read!()
      |> :json.decode()

    now = System.system_time(:second)

    Enum.each(posts, fn post ->
      due? = due?(post, now)

      if not Map.get(post, "published", false) and due? do
        forward(webhook, post)
      end
    end)
  end

  defp due?(post, now) do
    case Map.get(post, "scheduled_at") do
      nil -> true
      "" -> true
      ts ->
        case DateTime.from_iso8601(ts) do
          {:ok, dt, _} -> DateTime.to_unix(dt) <= now
          _ -> true
        end
    end
  end

  defp forward(nil, post) do
    IO.puts("[DRY-RUN] Post #{post["id"]} (canal #{Map.get(post, "channel", "default")}) reenviado.")
  end

  defp forward(url, post) do
    body =
      %{
        "id" => post["id"],
        "text" => post["text"],
        "channel" => Map.get(post, "channel", "default"),
        "scheduled_at" => Map.get(post, "scheduled_at") || ""
      }
      |> :json.encode()
      |> IO.iodata_to_binary()

    request = {String.to_charlist(url), [], ~c"application/json", body}

    case :httpc.request(:post, request, [{:timeout, 15_000}], []) do
      {:ok, {{_v, code, _r}, _headers, _resp}} when code in 200..299 ->
        IO.puts("[OK] Post #{post["id"]} aceptado por n8n (#{code}).")

      other ->
        IO.puts("[ERROR] Fallo reenviando #{post["id"]}: #{inspect(other)}")
    end
  end
end
