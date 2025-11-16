# MQTT Module - Complete Reference

## Overview

The **MQTT module** provides comprehensive MQTT (Message Queuing Telemetry Transport) integration for IoT and pub/sub messaging. MQTT is a lightweight messaging protocol designed for constrained devices and low-bandwidth, high-latency networks, making it ideal for IoT applications.

**Module Type:** `(mqtt)`
**Primary Use Cases:** IoT device communication, sensor networks, home automation, industrial IoT, telemetry, pub/sub messaging

---

## Table of Contents

1. [Features](#features)
2. [Configuration](#configuration)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [Common Use Cases](#common-use-cases)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Features

### Core Capabilities

- **Publish/Subscribe**: Topic-based message routing
- **Quality of Service (QoS)**: Three levels (0, 1, 2)
- **Retained Messages**: Last message stored on broker
- **Last Will and Testament (LWT)**: Automatic disconnect notifications
- **Topic Wildcards**: Single-level (+) and multi-level (#)
- **TLS/SSL Support**: Encrypted connections
- **JSON Support**: Easy structured data publishing
- **Auto-Reconnection**: Automatic resubscription after connection loss
- **Lightweight Protocol**: Optimized for IoT and constrained networks

### Quality of Service Levels

| QoS | Name | Description | Use Case |
|-----|------|-------------|----------|
| **0** | At most once | Fire and forget | High-frequency telemetry |
| **1** | At least once | Acknowledged delivery | Important messages |
| **2** | Exactly once | Guaranteed delivery | Critical data |

---

## Configuration

### Basic Configuration (aibasic.conf)

```ini
[mqtt]
BROKER = mqtt.example.com
PORT = 1883
USERNAME = mqtt_user
PASSWORD = mqtt_password
CLIENT_ID = aibasic_mqtt_client
KEEPALIVE = 60
CLEAN_SESSION = true
QOS = 1
USE_TLS = false
CA_CERTS = /path/to/ca.pem
LWT_TOPIC = devices/status
LWT_PAYLOAD = offline
LWT_QOS = 1
LWT_RETAIN = true
```

### Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `BROKER` | MQTT broker hostname | `localhost` | Yes |
| `PORT` | MQTT broker port | `1883` | No |
| `USERNAME` | MQTT username | - | No |
| `PASSWORD` | MQTT password | - | No |
| `CLIENT_ID` | Unique client identifier | Auto-generated | No |
| `KEEPALIVE` | Keepalive interval (seconds) | `60` | No |
| `CLEAN_SESSION` | Start with clean session | `true` | No |
| `QOS` | Default QoS level (0, 1, 2) | `1` | No |
| `USE_TLS` | Enable TLS/SSL | `false` | No |
| `CA_CERTS` | CA certificate file | - | No |
| `LWT_TOPIC` | Last Will topic | - | No |
| `LWT_PAYLOAD` | Last Will message | - | No |
| `LWT_QOS` | Last Will QoS | `1` | No |
| `LWT_RETAIN` | Retain Last Will | `false` | No |

---

## Basic Operations

### Connect and Publish

```basic
REM Connect to broker
10 (mqtt) connect to broker

REM Publish simple message
20 (mqtt) publish "Hello IoT!" to topic "sensors/temperature"

REM Publish with QoS
30 (mqtt) publish "Critical data" to topic "alerts/critical" with qos 2

REM Publish with retain flag
40 (mqtt) publish "Device Online" to topic "device/status" with retain true

REM Disconnect
50 (mqtt) disconnect
```

### Subscribe and Receive

```basic
REM Subscribe to topic
10 (mqtt) subscribe to topic "sensors/temperature"

REM Subscribe to multiple topics
20 (mqtt) subscribe to topic "sensors/#"

REM Wait for messages
30 (mqtt) wait for messages for 10 seconds

REM Unsubscribe
40 (mqtt) unsubscribe from topic "sensors/temperature"
```

### JSON Messages

```basic
REM Publish JSON data
10 (mqtt) publish json {"temperature": 25.5, "humidity": 60, "timestamp": "2025-01-15T10:30:00Z"} to topic "sensors/room1"

REM Subscribe and parse JSON
20 (mqtt) subscribe to topic "sensors/room1"
30 (mqtt) wait for messages for 5 seconds
```

---

## Advanced Features

### Topic Wildcards

```basic
REM Single-level wildcard (+)
10 (mqtt) subscribe to topic "home/+/temperature"
REM Matches: home/livingroom/temperature, home/bedroom/temperature

REM Multi-level wildcard (#)
20 (mqtt) subscribe to topic "sensors/#"
REM Matches: sensors/temp, sensors/room1/temp, sensors/room1/data/temp
```

### Last Will and Testament (LWT)

```basic
REM Set Last Will message (sent when client disconnects unexpectedly)
10 (mqtt) set last will topic "device/status" message "offline" with qos 1 and retain true

20 (mqtt) connect to broker

REM If connection is lost, broker sends LWT message automatically
```

### Retained Messages

```basic
REM Publish retained message (stored on broker)
10 (mqtt) publish "Device v1.2.3" to topic "device/version" with retain true

REM New subscribers receive last retained message immediately
20 (mqtt) subscribe to topic "device/version"

REM Clear retained message
30 (mqtt) clear retained message on topic "device/version"
```

### Quality of Service

```basic
REM QoS 0: At most once (fire and forget)
10 (mqtt) publish "Fast data" to topic "telemetry/speed" with qos 0

REM QoS 1: At least once (acknowledged)
20 (mqtt) publish "Important data" to topic "alerts/warning" with qos 1

REM QoS 2: Exactly once (guaranteed delivery)
30 (mqtt) publish "Critical command" to topic "control/shutdown" with qos 2
```

---

## Common Use Cases

### 1. IoT Sensor Data Collection

```basic
REM Temperature sensor publishing data every 5 seconds
10 (mqtt) connect to broker

20 FOR i = 1 TO 100
30   LET temperature = 20 + (i MOD 10) * 0.5
40   LET humidity = 50 + (i MOD 20)
50
60   LET sensor_data = {
70     "sensor_id": "TEMP_001",
80     "temperature": temperature,
90     "humidity": humidity,
100    "timestamp": "now()"
110  }
120
130  (mqtt) publish json sensor_data to topic "sensors/room1/data" with qos 1
140
150  SLEEP 5
160 NEXT i

170 (mqtt) disconnect
```

### 2. Smart Home Automation

```basic
REM Smart home control system
10 (mqtt) connect to broker

20 REM Subscribe to all device commands
30 (mqtt) subscribe to topic "home/+/command"

40 REM Subscribe to sensor data
50 (mqtt) subscribe to topic "home/+/sensor"

60 REM Motion detected - turn on lights
70 (mqtt) publish json {"action": "turn_on", "brightness": 100} to topic "home/livingroom/lights/command"

80 REM Temperature control
90 IF temperature > 25 THEN
100  (mqtt) publish json {"action": "set_temperature", "value": 22} to topic "home/climate/command"
110 END IF

120 REM Wait for messages
130 (mqtt) wait for messages for 60 seconds

140 (mqtt) disconnect
```

### 3. Industrial IoT Monitoring

```basic
REM Factory machine monitoring
10 (mqtt) connect to broker

20 REM Subscribe to all machines
30 (mqtt) subscribe to topic "factory/machine/+/status"
40 (mqtt) subscribe to topic "factory/machine/+/alerts"

50 REM Publish machine status
60 LET machine_status = {
70   "machine_id": "MACHINE_001",
80   "status": "running",
90   "temperature": 45.5,
100  "pressure": 2.3,
110  "vibration": 0.05,
120  "runtime_hours": 12345
130 }

140 (mqtt) publish json machine_status to topic "factory/machine/001/status" with qos 1

150 REM Alert on high temperature
160 IF machine_status["temperature"] > 50 THEN
170  (mqtt) publish "High temperature alert" to topic "factory/machine/001/alerts" with qos 2
180 END IF

190 (mqtt) wait for messages for 10 seconds
200 (mqtt) disconnect
```

### 4. Vehicle Telemetry

```basic
REM Vehicle GPS and telemetry data
10 (mqtt) connect to broker

20 FOR i = 1 TO 1000
30   LET telemetry = {
40     "vehicle_id": "VEH_12345",
50     "latitude": 40.7128 + (i * 0.0001),
60     "longitude": -74.0060 + (i * 0.0001),
70     "speed": 55 + (i MOD 20),
80     "fuel_level": 75 - (i * 0.01),
90     "engine_temp": 85 + (i MOD 15),
100    "timestamp": "now()"
110  }
120
130  (mqtt) publish json telemetry to topic "fleet/vehicle/12345/telemetry" with qos 0
140
150  SLEEP 1
160 NEXT i

170 (mqtt) disconnect
```

### 5. Environmental Monitoring

```basic
REM Weather station data
10 (mqtt) connect to broker

20 REM Set LWT for station offline detection
30 (mqtt) set last will topic "weather/station/001/status" message "offline" with qos 1 and retain true

40 REM Publish online status
50 (mqtt) publish "online" to topic "weather/station/001/status" with retain true

60 REM Publish weather data
70 FOR i = 1 TO 100
80   LET weather_data = {
90     "station_id": "WEATHER_001",
100    "temperature": 15 + (i MOD 20),
110    "humidity": 65 + (i MOD 30),
120    "pressure": 1013 + (i MOD 10),
130    "wind_speed": 10 + (i MOD 15),
140    "wind_direction": i MOD 360,
150    "rainfall": i MOD 5,
160    "timestamp": "now()"
170  }
180
190  (mqtt) publish json weather_data to topic "weather/station/001/data" with qos 1
200
210  SLEEP 60
220 NEXT i

230 (mqtt) disconnect
```

---

## Best Practices

### Topic Design

1. **Hierarchical Structure**: Use levels for organization
   - Good: `home/livingroom/temperature`
   - Bad: `home-livingroom-temperature`

2. **Specific to General**: Left to right
   - `country/city/building/floor/room/device/sensor`

3. **Avoid Leading Slash**: Don't start with `/`
   - Good: `sensors/temperature`
   - Bad: `/sensors/temperature`

4. **Use Descriptive Names**: Clear and meaningful
   - Good: `factory/machine/001/temperature`
   - Bad: `f/m/1/t`

### QoS Selection

1. **QoS 0**: High-frequency telemetry, non-critical data
2. **QoS 1**: Most messages (balanced)
3. **QoS 2**: Critical commands, financial data

### Connection Management

1. **Set Unique Client ID**: Avoid conflicts
2. **Use Clean Session = False**: For persistent subscriptions
3. **Implement Reconnection**: Handle network failures
4. **Set Appropriate Keepalive**: 60-300 seconds

### Security

1. **Use TLS/SSL**: Always in production
2. **Strong Authentication**: Username/password or certificates
3. **Topic ACLs**: Restrict pub/sub permissions
4. **Regular Updates**: Keep broker and clients updated

---

## Troubleshooting

### Common Issues

**Connection Refused**

```
Issue: "Connection refused"
Solution:
- Verify BROKER hostname and PORT
- Check firewall allows connections
- Verify broker is running
- Check authentication credentials
```

**Messages Not Received**

```
Issue: "Subscribed but not receiving messages"
Solution:
- Verify topic name matches exactly
- Check QoS level compatibility
- Ensure subscription succeeded
- Verify publisher is connected
```

**High Latency**

```
Issue: "Messages delayed"
Solution:
- Check network bandwidth
- Use QoS 0 for non-critical data
- Reduce message frequency
- Consider message compression
```

**Connection Drops**

```
Issue: "Frequent disconnections"
Solution:
- Increase KEEPALIVE interval
- Check network stability
- Verify broker capacity
- Implement reconnection logic
```

---

## API Reference

### Connection Methods

- `connect()` - Connect to MQTT broker
- `disconnect()` - Disconnect from broker
- `is_connected()` - Check connection status

### Publish Methods

- `publish(topic, payload, qos, retain)` - Publish message
- `publish_json(topic, data, qos, retain)` - Publish JSON
- `publish_retained(topic, payload, qos)` - Publish retained
- `clear_retained(topic)` - Clear retained message

### Subscribe Methods

- `subscribe(topic, qos)` - Subscribe to topic
- `unsubscribe(topic)` - Unsubscribe from topic
- `wait_for_messages(timeout)` - Wait for incoming messages

### Last Will Methods

- `set_last_will(topic, payload, qos, retain)` - Set LWT

---

## MQTT Brokers

Popular MQTT brokers:

- **Mosquitto**: Open-source, lightweight (Eclipse)
- **HiveMQ**: Enterprise-grade, scalable
- **EMQX**: Massive scale, IoT platform
- **AWS IoT Core**: Managed AWS service
- **Azure IoT Hub**: Managed Azure service

---

## Module Information

- **Module Name**: MQTTModule
- **Task Type**: `(mqtt)`
- **Dependencies**: `paho-mqtt>=1.6.1`
- **Python Version**: 3.7+
- **AIbasic Version**: 1.0+

---

*For more examples, see [example_mqtt.aib](../../examples/example_mqtt.aib)*
