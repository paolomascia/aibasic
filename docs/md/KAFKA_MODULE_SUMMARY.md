# Apache Kafka Module - Complete Reference

## Overview

The **Kafka module** provides comprehensive Apache Kafka integration for distributed streaming and event-driven architectures.

**Module Type**: `(kafka)`
**Primary Use Cases**: Event streaming, log aggregation, real-time data pipelines, microservices communication

---

## Configuration

```ini
[kafka]
BOOTSTRAP_SERVERS = localhost:9092
GROUP_ID = aibasic-consumer-group
AUTO_OFFSET_RESET = earliest
```

---

## Basic Operations

```basic
REM Produce messages
10 (kafka) produce message "Order created" to topic "orders"
20 (kafka) produce json {"order_id": 123, "amount": 99.99} to topic "orders"

REM Consume messages
30 (kafka) consume messages from topic "orders"
40 (kafka) consume messages from topic "orders" for 10 seconds
```

---

## Module Information

- **Module Name**: KafkaModule
- **Task Type**: `(kafka)`
- **Dependencies**: `kafka-python>=2.0.2`
