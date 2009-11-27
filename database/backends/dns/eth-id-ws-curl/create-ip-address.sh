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
# Setup an a-entry via curl to ETH ID Webservice
#

[ $# -eq 2 ] || exit 1

fqdn="$1";shift
ipv4a="$1";shift

cat << eof | curl --verbose --basic --netrc --insecure --request POST \
--header "Content-Type: text/xml" --data @- https://www.komcenter.ethz.ch/ip/rest/nameToIP
<insert>
  <nameToIP>
    <ip>${ipv4a}</ip>
    <fqName>${fqdn}</fqName>
    <forward>Y</forward>
    <reverse>Y</reverse>
    <ttl>600</ttl>
    <isgGroup>inf-pc</isgGroup>
  </nameToIP>
</insert>
eof
