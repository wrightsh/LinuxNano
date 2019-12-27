#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

try:
    output = subprocess.check_output(['halcmd', 'status'], universal_newlines=True)
except subprocess.CalledProcessError as e:
    output = e.output

print(output)
