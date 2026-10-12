from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IContentish
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility

import json


class QueryStringIndexOptions(BrowserView):
    def __call__(self):
        registry = getUtility(IRegistry)
        reader = getMultiAdapter((registry, self.request), IQuerystringRegistryReader)
        path = str(self.request.form.get("path", "")).strip("/")
        context = self.context.restrictedTraverse(path, None) if path else None
        if not IContentish.providedBy(context):
            context = None
        reader.vocab_context = context or self.context
        config = reader()
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        return json.dumps(config)
