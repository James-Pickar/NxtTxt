""" Exceptions raised in nxttxt """


# Errors surrounding file section
class InvalidPath(Exception):
    pass


class PathIsNotADirectory(Exception):
    pass


class PathIsADirectory(Exception):
    pass


class InvalidFileType(Exception):
    pass


# Errors surrounding server connection
class ConnectionRejected(Exception):
    pass


class ConnectionTimeout(Exception):
    pass


class TooManyRedirects(Exception):
    pass


class UnknownConnectionError(Exception):
    pass


# Errors surrounding PDF extraction
class NoPDFsLocated(Exception):
    pass


class ExtractionTimeOut(Exception):
    pass
