from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class DefaultViewSelectionView(BrowserView):

    def isValidTemplate(self, templateId):
        return templateId in [a[0] for a in self.vocab]

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
            if not 'objectId' in self.request.form:
                message = _(u'Please select an item to use.')
                msgtype = 'error'
            else:
                objectId = self.request.form['objectId']

                if not objectId in self.context.objectIds():
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
