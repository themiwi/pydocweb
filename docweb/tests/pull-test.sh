#!/bin/bash
#
# Extract docstrings from the test sample module.
#

if test "$1" = ""; then
    echo "Usage: pull-test.sh OUTPUTFILE"
    exit 1
fi

set -e

export SITEPATH=$PWD/../../scripts/tests

python2.5 $PYDOCTOOL collect -s $SITEPATH \
    sample_module \
| $PYDOCTOOL prune -i - \
| $PYDOCTOOL numpy-docs -i - -s $SITEPATH \
    -f $SITEPATH/sample_module/add_newdocs.py \
| $PYDOCTOOL sphinx-docs -i - \
    $SITEPATH/sample_module/doc \
> "$1"
