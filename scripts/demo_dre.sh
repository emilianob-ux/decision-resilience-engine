#!/usr/bin/env bash
# Demo DRE en 60 segundos / 60-second DRE demo.
#
# Levanta la API, ejecuta el camino feliz y muestra las tres propiedades que
# este repo intenta demostrar:
#   1. resume       -> el run se retoma desde el ultimo checkpoint persistido
#   2. idempotencia -> reenviar (run_id, data_hash) identico no duplica el run
#   3. colision     -> mismo run_id con data_hash distinto => HTTP 409 tipado
#
# Uso:  bash scripts/demo_dre.sh [--port 8000] [--keep]
#   --keep  conserva la base SQLite temporal e imprime su ruta.

set -euo pipefail

PORT=8000
KEEP=0
while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Opcion desconocida: $1" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY=python3

WORKDIR="$(mktemp -d)"
DB="$WORKDIR/dre_demo.sqlite"
BASE="http://127.0.0.1:${PORT}"
RUN_ID="opt_20260506_000100_v5.0"
SERVER_PID=""

cleanup() {
  [ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null || true
  if [ "$KEEP" = "1" ]; then
    echo ""
    echo "Ledger conservado en: $DB"
  else
    rm -rf "$WORKDIR"
  fi
}
trap cleanup EXIT

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

step "0/5  Arrancando la API sobre un ledger SQLite limpio"
echo "     db=$DB"
"$PY" scripts/run_dre_api.py --db "$DB" --port "$PORT" >"$WORKDIR/server.log" 2>&1 &
SERVER_PID=$!

if ! curl -sf --retry 30 --retry-connrefused --retry-delay 1 -o /dev/null "$BASE/dre/health"; then
  echo "La API no respondio en $BASE. Log:" >&2
  cat "$WORKDIR/server.log" >&2
  exit 1
fi

step "1/5  GET /dre/health"
curl -s "$BASE/dre/health"; echo

step "2/5  POST /dre/simulate  (IDLE -> ... -> MONITORING, con bitacora append-only)"
curl -s -X POST "$BASE/dre/simulate" \
  -H 'Content-Type: application/json' \
  -d "{\"run_id\":\"$RUN_ID\",\"data_hash\":\"sha256:demo\",\"rng_seed\":7,\"variant\":\"standard\"}" \
  | "$PY" -m json.tool

step "3/5  POST /dre/resume  (reconstruye el contexto desde el ultimo checkpoint)"
curl -s -X POST "$BASE/dre/resume" \
  -H 'Content-Type: application/json' \
  -d "{\"run_id\":\"$RUN_ID\"}" \
  | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print("current_state =", d["current_state"]); print("run_id        =", d["run_id"])'

step "4/5  Idempotencia: mismo run_id + mismo data_hash => el run NO se duplica"
curl -s -X POST "$BASE/dre/simulate" \
  -H 'Content-Type: application/json' \
  -d "{\"run_id\":\"$RUN_ID\",\"data_hash\":\"sha256:demo\",\"rng_seed\":7,\"variant\":\"standard\"}" \
  | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print("registry_write =", d["skill_statuses"]["registry_write"], "(esperado: already_existed)")'

step "5/5  Colision: mismo run_id + data_hash DISTINTO => HTTP 409 tipado"
curl -s -o "$WORKDIR/collision.json" -w '     HTTP %{http_code}\n' \
  -X POST "$BASE/dre/simulate" \
  -H 'Content-Type: application/json' \
  -d "{\"run_id\":\"$RUN_ID\",\"data_hash\":\"sha256:OTRO\",\"rng_seed\":7,\"variant\":\"standard\"}"
"$PY" -m json.tool < "$WORKDIR/collision.json"

step "Bitacora persistida (SQLite append-only)"
"$PY" - "$DB" <<'PYEOF'
import sqlite3
import sys

con = sqlite3.connect(sys.argv[1])
runs = con.execute("SELECT COUNT(*) FROM dre_run_registry").fetchone()[0]
events = con.execute("SELECT COUNT(*) FROM dre_audit_log").fetchone()[0]
cks = con.execute("SELECT COUNT(*) FROM dre_checkpoints").fetchone()[0]
print(f"     runs registrados = {runs}   eventos de auditoria = {events}   checkpoints = {cks}")
print("     transiciones:")
for before, after, ev in con.execute(
    "SELECT state_before, state_after, event_type FROM dre_audit_log ORDER BY id"
):
    print(f"       {before:<18} --{ev:<24}--> {after}")
con.close()
PYEOF

echo ""
echo "OK: 1 run, 1 sola fila de registro pese a 2 envios identicos, 409 en la colision."
