import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.content_status_history import ContentStatusHistoryDatesForm, ContentStatusHistoryView, IContentStatusHistoryDates instead.",
    IContentStatusHistoryDates="plone.app.layout.content.browser.content_status_history:IContentStatusHistoryDates",
    ContentStatusHistoryDatesForm="plone.app.layout.content.browser.content_status_history:ContentStatusHistoryDatesForm",
    ContentStatusHistoryView="plone.app.layout.content.browser.content_status_history:ContentStatusHistoryView",
)
