#!/bin/bash

does_pypi_version_exist () {
    pkg_name=$1; version=$2
    pip3 index versions "$pkg_name" | [[ $(cat) == *$version* ]]
}

pkg_version=$(cat phc/version.py | sed 's/[^0-9.]*\([0-9.]*\).*/\1/')
if does_pypi_version_exist phc "$pkg_version"; then
    echo "Package version $pkg_version has already been published to PyPi; exiting early"
    exit 0
fi

echo "Building the package"
make package

echo "Publishing package version $pkg_version to PyPi"
make deploy
