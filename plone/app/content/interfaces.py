# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface


class INameFromTitle(Interface):
    """An object that supports gettings it name from its title.
    """

    title = schema.TextLine(
        title=u"Title",
        description=u"A title, which will be converted to a name",
        required=True
    )


class IReindexOnModify(Interface):
    """Marker interface which makes sure an object gets reindexed when
    it's modified.
    """
