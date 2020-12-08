#!/bin/bash

# Init text
echo '############################################'
echo '# Run the ogame bot'
echo '# modified by edelblistar@kuppelwieser.net'
echo '############################################'
echo ''

# Update ogame pip
echo '# install python lib ogame'
echo ''
#pip uninstall --yes ogame
pip install ogame

# Run bot
echo '# run bot script'
echo 
python application.py