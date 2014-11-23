import threading
from coapthon2.client.coap_protocol import CoAP
from twisted.internet import reactor, stdio
import twisted
from twisted.protocols import basic
import traceback


# Demo the stdio input user command and get a CoAP resource
# To run this(make sure you have a CoAP resource of /time at 127.0.0.1):
# > python client_stdio.py
# >> get time


class WebCheckerCommandProtocol(basic.LineReceiver):
    delimiter = '\n' # unix terminal style newlines. remove this line
                     # for use with Telnet
    prompt_string = '>>>'

    def prompt(self):
        self.transport.write(self.prompt_string)

    def connectionMade(self):
        self.sendLine("PoE PL94 Console. Type 'help' for help.")
        self.prompt()

    def lineReceived(self, line):
        # Ignore blank lines
        if not line:
            self.prompt()
            return

        # Parse the command
        commandParts = line.split()
        command = commandParts[0].lower()
        args = commandParts[1:]

        # Dispatch the command to the appropriate method.  Note that all you
        # need to do to implement a new command is add another do_* method.
        try:
            method = getattr(self, 'do_' + command)
        except AttributeError, e:
            self.sendLine('Error: no such command.')
        else:
            try:
                method(*args)
            except Exception, e:
                self.sendLine('Error: ' + str(e))

    def do_help(self, command=None):
        """help [command]: List commands, or show help on the given command"""
        if command:
            self.sendLine(getattr(self, 'do_' + command).__doc__)
        else:
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            self.sendLine("Valid commands: " +", ".join(commands))
        self.prompt()

    def do_quit(self):
        """quit: Quit this session"""
        self.sendLine('Goodbye.')
        self.transport.loseConnection()

    def callback(self, response):
        print response.payload

    def do_get(self, url):
        """get <url>: Get a resource"""
        try:
            protocol.get(self.callback, '/' + url)
        except:
            print traceback.format_exc()

    def __checkSuccess(self, pageData):
        self.sendLine("Success: got %i bytes." % len(pageData))

    def __checkFailure(self, failure):
        self.sendLine("Failure: " + failure.getErrorMessage())

    def connectionLost(self, reason):
        # stop the reactor, only because this is meant to be run in Stdio.
        reactor.stop()


protocol = CoAP(("192.168.2.20", 5683))
reactor.listenUDP(0, protocol)

# For multicast(not tested)
#protocol = CoAP(("192.0.0.1", 5683))
#reactor.listenMulticast(0, protocol)

stdio.StandardIO(WebCheckerCommandProtocol())
reactor.run()



