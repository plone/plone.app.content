from zope.interface import Interface
from zope import schema

class INameFromTitle(Interface):
    """An object that supports gettings it name from its title.
    """
    
    title = schema.TextLine(title=u"Title",
                            description=u"A title, which will be converted to a name",
                            required=True)

class IBatch(Interface):
    """A batch splits up a large number of items over multiple pages"""

class IIndexableObjectWrapper(Interface):
    """An adapter of a (object, portal) where object is to be indexed in 
    portal_catalog.
    
    This should implement __getattr__(), which in turn should react
    when the catalog tries to get attributes to index.
    
    The update() method must be called before the catalog is given the
    wrapper.
    """
    
    def update(vars, **kwargs):
        """Update the wrapper with variables from e.g. the workflow
        tool.
        """