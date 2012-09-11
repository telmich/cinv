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

        mask_dec = (1<<32) - (1<<32>> int(mask))
        subnet_dec = self.subnet_decimal() & mask_dec
        subnet_str = self.ipv4_address_string(subnet_dec)

        if not self.subnet == subnet_str:
            raise Error("Given address is not the subnet address (%s != %s)" % (self.subnet, subnet_str))

    @staticmethod
    def validate_mask_int_range(mask):
        try:
            mask = int(mask)
        except ValueError as e:
            raise Error("Mask must be an integer")

        if mask not in range(1, 33):
            raise Error("Mask must be between 1 and 32 (inclusive)")

    @staticmethod
    def validate_ipv4address(ipv4address):
        return re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', ipv4address)


    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        self.validate_mask(mask)
        self._mask = str(mask)

    @staticmethod
    def get_base_dir(subnet):
        return os.path.join(sexy.get_base_dir("db"), "net-ipv4", subnet)

    @classmethod
    def subnet_list(cls):
        subnets = []

        base_dir = os.path.join(sexy.get_base_dir("db"), "net-ipv4")

        # FIXME: add mask!
        for entry in os.listdir(base_dir):
            subnets.append(entry)

        return subnets

    @classmethod
    def exists(cls, subnet):
        return os.path.exists(cls.get_base_dir(subnet))

    @staticmethod
    def ipv4_address_decimal(ipv4_address):
        """ Return IPv4 address in decimal """
        return struct.unpack('>L',socket.inet_aton(ipv4_address))[0]

    @staticmethod
    def ipv4_address_string(ipv4_address_decimal):
        """ Return IPv4 address in decimal """
        return socket.inet_ntoa(struct.pack('>L', ipv4_address_decimal))

    def subnet_decimal(self):
        """ Return Subnet address in decimal """
        return self.ipv4_address_decimal(self.subnet)

    def broadcast(self):
        """ Return broadcast string """
        add_mask = (1<<(32 - int(self.mask)))-1
        broadcast = socket.inet_ntoa(struct.pack(">L", self.subnet_decimal() | add_mask))

        log.debug("Broadcast: %s" % broadcast)

        return broadcast

    def addr_add(self, mac_address, ipv4_address):
        """ Add an address to the network"""
        
        # Ensure given mac address is valid
        import sexy.mac
        sexy.mac.Mac.validate_mac(mac_address)

        if mac_address in self.address:
            raise Error("Mac address %s already using IPv4a %s" % (mac_address, self.address[mac_address]))

        next_ipv4_address = self.get_next_ipv4_address()

        self.address[mac_address] = next_ipv4_address


    def get_next_ipv4_address(self):
        """Get next address from network"""

        if self.free:
            return free.pop()

        if self.last:
            last_decimal = self.ipv4_address_decimal(self.last)
            next_decimal = last_decimal + 1
            next_ipv4_address = self.ipv4_address_string(next_decimal)
        else:
            next_decimal = self.subnet_decimal() + 1
            next_ipv4_address = self.ipv4_address_string(next_decimal)

        if next_ipv4_address == self.broadcast():
            raise Error("Next address is broadcast - cannot get new one")

        self.last = next_ipv4_address
        log.debug("Next IPv4 address: %s" % next_ipv4_address)

        return next_ipv4_address


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

        sexy.backend_exec("net-ipv4", "add", [subnet, mask])

#    @classmethod
#    def commandline_del(cls, args):
#        if not cls.exists(args.fqdn):
#            if not args.missing_ignore:
#                raise Error("Host does not exist: %s" % args.fqdn)
#            else:
#                return
#
#        host = cls(fqdn=args.fqdn)
#
#        if not args.recursive:
#            if host.nics or host.disks:
#                raise Error("Cannot delete, host contains disks or nics: %s" % args.fqdn)
#
#        log.debug("Removing %s ..." % host.base_dir)
#        shutil.rmtree(host.base_dir)
#
#        sexy.backend_exec("host", "del", [args.fqdn])

                
#    @classmethod
#    def commandline_apply(cls, args):
#        """Apply changes using the backend"""
#
#        if not args.all and not args.fqdn and not args.type:
#            raise Error("Required to pass either FQDNs, type or --all")
#        if args.type and args.fqdn:
#            raise Error("Cannot combine FQDN list and type")
#
#        if args.type:
#            hosts = cls.hosts_list(args.type)
#        elif args.all:
#            hosts = cls.hosts_list()
#        else:
#            hosts = args.fqdn
#
#        sexy.backend_exec("host", "apply", hosts)

    @classmethod
    def commandline_list(cls, args):
        for subnet in cls.subnet_list():
            print(subnet)

    @classmethod
    def commandline_addr_add(cls, args):

        if not cls.exists(args.subnet):
            raise Error("Subnet does not exist: %s" % args.subnet)

        net = cls(args.subnet)
        net.addr_add(args.mac_address, args.ipv4_address)

    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', parents=parents)
        parser['add'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)')
        parser['add'].set_defaults(func=cls.commandline_add)

#        parser['del'] = parser['sub'].add_parser('del', parents=parents)
#        parser['del'].add_argument('-r', '--recursive', help='Delete subnet and all addresses',
#            action='store_true')
#        parser['del'].add_argument('-i', '--ignore-missing', 
#            help='Do not fail if subnet is missing', action='store_true')
#        parser['del'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)')
#        parser['del'].set_defaults(func=cls.commandline_del)

        parser['addr-add'] = parser['sub'].add_parser('addr-add', parents=parents)
        parser['addr-add'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)')
        parser['addr-add'].add_argument('-m', '--mac-address', help='Mac Address',
            required=True)
        parser['addr-add'].add_argument('-i', '--ipv4-address', help='Requested IPv4 Address')
        parser['addr-add'].set_defaults(func=cls.commandline_addr_add)

        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].set_defaults(func=cls.commandline_list)

#        parser['apply'] = parser['sub'].add_parser('apply', parents=parents)
#        parser['apply'].add_argument('subnet', help='Subnet name and mask (a.b.c.d/m)',
#            nargs='*')
#        parser['apply'].add_argument('-a', '--all', 
#            help='Apply settings for all subnets', required = False,
#            action='store_true')
#        parser['apply'].set_defaults(func=cls.commandline_apply)


