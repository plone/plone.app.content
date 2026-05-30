import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.interfaces import IFolderContentsView instead.",
    IFolderContentsView="plone.app.layout.content.browser.interfaces:IFolderContentsView",
)
