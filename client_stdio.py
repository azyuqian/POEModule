import sys
import logging
import json
import asyncio
import socket

from aiocoap import *
from defs import *

logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def get_impl(resource=''):

    context = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://{}/{}'.format(server_IP, resource))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        print("Failed to fetch resource: {}".format(e))
    else:
        print("Result: {}\n{}".format(response.code, response.payload))

@asyncio.coroutine
def put_impl(resource='', payload=""):

    context = yield from Context.create_client_context()

    yield from asyncio.sleep(2)

    request = Message(code=PUT, payload=payload.encode(UTF8))
    request.set_request_uri('coap://{}/{}'.format(server_IP, resource))

    try:
        response = yield from context.request(request).response
    except Exception as e:
        print("Failed to update resource: {}".format(e))
    else:
        print("Result: {}\n{}".format(response.code, response.payload))


def incoming_observation(response):
    sys.stdout.buffer.write(b'\f')
    sys.stdout.buffer.write(response.payload)
    sys.stdout.buffer.flush()

@asyncio.coroutine
def observe_impl(resource=''):
    context = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://{}/{}'.format(server_IP, resource))

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
        sys.stdout.buffer.write(response_data.payload)
        sys.stdout.buffer.flush()
    else:
        print(response_data.code, file=sys.stderr)
        if response_data.payload:
            print(response_data.payload.decode(UTF8), file=sys.stderr)
        sys.exit(1)

    exit_reason = yield from observation_is_over
    print(exit_reason, file=sys.stderr)

@asyncio.coroutine
def process_input():
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
                        if cmd.startswith('do_')]
            print("Valid commands: " + ", ".join(commands))

    @staticmethod
    def do_hello(code='GET', *args):
        """ Implementation of hello command

        Based on code type, perform GET or PUT request on hello resource
        Example: >>>hello
        Example: >>>hello GET -o
        Example: >>>hello PUT new hello world!

        :param code: type of CoAP request
        :type code: str
        :param args: payload of PUT request
        :type args: str
        """
        loop = asyncio.get_event_loop()

        payload = " ".join(args)
        if code == 'GET':
            if payload.startswith('-o'):
                yield from observe_impl('hello')
            else:
                yield from get_impl('hello')
        elif code == 'PUT':
            yield from put_impl('hello', payload)


    @staticmethod
    def do_time(code='GET', *args):
        """ Implementation of hello command

        Based on code type, perform GET or PUT request on hello resource
        Example: >>>time
        Example: >>>time GET -o
        Example: >>>time PUT period 3

        :param code: type of CoAP request
        :type code: str
        :param args: payload of PUT request
        :type args: str
        """
        loop = asyncio.get_event_loop()

        payload = " ".join(args)
        if code == 'GET':
            if payload.startswith('-o'):
                yield from observe_impl('time')
            else:
                yield from get_impl('time')
        elif code == 'PUT':
            yield from put_impl('time', payload)


def main():
    global server_IP

    with open('config.json') as data_file:
        server = json.load(data_file)['server']

    server_IP = server['IP']

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_input())

if __name__ == '__main__':
    main()