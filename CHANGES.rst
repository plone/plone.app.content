Changelog
=========


3.3.4 (2016-12-30)
------------------

Bug fixes:

- Add a missing comma between two strings in a list,
  python merges them into a single string if not.
  [keul, ekulos, gforcada]


3.3.3 (2016-12-02)
------------------

Bug fixes:

- Stop using ``canSelectDefaultPage`` Python script from CMFPlone.
  [davisagli]


3.3.2 (2016-11-10)
------------------

New features:

- Move ``get_top_site_from_url`` out from here into ``Products.CMFPlone.utils``.
  Deprecate old import.
  [thet]

Bug fixes:

- Fix ``folder_contents`` view incorrectly returning an ``application/json`` response instead of a ``text/html`` response.
  [thet]

- Fix issue with ``get_top_site_from_url``, where in some circumstances a ValueError was thrown.
  If that happens, just return ``getSite``.
  You will only notice, if you have subsites, access them non-VirtualHost-rooted and an error is thrown.
  Then folder contents won't be able to navigate up to the root Plone site.
  [thet]


3.3.1 (2016-09-23)
------------------

Bug fixes:

- Apply security hotfix 20160830 for folder factories redirection.  [maurits]
- Fix UnicodeDecodeError on full review list view
  [datakurre]


3.3 (2016-09-14)
----------------

New features:

- Folder contents rename dialog: In the rename dialog, show image thumbnails in ``thumb`` scale instead of ``icon``.
  Plones standard ``icon`` scale is way to small to be useful for images.
  [thet]

Bug fixes:

- Folder contents properties dialog: Fix form request variables for ``effectiveDate`` and ``expirationDate`` dates.
  [thet]

- Fix a json "circular reference detected" error which happened when the json dumper got unparsable data types.
  [pcdummy]


3.2 (2016-08-18)
----------------

New features:

- Add ``@@allow_upload`` view, which returns a JSON string to indicate if File or Image uploads are allowed in the current container.
  When the view is called with a ``path`` request parameter, then content at this path is used instead the content where the view is called.
  [thet]

- Factor out the available columns ignored list which can be used to narrow down the available columns list to a user friendly set.
  [thet]

Bug fixes:

- Explicitly set ``application/json`` content type for JSON responses and declare an ``utf-8`` charset.
  [thet]

- Properly deprecated ``_permissions`` in favor of ``PERMISSIONS``.
  Since 3.1, the ``_permissions`` variable was ``None`` instead of a
  backwards compatibility alias for ``PERMISSIONS`` due to a wrong
  deprecation.  [maurits]

- Fix recursive workflow actions. The ``isDefaultPage`` check acquired
  the wrong parent context. Also bypass the recurse flag for default page
  workflow state change. [petschki]


3.1.2 (2016-07-05)
------------------

Bug fixes:

- Bind view ``plonejsi18n`` to INavigationRoot in order to enable non-portal-root published sites to deliver the translations for javascript.
  [jensens]


3.1.1 (2016-05-02)
------------------

Bug fixes:

- Lookup of Content Type for passing in Content Type Factory improved,
  so that all Images (especially Tiff) are stored as Images not Files.
  [loechel]


3.1 (2016-04-26)
----------------

New:

- Show attributes from ``_unsafe_metadata`` if user has "Modify Portal Content" permissions.
  [thet]

- Add ``Creator``, ``Description``, ``end``, ``start`` and ``location`` to the available columns and context attributes for folder_contents.
  [thet]

Fixes:

- Folder contents: When pasting, handle "Disallowed subobject type" ValueError and present a helpful error message.
  Fixes: plone/mockup#657
  [thet]

- Folder contents: Acquire the top most visible portal object to operate on.
  Fixes some issues in INavigationRoot or ISite based subsites and virtual hosting environments pointing to subsites.
  Fixes include: show correct breadcrumb paths, paste to correct location.
  Fixes: #86
  [thet]

