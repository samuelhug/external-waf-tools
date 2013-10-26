#!/bin/bash

## Update Closure Compiler
TEMP_FILE=`mktemp`

wget http://closure-compiler.googlecode.com/files/compiler-latest.zip -O $TEMP_FILE

mkdir -p closure-compiler

pushd closure-compiler
unzip -o $TEMP_FILE
popd


## Update Closure Templates
TEMP_FILE=`mktemp`

wget https://closure-templates.googlecode.com/files/closure-templates-for-javascript-latest.zip -O $TEMP_FILE

mkdir -p closure-templates

pushd closure-templates
unzip -o $TEMP_FILE
popd
