# -*- coding: utf-8 -*-
"""
docserv
===
Documentation server. Uses `docpod.py` to generate HTML documentation
from POD format and then serves it under localhost:<port>. Port number is
assigned dynamically and returned by this server at start.

Usage:
---
python docserv.py <name_of_main_directory>

Name of main directory is scanned for files and if they contain POD-formatted
documentation

Returns:
---
+ `Serving @: localhost:<port_number>`
+ Server messages

Author
---
Robert K. Rasała

Accenture

October/November 2019
"""

import socket
import sys
import os
import subprocess
import re
import time
import docpod

no_index = ("no INDEX special comment tags detected. Without it"+
            " file/directory index cannot be inserted.\n*")
no_indexed = ("no INDEXED_PATHS special comment tags detected. Without it"+
              " file/directory index cannot be inserted.\n*")
no_header = ("no HEADER special comment tags detected. Without it file/directory"+
             "index cannot be inserted.\n*")

def send_html_frame(conn):
    conn.send(b'HTTP/1.0 200 OK\n')
    conn.send(b'Content-type:text/html;charset=utf8\n')
    conn.send(b'\n')

while True:
    try:
        try:
            main_dir = sys.argv[1]
        except IndexError:
            main_dir = "./"
        main_dir = os.path.join("", main_dir, "")
        main_dir = main_dir.translate(docpod.dictionary)
        abs_main_dir = os.path.abspath(main_dir).translate(docpod.dictionary)
        port = 49999
        s = socket.socket()
        s.bind(('', port))
        s.listen(5)
        print(f"Serving {abs_main_dir} @: localhost:{port}")

        try:
            while True:
                srt = time.process_time()
                #       target is path from main_dir
                target = ""
                #       accept connections
                c, addr = s.accept()
                #       get requests in utf-8
                request = c.recv(1000).decode("utf-8")
                #       try-except for unrecognized requests 
                try:
                    #       removing requests for favicon
                    if request.find("favicon") is -1:
                        target = re.search(re.compile(r"[\s\S]*(?=\sHTTP)",
                                                        re.MULTILINE),
                                            request)

                        if target is not None:
                            target = re.sub(r"GET \/", "", request[slice(*target.span())])
                        else:
                            target = ""
                except AttributeError:
                    print(request)
                try:
                    if target == "":
                        send_html_frame(c)
                        c.send(bytearray(docpod.main_index(main_dir, target), encoding="utf-8"))
                        c.close()
                        end = time.process_time()
                        print(f"{addr}: Main index of {main_dir} ({time.process_time()-srt}s)")
                        # c.send()
                    else:
                        if os.path.isfile(main_dir+target):
                            send_html_frame(c)
                            c.send(bytearray(docpod.document(main_dir+target), encoding="utf-8"))
                            c.close()
                            print(f"{addr}: File: {target} ({time.process_time()-srt}s)")
                        elif os.path.isdir(main_dir+target):
                            if target[-1] != "/":
                                c.send(bytearray("HTTP/1.0 301 Moved Permanently\n"+
                                                 "Location: "+target.split("/")[-1]+"/\n", encoding="utf-8"))
                                c.close()
                                continue
                            # target = os.path.join(target, "").translate(indexer.dictionary)
                            send_html_frame(c)
                            c.send(bytearray(docpod.sub_index(main_dir, target), encoding="utf-8"))
                            c.close()
                            print(f"{addr}: Index of {target} ({time.process_time()-srt}s)")
                        else:
                            send_html_frame(c)
                            c.send(bytearray(docpod.document(main_dir+target), encoding="utf-8"))
                            c.close()
                            print(f"{addr}: Unknown path: {main_dir + target} ({time.process_time()-srt}s)")
                except BrokenPipeError:
                    pass
                
        except KeyboardInterrupt:
            c.close()
            exit()
    except ConnectionAbortedError as e:
        print(e)
        print("Serving is continued.")
        pass
        # while True:
        #     print(str(e))
        #     msg = input("Continue serving?\n")
        #     if msg in ["yes", "y", "Y"]:
        #         break
        #     if msg in ["no", "n", "N"]:
        #         print("Exiting.")
        #         exit()