#!/bin/bash

for i in audio/*/*/*.wav; do
    new_name=${i/%.wav}
    ffmpeg -n -i $i -strict -2 $new_name.m4a;
done

for i in audio/*/*/*.m4a; do
    new_name=${i/%.m4a}
    ffmpeg -n -i $i $new_name.mp3;
    # ffmpeg -n -i $i $new_name.wav;
    ffmpeg -n -i $i -dash 1 $new_name.webm;
    # ffmpeg -n -i $i $new_name.ogg;
done
