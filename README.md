# 🐟 键盘 + 鼠标 输入显示

一个轻量级的制作基于“蓝色大肥鱼”的 Windows 桌面小工具，实时在屏幕一角显示你按下的**键盘按键**和**鼠标操作**。平时完全**鼠标穿透**，不挡任何点击；需要调整时右键圆环弹出菜单即可。

> 特别适合录屏、教学演示、直播、远程协助等场景，让观众一眼看到你在按什么键。

---

## ✨ 特性

- 🎯 **实时按键显示**：字母、数字、符号、F1–F24、方向键、修饰键（Ctrl / Shift / Alt / Win，左右键都能识别）、小键盘锁定/滚动锁定/打印屏幕/暂停、音量与媒体控制键
- 🖱️ **鼠标操作显示**：左键 / 右键 / 中键 / 滚轮上下
- 🔗 **组合键支持**：`Ctrl+Shift+S` 这类组合会合并为一张卡片，不会拆成三张
- ⏱️ **长按计时**：按住某个键超过 0.6 秒，松开后显示 `A*2s` 这样的持续时间
- 🖥️ **鼠标穿透**：闲置时窗口对鼠标完全透明，绝不干扰正常操作
- ⭕ **圆环抓手**：鼠标移到圆环上时圆环会变亮，右键即可弹出菜单
- 🎨 **主题色**：内置 5 套主题，或自定义键盘/鼠标卡片的文字与背景色
- 🔤 **自定义字体**：支持加载 `.ttf` / `.otf` / `.ttc` 字体文件
- 🎬 **流畅动画**：卡片从屏幕外滑入、并排显示、淡出缩小后向左/上滑出
- 📌 **强制置顶**：周期检查窗口层级，防止切输入法/切窗口后掉层
- 📦 **单实例运行**：重复启动只会唤起已有窗口，不会打开多个
- ⚙️ **设置即时生效**：所有修改保存到 QSettings，下次启动自动恢复

---

## 🚀 运行

需要 Python 3.8+（Windows）。

```bash
pip install -r requirements.txt
python main.py
```

依赖只有两个：

| 依赖 | 用途 |
| --- | --- |
| `PyQt5` | 窗口、绘制、托盘、设置界面 |
| `pynput` | 全局键盘 / 鼠标监听 |

> 托盘图标与程序图标取自仓库根目录的 `ips.png` / `ips.ico`。

## 📦 打包

安装 PyInstaller 后运行仓库里的 `db.bat`，它支持两种打包方式：

```bash
pip install pyinstaller

db.bat            # 默认：单文件，输出 dist\inputshow.exe
db.bat onedir     # 目录版，输出 dist\inputshow\inputshow.exe
db.bat onefile    # 等同不带参数
db.bat both       # 两种都打
```