- Added most notably `portal_type`, `review_state` and `Subject` but also `exclude_from_nav`, `is_folderish`, `last_comment_date`, `meta_type` and `total_comments` to ``BaseVocabularyView`` ``translate_ignored`` list.
  Some of them are necessary for frontend logic and others cannot be translated.
  Fixes https://github.com/plone/plone.app.content/issues/77
  [thet]

- Remove ``portal_type`` from available columns and use ``Type`` instead, which is meant to be read by humans.
  ``portal_type`` is now available on the attributes object.
  [thet]

- Vocabulary permissions are considered View permission by default, if not
  stated different in PERMISSIONS global. Renamed _permissions to PERMISSIONS,
  Deprecated BBB name in place. Also minor code-style changes
  [jensens, thet]

- Fix test isolation problem and remove an unnecessary test dependency on ``plone.app.widgets``.
  [thet]

- Restore acquisition context in orderings, which had been dropped by accident in 3.0.15
  [pysailor]


3.0.20 (2016-02-27)
-------------------

Fixes:

- Fixed tests for adding creators to content.  [vangheem]


3.0.19 (2016-02-26)
-------------------

Fixes:

- Add fallback to global vocabulary permission check when permission
  checker can't be found.
  [alecm]


3.0.18 (2016-02-19)
-------------------

Fixes:

- Added translation functionality to  folder content panel.
  https://github.com/plone/Products.CMFPlone/issues/1398
  [terapyon]


3.0.17 (2016-02-08)
-------------------

Fixes:

- Fixed error message unicode error in rename action.
  [Gagaro]

- Fixed errors when cutting and copying objects in folder contents.
  [vangheem]


3.0.16 (2016-01-08)
-------------------

Fixes:

- Fixed renaming when only changing title.
  [Gagaro]


3.0.15 (2015-12-15)
-------------------

New:

- Ensure the base context allows ordering during rearranging.
  [Gagaro]

Fixes:

- Fix case where non-dexterity object did not properties
  [vangheem]

- Fixed rearranging for archetypes.
  [Gagaro]

- Fixed error message displaying during rearranging.
  [Gagaro]


3.0.14 (2015-11-26)
-------------------

Fixes:

