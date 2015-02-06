import time
import json

import asyncio

import aiocoap.resource as resource
import aiocoap

from sensors.mcp3008 import MCP3008
from sensors.temp_sensor import WaitingSht15


FLOAT_FORMAT = '.2f'


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
        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        x, y, z = self.sensor.acceleration()
        payload = json.dumps(\
                            [{"x": format(x, FLOAT_FORMAT)}, \
                              {"y": format(y, FLOAT_FORMAT)}, \
                              {"z": format(z, FLOAT_FORMAT)}], \
                              sort_keys=True).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response


class HelloWorld(resource.Resource):
    def __init__(self):
        super(HelloWorld, self).__init__()
        self.content = "Hello World".encode('utf8')

    @asyncio.coroutine
    def render_GET(self, request):
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=self.content)
        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        print('PUT payload: %s' % request.payload)
        self.content = request.payload
        payload = ("PUT %s to resource" % self.content.decode('utf8')).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        return response


class LocalTime(resource.ObservableResource):
    def __init__(self):
        super(LocalTime, self).__init__()

        self.observe_period = 10
        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        current_time = time.time()
        payload = json.dumps({"time": current_time}).encode('utf8')
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

    @asyncio.coroutine
    def render_PUT(self, request):
        print('PUT %s to resource' % request.payload)
        err_msg = "argument is not correctly formatted. Follow 'period [sec]' to " \
                    "update period to observe 'time' resource\n\n"
        err_payload = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)

        args = request.payload.decode('utf8').split()
        if (len(args) != 2):
            return err_payload

        if (args[0] == "period") and (args[1].isdigit() and args[1] != "0"):
            self.observe_period = int(args[1])
        else:
            return err_payload

        payload = ("PUT %s to resource" % self.observe_period).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        return response


## FIXME: SHT15 should be combined and implemented in a single class, differentiated by request
class Temperature(resource.ObservableResource):
    temperature = WaitingSht15()

    def __init__(self):
        super(Temperature, self).__init__()
        self.observe_period = 3
        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)
    
    @asyncio.coroutine
    def render_GET(self, request, query=None):
        temp = self.temperature.read_temperature_C()
        payload = json.dumps({"temperature": format(temp, FLOAT_FORMAT)}).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response


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
        payload = json.dumps({"Humidity": format(humidity, FLOAT_FORMAT)}).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response

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
        payload = json.dumps([{"temperature": format(temp, FLOAT_FORMAT)}, \
                           {"humidity": format(humidity, FLOAT_FORMAT)}], sort_keys=True).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response



