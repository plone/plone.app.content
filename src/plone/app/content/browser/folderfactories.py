import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.folderfactories import FolderFactoriesView instead.",
    _allowedTypes="plone.app.layout.content.browser.folderfactories:_allowedTypes",
    FolderFactoriesView="plone.app.layout.content.browser.folderfactories:FolderFactoriesView",
)
