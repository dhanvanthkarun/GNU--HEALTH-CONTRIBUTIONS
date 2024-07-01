#########################################################################
#             GNU HEALTH HOSPITAL MANAGEMENT - GTK CLIENT               #
#                      https://www.gnuhealth.org                        #
#########################################################################
#       The GNUHealth HMIS client based on the Tryton GTK Client        #
#########################################################################
#
# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later
#
#
# This file is part of GNU Health.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import gettext
import os
from urllib.request import urlopen
from urllib.parse import unquote

from gi.repository import Gdk, Gtk

from gnuhealth.common import common
from gnuhealth.common import file_selection, Tooltips, file_open, file_write
from gnuhealth.common.entry_position import reset_position
from gnuhealth.gui.window.view_form.view.form_gtk.widget import Widget
from gnuhealth.gui.window.view_form.view.form import FormXMLViewParser

# The dicombinary widget is based on the existing binary widget of tryton.

# all plugins must have this function


def get_plugins(model):
    """
    Retrieve a list of plugins for the given model.
    """
    return []


def get_gettext():
    try:
        localedir = os.path.dirname(os.path.abspath(__file__)) + '/locale'
        lang = gettext.translation('dicombinary', localedir=localedir)
        return lang.gettext
    except Exception:
        return gettext.gettext


