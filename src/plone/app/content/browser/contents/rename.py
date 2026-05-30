import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.rename import RenameAction, RenameActionView instead.",
    RenameAction="plone.app.layout.content.browser.contents.rename:RenameAction",
    RenameActionView="plone.app.layout.content.browser.contents.rename:RenameActionView",
)