- Fixed upload of txt files in folder_contents (#33, #58).
  [ale-rt]

- Cleanup and rework: contenttype-icons and showing thumbnails
  for images/leadimages in listings.
  https://github.com/plone/Products.CMFPlone/issues/1226
  [fgrcon]

- Fixed @@getSource view to work with a text query
  (as done by the ajax autocomplete widget)
  in addition to a querystring widget query.
  [davisagli]


3.0.13 (2015-10-27)
-------------------

New:

- Refactored ``FolderContentsView`` to allow easy overwriting of options.
  [Gagaro]

Fixes:

- Fixed vocabulary item path to remove ``INavigationRoot`` path.
  [petschki]

- Fixed the actions to allow unicode in titles.
  [Gagaro]



3.0.12 (2015-09-20)
-------------------

- Require cmf.ModifyPortalContent for content_status_history
  [vangheem]

- Pull typesUseViewActionInListings settings from registry.
  [esteele]


3.0.11 (2015-09-12)
-------------------

- Fix tests: API usage to get default page in order to prevent side effects in
  other tests.
  [jensens]


3.0.10 (2015-09-07)
-------------------

- Display results of delete_confirmation_info in delete_confirmation and
  fc-delete to warn about linkintegrity-breaches.
  [bloodbare, vangheem, pbauer]


3.0.9 (2015-08-21)
------------------

- Respect view-action (e.g. for files and image) in rename, copy and cut.
  Fixes https://github.com/plone/Products.CMFPlone/issues/829
  [pbauer]


3.0.8 (2015-08-20)
------------------

- Added basic test for folder contents "rearrange" and "item order" features.
  Minor restructuring of actions in own files to have a consistent structure
  (bbb imports in place). Minor changes in touched area regarding pep8,
  code-analysis, et al.
  [jensens]

- Do not setDefaultPage in rename handler, there is already an subscriber that
  do so in `Products.CMFDynamicViewFTI`.
  [jensens]

- Do not clear clipboard when pasting content
  [vangheem]

- Fix i18n of '"title" has already been deleted'.

- When clicking cancel on the delete_confirmation got to the view_url.
  [ale-rt]

- Fix deletion of objects with unicode charaters in the title.
  [cillianderoiste]


3.0.7 (2015-07-18)
------------------

- Remove IFolderContentsViewletManager and IContentsPage as it's
  not used in Plone 5 anymore.
  [vangheem]

- Change "Workflow" to "State" in folder contents
  [vangheem]

- provide "no" button to delete on folder contents
  [vangheem]

- add portal_type to context info for folder contents pattern as it needs that data
  [hgarus]

- Give a decent error when ordering is not supported on a folder.
  [vangheem]

- Update folder contents integration to be able to work in a way where
  button actions can be provided by add-on products
  [vangheem]

- Make the ``@@fileUpload`` to not be guarded by the AddPortalContent
  permission, and instead do that check in code, so we can return better
  error message
  [frapell]

- Let ``@@getVocabulary`` return the vocabulary's value instead of the token
  for the id in the result set. The token is binary encoded and leads to
  encoding errors when selecting a value with non-ASCII data from vocabulary
  list in a select2 based widget.
  Fixes: https://github.com/plone/Products.CMFPlone/issues/650
  [thet]


3.0.6 (2015-06-05)
------------------

- remove context class from cancel button on select_default_page fixes https://github.com/plone/Products.CMFPlone/issues/577
  [vangheem]

- Fixes issue #584 in plone/Products.CMFPlone.
  [fulv]

- use 'as' syntax for exception
  [frentin]


3.0.5 (2015-05-11)
------------------

- Removed CMFDefault dependency
  [tomgross]

- Ensure that content is not deleted by acquisition when the delete action is
  used from a context that has already been deleted.  Provide tests to catch
  regressions (see https://github.com/plone/Products.CMFPlone/issues/383)
  [cewing]

3.0.4 (2015-05-04)
------------------

- add plone.protect as a dependency
  [vangheem]

- provide _authenticator token on old style createObject factory views
  [vangheem]

- Solving https://github.com/plone/Products.CMFPlone/issues/440
  [aleix]

- Translate folder contents add menu
  [vangheem]

- use same columns title in results and in displayed colums configuration
  [vincent]


3.0.3 (2015-03-26)
------------------

- pep8, flake8, utf8-headers et al cleanup.
  [jensens]

- refactored ``p.a.c.namechooser.NormalizingNameChooser._getCheckId`` to not
  use lambdas.
  [jensens]

3.0.2 (2015-03-13)
------------------

- Fix a few minor issues on folder_constraintypes_form.
  [fulv]

- Add ``id`` to available columns of the ``folder_contents`` view.
  [thet]

- fix json responses to be able to handle datetime objects and Missing.Value
  [vangheem]

- Keep default_page when renaming objects.
  [pbauer]

- Use INameChooser for new id when renaming objects using folder_rename or
  object_rename. Fix https://github.com/plone/plone.app.dexterity/issues/73
  [pbauer]

- Allow folderish types as default_page as long as users cannot add content
  to them.
  [pbauer]

- fix removing tags with non-ascii characters in folder_contents
  [petschki]

3.0.1 (2014-10-23)
------------------

- PLIP 13260: add browser views for ``select_default_page`` and
  ``select_default_view``.
  [saily]

- PLIP 13260: convert ``delete_confirmation``, ``folder_rename`` and
  ``object_rename`` into z3c.forms.
  [saily]

- PLIP 13260: Migration cut, copy and paste into browser views and add
  tests for that.
  [saily]

- Pass ``REQUEST`` into ``manage_delObjects`` method to support
  ``plone.app.linkintegrity`` checks.
  [saily]

- Ported tests to plone.app.testing
  [tomgross]

- PEP8
  [tomgross]

3.0.0 (2014-04-13)
------------------

- Bump Plone 5 branch to 3.0
  [esteele]

- PLIP 13260 add browser views for ``select_default_page`` and
   ``select_default_view``.
   [saily]


2.2.0 (2014-03-01)
------------------

- PLIP #13705: Remove <base> tag.
  [frapell]

- Fix constrainttypes form.
  [davisagli]

- Move content_status_history from CMFPlone to a browser view in this package.
  [bloodbare]

- Protect the folder constraintypes form with the 'Modify constrain types'
  permission.
  [davisagli]

- Fix tests for Plone 5 where the PLONE_FIXTURE layer does not provide
  content types any longer.
  [timo]

- Allow modifying the pagesize by adding a request-string e.g. "?pagesize=100".
  [pbauer]

- Use PLONE_APP_CONTENTTYPES_FIXTURE as testing base layer because
  ATContentTypes have been removed from PLONE_FIXTURE and some tests require
  content types.
  [timo]

- New folder contents implementation based on mockup
  [vangheem]


2.1.3 (2013-08-13)
------------------

- Fix translations of selectable restriction-options.
  [pbauer]


2.1.2 (2013-05-26)
------------------

- PEP8 cleanup.
  [timo]

- Added missing i18n markup to table.pt.
  [jianaijun]


2.1.1 (2013-04-06)
------------------

- Load folder_contents.js from the portal root instead of the context.
  [maurits]

- In the folder_contents view, assume a folderish context and set the base tag
  with a trailing slash. Fixes https://dev.plone.org/ticket/13487
  [danjacka]


2.1 (2013-03-05)
----------------

- show a warning message on the folder contents view when
  the default page is also a folder, that in order to add items
  to the default page's folder, they'll need to visit it's
  folder_contents view. also addresses https://dev.plone.org/ticket/9057
  [vangheem]

- on the folder_contents view, show the add menu for the
  context object always. This fixes the issue when the
  default view of a folder is also a folder and you
  can not add items to it. fixes https://dev.plone.org/ticket/9057
  [vangheem]


2.1a2 (2012-10-16)
------------------

- Remove KSS dependency from AJAX table views.
  [cah190]

- In table.pt use sequence_length to get batch size.
  [cah190]


2.1a1 (2012-06-29)
------------------

- Adjust table.pt TAL to work after the TAL engine became a bit stricter
  about only allowing path expressions within string expressions.
  [davisagli]

- Remove hard dependency on ATContentTypes.
  [davisagli]

- Clarify which item is the default view for the folder in the folder
  contents view.
  [rossp]

- Use plone.batching for all batches (PLIP #12235)
  [tom_gross]


2.0.9 (2012-04-15)
------------------

- In table.pt allow properly sorting on modification date, by adding a
  class like sortabledata-2012-04-03-10-37-27.
  [maurits]


2.0.8 (2012-03-06)
------------------

- Namechooser: Attempt to return an id with timestamp before returning a
  value error after 100 id check attempts.
  [eleddy]

- Namechooser: Pass the parent object to the Plone check_id script so
  it can detect duplicates.

- Namechooser: Use the Zope ObjectManager _checkId method to check
  new ids when possible, to avoid errors when adding invalid
  ids not caught by the old check. This fixes
  http://code.google.com/p/dexterity/issues/detail?id=244
  [davisagli]


2.0.7 (2011-07-04)
------------------

- Replace links to .../@@folder_contents by links to .../folder_contents
  so that 'Content' tab remains selected after a folder action.
  This fixes http://dev.plone.org/plone/ticket/10122.
  [thomasdesvenain]

- Add brain in dict returned by ``folderitems`` method of
  the ``FolderContentsTable`` for items not part of the currently
  visible batch as well.
  [mj]


2.0.6 (2011-05-02)
------------------

- Add brain in dict returned by ``folderitems`` method
  of ``FolderContentsTable`` class to ease customisation.
  [gotcha]

- Add MANIFEST.in.
  [WouterVH]

- Fixed state title in folder contents.
  [thomasdesvenain]


2.0.5 - 2011-04-06
------------------

- Fix display of title in folder contents table.
  [elro]


2.0.4 - 2011-04-04
------------------

- Reduce the required table item keys to ``id`` or ``getId``.
  [elro]

- Make all columns other than title optional in table view.
  [elro]

- It is the portal_type that is listed in `typesUseViewActionInListings`.
  [elro]


2.0.3 - 2011-03-15
------------------

- Preserve filename extension when picking a unique name.
  [elro]

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]


2.0.2 - 2010-12-23
------------------

- Avoid using a mutable default argument in the FolderContentsTable code. In a
  LinguaPlone environment after viewing the folder contents of a collection,
  the language of that collection got stuck as a content filter and wasn't
  reset anymore. Viewing the folder contents of any item in a different
  language showed an empty table until the Zope instance was restarted.
  [tom_gross, hannosch]

- Use the folder as the factory expression context when a front-page
  is used as the display for the folder. Tests in `plone.app.contentmenu`.
  [rossp]


2.0.1 - 2010-07-18
------------------

- Update license to GPL version 2 only.
  [hannosch]


2.0 - 2010-07-01
----------------

- Fetch the folder contents view icon more directly.
  [davisagli]


2.0b5 - 2010-05-01
------------------

- Speed up folder contents view by only creating the necessary data for
  items in the batch to be displayed.
  [witsch]

- Disable KSS updates for "select all" and "show all items/batched" in
  "folder contents" view as they are broken for folders with lots of content.
  [witsch]


2.0b4 - 2010-04-08
------------------

- Slight reconfiguration of the order of the folder_contents table;
  dragging is now in the first column, and visually much improved.
  [limi]

- Fixing possibly our #1 integrator issue, where do you find the template
  that corresponds to the folder_contents URL? Grep gives you nothing, since
  this was renamed to foldercontents.pt in the 3.x series. Renamed it back to
  folder_contents.pt, and adjusted the ZCML accordingly.
  [limi]

- Removed unused template foldercontents_table.pt. We have been using table.pt
  for ~2 years, it's time to kill it off.
  [limi]


2.0b3 - 2010-03-05
------------------

- Only display batching controls if we have more than the batch size number of
  elements. Fixes http://dev.plone.org/plone/ticket/10281
  [esteele]

- Adapt tests to new policy introduced in
  http://dev.plone.org/plone/changeset/34375
  References http://dev.plone.org/plone/ticket/10236
  [tomster]


2.0b2 - 2010-02-18
------------------

- Use non-skins versions of `isExpired` and `pretty_title_or_id` to speed
  up the `folder_contents` view a bit.
  [witsch]

- Updated templates to follow the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981
  [spliter]

- Mixed in Acquisition.Implicit back into the CMFAdding class. CMF skins depend
  on it inside templates. This closes http://dev.plone.org/plone/ticket/9865.
  [hannosch]

- Added test for adding view and Acquisition interaction. This references
  http://dev.plone.org/plone/ticket/9865.
  [hannosch]


2.0b1 - 2010-01-25
------------------

- Move logic for deciding source of folder contents listing to a new function
  so the FolderContentsTable view is useful as a base for subclasses.
  [MatthewWilkes]


2.0a3 - 2009-12-27
------------------

- Removed no longer required _getCharset handling from the name chooser. Plone
  only supports utf-8 as a database encoding.
  [hannosch]

- Use the getIconExprObject method of the FTI instead of the deprecated
  getIcon method.
  [hannosch]

- Fixed package dependencies and prefer Acquisition-less BrowserView.
  [hannosch]

- Introduce a new marker interface IContentsPage noting that the current
  request is showing the folder contents page.
  [hannnosch]


2.0a2 - 2009-12-02
------------------

- Fixed a unicodedecodeerror in foldercontents.py. Closes #9853
  [wigwam]

- Templates were updated to a new way of disabling the columns via a REQUEST
  variable.
  [spliter]


2.0a1 - 2009-11-14
------------------

- Avoid zope.app dependencies.
  [hannosch]

- folder_contents view used the same msgid for two different messages.
  Fixed that. This closes http://dev.plone.org/plone/ticket/9634
  [vincentfretin]

- Removed deprecated use of is_folderish script.
  [davisagli]

- Added support for the new add_view_expr property available on FTIs. This
  can be used to construct a URL for add views.
  [optilude]

- Removed PortalContent.__init__ call including an id argument from Item, as
  there's no base class which accepts this argument.
  [hannosch]

- Added package dependencies.
  [hannosch]


1.7 - 2010-04-07
----------------

- Fixed serious regression introduced in c31433. You cannot pass encoded
  strings into Message mappings.
  [hannosch]


1.6 - 2010-03-01
----------------

- Make the folder contents listing fall back to using the portal_type id when
  the title is not available (e.g. if the portal_type is missing).
  [davisagli]

- Fixed erroneous tfooter tag in table.pt (used in folder contents). It should
  be tfoot, not tfooter.
  [limi]

- Fixed not translatable message in table.pt: "Select ${title}"
  appears when the mouse is over a checkbox in folder_contents.
  [vincentfretin]

- Fixed folder_add_settings_long default message, it used "context"
  instead of "here".
  [vincentfretin]


1.5 - 2009-05-16
----------------

- Correct detection if an item in the review list is folderish.
  Partially fixes http://dev.plone.org/plone/ticket/8926
  [csenger]

- Add authenticator token to full_review_list form.
  Partially fixes http://dev.plone.org/plone/ticket/8926
  [csenger]

- Translate the name of the content types in full_review_list,
  add tests. This fixes http://dev.plone.org/plone/ticket/9164
  [csenger]


1.4 - 2009-03-04
----------------

- Changed the folder contents tables to deal properly with the Acquisition
  context of self.context. In Five's browser views, you need to do
  aq_inner(self.context). This closes
  http://dev.plone.org/plone/ticket/7686.

- Made the tests less fragile in regard to browser errors.
  [hannosch]

- Translate the name of the content types in folder_contents.
  Fixes http://dev.plone.org/plone/ticket/8459
  [csenger]

- Made the tests less fragile in regard to browser errors.
  [hannosch]

- Fixed folder contents tests, which tried to remove a no longer existing
  portlet assignment.
  [hannosch]

- Small cleanup and removed hard-dependency on KSS.
  [hannosch]

- Added missing i18n markup to batching.pt. This closes
  http://dev.plone.org/plone/ticket/8501
  [dunlapm]

- Fixed content type name for items in folder_contents when you hover any.
  Closes http://dev.plone.org/plone/ticket/8223
  [spliter]

- Fixed title and description for non AT content in folder_contents where
  widget method was acquired from parent AT content.
  [elro]


1.3 - 2008-07-07
----------------

- Use the widget itself to render the title and description and include the
  usual viewlet managers around the title.
  [wichert]

- Fixed i18n markup in table.pt.
  [naro]


1.2 - 2008-04-22
----------------

- Added authenticator token for CSRF protection.
  [witsch]

- Fix invalid leading space in all 'Up to Site Setup' links.
  [wichert]


1.1.1 - 2008-03-24
------------------

- Improved the batch disabling action so that it only shows up
  when there is a batch.
  [jvloothuis]

- Made the reviewlist more powerful by making the folder contents
  selection features available for it as well.
  [jvloothuis]

- Changed the replacement command to actually replace the div, not
  just its inner content. This fixes a problem with browsers like
  Internet Explorer which did not apply the drag and drop script
  after updating.
  [jvloothuis]

- Fixed i18n markup in table.pt.
  [hannosch]


1.1.0 - 2008-03-08
------------------

- Made it possible to show all the items in the folder contents at
  once (no batching). This can be used to drag items across batch
  boundaries and makes it easier to move an item from the end of
  the folder to the beginning.
  [jvloothuis]

- Update the folder_factories view to add the FTI id to the output of
  of addable_types. This makes it possible for callers to manipulate its
  results.
  [wichert]

- Fixed the 'id' attribute of CMFAdding class. By default, it is an
  empty string, which confuses absolute_url() and causes the <base />
  tag to be set incorrectly. This in turn confuses KSS, and probably
  other things.
  [optilude]


1.0 - 2007-08-16
----------------

- Fixed missing i18n markup on the folder contents view.
  [hannosch]
