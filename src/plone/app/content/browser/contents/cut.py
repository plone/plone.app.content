import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.cut import CutAction, CutActionView instead.",
    CutAction="plone.app.layout.content.browser.contents.cut:CutAction",
    CutActionView="plone.app.layout.content.browser.contents.cut:CutActionView",
)
