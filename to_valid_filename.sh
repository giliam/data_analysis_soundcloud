#!/bin/bash

ls data/rap | while read -r FILE
do
    mv -v "data/rap/$FILE" `echo data/rap/$FILE | tr ' ' '_' `
done
