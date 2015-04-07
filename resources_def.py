import json
import datetime

from defs import *

# payload wrapper fields
NAME_FIELD = 'name'
ACTIVE_FIELD = 'active'
SAMPLE_R_FIELD = 'rate'
DATA_FIELD = 'data'
TIME_FIELD = 'time'


class PayloadWrapper:
    @staticmethod
    def wrap(data, wrapper):
        wrapper.set_time(str(datetime.datetime.now()))
        wrapper.set_data(data)

        return json.dumps(wrapper).encode(UTF8)


class PayloadTable(dict):
    """ defaults to construct an empty table """
    def __init__(self, name='', is_active=False, rate=0):
        dict.__init__(self)
        dict.__setitem__(self, NAME_FIELD, name)
        dict.__setitem__(self, ACTIVE_FIELD, is_active)
        dict.__setitem__(self, SAMPLE_R_FIELD, rate)
        dict.__setitem__(self, DATA_FIELD, '')
        dict.__setitem__(self, TIME_FIELD, '')

    def __missing__(self, key):
        raise KeyError("The key {} not defined".format(key))

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


