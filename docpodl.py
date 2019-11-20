# -*- coding: utf-8 -*-
"""
`docpodl`
===
Creating documentation of PODL files that specify data model for Oracle BRM.
"""
import os
import re
import json
import sys
# import logging


walker = os.walk(sys.argv[1])
first_podl = ""
for p, d, f in walker:
    if re.search(r"\.podl", "".join(f)) is not None:
        for fl in f:
            if re.search(r"\.podl$", fl):
                first_podl = os.path.join(p, fl)
                print(first_podl)
                break
        break
podl_def = ""
try:
    with open(first_podl, 'r', encoding='utf-8') as fstream:
        podl_def = fstream.read()
except FileNotFoundError:
    print(f"This file was not found: {first_podl}")