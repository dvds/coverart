#!/bin/bash

# import virtualenv functions
source "virtualenv-functions"

# exit if virtual environment cannot be created
if [ ! create_virtualenv_with_pip_requirements ]
then
    exit 1
fi

# exit if ghostscript is not installed
if ! __check_apt_packages_installed ghostscript
then
    exit 1
fi

# declare variables
OUTPUT_FILENAME="DVDs.ps"

# execute the generator
python -B coverart-index-generator.py "$OUTPUT_FILENAME"

if [ $? -ne 0 ]
then
    # exit with failure
    destroy_virtualenv
    exit 1
fi

ps2pdf -dAutoFilterColorImages=false -dColorImageFilter=/FlateEncode "$OUTPUT_FILENAME"

if [ $? -ne 0 ]
then
    # exit with failure
    destroy_virtualenv
    exit 1
fi

rm "$OUTPUT_FILENAME"

if [ $? -ne 0 ]
then
    # exit with failure
    destroy_virtualenv
    exit 1
fi

# exit with success
destroy_virtualenv
exit 0