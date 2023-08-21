#!/usr/bin/env python
import argparse
import curses
import datetime
import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler

# twisted.internet  drives the whole process, accepting TCP connections and moving bytes
from twisted.internet import reactor
from twisted.internet import defer
from twisted.web import http
from twisted.internet import protocol
from twisted.web.server import NOT_DONE_YET

# Our own imports
from lib.custom_logging import log_message_http
from lib.custom_http import generate_html


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
    """
    Returns a deferred that will be fired after a specified number of seconds.

    This function schedules a callback to be called after a delay, using the Twisted reactor.
    It returns a deferred object that will be fired with the given result after the specified
    number of seconds.

    Args:
        seconds (float): The number of seconds to wait before firing the deferred.
        result (Optional[Any]): The result value to pass to the deferred's callback. Defaults to None.

    Returns:
        defer.Deferred: The deferred object that will be fired after the specified delay.

    Example:
        deferred_object = wait(5, "Done")
        deferred_object.addCallback(print)  # Will print "Done" after 5 seconds.
    """
    deferred_object = defer.Deferred()
    reactor.callLater(seconds, deferred_object.callback, result)
    return deferred_object


class StreamHandler(http.Request):
    """
    A custom handler for processing HTTP requests related to streaming.

    This class extends Twisted's http.Request and provides custom methods for handling
    connections, processing streams, and managing client interactions.

    Attributes:
        Y_POS: A global variable for managing the Y position in the screen.
        clients: A global variable containing a collection of connected clients.

    Methods:
        process(): An asynchronous method that processes the incoming stream.
        connection_lost(reason): Called when a connection with a client is lost.
    """
    global Y_POS
    global clients

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_alive = True

    def connectionLost(self, reason):
        self.connection_alive = False
        super().connectionLost(reason)

    @defer.inlineCallbacks
    def process(self):
        global Y_POS
        global clients
        newcli = Cli()
        newcli.connection_time = datetime.datetime.now()
        clients[self.client] = newcli
        clients[self.client].y_pos = Y_POS
        Y_POS += 1
        DATA_DISPLAY_POSITION = 140
        ALLOWED_METHODS = ['GET', 'POST', 'CONNECT', 'PUT', 'REPORT', 'PROPFIND', 'TRACE',
                           'COPY', 'ACL', 'PROPPATCH', 'MKCOL', 'VERSION-CONTROL', 'MOVE',
                           'UNLOCK', 'PATCH', 'MERGE', 'LINK', 'PATCH', 'UNLINK',
                           ]

        try:
            useragent = self.requestHeaders.getRawHeaders('User-Agent', [None])[0]
            short_useragent = useragent[0:50]
        except:
            useragent = "Empty"
            short_useragent = "Empty"

        log_message_http(
            logger,
            str(clients[self.client].connection_time),
            self.client,
            self.method,
            self.uri,
            useragent
        )

        # Create log message to print on the screen
        # Format:
        #   Connection Time Client Addr:Client Port Method URI User-Agent
        #   2023-08-12 20:24:30.834751 CLIENT 127.0.0.1:59728 GET / (Empty)
        log_msg=f"{str(clients[self.client].connection_time)} "
        log_msg=log_msg+f"CLIENT {str(self.client.host)}:{str(self.client.port)} "
        log_msg=log_msg+f"{self.method.decode()} "
        log_msg=log_msg+f"{self.uri.decode()} "
        log_msg=log_msg+f"({short_useragent})"

        screen.addstr(clients[self.client].y_pos, 0, log_msg)

        #screen.addstr(13,0,str(self.uri))
        screen.refresh()


        # For GET and POST it works fine
        if any(method in self.method.decode() for method in ALLOWED_METHODS):
            while self.connection_alive:
                self.setHeader('Connection', 'Keep-Alive')
                self.setHeader('Content-Type', 'text/html')
                html_content = generate_html()
                newcli.amount_transfered += len(html_content)

                # Prepare to display data
                data_display = f"Data {newcli.amount_transfered/1024/1024.0:>5.3f} MB, Duration {datetime.datetime.now() - newcli.connection_time}"
                screen.addstr(clients[self.client].y_pos, DATA_DISPLAY_POSITION, data_display, curses.color_pair(2))
                screen.refresh()

                try:
                    self.write(html_content.encode('utf-8'))
                    yield wait(0.1)
                except:
                    return
                time.sleep(0.1)
        # For HEAD we should do something different because they don't wait for any data.
        elif any(method in self.method.decode() for method in ['HEAD', 'OPTIONS']):
            while self.connection_alive:
                self.setHeader('Connection', 'Keep-Alive')
                self.setHeader('Content-Type', 'text/html')

                # Prepare to display data
                data_display = f"Data {newcli.amount_transfered/1024/1024.0:>5.3f} MB, Duration {datetime.datetime.now() - newcli.connection_time}"
                screen.addstr(clients[self.client].y_pos, DATA_DISPLAY_POSITION, data_display, curses.color_pair(2))
                screen.refresh()
                try:
                    yield wait(0.1)
                except:
                    return
                time.sleep(0.1)



class StreamProtocol(http.HTTPChannel):
    requestFactory = StreamHandler

class StreamFactory(http.HTTPFactory):
    protocol = StreamProtocol

class JsonFormatter(logging.Formatter):
    """
    A custom formatter for logging that formats log records as JSON objects.

    The resulting JSON object includes the following fields:
        - "timestamp": The timestamp of the log record, formatted according to the datefmt attribute.
        - "level": The log level of the record (e.g., "INFO", "WARNING").
        - "message": The log message.
    """
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage()
        }
        return json.dumps(log_object)

def main():
    """
    The main function to start The Infinite Website Honeypot.

    This function starts the server and listens for incoming connections.
    Log files are rotated every midnight, and old logs are kept indefinitely.

    The port can be specified with the -p or --port command-line option. If not specified,
    the default port is 8800.

    Usage:
        python the_infinite_website.py [--port PORT]

    Raises:
        Exception: Any unhandled exceptions that occur during execution.

    Example:
        python the_infinite_website.py --port 8000
    """
    try:
        # Port is given by command parameter or defaults to 8800
        reactor.listenTCP(port, StreamFactory())
        log_data = {
            'MessageType': 'Server',
            'Timestamp': str(datetime.datetime.now()),
            'Status': 'online',
            'Sport': port,
        }
        logger.info(json.dumps(log_data))
        reactor.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as err:
        print(f"Exception in main(): {err}")


if __name__ == '__main__':
    try:
        # Create a log filename
        log_filename = f'log/{datetime.datetime.now().strftime("%Y-%m-%d")}_tiw.log'

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

        # Logging: create a handler that writes log messages to a file, with a new log file
        # created every midnight, and keeps 30 old log files.
        handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=0)

        json_formatter = JsonFormatter()
        handler.setFormatter(json_formatter)

        # Create a logger and configure it with the handler, setting the log level and format
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Run the honeypot
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as err:
        logger.info(f'Exception in __main__: {err}')

