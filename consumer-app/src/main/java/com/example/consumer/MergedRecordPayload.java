package com.example.consumer;

import java.time.Instant;

public record MergedRecordPayload(
        Long id,
        String sourceName,
        String storedValue,
        Long messageNumber,
        String messageText,
        Instant mergedAt
) {
}
