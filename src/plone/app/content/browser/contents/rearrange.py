import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.rearrange import ItemOrderActionView, OrderContentsBaseAction, RearrangeActionView instead.",
    OrderContentsBaseAction="plone.app.layout.content.browser.contents.rearrange:OrderContentsBaseAction",
    ItemOrderActionView="plone.app.layout.content.browser.contents.rearrange:ItemOrderActionView",
    RearrangeActionView="plone.app.layout.content.browser.contents.rearrange:RearrangeActionView",
)
