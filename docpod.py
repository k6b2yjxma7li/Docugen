# -*- coding: utf-8 -*-
"""
docpod
===
POD documentation generator, Python version. This module brings all
functions needed to convert POD syntax to HTML code.

Usage
---
python docpod.py <pod_file_path>

Disclaimer
---
This tool have been prepared for Python 3 and may not work properly
(or work at all) for previous version. To prevent using it with
versions < 3 script will exit with `RuntimeError` if used with
incompatible Python version.

Author
---
Robert K. Rasała

Accenture

October/November 2019
"""
"""
As an addition to this tool there is `compressor` which
compresses/decompresses HTML template. 
"""

import re
import sys
# import logging
import os

# TO DO: logging
# ALSO: making log_file 

if sys.version_info.major < 3:
    sys.tracebacklimit = 0
    raise RuntimeError("Python version does not match requirements. "
                        "Please upgrade to Python 3.")

# just to ease code writing
_rm = lambda reg: re.compile(reg, re.MULTILINE)

# tag map for major in-tag structures
# order of `item` regex'es MATTERS A LOT SO DO NOT CHANGE THAT
# AND BE CAREFUL ABOUT WHAT YOU WISH FOR REGEX TO MATCH
tag_map1 = {
    r"^head1[\s\t\r]+": (re.compile(r"[^\n]*"), "<h1>*</h1>"),
    r"^head2[\s\t\r]+": (re.compile(r"[^\n]*"), "<h2>*</h2>"),
    r"^head3[\s\t\r]+": (re.compile(r"[^\n]*"), "<h3>*</h3>"),
    # r"^cut": (_rm(r"[\s\S]*"), "<!--\n*\n-->"),
    r"^cut": (_rm(r"[\s\S]*"), "<!--cut-->"),
    r"^over": (re.compile(r"[\s\S]*"), "<ul>"),
    r"^back": (re.compile(r"[\s\S]*"), "</ul>"),
    r"^item[\s\t\r]+\*[\s\n\t\r]+": (_rm(r"[\s\S]*"), "<li>*</li>"),
    r"^item[\s\t\r]+(\d)[\s\n\t\r]+":
    (_rm(r"[\s\S]*"), "<li style=\"list-style-type:decimal;\">*</li>"),
    r"^item[\s\t\r]+[A-Z][\s\r\t\n]+":
    (_rm(r"[\s\S]*"), "<li style=\"list-style-type:upper-latin;\">*</li>"),
    r"^item[\s\t\r]+[a-z][\s\r\t\n]+":
    (_rm(r"[\s\S]*"), "<li style=\"list-style-type:lower-latin;\">*</li>"),
    r"^item[\s\t]+":
    (_rm(r"[\s\S]*"), "<li style=\"list-style-type:none;\">*</li>"),
    r"^encoding[\s\t\r]+": (re.compile(r"[^\n]*"), "<!--*-->"),
    r"^": (_rm(r"[\s\S]+"), "<!--empty-->")
}

# tag map for minor in-tag structures
tag_map2 = {
    r"B\<+[\s\S]*\>+": "<b>*</b>",
    r"C\<+[\s\S]*\>+": "<a style=\"font-family: monospace; background-color: #f0f0f0;\">*</a>",
    r"E\<+[\s\S]*\>+": "&*;",
    r"F\<+[\s\S]*\>+": "<i class=\"file\">*</i>",
    r"I\<+[\s\S]*\>+": "<i>*</i>",
    r"L\<+[\s\S]*\>+": "<a href=\"\">*</a>"
}

# html special characters dictionary
html_spec = {
    ord("&"): "&amp;",
    ord("<"): "&lt;",
    ord(">"): "&gt;",
    ord("\""): "&quot;"
}

#   converting backslashes to slashes
dictionary = {92: 47}


# error communicates
no_index = ("no INDEX special comment tags detected. Without it"+
            " file/directory index cannot be inserted.\n*")
no_indexed = ("no INDEXED_PATHS special comment tags detected. Without it"+
              " file/directory index cannot be inserted.\n*")
