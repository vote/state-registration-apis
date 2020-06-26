class OVRLibException(Exception):
    pass


class InvalidAccessKeyError(OVRLibException):
    pass


class ReadOnlyAccessKeyError(OVRLibException):
    pass


class InvalidRegistrationError(OVRLibException):
    pass


class InvalidDLError(OVRLibException):
    pass


class InvalidSignatureError(OVRLibException):
    pass
