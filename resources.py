import time
import json
from coapthon2.resources.resource import Resource
from sensors.mcp3008 import MCP3008
from sensors.temp_sensor import WaitingSht1x


class Acceleration(Resource):
    def __init__(self, name="AccelerationResource"):
        super(Acceleration, self).__init__(name, visible=True, observable=True, allow_children=False)

        sensor = MCP3008()

    def render_GET(self, request, query=None):
        x, y, z = self.sensor.acceleration()
        return response


class HelloWorld(Resource):
    def __init__(self, name="HelloWorldResource"):
        super(HelloWorld, self).__init__(name, visible=True, observable=True, allow_children=False)

    def render_GET(self, request, query=None):
        return 'hello world'


class LocalTime(Resource):
    def __init__(self, name="LocalTimeResource"):
        super(LocalTime, self).__init__(name, visible=True, observable=True, allow_children=False)

    def render_GET(self, request, query=None):
        current_time = time.time()
        print current_time
        return json.dumps({"time": current_time})

class Temp_Humidity(Resource):
    def __init__(self, name="Temp_HumidityResource"):
        super(Temp_Humidity, self).__init__(name, visible=True, observable=True, allow_children=False)

        temp_hum = WaitingSht1x()

    def render_GET(self, request, query=None):
        temp, hum = self.temp_hum.read_temperature_and_Humidity()
        return response
        
        
    
