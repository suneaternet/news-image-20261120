#!/usr/bin/env python3
"""News poster 20 Nov 2026 — decode the poster from base64 text, validate
it, and hand it in as entry.png. Standard library only."""

import base64
import os
import struct
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ENCODED = os.path.join(ROOT, "assets", "poster.png.b64")
DECODED = os.path.join(ROOT, "poster.png")
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
CHUNK = 64 * 1024


def fail(message):
    raise SystemExit(f"news-image-20261120: {message}")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        fail("MAKEFUN_OUTPUT_DIR is not set")
    if not os.path.exists(ENCODED):
        fail("assets/poster.png.b64 is missing")
    with open(ENCODED, "r", encoding="ascii") as handle:
        text = handle.read().strip()
    try:
        data = base64.b64decode(text, validate=True)
    except Exception as exc:
        fail(f"base64 decode failed: {exc}")
    if len(data) > MAX_BYTES:
        fail(f"poster is {len(data)} bytes, over the {MAX_BYTES} byte limit")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("poster is not a PNG file")
    if len(data) < 24:
        fail("poster is too short for a PNG header")
    (length,) = struct.unpack(">I", data[8:12])
    if data[12:16] != b"IHDR" or length != 13:
        fail("poster has no valid IHDR chunk")
    (width, height) = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0 or width > MAX_SIDE or height > MAX_SIDE:
        fail(f"poster is {width}x{height}, over the {MAX_SIDE}x{MAX_SIDE} limit")
    with open(DECODED, "wb") as handle:
        handle.write(data)
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        fail(f"cannot create output directory {out_dir}: {exc}")
    dest = os.path.join(out_dir, "entry.png")
    with open(DECODED, "rb") as src, open(dest, "wb") as dst:
        while True:
            block = src.read(CHUNK)
            if not block:
                break
            dst.write(block)
    if os.path.getsize(dest) != len(data):
        fail("entry.png size does not match poster.png")
    with open(DECODED, "rb") as first, open(dest, "rb") as second:
        while True:
            a = first.read(CHUNK)
            b = second.read(CHUNK)
            if a != b:
                fail("entry.png does not match poster.png")
            if not a:
                break
    print(f"handed in: entry.png ({len(data)} bytes, {width}x{height})")


if __name__ == "__main__":
    main()
