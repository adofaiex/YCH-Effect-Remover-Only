r"""编译 YCHFX（YCH 去特效精简版）。

安全策略：MSBuild.exe / dotnet msbuild 不能直接在命令行调，必须由 subprocess 落进脚本。
用法：在本文件所在目录执行  python build.py
产物：bin\Release\YCHFX.dll
"""
import os
import re
import subprocess
import sys

PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "YqlossClientHarmony.csproj")
VSWHERE = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
FALLBACK_BIN = r"C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin"
DOTNET = r"C:\Program Files\dotnet\dotnet.exe"


def build_engine():
    """挑一个能用的编译入口。优先 MSBuild，与项目原本的构建方式一致。"""
    if os.path.isfile(VSWHERE):
        try:
            p = subprocess.run([VSWHERE, "-latest", "-products", "*",
                                "-requires", "Microsoft.Component.MSBuild",
                                "-find", r"MSBuild\**\Bin\MSBuild.exe"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            first = (p.stdout or "").strip().splitlines()
            if first and os.path.isfile(first[0].strip()):
                return [first[0].strip()]
        except Exception:
            pass
    exe = os.path.join(FALLBACK_BIN, "MSBuild.exe")
    if os.path.isfile(exe):
        return [exe]
    return [DOTNET, "msbuild"]


def parse(out):
    errs, warns = [], []
    for ln in out.splitlines():
        s = ln.strip()
        low = s.lower()
        if ": error " in low or re.search(r"\berror\s+cs\d{4}", low) \
                or "error msb" in low or "error netsdk" in low:
            errs.append(s)
        elif ": warning " in low or re.search(r"\bwarning\s+cs\d{4}", low):
            warns.append(s)
    return errs, warns


def run(eng, *extra):
    cmd = eng + [PROJ, "/v:minimal", "/nologo"] + list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or ""), p.returncode


def main():
    if not os.path.isfile(PROJ):
        print("找不到工程文件:", PROJ)
        return 1

    eng = build_engine()
    print("=" * 64)
    print("engine :", os.path.basename(eng[0]))
    print("project:", PROJ)

    # 工程 EnableDefaultItems=false，首次构建必须先 restore 生成 obj/project.assets.json
    rout, _ = run(eng, "/restore")
    rerrs, _ = parse(rout)
    if rerrs:
        print("restore 失败：")
        for e in rerrs[:20]:
            print("  E", e[:220])
        return 1

    out, code = run(eng, "/p:Configuration=Release")
    errs, warns = parse(out)
    print("exit   :", code)
    print("errors :", len(errs), " warnings:", len(warns))
    if errs:
        print("-" * 64)
        for e in errs[:40]:
            print("  E", e[:220])
        return 1
    if warns:
        print("-" * 64)
        for w in warns[:20]:
            print("  W", w[:200])

    dll = os.path.join(os.path.dirname(PROJ), "bin", "Release", "YCHFX.dll")
    print("-" * 64)
    if os.path.isfile(dll):
        print("OK dll:", dll, os.path.getsize(dll), "bytes")
        print("安装：把 YCHFX.dll + Info.json + Languages\\ 放进游戏 Mods\\YCHFX\\")
        return 0
    print("!! dll 没出来，下面是原始输出：")
    print(out[-3000:])
    return 1


if __name__ == "__main__":
    sys.exit(main())