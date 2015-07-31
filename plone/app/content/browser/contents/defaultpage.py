# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.content.browser.contents import ContentsBaseAction


class SetDefaultPageActionView(ContentsBaseAction):
    success_msg = _(u'Default page set successfully')
    failure_msg = _(u'Failed to set default page')

    def __call__(self):
        id = self.request.form.get('id')
        self.errors = []

        if id not in self.context.objectIds():
            self.errors.append(
                _(u'There is no object with short name '
                  u'${name} in this folder.',
                  mapping={u'name': id}))
        else:
            self.context.setDefaultPage(id)
        return self.message()
