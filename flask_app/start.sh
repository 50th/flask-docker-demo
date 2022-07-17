#!/bin/bash

mkdir log
gunicorn -c gun.conf app:app --daemon

# 保留一个 bash
/bin/bash
