from plone.i18n.normalizer import FILENAME_REGEX
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.i18n.normalizer.interfaces import IURLNormalizer
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.interface import implements

from Acquisition import aq_inner, aq_base
from zExceptions import BadRequest

from plone.app.content.interfaces import INameFromTitle
import time

ATTEMPTS = 100


class NormalizingNameChooser(object):
    """A name chooser for a Zope object manager.

    If the object is adaptable to or provides INameFromTitle, use the
    title to generate a name.
    """

    implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        return not self._getCheckId(object)(name, required=1)

    def chooseName(self, name, object):
        container = aq_inner(self.context)
        if not name:
            nameFromTitle = INameFromTitle(object, None)
            if nameFromTitle is not None:
                name = nameFromTitle.title
            if not name:
                name = getattr(aq_base(object), 'id', None)
            if not name:
                name = getattr(aq_base(object), 'portal_type', None)
            if not name:
                name = object.__class__.__name__

        if not isinstance(name, unicode):
            name = unicode(name, 'utf-8')

        request = getattr(object.__of__(container), 'REQUEST', None)
        if request is not None:
            name = IUserPreferredURLNormalizer(request).normalize(name)
        else:
            name = getUtility(IURLNormalizer).normalize(name)

        return self._findUniqueName(name, object)

    def _findUniqueName(self, name, object):
        """Find a unique name in the parent folder, based on the given id, by
        appending -n, where n is a number greater than 1, or just the id if
        it's ok.
        """
        check_id = self._getCheckId(object)

        if not check_id(name, required=1):
            return name

        ext = ''
        m = FILENAME_REGEX.match(name)
        if m is not None:
            name = m.groups()[0]
            ext = '.' + m.groups()[1]

        idx = 1
        while idx <= ATTEMPTS:
            new_name = "%s-%d%s" % (name, idx, ext)
            if not check_id(new_name, required=1):
                return new_name
            idx += 1

        # give one last attempt using the current date time before giving up
        new_name = "%s-%s%s" % (name, time.time(), ext)
        if not check_id(new_name, required=1):
            return new_name

        raise ValueError(
            "Cannot find a unique name based on %s after %d attemps." % (
                name,
                ATTEMPTS,
            )
        )

    def _getCheckId(self, object):
        """Return a function that can act as the check_id script.
        """
        parent = aq_inner(self.context)
        _check_id = getattr(object, 'check_id', None)
        if _check_id is not None:
            def do_Plone_check(id, required):
                return _check_id(id, required=required, contained_by=parent)
            check_id = lambda id, required: do_Plone_check(id, required)
        else:
            def do_OFS_check(parent, id):
                try:
                    parent._checkId(id)
                except BadRequest:
                    return True
            check_id = lambda id, required: do_OFS_check(parent, id)
        return check_id
