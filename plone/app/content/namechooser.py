import time

from Acquisition import aq_base, aq_inner
from plone.i18n.normalizer import FILENAME_REGEX
from plone.i18n.normalizer.interfaces import IURLNormalizer, IUserPreferredURLNormalizer
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.interface import implementer

from plone.app.content.interfaces import INameFromTitle

ATTEMPTS = 100


@implementer(INameChooser)
class NormalizingNameChooser:
    """A name chooser for a Zope object manager.

    If the object is adaptable to or provides INameFromTitle, use the
    title to generate a name.
    """

    def __init__(self, context):
        self.context = context

    def checkName(self, name, obj):
        return not self._getCheckId(obj)(name, required=1)

    def chooseName(self, name, obj):
        container = aq_inner(self.context)
        if not name:
            nameFromTitle = INameFromTitle(obj, None)
            if nameFromTitle is not None:
                name = nameFromTitle.title
            if not name:
                name = getattr(aq_base(obj), "id", None)
            if not name:
                name = getattr(aq_base(obj), "portal_type", None)
            if not name:
                name = obj.__class__.__name__

        if not isinstance(name, str):
            name = str(name, "utf-8")
            # name = name.encode('utf-8')

        request = getattr(obj.__of__(container), "REQUEST", None)
        if request is not None:
            name = IUserPreferredURLNormalizer(request).normalize(name)
        else:
            name = getUtility(IURLNormalizer).normalize(name)

        return self._findUniqueName(name, obj)

    def _findUniqueName(self, name, obj):
        """Find a unique name in the parent folder, based on the given id, by
        appending -n, where n is a number greater than 1, or just the id if
        it's ok.
        """
        check_id = self._getCheckId(obj)

        if not check_id(name, required=1):
            return name

        ext = ""
        m = FILENAME_REGEX.match(name)
        if m is not None:
            name = m.groups()[0]
            ext = "." + m.groups()[1]

        idx = 1
        while idx <= ATTEMPTS:
            new_name = "%s-%d%s" % (name, idx, ext)
            if not check_id(new_name, required=1):
                return new_name
            idx += 1

        # give one last attempt using the current date time before giving up
        new_name = f"{name}-{time.time()}{ext}"
        if not check_id(new_name, required=1):
            return new_name

        raise ValueError(
            "Cannot find a unique name based on %s after %d attemps."
            % (
                name,
                ATTEMPTS,
            )
        )

    def _getCheckId(self, obj):
        """Return a function that can act as the check_id script."""
        parent = aq_inner(self.context)
        # Check for a method or a skin script, like
        # Products/CMFPlone/skins/plone_scripts/check_id.py until Plone 5.1.
        _check_id = getattr(obj, "check_id", None)

        def do_Plone_check(newid, required):
            if _check_id is not None:
                return _check_id(newid, required=required, contained_by=parent)

            from Products.CMFPlone.utils import check_id

            return check_id(obj, newid, required=required, contained_by=parent)

        return do_Plone_check
