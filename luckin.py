from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from utils import json_response, check_3dup, generate_day_theme_list, build_queries_from_dict, transform_into_listofdict, build_queries_from_dict_username
from utils import theme_dict, rmb_table_dict, token_table_dict, ip2int, int2ip, get_sha256_hash
import json
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
import datetime

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
# INSERT  INTO `user`(`uid`,`info`) VALUES (1,'{\"mail\": \"jiangchengyao@gmail.com\", \"name\": \"David\", \"address\": \"Shangahai\"}'),(2,'{\"mail\": \"amy@gmail.com\", \"name\": \"Amy\"}');
# SELECT uid,json_extract(info,'$.mail') AS 'mail',json_extract(info,'$.name') AS 'name' FROM USER;
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


@app.before_request
def before_request():
    # HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
    # PORT = "3306"
    # DATABASE = "pigfarmdb"
    # USERNAME = "myadmin"
    # PASSWORD = "GGhavefun123"
    # RMB1_TABLE = "rmb1table"

    # DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
    #     format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

    # engine = create_engine(DB_URI)
    # conn = engine.connect()
    # result = conn.execute("select pattern from {rmb1} ORDER BY RAND() LIMIT 1;".format(rmb1=RMB1_TABLE))
    # print(result.fetchall())
    # conn.close()
    pass

@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    # return jsonify({
    #     'status': 401,
    #     'sub_status': 42,
    #     'msg': 'The {} token has expired'.format(token_type)
    # }), 401
    error = json.dumps({"error" : "The {} token has expired".format(token_type)})
    return json_response(error, 401)

@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_token):
    token_type = invalid_token['type']
    error = json.dumps({"error" : "The {} token is invalid".format(token_type)})
    return json_response(error, 404)



# Background scheduler task
def refresh_theme_list():
    # get all users
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

        result = conn.execute("select user_id from user;")
        user_row_list = result.fetchall()
        for each_user in user_row_list:
            day_theme_list = generate_day_theme_list()
            query = build_queries_from_dict(each_user[0], day_theme_list, "UPDATE")
            conn.execute(query)
        conn.close()
    except Exception as e:
        print(e)
        conn.close()





@app.route("/login", methods = ["POST"])
def login():
    try: 
        X_APP_ID = request.headers["X-App-Id"]
    except:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 403)
    
    try:
        X_DEVICE_ID = request.headers["X-Device-Id"]
    except:
        error = json.dumps({"error" : "Missing X-DEVICE-ID!"})
        return json_response(error, 403)
    
    data = request.json
    try:
        b = all([data.get("username"), data.get("password")])
    except Exception as e:
        # print(e)
        error = json.dumps({"error" : "HTTPS request body imcomplete!"})
        return json_response(error, 402)

    params = {
        "username": data["username"],
        "password": data["password"]
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

        result = conn.execute("select password from user where username=\"{var1}\";".format(var1=params["username"]))
        user_password = result.fetchone()[0]

        if user_password != params["password"]:
            error = json.dumps({"error":"password mismatch!"})
            return json_response(error, 405)
        
        expires = datetime.timedelta(days=10)
        token = create_access_token(params["username"], expires_delta=expires)

        # conn.execute("update user set user_id_hash = \"{var2}\" where username = \"{var3}\";".format(var2=token, var3=params["username"]))

        return_data = {"token": token}
        conn.close()
        # return json_response(return_data, 200)
        return jsonify(return_data), 200
    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 406)




    


@app.route("/register", methods = ["POST"])
def register():
    print("request.headers",request.headers)
    try:
        X_APP_ID = request.headers["X-App-Id"]
    except:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 403)
    
    try:
        X_DEVICE_ID = request.headers["X-Device-Id"]
    except:
        error = json.dumps({"error" : "Missing X-DEVICE-ID!"})
        return json_response(error, 403)

    data = request.json
    print("data",data)
    try:
        b = all([data.get("username"), data.get("password"), data.get("phone"), data.get("email"), data.get("WeChatID")])
    except Exception as e:
        # print(e)
        error = json.dumps({"error" : "HTTPS request body imcomplete!"})
        return json_response(error, 400)

    params = {
        "username": data["username"],
        "password": data["password"],
        "phone": data["phone"],
        "email": data["email"],
        "WeChatID": data["WeChatID"]
    }

    IP_addr = request.remote_addr
    IP_addr_int = ip2int(IP_addr)

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

        conn.execute("insert into user(username, password, email, phone, WeChatID, registered_IP) VALUES(\"{username}\", \"{password}\", \"{email}\", {phone}, \"{WeChatID}\", {registered_IP});"\
            .format(username=params["username"], password=params["password"], email=params["email"], phone=params["phone"], WeChatID=params["WeChatID"], registered_IP=IP_addr_int))

        # result = conn.execute("select user_id from user where username=\"{var1}\";".format(var1=params["username"]))
        # user_id = result.fetchone()[0]

        # user_id_hash = get_sha256_hash(str(user_id))

        # conn.execute("update user set user_id_hash = \"{var2}\" where username = \"{var3}\";".format(var2=user_id_hash, var3=params["username"]))

        day_theme_list = generate_day_theme_list()
        query = build_queries_from_dict_username(params["username"], day_theme_list, "UPDATE")
        conn.execute(query)

        conn.close()
        return json_response()
    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 403)



