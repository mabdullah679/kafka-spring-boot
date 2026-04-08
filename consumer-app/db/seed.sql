TRUNCATE TABLE eclipse_records;

INSERT INTO eclipse_records (id, source_name, stored_value, last_message_number, last_message_text, last_merged_at, sync_status) VALUES
    (1, 'record-1', 'stored payload 1', NULL, NULL, NULL, 'PENDING'),
    (2, 'record-2', 'stored payload 2', NULL, NULL, NULL, 'PENDING'),
    (3, 'record-3', 'stored payload 3', NULL, NULL, NULL, 'PENDING'),
    (4, 'record-4', 'stored payload 4', NULL, NULL, NULL, 'PENDING'),
    (5, 'record-5', 'stored payload 5', NULL, NULL, NULL, 'PENDING'),
    (6, 'record-6', 'stored payload 6', NULL, NULL, NULL, 'PENDING'),
    (7, 'record-7', 'stored payload 7', NULL, NULL, NULL, 'PENDING'),
    (8, 'record-8', 'stored payload 8', NULL, NULL, NULL, 'PENDING'),
    (9, 'record-9', 'stored payload 9', NULL, NULL, NULL, 'PENDING'),
    (10, 'record-10', 'stored payload 10', NULL, NULL, NULL, 'PENDING');
