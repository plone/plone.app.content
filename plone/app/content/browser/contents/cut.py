# -*- coding: utf-8 -*-
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from Products.CMFPlone import PloneMessageFactory as _
from zope.i18n import translate
from zope.interface import implementer


@implementer(IStructureAction)
class CutAction(object):

    order = 1

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        return {
            'tooltip': translate(_('Cut'), context=self.request),
            'id': 'cut',
            'icon': 'scissors',
            'url': self.context.absolute_url() + '/@@fc-cut'
        }


class CutActionView(ContentsBaseAction):
    success_msg = _('Successfully cut items')
    failure_msg = _('Failed to cut items')

    def action(self, obj):
        self.oblist.append(obj)

    def finish(self):
        oblist = []
        for ob in self.oblist:
            if ob.wl_isLocked():
                self.errors.append(_(u'${title} is being edited and cannot be cut.',
                                     mapping={u'title': self.objectTitle(ob)}))
                continue
            if not ob.cb_isMoveable():
                self.errors.append(_(u'${title} is being edited and cannot be cut.',
                                     mapping={u'title': self.objectTitle(ob)}))
                continue
            m = Moniker(ob)
            oblist.append(m.dump())
        cp = (1, oblist)
        cp = _cb_encode(cp)
        resp = self.request.response
        resp.setCookie('__cp', cp, path='%s' % cookie_path(self.request))
        self.request['__cp'] = cp

    def __call__(self):
        self.oblist = []
        return super(CutActionView, self).__call__()
