#!/bin/sh

set -e

name="$1"; shift
type="$1"; shift
location="$1"; shift
network="$1"; shift

# FIXME
basedir="./"
host_base="${basedir}/hosts/"
host_dir="${host_base}/${name}"
network_base="${basedir}/network/"
network_dir="${network_base}/${network}"


if [ ! -d "${network_dir}" ]; then
   echo No network configuration available for ${network}"
   exit 1
fi

mkdir -p "${ddir}"
echo "${type}" > "${ddir}/type"
echo "${type}" > "${ddir}/location"


