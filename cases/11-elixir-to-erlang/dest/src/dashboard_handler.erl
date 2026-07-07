%% ==================================================================================================
%% DASHBOARD HANDLER (Case 11) — sirve el HTML estático desde el priv/ del release.
%% ==================================================================================================
-module(dashboard_handler).
-export([init/2]).

init(Req0, State) ->
    File = filename:join(code:priv_dir(social_bot_dest), "index.html"),
    {Code, CType, Body} =
        case file:read_file(File) of
            {ok, Bin} -> {200, <<"text/html; charset=utf-8">>, Bin};
            {error, _} -> {200, <<"text/html; charset=utf-8">>, <<"<h1>Dashboard no encontrado</h1>">>}
        end,
    Req = cowboy_req:reply(Code, #{<<"content-type">> => CType}, Body, Req0),
    {ok, Req, State}.
