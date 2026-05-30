import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.file import AllowUploadView, FileUploadView instead.",
    possible_tus_options="plone.app.layout.content.browser.file:possible_tus_options",
    TUS_ENABLED="plone.app.layout.content.browser.file:TUS_ENABLED",
    FileUploadView="plone.app.layout.content.browser.file:FileUploadView",
    AllowUploadView="plone.app.layout.content.browser.file:AllowUploadView",
)
