#!/usr/bin/python
# -*- coding:utf-8 -*-

from enum import Enum


class FramerType(str, Enum):
    """Type of Modbus frame."""

    RAW = "raw"  # only used for testing
    ASCII = "ascii"
    RTU = "rtu"
    SOCKET = "socket"
    TLS = "tls"
