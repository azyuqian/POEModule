#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

import logging


import asyncio


import aiocoap
from aiocoap.resource import Site


import resources as r


# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


def main():
    """ Create resource tree """
    root = Site()

    root.add_resource(('.well-known', 'core'), r.CoreResource(root))
    root.add_resource(('hello',), r.HelloWorld())
    root.add_resource(('time',), r.LocalTime())
    root.add_resource(('acceleration',), r.Acceleration())
    root.add_resource(('hygrothermo',), r.HygroThermo())
    root.add_resource(('temperature',), r.Temperature())
    root.add_resource(('humidity',), r.Humidity())

    #root.add_resource(('other', 'block'), BlockResource())
    #root.add_resource(('other', 'separate'), SeparateLargeResource())

    asyncio.async(aiocoap.Context.create_server_context(root))

    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
