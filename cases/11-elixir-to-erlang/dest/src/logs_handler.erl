%% ==================================================================================================
%% LOGS HANDLER (Case 11) — expone los últimos registros de Mnesia para el dashboard.
%% ==================================================================================================
-module(logs_handler).
-export([init/2]).

init(Req0, State) ->
    Rows = store:recent(20),
    Logs = [format_log(R) || R <- Rows],
    Body = json:encode(#{<<"ok">> => true, <<"logs">> => Logs}),
    Req = cowboy_req:reply(200,
        #{<<"content-type">> => <<"application/json">>},
        Body, Req0),
    {ok, Req, State}.

format_log(#{<<"id">> := Id, <<"text">> := T, <<"channel">> := C, <<"created_at">> := Ts}) ->
    iolist_to_binary([<<"[">>, Ts, <<"] MNESIA | id=">>, Id,
                      <<" | channel=">>, C, <<" | text=">>, T]).
