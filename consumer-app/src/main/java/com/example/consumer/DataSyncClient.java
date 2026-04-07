package com.example.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class DataSyncClient {

    private static final Logger log = LoggerFactory.getLogger(DataSyncClient.class);

    private final RestClient restClient;
    private final String dataSyncUrl;

    public DataSyncClient(RestClient restClient,
                          @Value("${app.data-sync-url}") String dataSyncUrl) {
        this.restClient = restClient;
        this.dataSyncUrl = dataSyncUrl;
    }

    public void ship(MergedRecordPayload payload) {
        restClient.post()
                .uri(dataSyncUrl)
                .body(payload)
                .retrieve()
                .toBodilessEntity();
        log.info("posted merged record to dataSyncClass id={} messageNumber={}", payload.id(), payload.messageNumber());
    }
}
