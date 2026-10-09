class ZeppelinEmbed < Formula
  desc "In-process vector, lexical, and hybrid search for macOS"
  homepage "https://github.com/zepdb/zeppelin-embed"
  url "https://github.com/zepdb/zeppelin-embed/releases/download/v0.7.0/zeppelin-embed-macos-arm64.tar.gz"
  version "0.7.0"
  sha256 "c7e92f10a2fd48c6b3cd72a420ffdda5ccbadf326c137ab6fa5db2290c932861"
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
