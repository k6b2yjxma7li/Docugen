# -*- coding: utf-8 -*-
"""
`docpodl`
===
Creating documentation of PODL files that specify data model for Oracle BRM. PODL files have
in fact structure of JSON. Additional info is stored inside CSV file. Script reads CSV file,
finds corresponding PODL and merges data to generate documentation. 
"""
import os
import re
import json
import sys
# import docpod
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


#   Basic name map if fieldmap.json not specified
namemap = {
    "class.csv":
    {
        "NAZWA_KLASY": "Class name",
        "OPIS": "Description",
        "SEQ_START": "Sequence start",
        "READ_ACCESS": "Read access",
        "WRITE_ACCESS": "Write access",
        "IS_PARTITIONED": "Partitioning",
        "PARTITION_MODE": "Part. mode"
    },
    "class_fields.csv":
    {
    }
}

class csv_class:
    """
    class `csv_class`
    ===
    CSV specified data model classes
    ---
    """
    def __init__(self, csv_class_block, delim=";", level=0, max_level=3):
        """
        `csv_class.__init__`
        ===
        Constructor of `csv_class`
        ---
        """
        max_level = int(max_level)
        self.level = int(level)
        header = list(csv_class_block.keys())
        f_line = [csv_class_block[h][0] for h in header]
        self.name = csv_class_block[header[0]][0]
        self.parameters = dict(zip(header[max_level+1-self.level:],
                                   f_line[max_level+1-self.level:]))
        for h in header:
            csv_class_block[h].pop(0)
        csv_class_block.pop(header[0])
        if self.level < max_level and len(csv_class_block[header[-1]]) > 0:
            self.fields, _ = csv_class.get_classes(None, csv_class_block, level=self.level+1)
        else:
            self.fields = []

    def __str__(self):
        """
        `csv_class.__str__`
        ===
        String representation of `csv_class` object
        ---
        """
        result = f"name:\t{self.name}\n"
        if 'OPIS' in self.parameters.keys():
            result += f"descr.:\t{self.parameters['OPIS']}\n"
        params = str(self.parameters).replace("\\n", '\n\t')
        params = params.replace("', '", "',\n\t'")
        result += f"params:\t{params}\n"
        if len(self.fields) > 0:
            field_names = f"fields: (total: {len(self.fields)})\n\n\t"
            for field in self.fields:
                field_names += str(field).replace('\n', '\n\t')+"\n\t"
            result += field_names
        return result

    @staticmethod
    def split_table(csv_stream, delim=";"):
        """
        `csv_class.split_table`: static
        ===
        Partitioning CSV table by values in first column
        ---
        File's generator equivalent to `csv_class.split_dict`.
        """
        csv_reader = csv.DictReader(csv_stream, delimiter=delim)
        n = 0
        breaker = True
        endborder = False
        while breaker:
            if not(endborder):
                f_line = dict(next(csv_reader)) # first line of class
            endborder = False
            colname = list(f_line.keys())   # names of columns
            line = f_line.copy()    # first line (dict)
            const_lines = dict([[k, []] for k,v in line.items()])  # all lines within class
            while True:
                for k, v in line.items():
                    const_lines[k] += [v]
                try:
                    line = dict(next(csv_reader))
                    if not(line[colname[0]] == f_line[colname[0]]):
                        endborder = True
                        f_line = line
                        break
                except StopIteration:
                    breaker = False
                    break
            # print(const_lines)
            n += 1
            yield n, const_lines

    @staticmethod
    def split_dict(csv_dict, level=0):
        """
        `csv_class.split_dict`: static
        ===
        Partitioning dict of lists by value under first key
        ---
        Dict equivalent to `csv_class.split_table`.
        """
        n = 0
        breaker = True
        while breaker:
            f_line = dict([[h, csv_dict[h][n]] for h in list(csv_dict.keys())]) # first line of class
            colname = list(f_line.keys())   # names of columns
            line = f_line.copy()    # first line (dict)
            const_lines = dict([[k, []] for k,v in line.items()])  # all lines within class
            while line[colname[0]] == f_line[colname[0]]:
                for k, v in line.items():
                    const_lines[k] += [v]
                try:
                    n += 1
                    line = dict([[h, csv_dict[h][n]] for h in list(csv_dict.keys())])
                    # if not(line[colname[0]] == f_line[colname[0]]):
                    #     n -= 1
                except IndexError:
                    breaker = False
                    break
            yield n, const_lines

    @staticmethod
    def get_classes(csv_stream=None, csv_dict=None, delim=";", level=0, max_level=3):
        """
        `csv_class.get_classes`: static
        ===
        Creating list of classes
        ---
        From `csv_stream` (file's generator) or `csv_dist` (dict of lists) proper classes are 
        selected. One of first two arguments is a generator from `csv_class.split_table` or
        `csv_class.split_dict` (could be any object of matching type as yielded from those
        methods as well).
        """
        result = []
        names = []
        if csv_stream is not None:
            csv_iter = csv_class.split_table(csv_stream, delim=delim)
        else:
            csv_iter = csv_class.split_dict(csv_dict)
        for _, block in csv_iter:
            result.append(csv_class(block, level=level, max_level=max_level))
            names.append(result[-1].name)
        return result, names


def json2dict(json_path):
    """
    `json2dict`
    ===
    Dict from specified in json_path file
    ---
    """
    nmap = {}
    try:
        with open(json_path) as jsonfile:
            nmap = json.loads(jsonfile.read())
    except FileNotFoundError:
        global namemap
        nmap = namemap
    return nmap


def set_namemap(nmap):
    """
    `set_namemap`
    ===
    Seting global value of `namemap`
    ---
    `namemap` specifies how column names from CSV file are translated
    in tables.
    """
    global namemap
    namemap = nmap


def get_podls(mainpath="."):
    """
    `get_podls`
    ===
    Creates generator which contains path and name of each PODL file
    found in directory passed as argument.
    """
    filetree = os.walk(mainpath)
    def return_podl_path():
        for pth, dr, fl in filetree:
            for f in fl:
                if ".podl" in f:
                    yield pth, f
    return return_podl_path()


def make_reference(podl_name):
    """
    `make_reference`
    ===
    Finds class in CSV files and creates a dict of it by name of
    PODL equivalent.
    """


if __name__ == "__main__":
    path = input("Specify path for CSV file: ")
    print(path)
    mlev = input("Maximal level of nesting: ")
    if not(mlev):
        mlev = 3
        print("Default nesting level:", mlev)
    else:
        mlev = int(mlev)
        print("User specified nesting level:", mlev)
    podl, name = csv_class.get_classes(open(path,
                                            encoding='utf-8',
                                            newline=""), max_level=mlev)
    class_name = input("Specify class name: ")
    print(podl[name.index(class_name)])