#! /usr/bin/env bash

scontrl show hostnames > /tmp/hosts.txt
paste -sd ',' /tmp/hosts.txt