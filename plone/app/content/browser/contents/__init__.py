# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from plone.app.content.browser.file import TUS_ENABLED
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.interfaces import IStructureAction
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from plone.protect.postonly import check as checkpost
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer

import zope.deferredimport

zope.deferredimport.deprecated(
    # remove in Plone 5.1
    'Import from plone.app.content.browser.content.defaultpage instead',
    DefaultPage='plone.app.content.browser.content.defaultpage:SetDefaultPageActionView',  # noqa
)
zope.deferredimport.deprecated(
    # remove in Plone 5.1
    'Import from plone.app.content.browser.content.rearrange instead',
    ItemOrder='plone.app.content.browser.content.rearrange:ItemOrderActionView',  # noqa
    Rearrange='plone.app.content.browser.content.rearrange:RearrangeOrderActionView',  # noqa
)


class ContentsBaseAction(BrowserView):

    success_msg = _('Success')
    failure_msg = _('Failure')
    required_obj_permission = None

    def objectTitle(self, obj):
        context = aq_inner(obj)
        title = utils.pretty_title_or_id(context, context)
        return utils.safe_unicode(title)

    def protect(self):
        authenticator = getMultiAdapter((self.context, self.request),
                                        name='authenticator')
        if not authenticator.verify():
            raise Unauthorized
        checkpost(self.request)

    def json(self, data):
        self.request.response.setHeader("Content-Type", "application/json")
        return json_dumps(data)

    def get_selection(self):
        selection = self.request.form.get('selection', '[]')
        return json_loads(selection)

    def action(self, obj):
        """
        fill in this method to do action against each item in the selection
        """
        pass

    def finish(self):
        pass

    def __call__(self):
        self.protect()
        self.errors = []
        site = getSite()
        context = aq_inner(self.context)
        selection = self.get_selection()

        self.dest = site.restrictedTraverse(
            str(self.request.form['folder'].lstrip('/')))

        self.catalog = getToolByName(context, 'portal_catalog')
        self.mtool = getToolByName(self.context, 'portal_membership')

        for brain in self.catalog(UID=selection):
            # remove everyone so we know if we missed any
            selection.remove(brain.UID)
            obj = brain.getObject()
            if (
                self.required_obj_permission
                and not self.mtool.checkPermission(
                    self.required_obj_permission,
                    obj
                )
            ):
                self.errors.append(_(
                    'Permission denied for "${title}"',
                    mapping={'title': self.objectTitle(obj)}
                ))
                continue
            self.action(obj)

        self.finish()
        return self.message(selection)

    def message(self, missing=[]):
        if len(missing) > 0:
            self.errors.append(_(
                '${items} could not be found',
                mapping={'items': str(len(missing))}
            ))
        if self.errors:
            msg = self.failure_msg
        else:
            msg = self.success_msg

        translated_msg = translate(msg, context=self.request)
        if self.errors:
            translated_errors = [
                translate(error, context=self.request) for error in self.errors
            ]
            translated_msg = u'{0:s}: {1:s}'.format(
                translated_msg,
                u'\n'.join(translated_errors)
            )

        return self.json({
            'status': 'success',
            'msg': translated_msg
        })


