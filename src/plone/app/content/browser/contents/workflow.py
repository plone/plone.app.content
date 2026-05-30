import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.contents.workflow import WorkflowAction, WorkflowActionView instead.",
    WorkflowAction="plone.app.layout.content.browser.contents.workflow:WorkflowAction",
    WorkflowActionView="plone.app.layout.content.browser.contents.workflow:WorkflowActionView",
)
