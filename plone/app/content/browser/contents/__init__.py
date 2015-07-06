from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.interfaces import IStructureAction
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from plone.folder.interfaces import IExplicitOrdering
from plone.protect.postonly import check as checkpost
from plone.uuid.interfaces import IUUID
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer


try:
    from plone.app.content.browser.file import TUS_ENABLED
except ImportError:
    TUS_ENABLED = False


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
            if self.required_obj_permission:
                if not self.mtool.checkPermission(self.required_obj_permission,
                                                  obj):
                    self.errors.append(_('Permission denied for "${title}"',
                                         mapping={
                                             'title': self.objectTitle(obj)
                                         }))
                    continue
            self.action(obj)

        self.finish()
        return self.message(selection)

    def message(self, missing=[]):
        if len(missing) > 0:
            self.errors.append(_('${items} could not be found', mapping={
                'items': str(len(missing))}))
        if not self.errors:
            msg = self.success_msg
        else:
            msg = self.failure_msg

        translated_msg = translate(msg, context=self.request)
        if self.errors:
            translated_errors = [translate(error, context=self.request)
                                 for error in self.errors]
            translated_msg = '%s: %s' % (translated_msg, '\n'.join(translated_errors))

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

    def __call__(self):
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
                'Title': translate(_('Title'), context=self.request),
                'ModificationDate': translate(_('Last modified'), context=self.request),
                'EffectiveDate': translate(_('Publication date'), context=self.request),
                'CreationDate': translate(_('Created on'), context=self.request),
                'review_state': translate(_('Review state'), context=self.request),
                'Subject': translate(_('Tags'), context=self.request),
                'Type': translate(_('Type'), context=self.request),
                'is_folderish': translate(_('Folder'), context=self.request),
                'exclude_from_nav': translate(_('Excluded from navigation'), context=self.request),
                'getObjSize': translate(_('Object Size'), context=self.request),
                'last_comment_date': translate(_('Last comment date'), context=self.request),
                'total_comments': translate(_('Total comments'), context=self.request),
            },
            'buttons': self.get_actions(),
            'rearrange': {
                'properties': {
                    'id': translate(_('Id'), context=self.request),
                    'sortable_title': translate(_('Title'), context=self.request),
                    'modified': translate(_('Last modified'), context=self.request),
                    'created': translate(_('Created on'), context=self.request),
                    'effective': translate(_('Publication date'), context=self.request),
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
            }
        }
        self.options = json_dumps(options)
        return super(FolderContentsView, self).__call__()


class ItemOrder(ContentsBaseAction):
    success_msg = _('Successfully moved item')
    failure_msg = _('Error moving item')

    def getOrdering(self):
        if IPloneSiteRoot.providedBy(self.context):
            return self.context
        else:
            ordering = self.context.getOrdering()
            if not IExplicitOrdering.providedBy(ordering):
                return None
            return ordering

    def __call__(self):
        self.errors = []
        self.protect()
        id = self.request.form.get('id')
        ordering = self.getOrdering()
        delta = self.request.form['delta']
        subset_ids = json_loads(self.request.form.get('subset_ids', '[]'))
        if delta == 'top':
            ordering.moveObjectsToTop([id])
        elif delta == 'bottom':
            ordering.moveObjectsToBottom([id])
        else:
            delta = int(delta)
            if subset_ids:
                position_id = [(ordering.getObjectPosition(i), i)
                               for i in subset_ids]
                position_id.sort()
                if subset_ids != [i for position, i in position_id]:
                    self.errors.append(_('Client/server ordering mismatch'))
                    return self.message()

            if not hasattr(ordering, 'moveObjectsByDelta'):
                self.errors.append(_('This folder does not support ordering'))
            else:
                ordering.moveObjectsByDelta([id], delta)
        return self.message()


class SetDefaultPage(ContentsBaseAction):
    success_msg = _(u'Default page set successfully')
    failure_msg = _(u'Failed to set default page')

    def __call__(self):
        id = self.request.form.get('id')
        self.errors = []

        if id not in self.context.objectIds():
            self.errors.append(
                _(u'There is no object with short name '
                  u'${name} in this folder.',
                  mapping={u'name': id}))
        else:
            self.context.setDefaultPage(id)
        return self.message()


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
                'title': title and translate(title, context=self.request) or '',
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


def getOrdering(context):
    if IPloneSiteRoot.providedBy(context):
        return context
    else:
        ordering = context.getOrdering()
        if not IExplicitOrdering.providedBy(ordering):
            return None
        return ordering


class Rearrange(ContentsBaseAction):
    def __call__(self):
        self.protect()
        self.errors = []
        ordering = getOrdering(self.context)
        if ordering:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(path={
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1
            }, sort_on=self.request.form.get('rearrange_on'))
            if self.request.form.get('reversed') == 'true':
                brains = [b for b in reversed(brains)]
            for idx, brain in enumerate(brains):
                ordering.moveObjectToPosition(brain.id, idx)
        else:
            self.errors.append(_(u'cannot rearrange folder'))
        return self.message()