# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
from zope.i18n import translate
from zope.interface import implementer


@implementer(IStructureAction)
class PasteAction(object):

    order = 3

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        return {
            'title': translate(_('Paste'), context=self.request),
            'id': 'paste',
            'icon': 'paste',
            'url': self.context.absolute_url() + '/@@fc-paste'
        }


class PasteActionView(ContentsBaseAction):
    required_obj_permission = 'Copy or Move'
    success_msg = _('Successfully pasted items')
    failure_msg = _('Failed to paste items')

    def __call__(self):
        self.protect()
        self.errors = []

        self.dest = self.site.restrictedTraverse(
            str(self.request.form['folder'].lstrip('/')))

        try:
            self.dest.manage_pasteObjects(self.request['__cp'])
        except ConflictError:
            raise
        except Unauthorized:
            # avoid this unfriendly exception text:
            # "You are not allowed to access 'manage_pasteObjects' in this
            # context"
            self.errors.append(
                _(u'You are not authorized to paste ${title} here.',
                    mapping={u'title': self.objectTitle(self.dest)}))
        except ValueError as e:
            if 'Disallowed subobject type: ' in e.message:
                msg_parts = e.message.split(':')
                self.errors.append(
                    _(u'Disallowed subobject type "${type}"',
                        mapping={u'type': msg_parts[1].strip()}))
            else:
                raise e

        return self.message()
