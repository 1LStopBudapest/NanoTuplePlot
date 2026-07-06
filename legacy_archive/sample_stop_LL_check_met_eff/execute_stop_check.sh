#!/bin/bash

echo 'i am in this directory'
echo $PWD
python3 --version
root-config --python-version

echo " will run this python ${1} ${2} ${3}" 

python3 ${1} ${2} ${3}

echo 'done'

