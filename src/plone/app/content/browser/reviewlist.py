import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.reviewlist import FullReviewListView, ReviewListBrowserView, ReviewListTable instead.",
    FullReviewListView="plone.app.layout.content.browser.reviewlist:FullReviewListView",
    ReviewListTable="plone.app.layout.content.browser.reviewlist:ReviewListTable",
    ReviewListBrowserView="plone.app.layout.content.browser.reviewlist:ReviewListBrowserView",
)
