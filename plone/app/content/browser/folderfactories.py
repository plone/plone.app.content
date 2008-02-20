from urllib import quote_plus

from zope.component import getMultiAdapter, queryMultiAdapter, getAdapters, queryUtility

from zope.component.interfaces import IFactory
from zope.i18n import translate
from zope.app.container.constraints import checkFactory
from zope.app.publisher.interfaces.browser import AddMenu

from Acquisition import aq_inner
from Products.Five.browser import BrowserView

from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone import PloneMessageFactory as _

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.memoize.instance import memoize
from plone.memoize.request import memoize_diy_request

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
        
        portal_state = getMultiAdapter((context, request), name='plone_portal_state')
        portal_url = portal_state.portal_url()
        
        addContext = self.add_context()
        baseUrl = addContext.absolute_url()
        
        allowedTypes = _allowedTypes(request, addContext)
        
        # XXX: This is calling a pyscript (which we encourage people to customise TTW)
        exclude = addContext.getNotAddableTypes()

        # If there is an add view available, use that instead of createObject
        # Note: that this depends on the convention that the add view and the
        # factory have the same name, and it still only applies where there
        # is an FTI in portal_types to begin with. Alas, FTI-less content
        # is pretty much a no-go in CMF.
        addingview = queryMultiAdapter((addContext, request), name='+')
        idnormalizer = queryUtility(IIDNormalizer)
        for t in allowedTypes:
            typeId = t.getId()
            if typeId not in exclude and (include is None or typeId in include):
                cssId = idnormalizer.normalize(typeId)
                cssClass = 'contenttype-%s' % cssId
                factory = t.factory
                if addingview is not None and \
                   queryMultiAdapter((addingview, self.request), name=factory) is not None:
                    url = '%s/+/%s' % (baseUrl, factory,)
                else:
                    url = '%s/createObject?type_name=%s' % (baseUrl, quote_plus(typeId),)
                icon = t.getIcon()
                if icon:
                    icon = '%s/%s' % (portal_url, icon)

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
