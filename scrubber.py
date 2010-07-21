#!/usr/bin/env python

from __future__ import division

import os
import sys

assert sys.version_info >= (2, 3), "Install Python 2.3 or greater"

from threading import Event

import gtk
import gobject

from GUI.GUI import *

# XXX: This needs scrubedec! Where is scrubdec?!
#from scrub.jpeg import scrub_jpeg
from scrub.png import scrub_png
from scrub.tiff import scrub_tiff

class MainWindow(Window):

    def __init__(self, parent=None):
        Window.__init__(self)
        if parent is None:
            self.mainwindow = self # temp hack to make modal win32 file choosers work
        else:
            self.mainwindow = parent # temp hack to make modal win32 file choosers work
        self.connect('destroy', self.quit)
        self.set_title('FreeScrub')
        self.set_border_width(SPACING)
        self.resize(400,600)

        self.set_position(gtk.WIN_POS_CENTER)

        right_column_width=276
        self.box = gtk.VBox(spacing=SPACING)

        self.table = gtk.Table(rows=3,columns=2,homogeneous=False)
        self.table.set_col_spacings(SPACING)
        self.table.set_row_spacings(SPACING)
        y = 0

        # file list
        self.table.attach(lalign(gtk.Label('Scrub the following files:')),
                          0,2,y,y+1, xoptions=gtk.FILL, yoptions=gtk.FILL, )
        y+=1

        self.file_store = gtk.ListStore(gobject.TYPE_STRING)

        for i in range(4): self.file_store.append(('foo',))

        self.file_scroll = gtk.ScrolledWindow()
        self.file_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.file_scroll.set_shadow_type(gtk.SHADOW_IN)
        self.file_scroll.set_size_request(-1, SPACING)
        self.file_scroll.set_border_width(SPACING)

        self.file_list = gtk.TreeView(self.file_store)
        r = gtk.CellRendererText()
        column = gtk.TreeViewColumn(' _Files', r, text=0)
        self.file_list.append_column(column)
        self.file_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        file_list_height = self.file_list.size_request()[1] + SCROLLBAR_WIDTH
        self.file_store.clear()

        self.file_scroll.set_size_request(-1, file_list_height)
        self.file_scroll.add(self.file_list)
        self.table.attach(self.file_scroll,0,2,y,y+1,yoptions=gtk.EXPAND|gtk.FILL)
        y+=1

        self.file_list_button_box = gtk.HBox(homogeneous=True,spacing=SPACING)
        self.add_button = gtk.Button("Add Files")
        self.add_button.connect('clicked', self.choose_files)
        self.file_list_button_box.pack_start(self.add_button)
        self.remove_button = gtk.Button(stock=gtk.STOCK_REMOVE)
        self.remove_button.connect('clicked', self.remove_selection)
        self.remove_button.set_sensitive(False)
        self.file_list_button_box.pack_start(self.remove_button)
        self.clear_button = gtk.Button(stock=gtk.STOCK_CLEAR)
        self.clear_button.connect('clicked', self.clear_file_list)
        self.clear_button.set_sensitive(False)
        self.file_list_button_box.pack_start(self.clear_button)
        self.table.attach(self.file_list_button_box,0,2,y,y+1,
                          xoptions=gtk.FILL, yoptions=0)
        y+=1

        self.box.pack_start(self.table, expand=True, fill=True)

        self.buttonbox = gtk.HBox(homogeneous=True, spacing=SPACING)

        self.quitbutton = gtk.Button('_Close', stock=gtk.STOCK_QUIT)
        self.quitbutton.connect('clicked', self.quit)
        self.buttonbox.pack_start(self.quitbutton, expand=True, fill=True)

        self.buttonbox.pack_start(gtk.Label(''), expand=True, fill=True)

        self.makebutton = IconButton('Scrub', stock=gtk.STOCK_EXECUTE)
        self.makebutton.connect('clicked', self.make)
        self.makebutton.set_sensitive(False)
        self.buttonbox.pack_end(self.makebutton, expand=True, fill=True)

        self.box.pack_end(self.buttonbox, expand=False, fill=False)

        self.file_store.connect('row-changed', self.check_buttons)
        sel = self.file_list.get_selection()
        sel.connect('changed', self.check_buttons)

        self.add(self.box)
        self.show_all()

    def remove_selection(self,widget):
        sel = self.file_list.get_selection()
        list_store, rows = sel.get_selected_rows()
        rows.reverse()
        for row in rows:
            list_store.remove(list_store.get_iter(row))

    def clear_file_list(self,widget):
        self.file_store.clear()
        self.check_buttons()

    def choose_files(self,widget):
        fn = None

        selector = OpenMultiFileSelection(self, title="Select files to scrub:",
                                fullname=fn,
                                got_multiple_location_func=self.add_files)

    def add_files(self, names):
        for name in names:
            name = u'' + name
            self.file_store.append((name,))
        torrent_dir = os.path.split(name)[0]
        if torrent_dir[-1] != os.sep:
            torrent_dir += os.sep

    def get_file_list(self):
        it = self.file_store.get_iter_first()
        files = []
        while it is not None:
            files.append(self.file_store.get_value(it, 0))
            it = self.file_store.iter_next(it)
        return files

    def make(self, widget):
        file_list = self.get_file_list()
        errored = False
        if not errored:
            d = ProgressDialog(self, file_list)
            d.main()

    def check_buttons(self, *widgets):
        file_list = self.get_file_list()
        if len(file_list) >= 1:
            self.makebutton.set_sensitive(True)
            self.clear_button.set_sensitive(True)
            sel = self.file_list.get_selection()
            list_store, rows = sel.get_selected_rows()
            if len(rows):
                self.remove_button.set_sensitive(True)
            else:
                self.remove_button.set_sensitive(False)
        else:
            self.clear_button.set_sensitive(False)
            self.remove_button.set_sensitive(False)
            self.makebutton.set_sensitive(False)

    def check_make_button(self, *widgets):
        a_list = self.get_url_list()
        file_list = self.get_file_list()
        if len(file_list) >= 1 and len(a_list) >= 1:
            self.makebutton.set_sensitive(True)
        else:
            self.makebutton.set_sensitive(False)

    def quit(self, widget):
        self.destroy()
        if __name__ == "__main__":
            gtk.main_quit()

