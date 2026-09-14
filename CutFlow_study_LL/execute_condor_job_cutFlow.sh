#!/bin/bash

echo 'i am in this directory'
echo $PWD

source ../set_python_lxplus/set_env.sh

echo " will run this source ${1} ${2} ${3} ${4} ${5} ${6} ${7} ${8} ${9} ${10} ${11} ${12} ${13}"

python ${1} ${2} ${3} ${4} ${5} ${6} ${7} ${8} ${9} ${10} ${11} ${12} ${13}

echo 'done'