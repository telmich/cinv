#!/bin/sh
# 
# 2009      Nico Schottelius (nico-sexy at schottelius.org)
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
# Add a host (and do all the stuff depending on it)
#

set -e
set -x

name="$1"; shift
mac="$1"; shift
type="$1"; shift
location="$1"; shift
ipa="$1"; shift

# optional?
#address="..."

# FIXME
basedir="./"
host_base="${basedir}/hosts/"
host_dir="${host_base}/${name}"
network_base="${basedir}/network/"
network_dir="${network_base}/${network}"


network-host-add.sh "${name}" "${network}" "${address}"

mkdir -p "${ddir}"
echo "${type}" > "${ddir}/type"
echo "${type}" > "${ddir}/location"


