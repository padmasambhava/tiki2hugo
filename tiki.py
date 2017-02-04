
import sqlalchemy
from sqlalchemy.orm import sessionmaker

Conf = None
Engine = None
Db = None

class Menu:
    def __init__(self, url=None, type_=None, name=None):
        self.url = url
        self.type_ = type_
        self.name = name

class Tiki:
    
    def __init__(self):
        
        self.conf = None
        self.engine = None
        self.db = None
    
        
        
    def init(self, conf):
        #global Engine, Db, Conf
        self.conf = conf
        db_conn_str = self.conf.get('tiki_db')
        print "> DB.init()", db_conn_str
        if db_conn_str == None:
            return "Conf config"
        self.engine = sqlalchemy.create_engine(db_conn_str)
        #self.engine.connect()
        sess = sessionmaker(bind=self.engine)
        self.session = sess()
    
        
    def test_db(self):
        self.select.execute("select 1")
        return npper
        

    def menu(self, mid):
        lst = []
        sql = "select optionId, menuid, type, name, url from tiki_menu_options where menuId=%s" % mid
        sql += " order by position asc"
        res = self.session.execute(sql)
        for  r in res:
            d = dict(optionid=r[0], menid=r[1], type=r[2], name=r[3], url=r[4])
            lst.append(d)
            
        return lst