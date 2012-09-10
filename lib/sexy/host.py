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

import sexy
from sexy import fsproperty

from sexy.db import DB

log = logging.getLogger(__name__)

HOST_TYPES = ["hw", "vm"]

class Error(sexy.Error):
    pass

class Host(object):

    def __init__(self, fqdn):
        self.host_dir = os.path.join(DB.get_default_db_dir(), "host", fqdn)
        self.fqdn = fqdn
        self._init_dir()

    host_type = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.host_dir, "host_type"))
    disks  = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.host_dir, 'disks'))

    def _init_dir(self):
        try:
            os.makedirs(self.host_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)

    @staticmethod
    def convert_si_prefixed_size_values(value):
        """Convert given size of 101 G to bytes"""

        prefix = int(value[:-1])
        suffix = value[-1].lower()

        if suffix == 'k':
            bytes = prefix * (1024**1)
        elif suffix == 'm':
            bytes = prefix * (1024**2)
        elif suffix == 'g':
            bytes = prefix * (1024**3)
        elif suffix == 't':
            bytes = prefix * (1024**4)
        elif suffix == 'p':
            bytes = prefix * (1024**5)
        elif suffix == 'e':
            bytes = prefix * (1024**6)
        elif suffix == 'z':
            bytes = prefix * (1024**7)
        elif suffix == 'y':
            bytes = prefix * (1024**8)
        else:
            raise Error("Unsupported suffix %s" % (suffix))

        return bytes

    def get_next_disk_name(self):
        """Get next generic disk name"""

        base_name = "disk"

        if self.disks:
            last_name = sorted([key for key in self.disks if key.startswith(base_name)])[-1]
            last_number = last_name.lstrip(base_name)
            next_number = int(last_number) + 1
        else:
            next_number = 0

        return "%s%d" % (base_name, next_number)


    @classmethod
    def commandline_list(cls, args):
        print(args)
        pass

    @classmethod
    def commandline_add(cls, args):
        host = cls(fqdn=args.fqdn)
        host.host_type = args.type

    @classmethod
    def commandline_disk_add(cls, args):
        host = cls(fqdn=args.fqdn)
        size_bytes = cls.convert_si_prefixed_size_values(args.size)

        if args.name:
            if args.name in host.disks:
                raise Error("Disk %s already existing")
        else:
            name = host.get_next_disk_name()

        log.info("Adding disk %s (%s Bytes)" % (name, size_bytes))


    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', parents=parents)
        parser['add'].add_argument('fqdn', help='Host name')
        parser['add'].add_argument('-t', '--type', help='Machine Type',
            required=True, choices=["hw","vm"])
        parser['add'].set_defaults(func=cls.commandline_add)

        parser['del'] = parser['sub'].add_parser('del', parents=parents)
        parser['del'].add_argument('fqdn', help='Host name')

        parser['disk-add'] = parser['sub'].add_parser('disk-add', parents=parents)
        parser['disk-add'].add_argument('fqdn', help='Host name')
        parser['disk-add'].add_argument('-s', '--size', help='Disk size',
            required=True)
        parser['disk-add'].add_argument('-n', '--name', help='Disk name')
        parser['disk-add'].set_defaults(func=cls.commandline_disk_add)

        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].add_argument('-t', '--type', help='Host Type',
            choices=["hw","vm"])
        parser['list'].set_defaults(func=cls.commandline_list)


