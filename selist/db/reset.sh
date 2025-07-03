#!/bin/bash

source "$(dirname "$0")/../.env"
PGPASSWORD="$DB_ADMIN_PASSWORD" psql -U postgres -v db_user="$DB_USER" -v db_name="$DB_NAME" -f reset.sql