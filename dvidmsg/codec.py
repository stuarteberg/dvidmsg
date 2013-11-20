class Codec(object):
    
    def encode_from_ndarray(self, a, stream):
        pass
    def decode_to_ndarray(self, stream):
        pass

    def encode_from_description(self, description, stream):
        pass
    def decode_to_description(self, stream):
        pass


known_codecs = {}