no_header = ("no HEADER special comment tags detected. Without it file/directory"+
             "index cannot be inserted.\n*")
no_content = """no CONTENT special comment tags detected. Without it content cannot
be inserted.\n*"""
no_doc = """no convertible documentation detected.\n*"""


#   HTML styles for pages
style = """
        html {
            font-family: Calibri, "Helvetica", sans-serif;
            font-size: 14px;
        }
        h1:after, h2:after, h3:after {
            content: ' ';
            display: block;
            border: 2px solid #d0d0d0;
        }
        h1 {
            font-size: 1.7em;
        }
        h2 {
            font-size: 1.5em;
        }
        h3 {
            font-size: 1.3em;
        }
        h4 {
            font-size: 1.1em;
        }
        .collapsible {
            background-color: #777;
            color: white;
            cursor: pointer;
            padding: 18px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
        }
        .collapse {
            background-color: #777;
            color: white;
            cursor: pointer;
            padding: 18px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
        }
        .active, .collapsible:hover, .collapse:hover {
            background-color: #555;
        }
        .content {
            padding: 0 18px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s ease-out;
            background-color: #f1f1f1;
        }
        .line_enum {
            font-family: monospace;
            width: 4%;
            float: left;
            text-align: right;
            font-size: 10px;
            color: #fff;
            background-color: #909090;
        }
        .code {
            font-family: monospace;
            width: 95%;
            float: right;
            font-size: 10px;
        }
        #container {
            width: 100%;
        }
        #left_side {
            width: 27%;
            float: left;
        }
        #right_side {
            width: 73%;
            float: right;
        }
"""


#       JS scripts for pages
script = """
let coll = document.getElementsByClassName("collapsible");
let recoll = document.getElementsByClassName("collapse");
let i;
for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        let content = this.nextElementSibling;
        if (content.style.maxHeight){
            content.style.maxHeight = null;
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
        }
    });
}
for (let i = 0; i<recoll.length; i++) {
    recoll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        let content = this.parentElement;
        if (content.style.maxHeight){
            content.style.maxHeight = null;
        }
    });
}
"""


# standard documentation file
standard_file = """<!--ERRORS:0
*ERRORS-->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>"""+style+"""
    </style>
</head>
<body>
    <!--CONTENT-->
    <script>
"""+script+"""
    </script>
</body>
</html>
"""

# standard content of index file
sub_ix_content = """<!--HEADER-->
<div id='container'>
    <div id='left_side'>
        <h2>Files:</h2>
        <!--INDEX-->
    </div>
    <div id='right_side'>
        <h2>Files with paths:</h2>
        <!--INDEXED_PATHS-->
    </div>
</div>
<br>
"""

