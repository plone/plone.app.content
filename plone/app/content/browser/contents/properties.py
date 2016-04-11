# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.interfaces import IStructureAction
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer


@implementer(IStructureAction)
class PropertiesAction(object):

    template = ViewPageTemplateFile('templates/properties.pt')
    order = 8

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        base_vocabulary = '%s/@@getVocabulary?name=' % getSite().absolute_url()
        return {
            'title': translate(_('Properties'), context=self.request),
            'id': 'properties',
            'icon': 'edit',
            'url': self.context.absolute_url() + '/@@fc-properties',
            'form': {
                'title': _('Modify properties on items'),
                'template': self.template(
                    vocabulary_url='%splone.app.vocabularies.Users' % (
                        base_vocabulary)
                )
            }
        }


class PropertiesActionView(ContentsBaseAction):
    success_msg = _(u'Successfully updated metadata')
    failure_msg = _(u'Failure updating metadata')
    required_obj_permission = 'Modify portal content'

    def __call__(self):
        self.effectiveDate = self.request.form.get('effectiveDate')
        self.expirationDate = self.request.form.get('expirationDate')
        self.copyright = self.request.form.get('copyright')
        self.contributors = self.request.form.get('contributors')
        if self.contributors:
            self.contributors = self.contributors.split(',')
        else:
            self.contributors = []
        self.creators = self.request.form.get('creators', '')
        if self.creators:
            self.creators = self.creators.split(',')
        self.exclude = self.request.form.get('exclude-from-nav')
        return super(PropertiesActionView, self).__call__()

    def dx_action(self, obj):
        if self.effectiveDate and hasattr(obj, 'effective_date'):
            obj.effective_date = DateTime(self.effectiveDate)
        if self.expirationDate and hasattr(obj, 'expiration_date'):
            obj.expiration_date = DateTime(self.expirationDate)
        if self.copyright and hasattr(obj, 'rights'):
            obj.rights = self.copyright
        if self.contributors and hasattr(obj, 'contributors'):
            obj.contributors = tuple(self.contributors)
        if self.creators and hasattr(obj, 'creators'):
            obj.creators = tuple(self.creators)
        if self.exclude and hasattr(obj, 'exclude_from_nav'):
            obj.exclude_from_nav = self.exclude == 'yes'

    def action(self, obj):
        if IDexterityContent.providedBy(obj):
            self.dx_action(obj)
        else:
            if self.effectiveDate:
                try:
                    obj.setEffectiveDate(DateTime(self.effectiveDate))
                except AttributeError:
                    pass
            if self.expirationDate:
                try:
                    obj.setExpirationDate(DateTime(self.expirationDate))
                except AttributeError:
                    pass
            if self.copyright:
                try:
                    obj.setRights(self.copyright)
                except AttributeError:
                    pass
            if self.contributors:
                try:
                    obj.setContributors(self.contributors)
                except AttributeError:
                    pass
            if self.creators:
                try:
                    obj.setCreators(self.creators)
                except AttributeError:
                    pass
            if self.exclude:
                try:
                    obj.setExcludeFromNav(self.exclude == 'yes')
                except AttributeError:
                    pass
        obj.reindexObject()
