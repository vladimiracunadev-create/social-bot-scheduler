# ==================================================================================================
# Case 06 — Dest PHP con la extensión phpredis instalada (la imagen base no la trae).
# Corrige "Fatal error: Class Redis not found" al persistir en Redis.
# ==================================================================================================
FROM php:8.2-apache
RUN pecl install redis \
    && docker-php-ext-enable redis \
    && a2enmod headers
