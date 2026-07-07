%% ==================================================================================================
%% SUPERVISOR (Case 11) — árbol de supervisión OTP.
%% ==================================================================================================
%% Cowboy gestiona su propio pool de procesos (uno por conexión); este supervisor raíz mantiene
%% la aplicación viva con estrategia one_for_one. Es el punto natural donde colgar workers futuros
%% (p.ej. un limpiador de Mnesia) sin tocar el arranque.
%% ==================================================================================================
-module(social_bot_dest_sup).
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{strategy => one_for_one, intensity => 5, period => 10},
    {ok, {SupFlags, []}}.
