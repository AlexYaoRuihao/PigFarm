from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from .utils import json_response
import json

app = Flask(__name__)
# INSERT  INTO `user`(`uid`,`info`) VALUES (1,'{\"mail\": \"jiangchengyao@gmail.com\", \"name\": \"David\", \"address\": \"Shangahai\"}'),(2,'{\"mail\": \"amy@gmail.com\", \"name\": \"Amy\"}');
# SELECT uid,json_extract(info,'$.mail') AS 'mail',json_extract(info,'$.name') AS 'name' FROM USER;


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
    if X_APP_ID is None:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 401)
    
    data = request.json
    if not all([data.get("user_id"), data.get("username"), data.get("last_login_date"), data.get("current_cash"), data.get("current_token")]):
        error = json.dumps({"error" : "HTTPS request body imcomplete!"})
        return json_response(error, 402)
    
    params = {
        "user_id": data["user_id"],
        "username": data["username"],
        "last_login_date": data["last_login_date"],
        "current_cash": data["current_cash"],
        "current_token": data["current_token"]
    }
    try:
        HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
        PORT = "3306"
        DATABASE = "pigfarmdb"
        USERNAME = "myadmin"
        PASSWORD = "GGhavefun123"

        DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
        format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

        engine = create_engine(DB_URI)
        conn = engine.connect()

        # ground_truth_list = []
        result = conn.execute("select username, current_cash, current_token from user where user_id={user_id};".format(user_id=params["user_id"]))
        ground_truth_list = result.fetchall()
        if ground_truth_list[0][0] != params["username"]:
            error = json.dumps({"error" : "username mismatch!"})
            return json_response(error, 403)
        if ground_truth_list[0][1] != params["current_cash"]:
            error = json.dumps({"error" : "current_cash mismatch!"})
            return json_response(error, 403)
        if ground_truth_list[0][2] != params["current_token"]:
            error = json.dumps({"error" : "current_token mismatch!"})
            return json_response(error, 403)

        # then perform updates on last_login_date
        result = conn.execute("select timestampdiff(second, user.last_login_date, CURRENT_TIMESTAMP) from user where user_id={user_id};".format(user_id=params["user_id"]))
        timediff = result.fetchall()
        timediff = timediff[0][0]
        if timediff > 86400: # exceed one day
            result = conn.execute("update user set last_login_date = CURRENT_TIMESTAMP where user_id={user_id};".format(user_id=params["user_id"]))
        else: # doesn't exceed one day
            pass
        current_last_login_date = conn.execute("select last_login_date from user where user_id={user_id};".format(user_id=params["user_id"]))
        current_last_login_date = current_last_login_date[0][0]
        conn.close()
        return json_response(json.dumps({"user_id" : params["user_id"], "last_login_date" : current_last_login_date}), 200)
    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 403)



# 
@app.route("/items/<int:id>")
def items(id = None, X_APP_ID = None):
    if id is None:
        error = json.dumps({"error" : "Non existing id!"})
        return json_response(error, 400)
    if X_APP_ID is None:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 401)
    




if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port="8080", ssl_context = ("SSL_Certificate.key","SSL_Certificate.pem"))