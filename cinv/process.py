#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2014 Nico Schottelius (nico-cinv at schottelius.org)
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

import cinv
import logging
import os.path
import sys

log = logging.getLogger(__name__)

class Error(cinv.Error):
    pass

class Process(object):

    @classmethod
    def check_for_processes(cls):
        pdir = cinv.get_base_dir("process")
        pfile = os.path.join(pdir, "__init__.py")

        if os.path.exists(pfile):
            exists = True
        else:
            exists = False

        return exists
            
    @classmethod
    def commandline_args(cls, parent_parser, parents):
        """Add us to the parent parser and add all parents to our parsers"""

        parser = {}
        parser['sub'] = parent_parser.add_subparsers(title="Process Commands")

        if cls.check_for_processes():
            log.debug("importing processes")

            sys.path.insert(0, cinv.get_home_dir())
            import process as cinvprocess
            cinvprocess.register_parser(parser)

        else:
            log.debug("no processes defined")
