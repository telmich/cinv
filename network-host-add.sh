#!/bin/sh

set -e
set -x


name="$1"; shift
network="$1"; shift
ipn="$1"; shift

# FIXME
basedir="./"
host_base="${basedir}/hosts/"
host_dir="${host_base}/${name}"
network_base="${basedir}/network/"
network_dir="${network_base}/${network}"

usage()
{
   echo "name network [<ipn>|next-free]"
}


if [ ! -d "${network_dir}" ]; then
   echo "No network configuration found for ${network}"
   exit 1
fi

mkdir -p "${ddir}"
echo "${type}" > "${ddir}/type"
echo "${type}" > "${ddir}/location"


