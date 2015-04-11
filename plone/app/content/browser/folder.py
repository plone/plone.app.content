# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from OFS.CopySupport import CopyError
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import BrowserView
from ZODB.POSException import ConflictError
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from plone.dexterity.interfaces import IDexterityContent
from plone.folder.interfaces import IExplicitOrdering
from plone.protect.postonly import check as checkpost
from plone.uuid.interfaces import IUUID
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.interface import implementer
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent
import transaction

try:
    from plone.app.content.browser.file import TUS_ENABLED
except ImportError:
    TUS_ENABLED = False


@implementer(IFolderContentsView)
class FolderContentsView(BrowserView):

    def __call__(self):
        site = getSite()
        base_url = site.absolute_url()
        base_vocabulary = '%s/@@getVocabulary?name=' % base_url
        site_path = site.getPhysicalPath()
        context_path = self.context.getPhysicalPath()
        options = {
            'vocabularyUrl': '%splone.app.vocabularies.Catalog' % (
                base_vocabulary),
            'tagsVocabularyUrl': '%splone.app.vocabularies.Keywords' % (
                base_vocabulary),
            'usersVocabularyUrl': '%splone.app.vocabularies.Users' % (
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
                'ModificationDate': translate(_('Last modified'),
                    context=self.request),
                'EffectiveDate': translate(_('Publication date'),
                    context=self.request),
                'CreationDate': translate(_('Created on'),
                    context=self.request),
                'review_state': translate(_('Review state'),
                    context=self.request),
                'Subject': translate(_('Tags'), context=self.request),
                'Type': translate(_('Type'), context=self.request),
                'is_folderish': translate(_('Folder'), context=self.request),
                'exclude_from_nav': translate(_('Excluded from nav'),
                    context=self.request),
                'getObjSize': translate(_('Object Size'),
                    context=self.request),
                'last_comment_date': translate(_('Last comment date'),
                    context=self.request),
                'total_comments': translate(_('Total comments'),
                    context=self.request),
            },
            'buttonGroups': {
                'primary': [{
                    'id': 'cut',
                    'title': translate(_('Cut'), context=self.request),
                }, {
                    'id': 'copy',
                    'title': translate(_('Copy'), context=self.request),
                }, {
                    'id': 'paste',
                    'title': translate(_('Paste'), context=self.request),
                    'url': base_url + '/@@fc-paste'
                }, {
                    'id': 'delete',
                    'title': translate(_('Delete'), context=self.request),
                    'url': base_url + '/@@fc-delete',
                    'context': 'danger',
                    'icon': 'trash'
                }],
                'secondary': [{
                    'id': 'workflow',
                    'title': translate(_('Workflow'), context=self.request),
                    'url': base_url + '/@@fc-workflow'
                }, {
                    'id': 'tags',
                    'title': translate(_('Tags'), context=self.request),
                    'url': base_url + '/@@fc-tags'
                }, {
                    'id': 'properties',
                    'title': translate(_('Properties'), context=self.request),
                    'url': base_url + '/@@fc-properties'
                }, {
                    'id': 'rename',
                    'title': translate(_('Rename'), context=self.request),
                    'url': base_url + '/@@fc-rename'
                }]
            },
            'rearrange': {
                'properties': {
                    'id': translate(_('Id'), context=self.request),
                    'sortable_title': translate(_('Title'),
                        context=self.request),
                    'modified': translate(_('Last modified'),
                        context=self.request),
                    'created': translate(_('Created on'),
                        context=self.request),
                    'effective': translate(_('Publication date'),
                        context=self.request),
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


class FolderContentsActionView(BrowserView):

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
            self.action(obj)

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
        translated_errors = [translate(error, context=self.request)
                             for error in self.errors]

        return self.json({
            'status': 'success',
            'msg': '%s: %s' % (translated_msg, '\n'.join(translated_errors))
        })


class PasteAction(FolderContentsActionView):
    success_msg = _('Successfully pasted all items')
    failure_msg = _('Error during paste, some items were not pasted')
    required_obj_permission = 'Copy or Move'

    def copy(self, obj):
        title = self.objectTitle(obj)
        parent = obj.aq_inner.aq_parent
        try:
            parent.manage_copyObjects(obj.getId(), self.request)
        except CopyError:
            self.errors.append(_(u'${title} is not copyable.',
                                 mapping={u'title': title}))

    def cut(self, obj):
        title = self.objectTitle(obj)

        try:
            lock_info = obj.restrictedTraverse('@@plone_lock_info')
        except AttributeError:
            lock_info = None

        if lock_info is not None and lock_info.is_locked():
            self.errors.append(_(u'${title} is locked and cannot be cut.',
                                 mapping={u'title': title}))

        parent = obj.aq_inner.aq_parent
        try:
            parent.manage_cutObjects(obj.getId(), self.request)
        except CopyError:
            self.errors.append(_(u'${title} is not moveable.',
                                 mapping={u'title': title}))

    def action(self, obj):
        operation = self.request.form['pasteOperation']
        if operation == 'copy':
            self.copy(obj)
        else:  # cut
            self.cut(obj)
        if self.errors:
            return
        try:
            self.dest.manage_pasteObjects(self.request['__cp'])
        except ConflictError:
            raise
        except Unauthorized:
            # avoid this unfriendly exception text:
            # "You are not allowed to access 'manage_pasteObjects' in this
            # context"
            self.errors.append(
                _(u'You are not authorized to paste ${title} here.',
                    mapping={u'title': self.objectTitle(obj)}))


class DeleteAction(FolderContentsActionView):

    def action(self, obj):
        parent = obj.aq_inner.aq_parent
        title = self.objectTitle(obj)

        try:
            lock_info = obj.restrictedTraverse('@@plone_lock_info')
        except AttributeError:
            lock_info = None

        if lock_info is not None and lock_info.is_locked():
            self.errors.append(_(u'${title} is locked and cannot be deleted.',
                                 mapping={u'title': title}))
            return
        else:
            parent.manage_delObjects(obj.getId(), self.request)


class RenameAction(FolderContentsActionView):
    success_msg = _('Items renamed')
    failure_msg = _('Failed to rename all items')

    def __call__(self):
        self.errors = []
        self.protect()
        context = aq_inner(self.context)

        torename = json_loads(self.request.form['torename'])

        catalog = getToolByName(context, 'portal_catalog')
        mtool = getToolByName(context, 'portal_membership')

        missing = []
        for data in torename:
            uid = data['UID']
            brains = catalog(UID=uid)
            if len(brains) == 0:
                missing.append(uid)
                continue
            obj = brains[0].getObject()
            title = self.objectTitle(obj)
            if not mtool.checkPermission('Copy or Move', obj):
                self.errors(_(u'Permission denied to rename ${title}.',
                              mapping={u'title': title}))
                continue

            sp = transaction.savepoint(optimistic=True)

            newid = data['newid'].encode('utf8')
            newtitle = data['newtitle']
            try:
                obid = obj.getId()
                title = obj.Title()
                change_title = newtitle and title != newtitle
                if change_title:
                    getSecurityManager().validate(obj, obj, 'setTitle',
                                                  obj.setTitle)
                    obj.setTitle(newtitle)
                    notify(ObjectModifiedEvent(obj))
                if newid and obid != newid:
                    parent = aq_parent(aq_inner(obj))
                    # Make sure newid is safe
                    newid = INameChooser(parent).chooseName(newid, obj)
                    # Update the default_page on the parent.
                    context_state = getMultiAdapter(
                        (obj, self.request), name='plone_context_state')
                    if context_state.is_default_page():
                        parent.setDefaultPage(newid)
                    parent.manage_renameObjects((obid, ), (newid, ))
                elif change_title:
                    # the rename will have already triggered a reindex
                    obj.reindexObject()
            except ConflictError:
                raise
            except Exception:
                sp.rollback()
                self.errors.append(_('Error renaming ${title}', mapping={
                    'title': title}))

        return self.message(missing)


class TagsAction(FolderContentsActionView):
    required_obj_permission = 'Modify portal content'

    def __call__(self):
        self.remove = set([v.encode('utf8') for v in
                           json_loads(self.request.form.get('remove'))])
        self.add = set([v.encode('utf8') for v in
                        json_loads(self.request.form.get('add'))])
        return super(TagsAction, self).__call__()

    def action(self, obj):
        tags = set(obj.Subject())
        tags = tags - self.remove
        tags = tags | self.add
        obj.setSubject(list(tags))
        obj.reindexObject()


class WorkflowAction(FolderContentsActionView):
    required_obj_permission = 'Modify portal content'

    def __call__(self):
        self.pworkflow = getToolByName(self.context, 'portal_workflow')
        self.putils = getToolByName(self.context, 'plone_utils')
        self.transition_id = self.request.form.get('transition', None)
        self.comments = self.request.form.get('comments', '')
        self.recurse = self.request.form.get('recurse', 'no') == 'yes'
        if self.request.REQUEST_METHOD == 'POST':
            return super(WorkflowAction, self).__call__()
        else:
            # for GET, we return available transitions
            selection = self.get_selection()
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(UID=selection)
            transitions = []
            for brain in brains:
                obj = brain.getObject()
                for transition in self.pworkflow.getTransitionsFor(obj):
                    tdata = {
                        'id': transition['id'],
                        'title': transition['name']
                    }
                    if tdata not in transitions:
                        transitions.append(tdata)
            return self.json({
                'transitions': transitions
            })

    def action(self, obj):
        transitions = self.pworkflow.getTransitionsFor(obj)
        if self.transition_id in [t['id'] for t in transitions]:
            try:
                # set effective date if not already set
                if obj.EffectiveDate() == 'None':
                    obj.setEffectiveDate(DateTime())

                self.pworkflow.doActionFor(obj, self.transition_id,
                                           comment=self.comments)
                if self.putils.isDefaultPage(obj):
                    self.action(obj.aq_parent.aq_parent)
                if self.recurse and IFolderish.providedBy(obj):
                    for sub in obj.values():
                        self.action(sub)
            except ConflictError:
                raise
            except Exception:
                self.errors.append(_('Could not transition: ${title}',
                    mapping={'title': self.objectTitle(obj)}))


class PropertiesAction(FolderContentsActionView):
    success_msg = _(u'Successfully updated metadata')
    failure_msg = _(u'Failure updating metadata')
    required_obj_permission = 'Modify portal content'

    def __call__(self):
        self.effectiveDate = self.request.form.get('effectiveDate')
        effectiveTime = self.request.form.get('effectiveTime')
        if self.effectiveDate and effectiveTime:
            self.effectiveDate = self.effectiveDate + ' ' + effectiveTime
        self.expirationDate = self.request.form.get('expirationDate')
        expirationTime = self.request.form.get('expirationTime')
        if self.expirationDate and expirationTime:
            self.expirationDate = self.expirationDate + ' ' + expirationTime
        self.copyright = self.request.form.get('copyright', '')
        self.contributors = json_loads(
            self.request.form.get('contributors', '[]'))
        self.creators = json_loads(self.request.form.get('creators', '[]'))
        self.exclude = self.request.form.get('exclude_from_nav', None)
        return super(PropertiesAction, self).__call__()

    def dx_action(self, obj):
        if self.effectiveDate and hasattr(obj, 'effective_date'):
            obj.effective_date = DateTime(self.effectiveDate)
        if self.expirationDate and hasattr(obj, 'expiration_date'):
            obj.expiration_date = DateTime(self.expirationDate)
        if self.copyright and hasattr(obj, 'rights'):
            obj.rights = self.copyright
        if self.contributors and hasattr(obj, 'contributors'):
            obj.contributors = tuple([c['id'] for c in self.contributors])
        if self.creators and hasattr(obj, 'creators'):
            obj.creators = tuple([c['id'] for c in self.creators])
        if self.exclude and hasattr(obj, 'exclude_from_nav'):
            obj.exclude_from_nav = self.exclude == 'yes'

    def action(self, obj):
        if IDexterityContent.providedBy(obj):
            self.dx_action(obj)
        else:
            if self.effectiveDate:
                obj.setEffectiveDate(DateTime(self.effectiveDate))
            if self.expirationDate:
                obj.setExpirationDate(DateTime(self.expirationDate))
            if self.copyright:
                obj.setRights(self.copyright)
            if self.contributors:
                obj.setContributors([c['id'] for c in self.contributors])
            if self.creators:
                obj.setCreators([c['id'] for c in self.creators])
            if self.exclude:
                obj.setExcludeFromNav(self.exclude == 'yes')
        obj.reindexObject()


class ItemOrder(FolderContentsActionView):
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

            ordering.moveObjectsByDelta([id], delta)
        return self.message()


class SetDefaultPage(FolderContentsActionView):
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
                  'total_comments']

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
                'title': title and translate(title,
                    context=self.request) or '',
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


class Rearrange(FolderContentsActionView):
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
