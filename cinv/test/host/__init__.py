#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2011 Nico Schottelius (nico-cinv at schottelius.org)
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

import cinv.host
import unittest

class HostTest(unittest.TestCase):
    def setUp(self):
        self.host = cinv.host.Host("test.example.org")

    def wrong_host_type(self):
        self.host.host_type = "wrong type"

    def test_prevent_wrong_type(self):
        """Prevent adding hosts with wrong type"""
        self.assertRaises(cinv.host.Error, self.wrong_host_type)


    def wrong_memory(self):
        self.host.memory = "13A"

    def test_prevent_wrong_memory(self):
        """Prevent adding wrong memory values"""
        self.assertRaises(cinv.host.Error, self.wrong_memory)


    def wrong_cores(self):
        self.host.cores = "13A"

    def test_prevent_wrong_cores(self):
        """Prevent adding wrong core values"""
        self.assertRaises(cinv.host.Error, self.wrong_cores)

