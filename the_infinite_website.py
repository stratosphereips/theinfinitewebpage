#!/usr/bin/env python
import datetime
import curses
import logging
import argparse

# twisted.internet  drives the whole process, accepting TCP connections and moving bytes
from twisted.internet import reactor
from twisted.internet import defer
from twisted.web import http
from twisted.internet import protocol
from twisted.web.server import NOT_DONE_YET

# Initialise logging
logging.basicConfig(filename='theinfinitewebsite.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')


# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    '--port',
                    help='Port where the webserver should listen.',
                    action='store',
                    required=False,
                    type=int,
                    default=8800)
args = parser.parse_args()

if args.port:
    port = args.port



# Global Class. Oh my.
class Cli():
    def __init__(self):
        self.connection_time = -1
        self.disconnection_time = -1
        self.amount_transfered = 0
        self.y_pos = -1


# Global variables. YES GLOBAL
Y_POS = 1
clients = {}

# Initialize the curses
stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
new_screen = stdscr
curses.init_pair(1, curses.COLOR_GREEN, -1)
curses.init_pair(2, curses.COLOR_RED, -1)
curses.init_pair(3, curses.COLOR_CYAN, -1)
curses.init_pair(4, curses.COLOR_WHITE, -1)
stdscr.bkgd(' ')
curses.noecho()
curses.cbreak()
new_screen.keypad(1)
curses.curs_set(0)
new_screen.addstr(0,0, 'The Infinite Web Page. Live Log of captured clients.')
new_screen.refresh()
screen = new_screen


#####################
def wait(seconds, result=None):
    """Returns a deferred that will be fired later"""
    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, result)
    return d

class StreamHandler(http.Request):
    global Y_POS
    global clients

    @defer.inlineCallbacks
    def process(self):
        global Y_POS
        global clients
        newcli = Cli()
        newcli.connection_time = datetime.datetime.now()
        clients[self.client] = newcli
        clients[self.client].y_pos = Y_POS
        logging.info(f'New Client connected from {self.client.host}:{self.client.port}')
        Y_POS += 1
        try:
            useragent = http.Request.getAllHeaders(self)['user-agent']
            short_useragent = useragent[0:50]
        except:
            useragent = "Empty"
            short_useragent = "Empty"
        logging.info(f'Client {self.client.host}:{self.client.port}. User-Agent: {useragent}')
        logging.info(f'Client {self.client.host}:{self.client.port}. Method: {str(self.method)}')
        logging.info(f'Client {self.client.host}:{self.client.port}. Path: {str(self.uri)}')

        # Print
        screen.addstr(clients[self.client].y_pos,0, "Client "+str(self.client.host)+':'+str(self.client.port)+'.  '+str(clients[self.client].connection_time)+' '+str(self.method)+' '+str(self.uri)+' UA: '+short_useragent)

        #screen.addstr(13,0,str(self.uri))
        screen.refresh()


        # For GET and POST it works fine
        if 'GET' in self.method or 'POST' in self.method or 'CONNECT' in self.method or 'PUT' in self.method:
            while not http.Request.finished:
                self.setHeader('Connection', 'Keep-Alive')
                s = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\"><html><head><title>This is a TL;DR page.</title></head><body>"
                s += str("What you are looking for is in the next line<br>"*100)
                newcli.amount_transfered += len(s)
                # For some reason the connection is not stopped and continues to try to send data
                screen.addstr(clients[self.client].y_pos,140, " Data {:>5.3f} MB".format(clients[self.client].amount_transfered/1024/1024.0)+" Duration "+str(datetime.datetime.now() - clients[self.client].connection_tim), curses.color_pair(2))
                screen.refresh()
                try:
                    self.write(s)
                    yield wait(0)
                except:
                    return
        # For HEAD we should do something different because they don't wait for any data.
        elif 'HEAD' in self.method or 'OPTIONS' in self.method:
            self.setHeader('Connection', 'Keep-Alive')


    def connection_lost(self,reason):
        global clients
        disconnect_time = datetime.datetime.now()
        try:
            logging.info('Client {}:{}. Finished connection. Total Transfer: {:.3f} MB, Duration: {}'.format(self.client.host, self.client.port, clients[self.client].amount_transfered/1024/1024.0, str(disconnect_time - clients[self.client].connection_time)))
        except AttributeError:
            logging.error('The client variable was not available. No more info.')
            return
        http.Request.notifyFinish(self)
        http.Request.finish(self)


class StreamProtocol(http.HTTPChannel):
    requestFactory = StreamHandler

class StreamFactory(http.HTTPFactory):
    protocol = StreamProtocol

# Port is given by command parameter or defaults to 8800
reactor.listenTCP(port, StreamFactory())
logging.info(f'Listening on port {port}')
reactor.run()
