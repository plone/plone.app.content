import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.browser.selection import DefaultPageSelectionView",
    DefaultPageSelectionView="plone.app.layout:browser.selection.DefaultPageSelectionView",
    DefaultViewSelectionView="plone.app.layout:browser.selection.DefaultViewSelectionView",
)
