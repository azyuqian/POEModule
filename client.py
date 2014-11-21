#!/bin/python
import getopt
import sys
import json
from coapthon2.client.coap_protocol import HelperClient


client = HelperClient(server=("localhost", 5683))


def client_callback(response):
    print "Client Callback"
    print response

    deserialized_rsp = json.loads(response.payload)
    print deserialized_rsp['time']
    print type(deserialized_rsp['time'])


def main():
    op = 'GET'
    path = '/time' # or '/acceleration' or '/hello'
    payload = None

    if op == "GET":
        if path is None:
            print "Path cannot be empty for a GET request"
            usage()
            sys.exit(2)
        function = client.protocol.get
        args = (path,)
        kwargs = {}
        callback = client_callback

    operations = [(function, args, kwargs, callback)]
    client.start(operations)


if __name__ == '__main__':
    main()
