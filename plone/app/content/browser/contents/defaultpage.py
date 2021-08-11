from Products.CMFPlone import PloneMessageFactory as _

from plone.app.content.browser.contents import ContentsBaseAction


class SetDefaultPageActionView(ContentsBaseAction):
    success_msg = _("Default page set successfully")
    failure_msg = _("Failed to set default page")

    def __call__(self):
        cid = self.request.form.get("id")
        self.errors = []

        if cid not in self.context.objectIds():
            self.errors.append(
                _(
                    "There is no object with short name " "${name} in this folder.",
                    mapping={"name": cid},
                )
            )
        else:
            self.context.setDefaultPage(cid)
        return self.message()
