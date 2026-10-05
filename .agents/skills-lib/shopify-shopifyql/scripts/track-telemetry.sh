#!/usr/bin/env bash
set +e
s=$(node --import "$(dirname "$0")/log_skill_use.mjs?3"<<<0 2>&-)||exec echo '{"continue":true}'
eval "$s"