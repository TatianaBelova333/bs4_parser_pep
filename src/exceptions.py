class HTTPStatusCodeError(Exception):
    """Raises Exception if the response status code is not 200."""


class ParserFindTagException(Exception):
    """Raises Exception when the parser cannot find the required tag."""
