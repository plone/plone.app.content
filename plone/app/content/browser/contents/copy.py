from OFS.CopySupport import CopyError
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.CopySupport import eNotSupported
from OFS.Moniker import Moniker
from Products.CMFPlone import PloneMessageFactory as _
from cgi import escape
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from zope.interface import implements


class CopyAction(object):
    implements(IStructureAction)

    order = 2

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        return {
            'title': _('Copy'),
            'id': 'copy',
            'icon': 'copy',
            'url': self.context.absolute_url() + '/@@fc-copy'
        }


class CopyActionView(ContentsBaseAction):
    success_msg = _('Successly copied items')
    failure_msg = _('Failed to copy items')

    def action(self, obj):
        self.oblist.append(obj)

    def finish(self):
        oblist = []
        for ob in self.oblist:
            if not ob.cb_isCopyable():
                raise CopyError(eNotSupported % escape(id))
            m = Moniker(ob)
            oblist.append(m.dump())
        cp = (0, oblist)
        cp = _cb_encode(cp)
        resp = self.request.response
        resp.setCookie('__cp', cp, path='%s' % cookie_path(self.request))
        self.request['__cp'] = cp

    def __call__(self):
        self.oblist = []
        return super(CopyActionView, self).__call__()