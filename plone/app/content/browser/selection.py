# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter


class DefaultViewSelectionView(BrowserView):

    def isValidTemplate(self, templateId):
        return templateId in [a[0] for a in self.vocab]

    def canSelectDefaultPage(self):
        if not self.context.isPrincipiaFolderish:
            return False
        return self.context.canSetDefaultPage()

    @property
    def vocab(self):
        return self.context.getAvailableLayouts()

    @property
    def selectedLayout(self):
        if not self.context_state.is_default_page():
            return self.context.getLayout()
        else:
            return ''

    def selectViewTemplate(self):
        templateId = self.request.get('templateId')

        if self.isValidTemplate(templateId):
            self.context.setLayout(templateId)

        self.request.response.redirect(self.context.absolute_url() + '/view')

    @property
    def action_url(self):
        return '{0:s}/select_default_view'.format(
            self.context_state.object_url())

    def __call__(self):

        self.context_state = getMultiAdapter(
            (self.context, self.request), name='plone_context_state')

        templateId = self.request.form.get('templateId', False)
        if templateId:
            plone_utils = getToolByName(self.context, 'plone_utils')
            # Make sure this is a valid template
            if self.isValidTemplate(templateId):
                # Update the template
                self.context.setLayout(templateId)
                plone_utils.addPortalMessage(u'View changed.')
            else:
                plone_utils.addPortalMessage(u'Invalid view.', type="error")
                return self.index()

        if templateId or self.request.form.get('form.buttons.Cancel', False):
            # Redirect to view
            self.request.response.redirect(
                '%s/view' % self.context_state.object_url())

        return self.index()


class DefaultPageSelectionView(BrowserView):

    def __call__(self):
        if 'form.buttons.Save' in self.request.form:
            if 'objectId' not in self.request.form:
                message = _(u'Please select an item to use.')
                msgtype = 'error'
            else:
                objectId = self.request.form['objectId']

                if objectId not in self.context.objectIds():
                    message = _(u'There is no object with short name ${name} '
                                u'in this folder.',
                                mapping={u'name': objectId})
                    msgtype = 'error'
                else:
                    self.context.setDefaultPage(objectId)
                    message = _(u'View changed.')
                    msgtype = 'info'
                    self.request.response.redirect(self.context.absolute_url())
            IStatusMessage(self.request).add(message, msgtype)
        elif 'form.buttons.Cancel' in self.request.form:
            self.request.response.redirect(self.context.absolute_url())

        return self.index()

    def get_selectable_items(self):
        """ Return brains in this container that can be used as default_pages
        """
        context = aq_inner(self.context)
        registry = getUtility(IRegistry)
        view_types = registry.get(
            'plone.types_use_view_action_in_listings', [])
        default_page_types = registry.get('plone.default_page_types', [])
        portal_types = getToolByName(self.context, 'portal_types')

        results = []
        for brain in context.getFolderContents():
            portal_type = brain.portal_type
            if portal_type in view_types:
                # Skip files and images
                continue

            if portal_type in default_page_types:
                # Allow types that are explicitly in default_page_types
                results.append(brain)
                continue

            if brain.is_folderish:
                fti = portal_types.get(portal_type)
                if not fti:
                    continue
                if fti.filter_content_types and fti.allowed_content_types or \
                        not fti.filter_content_types:
                    # Disallow folderish types if you can't add any content.
                    # To override you have to add type to default_page_types
                    continue
            results.append(brain)
        return results
