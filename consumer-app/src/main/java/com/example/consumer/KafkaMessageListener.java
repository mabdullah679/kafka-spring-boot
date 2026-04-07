package com.example.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class KafkaMessageListener {

    private static final Logger log = LoggerFactory.getLogger(KafkaMessageListener.class);
    private final KafkaMessageProcessor kafkaMessageProcessor;

    public KafkaMessageListener(KafkaMessageProcessor kafkaMessageProcessor) {
        this.kafkaMessageProcessor = kafkaMessageProcessor;
    }

    @KafkaListener(topics = "${app.topic-name}", groupId = "${spring.kafka.consumer.group-id}")
    public void onMessage(String payload) {
        log.info("received payload={}", payload);
        kafkaMessageProcessor.process(payload);
    }
}
