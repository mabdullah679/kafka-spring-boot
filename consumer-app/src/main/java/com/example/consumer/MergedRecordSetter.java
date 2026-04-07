package com.example.consumer;

import java.time.Instant;

import org.springframework.stereotype.Component;

@Component
public class MergedRecordSetter {

    public MergedRecordPayload merge(EclipseRecord record, String messageText, long messageNumber) {
        return new MergedRecordPayload(
                record.getId(),
                record.getSourceName(),
                record.getStoredValue(),
                messageNumber,
                messageText,
                Instant.now()
        );
    }
}
