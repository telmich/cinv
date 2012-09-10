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

import argparse
import logging
import os.path
import os
import re

import sexy
from sexy import fsproperty

from sexy.db import DB

log = logging.getLogger(__name__)

class Error(sexy.Error):
    pass

class Mac(object):

    def __init__(self):
        self.base_dir = os.path.join(DB.get_default_db_dir(), "mac")

        self._init_dir()

    _prefix  = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "prefix"))
    last    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "last"))
    free    = fsproperty.FileListProperty(lambda obj: os.path.join(obj.base_dir, "free"))

    def _init_dir(self):
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)


    def get_next(self):
        if not self.prefix:
            raise Error("Cannot generate address without prefix - use prefix-set")

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        if not re.match(r'([0-9A-F]{2}[-:]){2}[0-9A-F]{2}$', prefix, re.I):
            raise Error("Wrong mac address format - use 00:11:22")

        self._prefix = prefix



    @classmethod
    def commandline_generate(cls, args):
        mac = Mac()
        print(mac.get_next())

    @classmethod
    def commandline_prefix_set(cls, args):
        mac = Mac()
        mac.prefix = args.prefix

    @classmethod
    def commandline_prefix_get(cls, args):
        print(args)

    @classmethod
    def commandline_add(cls, args):
        host = cls(fqdn=args.fqdn)
        host.host_type = args.type

    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Mac Commands")

        parser['generate'] = parser['sub'].add_parser('generate', parents=parents)
        parser['generate'].set_defaults(func=cls.commandline_generate)

        parser['free'] = parser['sub'].add_parser('free', parents=parents)
        parser['free'].add_argument('address', help='Address to add to free database')

        parser['prefix-set'] = parser['sub'].add_parser('prefix-set', parents=parents)
        parser['prefix-set'].add_argument('prefix', help="3 Byte address prefix (f.i. '00:16:3e')")
        parser['prefix-set'].set_defaults(func=cls.commandline_prefix_set)
