from zope.app.container.contained import Contained

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

class Item(PortalContent, DefaultDublinCoreImpl, Contained):
    """A non-containerish, CMFish item
    """
    
    def __init__(self, id=None):
        if id is not None:
            self.id = id