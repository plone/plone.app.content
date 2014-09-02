import urllib

from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import alsoProvides
from zope.i18n import translate
from zope.publisher.browser import BrowserView

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import pretty_title_or_id, isExpired

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser.interfaces import IContentsPage
from plone.app.content.browser.tableview import Table, TableBrowserView


class FolderContentsView(BrowserView):
    """
    """
    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(FolderContentsView, self).__init__(context, request)
        alsoProvides(request, IContentsPage)

    def __call__(self):
        getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )
        dp_view = getMultiAdapter((
            self.context, self.request), name='default_page')
        default_page = dp_view.getDefaultPage()
        self.default_page_is_folderish = False
        if default_page:
            # We need to check if the folder has a default page set that is
            # also a folder. If it does, give a status message warning that to
            # be able to add items to the default page's folder, they'll need
            # to go to its folder_contents view.
            default_page = self.context.restrictedTraverse(default_page, None)
            if default_page:
                df_context_state = getMultiAdapter(
                    (default_page, self.request),
                    name='plone_context_state')
                if df_context_state.is_folderish():
                    self.default_page_is_folderish = \
                        default_page.absolute_url()
        return super(FolderContentsView, self).__call__()

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
        plone_layout = getMultiAdapter((context, self.request),
                                       name="plone_layout")
        icon = plone_layout.getIcon(context)
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

        # We may get an unauthorized exception if we're not allowed to access
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

    def renderBase(self):
        """Returns the URL used in the base tag.
        """
        # Assume a folderish context
        return self.context.absolute_url() + '/'


class FolderContentsTable(object):
    """
    The foldercontents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter=None):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter is not None and contentFilter or {}
        if 'show_inactive' not in self.contentFilter:
            self.contentFilter['show_inactive'] = True
        self.pagesize = int(self.request.get('pagesize', 20))
        self.items = self.folderitems()
        url = context.absolute_url()
        view_url = url + '/folder_contents'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons,
                           pagesize=self.pagesize)

    def render(self):
        return self.table.render()

    def contentsMethod(self):
        context = aq_inner(self.context)
        if hasattr(context.__class__, 'queryCatalog'):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = context.getFolderContents
        return contentsMethod

    def folderitems(self):
        """
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        plone_layout = getMultiAdapter((context, self.request),
                                       name=u'plone_layout')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties

        use_view_action = site_properties.getProperty(
            'typesUseViewActionInListings', ())
        browser_default = plone_utils.browserDefault(context)

        contentsMethod = self.contentsMethod()

        show_all = self.request.get('show_all', '').lower() == 'true'
        pagesize = self.pagesize
        pagenumber = int(self.request.get('pagenumber', 1))
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            path = obj.getPath or "/".join(obj.getPhysicalPath())

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            # Include brain to make customizations easier (see comment below)
            if not show_all and not start <= i < end:
                results.append(dict(path=path, brain=obj))
                continue

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            icon = plone_layout.getIcon(obj)
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
            modified_sortable = 'sortabledata-' + obj.modified.strftime(
                '%Y-%m-%d-%H-%M-%S')

            if obj.portal_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results.append(dict(
                # provide the brain itself to allow cleaner customisation of
                # the view.
                #
                # this doesn't add any memory overhead, a reference to
                # the brain is already kept through its getPath bound method.
                brain=obj,
                url=url,
                url_href_title=url_href_title,
                id=obj.getId,
                quoted_id=urllib.quote_plus(obj.getId),
                path=path,
                title_or_id=safe_unicode(pretty_title_or_id(
                    plone_utils, obj)),
                obj_type=obj.Type,
                size=obj.getObjSize,
                modified=modified,
                modified_sortable=modified_sortable,
                icon=icon.html_tag(),
                type_class=type_class,
                wf_state=review_state,
                state_title=portal_workflow.getTitleForStateOnType(
                    review_state, obj.portal_type),
                state_class=state_class,
                is_browser_default=is_browser_default,
                folderish=obj.is_folderish,
                relative_url=relative_url,
                view_url=view_url,
                table_row_class=table_row_class,
                is_expired=isExpired(obj)
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
        button_actions = portal_actions.listActionInfos(
            object=aq_inner(self.context), categories=('folder_buttons', ))

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


class FolderContentsBrowserView(TableBrowserView):
    table = FolderContentsTable
