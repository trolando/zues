#!/bin/sh

python manage.py dumpdata --all --natural-foreign --indent 2 sites zues > zues/fixtures/demo_data.json
