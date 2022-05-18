from DateTime import DateTime

import datetime
import Missing

# use simplejson because it's ahead of stdlib and supports more types
import simplejson


def custom_json_handler(obj):
    if obj == Missing.Value:
        return None
    obj_type = type(obj)
    if obj_type in (datetime.datetime, datetime.date):
        return obj.isoformat()
    if obj_type == DateTime:
        dt = DateTime(obj)
        return dt.ISO()
    if obj_type == set:
        return list(obj)
    return obj


def json_dumps(data):
    return simplejson.dumps(data, default=custom_json_handler)


# can eventually provide custom handling here if we want
json_loads = simplejson.loads
