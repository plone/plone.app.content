import json
import datetime
import Missing


def custom_json_handler(obj):
    if obj == Missing.Value:
        return None
    if type(obj) in (datetime.datetime, datetime.date):
        return obj.isoformat()
    return obj


def json_dumps(data):
    return json.dumps(data, default=custom_json_handler)


# can eventually provide custom handling here if we want
json_loads = json.loads