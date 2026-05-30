import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.delete import DeleteAction, DeleteActionView instead.",
    DeleteAction="plone.app.layout.content.browser.contents.delete:DeleteAction",
    DeleteActionView="plone.app.layout.content.browser.contents.delete:DeleteActionView",
)
