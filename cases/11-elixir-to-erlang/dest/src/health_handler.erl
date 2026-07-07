%% ==================================================================================================
%% HEALTH HANDLER (Case 11) — readiness para el dashboard maestro y el healthcheck de Docker.
%% ==================================================================================================
-module(health_handler).
-export([init/2]).

init(Req0, State) ->
    Body = json:encode(#{<<"ok">> => true, <<"engine">> => <<"mnesia+beam">>}),
    Req = cowboy_req:reply(200,
        #{<<"content-type">> => <<"application/json">>},
        Body, Req0),
    {ok, Req, State}.
