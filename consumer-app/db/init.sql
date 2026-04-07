CREATE TABLE IF NOT EXISTS eclipse_records (
    id BIGINT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    stored_value VARCHAR(255) NOT NULL,
    last_message_number BIGINT,
    last_message_text VARCHAR(255),
    last_merged_at TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'PENDING'
);

INSERT INTO eclipse_records (id, source_name, stored_value, sync_status) VALUES
    (1, 'record-1', 'stored payload 1', 'PENDING'),
    (2, 'record-2', 'stored payload 2', 'PENDING'),
    (3, 'record-3', 'stored payload 3', 'PENDING'),
    (4, 'record-4', 'stored payload 4', 'PENDING'),
    (5, 'record-5', 'stored payload 5', 'PENDING'),
    (6, 'record-6', 'stored payload 6', 'PENDING'),
    (7, 'record-7', 'stored payload 7', 'PENDING'),
    (8, 'record-8', 'stored payload 8', 'PENDING'),
    (9, 'record-9', 'stored payload 9', 'PENDING'),
    (10, 'record-10', 'stored payload 10', 'PENDING')
ON CONFLICT (id) DO NOTHING;
