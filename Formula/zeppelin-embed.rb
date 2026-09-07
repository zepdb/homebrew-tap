class ZeppelinEmbed < Formula
  desc "In-process vector, lexical, and hybrid search for macOS"
  homepage "https://github.com/zepdb/zeppelin-embed"
  url "https://github.com/zepdb/zeppelin-embed/releases/download/v0.2.1/zeppelin-embed-macos-arm64.tar.gz"
  version "0.2.1"
  sha256 "9b9c2a5d7459614fac5b98dae42ad081757c7a567ac662caea4bc06623609025"
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

      int main(void) {
        return ze_abi_version() == ZE_ABI_VERSION ? 0 : 1;
      }
    C

    system ENV.cc, "abi.c", "-I#{include}", "-L#{lib}",
                   "-lzeppelin_embed_ffi", "-Wl,-rpath,#{lib}", "-o", "abi"
    system "./abi"
  end
end
