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

import cinv.mac
import shutil
import tempfile
import unittest

class MacTest(unittest.TestCase):
    def setUp(self):
        self.mac = cinv.mac.Mac()

        self.temp_dir = tempfile.mkdtemp()

        self.mac.base_dir = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_overflow(self):
        """ Check that no more than all possible mac addresses with one prefix can be used"""
        self.mac.last = "00:00:00:ff:ff:ff"
        self.assertRaises(cinv.mac.Error, self.mac.get_next)
