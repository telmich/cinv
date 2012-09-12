#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2011 Nico Schottelius (nico-sexy at schottelius.org)
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

import sexy.netipv4
import shutil
import tempfile
import unittest

class HostTest(unittest.TestCase):
    def setUp(self):
        self.network = sexy.netipv4.NetIPv4("127.0.0.0")
        self.temp_dir = tempfile.mkdtemp()
        self.network.base_dir = self.temp_dir
        self.network._init_base_dir(8)
        print(self.network.base_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_validate_network_address(self):
        bad_network = sexy.netipv4.NetIPv4("127.0.0.1")
        self.assertRaises(sexy.netipv4.Error, bad_network.validate_network_address, "16")

        # Should not raise anything
        good_network = sexy.netipv4.NetIPv4("127.0.0.0")
        good_network.validate_network_address(16)

    def test_map_address_in_network(self):
        in_net = "127.42.254.23"

        network = self.network.map_ipv4_address_to_network_address(in_net)
        self.assertEqual(network, self.network.network)

    def test_map_address_out_of_network(self):
        out_net = "128.0.0.0"
        network = self.network.map_ipv4_address_to_network_address(out_net)
        self.assertNotEqual(network, self.network.network)

    def test_ipv4address_in_network(self):
        in_addr = "127.42.254.23"
        self.assertTrue(self.network.ipv4_address_belongs_to_network(in_addr))

    def test_add_wrong_ipv4_address(self):
        """ Add Host with ip address of different network"""
        self.assertRaises(sexy.netipv4.Error, self.network.host_add, "test2", "00:11:22:33:44:66", "192.168.1.1")

    def test_double_add_ipv4_address(self):
        """Add two hosts with same IP address"""
        self.network.host_add("test1", "00:11:22:33:44:55", "127.0.0.1")
        self.assertRaises(sexy.netipv4.Error, self.network.host_add, "test2", "00:11:22:33:44:66", "127.0.0.1")

