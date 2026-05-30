import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.query import QueryStringIndexOptions instead.",
    QueryStringIndexOptions="plone.app.layout.content.browser.query:QueryStringIndexOptions",
)
