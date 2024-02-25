# coding: utf-8
from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.mysql import BIGINT, BIT, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

Base = declarative_base()
metadata = Base.metadata
  
class XgMsdsUnstocking(Base):
    __tablename__ = 'xg_msds_unstocking'
    __table_args__ = {'comment': 'msds 出库'}

    id = Column(BIGINT(20), primary_key=True, comment='ID')
    msds_id = Column(BIGINT(20), nullable=False, comment='msds ID')
    user_id = Column(BIGINT(20), nullable=False, comment='出库操作人员ID')
    user_name = Column(String(64, 'utf8mb4_unicode_ci'), nullable=False, comment='出库操作人员')
    tenant_id = Column(BIGINT(20), nullable=False, comment='租户ID')
    creator = Column(String(64, 'utf8mb4_unicode_ci'), server_default=text("''"), comment='创建者')
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='出库时间')
    updater = Column(String(64, 'utf8mb4_unicode_ci'), server_default=text("''"), comment='更新者')
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    deleted = Column(BIT(1), nullable=False)

# 基础类
Base = declarative_base()

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Enum,
    DECIMAL,
    DateTime,
    Boolean,
    UniqueConstraint,
    Index
)
from sqlalchemy.ext.declarative import declarative_base

# db = pymysql.connect(host='114.132.155.77', user='root', passwd='root', port=31189, db='ruoyi-kl')
# 创建引擎
engine = create_engine(
    # "mysql+pymysql://root:root@114.132.155.77:31189/ruoyi-kl?charset=utf8mb4",
    "mysql+pymysql://tom@127.0.0.1:3306/db1?charset=utf8mb4", # 无密码时
    # 超过链接池大小外最多创建的链接
    max_overflow=0,
    # 链接池大小
    pool_size=5,
    # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
    pool_timeout=10,
    # 多久之后对链接池中的链接进行一次回收
    pool_recycle=1,
    # 查看原生语句（未格式化）
    echo=True
)

# 绑定引擎
Session = sessionmaker(bind=engine)
# 创建数据库链接池，直接使用session即可为当前线程拿出一个链接对象conn
# 内部会采用threading.local进行隔离
session = scoped_session(Session)
