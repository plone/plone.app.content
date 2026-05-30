import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.paste import PasteAction, PasteActionView instead.",
    PasteAction="plone.app.layout.content.browser.contents.paste:PasteAction",
    PasteActionView="plone.app.layout.content.browser.contents.paste:PasteActionView",
)
