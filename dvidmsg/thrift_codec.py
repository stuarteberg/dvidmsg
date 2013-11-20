import contextlib
import dvidmsg.dthriftpy.thrift_conversions as thrift_conversions
from dvidmsg.dthriftpy.genpy.dvidmsg.ttypes import Array

from thrift import Thrift
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

class ThriftCodec(object):
    def encode_from_ndarray(self, a, stream):
        send_transport = TTransport.TFileObjectTransport( stream )
        protocol = TBinaryProtocol.TBinaryProtocol(send_transport)    
        send_msg = thrift_conversions.convert_array_to_dvidmsg( a )
        send_msg.write(protocol)

    def decode_to_ndarray(self, stream):
        rcv_transport = TTransport.TFileObjectTransport(stream)
        protocol = TBinaryProtocol.TBinaryProtocol(rcv_transport)
        rcv_msg = Array()
        rcv_msg.read( protocol )    
        return thrift_conversions.convert_array_from_dvidmsg( rcv_msg )

    def encode_from_description(self, description, stream):
        pass

    def decode_to_description(self, stream):
        pass

import dvidmsg.codec
dvidmsg.codec.known_codecs['thrift'] = ThriftCodec()
