import BaseHTTPServer
import SocketServer
import json

class HailyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        def _root_handler(self):
                result = {
                        "oauth_request_token_url": "/req",
                        "oauth_authorize_url": "/auth",
                        "oauth_access_token_url": "/acc",
                        "api-version": "1.0",
                }

                return result


        def do_GET(self):
                print self.path

                result = self._root_handler()

                payload = json.dumps(result,
                        indent=4,
                        sort_keys=True)

                self.send_response(200)
                self.wfile.write("Content-Type: text/json\n")
                self.wfile.write("Content-Length: %d\n" % (len(payload),))
                self.wfile.write("\n%s" % (payload,))

# first request is GET /api/1.0/

def run(host="", port=8001):
        
        handler = HailyRequestHandler

        httpd = SocketServer.TCPServer((host, port), handler)

        httpd.serve_forever()
