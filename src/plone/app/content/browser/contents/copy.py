import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.copy import CopyAction, CopyActionView instead.",
    CopyAction="plone.app.layout.content.browser.contents.copy:CopyAction",
    CopyActionView="plone.app.layout.content.browser.contents.copy:CopyActionView",
)
