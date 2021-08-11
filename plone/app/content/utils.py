import datetime

import Missing

# use simplejson because it's ahead of stdlib and supports more types
import simplejson
from DateTime import DateTime


def custom_json_handler(obj):
    if obj == Missing.Value:
        return None
    if type(obj) in (datetime.datetime, datetime.date):
        return obj.isoformat()
    if type(obj) == DateTime:
        dt = DateTime(obj)
        return dt.ISO()
    if type(obj) == set:
        return list(obj)
    return obj


def json_dumps(data):
    return simplejson.dumps(data, default=custom_json_handler)


# can eventually provide custom handling here if we want
json_loads = simplejson.loads
