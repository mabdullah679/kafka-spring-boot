# Kafka Producer and Spring Boot Consumer

This workspace contains two separate Docker Compose projects:

- `producer-stack/docker-compose.yml`: starts Kafka and a producer that writes to the `eclipse-events` topic.
- `consumer-app/docker-compose.yml`: starts a Spring Boot app that consumes from `eclipse-events` and logs each message.

## What gets published

The producer writes:

- `Hello from {containerName}.`
- telemetry noise as JSON strings

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

Note:

- As of April 7, 2026, the old `bitnami/kafka:3.7` reference no longer resolves on Docker Hub in this environment.
- The compose file now uses `apache/kafka:3.7.2`, which matches Apache Kafka's published Docker guidance for the 3.7 line.

## Start the Spring Boot consumer

In a second terminal:

```powershell
docker compose -f consumer-app/docker-compose.yml up --build
```

You should then see the consumer log messages similar to:

```text
received topic=eclipse-events offset=0 key=greeting payload=Hello from kafka-producer.
received topic=eclipse-events offset=1 key=telemetry payload={"type":"telemetry",...}
```

## Stop everything

```powershell
docker compose -f consumer-app/docker-compose.yml down
docker compose -f producer-stack/docker-compose.yml down
```
