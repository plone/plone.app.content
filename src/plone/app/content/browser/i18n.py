import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.i18n import i18njs instead.",
    i18njs="plone.app.layout.content.browser.i18n:i18njs",
)
