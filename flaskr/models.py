#--*-- coding:utf-8 --*--
from peewee import *

def get_db():
    mysql_db = MySQLDatabase("flaskr", user = "root", passwd = "123456", charset = "utf8")
    mysql_db.connect() #连接数据库
    return mysql_db

mysql_db = get_db()

class MySQLModel(Model):
    class Meta:
        database = mysql_db

class Entries(MySQLModel): #类的小写即表名
    title = CharField() #字段声明
    text = TextField()

if __name__ == '__main__':
	Entries.create_table()