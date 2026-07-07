%% ==================================================================================================
%% ERRORS HANDLER (Case 11) — Dead Letter Queue: n8n reporta aquí los fallos tras agotar reintentos.
%% ==================================================================================================
-module(errors_handler).
-export([init/2]).

init(Req0, State) ->
    {ok, Body, Req1} = read_body(Req0, <<>>),
    io:format("Error en DLQ: ~s~n", [Body]),
    Req = cowboy_req:reply(200,
        #{<<"content-type">> => <<"application/json">>},
        json:encode(#{<<"ok">> => true, <<"message">> => <<"Error registrado en DLQ">>}),
        Req1),
    {ok, Req, State}.

read_body(Req0, Acc) ->
    case cowboy_req:read_body(Req0) of
        {ok, Data, Req} -> {ok, <<Acc/binary, Data/binary>>, Req};
        {more, Data, Req} -> read_body(Req, <<Acc/binary, Data/binary>>)
    end.
