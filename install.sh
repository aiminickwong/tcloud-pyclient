#!/bin/sh

install=`dirname $0`

python $install/compile.py

mkdir -p output
rm -f ../output/twindow.tar.gz
rm -rf .settings 

find . -name \*.pyc -o -name \*.conf -o -name \*.ui | xargs tar cvfz output/twindow.tar.gz
