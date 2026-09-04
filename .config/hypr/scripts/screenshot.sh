#!/bin/bash
DIR="/home/cetos/Pictures/Screenshots"
mkdir -p "$DIR"
FILE="$DIR/screenshot_$(date +'%Y-%m-%d_%H-%M-%S').png"

grim -g "$(slurp)" - | satty --filename - --output-filename "$FILE"