# check validity of account token
@app.route("/verification/account", methods = ["POST"])
@jwt_required
# def verification(X_DEVICE_ID = None, X_APP_ID = None):
def verification():
    try:
        X_APP_ID = request.headers["X-App-Id"]
    except:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 403)
    
    try:
        X_DEVICE_ID = request.headers["X-Device-Id"]
    except:
        error = json.dumps({"error" : "Missing X-DEVICE-ID!"})
        return json_response(error, 403)

    
    data = request.json
    try:
        b = all([data.get("current_cash"), data.get("current_token")])
    except Exception as e:
        # print(e)
        error = json.dumps({"error" : "HTTPS request body imcomplete!"})
        return json_response(error, 402)
    
    # print("user_id_hash", data["user_id_hash"])
    params = {
        # "user_id_hash": data["token"],
        # "username": data["username"],
        # "last_login_date": data["last_login_date"],
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

        username = get_jwt_identity()

        # ground_truth_list = []
        # print("select username, current_cash, current_token from user where user_id_hash={user_id_hash};".format(user_id_hash=params["user_id_hash"]))
        result = conn.execute("select current_cash, current_token from user where username=\"{username}\";".format(username=username))
        ground_truth_list = result.fetchall()
        # if ground_truth_list[0][0] != username:
        #     error = json.dumps({"error" : "username mismatch!"})
        #     return json_response(error, 403)
        if (str(ground_truth_list[0][0]) != params["current_cash"]) and (str(ground_truth_list[0][1]) != params["current_token"]):
            error = json.dumps({"error" : "current_cash and current_token mismatch!"})
            return json_response(error, 403)
        if str(ground_truth_list[0][0]) != params["current_cash"]:
            error = json.dumps({"error" : "current_cash mismatch!"})
            return json_response(error, 403)
        if str(ground_truth_list[0][1]) != params["current_token"]:
            error = json.dumps({"error" : "current_token mismatch!"})
            return json_response(error, 403)

        # then perform updates on last_login_date
        result = conn.execute("select timestampdiff(second, user.last_login_date, CURRENT_TIMESTAMP) from user where username=\"{username}\";".format(username=username))
        timediff = result.fetchall()
        timediff = timediff[0][0]
        # print("type(timediff)",type(timediff))
        if timediff > 86400: # exceed one day
            result = conn.execute("update user set last_login_date = CURRENT_TIMESTAMP where username=\"{username}\";".format(username=username))

            expires = datetime.timedelta(days=10)
            token = create_access_token(username, expires_delta=expires)

            # conn.execute("update user set user_id_hash = \"{var2}\" where username = \"{var3}\";".format(var2=token, var3=params["username"]))

        else: # doesn't exceed one day
            token = request.headers["authorization"]
            token = token.split()[1]
            pass
        # current_last_login_date = conn.execute("select last_login_date from user where user_id_hash=\"{user_id_hash}\";".format(user_id_hash=params["user_id_hash"]))
        # current_last_login_date = current_last_login_date.fetchall()[0][0]
        # result = conn.execute("select user_id_hash from user where username=\"{username}\";".format(username=params["username"]))
        # account_token = result.fetchone()[0]
        conn.close()
        return json_response(json.dumps({"account" : token}), 200)
    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 403)



# 
@app.route("/items/<string:id>")
@jwt_required
def items(id = None):
    if id is None:
        error = json.dumps({"error" : "Non existing id!"})
        return json_response(error, 400)

    try:
        X_APP_ID = request.headers["X-App-Id"]
    except:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 401)

    
    # pre-calculate a day's profits if possible
    # perform sanity checks first
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

        username = get_jwt_identity()

        # result = conn.execute("select user_id_hash, current_cash, current_token from user where user_id_hash={user_id_hash};".format(user_id_hash=str(id)))
        # day_theme_list = generate_day_theme_list()
        # query = build_queries_from_dict(id, day_theme_list, "UPDATE")
        #perform updates on user's day_theme_list field
        # conn.execute(query)

        result = conn.execute("select day_theme_list from user where username=\"{username}\";".format(username = username))
        day_theme_list = result.fetchone()[0]
        day_theme_list = json.loads(day_theme_list)

        conn.close()

        return json_response(json.dumps(transform_into_listofdict(day_theme_list)), 200)




    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 403)


