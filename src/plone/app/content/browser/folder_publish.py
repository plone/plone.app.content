import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.folder_publish import FolderPublishView instead.",
    FolderPublishView="plone.app.layout.content.browser.folder_publish:FolderPublishView",
)
