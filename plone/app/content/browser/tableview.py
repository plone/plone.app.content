from zope.app.pagetemplate import ViewPageTemplateFile
from plone.app.content.batching import Batch

class Table(object):
    """   
    The table renders a table with sortable columns etc.

    It is meant to be subclassed to provide methods for getting specific table info.
    """                

    def __init__(self, request, base_url, view_url, items, show_sort_column=False,
                 buttons=[]):
        self.request = request
        self.context = None # Need for view pagetemplate

        self.base_url = base_url
        self.view_url = view_url
        self.url = view_url
        self.items = items
        self.show_sort_column = show_sort_column
        self.buttons = buttons

        selection = request.get('select')
        if selection == 'screen':
            self.selectcurrentbatch=True
        elif selection == 'all':
            self.selectall = True


    def set_checked(self, item):
        selected = self.selected(item)
        item['checked'] = selected and 'checked' or None
        item['table_row_class'] = item.get('table_row_class', '')
        if selected:
            item['table_row_class'] += ' selected'

    @property
    def batch(self):
        b = Batch(self.items,
                  pagenumber=int(self.request.get('pagenumber', 1)))
        map(self.set_checked, b)
        return b

    render = ViewPageTemplateFile("table.pt")
    batching = ViewPageTemplateFile("batching.pt")

    # options
    selectcurrentbatch = False
    _select_all = False

    def _get_select_all(self):
        return self._select_all

    def _set_select_all(self, value):
        self._select_all = bool(value)
        if self._select_all:
            self.selectcurrentbatch = True

    selectall = property(_get_select_all, _set_select_all)

    @property
    def show_select_all_items(self):
        return self.selectcurrentbatch and not self.selectall

    def get_nosort_class(self):
        """
        """
        return "nosort"

    @property
    def selectall_url(self):
        return self.selectnone_url+'&select=all'

    @property
    def selectscreen_url(self):
        return self.selectnone_url+'&select=screen'

    @property
    def selectnone_url(self):
        pagenumber = self.request.get('pagenumber', '1')
        return self.view_url+'?pagenumber=%s'%pagenumber

    def selected(self, item):
        if self.selectcurrentbatch:
            return True
        return False

    @property
    def viewname(self):
        return self.view_url.split('?')[0].split('/')[-1]
