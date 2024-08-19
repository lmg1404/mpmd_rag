#!/bin/bash

# This file resolves found dependencies when installing q-drant client
# and installing requirements onto a Linux machine. By downgrading and appending
# this file effectively replaces the command 'pip freeze > requirements.txt'. 

input1=requirements.txt
version="1.60.0"
append="; platform_system==\"Windows\""

pip freeze > $input1
sed -i 's/\r$//' $input1
sed -i -E "s/^(grpcio.*==).*/\1${version}/; s/^(pywin32==.*)/\1${append}/" $input1
