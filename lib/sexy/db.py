#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2012 Nico Schottelius (nico-sexy at schottelius.org)
#
# This file is part of sexy.
#
# sexy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sexy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sexy. If not, see <http://www.gnu.org/licenses/>.
#
#

import os

import sexy

class Error(sexy.Error):
    pass

class DB(object):

    def __init__(self, db_dir=None, prefix=None):
        if not db_dir:
            self.db_dir = self.get_default_db_dir()
        else:
            self.db_dir = db_dir

        self.prefix = prefix

    @staticmethod
    def get_default_db_dir():
        if 'HOME' in os.environ:
            db_dir = os.path.join(os.environ['HOME'], ".sexy", "db")
        else:
            raise Error("HOME unset - cannot find db dir")

        return db_dir

    def dir_add(self, key, exist_ok=True):
        """Create (new) db entry"""

        self.verify_prefix()
        sub_dir = os.path.join(self.prefix, key)
        entry_dir = os.path.join(self.db_dir, sub_dir)

        try:
            os.makedirs(entry_dir, exist_ok=exist_ok)
        except OSError as e:
            raise Error(e)

    def oneliner_add(self, sub_dir, key, value, exist_ok=True):
        """Create (new) oneliner entry"""

        self.verify_prefix()
        entry = os.path.join(self.db_dir, self.prefix, sub_dir, key)

        if not exist_ok:
            if os.path.exists(entry):
                raise Error("Key %s already exists for %s" % (key, os.path.join(self.prefix, sub_dir)))

        try:
            with open(entry, "w") as fd:
                fd.write("%s\n" % value)

        except IOError as e:
            raise Error(e)

    def verify_prefix(self):
        if not self.prefix:
            raise Error("Required prefix not given")


#    @classmethod
#    def commandline_list(cls, args):
#        print(args)
#        pass
#
#    @classmethod
#    def commandline_args(cls, parent_parser, parents):
#        """Add us to the parent parser and add all parents to our parsers"""
#
#        parser = {}
#        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")
#
#        parser['add'] = parser['sub'].add_parser('add', 
#            parents=parents)
#        parser['add'].add_argument('fqdn', help='Fully Qualified Domain Name')
#        parser['add'].add_argument('-t', '--type', help='Machine Type',
#            required=True, choices=["hw","vm"])
#
#        parser['del'] = parser['sub'].add_parser('del', 
#            parents=parents)
#
#        parser['del'].add_argument('subnet', help='Subnet to delete')
#
#        parser['list'] = parser['sub'].add_parser('list', 
#            parents=parents)
#        parser['list'].add_argument('-t', '--type', help='Machine Type',
#            choices=["hw","vm"])
#        parser['list'].set_defaults(func=cls.commandline_list)
#

