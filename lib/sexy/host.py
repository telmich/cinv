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
        self.base_dir = self.get_base_dir(fqdn)
        self.fqdn = fqdn

    disks       = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'disks'))
    _host_type  = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "host_type"))
    _memory     = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "memory"))
    nics        = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'nics'))
    _vm_host    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "vm_host"))

    def _init_base_dir(self, host_type):
        """Create base directory of host"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)

        self.host_type = host_type

    @staticmethod
    def validate_host_type(host_type):
        if host_type not in HOST_TYPES:
            raise Error("Host type must be one of %s" % (" ".join(HOST_TYPES)))

    @property
    def host_type(self):
        return self._host_type

    @host_type.setter
    def host_type(self, host_type):
        self.validate_host_type(host_type)
        self._host_type = host_type

    @property
    def vm_host(self):
        return self._vmhost

    @vm_host.setter
    def vm_host(self, vm_host):
        if not self.host_type == "vm":
            raise Error("Can only configure vmhost for VMs")

        self._vm_host = vm_host

    @staticmethod
    def get_base_dir(fqdn):
        return os.path.join(DB.get_default_db_dir(), "host", fqdn)

    @classmethod
    def hosts_list(cls, host_type=None):
        hosts = []

        if host_type:
            if host_type not in HOST_TYPES:
                raise Error("Host type must be one of %s" % (" ".join(HOST_TYPES)))

        base_dir = os.path.join(DB.get_default_db_dir(), "host")

        for entry in os.listdir(base_dir):
            if host_type:
                host = cls(entry)
                if host.host_type == host_type:
                    hosts.append(entry)
            else:
                hosts.append(entry)

        return hosts

    @classmethod
    def exists(cls, fqdn):
        return os.path.exists(cls.get_base_dir(fqdn))

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

    def get_next_name(self, area):
        """Get next generic disk name"""

        base_name = area
        attribute = getattr(self, "%ss" % area)

        if attribute:
            last_name = sorted([key for key in attribute if key.startswith(base_name)])[-1]
            last_number = last_name.lstrip(base_name)
            next_number = int(last_number) + 1
        else:
            next_number = 0

        return "%s%d" % (base_name, next_number)


    @classmethod
    def commandline_add(cls, args):
        if cls.exists(args.fqdn):
            raise Error("Host already exist: %s" % args.fqdn)

        host = cls(fqdn=args.fqdn)
        host.validate_host_type(args.type)
        host._init_base_dir(args.type)

    @classmethod
    def commandline_apply(cls, args):
        """Call backend"""

        if not args.all and not args.fqdn and not args.type:
            raise Error("Required to pass either FQDNs, type or --all")
        if args.type and args.fqdn:
            raise Error("Cannot combine FQDN list and type")

        if args.type:
            hosts = cls.hosts_list(args.type)
        elif args.all:
            hosts = cls.hosts_list()
        else:
            hosts = args.fqdn

        log.debug("Apply for: %s" % (" ".join(hosts)))

    @classmethod
    def commandline_disk_add(cls, args):

        if not cls.exists(args.fqdn):
            raise Error("Host does not exist: %s" % args.fqdn)

        host = cls(fqdn=args.fqdn)
        size_bytes = cls.convert_si_prefixed_size_values(args.size)

        if args.name:
            if args.name in host.disks:
                raise Error("Disk already existing: %s")
        else:
            name = host.get_next_name("disk")

        host.disks[name] = size_bytes

        log.info("Added disk %s (%s Bytes)" % (name, size_bytes))

    @classmethod
    def commandline_list(cls, args):
        for host in cls.hosts_list(args.type):
            print(host)

    @classmethod
    def commandline_nic_add(cls, args):

        if not cls.exists(args.fqdn):
            raise Error("Host does not exist: %s" % args.fqdn)

        host = cls(fqdn=args.fqdn)

        if args.name:
            if args.name in host.disks:
                raise Error("Network interface card already existing: %s")
        else:
            name = host.get_next_name("nic")

        host.nics[name] = args.address

        log.info("Added nic %s (%s)" % (name, args.address))

    @classmethod
    def commandline_vmhost_set(cls, args):

        if not cls.exists(args.fqdn):
            raise Error("Host does not exist: %s" % args.fqdn)

        host = cls(fqdn=args.fqdn)
        host.vm_host = args.vm_host

        log.info("VMHost for %s = %s" % (args.fqdn, args.vm_host))

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

        parser['nic-add'] = parser['sub'].add_parser('nic-add', parents=parents)
        parser['nic-add'].add_argument('fqdn', help='Host name')
        parser['nic-add'].add_argument('-a', '--address', help='Mac address',
            required=True)
        parser['nic-add'].add_argument('-n', '--name', help='Nic name')
        parser['nic-add'].set_defaults(func=cls.commandline_nic_add)

        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].add_argument('-t', '--type', help='Host Type',
            choices=["hw","vm"], required=False)
        parser['list'].set_defaults(func=cls.commandline_list)

        parser['vmhost-set'] = parser['sub'].add_parser('vmhost-set', parents=parents)
        parser['vmhost-set'].add_argument('fqdn', help='Host name')
        parser['vmhost-set'].add_argument('--vm-host', help='VM Host (only for VMs)',
            required=True)
        parser['vmhost-set'].set_defaults(func=cls.commandline_vmhost_set)

        parser['apply'] = parser['sub'].add_parser('apply', parents=parents)
        parser['apply'].add_argument('fqdn', help='Host name',
            nargs='*')
        parser['apply'].add_argument('-a', '--all', 
            help='Apply settings for all hosts', required = False,
            action='store_true')
        parser['apply'].add_argument('-t', '--type', help='Host Type (implies --all)',
            choices=["hw","vm"], required=False)
        parser['apply'].set_defaults(func=cls.commandline_apply)


