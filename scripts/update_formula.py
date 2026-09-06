#!/usr/bin/env python3
"""Update the tap from the latest published Zeppelin Embed SDK release."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY = "zepdb/zeppelin-embed"
ASSET_NAME = "zeppelin-embed-macos-arm64.tar.gz"
VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?")
EXPECTED_MEMBERS = {
    "zeppelin-embed-macos-arm64/LICENSE",
    "zeppelin-embed-macos-arm64/README.md",
    "zeppelin-embed-macos-arm64/include/zeppelin_embed.h",
    "zeppelin-embed-macos-arm64/lib/libzeppelin_embed_ffi.a",
    "zeppelin-embed-macos-arm64/lib/libzeppelin_embed_ffi.dylib",
}


def request(url: str) -> bytes:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "zepdb-homebrew-tap",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(
        urllib.request.Request(url, headers=headers)
    ) as response:
        return response.read()


def latest_release() -> tuple[str, str, bytes] | None:
    api_url = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
    try:
        release = json.loads(request(api_url))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            print(
                "No published Zeppelin Embed release exists yet; leaving the tap unchanged."
            )
            return None
        raise

    tag = release["tag_name"]
    if not tag.startswith("v") or VERSION_RE.fullmatch(tag[1:]) is None:
        raise SystemExit(f"latest release has an invalid tag: {tag!r}")
    assets = [asset for asset in release["assets"] if asset["name"] == ASSET_NAME]
    if len(assets) != 1:
        raise SystemExit(f"release {tag} must contain exactly one {ASSET_NAME} asset")
    url = assets[0]["browser_download_url"]
    return tag[1:], url, request(url)


def verify_archive(archive: bytes) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        members = {member.name.rstrip("/") for member in package.getmembers()}
    missing = EXPECTED_MEMBERS - members
    if missing:
        raise SystemExit(f"SDK archive is missing required members: {sorted(missing)}")


def render_formula(version: str, url: str, sha256: str) -> str:
    return f'''class ZeppelinEmbed < Formula
  desc "In-process vector, lexical, and hybrid search for macOS"
  homepage "https://github.com/zepdb/zeppelin-embed"
  url "{url}"
  version "{version}"
  sha256 "{sha256}"
  license "GPL-3.0-only"

  depends_on arch: :arm64
  depends_on macos: :big_sur

  def install
    include.install "include/zeppelin_embed.h"
    lib.install "lib/libzeppelin_embed_ffi.a"
    lib.install "lib/libzeppelin_embed_ffi.dylib"
    pkgshare.install "README.md"
  end

  test do
    (testpath/"abi.c").write <<~C
      #include <stdint.h>
      #include <zeppelin_embed.h>

      int main(void) {{
        return ze_abi_version() == ZE_ABI_VERSION ? 0 : 1;
      }}
    C

    system ENV.cc, "abi.c", "-I#{{include}}", "-L#{{lib}}",
                   "-lzeppelin_embed_ffi", "-Wl,-rpath,#{{lib}}", "-o", "abi"
    system "./abi"
  end
end
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--url")
    parser.add_argument(
        "--output", type=Path, default=Path("Formula/zeppelin-embed.rb")
    )
    args = parser.parse_args()

    local_mode = (
        args.version is not None or args.archive is not None or args.url is not None
    )
    if local_mode:
        if args.version is None or args.archive is None:
            raise SystemExit("--version and --archive must be provided together")
        if VERSION_RE.fullmatch(args.version) is None:
            raise SystemExit(f"invalid release version: {args.version!r}")
        version = args.version
        archive = args.archive.read_bytes()
        url = args.url or (
            f"https://github.com/{REPOSITORY}/releases/download/v{version}/{ASSET_NAME}"
        )
    else:
        release = latest_release()
        if release is None:
            return
        version, url, archive = release

    verify_archive(archive)
    sha256 = hashlib.sha256(archive).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_formula(version, url, sha256))
    print(f"Rendered Zeppelin Embed {version} with SHA-256 {sha256}")


if __name__ == "__main__":
    main()
