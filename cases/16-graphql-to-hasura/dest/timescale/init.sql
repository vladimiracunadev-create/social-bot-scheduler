-- ==================================================================================================
-- INICIALIZACIÓN DE TIMESCALEDB (Case 16)
-- ==================================================================================================
-- Este script lo ejecuta automáticamente la imagen de TimescaleDB al arrancar por primera vez
-- (se monta en /docker-entrypoint-initdb.d). Crea la tabla de posts como HYPERTABLE, la estructura
-- optimizada de TimescaleDB para series temporales: particiona transparentemente por tiempo en
-- "chunks", acelerando consultas por rango y la retención de datos.
--
-- Hasura descubre y expone esta tabla como GraphQL sin escribir una sola línea de resolver.

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

CREATE TABLE IF NOT EXISTS social_posts (
    id            TEXT        NOT NULL,
    text          TEXT        NOT NULL,
    channel       TEXT        NOT NULL DEFAULT 'default',
    scheduled_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- La PK compuesta incluye la columna de particionado (requisito de las hypertables).
    PRIMARY KEY (id, created_at)
);

-- Convierte la tabla en hypertable particionada por created_at (idempotente).
SELECT create_hypertable('social_posts', 'created_at', if_not_exists => TRUE);

-- Índice para las consultas del dashboard (últimos registros por canal).
CREATE INDEX IF NOT EXISTS idx_social_posts_channel ON social_posts (channel, created_at DESC);
