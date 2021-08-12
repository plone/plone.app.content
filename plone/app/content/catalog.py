def reindexOnModify(content, event):
    """When an object is modified, re-index it in the catalog"""
    if event.object is not content:
        return
    content.reindexObject(idxs=getattr(event, "descriptions", []))
