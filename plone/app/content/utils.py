from DateTime import DateTime
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

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
        return obj.ISO()
    if obj_type == set:
        return list(obj)
    if obj_type == PersistentMapping:
        return dict(obj)
    if obj_type == PersistentList:
        return list(obj)
    return obj


def json_dumps(data):
    return simplejson.dumps(data, default=custom_json_handler)


# can eventually provide custom handling here if we want
json_loads = simplejson.loads
