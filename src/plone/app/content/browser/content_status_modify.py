import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.content_status_modify import ContentStatusModifyView instead.",
    ContentStatusModifyView="plone.app.layout.content.browser.content_status_modify:ContentStatusModifyView",
)
