from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from minigraded import minigraded, PORT_NUMBER

http_server = HTTPServer(WSGIContainer(minigraded))
http_server.listen(PORT_NUMBER)
IOLoop.instance().start()
