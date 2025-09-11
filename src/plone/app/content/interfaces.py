from plone.base.interfaces import INameFromTitle as FutureINameFromTitle
from zope.interface import Attribute
from zope.interface import Interface


class INameFromTitle(FutureINameFromTitle):
    """An object that supports getting its name (id) from its title.

    This interface has been moved to plone.base.interfaces.
    This alias will be removed in Plone 7.0.
    We tried deprecating it like this:

        zope.deferredimport.deprecated(
            INameFromTitle="plone.base.interfaces:INameFromTitle",
        )

    Unfortunately this does not completely work: if your site has a content
    type with behavior `plone.app.content.interfaces.INameFromTitle` this would
    no longer work because the behavior is not found.
    If you use `plone.namefromtitle` then it works.

    So as long as we want to support the old spelling, we must keep the
    interface here, and also use this interface as the `provides` in the
    definition of the behavior in `plone.app.dexterity`.

    See https://github.com/plone/plone.app.dexterity/pull/379
    """


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
