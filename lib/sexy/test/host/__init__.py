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
        self.host = sexy.host.Host("test.example.org")

    def wrong_host_type(self):
        self.host.host_type = "wrong type"

    def test_prevent_wrong_type(self):
        """Prevent adding hosts with wrong type"""
        self.assertRaises(sexy.host.Error, self.wrong_host_type)

