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

    def __init__(self, network):

        if not self.validate_ipv4address(network):
            raise Error("Not a valid IPv4 address: %s" % network)

        self.base_dir = self.get_base_dir(network)
        self.host_dir = os.path.join(self.base_dir, "host")
        self.network   = network

    _mask   = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "mask"))
    free    = fsproperty.FileListProperty(lambda obj: os.path.join(obj.base_dir, "free"))
    last    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "last"))
    address = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'address'))

    bootserver      = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "bootserver"))
    bootfilename    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "bootfilename"))

    def _init_base_dir(self, mask):
        """Create base directory"""

        try:
            os.makedirs(self.base_dir, exist_ok=True)
            os.makedirs(self.host_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)

        self.mask = mask

    @staticmethod
    def network_split(network):
        return network.split('/')

    def validate_mask(self, mask):
        self.validate_mask_int_range(mask)
        self.validate_network_address(mask)

    def validate_network_address(self, mask):
        """Check whether given IPv4 address is the net address"""

        mask_dec = (1<<32) - (1<<32>> int(mask))
        network_dec = self.network_decimal() & mask_dec
        network_str = self.ipv4_address_string(network_dec)

        if not self.network == network_str:
            raise Error("Given address is not the net address (%s != %s)" % (self.network, network_str))

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
    def get_base_dir(network):
        return os.path.join(sexy.get_base_dir("db"), "net-ipv4", network)

    @classmethod
    def network_list(cls):
        networks = []

        base_dir = os.path.join(sexy.get_base_dir("db"), "net-ipv4")

        for entry in os.listdir(base_dir):
            # With or without the mask is the question...
            #network = cls(entry)
            #networks.append("%s/%s" % (entry, network.mask))
            networks.append("%s" % (entry))

        return networks

    @classmethod
    def exists(cls, network):
        return os.path.exists(cls.get_base_dir(network))

    @staticmethod
    def ipv4_address_decimal(ipv4_address):
        """ Return IPv4 address in decimal """
        return struct.unpack('>L',socket.inet_aton(ipv4_address))[0]

    @staticmethod
    def ipv4_address_string(ipv4_address_decimal):
        """ Return IPv4 address in decimal """
        return socket.inet_ntoa(struct.pack('>L', ipv4_address_decimal))

    def network_decimal(self):
        """ Return Network address in decimal """
        return self.ipv4_address_decimal(self.network)

    def broadcast(self):
        """ Return broadcast string """
        add_mask = (1<<(32 - int(self.mask)))-1
        broadcast = socket.inet_ntoa(struct.pack(">L", self.network_decimal() | add_mask))

        log.debug("Broadcast: %s" % broadcast)

        return broadcast

    def host_add(self, fqdn, mac_address, ipv4_address):
        """ Add a host to the network"""
        
        # Ensure given mac address is valid
        import sexy.mac
        sexy.mac.Mac.validate_mac(mac_address)

        if self.host_exists(fqdn):
            raise Error("Host %s already in network %s" % (fqdn, self.network))

        mac_address_used = self.mac_address_used(mac_address)
        if mac_address_used:
            raise Error("Mac %s already used in network %s by %s" % (mac_address, self.network, mac_address_used))

        next_ipv4_address = self.get_next_ipv4_address()

        self.host_create(fqdn)
        self.host_mac_address_set(fqdn, mac_address)
        self.host_ipv4_address_set(fqdn, next_ipv4_address)

    def host_exists(self, fqdn):
        host_path = os.path.join(self.host_dir, fqdn)

        log.debug("Checking for host %s at %s" % (fqdn, host_path))
        return os.path.exists(host_path)

    def host_list(self):
        hosts = []
        for host in os.listdir(self.host_dir):
            hosts.append(host)

        return hosts

    def host_create(self, host):
        host_dir = os.path.join(self.host_dir, host)

        try:
            os.makedirs(host_dir)
        except OSError as e:
            raise Error(e)

    def host_mac_address_get(self, host):
        mac_address_file = os.path.join(self.host_dir, host, "mac_address")

        with open(mac_address_file, "r") as fd:
            return fd.read().rstrip('\n')

    def host_mac_address_set(self, host, mac_address):
        mac_address_file = os.path.join(self.host_dir, host, "mac_address")

        with open(mac_address_file, "w") as fd:
            fd.write("%s\n" % mac_address)

    def host_ipv4_address_set(self, host, ipv4_address):
        ipv4_address_file = os.path.join(self.host_dir, host, "ipv4_address")

        with open(ipv4_address_file, "w") as fd:
            fd.write("%s\n" % ipv4_address)

    def mac_address_used(self, mac_address):
        for host in self.host_list():
            host_mac_address = self.host_mac_address_get(host)

            if host_mac_address == mac_address:
                return host

        return None

    def get_next_ipv4_address(self):
        """Get next address from network"""

        if self.free:
            return free.pop()

        if self.last:
            last_decimal = self.ipv4_address_decimal(self.last)
            next_decimal = last_decimal + 1
            next_ipv4_address = self.ipv4_address_string(next_decimal)
        else:
            next_decimal = self.network_decimal() + 1
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
            network, mask = cls.network_split(args.network)
        except ValueError:
            raise Error("Invalid net syntax (expected <IPv4addr>/<mask>): %s" % args.network)

        if cls.exists(network):
            raise Error("Network already exist: %s" % network)

        network = cls(network)
        network.validate_mask(mask)
        network._init_base_dir(mask)

        sexy.backend_exec("net-ipv4", "add", [network.network, mask])

    @classmethod
    def commandline_apply(cls, args):
        """Apply changes using the backend"""

        if not args.all and not args.network:
            raise Error("Required to pass either networks or --all")

        if args.all:
            networks = cls.network_list()
        else:
            networks = args.network

        sexy.backend_exec("net-ipv4", "apply", networks)

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

                
    @classmethod
    def commandline_list(cls, args):
        for network in cls.network_list():
            print(network)

    @classmethod
    def commandline_bootfilename_get(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        print(network.bootfilename)

    @classmethod
    def commandline_bootfilename_set(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        network.bootfilename = args.bootfilename

    @classmethod
    def commandline_bootserver_get(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        print(network.bootserver)

    @classmethod
    def commandline_bootserver_set(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        network.bootserver = args.bootserver

    @classmethod
    def commandline_host_add(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        network.host_add(args.fqdn, args.mac_address, args.ipv4_address)

    @classmethod
    def commandline_host_list(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        for host in network.host_list():
            print(host)

    @classmethod
    def commandline_host_mac_address_get(cls, args):
        if not cls.exists(args.network):
            raise Error("Network does not exist: %s" % args.network)

        network = cls(args.network)
        if not network.host_exists(args.fqdn):
            raise Error("Host does not exist: %s" % args.fqdn)

        print(network.host_mac_address_get(args.fqdn))

    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', parents=parents)
        parser['add'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['add'].set_defaults(func=cls.commandline_add)

#        parser['del'] = parser['sub'].add_parser('del', parents=parents)
#        parser['del'].add_argument('-r', '--recursive', help='Delete net and all addresses',
#            action='store_true')
#        parser['del'].add_argument('-i', '--ignore-missing', 
#            help='Do not fail if net is missing', action='store_true')
#        parser['del'].add_argument('net', help='Network name and mask (a.b.c.d/m)')
#        parser['del'].set_defaults(func=cls.commandline_del)

        parser['host-add'] = parser['sub'].add_parser('host-add', parents=parents)
        parser['host-add'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['host-add'].add_argument('-m', '--mac-address', help='Mac Address',
            required=True)
        parser['host-add'].add_argument('-f', '--fqdn', help='FQDN of host',
            required=True)
        parser['host-add'].add_argument('-i', '--ipv4-address', help='Requested IPv4 Address')
        parser['host-add'].set_defaults(func=cls.commandline_host_add)

        parser['host-list'] = parser['sub'].add_parser('host-list', parents=parents)
        parser['host-list'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['host-list'].set_defaults(func=cls.commandline_host_list)

        parser['host-mac-address-get'] = parser['sub'].add_parser('host-mac-address-get', parents=parents)
        parser['host-mac-address-get'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['host-mac-address-get'].add_argument('-f', '--fqdn', help='FQDN of host',
            required=True)
        parser['host-mac-address-get'].set_defaults(func=cls.commandline_host_mac_address_get)

        parser['bootfilename-get'] = parser['sub'].add_parser('bootfilename-get', parents=parents)
        parser['bootfilename-get'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['bootfilename-get'].set_defaults(func=cls.commandline_bootfilename_get)
 
        parser['bootfilename-set'] = parser['sub'].add_parser('bootfilename-set', parents=parents)
        parser['bootfilename-set'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['bootfilename-set'].add_argument('--bootfilename', help='Bootserver',
            required=True)
        parser['bootfilename-set'].set_defaults(func=cls.commandline_bootfilename_set)

        parser['bootserver-get'] = parser['sub'].add_parser('bootserver-get', parents=parents)
        parser['bootserver-get'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['bootserver-get'].set_defaults(func=cls.commandline_bootserver_get)
 
        parser['bootserver-set'] = parser['sub'].add_parser('bootserver-set', parents=parents)
        parser['bootserver-set'].add_argument('network', help='Network name and mask (a.b.c.d/m)')
        parser['bootserver-set'].add_argument('--bootserver', help='Bootserver',
            required=True)
        parser['bootserver-set'].set_defaults(func=cls.commandline_bootserver_set)
 
        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].set_defaults(func=cls.commandline_list)

        parser['apply'] = parser['sub'].add_parser('apply', parents=parents)
        parser['apply'].add_argument('network', help='Network name and mask (a.b.c.d/m)',
            nargs='*')
        parser['apply'].add_argument('-a', '--all', 
            help='Apply settings for all networks', required = False,
            action='store_true')
        parser['apply'].set_defaults(func=cls.commandline_apply)
