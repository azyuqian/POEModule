import time
from coapthon2.resources.resource import Resource
from sensors.mcp3008 import MCP3008


class Acceleration(Resource):
    def __init__(self, name="AccelerationResource"):
        super(Acceleration, self).__init__(name, visible=True, observable=True, allow_children=False)

        sensor = MCP3008()

    def render_GET(self, request, query=None):
        x, y, z = self.sensor.acceleration()
        return response


class HelloWorld(Resource):
    def __init__(self, name="AccelerationResource"):
        super(HelloWorld, self).__init__(name, visible=True, observable=True, allow_children=False)

    def render_GET(self, request, query=None):
        return 'hello world'