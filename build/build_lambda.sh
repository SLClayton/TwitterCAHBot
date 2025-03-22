#!/bin/bash

# Move into the directory where this script is located
cd "$(dirname "$0")" || exit

# Define the name of the output package and the temporary directory to build it
PACKAGE_NAME="lambda_package"
BUILD_DIR="temp_build_dir"
OUT_DIR="packages"

# Ensure the output directory exists
mkdir -p "$OUT_DIR"

# Create a directory to store the build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp -R ../src/* "$BUILD_DIR/"

# Install the required packages directly into the build directory
python -m pip install -r ../requirements.txt --target="$BUILD_DIR/"
