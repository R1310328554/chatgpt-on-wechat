import pymysql
import json # json 数据处理库
import os,re,sys,math,datetime,zipfile
import chardet,codecs
# from mysql_Util import *
from bot.LangchainChatchat import models 
# from models import AscBotBaseCfg as models

from sqlalchemy import *


def select ():
  # user_instance1 = models.AscBotBaseCfg( )
  # result = models.session.query(  models.AscBotBaseCfg ).all()
  result = models.session.query(  models.AscBotBaseCfg.name,
                                      models.AscBotBaseCfg.code.label("s_code")
                                  ).all()[0:20]
  # .filter_by(name="Jack")
  print(len ( result) )
  for row in result:
      print(row )
      print(row.s_code, row.name )
      pass
  models.session.close()
  
def selectById(botId):
  # user_instance1 = models.AscBotBaseCfg( )
  result = models.session.query(  models.AscBotBaseCfg ).filter_by(id=botId).first()
  # .filter_by(name="Jack") 
  print(result.code, result.name )
  models.session.close()
  return result
  
def sqlAchademy ():
  pass

def delete ():
  user_instance1 = models.AscBotBaseCfg( )
  result = models.session.query(  models.AscBotBaseCfg ).delete()
  print('deleted: ',result)
  models.session.commit()
  models.session.close()
  pass

def upd ():
  user_instance1 = models.AscBotBaseCfg( )
  result = models.session.query(  models.AscBotBaseCfg ).update()
  print('updated: ',result)
  models.session.commit()
  models.session.close()
  pass

selectById(1)
