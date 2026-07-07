%% ==================================================================================================
%% WEBHOOK HANDLER (Case 11) — recibe el post desde n8n y lo persiste en Mnesia.
%% ==================================================================================================
-module(webhook_handler).
-export([init/2]).

init(Req0, State) ->
    handle(cowboy_req:method(Req0), Req0, State).

handle(<<"POST">>, Req0, State) ->
    {ok, Body, Req1} = read_body(Req0, <<>>),
    try json:decode(Body) of
        Map when is_map(Map) ->
            Id = maps:get(<<"id">>, Map, undefined),
            Text = maps:get(<<"text">>, Map, undefined),
            case (Id =:= undefined) orelse (Text =:= undefined) of
                true ->
                    reply(422, #{<<"ok">> => false,
                                 <<"error">> => <<"id y text son obligatorios">>}, Req1, State);
                false ->
                    Channel = maps:get(<<"channel">>, Map, <<"default">>),
                    ok = store:insert(Id, Text, Channel),
                    io:format("Post persistido en Mnesia: ~s~n", [Id]),
                    reply(200, #{<<"ok">> => true,
                                 <<"message">> => <<"Post persistido en Mnesia (BEAM)">>,
                                 <<"case">> => <<"11-elixir-to-erlang">>}, Req1, State)
            end;
        _ ->
            reply(400, #{<<"ok">> => false, <<"error">> => <<"payload no es un objeto JSON">>}, Req1, State)
    catch _:_ ->
        reply(400, #{<<"ok">> => false, <<"error">> => <<"JSON invalido">>}, Req1, State)
    end;
handle(_Other, Req0, State) ->
    reply(405, #{<<"ok">> => false, <<"error">> => <<"method not allowed">>}, Req0, State).

read_body(Req0, Acc) ->
    case cowboy_req:read_body(Req0) of
        {ok, Data, Req} -> {ok, <<Acc/binary, Data/binary>>, Req};
        {more, Data, Req} -> read_body(Req, <<Acc/binary, Data/binary>>)
    end.

reply(Code, Map, Req0, State) ->
    Req = cowboy_req:reply(Code,
        #{<<"content-type">> => <<"application/json">>},
        json:encode(Map), Req0),
    {ok, Req, State}.
