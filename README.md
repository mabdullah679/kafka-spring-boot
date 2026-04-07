# Kafka Producer, Postgres, Spring Consumer, and Data Sync

This workspace contains two separate Docker Compose projects:

- `producer-stack/docker-compose.yml`: starts Kafka and a producer that writes numbered messages plus telemetry to the `eclipse-events` topic.
- `consumer-app/docker-compose.yml`: starts Postgres, a Spring Boot consumer, and the `data-sync` container.

## Runtime flow

1. The producer publishes:

- `message 1`, `message 2`, ... up to `message 999`, then wraps back to `message 1`
- telemetry noise as JSON strings

2. Postgres starts with 10 rows in `eclipse_records` using `BIGINT` primary keys `1..10`.

3. The Spring Boot consumer:

- reads from `eclipse-events`
- extracts the number from `message N`
- looks up the matching Postgres row by primary key
- joins the Kafka payload with the stored record using `MergedRecordSetter`
- ships the merged payload to `data-sync`

4. The `data-sync` container buffers merged payloads and updates Postgres every 5 minutes.

## Prerequisite

Create the shared Docker network once so the two compose projects can talk to each other:

```powershell
docker network create eclipse-net
```

## Start Kafka and the producer

```powershell
docker compose -f producer-stack/docker-compose.yml up --build
```

This starts:

- `kafka`
- `kafka-producer`

## Start Postgres, the Spring consumer, and data-sync

In a second terminal:

```powershell
docker compose -f consumer-app/docker-compose.yml up --build
```

This starts:

- `eclipse-postgres`
- `data-sync`
- `spring-consumer`

You should then see logs similar to:

```text
spring-consumer  | received payload=message 4
spring-consumer  | merged and shipped record id=4 messageNumber=4
data-sync        | buffered merged record id=4 messageNumber=4
```

After the configured 5-minute sync interval, `data-sync` updates `eclipse_records.last_message_number`, `last_message_text`, `last_merged_at`, and `sync_status`.

## Stop everything

```powershell
docker compose -f consumer-app/docker-compose.yml down
docker compose -f producer-stack/docker-compose.yml down
```
