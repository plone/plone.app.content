from Acquisition import Explicit, aq_parent, aq_inner

from zope.component import getMultiAdapter
from zope.interface import implements, providedBy
from zope.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from plone.app.views.interfaces import IFolderContentsView

from Products.ATContentTypes.interface import IATTopic

from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized

from OFS.interfaces import IOrderedContainer

NOT_ADDABLE_TYPES = ('Favorite',)

class FolderContentsView(BrowserView):
    """
    """
    implements(IFolderContentsView)
    
    def test(self, a, b, c):
        """
        """
        if a:
            return b
        return c
        
    def isChecked(self):
        """
        """
        return "checked"
            
    def getAllowedTypes(self):
        """
        """
        # taken from plone_sripts/getAddableTypes 
        types =  self.context.sortObjects(self.context.allowedContentTypes())
        return [ ctype for ctype in types if ctype.getId() not in NOT_ADDABLE_TYPES ]


class FolderContentsViewlet(ViewletBase):
    """    
    """                
    render = ViewPageTemplateFile("foldercontents_viewlet.pt")
    
    def title(self):        
        """
        """
        return "Change me!"
        # view_title and here.utranslate(view_title) or putils.pretty_title_or_id(here)        

    def parent_url(self):
        """
        """
        portal_url = getToolByName(self.context, 'portal_url')
        plone_utils = getToolByName(self.context, 'plone_utils')
        portal_membership = getToolByName(self.context, 'portal_membership')

        obj = self.context

        checkPermission = portal_membership.checkPermission

        # Abort if we are at the root of the portal
        if obj is portal_url.getPortalObject():
            return None

        # Get the parent. If we can't get it (unauthorized), use the portal
        parent = aq_parent(aq_inner(obj))
        
        # # We may get an unauthorized exception if we're not allowed to access#
        # the parent. In this case, return None
        try:
            if getattr(parent, 'getId', None) is None or \
                   parent.getId() == 'talkback':
                # Skip any Z3 views that may be in the acq tree;
                # Skip past the talkback container if that's where we are
                parent = aq_parent(aq_inner(parent))

            if not checkPermission('List folder contents', parent):
                return None
    
            return parent.absolute_url()

        except Unauthorized:
            return None        
            
    def batch(self):
        """
        """
        putils = getToolByName(self.context, 'plone_utils')        
        plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        wtool = getToolByName(self.context, "portal_workflow")
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = self.context.browserDefault()
                
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:     
            contentsMethod = self.context.getFolderContents
        
        contentFilter = self.request.get("contentFilter", None)
        b_size = self.request.get("b_size", 100)

        results = list()        
        for obj in contentsMethod(contentFilter, batch=True, b_size=b_size):
           url = obj.getURL()
           path = obj.getPath or "/".join(obj.getPhysicalPath())           
           icon = plone_view.getIcon(obj);
           type_class = 'contenttype-' + putils.normalizeString(obj.portal_type)
           review_state = obj.review_state or wtool.getInfoFor(obj, 'review_state', '')
           state_class = 'state-' + putils.normalizeString(review_state)
           relative_url = obj.getURL(relative=True)
           obj_type = obj.portal_type
           
           if obj_type in use_view_action:
               view_url = url + '/view'
           elif obj.is_folderish:
               view_url = url + "/folder_contents"              
           else:
               view_url = url
                                
           results.append(dict(
                            url = url,
                            id  = obj.getId,
                            path = path,
                            title_or_id = obj.pretty_title_or_id(),
                            description = obj.Description,
                            obj_type = obj_type,
                            size = obj.getObjSize,
                            modified = obj.ModificationDate,
                            icon = icon.html_tag(),
                            type_class = type_class,
                            wf_state = review_state,
                            state_title = wtool.getTitleForStateOnType(review_state, obj_type),
                            state_class = state_class,
                            is_browser_default = len(browser_default[1]) == 1 and obj.id == browser_default[1][0],
                            folderish = obj.is_folderish,
                            relative_url = relative_url,
                            view_url = view_url,
                            
           ))
        return results

           #hasGetUrl            python:hasattr(item.aq_explicit, 'getURL');
           #item_rel_url         python:hasGetUrl and item.getURL(relative=1) or getRelativeContentURL(item);
        
    def isOrderable(self):
        """
        """        
        return IOrderedContainer.providedBy(self.context)
        
    def test(self, a, b, c):
        """
        """
        if a:
            return b
        return c

    def isEditable(self):        
        """
        """
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return context_state.is_editable()
        
    def portal_url(self):
        """
        """
        utool = getToolByName(self.context, "portal_url")
        return utool.getPortalObject().absolute_url()
        
        
    def portal(self):
        """
        """    
        utool = getToolByName(self.context, "portal_url")
        return utool.getPortalObject()
    