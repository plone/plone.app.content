# -*- coding: utf-8 -*-
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import get_top_site_from_url
from zope.i18n import translate
from zope.interface import implementer


@implementer(IStructureAction)
class CopyAction(object):

    order = 2

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        site = get_top_site_from_url(self.context, self.request)
        base_url = site.absolute_url()
        return {
            'tooltip': translate(_('Copy'), context=self.request),
            'id': 'copy',
            'icon': 'duplicate',
            'url': '%s{path}/@@fc-copy' % base_url,
        }


class CopyActionView(ContentsBaseAction):
    success_msg = _('Successfully copied items')
    failure_msg = _('Failed to copy items')

    def action(self, obj):
        self.oblist.append(obj)

    def finish(self):
        oblist = []
        for ob in self.oblist:
            if not ob.cb_isCopyable():
                self.errors.append(_(u'${title} cannot be copied.',
                                     mapping={u'title': self.objectTitle(ob)}))
                continue
            m = Moniker(ob)
            oblist.append(m.dump())
        cp = (0, oblist)
        cp = _cb_encode(cp)
        resp = self.request.response
        resp.setCookie('__cp', cp, path='%s' % cookie_path(self.request))
        self.request['__cp'] = cp

    def __call__(self):
        self.oblist = []
        return super(CopyActionView, self).__call__(keep_selection_order=True)
