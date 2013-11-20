import contextlib
import cStringIO as StringIO
import numpy
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import HTTPConnection

import dvidmsg.codec
import dvidmsg.thrift_codec
import dvidmsg.protobuf_codec

from dvidmsg.timer import Timer

class EchoRequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        if not "echo" in self.path:
            self.send_response(404, "Only supports echo")
            self.end_headers()
            return
        content_length = int(self.headers['Content-Length'])
        rcvdata = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-Length", content_length)
        self.end_headers()
        
        # Send the raw data right back.
        self.wfile.write( rcvdata )

    def do_GET(self):
        self.send_response(404, "GET not supported.  Only supports echo via PUT")
        self.end_headers()
        return
    
    def log_request(self, *args):
        # Override default log behavior
        # We don't want our benchmark output cluttered with messages to stderr
        pass

def get_echo(a, hostname, codec):
    stream = StringIO.StringIO()
    
    with Timer() as encode_timer:
        codec.encode_from_ndarray(a, stream)
    
    with contextlib.closing( HTTPConnection(hostname) ) as conn:
        body = stream.getvalue()
        with Timer() as send_timer:
            conn.request( "PUT", "/echo", body=body )
        response = conn.getresponse()
        with Timer() as read_timer:
            strio = StringIO.StringIO( response.read() )
        with Timer() as decode_timer:
            echoed_a = codec.decode_to_ndarray(strio)
        return echoed_a, len(body), encode_timer.seconds(), send_timer.seconds(), read_timer.seconds(), decode_timer.seconds()

def start_server():
    def server_main():
        server_address = ('', 8000)
        server = HTTPServer( server_address, EchoRequestHandler )
        server.serve_forever()

    import multiprocessing
    server_proc = multiprocessing.Process( target=server_main )
    server_proc.start()    
    return server_proc

if __name__ == "__main__":
    server_proc = start_server()    

    codec = dvidmsg.codec.known_codecs['protobuf']    
    a = numpy.random.random( (10,10) ).astype( numpy.float32 )
    echoed_a, msg_length, encode_time, decode_time = get_echo( a, "localhost:8000", codec )

    server_proc.terminate()
    
    print "msg length was", msg_length
    print "timing was {}, {}".format( encode_time, decode_time )
    
    assert ( a == echoed_a ).all(), "Data didn't match."
    print "DONE!"
    
