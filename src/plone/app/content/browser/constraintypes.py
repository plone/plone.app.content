import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.constraintypes import ConstrainsFormView, FormContentAdapter, IConstrainForm, ValidTypes, ValidTypesFactory instead.",
    ACQUIRE="plone.app.layout.content.browser.constraintypes:ACQUIRE",
    DISABLED="plone.app.layout.content.browser.constraintypes:DISABLED",
    ENABLED="plone.app.layout.content.browser.constraintypes:ENABLED",
    ST="plone.app.layout.content.browser.constraintypes:ST",
    possible_constrain_types="plone.app.layout.content.browser.constraintypes:possible_constrain_types",
    ValidTypes="plone.app.layout.content.browser.constraintypes:ValidTypes",
    ValidTypesFactory="plone.app.layout.content.browser.constraintypes:ValidTypesFactory",
    IConstrainForm="plone.app.layout.content.browser.constraintypes:IConstrainForm",
    FormContentAdapter="plone.app.layout.content.browser.constraintypes:FormContentAdapter",
    ConstrainsFormView="plone.app.layout.content.browser.constraintypes:ConstrainsFormView",
)
