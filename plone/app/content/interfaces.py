from zope.interface import Attribute
from zope.interface import Interface

import zope.deferredimport


zope.deferredimport.deprecated(
    "It has been moved to plone.base.interfaces. "
    "This alias will be removed in Plone 7.0",
    INameFromTitle="plone.base.interfaces:INameFromTitle",
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
