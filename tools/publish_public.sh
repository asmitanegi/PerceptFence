#!/usr/bin/env bash
# publish_public.sh — project committed internal HEAD to the PUBLIC repository.
# Never copies the live working tree: ignored/untracked local files cannot ship.
#
# Usage:
#   tools/publish_public.sh /path/to/public-repo [--dry-run]
#
# The committed snapshot is exported, private/ is removed, and the destination's
# Git metadata is preserved. The public repo must pass without private/.
set -euo pipefail

DEST="${1:-}"
DRY="${2:-}"
if [[ -z "$DEST" ]]; then
  echo "usage: tools/publish_public.sh /path/to/public-repo [--dry-run]" >&2
  exit 2
fi

SOURCE_ROOT="$(git rev-parse --show-toplevel)"
DEST="$(cd "$DEST" && pwd)"

if [[ -n "$(git -C "$SOURCE_ROOT" status --porcelain)" ]]; then
  echo "FATAL: internal source tree is dirty; commit or stash before publishing." >&2
  exit 1
fi
if ! git -C "$DEST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "FATAL: destination is not a Git worktree: $DEST" >&2
  exit 1
fi
if [[ -n "$(git -C "$DEST" status --porcelain)" ]]; then
  echo "FATAL: public destination tree is dirty; refusing destructive sync." >&2
  exit 1
fi

DEST_REMOTE="$(git -C "$DEST" remote get-url origin 2>/dev/null || true)"
if [[ ! "$DEST_REMOTE" =~ (^|[:/])asmitanegi/PerceptFence(\.git)?$ ]]; then
  echo "FATAL: destination origin is not asmitanegi/PerceptFence: $DEST_REMOTE" >&2
  exit 1
fi

SNAPSHOT="$(mktemp -d "${TMPDIR:-/tmp}/perceptfence-public.XXXXXX")"
trap 'rm -rf "$SNAPSHOT"' EXIT
git -C "$SOURCE_ROOT" archive --format=tar HEAD | tar -xf - -C "$SNAPSHOT"
rm -rf "$SNAPSHOT/private"

if [[ -e "$SNAPSHOT/private" ]]; then
  echo "FATAL: private/ remained in committed public snapshot." >&2
  exit 1
fi

# A normal clone has a .git directory; a linked worktree has a .git file.
# Preserve either shape or rsync --delete will detach the destination worktree.
RSYNC_OPTS=(-a --delete --exclude=.git)
if [[ "$DRY" == "--dry-run" ]]; then
  RSYNC_OPTS+=(--dry-run -v)
  echo "=== DRY RUN — nothing copied. Below is what WOULD be published to $DEST ==="
fi

rsync "${RSYNC_OPTS[@]}" "$SNAPSHOT"/ "$DEST"/

if [[ "$DRY" != "--dry-run" ]]; then
  if ! grep -qxF '/private/' "$DEST/.gitignore"; then
    printf '\n# Public projection: internal control plane must never be committed here.\n/private/\n' >> "$DEST/.gitignore"
  fi
  if [[ -e "$DEST/private" ]]; then
    echo "FATAL: private/ leaked into $DEST — aborting. Remove it before publishing." >&2
    exit 1
  fi
  python3 "$DEST/tools/verify_public_tree.py"
  echo "Published committed HEAD to $DEST (private/ excluded)."
  echo "Now verify IN the public repo:"
  echo "  cd $DEST && python3 tools/verify_submission.py && python3 -m pytest tests/ -q"
fi
