# kafka-spring-boot

A local Kafka pipeline: a Python producer publishes numbered messages, a Spring Boot consumer joins each one with a Postgres row, and a Flask `data-sync` service writes the merged result back to Postgres in batches.

```
producer-stack/                              consumer-app/
kafka-producer --> kafka:9092 (eclipse-events) --> spring-consumer --POST /sync-records--> data-sync
 "message N" every 10 s                            looks up row id=N in      buffers, then every
 + telemetry JSON every 3 s                        eclipse-postgres          SYNC_INTERVAL_SECONDS
                                                   (ignores telemetry)       UPDATE ... SYNCED --> eclipse-postgres
```

Not local: base images (Kafka, Postgres, Python, Maven, Temurin) are pulled from Docker Hub and Maven/pip download dependencies at build time.

## Prerequisites
- Docker with `docker compose`, running. No Java, Python or Postgres is needed on the host (everything builds in containers).
- `make` (macOS/Linux). On Windows, use WSL or the manual commands under "Alternate startup".
- Free host ports 9092 (Kafka) and 5432 (Postgres).

## Run it
1. `make up` (creates the shared Docker network `eclipse-net`, then builds and starts both Compose projects)
2. `docker logs -f spring-consumer` and `docker logs -f data-sync`; within seconds you should see `merged and shipped record id=4 messageNumber=4` and `buffered merged record id=4 messageNumber=4` (ids 1 to 10 cycle)
3. After the sync interval (default 300 s) check the database:
   `docker exec eclipse-postgres psql -U eclipse -d eclipse -c "select id, last_message_number, last_message_text, last_merged_at, sync_status from eclipse_records order by id;"` (processed rows show `SYNCED`)
4. `make seed-data` resets the table to 10 fresh rows; `make destroy` stops everything and removes the network

Overrides: if host port 5432 is taken, `POSTGRES_HOST_PORT=15432 make up`. For a quick cycle, `SYNC_INTERVAL_SECONDS=20 make up`. If port 9092 is taken, edit the left side of `"9092:9092"` in `producer-stack/docker-compose.yml`.

Alternate startup (no make): `docker network create eclipse-net`, then `docker compose -f producer-stack/docker-compose.yml up --build -d` and `docker compose -f consumer-app/docker-compose.yml up --build -d`. Stop with `docker compose -f consumer-app/docker-compose.yml down --remove-orphans`, the same for the producer file, then `docker network rm eclipse-net`.

Publish a message by hand: `docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka:9092 --topic eclipse-events`, then type `message 4`.

## What it does
| Action | Result |
|---|---|
| producer runs | `message 1` ... `message 10`, wrapping to 1 (every 10 s), plus telemetry JSON (every 3 s), on topic `eclipse-events` |
| consumer reads `message N` | looks up row id N, builds a merged payload (`MergedRecordSetter`), POSTs it to `data-sync`; non-matching payloads (telemetry) are logged as ignored |
| `data-sync` flush | every `SYNC_INTERVAL_SECONDS` updates `last_message_number`, `last_message_text`, `last_merged_at`, `sync_status='SYNCED'` for buffered rows |
| `make seed-data` | truncates `eclipse_records` and re-inserts ids 1 to 10 with sync values cleared |

## Interface
| Endpoint / port | Service | Auth |
|---|---|---|
| `POST /sync-records` (returns 202), `GET /health` on 8081 | `data-sync`, Compose network only (not published) | none |
| `kafka:9092` (published to host) | Kafka, PLAINTEXT | none |
| Postgres 5432 (published; `POSTGRES_HOST_PORT`) | user/db/password `eclipse` | demo credential |

## Tests
There are no unit tests. `./tests/e2e.sh` (start with `SYNC_INTERVAL_SECONDS=20 make up`) resets the table, waits for at least one row to become `SYNCED`, and fails unless every `SYNCED` row has `last_message_text = 'message <id>'` and `last_message_number = <id>`, and both services logged a merge/flush. It needs Docker and the running stack, no external services. CI (`.github/workflows/ci.yml`) also packages the consumer with JDK 17, byte-compiles the Python, validates both compose files, runs shellcheck and gitleaks.

## Layout
| Path | Role |
|---|---|
| [producer-stack/docker-compose.yml](producer-stack/docker-compose.yml) | Kafka (KRaft, single node) and the producer |
| [producer-stack/producer/producer.py](producer-stack/producer/producer.py) | message and telemetry producer |
| [consumer-app/docker-compose.yml](consumer-app/docker-compose.yml) | Postgres, consumer, data-sync |
| [consumer-app/src/main/java/com/example/consumer/KafkaMessageProcessor.java](consumer-app/src/main/java/com/example/consumer/KafkaMessageProcessor.java) | parses `message N`, merges, ships |
| [consumer-app/src/main/resources/application.yml](consumer-app/src/main/resources/application.yml) | Spring config (env-overridable) |
| [consumer-app/db/init.sql](consumer-app/db/init.sql), [consumer-app/db/seed.sql](consumer-app/db/seed.sql) | schema + seed; reset |
| [data-sync/app.py](data-sync/app.py) | buffering service that writes back to Postgres |
| [Makefile](Makefile) | up/down/destroy/seed-data/logs |
| [tests/e2e.sh](tests/e2e.sh) | end-to-end check |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | CI |
| [CLAUDE.md](CLAUDE.md) | notes for Claude Code sessions |

## Known issues (not fixed in this pass)
- Kafka (PLAINTEXT, no auth) and Postgres (password `eclipse`) are published on all host interfaces. Fine on a trusted laptop; bind to `127.0.0.1` or drop the `ports:` lines before running on a shared network.
- `data-sync` keeps its buffer in memory: a restart loses merged records not yet flushed.

## Design notes
- Two Compose projects joined by an external network (`eclipse-net`) rather than one file, so the producer side can be run or replaced independently; the cost is the extra `network create` step that `make up` handles.
- `data-sync` batches writes on a timer instead of writing per message, so the consumer never blocks on the database write-back.
- `SYNC_INTERVAL_SECONDS` and `POSTGRES_HOST_PORT` are compose variables with the original values as defaults, so tests can shorten the flush interval and avoid host-port clashes without editing files.
