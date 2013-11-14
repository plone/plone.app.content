# Zope imports
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class IFolderContentsView(Interface):
    """Interface, which provides methods for folder contens
    """
    def test(a, b, c):
        """A simple replacement of python's test.
        """

    def getAllowedTypes():
        """Returns allowed types for context.
        """

    def title():
        """Returns the title for the template.
        """


class IFolderContentsViewletManager(IViewletManager):
    """A viewlet manager for folder contents
    """


class IContentsPage(Interface):
    """Marker interface which specifies that the current request is showing
    the "folder contents page" of the object.
    """
