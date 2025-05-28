#!/bin/bash

docker build -f Dockerfile.dev -t a4s-eval-dev .
docker run --rm -v .:/app -p 8001:8001 --name a4s-eval-dev -it a4s-eval-dev

