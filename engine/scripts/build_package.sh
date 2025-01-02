#!/bin/bash

PROJECT_DIR=$(pwd)
SOURCE_DIR="$PROJECT_DIR/src/"
DEST_DIR="$PROJECT_DIR/packages/"
VERSION=$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version)
ZIP_NAME="data_flow_engine-$VERSION.zip"

cd "$SOURCE_DIR" || { echo "Error: Could not find path $SOURCE_DIR"; exit 1; }
zip -r "$ZIP_NAME" ./* || { echo "Error: Could not create zip file"; exit 1; }
mv "$ZIP_NAME" "$DEST_DIR" || { echo "Error: Could not move file to $DEST_DIR"; exit 1; }
cd $PROJECT_DIR
echo "Package built in $DEST_DIR"
