from Products.CMFCore.PortalContent import PortalContent
from Products.CMFPlone.DublinCore import DefaultDublinCoreImpl
from zope.container.contained import Contained
from zope.interface import implementer

from plone.app.content.interfaces import IReindexOnModify


@implementer(IReindexOnModify)
class Item(PortalContent, DefaultDublinCoreImpl, Contained):
    """A non-containerish, CMFish item"""

    def __init__(self, id=None, **kwargs):
        DefaultDublinCoreImpl.__init__(self, **kwargs)
        if id is not None:
            self.id = id
