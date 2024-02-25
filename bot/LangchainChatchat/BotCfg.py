from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Table

DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/crudboy?charset=utf8mb4"
engine = create_engine(DATABASE_URI)
Base = declarative_base()
metadata = Base.metadata
metadata.bind = engine

class BotCfg(Base):
    __table__ = Table("employees", metadata, autoload=True)