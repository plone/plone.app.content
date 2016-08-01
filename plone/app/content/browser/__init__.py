# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
import json


class AllowedTypesInContext(BrowserView):

    def __call__(self):
        """Return JSON structure with all allowed content type ids from the
        current container.
        """

        self.request.response.setHeader(
            'Content-Type', 'application/json; charset=utf-8'
        )
        allowed_types = [t.getId() for t in self.context.allowedContentTypes()]
        return json.dumps({'allowed_types': allowed_types})
