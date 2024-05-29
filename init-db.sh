#!/bin/bash
set -e

# Путь к файлу, который будет использоваться как индикатор того, что дамп уже был применен
INIT_DB_FLAG="/var/lib/postgresql/data/init-db.flag"

if [ ! -f "$INIT_DB_FLAG" ]; then
    echo "Применение дампа базы данных..."
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < /var/lib/postgresql/dump/postgres_dump.sql
    # Создать файл-флаг, чтобы не применять дамп при следующем запуске
    touch "$INIT_DB_FLAG"
else
    echo "Дамп базы данных уже был применен."
fi
