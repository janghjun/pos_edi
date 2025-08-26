#!/bin/bash
set -e
superset fab create-admin --username admin --firstname admin --lastname admin --email admin@admin.com --password admin || true
superset db upgrade
superset init
