import  GlobalParameters
"""
    This class implements some usefull methods which
    are used in the whole DHCP server code
"""

''' This method takes data bytes and returns type
    of this message. Discovery or Request '''


def get_message_type(data):
    # calculate index of message type byte
    indx = GlobalParameters.MESSAGE_TYPE_BYTE_INDEX

    tp = data[indx]
    return tp

