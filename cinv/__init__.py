#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2012 Nico Schottelius (nico-cinv at schottelius.org)
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

VERSION="2.0"

import logging
import os.path
import cinv
import subprocess

log = logging.getLogger(__name__)

class Error(Exception):
    """Base class for fallback of all exceptions"""
    pass

def get_base_dir(area):
    if 'HOME' in os.environ:
        base_dir = os.path.join(os.environ['HOME'], ".cinv", area)
    else:
        raise Error("HOME unset - cannot find default directory")

    return base_dir

def backend_exec(area, command, args, missing_ok=True):
    command = os.path.join(get_base_dir("backend"), area, command)
    db_path = os.path.join(get_base_dir("db"), area)

    env = os.environ.copy()
    env_name = ('__cinv_db_%s' % area).replace("-","_")
    env[env_name] = db_path

    subprocess_args = [ command ]
    subprocess_args.extend(args)


    log.debug("Exec %s=%s %s %s" % (env_name, env[env_name], 
        command, " ".join(args)))

    log.debug("%s" % args)

    if not os.path.exists(command):
        if missing_ok:
            log.debug("%s ignores missing backend command: %s" % (area, command))
            return True
        else:
            raise Error("%s misses backend command: %s" % (area, command))

    return subprocess.call(subprocess_args, env=env)
