import time
import json

import asyncio

import aiocoap.resource as resource
import aiocoap

from resources_def import PayloadTable
from resources_def import UTF8 as UTF8
from resources_def import PayloadWrapper
import resources_def as r_defs

from sensors.mcp3008 import MCP3008
from sensors.temp_sensor import WaitingSht15

FLOAT_FORMAT = '.2f'


# FIXME: This resource is broken
class CoreResource(resource.Resource):
    """
    Example Resource that provides list of links hosted by a server.
    Normally it should be hosted at /.well-known/core

    Notice that self.visible is not set - that means that resource won't
    be listed in the link format it hosts.
    """

    def __init__(self, root):
        resource.Resource.__init__(self)
        self.root = root

    @asyncio.coroutine
    def render_GET(self, request):
        data = []
        self.root.generate_resource_list(data, "")
        payload = ",".join(data).encode(UTF8)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.LINK_FORMAT_CODE

        return response


class HelloWorld(resource.Resource):
    def __init__(self):
        super(HelloWorld, self).__init__()

        self.content = "Hello World"
        self.payload = PayloadTable('hello')

    @asyncio.coroutine
    def render_GET(self, request):
        payload = PayloadWrapper.wrap(self.content, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print("PUT payload: %s" % request.payload)
        self.content = request.payload.decode(UTF8)
        payload = ("PUT %s to resource" % self.content).encode(UTF8)

        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        return response


class LocalTime(resource.ObservableResource):
    def __init__(self):
        super(LocalTime, self).__init__()

        self.observe_period = 10
        self.payload = PayloadTable('local time', True, self.observe_period)

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        # FIXME: local time should be differentiated from timestamp (datetime.now())
        #        e.g. local time = time since last boot
        json_time = json.dumps({'time': time.time()})
        payload = PayloadWrapper.wrap(json_time, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print("PUT %s to resource" % request.payload)
        err_msg = ("argument is not correctly formatted. Follow 'period [sec]' t " \
                   "update period to observe 'time' resource\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response

        if (args[0] == 'period') and (args[1].isdigit() and args[1] != '0'):
            # FIXME: if period = 0, observation should be disabled
            self.observe_period = int(args[1])
            # PUT new value to non-data field requires updating payload wrapper content
            self.payload.set_sample_rate(self.observe_period)
        else:
            return err_response

        payload = ("PUT %s=%s to resource" % (args[0], self.observe_period)).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        return response


class Acceleration(resource.ObservableResource):
    def __init__(self):
        super(Acceleration, self).__init__()

        # It is safe to construct sensor driver as instance variable (i.e. faster
        #   access), since as a resource Acceleration will only have one instance
        self.sensor = MCP3008()

        self.observe_period = 1
        self.payload = PayloadTable('acceleration', True, self.observe_period)

        # start observing resource
        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        x, y, z = self.sensor.acceleration()
        # Wrap data with sensor related information and timestamps
        json_acc = json.dumps([{'x': format(x, FLOAT_FORMAT)},      \
                                {'y': format(y, FLOAT_FORMAT)},     \
                                {'z': format(z, FLOAT_FORMAT)}], sort_keys=True)
        payload = PayloadWrapper.wrap(json_acc, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response


# FIXME: add data wrapper or fix SHT15 class hierarchy
class HygroThermo(resource.ObservableResource):
    temp_hum = WaitingSht15()

    def __init__(self):
        super(HygroThermo, self).__init__()
        self.observe_period = 3
        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    def render_GET(self, request):
        temp, humidity = self.temp_hum.read_temperature_and_Humidity()
        payload = json.dumps([{'temperature': format(temp, FLOAT_FORMAT)},      \
                              {'humidity': format(humidity, FLOAT_FORMAT)}],    \
                             sort_keys=True).encode(UTF8)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response


# FIXME: SHT15 should be combined and implemented in a single class, differentiated by request
class Temperature(resource.ObservableResource):
    temperature = WaitingSht15()

    def __init__(self):
        super(Temperature, self).__init__()

        self.observe_period = 3
        self.payload = PayloadTable('temperature', True, self.observe_period)

        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)
    
    @asyncio.coroutine
    def render_GET(self, request, query=None):
        temp = self.temperature.read_temperature_C()
        json_temp = json.dumps({'temperature': format(temp, FLOAT_FORMAT)})
        payload = PayloadWrapper.wrap(json_temp, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response


# FIXME: add data wrapper or fix SHT15 class hierarchy
class Humidity(resource.ObservableResource):
    humidity = WaitingSht15()

    def __init__(self):
        super(Humidity, self).__init__()
        self.observe_period = 3
        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)
    
    @asyncio.coroutine
    def render_GET(self, request):
        humidity = self.humidity.read_humidity()
        payload = json.dumps({'humidity': format(humidity, FLOAT_FORMAT)}).encode(UTF8)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response
