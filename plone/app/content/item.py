from zope.container.contained import Contained
from zope.interface import implements

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from plone.app.content.interfaces import IReindexOnModify


class Item(PortalContent, DefaultDublinCoreImpl, Contained):
    """A non-containerish, CMFish item
    """

    implements(IReindexOnModify)

    def __init__(self, id=None, **kwargs):
        DefaultDublinCoreImpl.__init__(self, **kwargs)
        if id is not None:
            self.id = id
