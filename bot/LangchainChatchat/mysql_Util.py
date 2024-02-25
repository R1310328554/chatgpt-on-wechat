import pymysql
import json # json 数据处理库


def testCu(db):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 使用 execute() 方法执行 SQL，如果表存在则删除
    cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")

    # 使用预处理语句创建表
    sql = """CREATE TABLE EMPLOYEE (
            FIRST_NAME  CHAR(20) NOT NULL,
            LAST_NAME  CHAR(20),
            AGE INT,  
            SEX CHAR(1),
            INCOME FLOAT )"""

    cursor.execute(sql)
    print('建表成功！')

def INSERT(db):
  # 使用 cursor() 方法创建一个游标对象 cursor
  cursor = db.cursor()

  # SQL 插入语句
  sql = """INSERT INTO EMPLOYEE(FIRST_NAME,
          LAST_NAME, AGE, SEX, INCOME)
          VALUES ('Mac', 'Mohan', 20, 'M', 2000)"""
  try:
      # 执行sql语句
      cursor.execute(sql)
      # 提交到数据库执行
      db.commit()
      print('数据插入成功！')
  except:
      # 如果发生错误则回滚
      db.rollback()
      print('数据插入错误！')


def SELECT(db):
  # 使用 cursor() 方法创建一个游标对象 cursor
  cursor = db.cursor()

  # SQL 查询语句
  sql = "SELECT * FROM EMPLOYEE \
        WHERE INCOME > %s" % (1000)
  try:
      # 执行SQL语句
      cursor.execute(sql)
      # 获取所有记录列表
      results = cursor.fetchall()
      for row in results:
          fname = row[0]
          lname = row[1]
          age = row[2]
          sex = row[3]
          income = row[4]
          # 打印结果
          print('数据查询成功！')
          print("fname=%s,lname=%s,age=%s,sex=%s,income=%s" % \
                (fname, lname, age, sex, income))
  except:
      print("Error: unable to fetch data")


def UPDATE(db):
    # SQL 更新语句
  sql = "UPDATE EMPLOYEE SET AGE = AGE + 1 WHERE SEX = '%c'" % ('M')
  try:
      cursor = db.cursor()
      # 执行SQL语句
      cursor.execute(sql)
      # 提交到数据库执行
      db.commit()
      print('数据更新成功！')
  except:
      # 发生错误时回滚
      db.rollback()
      
def DELETE(db):
    # SQL 删除语句
    sql = "DELETE FROM EMPLOYEE WHERE AGE > %s" % (20)
    try:
        cursor = db.cursor()
        # 执行SQL语句
        cursor.execute(sql)
        # 提交修改
        db.commit()
        print('数据删除成功')
    except:
        # 发生错误时回滚
        db.rollback()
        
def db():
    # 
    # sqlacodegen.exe --outfile msds_mod.py mysql+pymysql://root:root@114.132.155.77:31189/ruoyi-kl  --tables xg_msds,xg_msds_type,xg_msds_rel_type,xg_msds_pick,xg_msds_return,xg_msds_stocking,xg_msds_unstocking 
    #           url: jdbc:mysql://114.132.155.77:31189/${spring.datasource.dynamic.datasource.master.name}?useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&nullCatalogMeansCurrent=true # MySQL Connector/J 8.X 连接的示例
    try:
        db = pymysql.connect(host='114.132.155.77', user='root', passwd='root', port=31189, db='ruoyi-kl')
        print('连接成功！')
        
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()

        # 使用 execute()  方法执行 SQL 查询
        cursor.execute("SELECT VERSION()")

        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchone()

        print("Database version : %s " % data)
        
        # 关闭数据库连接
        db.close()
        return db
    except Exception as e:
        print('something wrong!', e)

    '''
    连接成功！
    Database version : 8.0.25 
    '''
    
def main():
    # 打开数据库连接
    # ruoyi-kl 
    db2 = db()
    # testCu(db)
    # INSERT(db)
    # SELECT(db)
    
    d = {
        'name': "Mary",
        'address': "address123",
        # 'gender': "male",
        'phone': 123,
        'age': 20
    }
    
    print( *d )
    # print( **d ) TypeError: 'name' is an invalid keyword argument for print()
    print( d.get( 'name' ) )

    # 获取链接池、ORM表对象
    import models
    user_instance1 = models.UserInfo(
        **d
    )
    print ( user_instance1.name )
    print ( user_instance1.address )
    print ( user_instance1.age )


def pymysqlTest(rows):
  db = db()
  cursor = db.cursor()

  tb = 'xg_msds'
  try:
    for row in rows:
        # SQL 插入语句 #  batch 操作语法 ！ 
        sql = f"""INSERT INTO {tb}( num, name, enName, alias, cas, categorys, remark, pic, link )
                VALUES ( {row} )"""
        # 执行sql语句
        cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
    print('数据插入成功！')
  except:
      # 如果发生错误则回滚
      db.rollback()
      print('数据插入错误！')


main()


