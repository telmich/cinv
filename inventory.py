#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2012 Nico Schottelius (nico-cdist at schottelius.org)
#
# This file is part of cdist.
#
# cdist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cdist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cdist. If not, see <http://www.gnu.org/licenses/>.
#
#

import cdist
import os
import re


def split_network_name(name):
    if not re.match(r".*/[0-9]*", name):
        raise cdist.Error("Invalid network name: %s (expected <addr>/<mask>)" % network)

def cli(args):
    """Command line handling"""

    base_dir = "/home/users/nico/p/cdist/core/conf/inventory"

    if args.network_add:
        network = args.network_add
        address, mask = split_network_name(network)
        print("Adding network %s with mask %s" % (network, mask))
        network_dir = os.path.join(base_dir, address)

        os.makedirs(network_dir)
        else:
