#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
SYMDIR="$ROOT/Numerical_instabilities/symbolics"
CONTAINER=FPGen
TARGET_DIR=/home/fptesting/FPTesting/example

if ! docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
  echo "Container $CONTAINER not found. Start container first." >&2
  exit 1
fi

# Copy symbolics to container example dir
for f in "$SYMDIR"/*.c; do
  echo "Copying $(basename $f) to container..."
  docker cp "$f" "$CONTAINER:$TARGET_DIR/"
done

echo
cat <<'USAGE'
Now inside the container run the following for each symbolic file:

cd /home/fptesting/FPTesting/example
# compile to bitcode and link FP injection (example filenames vary per repo)
./compile.sh <symbolic-file.c>
# run a short KLEE run (adjust timeout in sample script)
./run_klee_short.sh <bitcode.bc> 30

After run completes, on the host run:
bash Numerical_instabilities/generate_inputs.sh
USAGE
