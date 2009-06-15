import sqlalchemy as sql

from cogent.db.ensembl.host import DbConnection, get_db_name

__author__ = "Gavin Huttley"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Gavin Huttley"]
__license__ = "GPL"
__version__ = "1.4.0.dev"
__maintainer__ = "Gavin Huttley"
__email__ = "Gavin.Huttley@anu.edu.au"
__status__ = "alpha"

class Database(object):
    """holds the data-base connection and table attributes"""
    def __init__(self, account, species=None, db_type=None, release=None):
        self._tables = {}
        self.db_name = get_db_name(account=account, species=species,
                            release=release, db_type=db_type)
        if not self.db_name:
            raise RuntimeError, "%s db doesn't exist for '%s' on '%s'" % (db_type, species, account.host)
        else:
            self.db_name = self.db_name[0]
        self._db = DbConnection(account=account, db_name=self.db_name)
        self._meta = sql.MetaData(self._db)
        self.Type = db_type
        
    def __str__(self):
        return str(self.db_name)
    
    def __cmp__(self, other):
        return cmp(self._db, other._db)
    
    def getTable(self, name):
        """returns the SQLalchemy table instance"""
        table = self._tables.get(name, None)
        if table is None:
            c = self._db.execute("DESCRIBE %s" % name)
            custom_columns = []
            for r in c.fetchall():
                Field = r["Field"]
                Type = r["Type"]
                if "tinyint" in Type:
                    custom_columns.append(sql.Column(Field, sql.Integer))
            
            table = sql.Table(name,self._meta,autoload=True,*custom_columns)
            self._tables[name] = table
        return table
    
    def getDistinct(self, table_name, column):
        """returns the Ensembl data-bases distinct values for the named
        property_type.
        
        Arguments:
            - table_name: the data base table name
            - column: valid values are biotype, status"""
        table = self.getTable(table_name)
        query = sql.select([table.c[column]], distinct=True)
        for record in query.execute():
            if type(record) != str:
                new = ()
                for value in record:
                    if type(value) == set:
                        value = tuple(value)
                    new += (value,)
                record = new
                while len(record) == 1 and type(record) in (tuple, list):
                    record = record[0]
            yield record
    

