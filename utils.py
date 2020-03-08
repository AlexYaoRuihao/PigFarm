from flask import make_response
import re
import hashlib
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
# from utils import json_response, check_3dup
import json, random
import socket
import struct

JSON_MIME_TYPE = 'application/json'
theme_dict = {
            1 : "airport",
            2 : "bus_stop",
            3 : "cake",
            4 : "casino",
            5 : "cinema",
            6 : "clothes",
            7 : "factory",
            8 : "fastfood",
            9 : "firestation",
            10: "fitness_room",
            11: "golf",
            12: "home",
            13: "hospital",
            14: "hotel",
            15: "hotpot",
            16: "library",
            17: "liquor",
            18: "mid_autumn_festival",
            19: "office",
            20: "park",
            21: "police_office",
            22: "school",
            23: "subway",
            24: "vacation",
            25: "zoo"
}

rmb_table_dict = {
            # 1 : "rmb1table",
            # 2 : "rmb2table",
            # 3 : "rmb5table",
            # 4 : "rmb10table",
            # 5 : "rmb50table",
            # 6 : "rmb88table",
            # 7 : "rmb100table",
            # 8 : "rmb521table",
            # 9 : "rmb666table",
            # 10: "rmb888table",
            # 11: "rmb1314table",
            # 12: "rmb6324table",
            # 13: "rmb8888table",
            # 14: "rmb13999table",
            # 15: "rmb88888table",
            1 : 1,
            2 : 2,
            3 : 5,
            4 : 10,
            5 : 50,
            6 : 88,
            7 : 100,
            8 : 521,
            9 : 666,
            10: 888,
            11: 1314,
            12: 6324,
            13: 8888,
            14: 13999,
            15: 88888
}

token_table_dict = {
            # 1 : "token10000table",
            # 2 : "token50000table",
            # 3 : "token100000table",
            # 4 : "token200000table",
            # 5 : "token500000table",
            # 6 : "token1000000table",
            # 7 : "token5000000table",
            # 8 : "rmb888token5000000table",
            # 9 : "rmb6666token10000000table"
            1 : 10000,
            2 : 50000,
            3 : 100000,
            4 : 200000,
            5 : 500000,
            6 : 1000000,
            7 : 5000000
}

extra_tokens_table = "extratokentable"


def json_response(data = "", status = 200, headers = None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = JSON_MIME_TYPE
        
    return make_response(data, status, headers)

def check_3dup(s):
    for n in range(4):
        char_count = len(re.findall(str(n), s))
        if char_count >= 3:
            return True
    return False

def get_sha256_hash(s):
    return hashlib.sha256((s).encode("utf-8")).hexdigest()


# update user set `day_theme_list` = '{\"0\": \"Airport\", \"1\": \"Bus_Stop\", \"2\": \"Casino\"}' where `user_id` = 1;
def build_queries_from_dict(user_id_hash, d, query_type):
    if query_type == "SELECT":
        query = "select user_id_hash, day_theme_list from user where user_id_hash=\"{user_id_hash}\";".format(user_id_hash = user_id_hash)
        return query
    elif query_type == "INSERT":
        # json_theme_list = []
        # for k, v in d.items():
        #     json_theme_list.append("\\\"" + k + "\\\"" + " : " + "\\\"" + v + "\\\"")
        # json_theme_list_query = ",".join(json_theme_list)
        # query = "insert into user day_theme_list = '{" + json_theme_list_query + "}' " + "where user_id_hash={user_id_hash}".format(user_id_hash = user_id_hash)
        # return query
        pass
    elif query_type == "UPDATE":
        json_theme_list = []
        for k, v in d.items():
            json_theme_list.append("\"" + str(k) + "\"" + " : " + "\"" + str(v) + "\"")
            # json_theme_list.append(str(k) + ":" + str(v))
        json_theme_list_query = ",".join(json_theme_list)
        query = "update user set day_theme_list = '{" + json_theme_list_query + "}'" + "where user_id_hash=\"{user_id_hash}\";".format(user_id_hash = user_id_hash)
        return query
    else:
        raise ValueError("{query_type} not implemented!".format(query_type=query_type))

def generate_day_theme_list(day_theme_num=25):
    day_theme_list = {}
    HOSTNAME = "rm-uf6ktwa39f10394a7no.mysql.rds.aliyuncs.com"
    PORT = "3306"
    DATABASE = "pigfarmdb"
    USERNAME = "myadmin"
    PASSWORD = "GGhavefun123"

    DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".\
    format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

    engine = create_engine(DB_URI)
    conn = engine.connect()



    for day_theme_idx in range(day_theme_num):
        if day_theme_idx < 20:
            day_theme_idx_hash = get_sha256_hash(str(day_theme_idx))
            theme_num = random.randint(1,25)
            cash_or_token = "r"
            table_num = random.randint(1,15)
            # get pattern
            table_name = "rmb"+str(rmb_table_dict[table_num])+"table"
            result = conn.execute("select pattern from {table_name} ORDER BY RAND() LIMIT 1;".format(table_name=table_name))
            pattern = result.fetchall()[0][0]
            result = conn.execute("select pattern from {table_name} ORDER BY RAND() LIMIT 1;".format(table_name=extra_tokens_table))
            extra_token_pattern = result.fetchall()[0][0]
            day_theme_list[day_theme_idx_hash] = str(theme_num)+"|"+cash_or_token+"|"+str(table_num)+"|"+pattern+"|"+extra_token_pattern 
        else:
            day_theme_idx_hash = get_sha256_hash(str(day_theme_idx))
            theme_num = random.randint(1,25)
            cash_or_token = "t"
            table_num = random.randint(1,7)
            # get pattern
            table_name = "token"+str(token_table_dict[table_num])+"table"
            result = conn.execute("select pattern from {table_name} ORDER BY RAND() LIMIT 1;".format(table_name=table_name))
            pattern = result.fetchall()[0][0]
            result = conn.execute("select pattern from {table_name} ORDER BY RAND() LIMIT 1;".format(table_name=extra_tokens_table))
            extra_token_pattern = result.fetchall()[0][0]
            day_theme_list[day_theme_idx_hash] = str(theme_num)+"|"+cash_or_token+"|"+str(table_num)+"|"+pattern+"|"+extra_token_pattern 
    conn.close()
    return day_theme_list

def transform_into_listofdict(d):
    day_theme_list_of_dict = []
    for k, v in d.items():
        temp_dict = {}
        decoded_data = v.split("|")
        temp_dict["theme"] = theme_dict[int(decoded_data[0])]
        temp_dict["pattern"] = decoded_data[3]
        day_theme_list_of_dict.append(temp_dict)
    return day_theme_list_of_dict


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))