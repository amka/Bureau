# MIT License
#
# Copyright (c) 2023 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT

import sys

import gi
import inject

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Goa', '1.0')
gi.require_version('Gom', '1.0')

from gi.repository import Gio, Adw

from .window import BureauWindow
from bureau.providers.account import AccountProvider
from bureau.providers.app_state import AppStateProvider
from bureau.providers.imap import ImapProvider


def configure_providers(binder: inject.Binder):
    binder.bind(ImapProvider, ImapProvider('imap.yandex.ru'))
    binder.bind(AccountProvider, AccountProvider())
    binder.bind(AppStateProvider, AppStateProvider())


class BureauApplication(Adw.Application):
    """The main application singleton class."""

    version: str

    def __init__(self, version: str):
        super().__init__(application_id='com.tenderowl.bureau',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self.version = version

        inject.configure(configure_providers)

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = BureauWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Bureau',
                                application_icon='com.tenderowl.bureau',
                                developer_name='TenderOwl',
                                version=self.version or '0.1.0',
                                developers=['Andrey Maksimov'],
                                copyright='© 2023 TenderOwl')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version: str):
    """The application's entry point."""
    app = BureauApplication(version)
    return app.run(sys.argv)
