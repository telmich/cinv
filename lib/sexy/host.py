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

import sexy
from sexy.db import DB

HOST_TYPES = ["hw", "vm"]

class Error(sexy.Error):
    pass

class Host(object):

    def __init__(self, fqdn=None, host_type=None):
        self.fqdn = fqdn
        self.host_type = host_type

        self.db = DB(prefix="host")

    def to_disk(self, exist_ok=True):
        """Write entry to disk"""

        self.verify()

        self.db.dir_add(self.fqdn, exist_ok=exist_ok)
        self.db.oneliner_add(self.fqdn, "host_type", self.host_type)

    def verify(self):
        self.verify_host_type()
        self.verify_host_fqdn()

    def verify_host_fqdn(self):
        if not self.fqdn:
            raise Error("Required FQDN not given")

    def verify_host_type(self):
        """Verify host type is correct"""

        if self.host_type not in HOST_TYPES:
            raise Error("Host type must be one of %s" % (" ".join(HOST_TYPES)))

    @staticmethod
    def convert_si_prefixed_size_values(value):
        """Convert given size of 101 G to bytes"""

        prefix = int(value[:-1])
        suffix = value[-1]

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
        else:
            raise Error("Unsupported suffix %s" % (suffix))

        return bytes
            

    @classmethod
    def commandline_list(cls, args):
        print(args)
        pass

    @classmethod
    def commandline_add(cls, args):
        host = cls(fqdn=args.fqdn, host_type = args.type)

        host.to_disk(exist_ok=False)


    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', parents=parents)
        parser['add'].add_argument('fqdn', help='Fully Qualified Domain Name')
        parser['add'].add_argument('-t', '--type', help='Machine Type',
            required=True, choices=["hw","vm"])
        parser['add'].set_defaults(func=cls.commandline_add)

        parser['del'] = parser['sub'].add_parser('del', 
            parents=parents)

        parser['del'].add_argument('subnet', help='Subnet to delete')

        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].add_argument('-t', '--type', help='Host Type',
            choices=["hw","vm"])
        parser['list'].set_defaults(func=cls.commandline_list)


