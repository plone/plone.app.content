import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.tableview import Table, TableBatchView, TableBrowserView instead.",
    TableBatchView="plone.app.layout.content.browser.tableview:TableBatchView",
    Table="plone.app.layout.content.browser.tableview:Table",
    TableBrowserView="plone.app.layout.content.browser.tableview:TableBrowserView",
)