class DicomBinaryMixin(Widget):

    def __init__(self, view, attrs):
        """
        Initialize the DicomBinaryMixin.

        :param view: The view parameter.
        :param attrs: The attrs parameter.
        """
        super(DicomBinaryMixin, self).__init__(view, attrs)
        self.filename = attrs.get('filename')

    def toolbar(self):
        'Return HBox with the toolbar'
        hbox = Gtk.HBox(spacing=0)
        tooltips = Tooltips()
        _ = get_gettext()

        self.but_save_as = Gtk.Button()
        self.but_save_as.set_image(common.IconFactory.get_image(
            'gnuhealth-save', Gtk.IconSize.SMALL_TOOLBAR))
        self.but_save_as.set_relief(Gtk.ReliefStyle.NONE)
        self.but_save_as.connect('clicked', self.save_as)
        tooltips.set_tip(self.but_save_as, _('Save As...'))
        hbox.pack_start(self.but_save_as, expand=False, fill=False, padding=0)

        self.but_select = Gtk.Button()
        self.but_select.set_image(common.IconFactory.get_image(
            'gnuhealth-search', Gtk.IconSize.SMALL_TOOLBAR))
        self.but_select.set_relief(Gtk.ReliefStyle.NONE)
        self.but_select.connect('clicked', self.select)
        target_entry = Gtk.TargetEntry.new('text/uri-list', 0, 0)
        self.but_select.drag_dest_set(Gtk.DestDefaults.ALL, [
            target_entry,
        ],
            Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
        self.but_select.connect(
            'drag-data-received', self.select_drag_data_received)
        tooltips.set_tip(self.but_select, _('Select...'))
        hbox.pack_start(self.but_select, expand=False, fill=False, padding=0)

        self.but_clear = Gtk.Button()
        self.but_clear.set_image(common.IconFactory.get_image(
            'gnuhealth-clear', Gtk.IconSize.SMALL_TOOLBAR))
        self.but_clear.set_relief(Gtk.ReliefStyle.NONE)
        self.but_clear.connect('clicked', self.clear)
        tooltips.set_tip(self.but_clear, _('Clear'))
        hbox.pack_start(self.but_clear, expand=False, fill=False, padding=0)

        tooltips.enable()
        return hbox

    @property
    def filename_field(self):
        """
        Returns the value of the `filename` field from
        the `group` dictionary in the `record` object.
        """
        return self.record.group.fields.get(self.filename)

    @property
    def filters(self):
        """
        Get the list of filters to apply when selecting files.
        Return a list of Gtk.FileFilter objects.
        """
        _ = get_gettext()
        filter_all = Gtk.FileFilter()
        filter_all.set_name(_('All files'))
        filter_all.add_pattern("*")
        filter_dicom = Gtk.FileFilter()
        filter_dicom.set_name(_('DICOM files'))
        filter_dicom.add_pattern("*.dcm")
        filter_dicom.add_pattern("*.DCM")
        filter_dicom.add_pattern("*.zip")
        filter_dicom.add_pattern("*.gz")
        return [filter_dicom, filter_all]

    @property
    def preview(self):
        """
        Getter method for the 'preview' property.
        Returns a boolean value indicating if preview is enabled or not.
        """
        return False

    def update_buttons(self, value):
        """
        Updates the visibility of buttons based on the input value.
        """
        if value:
            # self.but_save_as.show()    # don't show "save as" button
            self.but_select.hide()
            self.but_clear.show()
        else:
            self.but_save_as.hide()
            self.but_select.show()
            self.but_clear.hide()

    def select(self, widget=None):
        """
        Selects files from the file system and sets their URIs.
        """
        _ = get_gettext()
        if not self.field:
            return
        filenames = file_selection(
            _('Select'),
            preview=self.preview,
            filters=self.filters,
            multi=True)
        if filenames:
            uris = ['file:///' + filename for filename in filenames]
            self._set_uris(uris)

    def select_drag_data_received(self, selection):
        """
        Handle the data received when an item is
        dragged and dropped onto the widget.
        """
        if not self.field:
            return
        self._set_uris(selection.get_uris())

    def _set_uris(self, uris):
        # put the data of all files (and the length of the files)
        # into a bytearray.
        # the format is:
        #   1. the bytes 'M', 'U', 'L', 'T' (ASCII 77,85,76,84)
        #   2. 8 bytes containing the length of the file (Little Endian)
        #   3. the data of the file
        #   4. repeat steps 2 and 3 for next file
        allData = bytearray([77, 85, 76, 84])
        for uri in uris:
            uri = unquote(uri)
            data = urlopen(uri).read()
            # size in little endian 8 bytes
            allData.extend(len(data).to_bytes(8, byteorder='little'))
            allData.extend(data)
        # set the content of the field in the wizard
        self.field.set_client(self.record, allData)
        if self.filename_field:
            self.filename_field.set_client(self.record, len(allData))

    def get_data(self):
        """
        A method to retrieve data from the field associated with the record.
        """
        if hasattr(self.field, 'get_data'):
            data = self.field.get_data(self.record)
        else:
            data = self.field.get(self.record)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return data

    def open_(self, widget=None):
        """
        Opens a file based on the given widget and filename.
        """
        if not self.filename_field:
            return
        filename = self.filename_field.get(self.record)
        if not filename:
            return
        file_path = file_write(filename, self.get_data())
        root, type_ = os.path.splitext(filename)
        if type_:
            type_ = type_[1:]
        file_open(file_path, type_)

    def save_as(self, widget=None):
        """
        Save the data as a file after prompting the user for a filename.
        """
        _ = get_gettext()
        filename = ''
        if self.filename_field:
            filename = self.filename_field.get(self.record)
        filename = file_selection(_('Save As...'),
                                  filename=filename,
                                  action=Gtk.FileChooserAction.SAVE)
        if filename:
            with open(filename, 'wb') as fp:
                fp.write(self.get_data())

    def clear(self, widget=None):
        """
        A description of the entire function,
        its parameters, and its return types.
        """
        if self.filename_field:
            self.filename_field.set_client(self.record, None)
        self.field.set_client(self.record, None)


# This is the dedicated widget for uploading DICOM files.
# It allows multiple selection. It can read the DICOM files,
# the zipped DICOM files (.zip, .gz)
class DicomBinary(DicomBinaryMixin, Widget):
    "DicomBinary"

    def __init__(self, view, attrs):
        """
        Initializes the DicomBinary class with the given view and attrs.

        Parameters:
            view: The view parameter.
            attrs: The attrs parameter.

        Returns:
            None
        """
        super(DicomBinary, self).__init__(view, attrs)

        self.widget = Gtk.HBox(spacing=0)
        self.wid_size = Gtk.Entry()
        self.wid_size.set_width_chars(self.default_width_chars)
        self.wid_size.set_alignment(1.0)
        self.wid_size.props.sensitive = False
        if self.filename and attrs.get('filename_visible'):
            self.wid_text = Gtk.Entry()
            self.wid_text.set_property('activates_default', True)
            self.wid_text.connect('focus-out-event',
                                  lambda x,
                                  y: self._focus_out())
            self.wid_text.connect_after('key_press_event', self.sig_key_press)
            self.wid_text.connect('icon-press', self.sig_icon_press)
            self.widget.pack_start(
                self.wid_text, expand=True, fill=True, padding=0)
        else:
            self.wid_text = None
        self.mnemonic_widget = self.wid_text
        self.widget.pack_start(
            self.wid_size, expand=not self.filename, fill=True, padding=0)

        self.widget.pack_start(
            self.toolbar(), expand=False, fill=False, padding=0)

    def _readonly_set(self, value):
        """
        Set the sensitivity of buttons and
        text widget based on the given value.
        """
        self.but_select.set_sensitive(not value)
        self.but_clear.set_sensitive(not value)
        if self.wid_text:
            self.wid_text.set_editable(not value)

    def sig_key_press(self, widget, event, *args):
        """
        Handle key press events and perform corresponding
        actions based on the event's key value and widget's editability.
        """
        editable = self.wid_text and self.wid_text.get_editable()
        if event.keyval == Gdk.KEY_F3 and editable:
            self.sig_new(widget)
            return True
        elif event.keyval == Gdk.KEY_F2:
            if self.filename:
                self.sig_open(widget)
            else:
                self.sig_save_as(widget)
            return True
        return False

    def sig_icon_press(self, widget, icon_pos):
        """
        This function handles the press event for the signal icon.
        It takes in the widget, icon position, and event as parameters.
        """
        widget.grab_focus()
        if icon_pos == Gtk.EntryIconPosition.PRIMARY:
            self.open_()

    def display(self):
        """
        Displays the DicomBinary object on the screen.
        """
        _ = get_gettext()
        super(DicomBinary, self).display()
        if not self.field:
            if self.wid_text:
                self.wid_text.set_text('')
            self.wid_size.set_text('')
            self.but_save_as.hide()
            return False
        if hasattr(self.field, 'get_size'):
            size = self.field.get_size(self.record)
        else:
            size = len(self.field.get(self.record))
        self.wid_size.set_text(common.humanize(size or 0))
        reset_position(self.wid_size)
        if self.wid_text:
            self.wid_text.set_text(self.filename_field.get(self.record) or '')
            reset_position(self.wid_text)
            if size:
                icon, tooltip = 'gnuhealth-open', _("Open...")
            else:
                icon, tooltip = None, ''
            pos = Gtk.EntryIconPosition.PRIMARY
            if icon:
                pixbuf = common.IconFactory.get_pixbuf(
                    icon, Gtk.IconSize.MENU)
            else:
                pixbuf = None
            self.wid_text.set_icon_from_pixbuf(pos, pixbuf)
            self.wid_text.set_icon_tooltip_text(pos, tooltip)
        self.update_buttons(bool(size))
        return True

    def set_value(self):
        """
        Sets the value of the filename field in the
        record based on the text entered in the wid_text field
        """
        if self.wid_text:
            self.filename_field.set_client(self.record,
                                           self.wid_text.get_text() or False)
        return


FormXMLViewParser.WIDGETS['dicombinary'] = DicomBinary
