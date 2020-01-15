#!/usr/bin/env bash

# Script which copies the .github directory to enable templates and other github dotfile
# functionality to all the pack repos
# NOTE: It assumes packs repos are cloned in a local directory where the script runs

for PACK_DIR in syncurity-*; do
    echo "Processing pack: ${PACK_DIR}"
    PACK_DIR=`realpath ${PACK_DIR}`

    cd ${PACK_DIR}
    if [[ ! -d ".github" ]]; then
        echo "Creating .github directory"
        mkdir .github
    fi
    cp ~/repos/ci/.github/* ${PACK_DIR}/.github/.
    git add .github/*
    git commit -m "Update .github templates from ci repo."
    git push origin master
    cd ..
done
