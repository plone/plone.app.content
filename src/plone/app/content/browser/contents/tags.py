import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.tags import TagsAction, TagsActionView instead.",
    TagsAction="plone.app.layout.content.browser.contents.tags:TagsAction",
    TagsActionView="plone.app.layout.content.browser.contents.tags:TagsActionView",
)
