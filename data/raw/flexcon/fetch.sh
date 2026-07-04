#!/bin/bash
# fetch.sh <url> <outfile>
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
url="$1"
out="$2"
sleep 1
curl -sS --compressed -L -A "$UA" --max-time 60 -o "$out" -w "%{http_code} %{url_effective}\n" "$url"
