KAFKA-SPRING-BOOT (plain-text version of README.md)

What it is
A small pipeline that runs on your computer with Docker. A Python program sends numbered messages ("message 1" to "message 10") into Kafka. A Spring Boot Java program reads them, finds the database row with the same number, merges the two, and hands the result to a small Python service called data-sync. data-sync collects those results and writes them back into the Postgres database in batches.

How it fits together
Producer to Kafka (topic eclipse-events) to the Spring consumer. The consumer looks up the matching row in Postgres, then sends the merged result to data-sync. Every few minutes data-sync updates the row and marks it SYNCED. The producer also sends telemetry noise every 3 seconds, which the consumer ignores. Not on your computer: the Docker base images and the Java and Python libraries are downloaded when you build.

What you need
Docker running with compose. The make program (on Windows use WSL, or the manual commands below). Ports 9092 and 5432 free. You do not need Java, Python or Postgres installed.

How to run it
1. Run: make up. It creates a shared Docker network, then builds and starts everything.
2. Watch the logs: docker logs -f spring-consumer and docker logs -f data-sync. Within seconds you should see lines like "merged and shipped record id=4" and "buffered merged record id=4".
3. After the sync interval (5 minutes by default), look at the database with: docker exec eclipse-postgres psql -U eclipse -d eclipse -c "select id, last_message_number, last_message_text, last_merged_at, sync_status from eclipse_records order by id;". Processed rows show SYNCED.
4. make seed-data resets the table to 10 fresh rows. make destroy stops everything and removes the network.

If something goes wrong or you want to change it
If port 5432 is taken, run: POSTGRES_HOST_PORT=15432 make up. For a faster cycle, run: SYNC_INTERVAL_SECONDS=20 make up. If port 9092 is taken, change the left number in "9092:9092" in producer-stack/docker-compose.yml. Without make: create the network with docker network create eclipse-net, then start producer-stack/docker-compose.yml and consumer-app/docker-compose.yml with docker compose -f (file) up --build -d, and stop them with down --remove-orphans, then docker network rm eclipse-net. To send a message by hand: docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka:9092 --topic eclipse-events, then type message 4.

What it does
The producer sends message 1 to 10 (wrapping around) every 10 seconds plus telemetry every 3 seconds. When the consumer reads "message N" it finds row N, merges it and posts it to data-sync; anything else is logged as ignored. Every flush interval data-sync updates last_message_number, last_message_text, last_merged_at and sets sync_status to SYNCED. make seed-data empties the table and inserts rows 1 to 10 again.

Interfaces
data-sync listens on port 8081 inside Docker only: POST /sync-records (answers 202) and GET /health, no login. Kafka is published on port 9092 with no login. Postgres is published on port 5432 with user, database and password all "eclipse", a demo credential.

Tests
There are no unit tests. The script tests/e2e.sh (start with SYNC_INTERVAL_SECONDS=20 make up) resets the table, waits for a row to become SYNCED, and fails unless every SYNCED row holds the right message text and number and both services logged the work. It needs only Docker. The automatic check on GitHub also packages the Java app with Java 17, byte-compiles the Python files, validates both compose files, runs shellcheck, scans for leaked secrets, and runs the end-to-end script.

Files
producer-stack holds Kafka and the producer. consumer-app holds Postgres, the Spring consumer and its database scripts. data-sync is the Python service. Makefile has the commands. tests/e2e.sh is the end-to-end check. .github/workflows/ci.yml is the automatic check. CLAUDE.md is notes for Claude Code.

Known problems, not fixed in this pass
Kafka (no login) and Postgres (password eclipse) are open on all network interfaces of your computer; that is fine on a trusted laptop but bind them to 127.0.0.1 or remove the ports lines on a shared network. data-sync holds its waiting results in memory, so a restart loses anything not yet written.

Design notes
There are two Compose projects joined by a shared network so the producer side can be run or replaced separately; make up handles the extra network step. data-sync writes in timed batches so the consumer never waits on the database. SYNC_INTERVAL_SECONDS and POSTGRES_HOST_PORT are variables whose defaults match the original settings, so tests can shorten the interval and dodge port clashes without editing files.
