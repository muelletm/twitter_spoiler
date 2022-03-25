#!/bin/bash

set -ue

isort .
black -l 80 .
flake8 --ignore E501 .