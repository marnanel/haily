import SimpleHTTPServer
import SocketServer

def run(host="", port=8000):
        
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        httpd = SocketServer.TCPServer((host, port), handler)

        httpd.serve_forever()
