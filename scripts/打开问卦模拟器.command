#!/bin/zsh
set -euo pipefail

# WenguaApp: build and open the EXISTING offline iPhone app in Xcode Simulator.
# UI launcher only. Never modifies V8 templates, source matrices or algorithms.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "问卦模拟器启动失败：$1" >&2; exit 1; }

[[ "$(uname -s)" == "Darwin" ]] || fail "请在已安装 Xcode 的 Mac 上运行。"
command -v xcodebuild >/dev/null 2>&1 || fail "请先从 App Store 安装完整 Xcode。"
command -v xcrun >/dev/null 2>&1 || fail "没有找到 Xcode 命令行工具。"
command -v xcodegen >/dev/null 2>&1 || fail "请先运行 brew install xcodegen 安装 XcodeGen。"
command -v python3 >/dev/null 2>&1 || fail "请安装 Xcode Command Line Tools（需要 python3）。"

PROJECT_DIR="$ROOT/ios/WenguaAppUI"
(
  cd "$PROJECT_DIR"
  xcodegen generate --spec project.yml
)
PROJECT="$PROJECT_DIR/WenguaApp.xcodeproj"
[[ -d "$PROJECT" ]] || fail "没有生成 WenguaApp.xcodeproj。"
open -a Xcode "$PROJECT"

SIM_ID="$(xcrun simctl list -j devices available | python3 -c '
import json,sys
devices=json.load(sys.stdin).get("devices",{})
candidates=[]
for runtime in sorted(devices,reverse=True):
    if "iOS" not in runtime: continue
    for d in devices[runtime]:
        if d.get("isAvailable",True) and d.get("name","").startswith("iPhone"):
            candidates.append(d)
candidates.sort(key=lambda d: d.get("state")!="Booted")
print(candidates[0]["udid"] if candidates else "")
')"
[[ -n "$SIM_ID" ]] || fail "没有可用 iPhone Simulator。请在 Xcode > Settings > Platforms 安装 iOS Simulator Runtime。"

open -a Simulator
xcrun simctl boot "$SIM_ID" >/dev/null 2>&1 || true
xcrun simctl bootstatus "$SIM_ID" -b

DERIVED="$HOME/Library/Developer/Xcode/DerivedData/WenguaLocalSimulator"
LOG="${TMPDIR:-/tmp}/WenguaApp-simulator-build.log"
echo "正在用本机 Xcode 编译问卦 iPhone Simulator App……"
if ! xcodebuild -project "$PROJECT" -scheme WenguaApp -configuration Debug \
     -sdk iphonesimulator -destination "platform=iOS Simulator,id=$SIM_ID" \
     -derivedDataPath "$DERIVED" CODE_SIGNING_ALLOWED=NO build >"$LOG" 2>&1; then
    tail -n 90 "$LOG" >&2
    fail "Xcode 编译未通过，完整日志在 $LOG"
fi

APP="$DERIVED/Build/Products/Debug-iphonesimulator/问卦.app"
[[ -d "$APP" ]] || fail "找不到真实编译好的问卦.app。"
for resource in health_energy_200.json 81_pairs.tsv reading_template.json actor_profiles.json; do
    [[ -f "$APP/$resource" ]] || fail "App 缺少正式源资源：$resource"
done
xcrun simctl install "$SIM_ID" "$APP"
xcrun simctl launch "$SIM_ID" com.wengua.ios
echo "已在 iPhone Simulator 打开问卦。工程：$PROJECT"
echo "本脚本只编译/安装/启动 App；V8.0 模板、起盘及计分代码均未修改。"
