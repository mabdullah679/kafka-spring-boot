#!/usr/bin/env bash
# End-to-end check of the Kafka -> Spring consumer -> data-sync -> Postgres flow.
# Assumes the stack is up with a short flush interval:  SYNC_INTERVAL_SECONDS=20 make up
# Resets the table, then passes only if at least one row reaches sync_status=SYNCED and every SYNCED row carries
# last_message_text = 'message <id>' and last_message_number = <id> (i.e. the Kafka payload was joined to the right row).
set -euo pipefail

TIMEOUT="${E2E_TIMEOUT_SECONDS:-240}"
psql_q() { docker exec eclipse-postgres psql -U eclipse -d eclipse -tA -c "$1"; }

make -s seed-data >/dev/null
[ "$(psql_q "select count(*) from eclipse_records where sync_status='SYNCED'")" = "0" ] || { echo "FAIL: reset did not clear SYNCED rows"; exit 1; }

deadline=$((SECONDS + TIMEOUT))
until [ "$(psql_q "select count(*) from eclipse_records where sync_status='SYNCED'")" -ge 1 ]; do
  if [ "$SECONDS" -ge "$deadline" ]; then
    echo "TIMEOUT: no row reached SYNCED within ${TIMEOUT}s"
    docker logs --tail=20 spring-consumer 2>&1 || true
    docker logs --tail=20 data-sync 2>&1 || true
    exit 1
  fi
  sleep 5
done

bad="$(psql_q "select count(*) from eclipse_records where sync_status='SYNCED' and (last_message_text <> 'message ' || id or last_message_number <> id or last_merged_at is null)")"
[ "$bad" = "0" ] || { echo "FAIL: $bad SYNCED row(s) have a mismatched payload"; psql_q "select id,last_message_number,last_message_text from eclipse_records where sync_status='SYNCED'"; exit 1; }

consumer_log="$(docker logs spring-consumer 2>&1)"   # capture first: `grep -q` closing the pipe early would trip pipefail
sync_log="$(docker logs data-sync 2>&1)"
grep -q "merged and shipped record id=" <<<"$consumer_log" || { echo "FAIL: consumer never logged a merge"; exit 1; }
grep -q "flushed .* merged record" <<<"$sync_log" || { echo "FAIL: data-sync never logged a flush"; exit 1; }

echo "PASS: $(psql_q "select count(*) from eclipse_records where sync_status='SYNCED'") row(s) SYNCED with matching payloads"
