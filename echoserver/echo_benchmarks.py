import numpy
import echoserver

import dvidmsg.codec
from dvidmsg.timer import Timer
import dvidmsg.dthriftpy.thrift_conversions as thrift_conversions

class BenchmarkStats(object):
    def __init__(self):
        self.codec_name = None
        self.type_name = None
        self.image_size_mb = None
        self.message_size_mb = None
        self.encode_seconds = None
        self.send_seconds = None
        self.rcv_seconds = None
        self.decode_seconds = None
        self.roundtrip_seconds = None

def print_stats_header():
    header = "codec,"\
             "image size,"\
             "dtype,"\
             "encoded message size,"\
             "encode seconds,"\
             "send seconds,"\
             "rcv seconds,"\
             "decode seconds,"\
             "roundtrip seconds"
    print header

def print_stats( stats ):
    stats_row = ( "{codec_name},"
                  "{image_size_mb},"
                  "{type_name},"
                  "{message_size_mb},"
                  "{encode_seconds},"
                  "{send_seconds},"
                  "{rcv_seconds},"
                  "{decode_seconds},"
                  "{roundtrip_seconds}"
                  "".format( **stats.__dict__ ) )
    print stats_row

def run_benchmark( dtype, shape, codec_name ):
    codec = dvidmsg.codec.known_codecs[codec_name]
    a = numpy.random.random( shape ).astype( dtype )
    with Timer() as timer:
        echoed_a, msg_length, encode_seconds, send_seconds, rcv_seconds, decode_seconds = echoserver.get_echo( a, "localhost:8000", codec )
    
    assert ( a == echoed_a ).all(),\
        "Echoed data was incorrect for shape {}, dtype {}, codec {}".format( shape, dtype, codec )

    stats = BenchmarkStats()
    stats.codec_name = codec_name
    stats.type_name = thrift_conversions.conversion_specs_from_numpy[ dtype ].dvid_type
    stats.image_size_mb = numpy.prod( shape ) / 1e6
    stats.message_size_mb = msg_length / 1e6
    stats.encode_seconds = encode_seconds
    stats.send_seconds = send_seconds
    stats.rcv_seconds = rcv_seconds
    stats.decode_seconds = decode_seconds
    stats.roundtrip_seconds = timer.seconds()
    return stats

def run_benchmarks():
    shapes = [ (100,100),
               (100,1000),
               (1000,1000),
               (10,1000,1000) ]
               #(100,1000,1000),
               #(1000,1000,1000) ]
    
    print_stats_header()
    
    dtypes = [ numpy.uint8, numpy.int8,
               numpy.uint16, numpy.int16,
               numpy.uint32, numpy.int32,
               numpy.float32, 
               numpy.uint64, numpy.int64,
               numpy.float64 ]
    
    for codec in [ 'thrift', 'protobuf' ]:
        for shape in shapes:
            for dtype in dtypes:
                print_stats( run_benchmark( dtype, shape, codec ) )

if __name__ == "__main__":
    server_proc = echoserver.start_server()
    try:
        run_benchmarks()
    finally:
        server_proc.terminate()
