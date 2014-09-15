from zope.interface import Interface
from zope import schema


class INameFromTitle(Interface):
    """An object that supports gettings it name from its title.
    """

    title = schema.TextLine(title=u"Title",
                            description=u"A title, which will be converted to "
                                        u"a name",
                            required=True)


class IReindexOnModify(Interface):
    """Marker interface which makes sure an object gets reindexed when
    it's modified.
    """

# XXX: This should be deprecated and removed in Plone 4.


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

class ISiteContentSettings(Interface):
    """ Settings in the registry which determine various admin configurable global behaviour of content items
    """
    file_mimetype_behaviour = schema.Dict(
        title=u"File item behaviour per content type (can use '*')",
        key_type=schema.ASCIILine(title=u"Mimetype"),
        value_type=schema.Choice(
            values=("inline","attachment","view"),
            title=u"Behaviour",
            ),
        default={'application/msword':'inline',
                 'application/x-msexcel':'inline',
                 'application/vnd.ms-excel':'inline',
                 'application/vnd.ms-powerpoint':'inline',
                 'application/pdf':'inline',
                 'application/x-shockwave-flash':'inline',
                 '*':'attachment'}
    )