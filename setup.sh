#!/bin/bash -x
/usr/bin/mysqldump -uroot --no-data --create-options  --skip-add-drop-table so_testing | /bin/sed 's/AUTO_INCREMENT=[0-9][0-9]*//g' > ./db.sql
