# YCHFX — YCH 去特效精简版

基于 [YqlossClientHarmony](https://ych.yqloss.net)（作者 Yqloss）的 **GPLv2** 源码修改，
只保留「去特效（Effect Remover）」，去掉回放（Replay）与其余可选功能。
原项目在 1.5.0 上回放功能频繁崩溃，故做此精简版。

## 保留 / 移除清单

**保留**
- `Features/ModifyLoadingLevel` — 去特效的全部实现（4 个 Harmony patch）
- `Gui/Pages/EffectRemoverPage` — 去特效设置页
- `Gui/Pages/LanguagePage`、`I18N`、`Gui/YCHLayout*`、`Utilities/*`

**移除**
- `Features/Replay`（14 个类）— 回放，崩溃来源
- `Features/BlockUnintentionalEscape`、`LimitRecolorTrack`、`PlaySoundOnGameEnd`、
  `FixKillerDecorationsInNoFail` — 四个其它可选功能
- `Features/Interoperation.cs` — 只服务于回放（给别的 mod 用的开关）
- `Gui/Pages/ReplayPage`、`OtherFeaturesPage`

移除后的 Harmony patch 只剩 4 个，全部属于去特效：

| 目标方法 | 作用 |
|---|---|
| `LevelData.LoadLevel` | 标记「正在读关卡」 |
| `RDFile.ReadAllText` | **核心**：读关卡 JSON 时删掉被勾选的 action / decoration |
| `scnEditor.SaveLevel` | 改过关卡时保存前确认 |
| `scnEditor.SaveAndQuit` | 同上 |

## 与原 YCH 的差异

| 项 | 原 YCH | YCHFX |
|---|---|---|
| Info.json Id | `YCH` | `YCHFX` |
| 程序集 | `YCH.dll`（175 KB） | `YCHFX.dll`（94 KB） |
| Harmony Id | `YCH` | `YCHFX` |
| 入口方法 | `YqlossClientHarmony.Main.Load` | 同（namespace 未改） |
| 去��效预设 | 有（自己配的 profile） | 有（作者内置的「YCH」预设，首次进游戏写入） |

两者**可以共存**（Id / 程序集名 / Harmony Id 都不同，关掉一个不影响另一个的 patch），
但去特效配置**各存各的**，不会互通 —— 验证时建议只开一个。

## 构建

```bash
cd 本目录
python build.py
```

产物：`bin\Release\YCHFX.dll`（0 错误 0 警告）。

`YqlossClientHarmony.csproj` 里 `GameRoot` 要指向本机游戏目录
（默认已填 `D:\softwell\steamapps\common\A Dance of Fire and Ice`，换机器要改）。
三个坑（都踩过，已写进 csproj 注释）：
1. `%(FullPath)` 与 `$(MSBuildProjectDirectory)\...` 是相对项目目录解析的，
   绝对路径只能出现在 `$(GameRoot)` 一处，否则报 MSB4023。
2. `**\*.dll` 这种 glob 不支持带盘符的绝对路径，引用要逐个列（`ItemGroup` + `@(GameDll)`）。
3. 工程 `EnableDefaultItems=false`，首次构建必须先 `/restore` 生成 `obj\project.assets.json`
   （`build.py` 已自动处理）。

## 安装

把 `YCHFX/` 整个目录放进游戏的 `Mods\` 下即可（Info.json + YCHFX.dll + Languages\）。

## 许可与致谢

原项目 GPLv2，本衍生作品同样按 GPLv2 发布。`LICENSE` 与原作者署名完整保留
（`Properties/AssemblyInfo.cs` 里 `AssemblyCopyright("Copyright © 2025 Yqloss")` 未改）。
去特效功能的全部实现与界面均来自原作者，仅删减功能范围，未改动其逻辑。