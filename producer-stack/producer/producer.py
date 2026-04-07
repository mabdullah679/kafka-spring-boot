import json
import os
import socket
import time
from datetime import datetime, timezone

from confluent_kafka import Producer


BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "eclipse-events")
MESSAGE_INTERVAL_SECONDS = int(os.getenv("MESSAGE_INTERVAL_SECONDS", "10"))
TELEMETRY_INTERVAL_SECONDS = int(os.getenv("TELEMETRY_INTERVAL_SECONDS", "3"))
MAX_MESSAGE_SEQUENCE = int(os.getenv("MAX_MESSAGE_SEQUENCE", "10"))
CONTAINER_NAME = socket.gethostname()


def build_business_message(sequence: int) -> str:
    return f"message {sequence}"


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

    business_sequence = 1
    telemetry_sequence = 1
    last_message_at = 0.0

    while True:
        now = time.monotonic()

        if now - last_message_at >= MESSAGE_INTERVAL_SECONDS:
            business_message = build_business_message(business_sequence)
            producer.produce(TOPIC_NAME, key="message", value=business_message)
            producer.flush(10)
            print(f"sent business message: {business_message}", flush=True)
            last_message_at = now
            business_sequence = 1 if business_sequence == MAX_MESSAGE_SEQUENCE else business_sequence + 1

        telemetry_message = build_telemetry_message(telemetry_sequence)
        producer.produce(TOPIC_NAME, key="telemetry", value=telemetry_message)
        producer.flush(10)
        print(f"sent telemetry #{telemetry_sequence}: {telemetry_message}", flush=True)
        telemetry_sequence = 1 if telemetry_sequence == MAX_MESSAGE_SEQUENCE else telemetry_sequence + 1
        time.sleep(TELEMETRY_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
