#!/bin/bash

echo 'i am in this directory'
echo $PWD

echo " will run this source ${1} ${2} ${3}"

python3 ${1} ${2} ${3}

echo 'done'