# class for conversion handling;
# a lot of work to understand; read docstrings and comments;
class _tag_:
    """
    Class `_tag_`
    ===
    Class that preserves data about found tags between substitutions and
    string cuts.
    """
    def __init__(self, context="", tag_start=r"[A-Z]\<", tag_stop=r"\>",
                 left_delim=r"\<", right_delim=r"\>", tag_map=tag_map2):
        self.context = context
        self.start = len(self.context)
        self.stop = len(self.context)
        self.opening = tag_start
        self.closing = tag_stop
        self.__right__ = right_delim
        self.__left__ = left_delim
        self.__tag__ = ""
        self.content = ""
        self.__map__ = tag_map
        self.child = None
        self.neighbour = []
        self.env = []
        #       0 returned after successful border search
        self.__status__ = self._find_borders(tag_start, tag_stop,
                                             left_delim, right_delim)
        if self.__status__ == 0:
            try:
                self.env = [self.context[:self.start],
                            self.context[self.stop:]]
                if re.search(_rm(tag_start+r"+[\s\S]*"+tag_stop+r"+"),
                             self.content) is not None:
                    self.child = _tag_(self.content)
                else:
                    self.content = self.content.translate(html_spec)
                for n in range(len(self.env)):
                    if re.search(_rm(tag_start+r"+[\s\S]*"+tag_stop+r"+"),
                                 self.env[n]) is not None:
                        self.neighbour += [_tag_(self.env[n])]
                    else:
                        self.env[n] = self.env[n].translate(html_spec)
                        self.neighbour += [None]
            #       try-except is not neccessary here, but to be sure...
            except ValueError:
                pass
        elif self.__status__ != 0:
            self.context = self.context.translate(html_spec)
    
    def _find_borders(self, tag_start, tag_stop, left_delim, right_delim):
        """
        `_tag_`.`_find_borders`
        ===
        Monstrosity that rips strings apart in order to extract `_tag_`
        objects properly.

        Return
        ---
        + 0 -> whole function passed properly, string contains object(s),
        tags are not broken;
        + 1 -> string has broken tag; only if no closing tags matching
        opening tag are found;
        + 2 -> no tags in string  

        """
        ###
        # Here comes the pain:
        ###
        ####
        # First section
        # ===
        # making sure that start tags match in number closing tags
        ####
        #       needed for tag start and stop
        _full_tag = tag_start+r"+[\s\S]*"+tag_stop+r"+"
        #       cutting working space
        _work_span = re.search(_rm(_full_tag), self.context)
        if _work_span is not None:
            # setting start
            self.start = _work_span.span()[0]
            _work_span = self.context[slice(*_work_span.span())]
            #       getting starts of tags to match the number of closing
            #       tags using delims because some parts may appear inside
            #       other types of tags 
            _beg = re.findall(_rm(left_delim), _work_span)
            #       number of open tags
            _len = len(_beg)
            #       setting len of tag to cut from content (removing
            #       borders) finding n-th end tag position
            _reg = _rm(r"(?:[^" + right_delim + r"]*" + 
                       right_delim + r"){" + str(_len) + r"}")
            _stop = re.search(_reg, _work_span)
            #       there should not be any broken tags inside this block,
            #       however double check doesn't hurt anyone
            if _stop is not None:
                self.stop = self.start + _stop.span()[1]
                self.content = self.context[self.start:self.stop]
            else:
                # logging print("Error: broken tag. End tag could not be found.")
                return 1
        else:
            if re.search(_rm(tag_start), self.context) is not None:
                # logging print("Error: broken tag. End tag could not be found.")
                return 1
            else:
                # logging print("Warning: parsed string does not contain any tags.")
                return 2
        
        ###
        # Second section
        # ===
        # making sure, that neighbours are not included and removing tags
        # from content
        ###
        _end = 0
        _f_tag = re.search(_rm(tag_start), self.content)
        _content = self.content
        if _f_tag is not None:
            _end = _f_tag.span()[1]
            _f_tag = 1
            _content = self.content[_end:]
            while _f_tag > 0 and len(self.content[_end:]) != 0:
                #       looking for delimiters of tags
                _start = re.search(_rm(left_delim), _content)
                _stop = re.search(_rm(right_delim), _content)
                #       handling if searches throw NoneType
                _st_pos = len(_content)
                _sp_pos = len(_content)
                #       setting proper postions
                if _stop is not None:
                    _sp_pos = _stop.span()[1]
                if _start is not None:
                    _st_pos = _start.span()[1]
                #       getting most-left match and choosing it's position
                _poss = [_sp_pos, _st_pos]
                _new_pos = min(_poss)
                #       adding to the _end
                _end += _new_pos
                _content = _content[_new_pos:]
                #       changing tag flag --> if _f_tag is zero, loop breaks
                _f_tag += 2*_poss.index(_new_pos)-1
            #       cutting end of content to contain only one obj
            self.content = self.content[:_end]
            #       setting stop where _end is
            self.stop = self.start + _end
            #       and place it as `self.__tag__`
            self.__tag__ = self.content
            #       `self.content` is only 'guts' of this object
            #       removing first '<' which corresponds to `B<` tag
            self.content = re.sub(_rm(tag_start), "", self.content,
                                  count=1)
            #       removing last '>' which is closing `>` tag
            self.content = re.sub(_rm(tag_stop), "", self.content[::-1],
                                  count=1)[::-1]
            return 0
        else:
            return 3
        
    def __str__(self):
        #       for eventual use
        return self.context

    def __copy__(self):
        #       for eventual use
        return _tag_(self.context, self.opening, self.closing,
                     self.__left__, self.__right__, self.__map__)

    def convert(self):
        """
        `_tag_`.`convert`
        ===

        Mapping tags by `self`.`__map__`

        Algorithm:
        ---
        Function must lead directly to child's and neighbour's conversion
        before converting `self` object. This way conversion will actually
        happen bottom to the top. To sustain this scheme of conversion
        neighbour's `convert` call has to happen next and will lead to 
        conversion of youngest of its descendants.
        
        Converted object must provide content for previous generations.
        To achieve that, object's `__tag__` is surrounded by environment,
        but only after converting this environment, which means calling
        neighbour's conversion first. This is the case, because before
        converting any object child and neighbours are converted first.

        Finally conversion of main object happens.

        Example:
        ---
        B<...B<...B<...>...>...>...B<...>...B<...>

        self -> object: B<...B<...B<...>...>...>...B<...>...B<...>
        {
            self.env = ["", "...B<...>...B<...>"]
            self.child -> object: ...B<...B<...>...>...
            {
                self.env = ["...", "..."]
                self.child -> object: ...B<...>...
                {
                    self.env = ["...", "..."]
                    self.neighbour -> None
                    self.child -> None
                }
                self.neighbour -> None
            }
            self.neighbour -> object: ...B<...>...B<...>
            {
                self.env = ["...", "...B<...>"]
                self.child -> None
                self.neighbour -> object: ...B<...>
                {
                    self.env = ["...", ""]
                    self.neighbour -> None
                    self.child -> None
                }
            }
        }

        Linear structure:
                   {......}
              {...B<......>...}
              {...B<......>...}                    {......}
         {...B<...B<......>...>...}    {......|...B<......>}
         {...B<...B<......>...>...|...B<......>...B<......>}
       {B<...B<...B<......>...>...>...B<......>...B<......>}
        B<...B<...B<......>...>...>...B<......>...B<......>
        <------------------------cx0---------------------->
          <----------cn0---------> <---------cx3---------->
          <---------cx1---------->      <cn3-> <---cx4....>
               <-----cn1----->                      <cn4->
               <----cx2------>
                    <cn2->
        
        cx -- context
        cn -- content
        {} -- string borders
        |  -- equivalent to `}{`

        Notes:
        The youngest child in a branch has inconvertible:
        + content -- `self`.`content` (str)
        + environment -- `self`.`env` (list: str)
        Conversion goes from youngest descendant (obj. 2.) and its ancestor
        (obj. 1.), then to neighbour's child (obj. 4.) and then neighbour
        (obj. 3.) and main object itself (obj. 0.). 
        """
        #       obj does not have child -> nothing to convert, content stays
        #       the same;
        #       obj does have a child   -> child is converted, content
        #       changes;
        if self.child is not None:
            self.child.convert()
            self.content = self.child.context
        #       for every neighbour;
        #       obj neighbour is converted -> environment (context of 
        #       neighbour) is being changed and environment updates;
        #       if obj does not have neighbours env is not changed;
        for n in range(len(self.neighbour)):
            if self.neighbour[n] is not None:
                self.neighbour[n].convert()
                self.env[n] = self.neighbour[n].context
        #       detecting type of tag to convert by tag_map;
        ####
        #       Actual conversion block
        _tag_type = None
        for key, val in self.__map__.items():
            #       check if specific tag from `self.__map__` matches the
            #       obejct's tag;
            _tag_type = re.match(_rm(key), self.__tag__)
            #       if `_tag_type` is None it is not converted thus context
            #       doesn't change;
            if _tag_type is not None:
                #       if `_tag_type` is not None, conversion takes place
                # self.content = self.content.translate(html_spec)
                self.__tag__ = re.sub(_rm(r"\*"), self.content, val)
                #       after converting `self.__tag__` to new shape there
                #       is a need to return context with changes; however
                #       context must contain converted neighbours as well:
                #       it uses `self.env` which is already converted 
                #       before this block;
                self.context = self.__tag__.join(self.env)
                # self.env = list(map(lambda s: s.translate(html_spec), self.env))
                #       conversion achieved, breaking the loop
                break
        #       after exiting the for loop check if conversion occurred

        if (_tag_type is None and
            re.search(_rm(self.opening + r"[\s\S]*" + self.closing),
                      self.content) is None):
            #       to indicate that for this object tags are not mapped 
            # logging print("Warning: No tag to convert or tag not recognized.")
            pass
        return str(self)


