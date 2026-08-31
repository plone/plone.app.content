import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.adding import CMFAdding instead.",
    CMFAdding="plone.app.layout.content.browser.adding:CMFAdding",
)
