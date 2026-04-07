package com.example.consumer;

import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class KafkaMessageProcessor {

    private static final Logger log = LoggerFactory.getLogger(KafkaMessageProcessor.class);
    private static final Pattern MESSAGE_PATTERN = Pattern.compile("^message\\s+(\\d+)$");

    private final EclipseRecordRepository repository;
    private final MergedRecordSetter mergedRecordSetter;
    private final DataSyncClient dataSyncClient;

    public KafkaMessageProcessor(EclipseRecordRepository repository,
                                 MergedRecordSetter mergedRecordSetter,
                                 DataSyncClient dataSyncClient) {
        this.repository = repository;
        this.mergedRecordSetter = mergedRecordSetter;
        this.dataSyncClient = dataSyncClient;
    }

    public void process(String payload) {
        Matcher matcher = MESSAGE_PATTERN.matcher(payload.trim());
        if (!matcher.matches()) {
            log.info("ignoring non-business payload={}", payload);
            return;
        }

        long messageNumber = Long.parseLong(matcher.group(1));
        Optional<EclipseRecord> record = repository.findById(messageNumber);
        if (record.isEmpty()) {
            log.info("no db record found for messageNumber={}", messageNumber);
            return;
        }

        MergedRecordPayload mergedRecordPayload = mergedRecordSetter.merge(record.get(), payload, messageNumber);
        dataSyncClient.ship(mergedRecordPayload);
        log.info("merged and shipped record id={} messageNumber={}", record.get().getId(), messageNumber);
    }
}