def get_match(pattern, string, regex=re.match):
    """
    `get_match`
    === 
    Checks if there is a match and return exact matching part for a pattern
    in string, using one of the RegEx matching functions. 
    """
    # regex is a specific `re` module's function which returns match obj
    reg = regex(pattern, string)
    if reg is not None:
        return string[slice(*reg.span())]
    else:
        return ""


def minor_tag(string, tag_map=tag_map2):
    """
    `minor_tag`
    ===
    Converting strings with X<> structured tag according to tag_map
    (`tag_map2`).

    For more information read docstrings and comments inside `_tag_` class.
    """
    element = _tag_(string, tag_map=tag_map)
    #       converting element according to default settings of _tag_
    #       constructor and `tag_map2` mapping variable
    element.convert()
    #       returning converted string
    return str(element)


def major_tag(string, tag_map=tag_map1):
    """
    `major_tag`
    ===
    Extracts string values for in-tag HTML construction and creates
    structure with proper content to be used in HTML document.
    """
    for key, val in tag_map.items():
        #       looking for a matching major tag (in one line)
        match = get_match(key, string)
        #       second part of if statement is to catch beginning of file
        if match is not "" or key is r"^":
            #       if match is not an empty string
            string = re.sub(re.compile(key), "", string)
            intag = get_match(val[0], string, re.search)
            rest = string.strip(intag)
            rest = re.sub(_rm(r"^\n\n"), "\n", rest)
            try:
                return (re.sub(re.compile(r"\*"), intag, val[1])
                        + clean(line_breaker(rest), left=False))
            except re.error:
                return (clean(intag).join(val[1].split("*"))
                        + clean(line_breaker(rest), left=False))
    return ""


