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

log = logging.getLogger(__name__)

class Error(sexy.Error):
    pass

class Mac(object):

    def __init__(self):
        self.base_dir = self.get_base_dir()

    _prefix = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "prefix"))
    free   = fsproperty.FileListProperty(lambda obj: os.path.join(obj.base_dir, "free"))
    last    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "last"))

    def _init_base_dir(self):
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)

    @staticmethod
    def validate_mac(mac):
        if not re.match(r'([0-9A-F]{2}[-:]){5}[0-9A-F]{2}$', mac, re.I):
            raise Error("Not a valid mac address: %s" % mac)

    def free_append(self, mac):
        if mac in self.free:
            raise Error("Mac already in free database: %s" % mac)

        self.free.append(mac)


    @staticmethod
    def get_base_dir():
        return sexy.get_base_dir("mac")

    @classmethod
    def exists(cls):
        return os.path.exists(cls.get_base_dir())

    def get_next(self):
        if self.free:
            return self.free.pop()
            
        if not self.prefix:
            raise Error("Cannot generate address without prefix - use prefix-set")

        if self.last:
            suffix = re.search(r'([0-9A-F]{2}[-:]){2}[0-9A-F]{2}$', self.last, re.I)
            last_number_hex = "0x%s" % suffix.group().replace(":", "")
            last_number = int(last_number_hex, 16)

            if last_number == int('0xffffff', 16):
                raise Error("Exhausted all possible mac addresses - try to free some")

            next_number = last_number + 1
        else:
            next_number = 0

        next_number_hex = "%0.6x" % next_number
        next_suffix = "%s:%s:%s" % (next_number_hex[0:2], next_number_hex[2:4], next_number_hex[4:6])

        next_mac = "%s:%s" % (self.prefix, next_suffix)

        self.last = next_mac

        return next_mac


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
    def commandline_free_add(cls, args):
        mac = Mac()
        mac.validate_mac(args.address)
        mac.free_append(args.address)

    @classmethod
    def commandline_free_list(cls, args):
        mac = Mac()
        for mac in mac.free:
            print(mac)

    @classmethod
    def commandline_prefix_set(cls, args):
        mac = Mac()
        mac.prefix = args.prefix

    @classmethod
    def commandline_prefix_get(cls, args):
        mac = Mac()
        print(mac.prefix)

    @classmethod
    def commandline_add(cls, args):
        host = cls(fqdn=args.fqdn)
        host.host_type = args.type

    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Mac Commands")

        parser['free-add'] = parser['sub'].add_parser('free-add', parents=parents)
        parser['free-add'].add_argument('address', help='Address to add to free database')
        parser['free-add'].set_defaults(func=cls.commandline_free_add)

        parser['free-list'] = parser['sub'].add_parser('free-list', parents=parents,
            help="List free mac addresses")
        parser['free-list'].set_defaults(func=cls.commandline_free_list)

        parser['generate'] = parser['sub'].add_parser('generate', parents=parents)
        parser['generate'].set_defaults(func=cls.commandline_generate)

        parser['prefix-get'] = parser['sub'].add_parser('prefix-get', parents=parents)
        parser['prefix-get'].set_defaults(func=cls.commandline_prefix_get)

        parser['prefix-set'] = parser['sub'].add_parser('prefix-set', parents=parents)
        parser['prefix-set'].add_argument('prefix', help="3 Byte address prefix (f.i. '00:16:3e')")
        parser['prefix-set'].set_defaults(func=cls.commandline_prefix_set)
