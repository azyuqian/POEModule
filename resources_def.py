#import json

""" CoAP content format codes by media types
    Reference [RFC7252, Section 12.3]: http://tools.ietf.org/html/rfc7252 """
# plain text/string encoded in utf-8
TEXT_PLAIN_CODE = 0
# application/link-format: describe hosted resources, attributes and relationships
LINK_FORMAT_CODE = 40
# application/json
JSON_FORMAT_CODE = 50

# Constant definitions
UTF8 = 'utf-8'

NAME_FIELD = "name"
ACTIVE_FIELD = "active"
SAMPLE_R_FIELD = "rate"
DATA_FIELD = "data"
TIME_FIELD = "time"


class PayloadTable(dict):
    """ defaults to construct an empty table """
    def __init__(self, name='', is_active=False, rate=0):
        dict.__init__(self)
        dict.__setitem__(self, NAME_FIELD, name)
        dict.__setitem__(self, ACTIVE_FIELD, is_active)
        dict.__setitem__(self, SAMPLE_R_FIELD, rate)
        dict.__setitem__(self, DATA_FIELD, "")  # json.dumps('')
        dict.__setitem__(self, TIME_FIELD, "")

    def __missing__(self, key):
        raise KeyError('The key {} not defined'.format(key))

    def set_name(self, name):
        dict.__setitem__(self, NAME_FIELD, name)

    def set_active(self, is_active):
        dict.__setitem__(self, ACTIVE_FIELD, is_active)

    def set_sample_rate(self, rate):
        dict.__setitem__(self, SAMPLE_R_FIELD, rate)

    def set_data(self, data):
        dict.__setitem__(self, DATA_FIELD, data)

    def set_time(self, time):
        dict.__setitem__(self, TIME_FIELD, time)