def line_breaker(string, break_on="\n\n"):
    """
    `line_breaker`
    ===
    Converting double new-line symbol `\\n\\n` to line breaking tag `<br>`.
    """
    return re.sub(_rm(r"(?!^)"+break_on), "<br>\n", string)


def clean(string, left=True, right=True, guts=False):
    """
    `clean`
    ===
    Clean string from left/right-side and inner white characters.
    """
    rem = lambda reg: re.compile(reg, re.MULTILINE)
    if right:
        string = get_match(rem(r"[\s\S]*[^\n\t\r\s]"), string, re.search)
    if left:
        string = get_match(rem(r"[^\n\t\r\s][\s\S]*"), string, re.search)
    if guts:
        for ch in [r"\n", r"\t", r"\s", r"\r"]:
            if ch == r"\s":
                ch_sub = " "
            else:
                ch_sub = ch
            string = re.sub(rem(ch+r"{2,}"), ch_sub, string)
    return string


def get_tab(of_what, where):
    """
    `get_tab`
    ===
    Retrieve tabs that precede `of_what` string or regex.
    """
    tab = re.search(re.compile("[^\n]+?(?="+of_what+")"), where)
    if tab is not None:
        return where[slice(*tab.span())]
    else:
        return ""


def tab_shift(string, number=0, tab=""):
    """
    `tab_shift`
    ===
    Tab adding for prettier HTML formatting.
    """
    if tab == "":
        tab = number*"\t"
    string = ("\n"+tab).join(string.split("\n"))
    return string


