# RabbitMQ Module - Complete Reference

## Overview

The **RabbitMQ module** provides comprehensive RabbitMQ message broker integration for reliable message queuing.

**Module Type**: `(rabbitmq)`
**Primary Use Cases**: Message queuing, task distribution, microservices communication, async processing

---

## Configuration

```ini
[rabbitmq]
HOST = localhost
PORT = 5672
USERNAME = guest
PASSWORD = guest
QUEUE_NAME = tasks
EXCHANGE_NAME = events
```

---

## Basic Operations

```basic
10 (rabbitmq) publish message "Process order #123" to queue "tasks"
20 (rabbitmq) consume messages from queue "tasks"
30 (rabbitmq) create exchange "events" with type "fanout"
40 (rabbitmq) bind queue "notifications" to exchange "events"
```

---

## Module Information

- **Module Name**: RabbitMQModule
- **Task Type**: `(rabbitmq)`
- **Dependencies**: `pika>=1.3.2`
