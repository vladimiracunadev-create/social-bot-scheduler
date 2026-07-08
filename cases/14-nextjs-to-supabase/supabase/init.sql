-- ==================================================================================================
-- INICIALIZACIÓN SUPABASE-LITE (Case 14): Postgres + RLS + rol para PostgREST
-- ==================================================================================================
-- Reproduce el núcleo de Supabase: una tabla expuesta como API REST por PostgREST, gobernada por
-- Row Level Security (RLS). El rol `web_anon` es el rol anónimo que PostgREST asume por defecto.

-- Rol anónimo (sin login) que usará PostgREST.
CREATE ROLE web_anon NOLOGIN;
GRANT USAGE ON SCHEMA public TO web_anon;

CREATE TABLE IF NOT EXISTS social_posts (
    id           TEXT PRIMARY KEY,
    text         TEXT NOT NULL,
    channel      TEXT NOT NULL DEFAULT 'default',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Row Level Security: la tabla queda protegida y sólo las políticas permiten acceso.
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;

-- Política permisiva para el rol anónimo (lab local). En producción se restringiría por usuario/tenant.
CREATE POLICY anon_rw ON social_posts
    FOR ALL TO web_anon
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE ON social_posts TO web_anon;

-- PostgREST se conecta como `postgres` y hace SET ROLE web_anon en cada request anónima.
GRANT web_anon TO postgres;
