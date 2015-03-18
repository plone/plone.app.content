import json
from plone.registry.interfaces import IRegistry
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from zope.component import getUtility
from Products.Five import BrowserView


class QueryStringIndexOptions(BrowserView):

    def __call__(self):
        registry = getUtility(IRegistry)
        config = IQuerystringRegistryReader(registry)()
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(config)
