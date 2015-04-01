import sys
import logging
import json
import asyncio
import socket

from aiocoap import *
from defs import *
from oct2py import octave

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
    if jpayload['name'] in demo_resources:
        time = []
        data = []

        # Parse payload data
        import re
        time_str = re.split('[- :]', jpayload['time'])
        try:
            for i in range(5):
                time += [int(time_str[i])]
            time += [float(time_str[5])]
        except ValueError as e:
            print("Wrong time format: {}".format(e))
            time = [0, 0, 0, 0, 0, 0.0]

        try:
            jvalue = json.loads(jpayload['data'])
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
                         float(jvalue['updown']), float(jvalue['leftright'])]
            else:
                print("Warning: Unknown data\n")
                data += [float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'), float('NaN')]
        except Exception as e:
            raise Exception("Failed to parse data: {}".format(e))
        data += time

        print("data to plot: {}".format(data))
        #octave.test_update(data_file, data)


def incoming_observation(response):
    jpayload = json.loads(response.payload.decode(UTF8))
    print("Result: {}\n{}".format(response.code, jpayload))
    plot_octave(jpayload)


@asyncio.coroutine
def post_impl(jargs):
    context = yield from Context.create_client_context()

    request = Message(code=POST, payload=jargs.encode(UTF8))
    request.set_request_uri('coap://{}/'.format(server_IP))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        raise Exception("Failed to post new resource: {}".format(e))
    else:
        print("Result: {}\n{}".format(response.code, response.payload.decode(UTF8)))

@asyncio.coroutine
def get_impl(name, url=''):
    context = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://{}/{}'.format(server_IP, url))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        raise Exception("Failed to fetch resource: {}".format(e))
    else:
        jpayload = json.loads(response.payload.decode(UTF8))
        print("Result: {}\n{}".format(response.code, jpayload))
        plot_octave(jpayload)

@asyncio.coroutine
def put_impl(url='', payload=""):
    context = yield from Context.create_client_context()

    yield from asyncio.sleep(2)

    request = Message(code=PUT, payload=payload.encode(UTF8))
    request.set_request_uri('coap://{}/{}'.format(server_IP, url))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        print("Failed to update resource: {}".format(e))
    else:
        print("Result: {}\n{}".format(response.code, response.payload.decode(UTF8)))

@asyncio.coroutine
def observe_impl(name, url=''):
    context = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://{}/{}'.format(server_IP, url))

    request.opt.observe = 0
    observation_is_over = asyncio.Future()

    requester = context.request(request)

    requester.observation.register_errback(observation_is_over.set_result)
    requester.observation.register_callback(lambda data: incoming_observation(data))

    try:
        response_data = yield from requester.response
    except socket.gaierror as e:
        print("Name resolution error:", e, file=sys.stderr)
        sys.exit(1)

    if response_data.code.is_successful():
        jpayload = json.loads(response_data.payload.decode(UTF8))
        print("Result: {}\n{}".format(response_data.code, jpayload))
        plot_octave(jpayload)
    else:
        print(response_data.code, file=sys.stderr)
        if response_data.payload:
            print(response_data.payload.decode(UTF8), file=sys.stderr)
            print("\n")
        sys.exit(1)

    exit_reason = yield from observation_is_over
    print(exit_reason, file=sys.stderr)

@asyncio.coroutine
def client_console():
    # First, print general info and help menu on console when client starts
    print("Connecting to server {}...\n".format(server_IP))
    print("Probing available resources...")
    for r in resources:
        # test GET each resource
        yield from Commands.do_resource(r, 'GET')
        print("Success! Resource {} is available at path /{}\n".format(r, resources[r]['url']))
    print("Done probing...")
    print("Initializing command prompt...\n")
    yield from Commands.do_help()

    # Start acquiring user input
    while True:
        cmdline = input(">>>")
        cmd_parts = cmdline.split()

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
                yield from method(*args)
            except Exception as e:
                print("Error: {}".format(e))


class Commands():
    @staticmethod
    def do_help(command=None):
        """ Implementation of help command

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

        # Empty yield to avoid NoneType error
        yield

    @staticmethod
    def do_add(name, *args):
        """ Implementation of add command for POST new resource
        Syntax: >>>add [name] -c [ADC_channel] (-u [url]) (-l [min] -m [max])
                        (-o) (-f [observe_frequency])
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
            raise p.error("ADC Channel not found")
        else:
            try:
                channel = int(options.channel)
            except ValueError as e:
                raise p.error(e)

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
            print("Warning: use resource name {} as url")

        if options.min and options.max:
            try:
                min = int(options.min)
                max = int(options.max)
                b_range = True
            except ValueError as e:
                raise p.error(e)

        if options.observe:
            active = True

            # only set frequency if resource is observable
            if options.frequency:
                try:
                    frequency = int(options.frequency)
                except ValueError as e:
                    raise p.error(e)

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
        yield from post_impl(json.dumps(payload))

    @staticmethod
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
        resource = resources[name]
        url = resource['url']

        #print("do_resource: payload={}".format(payload))
        if code == 'GET':
            if payload.startswith('-o'):
                if resource['active'] is True:
                    yield from observe_impl(name, url)
                else:
                    yield from get_impl(name, url)
                    print("Warning: resource is not observable")
            else:
                yield from get_impl(name, url)
        elif code == 'PUT':
            yield from put_impl(url, payload)
        else:
            raise AttributeError("Invalid command")


def main():
    global server_IP
    global resources
    global data_file

    # default resources
    resources = {'hello': {'url': 'hello'},
                 'time': {'url': 'time'}}

    # FIXME: resource info is better acquired from server, provided server's IP
    with open('config.json') as config_file:
        data = json.load(config_file)
        server_IP = data['server']['IP']
        data_file = data['client']['datafile']
        # re-format each sensor entry for client to use
        for r in data['sensors']:
            resources[r['name']] = {i: r[i] for i in r if i != 'name'}

        # add default activeness as "false" - i.e. not observable
        for r in resources:
            if 'active' not in resources[r]:
                resources[r]['active'] = False

    #print("{}".format(resources))

    # Setup octave for data visualization and storage
    print("Initializing Octave database and visualizer")
    octave.addpath('./')
    #octave.test_init(data_file)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(client_console())

if __name__ == '__main__':
    main()