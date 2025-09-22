from DateTime import DateTime
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

import datetime
import Missing

# use simplejson because it's ahead of stdlib and supports more types
import simplejson


try:
    from z3c.relationfield.relation import RelationValue
except ImportError:
    RelationValue = None


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
    if RelationValue is not None and obj_type == RelationValue:
        return obj.to_id
    return obj


def json_dumps(data):
    return simplejson.dumps(data, default=custom_json_handler)


# can eventually provide custom handling here if we want
json_loads = simplejson.loads


def get_recycle_bin_message(title=None, retention_period=0):
    """Generate appropriate message for recycled items based on retention period.
    
    Args:
        title: The title of the deleted item (optional, for single item messages)
        retention_period: Number of days to retain items (0 = indefinite)
    
    Returns:
        Translated message string
    """
    from plone.base import PloneMessageFactory as _
    
    if title:
        # Single item message
        if retention_period == 0:
            return _(
                "${title} has been moved to the recycle bin. It can be restored by administrators.",
                mapping={"title": title},
            )
        else:
            return _(
                "${title} has been moved to the recycle bin. It can be restored by administrators and will be permanently deleted after ${days} days.",
                mapping={"title": title, "days": retention_period},
            )
    else:
        # Multiple items message
        if retention_period == 0:
            return _("Successfully moved items to recycle bin. Items can be restored by administrators.")
        else:
            return _(
                "Successfully moved items to recycle bin. Items can be restored by administrators and will be permanently deleted after ${days} days.",
                mapping={"days": retention_period},
            )
