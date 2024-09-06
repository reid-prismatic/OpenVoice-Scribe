#!/bin/bash

xattr -d com.apple.quarantine scribe_tts_v1_collection/*
xattr -d com.apple.quarantine scribe_tts_v1_collection/_internal/**/*.dylib
xattr -d com.apple.quarantine scribe_tts_v1_collection/_internal/**/*.so

find ./_internal/ -type f -exec xattr -d com.apple.quarantine {} +