from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from plone.base import PloneMessageFactory as _
from plone.base.defaultpage import check_default_page_via_view
from Products.CMFCore.interfaces._content import IFolderish
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer


@implementer(IStructureAction)
class TagsAction:
    template = ViewPageTemplateFile("templates/tags.pt")
    order = 6

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        base_vocabulary = "%s/@@getVocabulary?name=" % getSite().absolute_url()
        return {
            "tooltip": translate(_("Tags"), context=self.request),
            "id": "tags",
            "icon": "tags",
            "url": self.context.absolute_url() + "/@@fc-tags",
            "form": {
                "title": translate(_("Tags"), context=self.request),
                "template": self.template(
                    vocabulary_url="%splone.app.vocabularies.Keywords"
                    % (base_vocabulary)
                ),
            },
        }


class TagsActionView(ContentsBaseAction):
    required_obj_permission = "Modify portal content"
    success_msg = _("Successfully updated tags on items")
    failure_msg = _("Failed to modify tags on items")

    def __call__(self):
        self.tags_add = [
            tag for tag in self.request.form.get("toadd", "").split(",") if tag
        ]
        self.tags_remove = [
            tag for tag in self.request.form.get("toremove", "").split(",") if tag
        ]

        self.recurse = self.request.form.get("recurse", "no") == "yes"
        return super().__call__()

    def action(self, obj, bypass_recurse=False):
        if check_default_page_via_view(obj, self.request):
            self.action(obj.aq_parent, bypass_recurse=True)
        recurse = self.recurse and not bypass_recurse
        if recurse and IFolderish.providedBy(obj):
            for sub in obj.values():
                self.action(sub)

        tags = set(obj.Subject())
        if self.tags_remove:
            tags = tags - set(self.tags_remove)
        if self.tags_add:
            tags = tags | set(self.tags_add)
        if self.tags_remove or self.tags_add:
            obj.setSubject(list(tags))
            obj.reindexObject(idxs=["Subject"])
