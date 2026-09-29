#!/bin/sh

celery -A config worker --loglevel=INFO --pool=solo