@app.route("/items/<string:id1>/item/<string:id2>")
@jwt_required
def get_items(id1 = None, id2 = None):
    if id1 is None:
        error = json.dumps({"error" : "Non existing id!"})
        return json_response(error, 403)
    if id2 is None:
        error = json.dumps({"error" : "Non existing id!"})
        return json_response(error, 403)
    
    try:
        X_APP_ID = request.headers["X-App-Id"]
    except:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 403)

    try:
        return_dict = {}
        id1_str = str(id1)
        id2_str = str(id2)
        HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
        PORT = "3306"
        DATABASE = "pigfarmdb"
        USERNAME = "myadmin"
        PASSWORD = "GGhavefun123"

        DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
            format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

        engine = create_engine(DB_URI)
        conn = engine.connect()

        username = get_jwt_identity()

        result = conn.execute("select user_id, day_theme_list from user where username=\"{username}\";".format(username = username))
        day_theme_dict = json.loads(result.fetchall()[0][1])
        encoded_str = day_theme_dict[id2_str]
        encoded_str_list = encoded_str.split("|")
        return_dict["bonus"] = int(encoded_str_list[4])
        return_dict["order"] = [int(encoded_str_list[3][0]), int(encoded_str_list[3][1]), int(encoded_str_list[3][2]), int(encoded_str_list[3][3]), int(encoded_str_list[3][4]), int(encoded_str_list[3][5])]

        conn.close()
        return json_response(json.dumps(return_dict), 200)

    
    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 403)


@app.route("/items/<string:id1>/item/<string:id2>", methods = ["POST"])
@jwt_required
def get_items_post(id1 = None, id2 = None):
    if id1 is None:
        error = json.dumps({"error" : "Non existing id!"})
        return json_response(error, 400)
    if id2 is None:
        error = json.dumps({"error" : "Non existing id!"})
        return json_response(error, 400)
    
    try:
        X_APP_ID = request.headers["X-App-Id"]
    except:
        error = json.dumps({"error" : "Missing X-APP-ID!"})
        return json_response(error, 401)

    try:
        id1_str = str(id1)
        id2_str = str(id2)
        HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
        PORT = "3306"
        DATABASE = "pigfarmdb"
        USERNAME = "myadmin"
        PASSWORD = "GGhavefun123"

        DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
            format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

        engine = create_engine(DB_URI)
        conn = engine.connect()

        username = get_jwt_identity()

        result = conn.execute("select day_theme_list from user where username = \"{username}\";".format(username=username))

        day_theme_list = result.fetchall()[0][0]
        day_theme_list_dict = json.loads(day_theme_list)

        info_str = day_theme_list_dict[id2_str]
        info_str_l = info_str.split("|")
        rmb_or_token = info_str_l[1]
        if rmb_or_token == "r":
            reward = rmb_table_dict[int(info_str_l[2])]
        else:
            reward = token_table_dict[int(info_str_l[2])]
        
        three_dup = check_3dup(info_str_l[3])

        extra_tokens = info_str_l[4]

        day_theme_list_dict.pop(id2_str)
        day_theme_list_dict_str = json.dumps(day_theme_list_dict)
        conn.execute("update user set day_theme_list = '{var1}' where username=\"{username}\";".format(var1=day_theme_list_dict_str, username=username))
        if three_dup == False:
            # day_theme_list_dict.pop(id2_str)
            # day_theme_list_dict_str = json.dumps(day_theme_list_dict)
            # conn.execute("update user set day_theme_list = {var1} where user_id_hash={user_id_hash}".format(var1=day_theme_list_dict_str, user_id_hash=id1_str))
            pass
        else: # True
            if rmb_or_token == "r":
                conn.execute("update user set current_cash = current_cash + {var2} where username=\"{username}\";".format(var2=reward, username=username))
            else:
                conn.execute("update user set current_token = current_token + {var2} where username=\"{username}\";".format(var2=reward, username=username))

        # update extra tokens
        conn.execute("update user set current_token = current_token + {var3} where username=\"{username}\";".format(var3=extra_tokens, username=username))
        conn.close()
        return json_response()
    except Exception as e:
        conn.close()
        error = json.dumps({"error" : e})
        return json_response(error, 403)



sched = BackgroundScheduler(daemon=True)
sched.add_job(refresh_theme_list, 'interval', days=1, start_date="2020-4-15 00:00:00")
sched.start()
    
if __name__ == "__main__":
    # sched = BackgroundScheduler(daemon=True)
    # sched.add_job(refresh_theme_list,'cron',minute='*')
    # sched.start()
    app.debug = True
    app.run(host="0.0.0.0", port="8080", ssl_context = ("SSL_Certificate.key","SSL_Certificate.pem"))