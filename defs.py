from enum import Enum

# string encode format
UTF8 = 'utf-8'
# default resource data decimal format (2 digits after decimal points)
DEFAULT_FP_FORMAT = '.{}f'.format(2)

""" CoAP content format codes by media types
    Reference [RFC7252, Section 12.3]: http://tools.ietf.org/html/rfc7252 """
# plain text/string encoded in utf-8
TEXT_PLAIN_CODE = 0
# application/link-format: describe hosted resources, attributes and relationships
LINK_FORMAT_CODE = 40
# application/json
JSON_FORMAT_CODE = 50


# FIXME: resource name should be dynamic
#        this is only for demonstration purpose (talk with MATLAB/Octave script),
#           and only work with pre-defined resources
demo_resources = ['temperature',
                  'humidity',
                  'acceleration',
                  'motion',
                  'joystick']
