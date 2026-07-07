%% ==================================================================================================
%% APPLICATION BEHAVIOUR (Case 11) — arranque OTP del receptor.
%% ==================================================================================================
%% Orden de arranque:
%%   1. Inicializa Mnesia y la tabla `social_post` (ver store.erl).
%%   2. Compila el router de Cowboy y levanta el listener HTTP.
%%   3. Arranca el árbol de supervisión (filosofía OTP "let it crash").
%% ==================================================================================================
-module(social_bot_dest_app).
-behaviour(application).

-export([start/2, stop/1]).

start(_Type, _Args) ->
    ok = store:init(),

    Dispatch = cowboy_router:compile([
        {'_', [
            {"/webhook", webhook_handler, []},
            {"/errors", errors_handler, []},
            {"/logs", logs_handler, []},
            {"/health", health_handler, []},
            {"/", dashboard_handler, []}
        ]}
    ]),

    Port = port_from_env(),
    {ok, _} = cowboy:start_clear(
        http_listener,
        [{port, Port}],
        #{env => #{dispatch => Dispatch}}
    ),
    io:format("Receiver Case 11 (Erlang/Cowboy + Mnesia) escuchando en :~p~n", [Port]),

    social_bot_dest_sup:start_link().

stop(_State) ->
    ok = cowboy:stop_listener(http_listener),
    ok.

port_from_env() ->
    case os:getenv("PORT") of
        false -> 8080;
        Value -> list_to_integer(Value)
    end.
