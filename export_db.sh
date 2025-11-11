#!/bin/bash
# Auto-export DATABASE_URL for Hurtrock Music Store
export DATABASE_URL='postgresql://postgres:fajar@localhost:5432/hurtrock'
echo "[INFO] DATABASE_URL exported: $DATABASE_URL"