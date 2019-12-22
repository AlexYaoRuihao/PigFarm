from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from .utils import json_response

app = Flask(__name__)

@app.before_request
def before_request():
    HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
    PORT = "3306"
    DATABASE = "pigfarmdb"
    USERNAME = "myadmin"
    PASSWORD = "GGhavefun123"
    RMB1_TABLE = "rmb1table"

    DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
        format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

    engine = create_engine(DB_URI)
    conn = engine.connect()
    result = conn.execute("select pattern from {rmb1} ORDER BY RAND() LIMIT 1;".format(rmb1=RMB1_TABLE))
    print(result.fetchall())
    conn.close()





# check validity of account token
@app.route("/verification/account", methods = ["POST"])
def verification(X_DEVICE_ID = None, X_APP_ID = None):

    pass



# 
@app.route("/items/<int:id>")
def items(id = None, X_APP_ID = None):
    pass




if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port="8080", ssl_context = ("SSL_Certificate.key","SSL_Certificate.pem"))