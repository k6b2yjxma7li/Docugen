# -*- coding: utf-8 -*-
"""
`docpodl`
===
Creating documentation of PODL files that specify data model for Oracle BRM.
PODL files have in fact structure of JSON. Additional info is stored inside
CSV file. Script reads CSV file, finds corresponding PODL and merges data to
generate documentation. 
"""
import os
import re
import json
import sys
import docpod
import csv
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
Lines starting with # will be ignored in preprocessing.

name:
^[A-Z]+[\s]*[A-Z]+


"""

storables_reg = r"[A-Z]+?[\s\S]+?\{+[\s\S]*\}+"
header_reg = r"(?<=\b)[^\n]+?(?=\s\{)"

storables_map = {
    r"(?=(^STORABLE CLASS)[\s\S]+?\{+[\s\S]*\}+": "<div class=\"storable_class\">*</div>",
    r"INT [\s\S]+?\{+[\s\S]*\}+": "<div class=\"integer\">*</div>",
    r"DECIMAL [\s\S]+?\{+[\s\S]*\}+": "<div class=\"float\">*</div>",
    r"STRING [\s\S]+?\{+[\s\S]*\}+": "<div class=\"string\">*</div>",
    r"ENUM [\s\S]+?\{+[\s\S]*\}+": "<div class=\"enum\">*</div>",
    r"SUBSTRUCT [\s\S]+?\{+[\s\S]*\}+": "<div class=\"enum\">*</div>",
    r"[A-Z]+ [\s\S]+?\{+[\s\S]*\}+": "<div class=\"non_recognized_class\">*</div>"
}

def csv2table(csv_file, is_header=True, delim=","):
    """
    csv2table
    ===
    Create HTML table from CSV formatted data, that 
    """
    pass
    # csv.DictReader(csv_file, delim=",")


def main(path):
    pass
    # SEARCHING FOR PODL_ZZZ
    # walker = os.walk(os.path.normpath(path))
    # podl_files = []
    # for p, d, f in walker:
    #     # print("".join(f))
    #     if re.search(r"\.podl", "".join(f)) is not None:
    #         # print(f)
    #         for fl in f:
    #             if re.search(r"\.podl$", fl):
    #                 # print(os.path.join(p, fl))
    #                 podl_files += [os.path.join(p, fl)]
    #                 # break
    #         # break
    # # print(f"Podl files: {len(podl_files)}")
    # for the_podl in podl_files:
    #     podl_def = ""
    # try:
    #     the_podl = path
    #     with open(the_podl, 'r', encoding='utf-8') as fstream:
    #         podl_def = fstream.read()
    # except FileNotFoundError:
    #     print(f"File not found: {the_podl}")
    #     # exit()
    # # print(the_podl)
    # podl_def = re.sub(r"\#[^\n]*(\n|$)", "", podl_def)
    # def1 = docpod._tag_(podl_def, r'(?<=\b)[^\n]+?\{', r'\}', r'\{', r'\}', storables_map)
    # print(def1.convert())
    # exit()

if __name__ == "__main__":
    pass
    # main(sys.argv[1])