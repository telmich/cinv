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
import shutil
import socket
import struct

import sexy
from sexy import fsproperty

log = logging.getLogger(__name__)

HOST_TYPES = ["hw", "vm"]

class Error(sexy.Error):
    pass

class NetIPv4(object):

    def __init__(self, subnet):

        if not self.validate_ipv4address(subnet):
            raise Error("Not a valid IPv4 address: %s" % subnet)

        self.base_dir = self.get_base_dir(subnet)
        self.subnet   = subnet

    _mask   = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "mask"))
    free    = fsproperty.FileListProperty(lambda obj: os.path.join(obj.base_dir, "free"))
    last    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "last"))
    address = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'address'))

    def _init_base_dir(self, mask):
        """Create base directory"""

        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)

        self.mask = mask

    @staticmethod
    def subnet_split(subnet):
        return subnet.split('/')

    def validate_mask(self, mask):
        self.validate_mask_int_range(mask)
        self.validate_subnetaddress(mask)

    def validate_subnetaddress(self, mask):
        """Check whether given IPv4 address is the subnet address"""

        ip_dec = struct.unpack('>L',socket.inet_aton(self.subnet))[0]
        mask_dec = (1<<32) - (1<<32>> int(mask))

        subnet_dec = ip_dec & mask_dec

        log.debug("%s - %s %s" % (ip_dec, subnet_dec, mask_dec))

        subnet_str = socket.inet_ntoa(struct.pack('>L', subnet_dec))

        if not self.subnet == subnet_str:
            raise Error("Given address is not the subnet address (%s != %s)" % (subnet, subnet_str))

        log.debug("%s/%s" % (self.subnet, subnet_str))


    @staticmethod
    def validate_mask_int_range(mask):
        try:
            mask = int(mask)
        except ValueError as e:
            raise Error("Mask must be an integer")

        if mask not in range(1, 33):
            raise Error("Mask must be between 1 and 32 (inclusive)")

        return mask

    @staticmethod
    def validate_ipv4address(ipv4address):
        return re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', ipv4address)


    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        mask = self.validate_mask(mask)
        self._mask = str(mask)

    @staticmethod
    def get_base_dir(subnet):
        return os.path.join(sexy.get_base_dir("db"), "net-ipv4", subnet)

    @classmethod
    def subnet_list(cls):
        subnets = []

        base_dir = os.path.join(sexy.get_base_dir("db"), "net-ipv4")

        for entry in os.listdir(base_dir):
            subnets.append(entry)

        return subnets

    @classmethod
    def exists(cls, subnet):
        return os.path.exists(cls.get_base_dir(subnet))

    def get_next_ipv4address(self):
        """Get next address from network"""

        attribute = getattr(self, "%ss" % area)

        if attribute:
            last_name = sorted([key for key in attribute if key.startswith(base_name)])[-1]
            last_number = last_name.lstrip(base_name)
            next_number = int(last_number) + 1
        else:
            next_number = 0

        return "%s%d" % (base_name, next_number)


    ######################################################################
    @classmethod
    def commandline_add(cls, args):
        try:
            subnet, mask = cls.subnet_split(args.subnet)
        except ValueError:
            raise Error("Invalid subnet syntax (expected <IPv4addr>/<mask>): %s" % args.subnet)

        if cls.exists(subnet):
            raise Error("Network already exist: %s" % subnet)

        net = cls(subnet)
        net.validate_mask(mask)
        net._init_base_dir(mask)

    @classmethod
    def commandline_del(cls, args):
        if not cls.exists(args.fqdn):
            if not args.missing_ignore:
                raise Error("Host does not exist: %s" % args.fqdn)
            else:
                return

        host = cls(fqdn=args.fqdn)

        if not args.recursive:
            if host.nics or host.disks:
                raise Error("Cannot delete, host contains disks or nics: %s" % args.fqdn)

        log.debug("Removing %s ..." % host.base_dir)
        shutil.rmtree(host.base_dir)

        sexy.backend_exec("host", "del", [args.fqdn])

                
    @classmethod
    def commandline_apply(cls, args):
        """Apply changes using the backend"""

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

        sexy.backend_exec("host", "apply", hosts)

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

        sexy.backend_exec("host", "disk_add", [args.fqdn, name, str(size_bytes)])

        log.info("Added disk %s (%s Bytes)" % (name, size_bytes))

    @classmethod
    def commandline_list(cls, args):
        for host in cls.hosts_list(args.type):
            print(host)

    @classmethod
    def commandline_addr_add(cls, args):

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
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', parents=parents)
        parser['add'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)')
        parser['add'].set_defaults(func=cls.commandline_add)

        parser['del'] = parser['sub'].add_parser('del', parents=parents)
        parser['del'].add_argument('-r', '--recursive', help='Delete subnet and all addresses',
            action='store_true')
        parser['del'].add_argument('-i', '--ignore-missing', 
            help='Do not fail if subnet is missing', action='store_true')
        parser['del'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)')
        parser['del'].set_defaults(func=cls.commandline_del)

        parser['addr-add'] = parser['sub'].add_parser('addr-add', parents=parents)
        parser['addr-add'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)')
        parser['addr-add'].add_argument('-s', '--size', help='Disk size',
            required=True)
        parser['addr-add'].add_argument('-n', '--name', help='Disk name')
        parser['addr-add'].set_defaults(func=cls.commandline_addr_add)

        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].set_defaults(func=cls.commandline_list)

        parser['apply'] = parser['sub'].add_parser('apply', parents=parents)
        parser['apply'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)',
            nargs='*')
        parser['apply'].add_argument('-a', '--all', 
            help='Apply settings for all subnets', required = False,
            action='store_true')
        parser['apply'].set_defaults(func=cls.commandline_apply)


