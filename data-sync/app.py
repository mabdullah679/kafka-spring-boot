import logging
import os
import threading
import time
from datetime import datetime, timezone

import psycopg
from flask import Flask, jsonify, request


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eclipse:eclipse@postgres:5432/eclipse")
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))
PORT = int(os.getenv("PORT", "8081"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
pending_records = {}
pending_lock = threading.Lock()


@app.post("/sync-records")
def receive_record():
    payload = request.get_json(force=True)
    record_id = int(payload["id"])
    with pending_lock:
        pending_records[record_id] = payload
    app.logger.info("buffered merged record id=%s messageNumber=%s", record_id, payload["messageNumber"])
    return jsonify({"status": "accepted", "recordId": record_id}), 202


@app.get("/health")
def health():
    return jsonify({"status": "ok", "bufferedRecords": len(pending_records)})


def flush_pending_records():
    while True:
        time.sleep(SYNC_INTERVAL_SECONDS)
        with pending_lock:
            batch = list(pending_records.values())
            pending_records.clear()

        if not batch:
            app.logger.info("no merged records pending for sync")
            continue

        with psycopg.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                for payload in batch:
                    merged_at = datetime.fromisoformat(payload["mergedAt"].replace("Z", "+00:00"))
                    cursor.execute(
                        """
                        UPDATE eclipse_records
                        SET last_message_number = %s,
                            last_message_text = %s,
                            last_merged_at = %s,
                            sync_status = %s
                        WHERE id = %s
                        """,
                        (
                            int(payload["messageNumber"]),
                            payload["messageText"],
                            merged_at,
                            "SYNCED",
                            int(payload["id"]),
                        ),
                    )
            connection.commit()

        app.logger.info("flushed %s merged record(s) to postgres at %s", len(batch), datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    app.logger.info("starting data-sync with interval=%s seconds", SYNC_INTERVAL_SECONDS)
    threading.Thread(target=flush_pending_records, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
