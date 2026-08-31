import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.defaultpage import SetDefaultPageActionView instead.",
    SetDefaultPageActionView="plone.app.layout.content.browser.contents.defaultpage:SetDefaultPageActionView",
)