| | onefile | onedir |
| --- | --- | --- |
| 产物 | 单个 `inputshow.exe`（31 MB） | `dist\inputshow\` 整个目录（44 MB） |
| 启动 | 每次启动都要把整包解压到 `%TEMP%` | 直接从目录运行，**不解压** |
| 启动速度 | 较慢（有解压开销） | 快 |
| 分发 | 只发一个文件 | 必须整个目录一起发 |
| 风险 | 解压这一步可能被安全软件拦截（实测 360 会偶发导致 `Could not create temporary directory!` 而启动失败） | 无此问题 |

> **建议优先用 `onedir`**：它规避了"启动时解压到临时目录"这一最容易出问题的环节。
> 如果遇到 onefile 版双击没反应，先换 onedir 版试试。

脚本已剔除 QtWebEngine、numpy 等无用模块，自动使用 `ips.ico` 作为程序图标，
并在 `C:\upx` 存在时启用 UPX 压缩（不存在则自动改用 `--noupx`）。

## 🔤 换字体

程序**不内置字体**，默认使用系统自带的 `Microsoft YaHei`。想换字体有两种方式：

1. 右键圆环 → 设置 → 字体 → **浏览字体文件…**，选择 `.ttf` / `.otf` / `.ttc`（路径会记住）；
2. 把字体文件放进 `assets/fonts/`，启动时会自动扫描并出现在字体菜单里。

详见 [assets/fonts/README.md](assets/fonts/README.md)。

## 🖼️ 截图

![screenshot](docs/screenshot.jpg)

---

## ❓ 常见问题

**Q：为什么我按键没反应？**

A：请确认：

- 在“设置 → 键盘按键显示”里已经开启；
- 输入法处于英文状态（中文输入法的按键在程序里无法可靠捕获）。

**Q：窗口跑到屏幕外面找不到了怎么办？**

A：右键托盘图标 → 设置 → 调整位置…，可以精确设定坐标或一键吸附到屏幕角落。

**Q：设置里改颜色时看不到预览？**

A：预览区域在对话框顶部，拖动调色板时会实时刷新。

**Q：能不能显示中文按键？**

A：暂不支持。pynput 在 Windows 上无法获取输入法的候选字符，只能拿到物理按键。

**Q：会不会被某些程序挡住？**

A：程序每 2 秒检查一次窗口层级，正常应用都能盖过去。以下情况无法置顶（Windows 系统限制）：

- UAC 安全桌面
- Ctrl+Alt+Del 界面
- 部分全屏独占游戏

---
---

# 🐟 Keyboard + Mouse Input Overlay

A lightweight Windows desktop utility based on "Big Blue Fat Fish". It displays your pressed **keyboard keys** and **mouse actions** in real-time at a corner of your screen.
The window is fully **click-through** when idle and will not block any mouse clicks. Right-click the ring handle to open the menu for configuration.

> Ideal for screen recording, teaching demos, live streaming and remote support. Lets viewers instantly see which keys you are pressing.

## ✨ Features

- 🎯 **Real-time key display**: Letters, numbers, symbols, F1-F24, arrow keys, modifier keys (Ctrl / Shift / Alt / Win, both left and right), Num Lock / Scroll Lock / Print Screen / Pause, and the volume / media keys
- 🖱️ **Mouse action display**: Left-click, right-click, middle-click, scroll wheel up / down
- 🔗 **Combination key support**: Combinations such as `Ctrl+Shift+S` are shown as one single card instead of three separate ones
- ⏱️ **Long-press duration tracking**: When a key is held longer than 0.6 seconds, its hold time like `A*2s` will be shown upon release
- 🖥️ **Click-through window**: The window becomes completely transparent to mouse input while idle and never interferes with normal operations
- ⭕ **Ring handle**: The ring brightens when your mouse hovers over it; right-click brings up the menu
- 🎨 **Color themes**: 5 built-in themes, plus custom text and background colors for keyboard and mouse cards
- 🔤 **Custom fonts**: Supports `.ttf` / `.otf` / `.ttc` font files
- 🎬 **Smooth animations**: Cards slide in from off-screen, arrange side-by-side, fade out, shrink and slide away upward or leftward
- 📌 **Always-on-top enforcement**: Periodically checks window layering to prevent losing top-most status after switching input methods or windows
- 📦 **Single-instance mode**: Re-launching the program activates the existing window instead of opening duplicate instances
- ⚙️ **Instant-apply settings**: All preferences are saved to QSettings and automatically restored on next launch

## 🚀 Getting started

Requires Python 3.8+ on Windows.

```bash
pip install -r requirements.txt
python main.py
```

## 📦 Build

`db.bat` supports two packaging modes:

```bash
pip install pyinstaller

db.bat            # default: onefile  -> dist\inputshow.exe
db.bat onedir     # folder build      -> dist\inputshow\inputshow.exe
db.bat onefile    # same as no argument
db.bat both       # build both
```

| | onefile | onedir |
| --- | --- | --- |
| Output | single `inputshow.exe` (31 MB) | whole `dist\inputshow\` folder (44 MB) |
| Startup | unpacks the archive into `%TEMP%` every launch | runs in place, **no unpacking** |
| Speed | slower (unpack cost) | faster |
| Sharing | send one file | send the whole folder |
| Risk | the unpack step can be blocked by security software (observed with 360: `Could not create temporary directory!`) | none |

> **`onedir` is recommended** — it avoids the unpack-to-temp step entirely.
> If the onefile build does not start when double-clicked, try the onedir build.

## ❓ FAQ

**Q: Why are my keystrokes not showing up?**

A: Please verify:

- The option is enabled under *Settings → Keyboard Key Display*.
- Your input method is set to English. Keystrokes from Chinese input methods cannot be reliably captured by this program.

**Q: The window moved off-screen and I cannot find it. What can I do?**

A: Right-click the tray icon → Settings → Adjust Position… You can set exact coordinates or snap the window to any screen corner with one click.

**Q: I cannot see previews when changing colors in settings.**

A: The preview area is at the top of the settings dialog. Previews refresh live as you drag the color picker.

**Q: Can it display Chinese characters?**

A: Not currently supported. On Windows, pynput can only read physical hardware keystrokes and cannot obtain candidate characters from input-method software.

**Q: Can some applications cover this overlay?**

A: The program checks window layering every two seconds and stays above most regular applications. Certain scenarios are restricted by Windows system rules and cannot stay on top:

- UAC secure desktop
- Ctrl+Alt+Del screen
- Some full-screen exclusive games
