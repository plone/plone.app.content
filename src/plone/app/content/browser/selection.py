import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.selection import DefaultPageSelectionView, DefaultViewSelectionView instead.",
    DefaultViewSelectionView="plone.app.layout.content.browser.selection:DefaultViewSelectionView",
    DefaultPageSelectionView="plone.app.layout.content.browser.selection:DefaultPageSelectionView",
)