def collapsible(name, inner_text):
    """
    `collapsible`
    ===
    Prepare code for collapsible div with name `name` and
    insides `inner_text`.
    """
    html="""<button class="collapsible">"""+name+"""</button>
    <div class='content'>
    """+inner_text+"""
    <button class="collapse">"""+name+"""</button>
    </div>"""
    return html


def code(code_str, lines_number):
    """
    `code`
    ===
    HTML code tags with side line enumeration.
    """
    # enum = [str(n)+".<br>\n" for n in range(1,lines_number+1)]
    enum = [str(n)+".\n" for n in range(1,lines_number+1)]
    enum = "".join(enum)
    html = ("<div class='container'>\n\t<div class='line_enum'>\n\t\t<pre>"+
            "\n\t\t\t<code>\n"+enum+"\n\t\t\t</code>\n\t\t</pre>\n\t</div>\n\t"+
            "<div class='code'>\n\t\t<pre>\n\t\t\t<code>\n"+code_str+"\n\t\t\t"+
            "</code>\n\t\t</pre>\n\t</div>\n</div>")
    return html


def update_errors(html_document, error_msg):
    """
    `update_errors`
    ===
    Update error number and information of HTML document
    """
    error_reg = re.compile(r"(?<=\<\!\-\-ERRORS\:)[\d]+", re.MULTILINE)
    errno = re.search(error_reg, standard_file)
    errno = int(standard_file[slice(*errno.span())])
    errno += 1
    err_com = "err("+str(errno)+"): " + error_msg
    html_document = re.sub(r"\*(?=ERRORS\-\-\>)", err_com, html_document, 1)
    return re.sub(error_reg, str(errno), html_document)


def get_err_no(html_document):
    """
    `get_err_no`
    ===
    Returns number of errors that ocurred while preparing document.
    """
    error_reg = re.compile(r"(?<=\<\!\-\-ERRORS\:)[\d]+", re.MULTILINE)
    errno = re.search(error_reg, html_document)
    errno = int(html_document[slice(*errno.span())])
    return errno



def main_index(main_path, target):
    error_reg = re.compile(r"(?<=\<\!\-\-ERRORS\:)[\d]+", re.MULTILINE)
    ix_page = document(main_path+target)
    ix_page = re.sub(r"\<\!\-\-CONTENT\-\-\>", sub_ix_content, ix_page)
    files, filepaths = file_list(main_path+target, ["pl", "pm"])
    header = ("<h1>Main index of "+os.path.abspath(main_path).translate(dictionary)+
              "</h1>\n<u>For document generation info check HTML source</u><br>\n")
    tab = re.search(r"[^\n]+?(?=(\<\!\-\-INDEX\-\-\>))", ix_page)
    errno = re.search(error_reg, ix_page)
    errno = int(ix_page[slice(*errno.span())])
    links = []
    links_full = []
    if tab is not None:
        tab = ix_page[slice(*tab.span())]
    else:
        errno += 1
        err_com = "err("+str(errno)+"):"+no_index
        ix_page = re.sub(r"\*(?=ERRORS\-\-\>)", err_com, ix_page, 1)
        tab = ""
    for n in range(len(files)):
        filepaths[n] = filepaths[n].translate(dictionary)
        filepaths[n] = "".join(filepaths[n].split(main_path))
        # filepaths[n] = re.sub(re.compile(path), "./", filepaths[n])
        links.append(html_link(filepaths[n], files[n]))
        links_full.append(html_link(filepaths[n], filepaths[n]))
    #       adding header
    if re.search(r"\<\!\-\-HEADER\-\-\>", ix_page) is None:
        errno += 1
        err_com = "err("+str(errno)+"):"+no_header
        ix_page = re.sub(r"\*(?=ERRORS\-\-\>)", err_com, ix_page, 1)
    ix_page = re.sub(r"\<\!\-\-HEADER\-\-\>", header, ix_page)
    #       creating html lists: left and right
    left_index = html_list(links)
    left_index = tab_shift(left_index, tab=tab)
    right_index = html_list(links_full)
    right_index = tab_shift(right_index, tab=tab)
    #       adding lists to html
    ix_page = re.sub(r"\<\!\-\-INDEX\-\-\>", left_index, ix_page)
    if re.search(r"\<\!\-\-INDEXED_PATHS\-\-\>", ix_page) is None:
        errno += 1    
        err_com = "err("+str(errno)+"):"+no_indexed
        ix_page = re.sub(r"\*(?=ERRORS\-\-\>)", err_com, ix_page, 1)
    ix_page = re.sub(r"\<\!\-\-INDEXED_PATHS\-\-\>", right_index, ix_page)
    #       updating error list
    ix_page = re.sub(error_reg, str(errno), ix_page)

    return ix_page


