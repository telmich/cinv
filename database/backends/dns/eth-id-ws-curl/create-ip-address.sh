#!/bin/sh

set -x

[ $# -eq 2 ] || exit 1

hostname="$1";shift
ipv4a="$1";shift

#cat << eof | curl  --insecure --basic --request POST --header "Content-Type: text/xml" --netrc https://www.komcenter.ethz.ch/ip/rest/nameToIP
cat << eof | curl --verbose --basic --netrc --insecure --request POST \
--header "Content-Type: text/xml" --data - https://www.komcenter.ethz.ch/ip/rest/nameToIP
<insert>
  <nameToIP>
    <ip>$ipv4a</ip>
    <fqName>$hostname</fqName>
    <forward>Y</forward>
    <reverse>Y</reverse>
    <ttl>600</ttl>
    <isgGroup>inf-pc</isgGroup>
  </nameToIP>
</insert>
eof