@implementer(IFolderContentsView)
class FolderContentsView(BrowserView):

    def get_actions(self):
        actions = []
        for name, Utility in getUtilitiesFor(IStructureAction):
            utility = Utility(self.context, self.request)
            actions.append(utility)
        actions.sort(key=lambda a: a.order)
        return [a.get_options() for a in actions]

    def get_options(self):
        site = getSite()
        base_url = site.absolute_url()
        base_vocabulary = '%s/@@getVocabulary?name=' % base_url
        site_path = site.getPhysicalPath()
        context_path = self.context.getPhysicalPath()
        options = {
            'vocabularyUrl': '%splone.app.vocabularies.Catalog' % (
                base_vocabulary),
            'urlStructure': {
                'base': base_url,
                'appended': '/folder_contents'
            },
            'moveUrl': '%s{path}/fc-itemOrder' % base_url,
            'indexOptionsUrl': '%s/@@qsOptions' % base_url,
            'contextInfoUrl': '%s{path}/@@fc-contextInfo' % base_url,
            'setDefaultPageUrl': '%s{path}/@@fc-setDefaultPage' % base_url,
            'availableColumns': {
                'id': translate(_('ID'), context=self.request),
                'ModificationDate': translate(_('Last modified'), context=self.request),  # noqa
                'EffectiveDate': translate(_('Publication date'), context=self.request),  # noqa
                'CreationDate': translate(_('Created on'), context=self.request),  # noqa
                'review_state': translate(_('Review state'), context=self.request),  # noqa
                'Subject': translate(_('Tags'), context=self.request),
                'Type': translate(_('Type'), context=self.request),
                'is_folderish': translate(_('Folder'), context=self.request),
                'exclude_from_nav': translate(_('Excluded from navigation'), context=self.request),  # noqa
                'getObjSize': translate(_('Object Size'), context=self.request),  # noqa
                'last_comment_date': translate(_('Last comment date'), context=self.request),  # noqa
                'total_comments': translate(_('Total comments'), context=self.request),  # noqa
            },
            'buttons': self.get_actions(),
            'rearrange': {
                'properties': {
                    'id': translate(_('Id'), context=self.request),
                    'sortable_title': translate(_('Title'), context=self.request),  # noqa
                    'modified': translate(_('Last modified'), context=self.request),  # noqa
                    'created': translate(_('Created on'), context=self.request),  # noqa
                    'effective': translate(_('Publication date'), context=self.request),  # noqa
                    'Type': translate(_('Type'), context=self.request)
                },
                'url': '%s{path}/@@fc-rearrange' % base_url
            },
            'basePath': '/' + '/'.join(context_path[len(site_path):]),
            'upload': {
                'relativePath': 'fileUpload',
                'baseUrl': base_url,
                'initialFolder': IUUID(self.context, None),
                'useTus': TUS_ENABLED
            },
        }
        return options

    def __call__(self):
        self.options = json_dumps(self.get_options())
        return super(FolderContentsView, self).__call__()


class ContextInfo(BrowserView):

    attributes = ['UID', 'Title', 'Type', 'path', 'review_state',
                  'ModificationDate', 'EffectiveDate', 'CreationDate',
                  'is_folderish', 'Subject', 'getURL', 'id',
                  'exclude_from_nav', 'getObjSize', 'last_comment_date',
                  'total_comments', 'portal_type']

    def __call__(self):
        factories_menu = getUtility(
            IBrowserMenu, name='plone_contentmenu_factory',
            context=self.context).getMenuItems(self.context, self.request)
        factories = []
        for item in factories_menu:
            if item.get('title') == 'folder_add_settings':
                continue
            title = item.get('title', '')
            factories.append({
                'id': item.get('id'),
                'title': title and translate(title, context=self.request) or '',  # noqa
                'action': item.get('action')
                })

        context = aq_inner(self.context)
        crumbs = []
        while not IPloneSiteRoot.providedBy(context):
            crumbs.append({
                'id': context.getId(),
                'title': utils.pretty_title_or_id(context, context)
            })
            context = utils.parent(context)

        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            brains = catalog(UID=IUUID(self.context))
        except TypeError:
            brains = []
        item = None
        if len(brains) > 0:
            obj = brains[0]
            # context here should be site root
            base_path = '/'.join(context.getPhysicalPath())
            item = {}
            for attr in self.attributes:
                key = attr
                if key == 'path':
                    attr = 'getPath'
                val = getattr(obj, attr, None)
                if callable(val):
                    val = val()
                if key == 'path':
                    val = val[len(base_path):]
                item[key] = val
        return json_dumps({
            'addButtons': factories,
            'defaultPage': self.context.getDefaultPage(),
            'breadcrumbs': [c for c in reversed(crumbs)],
            'object': item
        })
