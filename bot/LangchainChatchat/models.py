# coding: utf-8
from sqlalchemy import Column, DECIMAL, DateTime, String, text
from sqlalchemy.dialects.mysql import BIGINT, BIT, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

Base = declarative_base()
metadata = Base.metadata


class AscBotBaseCfg(Base):
    __tablename__ = 'asc_bot_base_cfg'
    __table_args__ = {'comment': '机器人的基础配置'}

    id = Column(BIGINT(20), primary_key=True, comment='主键， 机器人id')
    afterwards_reply_cfg_id = Column(BIGINT(20), server_default=text("'0'"), comment='后续主动沟通的询问方案的id')
    file_match_cfg_id = Column(BIGINT(20), server_default=text("'0'"), comment='关键信息和文件链接匹配方案的id')
    code = Column(String(256, 'utf8mb4_unicode_ci'), nullable=False, comment='机器人代号')
    name = Column(String(256, 'utf8mb4_unicode_ci'), nullable=False, comment='机器人名称')
    avatar = Column(String(256, 'utf8mb4_unicode_ci'), comment='头像的url、或本地文件目录')
    role = Column(String(2560, 'utf8mb4_unicode_ci'), comment='角色设定，从 asc_bot_prompt 表选择')
    model = Column(String(256, 'utf8mb4_unicode_ci'), nullable=False, comment='毕业院校，即gpt模型')
    temperature = Column(DECIMAL(13, 4), comment='表达风格，即 回复是自由度')
    max_ctx_len = Column(INTEGER(11), comment='上下文记忆量，超过则舍弃')
    post = Column(String(256, 'utf8mb4_unicode_ci'), comment='岗位')
    speed = Column(INTEGER(11), comment='回复语速(秒)')
    reply_delay = Column(INTEGER(11), comment='人工智能雇员会在客户发送最末信息（单条或多条）后 多少 秒后，整体理解，再统一回复')
    rate_limit_duration = Column(INTEGER(11), comment='限流设置，总共时间跨度(秒)')
    rate_limit_questions = Column(INTEGER(11), comment='限流设置，多少个问题')
    rate_limit_prompt = Column(String(2560, 'utf8mb4_unicode_ci'), comment='沟通频率和数量超过限制时，应出现的提示语')
    user_info_collector = Column(String(256, 'utf8mb4_unicode_ci'), comment='客户信息收集提示信息')
    user_info_collector_type = Column(String(256, 'utf8mb4_unicode_ci'), comment='客户信息收集提示信息, 姓名|电话|微信, 多选一')
    init_reply = Column(String(2560, 'utf8mb4_unicode_ci'), comment='初始信息， 比如，用户开始聊天，第一句话是‘你好’之类的问候语， 那么就回复这个初始信息')
    remark = Column(String(2560, 'utf8mb4_unicode_ci'), comment='备注')
    creator = Column(String(64, 'utf8mb4_unicode_ci'), server_default=text("''"), comment='创建者')
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    updater = Column(String(64, 'utf8mb4_unicode_ci'), server_default=text("''"), comment='更新者')
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    status = Column(String(256, 'utf8mb4_unicode_ci'), nullable=False, server_default=text("'0'"), comment='0草稿、1上岗、2下岗、3维护中、4删除、')
    deleted = Column(BIT(1), nullable=False)
    tenant_id = Column(BIGINT(20), nullable=False, server_default=text("'0'"), comment='租户编号')

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

# db = pymysql.connect(host='114.132.155.77', user='root', passwd='root', port=31189, db='ruoyi-kl')
# 创建引擎
engine = create_engine(
    # "mysql+pymysql://root:root@114.132.155.77:31189/ruoyi-kl?charset=utf8mb4",
    # "mysql+pymysql://tom@127.0.0.1:3306/db1?charset=utf8mb4", # 无密码时
    "mysql+pymysql://root:root@127.0.0.1:3306/crudboy?charset=utf8mb4", # 无密码时
    # "mysql+pymysql://crudboy:root@47.102.105.8:3306/crudboy?charset=utf8mb4", # 无密码时
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
session = scoped_session(Session) # 需要在每个线程中使用session对象时，都需要调用session()方法获取session对象； 全局唯一， 静态化


class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

# response = DotDict({'aa': 11})
# print(response.aa)  # 输出：11