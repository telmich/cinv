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

class Host(object):

    def __init__(self):
        pass

    @classmethod
    def commandline_handle(cls, args):
        print(args)
        pass

    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        #parser['main'] = parent_parser.add_parser('host', parents=parent)
        #parser['sub'] = parser['main'].add_subparsers(title="Host Commands")

        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', 
            parents=parents)
        parser['add'].add_argument('fqdn', help='Fully Qualified Domain Name')
        parser['add'].add_argument('-t', '--type', help='Machine Type',
            choices=["hw","vm"])

        parser['del'] = parser['sub'].add_parser('del', 
            parents=parents)

        parser['del'].add_argument('subnet', help='Subnet to delete')

        parser['list'] = parser['sub'].add_parser('list', 
            parents=parents)
        parser['list'].add_argument('-t', '--type', help='Machine Type',
            choices=["hw","vm"])
        parser['list'].set_defaults(func=cls.commandline_handle)

