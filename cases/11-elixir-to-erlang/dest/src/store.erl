%% ==================================================================================================
%% STORE (Case 11) — persistencia en Mnesia, la BD nativa de la BEAM.
%% ==================================================================================================
%% Mnesia es la única BD de la matriz que vive *dentro* del runtime de la aplicación: no hay
%% contenedor de base de datos separado. Aquí usamos `ram_copies` (tabla en memoria del nodo) por
%% simplicidad y para reflejar el patrón "hot storage" de ETS/Mnesia; en un despliegue distribuido
%% se cambiaría a `disc_copies` con replicación entre nodos.
%% ==================================================================================================
-module(store).
-export([init/0, insert/3, recent/1]).

-record(social_post, {key, id, text, channel, created_at}).

init() ->
    ok = mnesia:start(),
    case mnesia:create_table(social_post,
             [{attributes, record_info(fields, social_post)},
              {ram_copies, [node()]},
              {type, ordered_set}]) of
        {atomic, ok} -> ok;
        {aborted, {already_exists, social_post}} -> ok
    end,
    ok = mnesia:wait_for_tables([social_post], 10000),
    ok.

%% Inserta un post. La clave es el timestamp en microsegundos (ordered_set => orden temporal).
insert(Id, Text, Channel) ->
    Now = erlang:system_time(microsecond),
    Rec = #social_post{
        key = Now,
        id = Id,
        text = Text,
        channel = Channel,
        created_at = iso8601(Now)
    },
    {atomic, ok} = mnesia:transaction(fun() -> mnesia:write(Rec) end),
    ok.

%% Devuelve los N registros más recientes como lista de mapas (para serializar a JSON).
recent(N) ->
    F = fun() ->
        Keys = mnesia:all_keys(social_post),
        Top = lists:sublist(lists:reverse(lists:sort(Keys)), N),
        [rec_to_map(hd(mnesia:read(social_post, K))) || K <- Top]
    end,
    {atomic, Rows} = mnesia:transaction(F),
    Rows.

rec_to_map(#social_post{id = Id, text = Text, channel = Ch, created_at = Ts}) ->
    #{<<"id">> => Id, <<"text">> => Text, <<"channel">> => Ch, <<"created_at">> => Ts}.

iso8601(Micros) ->
    Secs = Micros div 1000000,
    {{Y, Mo, D}, {H, Mi, S}} = calendar:system_time_to_universal_time(Secs, second),
    iolist_to_binary(
        io_lib:format("~4..0w-~2..0w-~2..0wT~2..0w:~2..0w:~2..0wZ", [Y, Mo, D, H, Mi, S])
    ).
