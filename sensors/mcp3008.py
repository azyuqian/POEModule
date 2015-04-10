# This script provides interface with 8-channel ADC converter MCP3008
import platform

if platform.machine() != 'x86_64':
    import spidev

    class SPIDevice(object):
        spi = spidev.SpiDev()

    class MCP3008(SPIDevice):
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

        # Commands and operation modes
        MCP3008_START = 0x01
        #MCP3008_DIFF = 0x0
        MCP3008_SINGLE = 0x8

        # Accelerometer definitions
        ACC_X_CH = MCP3008_CH0
        ACC_Y_CH = MCP3008_CH1
        ACC_Z_CH = MCP3008_CH2
        AXIS_X = 0
        AXIS_Y = 1
        AXIS_Z = 2
        # Joystick definitions
        JOYSTICK_LR_CH = MCP3008_CH3
        JOYSTICK_UD_CH = MCP3008_CH4

        # Digital data received is in range 0~1023:
        # Reference point zero acceleration on x, y, z axis,
        #   number below reference point represents negative acceleration
        ZERO_G_REF = [512, 502, 522]
        # delta per g (m/s^2)
        DELTA_PER_G = [102, 104, 102]

        def _read_channel_raw(self, channel):
            self.spi.open(0, self.MCP3008_CS0)

            # 3-byte command to read a 10 bit data from MCP3008:
            # 1st byte contains only Start Bit, then operation mode and channel select
            adc = self.spi.xfer2([self.MCP3008_START, (self.MCP3008_SINGLE + channel) << 4, 0])

            # last 10 bits out of 3 bytes are received data
            data = ((adc[1] & 0x03) << 8) + adc[2]

            self.spi.close()
            return data

        # FIXME: This structure may have some issues. Accelerometer device should be an individual class /
        #       based on MCP3008 channels
        def _convert_raw_to_g(self, raw_acc, axis):
            return (float(raw_acc - self.ZERO_G_REF[axis])) / self.DELTA_PER_G[axis]

        def read_channel_raw(self, channel):
            return self._read_channel_raw(channel)

        def acceleration(self):
            # Raw data is converted to g (m/s^2) before output
            x = self._convert_raw_to_g(self._read_channel_raw(self.ACC_X_CH), self.AXIS_X)
            y = self._convert_raw_to_g(self._read_channel_raw(self.ACC_Y_CH), self.AXIS_Y)
            z = self._convert_raw_to_g(self._read_channel_raw(self.ACC_Z_CH), self.AXIS_Z)
            return x, y, z

        def joystick(self):
            leftright = self._read_channel_raw(self.JOYSTICK_LR_CH)
            updown = self._read_channel_raw(self.JOYSTICK_UD_CH)
            return leftright, updown


class MCP3008Mock():
    import random
    random.seed()

    # default parameters
    adc = [0xff, 0xff, 0xff]
    x = 1.0
    y = 0.0
    z = 0.0
    leftright = 516
    updown = 510

    def read_channel_raw(self, channel):
        self.adc[1] = self.random.randint(0, 0xff)
        self.adc[2] = self.random.randint(0, 0xff)
        return ((self.adc[1] & 0x03) << 8) + self.adc[2]

    def acceleration(self):
        # Theoretical limits provided by datasheet
        # https://www.sparkfun.com/datasheets/Components/SMD/adxl335.pdf
        self.x = self.random.uniform(-3.0, 3.0)
        self.y = self.random.uniform(-3.0, 3.0)
        self.z = self.random.uniform(-3.0, 3.0)
        return self.x, self.y, self.z

    def joystick(self):
        # Experimental limits at 3.3V
        self.leftright = self.random.randint(260, 763)
        self.updown = self.random.randint(253, 769)
        return self.leftright, self.updown
