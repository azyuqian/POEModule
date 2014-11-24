from twisted.internet import reactor
from coapthon2 import defines
from coapthon2.server.coap_protocol import CoAP
from resources import Acceleration, HelloWorld, LocalTime, Temperature, Humidity, Temp_Humidity

class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, multicast)
        self.add_resource('hello/', HelloWorld())
        self.add_resource('acceleration/', Acceleration())
        self.add_resource('time/', LocalTime())
        self.add_resource('temp_hum/', Temp_Humidity())
        self.add_resource('temperature', Temperature())
        self.add_resource('humidity', Humidity())

        print "CoAP Server start on " + host + ":" + str(port)
        print(self.root.dump())


def main():
    server = CoAPServer("192.168.2.20", 5683)
    #reactor.listenMulticast(5683, server, listenMultiple=True)
    reactor.listenUDP(5683, server, "192.168.2.20")
    reactor.run()


if __name__ == '__main__':
    main()
