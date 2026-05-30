import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.actions import DeleteConfirmationForm, IRenameForm, LockingBase, ObjectCopyView, ObjectCutView, ObjectDeleteView, ObjectPasteView, RenameForm, valid_id instead.",
    LockingBase="plone.app.layout.content.browser.actions:LockingBase",
    DeleteConfirmationForm="plone.app.layout.content.browser.actions:DeleteConfirmationForm",
    valid_id="plone.app.layout.content.browser.actions:valid_id",
    IRenameForm="plone.app.layout.content.browser.actions:IRenameForm",
    default_new_id="plone.app.layout.content.browser.actions:default_new_id",
    default_new_title="plone.app.layout.content.browser.actions:default_new_title",
    RenameForm="plone.app.layout.content.browser.actions:RenameForm",
    ObjectCutView="plone.app.layout.content.browser.actions:ObjectCutView",
    ObjectCopyView="plone.app.layout.content.browser.actions:ObjectCopyView",
    ObjectDeleteView="plone.app.layout.content.browser.actions:ObjectDeleteView",
    ObjectPasteView="plone.app.layout.content.browser.actions:ObjectPasteView",
)
