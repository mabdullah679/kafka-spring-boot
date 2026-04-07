package com.example.consumer;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "eclipse_records")
public class EclipseRecord {

    @Id
    private Long id;

    @Column(name = "source_name")
    private String sourceName;

    @Column(name = "stored_value")
    private String storedValue;

    public Long getId() {
        return id;
    }

    public String getSourceName() {
        return sourceName;
    }

    public String getStoredValue() {
        return storedValue;
    }
}
