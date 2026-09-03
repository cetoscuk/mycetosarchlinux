#!/usr/bin/env bash
cal | sed "s/$(date +%e)/[$(date +%e)]/"
