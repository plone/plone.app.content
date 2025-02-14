from plone.memoize.request import memoize_diy_request

import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.browser.folderfactories import FolderFactoriesView",
    FolderFactoriesView="plone.app.layout:browser.folderfactories.FolderFactoriesView",
)


@memoize_diy_request(arg=0)
def _allowedTypes(request, context):
    return context.allowedContentTypes()
