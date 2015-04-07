import sys
import time
import logging
import json
import asyncio
import socket
import functools
import signal


from aiocoap import *
from defs import *

# Default client configuration:
# IP is (local) 127.0.0.1
server_IP = 'localhost'
# resources independent from hardware implementation
resources = {'hello': {'url': 'hello'},
             'time': {'url': 'time'}}
# Octave plotting data file
data_file = 'data.txt'
# flag to enable Octave plotting
run_demo = False
# asyncio event loop for client
# Keep a record so that it can be switched back after observation
client_event_loop = asyncio.get_event_loop()

try:
    from oct2py import octave
except Exception as e:
    print("{}: Not running demo files".format(e))
    run_demo = False
else:
    run_demo = True


logging.basicConfig(level=logging.INFO)
# FIXME: Add logging function to replace "print" in the code


def plot_octave(jpayload):
    '''
    Example:
        octave.database_init('data.txt')
        acceleration:              x  y  z  tem,  hum   year  mon day hh  mm  ss
        octave.update_plot('data.txt', [3, 3, 3, None, None, 1111, 11, 11, 11, 11, 11])
        octave.save_database('data.txt')
    '''
    if run_demo is True and jpayload['name'] in resources:
        #print("payload is {}".format(jpayload))
        time = []
        data = []
        plot_i = -1

        try:
            jvalue = json.loads(jpayload['data'])
            #print("{}".format(jvalue))
            '''
            if jpayload['name'] == 'acceleration':
                data += [float(jvalue['x']), float(jvalue['y']), float(jvalue['z']),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN')]
            elif jpayload['name'] == 'temperature':
                data += [float('NaN'), float('NaN'), float('NaN'),
                         float(jvalue['temperature']),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN')]
            elif jpayload['name'] == 'humidity':
                data += [float('NaN'), float('NaN'), float('NaN'), float('NaN'),
                         float(jvalue['humidity']),
                         float('NaN'), float('NaN'), float('NaN')]
            elif jpayload['name'] == 'motion':
                data += [float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'),
                         bool(jvalue['motion']),
                         float('NaN'), float('NaN')]
            elif jpayload['name'] == 'joystick':
                data += [float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'),
                         float(jvalue['leftright']), float(jvalue['updown'])]
            else:
                print("Warning: Unknown data\n")
                data += [float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'), float('NaN')]
            '''
            if jpayload['name'] == 'joystick':
                data += [float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'),
                         float(jvalue['leftright']), float(jvalue['updown'])]
                plot_i = 1;
            elif jpayload['name'] == 'temperature':
                data += [float('NaN'), float('NaN'), float('NaN'),
                         float(jvalue['temperature']),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN')]
                plot_i = 2;
            elif jpayload['name'] == 'humidity':
                data += [float('NaN'), float('NaN'), float('NaN'), float('NaN'),
                         float(jvalue['humidity']),
                         float('NaN'), float('NaN'), float('NaN')]
                plot_i = 3;
            else:
                print("Unknown data. Skip plotting...\n")
                return
        except Exception as e:
            raise AttributeError("Failed to parse data for demo: {}".format(e))

        # Parse payload data
        import re
        time_str = re.split('[- :]', jpayload['time'])
        try:
            for i in range(5):
                time += [int(time_str[i])]
            time += [float(time_str[5])]
        except Exception as e:
            time = [0, 0, 0, 0, 0, 0.0]
            print("Failed to parse time: {}, using:".format(e, time))
        data += time

        print("data to plot: {}".format(data))

        try:
            octave.demo_update(data_file, data, plot_i)
        except Exception as e:
            raise RuntimeError("Failed to plot: {}".format(e));


def incoming_data(response):
    global run_demo

    payload = response.payload.decode(UTF8)

    if response.opt.content_format is not JSON_FORMAT_CODE:
        print("Result:\n{}: {}".format(response.code, payload))
    else:
        jpayload = json.loads(payload)
        print("Result (JSON):\n{}: {}".format(response.code, jpayload))

        try:
            plot_octave(jpayload)
        except Exception as e:
            print("{}".format(e))
            print("Disabling Octave script...")
            run_demo = False


def end_observation(loop):
    # FIXME: method should actually end observation on server.
    #       Now, it only deals with client side

    print("Observation ended by user interrupt...")
    # Terminate observation event loop
    loop.close()
    print("Observation loop ended...")

    # Restore event loop
    asyncio.set_event_loop(client_event_loop)
    print("Switched back to client console...")

@asyncio.coroutine
def post_impl(jargs):
    context = yield from Context.create_client_context()

    request = Message(code=POST, payload=jargs.encode(UTF8))
    request.set_request_uri('coap://{}/'.format(server_IP))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        raise RuntimeError("Failed to create new resource: {}".format(e))
    else:
        incoming_data(response)

@asyncio.coroutine
def get_impl(url='', payload=""):
    context = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://{}/{}'.format(server_IP, url))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        raise RuntimeError("Failed to fetch resource: {}".format(e))
    else:
        incoming_data(response)

@asyncio.coroutine
def put_impl(url='', payload=""):
    context = yield from Context.create_client_context()

    yield from asyncio.sleep(2)

    request = Message(code=PUT, payload=payload.encode(UTF8))
    request.set_request_uri('coap://{}/{}'.format(server_IP, url))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        raise RuntimeError("Failed to update resource: {}".format(e))
    else:
        incoming_data(response)

@asyncio.coroutine
def observe_impl(url='', payload=""):
    context = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://{}/{}'.format(server_IP, url))

    request.opt.observe = 0
    observation_is_over = asyncio.Future()

    requester = context.request(request)

    requester.observation.register_errback(observation_is_over.set_result)
    requester.observation.register_callback(lambda data: incoming_data(data))

    try:
        response_data = yield from requester.response
    except socket.gaierror as e:
        raise NameError("Name resolution error: {}".format(e))

    if response_data.payload:
        incoming_data(response_data)
    if not response_data.code.is_successful():
        raise RuntimeError("Observation failed!")

    exit_reason = yield from observation_is_over
    print("Observation exits due to {}".format(exit_reason))


def client_console():
    global run_demo

    # First, print general info and help menu on console when client starts
    print("Connecting to server {}...\n".format(server_IP))
    print("Probing available resources...")

    # Temporarily disable plotting
    run_demo_cache = run_demo
    run_demo = False
    for r in resources:
        # Test GET for each known resource
        yield from Commands.do_resource(r, 'GET')
        print("Success! Resource {} is available at path /{}\n".format(r, resources[r]['url']))
    print("Done probing...")
    # Restore plotting configuration
    run_demo = run_demo_cache

    print("Initializing command prompt...\n")
    Commands.do_help()

    # Start acquiring user input
    while True:
        cmdline = input(">>>")
        cmd_parts = cmdline.split()

        # Handle empaty input
        if len(cmd_parts) is 0:
            continue

        #print("cmd = {}".format(cmd_parts))
        cmd = cmd_parts[0]
        args = cmd_parts[1:]

        try:
            method = getattr(Commands, 'do_' + cmd)
        except AttributeError:
            if cmd in resources:
                try:
                    yield from Commands.do_resource(cmd, *args)
                except Exception as e:
                    print("Error: {}".format(e))
            else:
                print("Error: no such command.")

        else:
            try:
                # do_help and do_IP are not asyncio coroutine
                if method.__name__ == 'do_help' or method.__name__ == 'do_IP':
                    method(*args)
                else:
                    yield from method(*args)
            except Exception as e:
                print("Error: {}".format(e))


class Commands():
    @staticmethod
    def do_help(command=None):
        """ print help menu

        If no command is given, list all available commands;
        otherwise, show __doc__ of given command.
        Example: >>>help time

        :param command: of which command help is needed
        :type command: str
        """
        if command:
            print(getattr(Commands, 'do_'+command).__doc__)
        else:
            commands = [cmd[3:] for cmd in dir(Commands)
                        if cmd.startswith('do_') and cmd != 'do_resource']
            print("Valid commands: " + ", ".join(commands))
            print("Valid resources: " + ", ".join(resources))
            print("\n'help [command]' or 'help resource' for more details\n")

    @staticmethod
    def do_ip(ip=None):
        """ read or change server IP
            default IP is given by config.json upon client initialization

        If no parameter is given, return server IP;
        otherwise, set server IP to given value
        Example: >>>IP 192.168.2.20
        Example: >>>IP localhost
        Example: >>>IP

        :param ip: server IP to set
        :type ip: str
        """
        global server_IP

        if ip is None:
            print("Server IP: {}".format(server_IP))
        else:
            print("Server IP was {}".format(server_IP))
            server_IP = ip
            print("Server IP is set to {}".format(IP))

    @staticmethod
    @asyncio.coroutine
    def do_add(name, *args):
        """ add new resource to server

        Syntax: >>>add [name] -c [ADC_channel] (-u [url]) (-l [min] -m [max])
                        (-o) (-f [observe_frequency]) (-h)
        -h --help   detailed help page of arguments

        Example: >>>add new_r -c0 -u myR/r1 -l0 -m10 -o -f5

        :param name: name of the resource
        :type code: str
        :param args: option or payload of PUT request
        :type args: str
        """
        import argparse

        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument('-c', '--channel', help="ADC channel this resource is connected to")
        p.add_argument('-u', '--url', help="new URL for the resource to post")
        p.add_argument('-l', '--min', help="lower bound of resource data")
        p.add_argument('-m', '--max', help="higher bound of resource data")
        p.add_argument('-o', '--observe', help="Set the resource to be observable", action='store_true')
        p.add_argument('-f', '--frequency', help="Set the frequency of observable")

        options = p.parse_args(args)

        # channel number is not optional
        if not options.channel:
            raise AttributeError("ADC Channel not found")
        else:
            try:
                channel = int(options.channel)
            except ValueError as e:
                raise ValueError("Channel must be integer")

        # default value of other options
        url = name
        active = False
        frequency = 0
        b_range = False
        min = None
        max = None

        if options.url:
            url = options.url
        else:
            print("Warning: use resource name ({}) as url".format(name))

        if options.min and options.max:
            try:
                min = int(options.min)
                max = int(options.max)
                b_range = True
            except ValueError as e:
                raise ValueError("Value range must be integer")

        if options.observe:
            active = True

            # only set frequency if resource is observable
            if options.frequency:
                try:
                    frequency = int(options.frequency)
                except ValueError as e:
                    raise ValueError("Observing frequency must be integer")

        # add new resource to resource list
        resources[name] = {'url': url,
                           'channel': channel,
                           'active': active,
                           'frequency': frequency}
        if b_range is True:
            resources[name]['min'] = min
            resources[name]['max'] = max

        # convert resource to payload (add name field)
        payload = resources[name]
        payload['name'] = name

        try:
            yield from post_impl(json.dumps(payload))
        except Exception as e:
            raise RuntimeError("Failed to complete CoAP request: {}".format(e))

    @staticmethod
    @asyncio.coroutine
    def do_resource(name, code='GET', *args):
        """ General implementation of resource command for GET/PUT

        Syntax: >>>[resource] [code] ([-o]) ([payload])
        resource: full resource list can be acquired by help command
        code: GET/PUT
        -o: observe

        :param name: name of the resource
        :type code: str
        :param code: type of CoAP request
        :type code: str
        :param args: option or payload of PUT request
        :type args: str
        """
        payload = " ".join(args)
        try:
            resource = resources[name]
            url = resource['url']
        except AttributeError and IndexError as e:
            raise AttributeError("Resource name or url not found: {}".format(e))

        #print("do_resource: payload={}".format(payload))
        try:
            if code == 'GET':
                if payload.startswith('-o'):
                    if resource['active'] is True:
                        # Create new event loop for observation
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        try:
                            # Set keyboard interrupt as method to end observation
                            for signame in ('SIGINT', 'SIGTERM'):
                                loop.add_signal_handler(getattr(signal, signame),
                                                        functools.partial(end_observation, loop))

                            print("Observation running forever...")
                            print("Press Ctrl + c to end observation")

                            loop.run_until_complete(observe_impl(url))
                        finally:
                            # In case of exceptions, must terminate observation loop and
                            #   switch back to client event loop
                            loop.close()
                            asyncio.set_event_loop(client_event_loop)

                    else:   # Resource is not configured to observable
                        yield from get_impl(url)
                        print("Warning: resource is not observable")

                else:
                    yield from get_impl(url)

            elif code == 'PUT':
                yield from put_impl(url, payload)

            else:
                raise ValueError("invalid request code")
        except Exception as e:
            raise RuntimeError("Failed to complete CoAP request: {}".format(e))


def main():
    global server_IP
    global resources
    global data_file
    global run_demo
    global client_event_loop

    try:
        # FIXME: resource info is better acquired from server, provided server's IP
        with open('config.json') as config_file:
            data = json.load(config_file)
            server_IP = data['server']['IP']
            data_file = data['client']['datafile']
            demo_config = data['client']['demo']
            # re-format each sensor entry for client to use
            for r in data['sensors']:
                resources[r['name']] = {i: r[i] for i in r if i != 'name'}

            # add default activeness as "false" - i.e. not observable
            for r in resources:
                if 'active' not in resources[r]:
                    resources[r]['active'] = False
    except Exception as e:
        print("Failed to parse config file: {}".format(e))
        print("Exiting client!!!")
        return

    #print("{}".format(resources))

    if run_demo is True and demo_config is True:
        # Setup octave for data visualization and storage
        print("Initializing Octave database and visualizer...")
        octave.addpath('./')
        try:
            octave.demo_init(data_file)
            # Wait for Octave initialization to complete
            time.sleep(0.5)
        except Exception as e:
            print("Failed to initialize demo script: {}".format(e))
            print("Disabling Octave script...")
            run_demo = False
    else:
        # Turn off demo if oct2py module not present or config to not demo
        print("Disabling Octave script...")
        run_demo = False

    loop = asyncio.get_event_loop()
    # Keep a global record of the event loop for client
    client_event_loop = loop
    loop.run_until_complete(client_console())

if __name__ == '__main__':
    main()