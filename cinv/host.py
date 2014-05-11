#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2012-2014 Nico Schottelius (nico-cinv at schottelius.org)
#
# This file is part of cinv.
#
# cinv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cinv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cinv. If not, see <http://www.gnu.org/licenses/>.
#
#

import argparse
import logging
import os.path
import os
import shutil

import cinv
from cinv import fsproperty

log = logging.getLogger(__name__)

HOST_TYPES = ["hw", "vm"]

class Error(cinv.Error):
    pass

class Host(object):

    ######################################################################
    # Initialisation
    #

    def __str__(self):
        return self.fqdn

    def __init__(self, fqdn):

        if fqdn == None or fqdn == "":
            raise cdist.Error("Cannot create host with empty fqdn")

        self.base_dir = self.get_base_dir(fqdn)
        self.fqdn = fqdn

    def _init_base_dir(self, host_type):
        """Create base directory of host"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise Error(e)

        self.host_type = host_type

    ######################################################################
    # Properties
    #

    _cores      = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "cores"))
    disk        = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'disk'))
    _host_type  = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "host_type"))
    _memory     = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "memory"))
    nic         = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'nic'))
    tag         = fsproperty.DirectoryDictProperty(lambda obj: os.path.join(obj.base_dir, 'tag'))
    _vm_host    = fsproperty.FileStringProperty(lambda obj: os.path.join(obj.base_dir, "vm_host"))

    @property
    def cores(self):
        return self._cores

    @cores.setter
    def cores(self, cores):
        cores = self.convert_si_prefixed_size_values(cores)
        self._cores = cores

    def disk_add(self, size, name=False):
        size = self.convert_si_prefixed_size_values(size)

        if name:
            if name in self.disk:
                raise Error("Disk already exists: %s" % name)
        else:
            name = self.get_next_name("disk")

        self.disk[name] = size

        cinv.backend_exec("host", "disk_add", [self.fqdn, name, str(size)])

    @property
    def hostname(self):
        return self.fqdn.split(".")[0]

    @property
    def host_type(self):
        return self._host_type

    @host_type.setter
    def host_type(self, host_type):
        self.validate_host_type(host_type)
        self._host_type = host_type

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, memory):
        memory = self.convert_si_prefixed_size_values(memory)
        self._memory = memory

    @property
    def vm_host(self):
        return self._vm_host

    @vm_host.setter
    def vm_host(self, vm_host):
        if not self.host_type == "vm":
            raise Error("Can only configure vm-host for VMs")

        self._vm_host = vm_host

    @staticmethod
    def get_base_dir(fqdn):
        return os.path.join(cinv.get_base_dir("db"), "host", fqdn)

    @classmethod
    def host_list(cls, host_type=None, tags=[]):
        hosts = []

        if host_type:
            if host_type not in HOST_TYPES:
                raise Error("Host type must be one of %s" % (" ".join(HOST_TYPES)))

        base_dir = os.path.join(cinv.get_base_dir("db"), "host")

        if not os.path.isdir(base_dir):
            return []

        for entry in os.listdir(base_dir):
            if host_type:
                host = cls(entry)
                if host.host_type == host_type:
                    hosts.append(entry)
            else:
                hosts.append(entry)

        # Only show hosts matching all tags (but can contain other tags)
        if len(tags) > 0:
            hosts_with_tags = []

            for host in hosts:
                host_object = cls(host)
                has_tags = True
                for tag in tags:
                    if not tag in host_object.tag.keys():
                        has_tags = False
                        break
                if has_tags:
                    hosts_with_tags.append(host)

            hosts = hosts_with_tags

        return hosts

    @classmethod
    def exists(cls, fqdn):
        return os.path.exists(cls.get_base_dir(fqdn))

    @classmethod
    def exists_or_raise_error(cls, fqdn):
        if not cls.exists(fqdn):
            raise Error("Host does not exist: %s" % fqdn)

    @staticmethod
    def convert_si_prefixed_size_values(value):
        """Convert given size to bytes"""

        # Skip if there is nothing to calculate
        if type(value) == int:
            return value

        # Skip if it is a string that is just an int
        try:
            value = int(value)
            return value
        except ValueError:
            pass

        prefix = int(value[:-1])
        suffix = value[-1].lower()

        if suffix == 'k':
            value = prefix * (1024**1)
        elif suffix == 'm':
            value = prefix * (1024**2)
        elif suffix == 'g':
            value = prefix * (1024**3)
        elif suffix == 't':
            value = prefix * (1024**4)
        elif suffix == 'p':
            value = prefix * (1024**5)
        elif suffix == 'e':
            value = prefix * (1024**6)
        elif suffix == 'z':
            value = prefix * (1024**7)
        elif suffix == 'y':
            value = prefix * (1024**8)
        else:
            raise Error("Unsupported suffix %s" % (suffix))

        return value

    def get_next_name(self, area):
        """Get next generic disk name"""

        base_name = area
        attribute = getattr(self, area)

        if attribute:
            last_name = sorted([key for key in attribute if key.startswith(base_name)])[-1]
            last_number = last_name.lstrip(base_name)
            next_number = int(last_number) + 1
        else:
            next_number = 0

        return "%s%d" % (base_name, next_number)

    @staticmethod
    def validate_host_type(host_type):
        if host_type not in HOST_TYPES:
            raise Error("Host type must be one of %s" % (" ".join(HOST_TYPES)))


    ######################################################################
    # Commandline
    #

    @classmethod
    def commandline_add(cls, args):
        if cls.exists(args.fqdn):
            raise Error("Host already exist: %s" % args.fqdn)

        host = cls(fqdn=args.fqdn)
        host.validate_host_type(args.type)
        host._init_base_dir(args.type)

                
    @classmethod
    def commandline_apply(cls, args):
        """Apply changes using the backend"""

        # FIXME: maybe support only --all - everything else could cause inconsistencies

        if not args.all and not args.fqdn and not args.type:
            raise Error("Required to pass either FQDNs, type or --all")
        if args.type and args.fqdn:
            raise Error("Cannot combine FQDN list and type")

        if args.type:
            hosts = cls.host_list(args.type)
        elif args.all:
            hosts = cls.host_list()
        else:
            hosts = args.fqdn

        cinv.backend_exec("host", "apply", hosts)

    @classmethod
    def commandline_cores_get(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        print(host.cores)

    @classmethod
    def commandline_cores_set(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        host.cores = args.cores

        log.info("Cores for %s = %s" % (args.fqdn, args.cores))

    @classmethod
    def commandline_del(cls, args):
        if not cls.exists(args.fqdn):
            if not args.ignore_missing:
                raise Error("Host does not exist: %s" % args.fqdn)
            else:
                return

        host = cls(fqdn=args.fqdn)

        if not args.recursive:
            if host.nic or host.disk:
                raise Error("Cannot delete, host contains disk or nic: %s" % args.fqdn)

        log.debug("Removing %s ..." % host.base_dir)
        shutil.rmtree(host.base_dir)

        cinv.backend_exec("host", "del", [args.fqdn])



    @classmethod
    def commandline_disk_add(cls, args):

        cls.exists_or_raise_error(args.fqdn)
        host = cls(fqdn=args.fqdn)
        host.disk_add(size=args.size, name=args.name)

        log.info("Added disk %s (%s Bytes)" % (name, size_bytes))

    @classmethod
    def commandline_disk_list(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        for disk in host.disk.keys():
            print(disk)


    @classmethod
    def commandline_disk_size_get(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        try:
            size = host.disk[args.name]
        except KeyError:
            raise Error("Host %s does not have disk: %s" % (args.fqdn,  args.name))

        print(size)


    @classmethod
    def commandline_list(cls, args):
        for host in cls.host_list(args.type, args.tags):
            print(host)

    @classmethod
    def commandline_memory_get(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        print(host.memory)

    @classmethod
    def commandline_memory_set(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        size_bytes = cls.convert_si_prefixed_size_values(args.memory)
        host.memory = size_bytes

        log.info("Memory for %s = %s" % (args.fqdn, args.memory))


    @classmethod
    def commandline_nic_add(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        if args.name:
            if args.name in host.nic:
                raise Error("Network interface card already existing: %s")
            name = args.name
        else:
            name = host.get_next_name("nic")

        host.nic[name] = args.mac_address

        log.info("Added nic %s (%s)" % (name, args.mac_address))

    @classmethod
    def commandline_nic_addr_get(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        try:
            mac_address = host.nic[args.name]
        except KeyError:
            raise Error("Host %s does not have nic: %s" % (args.fqdn,  args.name))

        print(mac_address)

    @classmethod
    def commandline_nic_del(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        name = args.name

        if not name in host.nic:
            raise Error("Cannot delete non existing nic: %s" % name)

        del host.nic[name]

        log.info("Deleted nic %s" % name)


    @classmethod
    def commandline_nic_list(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        for nic in host.nic.keys():
            print(nic)

    def tag_add(self, name, value="", force=False):

        if name in self.tag and not force:
            raise Error("tag already existing: %s" % name)

        self.tag[name] = value


    @classmethod
    def commandline_tag_add(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        host.tag_add(args.name, args.value, args.force)

        log.info("Added tag %s = \"%s\"" % (args.name, args.value))

    def tag_del(self, name, force=False):
        if name in self.tag:
            del self.tag[name]
        else:
            if not force:
                raise Error("tag does not exist: %s" % name)

    @classmethod
    def commandline_tag_del(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        host.tag_del(args.name, args.force)

        log.info("Deleted tag %s" % (name))

    @classmethod
    def commandline_tag_list(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)

        for name in host.tag.keys():
            print(name)


    @classmethod
    def commandline_type_get(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        print(host.host_type)

    @classmethod
    def commandline_vm_host_get(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        print(host.vm_host)

    @classmethod
    def vmhosts_vms_list(cls, tags=[]):
        vm_hosts = {}
        for fqdn in cls.host_list(tags=tags):
            host = cls(fqdn)
            if host.vm_host:
                # Create new array, if not already existing
                if host.vm_host not in vm_hosts:
                    vm_hosts[host.vm_host] = []

                vm_hosts[host.vm_host].append(fqdn)
        
        return vm_hosts

    @classmethod
    def commandline_vm_host_list(cls, args):
        vm_hosts = cls.vmhosts_vms_list()
        sorted_vm_host_names = sorted(vm_hosts.keys())

        for vm_host in sorted_vm_host_names:
            print("%s:" % vm_host)

            for fqdn in vm_hosts[vm_host]:
                print("\t%s" % fqdn)


    @classmethod
    def commandline_vm_host_set(cls, args):

        cls.exists_or_raise_error(args.fqdn)

        host = cls(fqdn=args.fqdn)
        host.vm_host = args.vm_host

        log.info("VMHost for %s = %s" % (args.fqdn, args.vm_host))

    ######################################################################
    # Argument parser
    #

    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Host Commands")

        parser['add'] = parser['sub'].add_parser('add', parents=parents)
        parser['add'].add_argument('fqdn', help='Host name')
        parser['add'].add_argument('-t', '--type', help='Machine Type',
            required=True, choices=HOST_TYPES)
        parser['add'].set_defaults(func=cls.commandline_add)

        parser['cores-get'] = parser['sub'].add_parser('cores-get', parents=parents)
        parser['cores-get'].add_argument('fqdn', help='Host name')
        parser['cores-get'].set_defaults(func=cls.commandline_cores_get)

        parser['cores-set'] = parser['sub'].add_parser('cores-set', parents=parents)
        parser['cores-set'].add_argument('fqdn', help='Host name')
        parser['cores-set'].add_argument('-c', '--cores', help='Number of Cores',
            required=True)
        parser['cores-set'].set_defaults(func=cls.commandline_cores_set)

        parser['del'] = parser['sub'].add_parser('del', parents=parents)
        parser['del'].add_argument('-r', '--recursive', help='Delete host and all parts',
            action='store_true')
        parser['del'].add_argument('-i', '--ignore-missing', 
            help='Do not fail if host is missing', action='store_true')
        parser['del'].add_argument('fqdn', help='Host name')
        parser['del'].set_defaults(func=cls.commandline_del)

        parser['disk-add'] = parser['sub'].add_parser('disk-add', parents=parents)
        parser['disk-add'].add_argument('fqdn', help='Host name')
        parser['disk-add'].add_argument('-s', '--size', help='Disk size',
            required=True)
        parser['disk-add'].add_argument('-n', '--name', help='Disk name')
        parser['disk-add'].set_defaults(func=cls.commandline_disk_add)

        parser['disk-size-get'] = parser['sub'].add_parser('disk-size-get', parents=parents)
        parser['disk-size-get'].add_argument('fqdn', help='Host name')
        parser['disk-size-get'].add_argument('-n', '--name', help='Disk name', required=True)
        parser['disk-size-get'].set_defaults(func=cls.commandline_disk_size_get)

        parser['disk-list'] = parser['sub'].add_parser('disk-list', parents=parents)
        parser['disk-list'].add_argument('fqdn', help='Host name')
        parser['disk-list'].set_defaults(func=cls.commandline_disk_list)

        parser['list'] = parser['sub'].add_parser('list', parents=parents)
        parser['list'].add_argument('-t', '--type', help='Host Type',
            choices=HOST_TYPES, required=False)
        parser['list'].add_argument('-T', '--tags', help='Host containing tag', action='append',
            default=[], required=False)
        parser['list'].set_defaults(func=cls.commandline_list)


        parser['memory-get'] = parser['sub'].add_parser('memory-get', parents=parents)
        parser['memory-get'].add_argument('fqdn', help='Host name')
        parser['memory-get'].set_defaults(func=cls.commandline_memory_get)

        parser['memory-set'] = parser['sub'].add_parser('memory-set', parents=parents)
        parser['memory-set'].add_argument('fqdn', help='Host name')
        parser['memory-set'].add_argument('-m', '--memory', help='Main memory',
            required=True)
        parser['memory-set'].set_defaults(func=cls.commandline_memory_set)


        parser['nic-add'] = parser['sub'].add_parser('nic-add', parents=parents)
        parser['nic-add'].add_argument('fqdn', help='Host name')
        parser['nic-add'].add_argument('-m', '--mac-address', help='Mac address',
            required=True)
        parser['nic-add'].add_argument('-n', '--name', help='Nic name')
        parser['nic-add'].set_defaults(func=cls.commandline_nic_add)

        parser['nic-del'] = parser['sub'].add_parser('nic-del', parents=parents)
        parser['nic-del'].add_argument('fqdn', help='Host name')
        parser['nic-del'].add_argument('-n', '--name', help='Nic name', required=True)
        parser['nic-del'].set_defaults(func=cls.commandline_nic_del)

        parser['nic-addr-get'] = parser['sub'].add_parser('nic-addr-get', parents=parents)
        parser['nic-addr-get'].add_argument('fqdn', help='Host name')
        parser['nic-addr-get'].add_argument('-n', '--name', help='Name', required=True)
        parser['nic-addr-get'].set_defaults(func=cls.commandline_nic_addr_get)

        parser['nic-list'] = parser['sub'].add_parser('nic-list', parents=parents)
        parser['nic-list'].add_argument('fqdn', help='Host name')
        parser['nic-list'].set_defaults(func=cls.commandline_nic_list)

        parser['tag-add'] = parser['sub'].add_parser('tag-add', parents=parents)
        parser['tag-add'].add_argument('fqdn', help='Host name')
        parser['tag-add'].add_argument('-f', '--force', help='Also add if already existent')
        parser['tag-add'].add_argument('-n', '--name', help='Name', required=True)
        parser['tag-add'].add_argument('-V', '--value', help='Value')
        parser['tag-add'].set_defaults(func=cls.commandline_tag_add)

        parser['tag-del'] = parser['sub'].add_parser('tag-del', parents=parents)
        parser['tag-del'].add_argument('fqdn', help='Host name')
        parser['tag-del'].add_argument('-f', '--force', help='Do not fail if tag is gone already')
        parser['tag-del'].add_argument('-n', '--name', help='Name', required=True)
        parser['tag-del'].add_argument('-V', '--value', help='Value')
        parser['tag-del'].set_defaults(func=cls.commandline_tag_del)

        parser['tag-list'] = parser['sub'].add_parser('tag-list', parents=parents)
        parser['tag-list'].add_argument('fqdn', help='Host name')
        parser['tag-list'].set_defaults(func=cls.commandline_tag_list)

        parser['type-get'] = parser['sub'].add_parser('type-get', parents=parents)
        parser['type-get'].add_argument('fqdn', help='Host name')
        parser['type-get'].set_defaults(func=cls.commandline_type_get)

        parser['vm-host-get'] = parser['sub'].add_parser('vm-host-get', parents=parents)
        parser['vm-host-get'].add_argument('fqdn', help='Host name')
        parser['vm-host-get'].set_defaults(func=cls.commandline_vm_host_get)

        parser['vm-host-list'] = parser['sub'].add_parser('vm-host-list', parents=parents)
        parser['vm-host-list'].set_defaults(func=cls.commandline_vm_host_list)

        parser['vm-host-set'] = parser['sub'].add_parser('vm-host-set', parents=parents)
        parser['vm-host-set'].add_argument('fqdn', help='Host name')
        parser['vm-host-set'].add_argument('--vm-host', help='VM Host (only for VMs)',
            required=True)
        parser['vm-host-set'].set_defaults(func=cls.commandline_vm_host_set)

        parser['apply'] = parser['sub'].add_parser('apply', parents=parents)
        parser['apply'].add_argument('fqdn', help='Host name',
            nargs='*')
        parser['apply'].add_argument('-a', '--all', 
            help='Apply settings for all hosts', required = False,
            action='store_true')
        parser['apply'].add_argument('-t', '--type', help='Host Type (implies --all)',
            choices=HOST_TYPES, required=False)
        parser['apply'].set_defaults(func=cls.commandline_apply)
