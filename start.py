#!/usr/bin/env python
# ------------------------------------------------------------------------------
# Author: Ravit Khurana <ravit.khurana@gmail.com>
# ------------------------------------------------------------------------------
# TODO: Alert user if title for gnome terminal/guake is set as dynamic
# TODO: Let user choose which terminal he/she wants to use

import sys
import gtk
import appindicator
import os
import subprocess
import re

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SERVER_DETAILS_PROPERTIES = BASE_PATH + '/config/server_details.properties'
GET_GUAKE_VISIBILTY_PY = BASE_PATH + '/lib/getGuakeVisibilty.py'
SSH_LOGIN_WITH_PASSWORD_SH = BASE_PATH + '/lib/ssh_login_with_password.sh'
QUICK_SSH_PNG = BASE_PATH + "/res/icons/quick-ssh.png"


class TERMINALS:
    GUAKE = "Guake Terminal"
    GNOME = "Gnome Terminal"

# TERMINAL_TO_USE = TERMINALS.GUAKE


class QuickSSHMenu:

    def __init__(self):
        self.TERMINAL_TO_USE = TERMINALS.GUAKE
        self.ind = appindicator.Indicator(
            "quick-ssh-indicator",
            QUICK_SSH_PNG,
            appindicator.CATEGORY_APPLICATION_STATUS
        )
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

        self.edit_server_details_item = gtk.MenuItem("<< Edit Server Details >>")
        self.edit_server_details_item.connect("activate", self.edit_server_details)
        self.edit_server_details_item.show()
        self.menu.append(self.edit_server_details_item)

        # TODO: Make this a submenu containing the available terminals
        self.toggle_item = gtk.MenuItem("Using - " + self.TERMINAL_TO_USE)
        self.toggle_item.connect("activate", self.toggle)  # TODO: Rename toggle to something else
        self.toggle_item.show()
        self.menu.append(self.toggle_item)

        # Reading server details from properties file
        serverDetails = []
        with open(SERVER_DETAILS_PROPERTIES, 'r') as f:
            p = re.compile('^[^=]*')
            for line in f.readlines():
                line = line.strip()
                if line[0] == '#':
                    continue
                else:
                    m = p.match(line)
                    pos_of_equals = m.end()
                    ip = line[0:pos_of_equals].strip()
                    label, username, password = [x.strip() for x in line[pos_of_equals+1:].strip().split(':')]
                    serverDetails.append(
                        {
                            'ip': ip,
                            'label': label,
                            'username': username,
                            'password': password
                        }
                    )

        # Populate the menu
        self.item_dict = {}
        # TODO: Make the text formating better
        for server in serverDetails:
            self.item_dict[server['label']] = gtk.MenuItem(
                "%s@%s\t\t (%s)" % (server['username'], server['ip'], server['label']))
            self.item_dict[server['label']].connect(
                "activate",
                self.generator(server))
            self.item_dict[server['label']].show()
            self.menu.append(self.item_dict[server['label']])

    def main(self):
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    # TODO: Change name of toggle method and change implementation
    #       to be able to choose between more than two terminals.
    def toggle(self, widget):
        # result = {
        #     'a': lambda x: x * 5,
        #     'b': lambda x: x + 7,
        #     'c': lambda x: x - 2
        # }.get(self.TERMINAL_TO_USE, TERMINALS.GNOME)
        if self.TERMINAL_TO_USE == TERMINALS.GNOME:
            self.TERMINAL_TO_USE = TERMINALS.GUAKE
        else:
            self.TERMINAL_TO_USE = TERMINALS.GNOME

    def generator(self, server):
        return lambda x: self.launchSSH(
            server['ip'] + ' (' + server['label'] + ')',
            server['ip'],
            server['username'],
            server['password'])

    def launchSSH(self, name, ip, username, password):
        ssh_connect_cmd = "sh %s %s %s %s && exit" % (SSH_LOGIN_WITH_PASSWORD_SH, ip, username, password)

        # TODO: Change implementation to be able to choose between more
        #       than two terminals
        if self.TERMINAL_TO_USE == TERMINALS.GUAKE:
            if self.isGuakeVisibile():
                os.system('guake -t')
                os.system('guake -t')
            else:
                os.system('guake -t')
            os.system('guake -n "1" -r "%s" -e "%s"' % (name, ssh_connect_cmd))
        else:
            os.system('gnome-terminal --title="%s" -x %s' % (name, ssh_connect_cmd))

    def edit_server_details(self, widget):
        os.system('xdg-open %s' % SERVER_DETAILS_PROPERTIES)

    def isGuakeVisibile(self):
        p = subprocess.Popen(
            ['python', GET_GUAKE_VISIBILTY_PY],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out.strip() == 'True':
            return True
        else:
            return False

if __name__ == "__main__":
    indicator = QuickSSHMenu()
    indicator.main()
