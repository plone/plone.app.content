from zope import interface
from plone.app.content.interfaces import IBatch

class Batch(object):
    interface.implements(IBatch)

    def __init__(self, items, pagesize=20, pagenumber=1, navlistsize=5):
        self.items = items
        self.pagesize = pagesize
        self.pagenumber = pagenumber
        self.navlistsize = navlistsize

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        start = (self.pagenumber-1) * self.pagesize
        end = start + self.pagesize
        return self.items[start:end].__iter__()

    @property
    def size(self):
        return len(self)

    @property
    def firstpage(self):
        return 1

    @property
    def lastpage(self):
        pages = self.size / self.pagesize
        if self.size % self.pagesize:
            pages += 1
        return pages

    @property
    def items_not_on_page(self):
        items_on_page = list(self)
        return [item for item in self.items if item not in
                items_on_page]

    @property
    def multiple_pages(self):
        return bool(self.size / self.pagesize)

    @property
    def has_next(self):
        return (self.pagenumber * self.pagesize) < self.size

    @property
    def has_previous(self):
        return self.pagenumber > 1

    @property
    def previouspage(self):
        return self.pagenumber - 1

    @property
    def nextpage(self):
        return self.pagenumber + 1

    @property
    def next_item_count(self):
        nextitems = self.size - (self.pagenumber * self.pagesize)
        if nextitems > self.pagesize:
            return self.pagesize
        return nextitems

    @property
    def navlist(self):
        start = self.pagenumber - (self.navlistsize / 2)
        if start < 1:
            start = 1
        end = start + self.navlistsize - 1
        if end > self.lastpage:
            end = self.lastpage

        return range(start, end+1)

    @property
    def show_link_to_first(self):
        return 1 not in self.navlist

    @property
    def show_link_to_last(self):
        return self.lastpage not in self.navlist

    @property
    def second_page_not_in_navlist(self):
        return 2 not in self.navlist

    @property
    def islastpage(self):
        return self.lastpage == self.pagenumber

    @property
    def previous_pages(self):
        return self.navlist[:self.navlist.index(self.pagenumber)]

    @property
    def next_pages(self):
        return self.navlist[self.navlist.index(self.pagenumber)+1:]

    @property
    def before_last_page_not_in_navlist(self):
        return (self.lastpage - 1) not in self.navlist

    @property
    def items_on_page(self):
        if self.islastpage:
            remainder = self.size % self.pagesize
            if remainder == 0:
                return self.pagesize
            else:
                return remainder
        else:
            return self.pagesize
