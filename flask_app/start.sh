#!/bin/bash

mkdir log
gunicorn -c gun.py app:app --daemon

# 保留一个 bash
/bin/bash
