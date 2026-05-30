import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.properties import PropertiesAction, PropertiesActionView instead.",
    PropertiesAction="plone.app.layout.content.browser.contents.properties:PropertiesAction",
    PropertiesActionView="plone.app.layout.content.browser.contents.properties:PropertiesActionView",
)
