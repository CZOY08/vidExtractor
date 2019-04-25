#!/bin/bash
rm /data/ftp/pics.zip
cd /data
/root/cut.py
zip -P U2I3gb23sdahghn5kKH523JBDSG32235798 -r /data/ftp/pics.zip /data/pics 
