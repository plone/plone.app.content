from AccessControl import Unauthorized
from AccessControl.Permissions import delete_objects
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from zope.interface import implements


class DeleteAction(object):
    implements(IStructureAction)

    template = ViewPageTemplateFile('templates/delete.pt')
    order = 4

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        return {
            'title': _('Delete'),
            'id': 'delete',
            'icon': 'trash',
            'context': 'danger',
            'url': self.context.absolute_url() + '/@@fc-delete',
            'form': {
                'title': _('Delete selected items'),
                'submitText': _('Yes'),
                'submitContext': 'danger',
                'template': self.template(),
                'closeText': _('No')
            }
        }


class DeleteActionView(ContentsBaseAction):
    required_obj_permission = delete_objects
    success_msg = _('Successly delete items')
    failure_msg = _('Failed to delete items')

    def action(self, obj):
        parent = obj.aq_inner.aq_parent
        title = self.objectTitle(obj)

        try:
            lock_info = obj.restrictedTraverse('@@plone_lock_info')
        except AttributeError:
            lock_info = None

        if lock_info is not None and lock_info.is_locked():
            self.errors.append(_(u'${title} is locked and cannot be deleted.',
                                 mapping={u'title': title}))
            return
        else:
            try:
                parent.manage_delObjects(obj.getId(), self.request)
            except Unauthorized:
                self.errors.append(
                    _(u'You are not authorized to delete ${title}.',
                        mapping={u'title': self.objectTitle(self.dest)}))