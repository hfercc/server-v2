#!/bin/bash
python utils/setup.py --py-file=$1 build_ext
pdot=`expr index "$1" .`
name=${1:0:$pdot-1}
cp build/lib.linux-x86_64-2.7/$name.so ./alpha/
rm -f $1
rm -f *.c
