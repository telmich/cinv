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

import sexy.host
import unittest

class HostTest(unittest.TestCase):
    def setUp(self):

    #    self.host = sexy.host.Host(fqdn = "test.example.org", host_type = "vm")

    def test_prevent_wrong_type(self):
        self.assertRaises(sexy.host.Error, sexy.host.Host, "test", "nothw")

    def test_host_add(self):
        self.host

