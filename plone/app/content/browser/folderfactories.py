from urllib import quote_plus

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.memoize.request import memoize_diy_request
from zope.component import getMultiAdapter, queryUtility
from zope.i18n import translate
from zope.publisher.browser import BrowserView

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes


@memoize_diy_request(arg=0)
def _allowedTypes(request, context):
    return context.allowedContentTypes()


class FolderFactoriesView(BrowserView):
    """The folder_factories view - show addable types
    """

    def __call__(self):
        if 'form.button.Add' in self.request.form:
            url = self.request.form.get('url')
            self.request.response.redirect(url)
            return ''
        else:
            return self.index()

    def can_constrain_types(self):
        constrain_types = ISelectableConstrainTypes(self.add_context(), None)
        return constrain_types is not None and constrain_types.canConstrainTypes()

    @memoize
    def add_context(self):
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        return context_state.folder()

    # NOTE: This is also used by plone.app.contentmenu.menu.FactoriesMenu.
    # The return value is somewhat dictated by the menu infrastructure, so
    # be careful if you change it

    def addable_types(self, include=None):
        """Return menu item entries in a TAL-friendly form.

        Pass a list of type ids to 'include' to explicitly allow a list of
        types.
        """

        context = aq_inner(self.context)
        request = self.request

        results = []

        idnormalizer = queryUtility(IIDNormalizer)
        portal_state = getMultiAdapter((context, request), name='plone_portal_state')
        portal_url = portal_state.portal_url()

        addContext = self.add_context()
        baseUrl = addContext.absolute_url()

        allowedTypes = _allowedTypes(request, addContext)

        types_tool = getToolByName(context, 'portal_types')

        # Note: we don't check 'allowed' or 'available' here, because these are
        # slow. We assume the 'allowedTypes' list has already performed the
        # necessary calculations
        actions = types_tool.listActionInfos(
            object=context,
            check_permissions=False,
            check_condition=False,
            category='folder/add',
        )
        addActionsById = dict([(a['id'], a) for a in actions])

        expr_context = createExprContext(
            aq_parent(context), portal_state.portal(), context)
        for t in allowedTypes:
            typeId = t.getId()
            if include is None or typeId in include:
                cssId = idnormalizer.normalize(typeId)
                cssClass = 'contenttype-%s' % cssId

                url = None
                addAction = addActionsById.get(typeId, None)
                if addAction is not None:
                    url = addAction['url']

                if not url:
                    url = '%s/createObject?type_name=%s' % (baseUrl, quote_plus(typeId),)

                icon = t.getIconExprObject()
                if icon:
                    icon = icon(expr_context)

                results.append({ 'id'           : typeId,
                                 'title'        : t.Title(),
                                 'description'  : t.Description(),
                                 'action'       : url,
                                 'selected'     : False,
                                 'icon'         : icon,
                                 'extra'        : {'id' : cssId, 'separator' : None, 'class' : cssClass},
                                 'submenu'      : None,
                                })

        # Sort the addable content types based on their translated title
        results = [(translate(ctype['title'], context=request), ctype) for ctype in results]
        results.sort()
        results = [ctype[-1] for ctype in results]

        return results
