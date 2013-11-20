from dvidmsg.dprotopy.dvidmsg_pb2 import Array
import dvidmsg.dprotopy.proto_conversions as proto_conversions

class ThriftCodec(object):
    def encode_from_ndarray(self, a, stream):
        send_msg = proto_conversions.convert_array_to_dvidmsg( a )
        stream.write( send_msg.SerializeToString() )

    def decode_to_ndarray(self, stream):
        rcv_msg = Array()
        rcv_msg.ParseFromString( stream.read() )
        return proto_conversions.convert_array_from_dvidmsg( rcv_msg )

    def encode_from_description(self, description, stream):
        pass

    def decode_to_description(self, stream):
        pass

import dvidmsg.codec
dvidmsg.codec.known_codecs['protobuf'] = ThriftCodec()
