# MQBrokerPy

https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html


## Usage

Run broker,

```
mqbrokerpy
```

```
mosquitto_sub -h 127.0.0.1 -p 1234 -t mytopic -q 1
```

```
mosquitto_pub -h 127.0.0.1 -p 1234 -t mytopic -m mymessage -q 1
```
