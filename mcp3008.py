# This script provides interface with 8-channel ADC converter MCP3008
import time
import os
import spidev


class SPIDevice(object):
    self.spi = spidev.SpiDev()


class MCP3008(SPIDevice)
    # Channel names and chip select
    MCP3008_CH0 = 0
    MCP3008_CH1 = 1
    MCP3008_CH2 = 2
    MCP3008_CH3 = 3
    MCP3008_CH4 = 4
    MCP3008_CH5 = 5
    MCP3008_CH6 = 6
    MCP3008_CH7 = 7

    MCP3008_CS0 = 0
    MCP3008_CS1 = 1

    ACC_X_CH = MCP3008_CH0
    ACC_Y_CH = MCP3008_CH1
    ACC_Z_CH = MCP3008_CH2

    # Commands and operation modes
    MCP3008_START = 0x01
    #MCP3008_DIFF = 0x0
    MCP3008_SINGLE = 0x8

    def _read_channel_raw(channel):
        self.spi.open(0, MCP3008_CS0)

        # 3-byte command to read a 10 bit data from MCP3008:
        # 1st byte contains only Start Bit, then operation mode and channel select
        adc = spi.xfer2([MCP3008_START, (MCP3008_SINGLE + channel) << 4, 0])

        # last 10 bits out of 3 bytes are received data
        data = ((adc[1] & 0x03) << 8) + adc[2]

        self.spi.close()
        return data

    def _read_channel(channel):
        # TO-DO: need to decide what information we want to convert to
        #       - degree? (for gyro)
        #       - accelerometer? (for vibration)
        return self._read_channel_raw(channel)

    def acceleration(self):
        x = self._read_channel(ACC_X_CH)
        y = self._read_channel(ACC_Y_CH)
        z = self._read_channel(ACC_Z_CH)
        return x, y, z
