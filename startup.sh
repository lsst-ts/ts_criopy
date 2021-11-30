#!/usr/bin/bash

# setup colors
b=$(tput bold)
r=$(tput rev)
R=$(tput setaf 1)
Y=$(tput setaf 3)
N=$(tput sgr0)

if [ "$1" == "bare" ]; then
  shift
  echo "${Y}Executing bare bash with arguments${N}: $@"
  exec "bash" "$@"
fi

cd /home/saluser
source .criopy_setup.sh

if [ "$#" -eq 0 ]; then
  echo """
${R}No parameter specified, dropping you to a shell.${N} Supported docker run parameters:
  ${b}bare${N} - run bare container, don't source SAL/DDS setup files, don't setup environment
  ${b}SSGUI${N} - run M1M3 Support System GUI
  ${b}TSGUI${N} - run M1M3 Thermal System GUI
  ${b}VMSGUI${N} - run VMS GUI
  ${b}VMSlogger${N} - run VMSlogger. Pass provided arguments to logger call.
"""
  exec "bash"
fi

par=$(echo $1 | tr [:lower:] [:upper:])
shift

cd repos/ts_cRIOpy/bin

case $par in
  SSGUI)
    ./M1M3GUI
    ;;
  TSGUI)
    ./M1M3TSGUI
    ;;
  VMSGUI)
    ./VMSGUI
    ;;
  VMSLOGGER)
    ./VMSlogger $*
    ;;
  *)
    echo "${Y}Unknown argument $par, executing shell${N}"
    exec "bash"
    ;;
esac
