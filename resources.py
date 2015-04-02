import time
import json
import asyncio

import aiocoap.resource as resource
import aiocoap

from resources_def import PayloadTable
from resources_def import UTF8 as UTF8
from resources_def import PayloadWrapper
import resources_def as r_defs

import platform
if platform.machine() == 'x86_64':
    from sensors.mcp3008 import MCP3008Mock as MCP3008
    from sensors.temp_sensor import WaitingSht15Mock as WaitingSht15
    from sensors.pir import PirMock as Pir
else:
    from sensors.mcp3008 import MCP3008
    from sensors.temp_sensor import WaitingSht15
    from sensors.pir import Pir

# FIXME: Add logging


class RootResource(resource.Resource):
    """
    Example Resource that provides list of links hosted by a server.
    Normally it should be hosted at /
    """

    def __init__(self, root):
        resource.Resource.__init__(self)
        self.root = root

    @asyncio.coroutine
    def render_POST(self, request):
        payload = request.payload.decode(UTF8)

        try:
            jpayload = json.loads(payload)
        except Exception as e:
            # JSON parsing error
            err_msg = ("Invalid JSON format: " + str(e)).encode(UTF8)
            err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
            err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE
            return err_response

        try:
            path = jpayload['url']
            resource_name = jpayload['name']
        except Exception as e:
            # Invalid JSON contents
            err_msg = ("Invalid JSON contents: " + str(e)).encode(UTF8)
            err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
            err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE
            return err_response

        # Try to locate the resource class using its name(resource_name)
        if resource_name in IMPLEMENTED_RESOURCES:
            self.root.add_resource(tuple(path.split('/')), IMPLEMENTED_RESOURCES[resource_name]())
        # Use template resource if resource name is not known
        else:
            try:
                active = jpayload['active']
                period = jpayload['frequency']
                channel = jpayload['channel']
            except Exception as e:
                # Invalid JSON contents
                err_msg = ("Invalid JSON contents: " + str(e)).encode(UTF8)
                err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
                err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE
                return err_response

            try:
                min = jpayload['min']
                max = jpayload['max']
            # In case of min/max is not given
            except KeyError:
                self.root.add_resource(tuple(path.split('/')),
                                       ResourceTemplate(name=resource_name,
                                                        active=active,
                                                        period=period,
                                                        channel=channel))
            else:
                self.root.add_resource(tuple(path.split('/')),
                                       ResourceTemplate(name=resource_name,
                                                        active=active,
                                                        period=period,
                                                        min=min,
                                                        max=max,
                                                        channel=channel))

        # Refresh server
        asyncio.async(aiocoap.Context.create_server_context(self.root))

        payload = "Successful add {} at /{}/".format(resource_name, path).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CREATED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE
        return response


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
        self.payload = PayloadTable('time', True, self.observe_period)

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
        # FIXME: This should probably be formatted with corresponding error code
        err_msg = ("argument is not correctly formatted. Follow 'period [sec]' to " \
                   "update period to observe 'time' resource\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response

        # Observe with period = 0 is not allowed
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


class Alert(resource.ObservableResource):
    def __init__(self):
        self.count = 0

        super(Alert, self).__init__()

        self.observe_period = 1
        self.payload = PayloadTable('alert', True, self.observe_period)

        self.notify()
        self.alert_status = False

        # TODO: Should be an earthquake detection algorithm
        ## Not tested
        # self.sensor = MCP3008()

    def notify(self):
        # Only update resource if an alert is raised
        if self.detect_alert():
          self.alert_status = True
          self.updated_state()
        else:
          asyncio.get_event_loop().call_later(self.observe_period, self.notify)


    def detect_alert(self):
        # TODO: Should be an earthquake detection algorithm
        ## Not tested
        #THRESHOLD = 1.5
        #total_acceleration = sum(self.sensor.acceleration)
        #if total_acceleration > THRESHOLD:
          #return True

        if self.count > 10:
          return True
        else:
          self.count = self.count + 1
          return False

    @asyncio.coroutine
    def render_GET(self, request):
        json_status = json.dumps({"alert": self.alert_status})
        payload = PayloadWrapper.wrap(json_status, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        self.alert_status = False
        self.count = 0

        json_status = json.dumps({"alert": self.alert_status})
        payload = PayloadWrapper.wrap(json_status, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response


class Adc8Channel(resource.ObservableResource):
    # ADC driver must be a class variable, because possibly >1 instances may
    #   be initialized as child of Adc8Channel class
    mcp3008 = MCP3008()

    def __init__(self):
        super(Adc8Channel, self).__init__()


class Acceleration(Adc8Channel):
    def __init__(self):
        super(Acceleration, self).__init__()

        self.observe_period = 1
        self.fp_format = r_defs.DEFAULT_FP_FORMAT

        self.payload = PayloadTable('acceleration', True, self.observe_period)

        # start observing resource
        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        x, y, z = self.mcp3008.acceleration()
        # Wrap data with sensor related information and timestamps
        json_acc = json.dumps({'x': format(x, self.fp_format),
                               'y': format(y, self.fp_format),
                               'z': format(z, self.fp_format)}, sort_keys=True)
        payload = PayloadWrapper.wrap(json_acc, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print("PUT %s to resource" % request.payload)
        # FIXME: This should probably be formatted with corresponding error code
        # FIXME: Various error messages for different PUT methods
        err_msg = ("argument is not correctly formatted. Follow 'period [sec]' to " \
                   "update period to observe 'acceleration' resource\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response

        # Observe with period = 0 is not allowed
        if (args[0] == 'period') and (args[1].isdigit() and args[1] != '0'):
            self.observe_period = int(args[1])
            # PUT new value to non-data field requires updating payload wrapper content
            self.payload.set_sample_rate(self.observe_period)
        elif args[0] == 'decimal':
            self.fp_format = '.{}f'.format(int(args[1]))
        else:
            return err_response

        payload = ("PUT %s=%s to resource" % (args[0], args[1])).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        return response


class Joystick(Adc8Channel):
    def __init__(self):
        super(Joystick, self).__init__()

        self.observe_period = 1
        self.fp_format = r_defs.DEFAULT_FP_FORMAT

        self.payload = PayloadTable('joystick', True, self.observe_period)

        # start observing resource
        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        leftright, updown = self.mcp3008.joystick()
        # Wrap data with sensor related information and timestamps
        jdata = json.dumps({'leftright': format(leftright, self.fp_format),
                            'updown': format(updown, self.fp_format)}, sort_keys=True)
        payload = PayloadWrapper.wrap(jdata, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print("PUT %s to resource" % request.payload)
        # FIXME: This should probably be formatted with corresponding error code
        # FIXME: Various error messages for different PUT methods
        err_msg = ("argument is not correctly formatted. Follow 'period [sec]' to " \
                   "update period to observe 'joystick' resource\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response

        # Observe with period = 0 is not allowed
        if (args[0] == 'period') and (args[1].isdigit() and args[1] != '0'):
            self.observe_period = int(args[1])
            # PUT new value to non-data field requires updating payload wrapper content
            self.payload.set_sample_rate(self.observe_period)
        elif args[0] == 'decimal':
            self.fp_format = '.{}f'.format(int(args[1]))
        else:
            return err_response

        payload = ("PUT %s=%s to resource" % (args[0], args[1])).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        return response


class HygroThermo(resource.ObservableResource):
    # Sensor driver must be a class variable, because HygroThermo class may
    #   be initialized more than once
    driver = WaitingSht15()

    def __init__(self):
        super(HygroThermo, self).__init__()


class Temperature(HygroThermo):
    def __init__(self):
        super(Temperature, self).__init__()

        self.observe_period = 3
        self.fp_format = r_defs.DEFAULT_FP_FORMAT
        self.payload = PayloadTable('temperature', True, self.observe_period)

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request, query=None):
        temp = self.driver.read_temperature_C()
        json_temp = json.dumps({'temperature': format(temp, self.fp_format)})
        payload = PayloadWrapper.wrap(json_temp, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print("PUT %s to resource" % request.payload)
        # FIXME: This should probably be formatted with corresponding error code
        # FIXME: Various error messages for different PUT methods
        err_msg = ("argument is not correctly formatted.\n\n"                           \
                   "Follow 'period [sec]' to update period to observe 'temperature'"    \
                   "resource. [sec] > 2.\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response

        # Observe with period = 0 is not allowed
        if (args[0] == 'period') and (args[1].isdigit() and args[1] != '0'):
            new_period = int(args[1])
            # Physical constraint of the sensor does not allow update faster than 1 sec;
            #   double the value to improve reliability
            if new_period <= 2:
                return err_response
            self.observe_period = new_period
            # PUT new value to non-data field requires updating payload wrapper content
            self.payload.set_sample_rate(self.observe_period)
        elif args[0] == 'decimal':
            self.fp_format = '.{}f'.format(int(args[1]))
        else:
            return err_response

        payload = ("PUT %s=%s to resource" % (args[0], args[1])).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        return response


class Humidity(HygroThermo):
    def __init__(self):
        super(Humidity, self).__init__()

        self.observe_period = 3
        self.fp_format = r_defs.DEFAULT_FP_FORMAT
        self.payload = PayloadTable('humidity', True, self.observe_period)

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        humidity = self.driver.read_humidity()
        json_humidity = json.dumps({'humidity': format(humidity, self.fp_format)})
        payload = PayloadWrapper.wrap(json_humidity, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        #print("PUT %s to resource" % request.payload)
        # FIXME: This should probably be formatted with corresponding error code
        # FIXME: Various error messages for different PUT methods
        err_msg = ("argument is not correctly formatted.\n\n"                           \
                   "Follow 'period [sec]' to update period to observe 'humidity'"       \
                   "resource. [sec] > 2.\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response

        # Observe with period = 0 is not allowed
        if (args[0] == 'period') and (args[1].isdigit() and args[1] != '0'):
            new_period = int(args[1])
            # Physical constraint of the sensor does not allow update faster than 1 sec;
            #   double the value to improve reliability
            if new_period <= 2:
                return err_response
            self.observe_period = new_period
            # PUT new value to non-data field requires updating payload wrapper content
            self.payload.set_sample_rate(self.observe_period)
        elif args[0] == 'decimal':
            self.fp_format = '.{}f'.format(int(args[1]))
        else:
            return err_response

        payload = ("PUT %s=%s to resource" % (args[0], args[1])).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        return response


class Motion(resource.ObservableResource):
    def __init__(self):
        super(Motion, self).__init__()

        self.driver = Pir()

        self.observe_period = 1
        self.fp_format = r_defs.DEFAULT_FP_FORMAT

        self.payload = PayloadTable('motion', True, self.observe_period)

        # start observing resource
        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)

    @asyncio.coroutine
    def render_GET(self, request):
        has_motion = self.driver.has_motion()
        # Wrap data with sensor related information and timestamps
        jmotion = json.dumps({'motion': str(has_motion)})
        payload = PayloadWrapper.wrap(jmotion, self.payload)

        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE

        return response


class ResourceTemplate(resource.ObservableResource):
    def __init__(self, name=None, active=False, period=3, min=0, max=1023, channel=0):
        super(ResourceTemplate, self).__init__()
        
        self.observe_period = period
        self.fp_format = r_defs.DEFAULT_FP_FORMAT
        self.sensor = MCP3008()
        self.active = active
        self.channel = channel
        self.min = min
        self.max = max
        self.name = name

        self.payload = PayloadTable(name, self.active, self.observe_period)
        
        self.notify()
    
    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(self.observe_period, self.notify)
    
    @asyncio.coroutine
    def render_GET(self, request):
        reading = self.sensor.read_channel_raw(self.channel)
        reading_conv = ((reading/1024) * (self.max-self.min)) + self.min
        json_temp_resource = json.dumps({self.name: format(reading_conv, self.fp_format)})
        payload = PayloadWrapper.wrap(json_temp_resource, self.payload)
        
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        response.opt.content_format = r_defs.JSON_FORMAT_CODE
        
        return response

    @asyncio.coroutine
    def render_PUT(self, request):
        err_msg = ("argument is not correctly formatted.\n\n"                           \
                    "Follow 'period [sec]' to update period to observe 'humidity'"       \
                    "resource. [sec] > 2.\n\n").encode(UTF8)
        err_response = aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=err_msg)
        err_response.opt.content_format = r_defs.TEXT_PLAIN_CODE

        args = request.payload.decode(UTF8).split()
        if len(args) != 2:
            return err_response
            
        # Observe with period = 0 is not allowed
        if (args[0] == 'period') and (args[1].isdigit() and args[1] != '0'):
            new_period = int(args[1])
            # Physical constraint of the sensor does not allow update faster than 1 sec;
            #   double the value to improve reliability
            if new_period <= 2:
                return err_response
            self.observe_period = new_period
            # PUT new value to non-data field requires updating payload wrapper content
            self.payload.set_sample_rate(self.observe_period)
        elif args[0] == 'min':
            self.min = int(args[1])
        elif args[0] == 'max':
            self.max = int(args[1])
        elif args[0] == 'channel':
            self.channel = int(args[1])
        elif args[0] == 'decimal':
            self.fp_format = '.{}f'.format(int(args[1]))
        else:
            return err_response
            
        payload = ("PUT %s=%s to resource" % (args[0], args[1])).encode(UTF8)
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        response.opt.content_format = r_defs.TEXT_PLAIN_CODE
        
        return response

# Define the resources can be added dynamically
IMPLEMENTED_RESOURCES = {'hello': HelloWorld,
                         'time': LocalTime,
                         'alert': Alert,
                         'acceleration': Acceleration,
                         'joystick': Joystick,
                         'temperature': Temperature,
                         'humidity': Humidity,
                         'motion': Motion}
