#!/usr/bin/env bash
set -euo pipefail

# generate_inputs.sh
# 1) create a python parser inside the FPGen container
# 2) run it there to produce inputs.txt in the container klee-out dir
# 3) copy klee-out-1 and inputs.txt back to host ./Numerical_instabilities

CONTAINER="FPGen"
CONTAINER_KLEE_OUT="/home/fptesting/FPTesting/example/klee-out-1"
CONTAINER_PY="/home/fptesting/FPTesting/example/ktest_to_inputs.sh"
HOST_DIR="$(pwd)/Numerical_instabilities"
HOST_KLEE_OUT="$HOST_DIR/klee-out-1"

mkdir -p "$HOST_DIR"

echo "[1/5] Ensure container '$CONTAINER' exists and is running..."
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "Container $CONTAINER not found. Please start the FPGen container and retry." >&2
  exit 1
fi

# write the python parser into a local file and copy into the container
echo "[2/5] Using parser script: tools/ktest_to_inputs.sh"
LOCAL_PY="tools/ktest_to_inputs.sh"

docker cp "$LOCAL_PY" "$CONTAINER:$CONTAINER_PY"

# make it executable
# run the parser inside the container (it will create inputs.txt in container klee-out)
echo "[3/5] Running parser inside container to produce inputs.txt"
docker exec -ti "$CONTAINER" bash -lc "bash $CONTAINER_PY"

# copy klee-out-1 directory and inputs.txt to host
echo "[4/5] Copying klee-out-1 and inputs.txt to host: $HOST_DIR"
rm -rf "$HOST_KLEE_OUT" || true
docker cp "$CONTAINER:$CONTAINER_KLEE_OUT" "$HOST_KLEE_OUT"

# also copy inputs.txt if it exists (it should be inside the copied dir)
if [ -f "$HOST_KLEE_OUT/inputs.txt" ]; then
  echo "[5/5] inputs.txt is available at: $HOST_KLEE_OUT/inputs.txt"
  echo "--- head of inputs.txt ---"
  sed -n '1,20p' "$HOST_KLEE_OUT/inputs.txt"
else
  echo "inputs.txt not found in $HOST_KLEE_OUT" >&2
  # try to docker cp specifically
  docker cp "$CONTAINER:$CONTAINER_KLEE_OUT/inputs.txt" "$HOST_DIR/inputs.txt" || true
  if [ -f "$HOST_DIR/inputs.txt" ]; then
    echo "Found inputs.txt at $HOST_DIR/inputs.txt"
    sed -n '1,20p' "$HOST_DIR/inputs.txt"
  else
    echo "Failed to retrieve inputs.txt" >&2
    exit 1
  fi
fi

echo "Done. Host directory: $HOST_DIR"