class ProgressDialog(gtk.Dialog):

    def __init__(self, parent, file_list):
        gtk.Dialog.__init__(self, parent=parent, flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        self.set_size_request(400,-1)
        self.set_border_width(SPACING)
        self.set_title('FreeScrub')
        self.file_list = file_list
        self.flag = Event() # ???

        self.label = gtk.Label('Scrubbing Documents..')
        self.label.set_line_wrap(True)

        self.vbox.set_spacing(SPACING)
        self.vbox.pack_start(lalign(self.label), expand=False, fill=False)

        self.cancelbutton = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancelbutton.connect('clicked', self.cancel)
        self.action_area.pack_end(self.cancelbutton)

        self.show_all()

        self.done_button = gtk.Button(stock=gtk.STOCK_OK)
        self.done_button.connect('clicked', self.cancel)

    def main(self):
        self.complete()

    def cancel(self, widget=None):
        self.flag.set()
        self.destroy()

    def set_progress_value(self, value):
        self._update_gui()

    def set_file(self, filename):
        self.label.set_text('Scrubbing!\n')
        self._update_gui()

    def _update_gui(self):
        #while gtk.events_pending():
        gtk.main_iteration(block=False)

    def scrub(self):
        for file in self.file_list:
            type = file[-4::]
            if type == ".pdf" or type == ".PDF":
                #PDF Scrubbing
                print "PDF needs to be OOified"
            elif type == ".jpg" or type == "jpeg" or type == ".JPG" or type == "JPEG":
                #JPEG Scrubbing
                #scrub_jpeg(file, file)
                pass
            elif type == "tiff" or type == "TIFF":
                #TIFF Scrubbing
                scrub_tiff(file, file)
            elif type == ".png" or type == ".PNG":
                #PNG Scrub
                scrub_png(file, file)
            else:
                print "Unsupported filetype"

    def complete(self):
        try:
            self.scrub()
            if not self.flag.isSet():
                self.set_title('Done.')
                self.label.set_text('Done scrubbing!')
                self.set_progress_value(1)
                self.action_area.remove(self.cancelbutton)
                self.action_area.pack_start(self.done_button)
                self.done_button.show()
        except (OSError, IOError), e:
            self.set_title('Error!')
            self.label.set_text('Error scrubbing documents: ' + str(e))

def main(parent=None):
    w = MainWindow(parent)

if __name__ == '__main__':
    main()
    try:
        gtk.main()
    except KeyboardInterrupt:
        # gtk.mainloop not running
        # exit and don't save config options
        sys.exit(1)

