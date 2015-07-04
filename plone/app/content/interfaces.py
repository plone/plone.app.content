# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface, Attribute


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


class IStructureAction(Interface):
    order = Attribute("Order the action should be listed")

    def get_options():
        """
        Return a dict of action widget options.

        Options: {
            'title': 'Button title', // required
            'name': 'short name', // required
            'formTemplate': None, // If action requires form to submit additional options
            'icon': None, // icon name
            'button-type': 'danger', //
        }
        """
