#!/bin/sh
#
#	Generate the documentation using pdoc (http://pdoc.burntsushi.net/pdoc)
#
export PYTHONPATH=`pwd`
pdoc  --overwrite --html-no-source --html --external-links --template-dir doc/template --html-dir doc onem2mlib

