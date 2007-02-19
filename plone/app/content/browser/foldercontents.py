from Acquisition import Explicit, aq_parent, aq_inner

from zope.component import getMultiAdapter
from zope.interface import implements, providedBy
from zope.app.pagetemplate import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView

from Products.ATContentTypes.interface import IATTopic

from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized

from OFS.interfaces import IOrderedContainer

import urllib

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

    def contents_table(self):
        table = FolderContentsTable(self.context, self.request)
        return table.render()


from kss.core import KSSView

class FolderContentsKSSView(KSSView):
    def selectall(self):
        table = FolderContentsTable(self.context, self.request)
        table.selectcurrentbatch=True
        return self.replaceTable(table)

    def sort_on(self, sort_on):
        table = FolderContentsTable(self.context, self.request, contentFilter={'sort_on':sort_on})
        table.selectcurrentbatch=True
        return self.replaceTable(table)

    def replaceTable(self, table):
        core = self.getCommandSet('core')
        core.replaceInnerHTML('#folderlisting-main-viewlet', table.render())
        return self.render()

class FolderContentsTable(object):
    """    
    """                
    # options
    selectcurrentbatch = False

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        requestContentFilter = self.request.get("contentFilter", {})
        requestContentFilter.update(contentFilter)
        self.contentFilter = requestContentFilter

    render = ViewPageTemplateFile("foldercontents_viewlet.pt")
    
    def title(self):
        """
        """
        return "Change me!"
        # view_title and here.utranslate(view_title) or putils.pretty_title_or_id(here)        

    def folder_buttons(self):
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        buttons = []
        button_actions = context_state.actions()['folder_buttons']

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if self.batch and not self.context.cb_dataValid():
            return buttons
        elif not self.batch:
            return button_actions['paste']

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] == 'paste':
                button['cssclass'] = 'standalone'
            else:
                button['cssclass'] = 'context'

            if button['id'] != 'paste' or self.context.cb_dataValid():
                buttons.append(button)
        return buttons


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
            
    @property
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
        
        b_size = self.request.get("b_size", 100)

        selected = self.selectcurrentbatch

        results = list()        
        for obj in contentsMethod(self.contentFilter, batch=True, b_size=b_size):
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
               checked = selected and 'checked' or None,
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
    
