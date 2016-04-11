# -*- coding: utf-8 -*-
from mock import Mock
from plone.app.content.browser import vocabulary
from plone.app.content.browser.file import FileUploadView
from plone.app.content.browser.query import QueryStringIndexOptions
from plone.app.content.browser.vocabulary import VocabularyView
from plone.app.content.testing import ExampleFunctionVocabulary
from plone.app.content.testing import ExampleVocabulary
from plone.app.content.testing import PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING
from plone.app.content.testing import PLONE_APP_CONTENT_DX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.widgets.interfaces import IFieldPermissionChecker
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.component.globalregistry import base
from zope.globalrequest import setRequest
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides
from zope.publisher.browser import TestRequest

import json
import mock
import os
import transaction


_dir = os.path.dirname(__file__)

try:
    import unittest2 as unittest
except ImportError:  # pragma: nocover
    import unittest  # pragma: nocover
    assert unittest  # pragma: nocover


class PermissionChecker(object):
    def __init__(self, context):
        pass

    def validate(self, field_name, vocabulary_name=None):
        if field_name == 'allowed_field':
            return True
        elif field_name == 'disallowed_field':
            return False
        else:
            raise AttributeError('Missing Field')


class ICustomPermissionProvider(Interface):
    pass


def _enable_permission_checker(context):
    provideAdapter(PermissionChecker, adapts=(ICustomPermissionProvider,),
                   provides=IFieldPermissionChecker)
    alsoProvides(context, ICustomPermissionProvider)


def _disable_permission_checker(context):
    noLongerProvides(context, ICustomPermissionProvider)
    base.unregisterAdapter(required=(ICustomPermissionProvider,),
                           provided=IFieldPermissionChecker)


