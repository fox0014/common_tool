#!/bin/bash

port='22756'
bwlimit='10000'
descodedir="/evlinkdata/data/backup/mysqlbackup/"
srccodedir="/evcharge/databack/mysqlbak"

remote_server=$(echo "iZbp120t9nsrhswnpg4a45Z iZbp1h470k1r457img4zl9Z  iZbp1cex1ltxqvo1knka9sZ $RANDOM" | awk '{print $($NF%(NF-1)+1)}')
echo $remote_server

rsync -e "ssh -p $port" -uvrtzpP --progress --bwlimit=$bwlimit root@${remote_server}:${descodedir} ${srccodedir}

