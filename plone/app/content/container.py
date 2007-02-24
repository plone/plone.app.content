from zope.interface import implements
from zope.app.container.interfaces import IContainer
from zope.app.container.contained import Contained

from OFS.ObjectManager import ObjectManager

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

class OFSContainer(ObjectManager):
    """A folder that's also a container.
    
    Borrowed in part from megrok.five.
    """
    
    implements(IContainer)
    
    def __init__(self, id=None):
        if id is not None:
            self.id = id

    # fulfill IContainer interface

    def keys(self):
        return self.objectIds()

    def values(self):
        return self.objectValues()

    def items(self):
        return self.objectItems()

    def get(self, name, default=None):
        return getattr(self, name, default)

    # __getitem__ is already implemented by ObjectManager

    def __setitem__(self, name, obj):
        name = str(name) # Zope 2 doesn't like unicode names
        # TODO there should be a check here if 'name' contains
        # non-ASCII unicode data. In this case I think we should just
        # raise an error.
        self._setObject(name, obj)

    def __delitem__(self, name):
        self.manage_delObjects([name])

    def __contains__(self, name):
        return self.hasObject(name)

    def __iter__(self):
        return iter(self.objectIds())

    def __len__(self):
        return len(self.objectIds())
        
class Container(OFSContainer, PortalContent, PortalFolderBase, DefaultDublinCoreImpl, Contained):
    """A base class mixing in CMFish, contentish, containerish, containedish,
    dublincoreish behaviour.
    """
    
    def __init__(self, id=None):
        if id is not None:
            self.id = id