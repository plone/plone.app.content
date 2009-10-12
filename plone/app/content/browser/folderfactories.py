from urllib import quote_plus

from zope.component import getMultiAdapter, queryUtility

from zope.i18n import translate

from Acquisition import aq_inner
from Products.Five.browser import BrowserView

from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

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
        
        context_state = getMultiAdapter((context, request), name='plone_context_state')
        
        # Note: we don't check 'allowed' or 'available' here, because these are slow.
        # We assume the 'allowedTypes' list has already performed the necessary 
        # calculations
        addActionsById = dict([(a['id'], a) for a in context_state.actions().get('folder/add', [])])
        
        # If there is an add view available, use that instead of createObject
        idnormalizer = queryUtility(IIDNormalizer)
        
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
