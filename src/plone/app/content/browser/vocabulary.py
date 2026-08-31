import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.content.browser.vocabulary import BaseVocabularyView, SourceView, VocabLookupException, VocabularyView instead.",
    MAX_BATCH_SIZE="plone.app.layout.content.browser.vocabulary:MAX_BATCH_SIZE",
    DEFAULT_PERMISSION="plone.app.layout.content.browser.vocabulary:DEFAULT_PERMISSION",
    DEFAULT_PERMISSION_SECURE="plone.app.layout.content.browser.vocabulary:DEFAULT_PERMISSION_SECURE",
    PERMISSIONS="plone.app.layout.content.browser.vocabulary:PERMISSIONS",
    TRANSLATED_IGNORED="plone.app.layout.content.browser.vocabulary:TRANSLATED_IGNORED",
    VocabLookupException="plone.app.layout.content.browser.vocabulary:VocabLookupException",
    BaseVocabularyView="plone.app.layout.content.browser.vocabulary:BaseVocabularyView",
    VocabularyView="plone.app.layout.content.browser.vocabulary:VocabularyView",
    SourceView="plone.app.layout.content.browser.vocabulary:SourceView",
)
