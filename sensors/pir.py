import traceback
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import platform
if platform.machine() != 'x86_64':
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        logger.warning("Could not import the RPi.GPIO package (http://pypi.python.org/pypi/RPi.GPIO). "
                       "Using a mock instead. Notice that this is useful only for the purpose of "
                       "debugging this module, but will not give the end user any useful result.")
        import RPiMock.GPIO as GPIO
    except:
        logger.warning("Could not import the RPi.GPIO package (http://pypi.python.org/pypi/RPi.GPIO). "
                       "Using a mock instead. Notice that this is useful only for the purpose of "
                       "debugging this module, but will not give the end user any useful result.")
        import RPiMock.GPIO as GPIO
        traceback.print_exc(file=sys.stdout)

    PIR_PIN = 13  # Pin 13 = GPIO 27

    class Pir(object):
        def __init__(self, gpio=PIR_PIN , gpioMode=GPIO.BOARD):
            self.gpio = gpio
            GPIO.setmode(gpioMode)

        def has_motion(self):
            GPIO.setup(self.gpio, GPIO.IN)
            if GPIO.input(self.gpio) == GPIO.LOW:
                return False
            else:
                return True

class PirMock():
    motion = True

    def has_motion(self):
        return self.motion