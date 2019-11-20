# -*- coding: utf-8 -*-
"""
`docpodl`
===
Creating documentation of PODL files that specify data model for Oracle BRM.
PODL files have in fact structure of JSON.
"""
import os
import re
import json
import sys
import docpod
# import logging

"""
Structure of storable classess:

TYPE name {
    PARAM_1 = value;
    PARAM_2 = value;
    ...
    PARAM_n = value;

    #==============
    #   Fields
    #==============

    FIELD_1_TYPE FIELD_1_NAME {
        FIELD_1_PARAM_1 = ...
        ...
    }

    ...

    FIELD_m_TYPE FIELD_m_NAME {
        FIELD_m_PARAM_1 = ...
        ...
    }
}

so it's a nested JSON-like structure, however IT IS NOT JSON.
"""

storables_map = {
    
}


walker = os.walk(os.path.normpath(sys.argv[1]))
podl_files = []
for p, d, f in walker:
    # print("".join(f))
    if re.search(r"\.podl", "".join(f)) is not None:
        print(f)
        for fl in f:
            if re.search(r"\.podl$", fl):
                print(os.path.join(p, fl))
                podl_files += [os.path.join(p, fl)]
                # break
        # break
if type(podl_files) in [tuple, list]:
    print(f"Podl files: {len(podl_files)}")
for the_podl in podl_files:
    podl_def = ""
    try:
        # the_podl = podl_files[0]
        with open(the_podl, 'r', encoding='utf-8') as fstream:
            podl_def = fstream.read()
    except FileNotFoundError:
        print(f"This file was not found: {the_podl}")
        exit()

    podls = re.findall(re.compile(r"^[\s\S]+?\{[\s\S]+?\}", re.MULTILINE), podl_def)
    the_podl_file = the_podl.split("\\")[-1]
    print(f"{the_podl_file}: {len(podls)} definitions")
    print(podls[0])