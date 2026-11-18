# CLAUDE.md

Kafka demo pipeline in two Compose projects: `producer-stack/` (Kafka 3.7.2 KRaft + Python producer) and `consumer-app/` (Postgres 17, Spring Boot 3.3.5 / Java 17 consumer, Flask `data-sync`). Producer sends `message 1..10` plus telemetry JSON to topic `eclipse-events`; the consumer joins `message N` with row id N and ships it to `data-sync`, which flushes to Postgres every `SYNC_INTERVAL_SECONDS` (default 300).
Global working rules: `~/.claude/CLAUDE.md` (not copied here).

## Commands (run and verified)
- `make up` / `make down` / `make destroy` (also removes the `eclipse-net` network) / `make ps` / `make seed-data` (resets table to 10 rows).
- Build the consumer: `mvn -B -q -f consumer-app/pom.xml package`. There are no unit tests.
- End-to-end: `SYNC_INTERVAL_SECONDS=20 make up`, then `./tests/e2e.sh` (about 10-30 s). Exit 0 = pass. Use `POSTGRES_HOST_PORT=15432` if host port 5432 is taken.

## Conventions and traps
- Both compose files share the external network `eclipse-net`; `make up` creates it. Container names are fixed (`kafka`, `kafka-producer`, `eclipse-postgres`, `spring-consumer`, `data-sync`).
- `consumer-app/docker-compose.yml` reads two optional env vars (defaults keep the shipped behaviour): `SYNC_INTERVAL_SECONDS` (300) and `POSTGRES_HOST_PORT` (5432).
- The Postgres password `eclipse` is a local-demo default, repeated in compose and `application.yml`; it is not a real secret. Do not reuse it elsewhere.
- Schema/seed: `consumer-app/db/init.sql` runs only on a fresh Postgres volume; `seed.sql` is the reset used by `make seed-data`.

## Do not touch
- Never push to `main` (branch + PR; CI in `.github/workflows/ci.yml`). Do not change the ports/credentials exposure without the owner (see README, known issues).
