flask-demo-peewee-mysql
=======================

Rewrite the Python web framework Flask's demos with the peewee and mysql

1.运行demo程序需要安装flask,MySQLdb以及peewee orm
  (1)pip install flask
  (2)下载MySQL-python-1.2.3.tar.gz并安装
  (3)pip install peewee
  
2.在mysql创建数据库flaskr，修改models.py中的数据库连接参数，生成初始化数据表
  python models.py
  
3.启动应用
  python flaskr.py 或者python minitwit.py
  在浏览器上输入查看启动的应用:http://127.0.0.1:5000
  
4.大家可以查看我vps上的部署的应用minitwit：http://twit.pytip.com
  欢迎访问我的个人博客:http://www.pytip.com