def sub_index(main_path, target):
    error_reg = re.compile(r"(?<=\<\!\-\-ERRORS\:)[\d]+", re.MULTILINE)
    ix_page = document(main_path+target)
    ix_page = re.sub(r"\<\!\-\-CONTENT\-\-\>", sub_ix_content, ix_page)
    path = os.path.join(main_path, target, "").translate(dictionary)
    _, dirs, files = next(os.walk(path))
    dirs = ["../"] + dirs
    header = ("<h1>Index of "+path+"</h1>\n<u>For document generation"+
              " info check HTML source.</u><br>\n<a href='/'>Main index</a><br>\n")
    errno = re.search(error_reg, ix_page)
    errno = int(ix_page[slice(*errno.span())])
    for n in range(len(dirs)):
        dirs[n] = os.path.join(dirs[n], "").translate(dictionary)
        dirs[n] = html_link(dirs[n], dirs[n])
    for n in range(len(files)):
        files[n] = html_link(files[n], files[n])
    tab = re.search(r"[^\n]+?(?=(\<\!\-\-INDEX\-\-\>))", ix_page)
    if tab is not None:
        tab = ix_page[slice(*tab.span())]
    else:
        errno += 1
        err_com = "err("+str(errno)+"): " + no_index
        ix_page = re.sub(r"\*(?=ERRORS\-\-\>)", err_com, ix_page, 1)
        tab = ""
    if re.search(r"\<\!\-\-HEADER\-\-\>", ix_page) is None:
        errno += 1
        err_com = "err("+str(errno)+"): " + no_header
        ix_page = re.sub(r"\*(?=ERRORS\-\-\>)", err_com, ix_page, 1)
    ix_page = re.sub(r"\<\!\-\-HEADER\-\-\>", header, ix_page)
    #       creating html lists: left and right
    left_index = "<h2>Directories:</h2>\n"+html_list(dirs)
    right_index = "<h2>Files:</h2>\n"+html_list(files)
    left_index = tab_shift(left_index, tab=tab)
    right_index = tab_shift(right_index, tab=tab)
    #       adding lists to html
    ix_page = re.sub(r"(?<=\<div id\=\'left\_side\'\>)[\s\S]+?(?=\<\/div\>)",
                     left_index+"\n"+(len(tab)-1)*"\t", ix_page)
    ix_page = re.sub(r"(?<=\<div id\=\'right\_side\'\>)[\s\S]+?(?=\<\/div\>)",
                     right_index+"\n"+(len(tab)-1)*"\t", ix_page)
    #       updating error list
    ix_page = re.sub(error_reg, str(errno), ix_page)
    return ix_page


def html_link(link_path, link_str):
    """
    `html_link`
    ===
    Generates structure of HTML link with
    `link_path` as address and `link_str` as
    visual string symbol in <a href...>`link_str`</a>
    """
    return "<a href=\""+link_path+"\">"+link_str+"</a>"


def html_list(elem_list, style_type="none"):
    """
    `html_list`
    ===
    Generates HTML list from `elem_list` with style bullet style
    `style_type`
    """
    result = ("<ul style=\"list-style-type:"+
              style_type+";\">\n<!--ELEMS--></ul>")
    listed = ""
    for el in elem_list:
        listed += "\t<li>"+el+"</li>\n"
    return re.sub(r"\<\!\-\-ELEMS\-\-\>", listed, result)


