import struct
import time

from pylegoboost.constants import *


class MoveHub(object):
    """
    :type connection: pylegoboost.comms.Connection
    :type led: LED
    """

    def __init__(self, connection):
        self.connection = connection

        self.led = LED(self)
        self.motor_A = EncodedMotor(self, PORT_A)
        self.motor_B = EncodedMotor(self, PORT_B)
        self.motor_AB = EncodedMotor(self, PORT_AB)

        # self.port_c
        # self.port_d

        # self.button
        # self.tilt_sensor

        # transport.write(ENABLE_NOTIFICATIONS_HANDLE, ENABLE_NOTIFICATIONS_VALUE)
        # transport.write(MOVE_HUB_HARDWARE_HANDLE, b'\x0a\x00\x41\x01\x08\x01\x00\x00\x00\x01')


class Peripheral(object):
    """
    :type parent: MoveHub
    """

    def __init__(self, parent):
        super(Peripheral, self).__init__()
        self.parent = parent


class LED(Peripheral):
    def set_color(self, color):
        if color not in COLORS:
            raise ValueError("Color %s is not in list of available colors" % color)

        cmd = CMD_SET_COLOR + chr(color)
        self.parent.connection.write(MOVE_HUB_HARDWARE_HANDLE, cmd)


class EncodedMotor(Peripheral):
    PACKET_VER = b'\x01'
    SET_PORT_VAL = b'\x81'
    MOTOR_TIMED_END = b'\x64\x7f\x03'
    TRAILER = b'\x64\x7f\x03'  # NOTE: \x64 is 100, might mean something
    TIMED_GROUP = b'\x0A'
    TIMED_SINGLE = b'\x09'
    MOVEMENT_TYPE = b'\x11'

    def __init__(self, parent, port):
        super(EncodedMotor, self).__init__(parent)
        if port not in PORTS:
            raise ValueError("Invalid port for motor: %s" % port)
        self.port = port

    def _speed_abs(self, relative):
        relative *= 100
        if relative < 0:
            relative += 255
        return int(relative)

    def timed(self, seconds, speed_primary=1, speed_secondary=None, async=False):
        if speed_primary < -1 or speed_primary > 1:
            raise ValueError("Invalid primary motor speed value: %s", speed_primary)

        if speed_secondary is None:
            speed_secondary = speed_primary

        if speed_secondary < -1 or speed_secondary > 1:
            raise ValueError("Invalid secondary motor speed value: %s", speed_primary)

        time_ms = int(seconds * 1000)

        # set for port
        command = self.SET_PORT_VAL + chr(self.port)

        # movement type
        command += self.MOVEMENT_TYPE
        command += self.TIMED_GROUP if self.port == PORT_AB else self.TIMED_SINGLE

        command += struct.pack('<H', time_ms)

        command += chr(self._speed_abs(speed_primary))

        ###
        if self.port == PORT_AB:
            command += chr(self._speed_abs(speed_secondary))

        command += self.TRAILER

        self.parent.connection.write(MOVE_HUB_HARDWARE_HANDLE, chr(len(command)) + self.PACKET_VER + command)
        if not async:
            time.sleep(seconds)


class ColorDistanceSensor(Peripheral):
    pass
