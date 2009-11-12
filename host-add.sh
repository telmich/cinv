#!/bin/sh


name="$1"; shift
type="$1"; shift
location="$1"; shift
network="$1"; shift

# FIXME
basedir="./"
host_dir="${basedir}/hosts/"
network_dir="${basedir}/network/"
ddir="${hostdir}/${name}"

mkdir -p "${ddir}"
echo "${type}" > "${ddir}/type"
echo "${type}" > "${ddir}/location"


