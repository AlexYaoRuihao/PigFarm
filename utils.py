from flask import make_response
import re

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
