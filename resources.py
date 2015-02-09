import time
import datetime
import json

import asyncio

import aiocoap.resource as resource
import aiocoap

from resources_def import PayloadTable
from sensors.mcp3008 import MCP3008
from sensors.temp_sensor import WaitingSht15

FLOAT_FORMAT = '.2f'
# CoAP content format for application/json defined by RFC4627
JSON_FORMAT_CODE = 50
TEXT_FORMAT_CODE = 0


def wrap_data(self, data, wrapper):
    wrapper.set_time(str(datetime.datetime.now()))
    wrapper.set_data(data)

    return json.dumps(wrapper).encode('utf-8')


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
        payload = ",".join(data).encode('utf-8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = 40
        return response


class Acceleration(resource.ObservableResource):
    sensor = MCP3008()

    def __init__(self):
        super(Acceleration, self).__init__()

        self.observe_period = 1
        self.payload = PayloadTable("acceleration", True, self.observe_period)

        # start observing resource
        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        x, y, z = self.sensor.acceleration()
        # Wrap data with sensor related information and timestamps

        json_acc = json.dumps([{"x": format(x, FLOAT_FORMAT)},      \
                                {"y": format(y, FLOAT_FORMAT)},     \
                                {"z": format(z, FLOAT_FORMAT)}], sort_keys=True)
        payload = wrap_data(json_acc, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = JSON_FORMAT_CODE  # application/json: 50
        return response


class HelloWorld(resource.Resource):
    def __init__(self):
        super(HelloWorld, self).__init__()

        self.content = 'Hello World'
        self.payload = PayloadTable("hello")

    @asyncio.coroutine
    def render_GET(self, request):
        payload = wrap_data(self.content, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = JSON_FORMAT_CODE  # application/json: 50
        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print('PUT payload: %s' % request.payload)
        self.content = request.payload.decode('utf8')

        payload = ("PUT %s to resource" % self.content).encode('utf-8')

        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = TEXT_FORMAT_CODE  # text/plain: 0
        return response


class LocalTime(resource.ObservableResource):
    def __init__(self):
        super(LocalTime, self).__init__()

        self.observe_period = 10
        self.payload = PayloadTable("local time", True, self.observe_period)

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        # FIXME: local time should be differentiated from timestamp (datetime.now())
        #        e.g. local time = time since last boot
        json_time = json.dumps({"time": time.time()})
        payload = wrap_data(json_time, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = JSON_FORMAT_CODE  # application/json: 50
        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        print('PUT %s to resource' % request.payload)
        err_msg = ("argument is not correctly formatted. Follow 'period [sec]' t " \
                   "update period to observe 'time' resource\n\n").encode('utf-8')
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = TEXT_FORMAT_CODE

        args = request.payload.decode('utf-8').split()
        if len(args) != 2:
            return err_response

        if (args[0] == "period") and (args[1].isdigit() and args[1] != "0"):
            # FIXME: if period = 0, observation should be disabled
            self.observe_period = int(args[1])
        else:
            return err_response

        # FIXME: should indicate what parameter is changed in returned string
        payload = ("PUT %s to resource" % self.observe_period).encode('utf-8')
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = TEXT_FORMAT_CODE  # text/plain: 0

        return response


# FIXME: SHT15 should be combined and implemented in a single class, differentiated by request
class Temperature(resource.ObservableResource):
    temperature = WaitingSht15()

    def __init__(self):
        super(Temperature, self).__init__()

        self.observe_period = 3
        self.payload = PayloadTable("temperature", True, self.observe_period)

        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)
    
    @asyncio.coroutine
    def render_GET(self, request, query=None):
        temp = self.temperature.read_temperature_C()
        json_temp = json.dumps({"temperature": format(temp, FLOAT_FORMAT)})

        payload = wrap_data(json_temp, self.payload)
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = JSON_FORMAT_CODE  # application/json: 50

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
        payload = json.dumps({"Humidity": format(humidity, FLOAT_FORMAT)}).encode('utf-8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response


# FIXME: add data wrapper or fix SHT15 class hierarchy
class Temp_Humidity(resource.ObservableResource):
    temp_hum = WaitingSht15()
    
    def __init__(self):
        super(Temp_Humidity, self).__init__()
        self.observe_period = 3
        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)
    
    def render_GET(self, request):
        temp, humidity = self.temp_hum.read_temperature_and_Humidity()
        payload = json.dumps([{"temperature": format(temp, FLOAT_FORMAT)},      \
                              {"humidity": format(humidity, FLOAT_FORMAT)}],    \
                             sort_keys=True).encode('utf-8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response
