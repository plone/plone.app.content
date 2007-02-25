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

from plone.app.content.browser.tableview import Table
from kss.core import KSSView

import urllib

NOT_ADDABLE_TYPES = ('Favorite',)

class FolderContentsView(BrowserView):
    """
    """
    implements(IFolderContentsView)
    
    def contents_table(self):
        table = FolderContentsTable(self.context, self.request)
        return table.render()

    def title(self):
        """
        """
        return self.context.pretty_title_or_id()

    def icon(self):
        """
        """
        return getattr(self.context, self.context.getIcon(1)).tag(alt = self.context.portal_type)

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


class FolderContentsKSSView(KSSView):
    def update_table(self, pagenumber='1', sort_on='getObjPositionInParent'):
        self.request.set('sort_on', sort_on)
        self.request.set('pagenumber', pagenumber)
        table = FolderContentsTable(self.context, self.request,
                                    contentFilter={'sort_on':sort_on})
        return self.replace_table(table)

    def replace_table(self, table):
        core = self.getCommandSet('core')
        core.replaceInnerHTML('#folderlisting-main-table', table.render())
        return self.render()

class FolderContentsTable(object):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = self.context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    def render(self):
        return self.table.render()

    @property
    def items(self):
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
        
        results = list()
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if i % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + putils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + putils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)
            obj_type = obj.portal_type

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"              
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])
                                 
            results.append(dict(
                url = url,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                description = obj.Description,
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = wtool.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = self.context.isExpired(obj),
            ))
        return results

    @property
    def orderable(self):
        """
        """        
        return IOrderedContainer.providedBy(self.context)

    @property
    def show_sort_column(self):
        return self.orderable and self.editable
        
    @property
    def editable(self):
        """
        """
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.is_editable()

    @property
    def buttons(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        buttons = []
        button_actions = context_state.actions()['folder_buttons']

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if False:#not len(self.batch):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or self.context.cb_dataValid():
                buttons.append(self.setbuttonclass(button))
        return buttons

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button
