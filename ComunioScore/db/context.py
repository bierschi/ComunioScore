

class CursorContextManager:
    """ class CursorContextManager

    USAGE:
            CursorContextManager(pool=pool, autocommit=False)

    """
    def __init__(self, pool, autocommit=False):

        self.pool = pool
        self.autocommit = autocommit
        self.conn = None

    def __enter__(self):
        """ implicit enter context for a cursor object generated from ThreadedConnectionPool

        :return: cursor object
        """

        self.conn = self.pool.getconn()
        self.conn.autocommit = self.autocommit
        self.cursor = self.conn.cursor()

        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ implicit exit context to cleanly execute commit/rollback on current connection object

        :param exc_type: exception type
        :param exc_val: exception value
        :param exc_tb: exception traceback
        """

        if (exc_type and exc_val and exc_tb) is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        # set False as default
        self.conn.autocommit = False
        self.cursor.close()
        self.pool.putconn(self.conn)


class ConnectionContextManager:
    """ class ConnectionContextManager

    USAGE:
            ConnectionContextManager(pool=pool, autocommit=False)

    """
    def __init__(self, pool, autocommit=False):

        self.pool = pool
        self.autocommit = autocommit

    def __enter__(self):
        """ implicit enter context for a connection object generated from ThreadedConnectionPool

        :return:
        """

        self.conn = self.pool.getconn()
        self.conn.autocommit = self.autocommit

        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ implicit exit context to cleanly execute rollback on current connection object

        :param exc_type: exception type
        :param exc_val: exception value
        :param exc_tb: exception traceback
        """

        self.conn.rollback()
        self.conn.autocommit = False
        self.pool.putconn(self.conn)
