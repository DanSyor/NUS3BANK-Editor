# coding: utf-8
from __future__ import absolute_import, division, print_function
import pyLib.six as six
import pyLib.xis as xis
if six.PY3:
    from tkinter import *
    import tkinter.font as tkFont
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import tkFont
    import ttk


# colors for listbox elements
# color_l_default = u'black'
# color_l_change  = u'blue'
# color_l_bg = [u'white',u'#eeeeff']

# evenrow = u'evenrow'
# oddrow  = u'oddrow'
# linetag = [evenrow,oddrow]

class MultiListbox(object):
    
    def __init__(self, root, columns, padx=0, pady= 0):
        self.root=root
        self.columns = columns
        self.tree = None
        self._setup_widgets(padx,pady)
        self._sel_start_iid = 0
        self._sel_last_iid = 0
        self._items = []
        self._context_menu_v = Menu(root,bd=0)
        self._double_click_action_v = lambda e: ()
        self.linetags = []
    
    def _setup_widgets(self,padx,pady):
        # create a treeview with dual scrollbars
        container = ttk.Frame(self.root)

        self.tree = ttk.Treeview(container, columns=self.columns, show=u"headings")
        vsb = ttk.Scrollbar(container, orient=VERTICAL  , command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=RIGHT , fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        self.tree.pack(fill=BOTH, padx=padx, pady=pady, expand=1)
        container.pack(fill=BOTH, expand=1)
        
        # for i in range(len(linetag)):
            # self.tree.tag_configure(linetag[i],background=color_l_bg[i])

        self.tree.bind(u"<Button1-Motion>", self._selection)
        self.tree.bind(u"<Button-1>"      , self._selection_start)
        self.tree.bind(u"<Double-1>"      , self._double_click_action_f)
        self.tree.bind(u"<Button-3>"      , self._context_menu_f)
        # self.tree.bind('<Return>', self._print_sel)
        
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self._sort_column(_col, False))
            # adjust the column's width to the header string
            self.tree.column(col, width=tkFont.Font().measure(col))
    
    def tag_remove(self, tags, items='all'):
        if items == 'all':
            items = self.tree.get_children('')
        for item in items:
            old_tags = list(self.tree.item(item, tags=None))
            new_tags = []
            for tag in old_tags:
                if not tag in tags:
                    new_tags.append(tag)
            self.tree.item(item,tags=new_tags)
    
    def linetags_set(self, linetags=u'default'):
        self.tag_remove(self.linetags)
        if linetags != u'default':
            self.linetags = linetags
        if self.linetags:
            i = 0
            for item in self.tree.get_children(''):
                tags = list(self.tree.item(item,tags=None))
                tags.append(linetags[i%len(linetags)])
                i+=1
                self.tree.item(item,tags=tags)
                
    def tag_configure(self,tag,foreground='',background='',font='',image=''):
        self.tree.tag_configure(tag,foreground=foreground,background=background,font=font,image=image)
        
    def tag_set(self,items,tags):
        if items == 'all':
            items = self.tree.get_children('')
        if tags:
            for item in items:
                o_tags = list(self.tree.item(item,tags=None))
                for tag in tags:
                    o_tags.append(tag)
                self.tree.item(item,tags=o_tags)
    
    def _context_menu_f(self,event):
        try:
            id = self.tree.identify_row(event.y)
        except IndexError:
            return
        if id == '':
            return
        if not id in self.tree.selection():
            self.selectAll()
            self.invertSelection()
            self.tree.selection_add(id)
        self._context_menu_v.post(event.x_root,event.y_root)
        
    def set_context_menu(self, menu):
        self._context_menu_v = menu
    
    def _double_click_action_f(self,event):
        if self.on_item(event):
            self._double_click_action_v(event)
    
    def set_double_click_action(self, action):
        self._double_click_action_v = action
    
    def insert(self, index, item):
        if self.linetags:
            iid = self.tree.insert('',index,values=item,tags=[self.linetags[len(self.tree.get_children(''))%len(self.linetags)]])
        else:
            iid = self.tree.insert('',index,values=item)
        self._items.append(iid)
        for i,v in enumerate(item):
            vWidth = tkFont.Font().measure(v)
            # print(i)
            # print (str(v)+' '+str(vWidth) +' | Col '+str(self.tree.column(self.columns[i],width=None)))
            if self.tree.column(self.columns[i],width=None) < vWidth:
                self.tree.column(self.columns[i],width=vWidth)
        # print(type(self.tree.item(iid,tags=None)))
        return iid
    
    def on_item(self,event):
        try:
            id = self.tree.identify_row(event.y)
        except IndexError:
            return ''
        # if id == '':
            # return ''
        return id
        
    def _sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        # print (l)
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
            # print(u'ints!')
        except:
            try:
                l.sort(key=lambda t: int(t[0],16), reverse=reverse)
                # print('hex!')
            except:
                l.sort(reverse=reverse)
                # print(u'strings...')

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # reverse sort order for next sort
        self.tree.heading(col, command=lambda _col=col: self._sort_column(_col, not reverse))
        # reset sort order in other columns
        for col2 in self.columns:
            if col != col2:
                self.tree.heading(col2, command=lambda _col=col2: self._sort_column(_col, False))
        
        # reset row tags
        self.linetags_set()
                
    def _selection_start(self,event):
        self._sel_start_iid = self.on_item(event)
        self._sel_last_iid  = self._sel_start_iid
        
    def _selection(self, event):
        if self._sel_start_iid == '':
            return
        id = self.on_item(event)
        if id == '':
            return
        # print('ID: '+id)
        # print('Position: '+str(l.index(id)))
        if id == self._sel_last_iid:
            return
        l = self.tree.get_children('')
        id_cur = l.index(id)
        id_pre = l.index(self._sel_last_iid)
        id_ini = l.index(self._sel_start_iid)
        if id_cur > id_ini:
            if id_cur > id_pre:
                for x in range(id_ini,id_cur+1):
                    self.tree.selection_add(l[x])
            else:
                for x in range(id_cur+1,id_pre+1):
                    self.tree.selection_remove(l[x])
        elif id_cur < id_ini:
            if id_cur < id_pre:
                for x in range(id_cur,id_ini+1):
                    self.tree.selection_add(l[x])
            else:
                for x in range(id_pre,id_cur):
                    self.tree.selection_remove(l[x])
        else: # id = _sel_start_iid
            if id_cur < id_pre:
                for x in range(id_cur+1,id_pre+1):
                    self.tree.selection_remove(l[x])
            else:
                for x in range(id_pre,id_cur):
                    self.tree.selection_remove(l[x])
            
        self._sel_last_iid = id
    
    def bind(self,config,fun):
        self.tree.bind(config,fun)
        
    def deleteAll(self):
        for item in self.tree.get_children(''):
            self.tree.delete(item)
        self._items = []
        
    def curselection(self):
        cursel = []
        itmsel = self.tree.selection()
        for i in range(len(self._items)):
            if self._items[i] in itmsel:
                cursel.append(i)
        return cursel
                
    def invertSelection(self):
        for item in self.tree.get_children(''):
            self.tree.selection_toggle(item)
            
    def selectAll(self):
        for item in self.tree.get_children(''):
            self.tree.selection_add(item)
            
    def focus_set(self):
        self.tree.focus_set()