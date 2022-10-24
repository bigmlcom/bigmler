# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,attribute-defined-outside-init
# Auxiliar class: Simple stoppable HTTPServer extracted from
#
# http://code.activestate.com/recipes/425210-simple-stoppable-server-using-socket-timeout/
#
# Unless required by applicable law or agreed to in writing, this software
# is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import http.server
import socket

class StoppableHTTPServer(http.server.HTTPServer):
    """Basic stoppable HTTP server to show reports"""

    def server_bind(self):
        """Binding the server """
        http.server.HTTPServer.server_bind(self)
        self.socket.settimeout(1)
        self.run = True

    def get_request(self):
        """Get method"""
        while self.run:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(None)
                return (sock, addr)
            except socket.timeout:
                pass

    def stop(self):
        """Stopper """
        self.run = False

    def serve(self):
        """Serving """
        while self.run:
            self.handle_request()
