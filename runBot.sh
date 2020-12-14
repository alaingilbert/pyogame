#!/bin/bash

# Init text
echo '############################################'
echo '# Run the ogame bot'
echo '# modified by edelblistar@kuppelwieser.net'
echo '############################################'
echo ''

# Remove ogame pip
echo '# install python lib ogame'
echo ''
#pip uninstall --yes ogame

# Install libs
pip install ogame
pip install loguru

# Run bot
echo '# run bot script'
echo 
python application.py