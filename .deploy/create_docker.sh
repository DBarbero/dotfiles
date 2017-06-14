#!/usr/bin/env bash
ng build

docker build --rm -t eu.gcr.io/optimal-life-112611/app-name:0.0.0 .
