=============
Basic content
=============

plone.app.content provides some helper base classes for content. Here are
some simple examples of using them.
.. code-block:: python

    >>> from plone.app.content import container, item

Let us define two fictional types, a folderish one and a non-folderish one.
We should define factories for these types as well. Factories can be
referenced from CMF FTI's, and also from <browser:addMenuItem /> directives.
With an appropriate add view (e.g. using formlib's AddForm) this will be
available from Plone's "add item" menu. Factories are registered as named
utilities.

Note that we need to define a portal_type to keep CMF happy.
.. code-block:: python

    >>> from zope.interface import implements, Interface
    >>> from zope import schema
    >>> from zope.component.factory import Factory

First, a container:
.. code-block:: python

    >>> class IMyContainer(Interface):
    ...     title = schema.TextLine(title=u"My title")
    ...     description = schema.TextLine(title=u"My other title")

    >>> class MyContainer(container.Container):
    ...     implements(IMyContainer)
    ...     portal_type = "My container"
    ...     title = u""
    ...     description = u""

    >>> containerFactory = Factory(MyContainer)

Then, an item:
.. code-block:: python

    >>> class IMyType(Interface):
    ...     title = schema.TextLine(title=u"My title")
    ...     description = schema.TextLine(title=u"My other title")

    >>> class MyType(item.Item):
    ...     implements(IMyType)
    ...     portal_type = "My type"
    ...     title = u""
    ...     description = u""

    >>> itemFactory = Factory(MyType)

We can now create the items.
.. code-block:: python

    >>> container = containerFactory("my-container")
    >>> container.id
    'my-container'
    >>> container.title = "A sample container"

We need to add it to an object manager for acquisition to do its magic.
.. code-block:: python

    >>> newid = self.portal._setObject(container.id, container)
    >>> container = getattr(self.portal, newid)

We will add the item directly to the container later.
.. code-block:: python

    >>> item = itemFactory("my-item")
    >>> item.id
    'my-item'
    >>> item.title = "A non-folderish item"

Note that both the container type and the item type are contentish. This is
important, because CMF provides event handlers that automatically index
objects that are IContentish.
.. code-block:: python

    >>> from Products.CMFCore.interfaces import IContentish
    >>> IContentish.providedBy(container)
    True
    >>> IContentish.providedBy(item)
    True

Only the container is folderish, though:
.. code-block:: python

    >>> from Products.CMFCore.interfaces import IFolderish
    >>> bool(container.isPrincipiaFolderish)
    True
    >>> IFolderish.providedBy(container)
    True
    >>> bool(item.isPrincipiaFolderish)
    False
    >>> IFolderish.providedBy(item)
    False

We can use the more natural Zope3-style container API, or the traditional
ObjectManager one.
.. code-block:: python

    >>> container['my-item'] = item
    >>> 'my-item' in container
    True
    >>> 'my-item' in container.objectIds()
    True
    >>> del container['my-item']
    >>> 'my-item' in container
    False
    >>> container._setObject('my-item', item)
    'my-item'
    >>> 'my-item' in container
    True

Both pieces of content should have been cataloged.
.. code-block:: python

    >>> container = self.portal['my-container']
    >>> item = container['my-item']

    >>> from Products.CMFCore.utils import getToolByName
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> [b.Title for b in catalog(getId = 'my-container')]
    ['A sample container']
    >>> [b.Title for b in catalog(getId = 'my-item')]
    ['A non-folderish item']

If we modify an object and trigger a modified event, it should be updated.
.. code-block:: python

    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> from zope.event import notify

    >>> container.title = "Updated title"
    >>> item.title = "Also updated title"

    >>> [b.Title for b in catalog(getId = 'my-container')]
    ['A sample container']
    >>> [b.Title for b in catalog(getId = 'my-item')]
    ['A non-folderish item']


    >>> notify(ObjectModifiedEvent(container))
    >>> notify(ObjectModifiedEvent(item))

    >>> [b.Title for b in catalog(getId = 'my-container')]
    ['Updated title']
    >>> [b.Title for b in catalog(getId = 'my-item')]
    ['Also updated title']
