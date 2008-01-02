from Products.Five.browser.adding import ContentAdding
from Products.CMFCore.utils import getToolByName

class CMFAdding(ContentAdding):
    """An adding view with a less silly next-url
    """
    
    # We need to do this to get proper traversal URLs - otherwise, the
    # <base /> tag is messed up.
    id = '+'
    
    def add(self, content):
        content = super(CMFAdding, self).add(content)
        
        # We need to ensure that we finish type construction, not at least
        # to set the correct permissions based on the workflow
        portal_types = getToolByName(content, 'portal_types')
        fti = portal_types.getTypeInfo(content)
        if fti is not None:
            fti._finishConstruction(content)
        
        return content
    
    def nextURL(self):
        return "%s/%s/view" % (self.context.absolute_url(), self.contentName)