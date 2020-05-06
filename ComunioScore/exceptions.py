

class DBConnectorError(ConnectionError):
    """DBConnectorException"""
    pass


class DBCreatorError(Exception):
    """DBCreatorException"""
    pass


class DBInserterError(Exception):
    """DBInserterException"""
    pass


class DBIntegrityError(Exception):
    """DBIntegrityError"""
    pass


class SofascoreRequestError(Exception):
    """SofascoreRequestError"""
    pass


class InvalidAccessToken(Exception):
    """InvalidAccessToken"""
    pass
