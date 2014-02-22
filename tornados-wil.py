from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from minigrade import minigrade

http_server = HTTPServer(WSGIContainer(minigrade))
http_server.listen(9080)
IOLoop.instance().start()