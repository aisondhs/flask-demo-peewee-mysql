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
	
class User(MySQLModel):
    username = CharField()
    email = CharField()
    pw_hash = CharField()

class Follower(MySQLModel):
	who = ForeignKeyField(User, related_name='users')
	whom = ForeignKeyField(User, related_name='users')

class Message(MySQLModel):
    author = ForeignKeyField(User, related_name='users')
    text = TextField()
    pub_date = IntegerField()

if __name__ == '__main__':
	User.create_table(True)
	Follower.create_table(True)
	Message.create_table(True)