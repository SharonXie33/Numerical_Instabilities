#!/usr/bin/env python3
"""Parse KLEE .ktest files into inputs.txt and inputs.csv.

Usage: ktest_to_inputs.py [KLEE_OUT_DIR]
If KLEE_OUT_DIR not provided will use KLEE_OUT env or a reasonable default.
This script will try to call `ktest-tool` if available in PATH; otherwise it falls
back to a small binary parser that searches for an 'input' chunk and unpacks
little-endian floats.
"""
import subprocess, glob, re, struct, os, sys, shutil, csv

def find_ktest_tool():
    # prefer a ktest-tool in PATH
    kt = shutil.which('ktest-tool')
    if kt:
        return kt
    # common container paths (kept for compatibility)
    candidates = [
        '/home/fptesting/klee-float/build/bin/ktest-tool',
        '/home/fptesting/FPTesting/utils/ktest-tool',
        '/home/fptesting/FPTesting/src/klee-float/build/bin/ktest-tool'
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def parse_with_ktest_tool(ktest_tool, path):
    try:
        p = subprocess.run([ktest_tool, '--write-floats', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        out = p.stdout
    except Exception:
        return None
    # collect float-like lines
    vals = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        # accept numeric-like lines
        if re.match(r"^-?([0-9]+\.[0-9]*|\.[0-9]+|[0-9]+)([eE][-+]?[0-9]+)?$", line):
            vals.append(float(line))
    return vals if vals else None


def fallback_binary_parse(path):
    try:
        b = open(path, 'rb').read()
    except Exception:
        return None
    idx = b.find(b'input')
    if idx == -1:
        return None
    s = idx + len(b'input')
    if s + 4 > len(b):
        return None
    length = int.from_bytes(b[s:s+4], 'big')
    payload = b[s+4:s+4+length]
    if len(payload) < 4:
        return None
    n = len(payload) // 4
    try:
        vals = list(struct.unpack('<%df' % n, payload[:n*4]))
    except Exception:
        # fallback to hex
        return ['0x' + payload.hex()]
    return vals


def main():
    if len(sys.argv) > 1:
        indir = sys.argv[1]
    else:
        indir = os.environ.get('KLEE_OUT', '/home/fptesting/FPTesting/example/klee-out-1')
    indir = os.path.abspath(indir)
    outf_txt = os.path.join(indir, 'inputs.txt')
    outf_csv = os.path.join(indir, 'inputs.csv')

    ktests = sorted(glob.glob(os.path.join(indir, 'test*.ktest')))
    if not ktests:
        print('no ktest files found in', indir, file=sys.stderr)
        sys.exit(1)

    ktest_tool = find_ktest_tool()
    lines = []
    csv_rows = []
    for k in ktests:
        vals = None
        if ktest_tool:
            vals = parse_with_ktest_tool(ktest_tool, k)
        if vals is None:
            vals = fallback_binary_parse(k)
        if vals is None:
            print('no data for', k, file=sys.stderr)
            continue
        # normalize values to strings for text output
        str_vals = []
        for v in vals:
            if isinstance(v, float):
                # preserve repr for nan/inf
                str_vals.append(repr(v))
            else:
                str_vals.append(str(v))
        line = os.path.basename(k) + ' : ' + ','.join(str_vals)
        lines.append(line)
        # CSV: filename, "v1,v2,v3"
        csv_rows.append([os.path.basename(k), ','.join(str_vals)])

    with open(outf_txt, 'w') as f:
        f.write('\n'.join(lines))
    with open(outf_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['testfile', 'values'])
        for r in csv_rows:
            writer.writerow(r)

    print('wrote', outf_txt, 'and', outf_csv, 'with', len(lines), 'lines')


if __name__ == '__main__':
    main()
