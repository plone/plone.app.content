import urllib

from plone.memoize import instance
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import alsoProvides
from zope.i18n import translate
from zope.publisher.browser import BrowserView

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import pretty_title_or_id, isExpired

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser.interfaces import IContentsPage
from plone.app.content.browser.tableview import Table, TableKSSView


class FolderContentsView(BrowserView):
    """
    """
    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(FolderContentsView, self).__init__(context, request)
        alsoProvides(request, IContentsPage)

    def contents_table(self):
        table = FolderContentsTable(aq_inner(self.context), self.request)
        return table.render()

    def title(self):
        """
        """
        return pretty_title_or_id(context=self.context, obj=self.context)

    def icon(self):
        """
        """
        context = aq_inner(self.context)
        ploneview = getMultiAdapter((context, self.request), name="plone")
        icon = ploneview.getIcon(context)
        return icon.html_tag()

    def parent_url(self):
        """
        """
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')

        obj = context

        checkPermission = portal_membership.checkPermission

        # Abort if we are at the root of the portal
        if IPloneSiteRoot.providedBy(context):
            return None
        

        # Get the parent. If we can't get it (unauthorized), use the portal
        parent = aq_parent(obj)
        
        # # We may get an unauthorized exception if we're not allowed to access#
        # the parent. In this case, return None
        try:
            if getattr(parent, 'getId', None) is None or \
                   parent.getId() == 'talkback':
                # Skip any Z3 views that may be in the acq tree;
                # Skip past the talkback container if that's where we are
                parent = aq_parent(parent)

            if not checkPermission('List folder contents', parent):
                return None

            return parent.absolute_url()

        except Unauthorized:
            return None

class FolderContentsTable(object):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    def render(self):
        return self.table.render()

    def contentsMethod(self):
        context = aq_inner(self.context)
        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = context.getFolderContents
        return contentsMethod

    @property
    @instance.memoize
    def items(self):
        """
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = plone_utils.browserDefault(context)

        contentsMethod = self.contentsMethod()

        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)

            fti = portal_types.get(obj.portal_type)
            if fti is not None:
                type_title_msgid = fti.Title()
            else:
                type_title_msgid = obj.portal_type
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(obj.Description))

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)

            obj_type = obj.Type
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
                url_href_title = url_href_title,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = safe_unicode(pretty_title_or_id(plone_utils, obj)),
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = isExpired(obj),
            ))
        return results

    @property
    def orderable(self):
        """
        """
        return IOrderedContainer.providedBy(aq_inner(self.context))

    @property
    def show_sort_column(self):
        return self.orderable and self.editable
        
    @property
    def editable(self):
        """
        """
        context_state = getMultiAdapter((aq_inner(self.context), self.request),
                                        name=u'plone_context_state')
        return context_state.is_editable()

    @property
    def buttons(self):
        buttons = []
        context = aq_inner(self.context)
        portal_actions = getToolByName(context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=aq_inner(self.context), categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.items):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or context.cb_dataValid():
                buttons.append(self.setbuttonclass(button))
        return buttons

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button

class FolderContentsKSSView(TableKSSView):
    table = FolderContentsTable

