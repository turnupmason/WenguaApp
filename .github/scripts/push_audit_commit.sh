#!/usr/bin/env bash
# Keep generated uncommitted test artifacts while publishing an audit commit.
# Rebase never overwrites remote work; an actual conflict remains a failure.
set -euo pipefail
for attempt in 1 2 3 4 5; do
  git -c rebase.autoStash=true pull --rebase origin main
  if git push origin HEAD:main; then
    exit 0
  fi
done
exit 1
