#!/bin/bash
say() {
    ./venv/bin/aws polly synthesize-speech --output-format mp3 --voice-id Joanna --text "$*" tmp.mp3;
    local IFS=+;/usr/bin/mplayer -af volume=10:1 -ao alsa -noconsolecontrols tmp.mp3;
    rm tmp.mp3
}
say $*
