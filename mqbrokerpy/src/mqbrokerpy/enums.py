from enum import auto
from enum import Enum


class ControlPacketType(Enum):
    RESERVED = 0
    CONNECT = auto()
    CONNACK = auto()
    PUBLISH = auto()
    PUBACK = auto()
    PUBREC = auto()
    PUBREL = auto()
    PUBCOMP = auto()
    SUBSCRIBE = auto()
    SUBACK = auto()
    UNSUBSCRIBE = auto()
    UNSUBACK = auto()
    PINGREQ = auto()
    PINGRESP = auto()
    DISCONNECT = auto()
    AUTH = auto()
