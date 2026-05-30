import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents import ContentsBaseAction, ContextInfo, FolderContentsView instead.",
    ContentsBaseAction="plone.app.layout.content.browser.contents:ContentsBaseAction",
    FolderContentsView="plone.app.layout.content.browser.contents:FolderContentsView",
    ContextInfo="plone.app.layout.content.browser.contents:ContextInfo",
)
