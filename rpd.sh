#!/bin/bash

input1=requirements.txt
version="1.60.0"
append="; platform_system==\"Windows\""

pip freeze > $input1
sed -i 's/\r$//' $input1
sed -i -E "s/^(grpcio.*==).*/\1${version}/" $input1
sed -i -E "s/^(pywin32==.*)/\1${append}/" $input1
