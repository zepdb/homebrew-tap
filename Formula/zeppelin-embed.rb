class ZeppelinEmbed < Formula
  desc "In-process vector, lexical, and hybrid search for macOS"
  homepage "https://github.com/zepdb/zeppelin-embed"
  url "https://github.com/zepdb/zeppelin-embed/releases/download/v0.3.0/zeppelin-embed-macos-arm64.tar.gz"
  version "0.3.0"
  sha256 "4b0aa7e5d3be86452bb38a6b2ce28f5d40656a11a5ede47e5557b0cfb796f6e5"
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
