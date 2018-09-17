# -*- coding: utf-8 -*-
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFPlone.DublinCore import DefaultDublinCoreImpl
from plone.app.content.interfaces import IReindexOnModify
from zope.container.contained import Contained
from zope.container.interfaces import IContainer
from zope.interface import implementer

import six


@implementer(IContainer)
class OFSContainer(object):
    """A folder that's also a container.

    Borrowed in part from megrok.five.
    """

    isPrincipiaFolderish = 1

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
        if six.PY2 and isinstance(name, six.text_type):
            name = name.encode('ascii')  # may raise if there's a bugus id
        self._setObject(name, obj)

    def __delitem__(self, name):
        self.manage_delObjects([name])

    def __contains__(self, name):
        return self.hasObject(name)

    def __iter__(self):
        return iter(self.objectIds())

    def __len__(self):
        return len(self.objectIds())

# Notes on this insane mixing of classes:
#
#  - OFSContainer gives us Zope3-like container operations, and we want that
#       to take priority so it comes first
#  - CMFCatalogAware gives us catalog functionality. So does PortalContent,
#       but PortalFolderBase overrides indexObject() and friends to do
#       nothing.
#  - PortalFolderBase gives folder-like behaviour. It needs to come before
#       PortalContent, otherwise objectIds() and friends don't work
#  - PortalContent gives us SearchableText and WebDAV
#  - DublinCoreImpl gives us DC fields
#  - Contained gives us Zope3-like containment
#
# ... I WANT AN ADAPTER!


@implementer(IReindexOnModify)
class Container(OFSContainer, CMFCatalogAware, PortalFolderBase, PortalContent,
                DefaultDublinCoreImpl, Contained):
    """A base class mixing in CMFish, contentish, containerish, containedish,
    dublincoreish behaviour.
    """

    def __init__(self, id=None, **kwargs):
        OFSContainer.__init__(self, id, **kwargs)
        PortalFolderBase.__init__(self, id, **kwargs)
        DefaultDublinCoreImpl.__init__(self, **kwargs)

        if id is not None:
            self.id = id
