#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

import logging
import json

import asyncio

import aiocoap
from aiocoap.resource import Site

import resources as r

# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger('coap-server').setLevel(logging.DEBUG)


def main():
    """ Create resource tree """
    root = Site()

    # default resources to add
    root.add_resource('', r.RootResource(root))
    root.add_resource(('.well-known', 'core'), r.CoreResource(root))
    root.add_resource(('hello',), r.HelloWorld())
    root.add_resource(('time',), r.LocalTime())
    root.add_resource(('alert',), r.Alert())
    #root.add_resource(('other', 'block'), BlockResource())
    #root.add_resource(('other', 'separate'), SeparateLargeResource())

    with open('config.json') as data_file:
        sensor_list = json.load(data_file)['sensors']
    
    for sensor in sensor_list:
        # Known sensors that has been pre-defined
        if sensor['name'] == 'accelerometer':
            root.add_resource(tuple(sensor['url'].split('/')), r.Acceleration())
        elif sensor['name'] == 'temperature':
            root.add_resource(tuple(sensor['url'].split('/')), r.Temperature())
        elif sensor['name'] == 'humidity':
            root.add_resource(tuple(sensor['url'].split('/')), r.Humidity())
        # For unknown sensors, use template resource
        else:
            root.add_resource(tuple(sensor['url'].split('/')),
                              r.ResourceTemplate(sensor['name'],
                                                 sensor['active'],
                                                 sensor['period'],
                                                 sensor['min'],
                                                 sensor['max'],
                                                 sensor['channel']))

        print("\n{} resource added to path {}".format(sensor['name'], sensor['url']))
        for entry in sensor:
            if entry != 'name' and entry != 'url':
                print("{}:{}".format(entry, sensor[entry]))

    asyncio.async(aiocoap.Context.create_server_context(root))

    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
