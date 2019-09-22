from BreachCompilationRestAPI.db.connector import DBConnector
from BreachCompilationRestAPI.exceptions.db import DBCreatorError


class Database:
    """ class Database to build a sql string for Database creation

    USAGE:
            Database(name="web")

    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        """ string representation of database creation

        :return: sql string for database creation
        """
        return "create database {}".format(self.name)

    def __repr__(self):
        """ string representation of database object

        :return: sql string for database creation
        """
        return "create database {}".format(self.name)


class Table:
    """ class Table to build a sql string for Table creation

    USAGE:
            Table("page", Column('id', 'int', False, False), schema="web")
            Table("page")

    """
    def __init__(self, name, *columns, schema=None):

        self.name = name
        self.schema = schema
        self.sql_table = ""

        if schema is None:
            self.sql_table = "create table if not exists {} ".format(self.name)
        else:
            self.sql_table = "create table if not exists  {}.{} ".format(self.schema, self.name)

        if len(columns) == 1:
            self.sql_table = self.sql_table + str(columns).replace(',', '')
        elif len(columns) > 1:
            self.sql_table = self.sql_table + str(columns)

    def __call__(self, *columns):
        """ implicit method to invoke table instances to create new sql strings with variable *columns objects

        :param columns: objects of type Column()
        :return: sql table creation string
        """

        if len(columns) == 1:
            self.sql_table = self.sql_table + str(columns).replace(',', '')
            return self.sql_table
        elif len(columns) > 1:
            self.sql_table = self.sql_table + str(columns)
            return self.sql_table

    def __str__(self):
        """ string representation of table creation

        :return: sql string for table creation
        """
        return self.sql_table

    def __repr__(self):
        """ string representation of table object

        :return: sql string for table creation
        """
        return self.sql_table


class Column:
    """ class Column to build a sql string for Column creation

    USAGE:
            Column(name='id', type='int', not_null=False, prim_key=True)

    """
    def __init__(self, name, type, not_null=False, prim_key=False, exist_table=False, table_name=None, schema=None):

        self.name = name
        self.type = type
        self.not_null = not_null
        self.prim_key = prim_key
        self.exist_table = exist_table
        self.table_name = table_name
        self.schema = schema

        if self.schema is None:
            self.alter_table = "alter table {} ".format(self.table_name)
        else:
            self.alter_table = "alter table {}.{} ".format(self.schema, self.table_name)

        self.name_type_str     = "{} {} ".format(self.name, self.type)
        self.add_column_str    = "add column "
        self.primary_key_str   = "primary key "
        self.not_null_str      = "not null "
        self.if_not_exists     = "if not exists "

        self.sql_primary_key = self.name_type_str + self.primary_key_str
        self.sql_not_null    = self.name_type_str + self.not_null_str
        self.sql_exist_table = self.alter_table + self.add_column_str + self.if_not_exists + self.name_type_str
        self.sql_exist_table_prim_key = self.sql_exist_table + self.primary_key_str
        self.sql_exit_table_not_null  = self.sql_exist_table + self.not_null_str

    def __str__(self):
        """ string representation of column creation

        :return: sql string for column creation
        """
        if self.prim_key and not self.not_null and not self.exist_table:
            return self.sql_primary_key
        if self.not_null and not self.prim_key and not self.exist_table:
            return self.sql_not_null
        if self.exist_table and not self.prim_key and not self.not_null:
            return self.sql_exist_table
        if self.exist_table and self.prim_key:
            return self.sql_exist_table_prim_key
        if self.exist_table and self.not_null:
            return self.sql_exit_table_not_null
        else:
            return "{} {} ".format(self.name, self.type)

    def __repr__(self):
        """ string representation of column object

        :return: sql string for column creation
        """
        if self.prim_key and not self.not_null and not self.exist_table:
            return self.sql_primary_key
        if self.not_null and not self.prim_key and not self.exist_table:
            return self.sql_not_null
        if self.exist_table and not self.prim_key and not self.not_null:
            return self.sql_exist_table
        if self.exist_table and self.prim_key:
            return self.sql_exist_table_prim_key
        if self.exist_table and self.not_null:
            return self.sql_exit_table_not_null
        else:
            return "{} {} ".format(self.name, self.type)


class DBCreator(DBConnector):
    """ class DBCreator to build database, table or column

    USAGE:
            creator = DBCreator()
            creator.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
            creator.build(obj=Database(name="web"))
            creator.build(obj=Table("gps", Column('did', 'text'), Column('ts', 'text')))

    """
    def __init__(self):

        # init connector base class
        super().__init__()

    def build(self, obj):
        """

        :return:
        """
        if isinstance(obj, Database):
            self.__database(obj)
        elif isinstance(obj, Table):
            self.__table(obj)
        elif isinstance(obj, Column):
            self.__column(obj)
        else:
            raise DBCreatorError("Provide either a Database, Table or Column object")

    def __database(self, database_obj):
        """

        :param database_obj:
        """
        with self.get_cursor(autocommit=True) as cursor:
            cursor.execute(str(database_obj))

    def __table(self, table_obj):
        """

        """
        with self.get_cursor() as cursor:
            cursor.execute(str(table_obj))

    def __column(self, column_obj):
        """

        :return:
        """
        # only possible in existing table
        if column_obj.exist_table:
            with self.get_cursor() as cursor:
                cursor.execute(str(column_obj))
        else:
            raise DBCreatorError("Creation of column object is only possible in existing tables")


if __name__ == '__main__':

    creator = DBCreator()
    creator.connect(username="christian", password="", host="192.168.178.37", port="5432", dbname="")
    #creator.table(Table("abc", Column('did', 'text')))
    creator.build(obj=Column(name="abc", type="text", not_null=True, prim_key=False, exist_table=True, table_name="abc"))
    #gps_table = Table("test", "a", Column(name='did', type='int', not_null=True, prim_key=False))
