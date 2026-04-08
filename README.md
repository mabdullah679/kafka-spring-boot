# Kafka Producer, Postgres, Spring Consumer, and Data Sync

This workspace contains two separate Docker Compose projects:

- `producer-stack/docker-compose.yml`: starts Kafka and a producer that writes numbered messages plus telemetry to the `eclipse-events` topic.
- `consumer-app/docker-compose.yml`: starts Postgres, a Spring Boot consumer, and the `data-sync` container.

## Runtime flow

1. The producer publishes:

- `message 1`, `message 2`, ... up to `message 10`, then wraps back to `message 1`
- telemetry noise as JSON strings

2. Postgres starts with 10 rows in `eclipse_records` using `BIGINT` primary keys `1..10`.

3. The Spring Boot consumer:

- reads from `eclipse-events`
- extracts the number from `message N`
- looks up the matching Postgres row by primary key
- joins the Kafka payload with the stored record using `MergedRecordSetter`
- ships the merged payload to `data-sync`

4. The `data-sync` container buffers merged payloads and updates Postgres every 5 minutes.

## Get Running

The simplest way to start the full stack is:

```powershell
make up
```

That starts:

- `kafka`
- `kafka-producer`
- `eclipse-postgres`
- `spring-consumer`
- `data-sync`

## Alternate Manual Startup

Use this only if you want to start the stack piece by piece instead of `make up`.

Create the shared Docker network once so the two compose projects can talk to each other:

```powershell
docker network create eclipse-net
```

Start Kafka and the producer:

```powershell
docker compose -f producer-stack/docker-compose.yml up --build
```

In a second terminal, start Postgres, the Spring app, and `data-sync`:

```powershell
docker compose -f consumer-app/docker-compose.yml up --build
```

## Test It

Watch the application logs:

```powershell
docker logs -f spring-consumer
docker logs -f data-sync
```

You should see lines similar to:

```text
spring-consumer  | received payload=message 4
spring-consumer  | merged and shipped record id=4 messageNumber=4
data-sync        | buffered merged record id=4 messageNumber=4
```

For a fresh test cycle, reset the database back to the original 10 rows:

```powershell
make seed-data
```

`make seed-data` runs `consumer-app/db/seed.sql`, which:

- removes all current rows from `eclipse_records`
- inserts 10 fresh records with ids `1..10`
- clears old sync values so testing starts clean

`TRUNCATE TABLE eclipse_records;` means "empty the table completely" before inserting the fresh rows.

After the configured 5-minute sync interval, `data-sync` writes updates back to Postgres. Confirm that with:

```powershell
docker exec eclipse-postgres psql -U eclipse -d eclipse -c "select id, last_message_number, last_message_text, last_merged_at, sync_status from eclipse_records order by id;"
```

Rows with processed matches will show:

- `last_message_number`
- `last_message_text`
- `last_merged_at`
- `sync_status = SYNCED`

## Stop everything

```powershell
docker compose -f consumer-app/docker-compose.yml down --remove-orphans
docker compose -f producer-stack/docker-compose.yml down --remove-orphans
docker network rm eclipse-net
```

Or:

```powershell
make destroy
```
