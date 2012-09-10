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

import sexy.mac
import shutil
import tempfile
import unittest

class MacTest(unittest.TestCase):
    def setUp(self):
        self.mac = sexy.mac.Mac()
        self.temp_dir = tempfile.mkdtemp()

        self.mac.base_dir = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_overflow(self):
        self.mac.last = "00:00:00:ff:ff:ff"
        self.assertRaises(sexy.mac.Error, self.mac.get_next)
