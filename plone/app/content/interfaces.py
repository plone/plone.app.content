from zope.interface import Interface
from zope import schema

class INameFromTitle(Interface):
    """An object that supports gettings it name from its title.
    """
    
    title = schema.TextLine(title=u"Title",
                            description=u"A title, which will be converted to a name",
                            required=True)