def header(html, header_content):
    """
    `header`
    ===
    Replacing comment <!--HEADER--> with string
    `header_content`. Header tags i.e. <h1></h1> have to be
    added around this string (function does not provide it).
    """
    return re.sub(r"\<\!\-\-HEADER\-\-\>", header_content, html)


def file_list(directory=".", ext=""):
    """
    `file_list`
    ===
    Listing files in specified directory and its subdirs with
    extension `ext`. Empty extension for listing all files.
    """
    if type(ext) == str:
        ext = [ext]
    for n in range(len(ext)):
        ext[n] = r"\." + ext[n] + "$"
    reg = "(" + "|".join(ext) + ")"
    files = []
    files_with_path = []
    walker = os.walk(directory)
    for p, _, f in walker:
        for fl in f:
            if re.search(r"[\s\S]+"+reg, fl) is not None:
                files.append(fl)
                files_with_path.append(p+"/"+fl)
    return files, files_with_path


def document(arg=""):
    """
    `document`
    ===
    Extract POD from a file and convert to HTML output
    """
    global standard_file
    std_file = standard_file
    global no_content
    global no_header
    global no_index
    global no_indexed
    content = ""
    try:
        with open(arg, "r", encoding="utf-8") as f_stream:
            pod_string = f_stream.read()
        pod_document = re.split(re.compile(r"^\=", re.MULTILINE),
                                pod_string)
        doc_len = sum(1 for line in open(arg, encoding="utf-8"))
        code_str = pod_string.translate(html_spec)
        content += f"""<a href="/">Main index</a>&nbsp;<a href="./">Folder index</a>"""
        code_html = collapsible("+ Code", code(code_str, doc_len))
        if len(pod_document) == 1:
            content += "<h1>FILE: "+arg+"</h1>"
            content += code_html
            std_file = update_errors(std_file, no_doc)
        else:
            content += code_html
        #       main POD conversion
        for n in range(len(pod_document)):
            content += major_tag(_tag_(pod_document[n]).convert())+"\n"
        std_file_split = std_file.split("<!--CONTENT-->")
        if len(std_file_split) == 1:
            std_file = "".join(std_file_split)
            std_file = update_errors(std_file, no_content)
        else:
            std_file = content.join(std_file_split)
        header = re.search(r"(?<=\<h1\>)[\s\S]+?(?=\<\/h1\>)", std_file)
        if header is not None and get_err_no(std_file) != 0:
            header = get_match(r"\<h1\>[\s\S]+?<\/h1\>", std_file, re.search)
            header += "\n<u>Some errors occurred. Check file source for more info.</u><br>\n"
            std_file = re.sub(r"\<h1\>[\s\S]+?\<\/h1\>", header, std_file)
        # else:
        return std_file
    except FileNotFoundError:
        content += f"<b>File not found: {arg}</b><br>\n"
        content += """<a href="/"><<< Back to main page</a><br>\n"""
        content += line_breaker(__doc__, "\n") + "\n"
        std_file = std_file.split("<!--CONTENT-->")
        if len(std_file) == 1:
            std_file = "".join(std_file)
            std_file = update_errors(std_file, no_content)
        else:
            std_file = content.join(std_file)
        return std_file
    except (PermissionError, IsADirectoryError):
        if os.path.isdir(arg):
            return std_file
        else:
            content += f"<b>Permission denied for a file: {arg}</b><br>\n"
            content += """<a href="/"><<< Back to main page</a><br>\n"""
            content += line_breaker(__doc__, "\n") + "\n"
            std_file = std_file.split("<!--CONTENT-->")
            if len(std_file) == 1:
                std_file = "".join(std_file)
                std_file = update_errors(std_file, no_content)
            else:
                std_file = content.join(std_file)
            return std_file

if __name__=="__main__":
    print(document("C:/Users/robert.rasala/Desktop/BRM/brm/base/apps/tp_bill/tp_bill.pl"))
    # try:
    #     print(document(sys.argv[1]))
    # except IndexError:
    #     print(main(""))
