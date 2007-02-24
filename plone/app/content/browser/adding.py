from Products.Five.browser.adding import ContentAdding

class CMFAdding(ContentAdding):
    """An adding view with a less silly next-url
    """
    
    def nextURL(self):
        return "%s/%s/view" % (self.context.absolute_url(), self.contentName)