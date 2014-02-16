from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from minigrade import minigrade, PORT_NUMBER
import logging

logging.basicConfig(filename='grader.log',level=logging.DEBUG)
logging.debug('Started logging on port: ' + str(PORT_NUMBER))

http_server = HTTPServer(WSGIContainer(minigrade))
http_server.listen(PORT_NUMBER)
IOLoop.instance().start()

logging.debug('Finished tornados!');
