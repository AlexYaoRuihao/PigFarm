from flask import make_response
import re
import hashlib
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
# from utils import json_response, check_3dup
import json

JSON_MIME_TYPE = 'application/json'
theme_dict = {
            1 : "airport",
            2 : "bus_stop",
            3 : "casino",
            4 : "cinema",
            5 : "clothes",
            6 : "factory",
            7 : "fastfood",
            8 : "fitness_room",
            9 : "golf",
            10: "hospital",
            11: "hotel",
            12: "hotpot",
            13: "library",
            14: "liquor",
            15: "mid_autumn_festival",
            16: "office",
            17: "park",
            18: "subway",
            19: "vacation",
            20: "zoo"
}

rmb_table_dict = {
            1 : "rmb1table",
            2 : "rmb2table",
            3 : "rmb5table",
            4 : "rmb10table",
            5 : "rmb50table",
            6 : "rmb88table",
            7 : "rmb100table",
            8 : "rmb521table",
            9 : "rmb666table",
            10: "rmb888table",
            11: "rmb1314table",
            12: "rmb6324table",
            13: "rmb8888table",
            14: "rmb13999table",
            15: "rmb88888table",
}

token_table_dict = {
            1 : "token10000table",
            2 : "token50000table",
            3 : "token100000table",
            4 : "token200000table",
            5 : "token500000table",
            6 : "token1000000table",
            7 : "token5000000table",
            8 : "rmb888token5000000table",
            9 : "rmb6666token10000000table"
}



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
        query = "select user_id_hash, day_theme_list from user where user_id_hash={user_id_hash}".format(user_id_hash = user_id_hash)
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
            json_theme_list.append("\\\"" + k + "\\\"" + " : " + "\\\"" + v + "\\\"")
        json_theme_list_query = ",".join(json_theme_list)
        query = "update user set day_theme_list = '{" + json_theme_list_query + "}' " + "where user_id_hash={user_id_hash}".format(user_id_hash = user_id_hash)
        return query
    else:
        raise ValueError("{query_type} not implemented!".format(query_type=query_type))

def calculate_rewards(d):
    pass