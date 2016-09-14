# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.content.browser.tableview import Table
from plone.app.content.browser.tableview import TableBrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.publisher.browser import BrowserView
import urllib


class FullReviewListView(BrowserView):

    def revlist(self):
        return self.context.my_worklist()

    def url(self):
        return self.context.absolute_url() + '/full_review_list'

    def review_table(self):
        table = ReviewListTable(self.context, self.request)
        return table.render()


class ReviewListTable(object):
    """
    The review list table renders the table and its actions.
    """

    def __init__(self, context, request, **kwargs):
        self.context = context
        self.request = request

        url = self.context.absolute_url()
        view_url = url + '/full_review_list'
        self.table = Table(request, url, view_url, self.items,
                           buttons=self.buttons)

    def render(self):
        return self.table.render()

    @property
    def items(self):
        plone_utils = getToolByName(self.context, 'plone_utils')
        portal_url = getToolByName(self.context, 'portal_url')
        plone_view = getMultiAdapter((self.context, self.request),
                                     name=u'plone')
        plone_layout = getMultiAdapter((self.context, self.request),
                                       name=u'plone_layout')
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        portal_types = getToolByName(self.context, 'portal_types')

        registry = getUtility(IRegistry)
        use_view_action = registry.get(
            'plone.types_use_view_action_in_listings', ())

        browser_default = self.context.browserDefault()

        results = list()
        for i, obj in enumerate(self.context.my_worklist()):
            if i % 2 == 0:
                table_row_class = "even"
            else:
                table_row_class = "odd"

            url = obj.absolute_url()
            path = '/'.join(obj.getPhysicalPath())
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = portal_workflow.getInfoFor(obj, 'review_state', '')

            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = portal_url.getRelativeContentURL(obj)

            type_title_msgid = portal_types[obj.portal_type].Title()
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(obj.Description()))
            getMember = getToolByName(obj, 'portal_membership').getMemberById
            creator_id = obj.Creator()
            creator = getMember(creator_id)            
            if creator:
                creator_name = creator.getProperty('fullname', '') or creator_id
            else:
                creator_name = creator_id
            modified = ''.join(map(safe_unicode, [
                creator_name, ' - ',
                plone_view.toLocalizedTime(obj.ModificationDate(),
                                           long_format=1)]))
            is_structural_folder = obj.restrictedTraverse(
                '@@plone').isStructuralFolder()

            if obj.portal_type in use_view_action:
                view_url = url + '/view'
            elif is_structural_folder:
                view_url = url + "/folder_contents"
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results.append(dict(
                url=url,
                url_href_title=url_href_title,
                id=obj.getId(),
                quoted_id=urllib.quote_plus(obj.getId()),
                path=path,
                title_or_id=obj.pretty_title_or_id(),
                description=obj.Description(),
                obj_type=obj.Type,
                size=obj.getObjSize(),
                modified=modified,
                type_class=type_class,
                wf_state=review_state,
                state_title=portal_workflow.getTitleForStateOnType(
                    review_state, obj.portal_type),
                state_class=state_class,
                is_browser_default=is_browser_default,
                folderish=is_structural_folder,
                relative_url=relative_url,
                view_url=view_url,
                table_row_class=table_row_class,
                is_expired=self.context.isExpired(obj)
            ))
        return results

    @property
    def show_sort_column(self):
        return False

    def buttons(self):
        buttons = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(
            object=aq_inner(self.context), categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if False:  # not len(self.batch):
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


class ReviewListBrowserView(TableBrowserView):
    table = ReviewListTable
