# -*- coding: utf-8 -*-
from plone.app.content.browser.contents import ContentsBaseAction
from Products.CMFPlone import PloneMessageFactory as _


class SetDefaultPageActionView(ContentsBaseAction):
    success_msg = _(u'Default page set successfully')
    failure_msg = _(u'Failed to set default page')

    def __call__(self):
        cid = self.request.form.get('id')
        self.errors = []

        if cid not in self.context.objectIds():
            self.errors.append(
                _(u'There is no object with short name '
                  u'${name} in this folder.',
                  mapping={u'name': cid}))
        else:
            self.context.setDefaultPage(cid)
        return self.message()
