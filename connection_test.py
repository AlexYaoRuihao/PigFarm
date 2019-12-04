from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
PORT = "3306"
DATABASE = "pigfarmdb"
USERNAME = "myadmin"
PASSWORD = "GGhavefun123"

RMB1_TABLE = "rmb1table"

DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
    format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

# app = Flask(__name__)
# app.config["rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"] = "sqlite:///example.sqlite"
# db = SQLAlchemy(app)
engine = create_engine(DB_URI)
conn = engine.connect()
result = conn.execute("select pattern from {rmb1} ORDER BY RAND() LIMIT 1;".format(rmb1=RMB1_TABLE))
print(result.fetchall())
conn.close()