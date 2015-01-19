import time
import json

import asyncio

import aiocoap.resource as resource
import aiocoap

#from sensors.mcp3008 import MCP3008
#from sensors.temp_sensor import WaitingSht15


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

## TODO: It seems spidev cannot be compiled under Python3.4, pls confirm this.
##       We, might need to find an alternative for spidev library.
#class Acceleration(resource.Resource):
    #sensor = MCP3008()

    #def __init__(self):
        #super(Acceleration, self).__init__()

    #@asyncio.coroutine
    #def render_GET(self, request):
        #x, y, z = self.sensor.acceleration()
        #payload = json.dumps(\
                            #[{"x": format(x, FLOAT_FORMAT)}, \
                              #{"y": format(y, FLOAT_FORMAT)}, \
                              #{"z": format(z, FLOAT_FORMAT)}], \
                              #sort_keys=True).encode('utf8')
        #response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        #return response


class HelloWorld(resource.Resource):
    def __init__(self):
        super(HelloWorld, self).__init__()

    @asyncio.coroutine
    def render_GET(self, request):
        payload = "Hello World".encode('utf8')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response


class LocalTime(resource.ObservableResource):
    def __init__(self):
        super(LocalTime, self).__init__()

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(1, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        current_time = time.time()
        payload = json.dumps({"time": current_time}).encode('utf8')
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)


## FIXME: SHT15 should be combined and implemented in a single class, differentiated by request
#class Temperature(resource.Resource):
    #temperature = WaitingSht15()

    #def __init__(self, name="TemperatureResource"):
        #super(Temperature, self).__init__(name, visible=True, observable=True, allow_children=False)

    #@asyncio.coroutine
    #def render_GET(self, request, query=None):
        #temp = self.temperature.read_temperature_C()
        #return json.dumps({"temperature": format(temp, FLOAT_FORMAT)})


#class Humidity(resource.Resource):
    #humidity = WaitingSht15()

    #def __init__(self, name="HumidityResource"):
        #super(Humidity, self).__init__(name, visible=True, observable=True, allow_children=False)

    #def render_GET(self, request):
        #humidity = self.humidity.read_humidity()
        #return json.dumps({"temperature": format(humidity, FLOAT_FORMAT)})


#class Temp_Humidity(resource.Resource):
    #temp_hum = WaitingSht15()

    #def __init__(self, name="Temp_HumidityResource"):
        #super(Temp_Humidity, self).__init__(name, visible=True, observable=True, allow_children=False)

    #def render_GET(self, request):
        #temp, humidity = self.temp_hum.read_temperature_and_Humidity()
        #return json.dumps([{"temperature": format(temp, FLOAT_FORMAT)}, \
                           #{"humidity": format(humidity, FLOAT_FORMAT)}], sort_keys=True)
