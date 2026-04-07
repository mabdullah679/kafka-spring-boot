import json
import os
import socket
import time
from datetime import datetime, timezone

from confluent_kafka import Producer


BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "eclipse-events")
HELLO_INTERVAL_SECONDS = int(os.getenv("HELLO_INTERVAL_SECONDS", "10"))
TELEMETRY_INTERVAL_SECONDS = int(os.getenv("TELEMETRY_INTERVAL_SECONDS", "3"))
CONTAINER_NAME = socket.gethostname()


def build_hello_message() -> str:
    return f"Hello from {CONTAINER_NAME}."


def build_telemetry_message(sequence: int) -> str:
    payload = {
        "type": "telemetry",
        "container": CONTAINER_NAME,
        "sequence": sequence,
        "cpuLoad": round((sequence * 7 % 100) / 10, 2),
        "memoryMb": 128 + (sequence % 32),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload)


def main() -> None:
    producer = Producer(
        {
            "bootstrap.servers": BOOTSTRAP_SERVERS,
            "client.id": CONTAINER_NAME,
        }
    )

    print(f"Producing to topic '{TOPIC_NAME}' on {BOOTSTRAP_SERVERS} from {CONTAINER_NAME}", flush=True)

    sequence = 1
    last_hello_at = 0.0

    while True:
        now = time.monotonic()

        if now - last_hello_at >= HELLO_INTERVAL_SECONDS:
            hello_message = build_hello_message()
            producer.produce(TOPIC_NAME, key="greeting", value=hello_message)
            producer.flush(10)
            print(f"sent greeting: {hello_message}", flush=True)
            last_hello_at = now

        telemetry_message = build_telemetry_message(sequence)
        producer.produce(TOPIC_NAME, key="telemetry", value=telemetry_message)
        producer.flush(10)
        print(f"sent telemetry #{sequence}: {telemetry_message}", flush=True)
        sequence += 1
        time.sleep(TELEMETRY_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
