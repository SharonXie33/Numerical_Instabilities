#!/usr/bin/env bash
set -euo pipefail
KT='/home/fptesting/klee-float/build/bin/ktest-tool'
INDIR="${KLEE_OUT:-/home/fptesting/FPTesting/example/klee-out-1}"
OUTF="$INDIR/inputs.txt"
rm -f "$OUTF"
for k in "$INDIR"/test*.ktest; do
    [ -e "$k" ] || continue
  # try multiple ktest-tool paths
  for KT_TOOL in /home/fptesting/klee-float/build/bin/ktest-tool /home/fptesting/FPTesting/utils/ktest-tool /home/fptesting/FPTesting/src/klee-float/build/bin/ktest-tool; do
    if [ -x "$KT_TOOL" ]; then
      $KT_TOOL --write-floats "$k" > /tmp/ktest_tmp.txt 2>/dev/null || true
      break
    fi
  done
  # extract numeric lines (floats) from ktest-tool output
  vals=$(grep -E "^-?([0-9]+\.[0-9]*|\.[0-9]+|[0-9]+(\.[0-9]*)?([eE][-+]?[0-9]+)?)$" /tmp/ktest_tmp.txt -A0 || true)
  vals=$(echo "$vals" | tr '\n' ',' | sed 's/,$//')
    if [ -z "$vals" ]; then
    # fallback: locate 'input' in ktest file, read length and payload, decode as little-endian floats
    decoded=$(python3 - "$k" <<'PY'
import sys,struct
p=sys.argv[1]
b=open(p,'rb').read()
idx=b.find(b'input')
if idx==-1:
    sys.exit(0)
s=idx+len(b'input')
# length appears stored as big-endian 4-byte integer
length=int.from_bytes(b[s:s+4],'big')
payload=b[s+4:s+4+length]
if len(payload)>=4:
    n=len(payload)//4
    vals=struct.unpack('<%df'%n, payload[:n*4])
    print(','.join(map(str,vals)))
PY
)
    if [ -n "$decoded" ]; then
      echo "$(basename "$k") : $decoded" >> "$OUTF"
    else
      echo "$(basename "$k") : 0x$(xxd -p -l 64 "$k" | tr -d '\n')" >> "$OUTF"
    fi
    else
    echo "$(basename "$k") : $vals" >> "$OUTF"
    fi
done
echo "wrote $OUTF"