class BrowserTest(unittest.TestCase):

    layer = PLONE_APP_CONTENT_DX_INTEGRATION_TESTING

    def setUp(self):
        self.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})
        setRequest(self.request)
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        provideUtility(ExampleVocabulary(), name=u'vocab_class')
        provideUtility(ExampleFunctionVocabulary, name=u'vocab_function')
        vocabulary.PERMISSIONS.update({
            'vocab_class': 'Modify portal content',
            'vocab_function': 'Modify portal content',
        })

    def testVocabularyQueryString(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = VocabularyView(self.portal, self.request)
        self.request.form.update({
            'name': 'vocab_class',
            'query': 'three'
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)

    def testVocabularyFunctionQueryString(self):
        """Test querying a function based vocabulary with a search string.
        """
        view = VocabularyView(self.portal, self.request)
        self.request.form.update({
            'name': 'vocab_function',
            'query': 'third'
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)

    def testVocabularyNoResults(self):
        """Tests that the widgets displays correctly
        """
        view = VocabularyView(self.portal, self.request)
        query = {
            'criteria': [
                {
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/foo'
                }
            ]
        }
        self.request.form.update({
            'name': 'plone.app.vocabularies.Catalog',
            'query': json.dumps(query)
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 0)

    def testVocabularyCatalogResults(self):
        self.portal.invokeFactory('Document', id="page", title="page")
        self.portal.page.reindexObject()
        view = VocabularyView(self.portal, self.request)
        query = {
            'criteria': [
                {
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/plone'
                }
            ]
        }
        self.request.form.update({
            'name': 'plone.app.vocabularies.Catalog',
            'query': json.dumps(query),
            'attributes': ['UID', 'id', 'title', 'path']
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)

    def testVocabularyCatalogUnsafeMetadataAllowed(self):
        """Users with permission "Modify portal content" are allowed to see
        ``_unsafe_metadata``.
        """
        self.portal.invokeFactory('Document', id="page", title="page")
        self.portal.page.reindexObject()
        view = VocabularyView(self.portal, self.request)
        query = {
            'criteria': [
                {
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/plone/page'
                }
            ]
        }
        self.request.form.update({
            'name': 'plone.app.vocabularies.Catalog',
            'query': json.dumps(query),
            'attributes': [
                'id',
                'commentors',
                'Creator',
                'listCreators',
            ]
        })
        data = json.loads(view())
        self.assertEquals(len(data['results'][0].keys()), 4)

    def testVocabularyCatalogUnsafeMetadataDisallowed(self):
        """Users without permission "Modify portal content" are not allowed to
        see ``_unsafe_metadata``.
        """
        self.portal.invokeFactory('Document', id="page", title="page")
        self.portal.page.reindexObject()
        # Downgrade permissions
        setRoles(self.portal, TEST_USER_ID, [])
        view = VocabularyView(self.portal, self.request)
        query = {
            'criteria': [
                {
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/plone/page'
                }
            ]
        }
        self.request.form.update({
            'name': 'plone.app.vocabularies.Catalog',
            'query': json.dumps(query),
            'attributes': [
                'id',
                'commentors',
                'Creator',
                'listCreators',
            ]
        })
        data = json.loads(view())
        # Only one result key should be returned, as ``commentors``,
        # ``Creator`` and ``listCreators`` is considered unsafe and thus
        # skipped.
        self.assertEquals(len(data['results'][0].keys()), 1)

    def testVocabularyBatching(self):
        amount = 30
        for i in xrange(amount):
            self.portal.invokeFactory('Document', id="page" + str(i),
                                      title="Page" + str(i))
            self.portal['page' + str(i)].reindexObject()
        view = VocabularyView(self.portal, self.request)
        query = {
            'criteria': [
                {
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/plone'
                }
            ]
        }
        # batch pages are 1-based
        self.request.form.update({
            'name': 'plone.app.vocabularies.Catalog',
            'query': json.dumps(query),
            'attributes': ['UID', 'id', 'title', 'path'],
            'batch': {
                'page': '1',
                'size': '10'
            }
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 10)
        self.assertEquals(data['total'], amount)

    def testVocabularyEncoding(self):
        """The vocabulary should not return the binary encoded token
        ("N=C3=A5=C3=B8=C3=AF"), but instead the value as the id in the result
        set. Fixes an encoding problem. See:
        https://github.com/plone/Products.CMFPlone/issues/650
        """
        test_val = u'Nåøï'

        self.portal.invokeFactory('Document', id="page", title="page")
        self.portal.page.subject = (test_val,)
        self.portal.page.reindexObject(idxs=['Subject'])

        self.request.form['name'] = 'plone.app.vocabularies.Keywords'
        results = getMultiAdapter(
            (self.portal, self.request),
            name='getVocabulary'
        )()
        results = json.loads(results)
        result = results['results'][0]

        self.assertEquals(result['text'], test_val)
        self.assertEquals(result['id'], test_val)

    def testVocabularyUnauthorized(self):
        setRoles(self.portal, TEST_USER_ID, [])
        view = VocabularyView(self.portal, self.request)
        self.request.form.update({
            'name': 'plone.app.vocabularies.Users',
            'query': TEST_USER_NAME
        })
        data = json.loads(view())
        self.assertEquals(data['error'], 'Vocabulary lookup not allowed')

    def testVocabularyMissing(self):
        view = VocabularyView(self.portal, self.request)
        self.request.form.update({
            'name': 'vocabulary.that.does.not.exist',
        })
        data = json.loads(view())
        self.assertEquals(data['error'], 'Vocabulary lookup not allowed')

    def testPermissionCheckerAllowed(self):
        # Setup a custom permission checker on the portal
        _enable_permission_checker(self.portal)
        view = VocabularyView(self.portal, self.request)

        # Allowed field is allowed
        self.request.form.update({
            'name': 'plone.app.vocabularies.PortalTypes',
            'field': 'allowed_field',
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']),
                          len(self.portal.portal_types.objectIds()))
        _disable_permission_checker(self.portal)

    def testPermissionCheckerUnknownVocab(self):
        _enable_permission_checker(self.portal)
        view = VocabularyView(self.portal, self.request)
        # Unknown vocabulary gives error
        self.request.form.update({
            'name': 'vocab.does.not.exist',
            'field': 'allowed_field',
        })
        data = json.loads(view())
        self.assertEquals(
            data['error'],
            'No factory with name "{}" exists.'.format(
                'vocab.does.not.exist'))
        _disable_permission_checker(self.portal)

    def testPermissionCheckerDisallowed(self):
        _enable_permission_checker(self.portal)
        view = VocabularyView(self.portal, self.request)
        # Disallowed field is not allowed
        # Allowed field is allowed
        self.request.form.update({
            'name': 'plone.app.vocabularies.PortalTypes',
            'field': 'disallowed_field',
        })
        data = json.loads(view())
        self.assertEquals(data['error'], 'Vocabulary lookup not allowed')
        _disable_permission_checker(self.portal)

    def testPermissionCheckerShortCircuit(self):
        _enable_permission_checker(self.portal)
        view = VocabularyView(self.portal, self.request)
        # Known vocabulary name short-circuits field permission check
        # global permission
        self.request.form['name'] = 'plone.app.vocabularies.Users'
        self.request.form.update({
            'name': 'plone.app.vocabularies.Users',
            'field': 'disallowed_field',
        })
        data = json.loads(view())
        self.assertEquals(data['results'], [])
        _disable_permission_checker(self.portal)

    def testPermissionCheckerUnknownField(self):
        _enable_permission_checker(self.portal)
        view = VocabularyView(self.portal, self.request)
        # Unknown field is raises error
        self.request.form.update({
            'name': 'plone.app.vocabularies.PortalTypes',
            'field': 'missing_field',
        })
        with self.assertRaises(AttributeError):
            view()
        _disable_permission_checker(self.portal)

    def testVocabularyUsers(self):
        acl_users = self.portal.acl_users
        membership = self.portal.portal_membership
        amount = 10
        for i in range(amount):
            id = 'user' + str(i)
            acl_users.userFolderAddUser(id, 'secret', ['Member'], [])
            member = membership.getMemberById(id)
            member.setMemberProperties(mapping={"fullname": id})
        view = VocabularyView(self.portal, self.request)
        self.request.form.update({
            'name': 'plone.app.vocabularies.Users',
            'query': 'user'
        })
        data = json.loads(view())
        self.assertEqual(len(data['results']), amount)

    def testSource(self):
        from z3c.form.browser.text import TextWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.schema import Choice
        from zope.schema.interfaces import ISource

        @implementer(ISource)
        class DummyCatalogSource(object):
            def search_catalog(self, query):
                querytext = query['SearchableText']['query']
                return [Mock(id=querytext)]

        widget = TextWidget(self.request)
        widget.context = self.portal
        widget.field = Choice(source=DummyCatalogSource())
        widget.field.interface = Interface

        from plone.app.content.browser.vocabulary import SourceView
        view = SourceView(widget, self.request)
        query = {
            'criteria': [
                {
                    'i': 'SearchableText',
                    'o': 'plone.app.querystring.operation.string.is',
                    'v': 'foo'
                }
            ]
        }
        self.request.form.update({
            'query': json.dumps(query),
            'attributes': 'id',
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)
        self.assertEquals(data['results'][0]['id'], 'foo')

    def testSourceCollectionField(self):
        # This test uses a collection field
        # and a source providing the 'search' method
        # to help achieve coverage.
        from z3c.form.browser.text import TextWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.schema import List, Choice
        from zope.schema.interfaces import ISource
        from zope.schema.vocabulary import SimpleTerm

        @implementer(ISource)
        class DummySource(object):
            def search(self, query):
                terms = [SimpleTerm(query, query)]
                return iter(terms)

        widget = TextWidget(self.request)
        widget.context = self.portal
        widget.field = List(value_type=Choice(source=DummySource()))
        widget.field.interface = Interface

        from plone.app.content.browser.vocabulary import SourceView
        view = SourceView(widget, self.request)
        query = {
            'criteria': [
                {
                    'i': 'SearchableText',
                    'o': 'plone.app.querystring.operation.string.is',
                    'v': 'foo'
                }
            ],
            'sort_on': 'id',
            'sort_order': 'ascending',
        }
        self.request.form.update({
            'query': json.dumps(query),
            'batch': json.dumps({'size': 10, 'page': 1}),
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)
        self.assertEquals(data['results'][0]['id'], 'foo')

    def testSourcePermissionDenied(self):
        from z3c.form.browser.text import TextWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.schema import Choice
        from zope.schema.interfaces import ISource

        @implementer(ISource)
        class DummyCatalogSource(object):
            def search_catalog(self, query):
                querytext = query['SearchableText']['query']
                return [Mock(id=querytext)]

        widget = TextWidget(self.request)
        widget.context = self.portal
        widget.field = Choice(source=DummyCatalogSource())
        widget.field.interface = Interface

        from plone.app.content.browser.vocabulary import SourceView
        view = SourceView(widget, self.request)
        query = {
            'criteria': [
                {
                    'i': 'SearchableText',
                    'o': 'plone.app.querystring.operation.string.is',
                    'v': 'foo'
                }
            ]
        }
        self.request.form.update({
            'query': json.dumps(query),
        })
        logout()
        data = json.loads(view())
        self.assertEquals(data['error'], 'Vocabulary lookup not allowed.')

    def testSourceTextQuery(self):
        from z3c.form.browser.text import TextWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.schema import Choice
        from zope.schema.interfaces import ISource

        @implementer(ISource)
        class DummyCatalogSource(object):
            def search(self, query):
                return [Mock(value=Mock(id=query))]

        widget = TextWidget(self.request)
        widget.context = self.portal
        widget.field = Choice(source=DummyCatalogSource())
        widget.field.interface = Interface

        from plone.app.content.browser.vocabulary import SourceView
        view = SourceView(widget, self.request)
        self.request.form.update({
            'query': 'foo',
            'attributes': 'id',
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)
        self.assertEquals(data['results'][0]['id'], 'foo')

    def testQueryStringConfiguration(self):
        view = QueryStringIndexOptions(self.portal, self.request)
        data = json.loads(view())
        # just test one so we know it's working...
        self.assertEqual(data['indexes']['sortable_title']['sortable'], True)

    @mock.patch('zope.i18n.negotiate', new=lambda ctx: 'de')
    def testUntranslatableMetadata(self):
        """Test translation of ``@@getVocabulary`` view results.
        From the standard metadata columns, only ``Type`` is translated.
        """
        # Language is set via language negotiaton patch.

        self.portal.invokeFactory('Document', id="page", title="page")
        self.portal.page.reindexObject()
        view = VocabularyView(self.portal, self.request)
        query = {
            'criteria': [
                {
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/plone/page'
                }
            ]
        }
        self.request.form.update({
            'name': 'plone.app.vocabularies.Catalog',
            'query': json.dumps(query),
            'attributes': [
                'id',
                'portal_type',
                'Type',
            ]
        })

        # data['results'] should return one item, which represents the document
        # created before.
        data = json.loads(view())

        # Type is translated
        self.assertEqual(data['results'][0]['Type'], u'Seite')

        # portal_type is never translated
        self.assertEqual(data['results'][0]['portal_type'], u'Document')


class FunctionalBrowserTest(unittest.TestCase):

    layer = PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = TestRequest()
        setRequest(self.request)
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def testFileUpload(self):
        view = FileUploadView(self.portal, self.request)
        from plone.namedfile.file import FileChunk
        chunk = FileChunk('foobar')
        chunk.filename = 'test.xml'
        self.request.form['file'] = chunk
        self.request.REQUEST_METHOD = 'POST'
        # the next calls plone.app.dexterity.factories and does a
        # transaction.commit. Needs cleanup and FunctionalTesting layer.
        data = json.loads(view())
        self.assertEqual(data['url'], 'http://nohost/plone/test.xml')
        self.assertTrue(data['UID'] is not None)
        # clean it up...
        self.portal.manage_delObjects(['test.xml'])
        transaction.commit()

    def testFileUploadTxt(self):
        view = FileUploadView(self.portal, self.request)
        from plone.namedfile.file import FileChunk
        chunk = FileChunk('foobar')
        chunk.filename = 'test.txt'
        self.request.form['file'] = chunk
        self.request.REQUEST_METHOD = 'POST'
        # the next calls plone.app.dexterity.factories and does a
        # transaction.commit. Needs cleanup and FunctionalTesting layer.
        data = json.loads(view())
        self.assertEqual(data['url'], 'http://nohost/plone/test.txt')
        self.assertTrue(data['UID'] is not None)
        # clean it up...
        self.portal.manage_delObjects(['test.txt'])
        transaction.commit()
