#!/home/pi
#--------------------------------------------------------------------  
# This script provides interface with 8-channel ADC converter MCP3008 
#
# Author : Yaodong Yu
# Date   : Nov.13, 2014
#
# http://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

import spidev
import time
import os

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

ACC_X_CH = CH0
ACC_Y_CH = CH1
ACC_Z_CH = CH2

# Commands and operation modes
MCP3008_START = 0x01
#MCP3008_DIFF = 0x0
MCP3008_SINGLE = 0x8

# Sensor sample rate


# Function to read SPI data from MCP3008 chip
# Param(in): channel - must be an integer 0-7
def ReadChannel(channel):

    # 3-byte command to read a 10 bit data from MCP3008:
    # 1st byte contains only Start Bit, then operation mode and channel select
    adc = spi.xfer2([MCP3008_START, (MCP3008_SINGLE + channel) << 4, 0])

    # last 10 bits out of 3 bytes are received data
    data = ((adc[1] & 0x03) << 8) + adc[2]

    return data
  


# TO-DO(yyu): The following code should be modified and moved to a higher
#               level script

# Function to convert 10-bit digital accelerometer data to meaningful info
def ConvertAcc(raw_acc):
    # TO-DO: need to decide what information we want to convert to
    #       - degree? (for gyro)
    #       - accelerometer? (for vibration)
    return raw_acc


# Main code:
def read_acc(delay):
    # Open SPI bus
    spi = spidev.SpiDev()
    spi.open(0, MCP3008_CS0)

    while True:

        # Read accelerometer data
        temp_acc_x = ReadChannel(ACC_X_CH)
        temp_acc_y = ReadChannel(ACC_Y_CH)
        temp_acc_z = ReadChannel(ACC_Z_CH)

        # Convert accelerometer from 0~1023 to meaningful measurement
        acc_x = ConvertAcc(temp_acc_x)
        acc_y = ConvertAcc(temp_acc_y)
        acc_z = ConvertAcc(temp_acc_z)

        # Print out results
        print "--------------------------------------------"  
        print("Accelerometer: x - {}, y - {} , z - {}".format(acc_x, acc_y, acc_z))  

        # Wait before repeating loop
        time.sleep(delay)
 
