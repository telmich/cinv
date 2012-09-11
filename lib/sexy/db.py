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

import os

import sexy

class Error(sexy.Error):
    pass

class DB(object):

    def __init__(self, db_dir=None, prefix=None):
        if not db_dir:
            self.db_dir = self.get_default_db_dir()
        else:
            self.db_dir = db_dir

        self.prefix = prefix

    @staticmethod
    def get_default_db_dir():
        if 'HOME' in os.environ:
            db_dir = os.path.join(os.environ['HOME'], ".sexy", "db")
        else:
            raise Error("HOME unset - cannot find db dir")

        return db_dir

    @staticmethod
    def get_default_db_dir():
        if 'HOME' in os.environ:
            db_dir = os.path.join(os.environ['HOME'], ".sexy", "db")
        else:
            raise Error("HOME unset - cannot find db dir")

        return db_dir

    @staticmethod
    def get_default_backend_dir():
        if 'HOME' in os.environ:
            db_dir = os.path.join(os.environ['HOME'], ".sexy", "db")
        else:
            raise Error("HOME unset - cannot find db dir")

        return db_dir
