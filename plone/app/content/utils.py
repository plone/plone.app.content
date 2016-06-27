# -*- coding: utf-8 -*-
# utils.py
import Missing
import datetime
import json
import DateTime

def custom_json_handler(obj):
    if obj == Missing.Value:
        return None
    if type(obj) == set: 
        obj = list(obj)
    if type(obj) == DateTime.DateTime:
        return obj.asdatetime().isoformat()
    if type(obj) in (datetime.datetime, datetime.date):
        return obj.isoformat()
    return obj


def json_dumps(data):
    return json.dumps(data, default=custom_json_handler)


# can eventually provide custom handling here if we want
json_loads = json.loads
