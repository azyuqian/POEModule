import time
import json
from coapthon2.resources.resource import Resource
from sensors.mcp3008 import MCP3008
from sensors.temp_sensor import WaitingSht15


class Acceleration(Resource):
    sensor = MCP3008()
    def __init__(self, name="AccelerationResource"):
        super(Acceleration, self).__init__(name, visible=True, observable=True, allow_children=False)

    def render_GET(self, request, query=None):
        x, y, z = self.sensor.acceleration()
        return json.dumps({"x": x, "y": y, "z":z})


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
    temp_hum = WaitingSht15()
    def __init__(self, name="Temp_HumidityResource"):
        super(Temp_Humidity, self).__init__(name, visible=True, observable=True, allow_children=False)

    def render_GET(self, request, query=None):
        temp, humidity = self.temp_hum.read_temperature_and_Humidity()
        return json.dumps({"temperature": temp, "humidity": humidity})
