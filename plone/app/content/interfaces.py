from zope.interface import Interface
from zope import schema

class INameFromTitle(Interface):
    """An object that supports gettings it name from its title.
    """
    
    title = schema.TextLine(title=u"Title",
                            description=u"A title, which will be converted to a name",
                            required=True)

class IReindexOnModify(Interface):
    """Marker interface which makes sure an object gets reindexed when
    it's modified.
    """

class IBatch(Interface):
    """A batch splits up a large number of items over multiple pages"""

    size = schema.Int(title=u"The amount of items in the batch")

    firstpage = schema.Int(title=u"The number of the first page (always 1)")

    lastpage = schema.Int(title=u"The number of the last page")

    items_not_on_page = schema.List(
        title=u"All items that are in the batch but not on the current page")

    multiple_pages = schema.Bool(
        title=u"Boolean indicating wheter there are multiple pages or not")

    has_next = schema.Bool(
        title=u"Indicator for wheter there is a page after the current one")

    has_previous = schema.Bool(
        title=u"Indicator for wheter there is a page after the current one")

    previouspage = schema.Int(title=u"The number of the previous page")

    nextpage = schema.Int(title=u"The number of the nextpage page")

    next_item_count = schema.Int(title=u"The number of items on the next page")

    navlist = schema.List(
        title=u"List of page numbers to be used as a navigation list")

    show_link_to_first = schema.Bool(
        title=u"First page not in the navigation list")

    show_link_to_last = schema.Bool(
        title=u"Last page not in the navigation list")

    second_page_not_in_navlist = schema.Bool(
        title=u"Second page not in the navigation list")

    before_last_page_not_in_navlist = schema.Bool(
        title=u"Before last page not in the navigation list")

    islastpage = schema.Bool(
        title=u"Boolean indicating wheter the current page is the last page")

    previous_pages = schema.List(
        title=u"All previous pages that are in the navlist")

    next_pages = schema.List(
        title=u"All previous pages that are in the navlist")

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
