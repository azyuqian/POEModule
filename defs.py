from enum import Enum

# string encode format
UTF8 = 'utf-8'
# default resource data decimal format (2 digits after decimal points)
DEFAULT_FP_FORMAT = '.{}f'.format(2)


# FIXME: resource name should be dynamic
#        this is only for demonstration purpose (talk with MATLAB/Octave script),
#           and only work with pre-defined resources
resource_code = {
    'unknown': -1,

    'temperature': 1,
    'humidity': 2,
    'acceleration': 3
}
