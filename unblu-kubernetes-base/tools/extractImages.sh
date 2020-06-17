#!/usr/bin/env sh
egrep -o "image: (.*)" | cut -d " " -f2 | sort | uniq