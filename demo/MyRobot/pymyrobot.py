#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import struct
import time
import serial


def setup_serial_connect(port, baudrate, timeout=None):
    serial_api = serial.Serial()
    serial_api.port = port
    serial_api.baudrate = baudrate
    serial_api.timeout = timeout
    serial_api.rts = False
    serial_api.open()
    return serial_api


class Utils:
    @classmethod
    def process_data_command(cls, args):
        if not args:
            return []

        processed_args = []
        for index in range(len(args)):
            if isinstance(args[index], list):
                data = cls.encode_int16(args[index])
                processed_args.extend(data)
            else:
                processed_args.append(args[index])

        return cls.flatten(processed_args)

    @classmethod
    def flatten(cls, datas):
        flat_list = []
        for item in datas:
            if not isinstance(item, list):
                flat_list.append(item)
            else:
                flat_list.extend(cls.flatten(item))
        return flat_list

    @classmethod
    def float(cls, number, decimal=2):
        return round(number / 10 ** decimal, 2)

    @classmethod
    def encode_int16(cls, data):
        if isinstance(data, int):
            return [
                ord(i) if isinstance(i, str) else i
                for i in list(struct.pack(">h", data))
            ]
        else:
            res = []
            for v in data:
                t = cls.encode_int16(v)
                res.extend(t)
            return res

    @classmethod
    def decode_int16(cls, data):
        return struct.unpack(">h", data)[0]

    @classmethod
    def crc16_check(cls, command):
        crc = 0xffff
        for index in range(len(command)):
            crc ^= command[index]
            for _ in range(8):
                if crc & 1 == 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        if crc > 0x7FFF:
            crc_res = list(struct.pack(">H", crc))
        else:
            crc_res = cls.encode_int16(crc)

        for i in range(2):
            if isinstance(crc_res[i], str):
                crc_res[i] = ord(crc_res[i])
        return crc_res

    @classmethod
    def crc16_check_bytes(cls, command):
        data = cls.crc16_check(command)
        return bytes(bytearray(data))

    @classmethod
    def get_bits(cls, data):
        reverse_bins = reversed(bin(data)[2:])
        rank = [i for i, e in enumerate(reverse_bins) if e != '0']
        return rank


class MyRobot:
    def __init__(self, port, baudrate, timeout=None):
        self.serial_api = setup_serial_connect(port, baudrate, timeout)

    def _read_by_timeout(self, timeout=1.0):
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = self.serial_api.read(1)
            if len(data) == 0:
                continue

            yield data

    def _read_command_buffer(self, start_flag_caller, end_flag_caller, timeout=1.0):
        channel_buffer = b""
        real_command = b""
        is_record = False

        for data in self._read_by_timeout(timeout):
            channel_buffer += data

            start_flag = start_flag_caller()
            if channel_buffer.endswith(start_flag) and is_record is False:
                real_command = start_flag
                is_record = True
                continue

            if is_record is False:
                continue

            real_command += data
            end_flag = end_flag_caller(real_command)
            if real_command.endswith(end_flag):
                break
        else:
            real_command = b""
        return real_command

    def read_pressure_value(self):
        self.serial_api.reset_input_buffer()
        self.serial_api.reset_output_buffer()

        reply_data = self._read_command_buffer(
            start_flag_caller=lambda: b'\xfe\xfe',
            end_flag_caller=lambda cmds: Utils.crc16_check_bytes(cmds[:-2]),
            timeout=20
        )
        if reply_data is None:
            return None

        respond = []
        respond_body = reply_data[4:-2]
        for i in range(0, len(respond_body), 2):
            data = Utils.decode_int16(respond_body[i:i + 2])
            respond.append(data)
        return respond

