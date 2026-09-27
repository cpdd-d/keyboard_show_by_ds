# 🐟 键盘 + 鼠标 输入显示

一个轻量级的制作基于“蓝色大肥鱼”的 Windows 桌面小工具，实时在屏幕一角显示你按下的**键盘按键**和**鼠标操作**。平时完全**鼠标穿透**，不挡任何点击；需要调整时右键圆环弹出菜单即可。

> 特别适合录屏、教学演示、直播、远程协助等场景，让观众一眼看到你在按什么键。

---

## ✨ 特性

- 🎯 **实时按键显示**：字母、数字、符号、F1–F12、方向键、修饰键（Ctrl / Shift / Alt / Win）
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




❓ 常见问题
Q：为什么我按键没反应？

A：请确认：

在"设置 → 键盘按键显示"里已经开启

输入法处于英文状态（中文输入法的按键在程序里无法可靠捕获）

Q：窗口跑到屏幕外面找不到了怎么办？

A：右键托盘图标 → 设置 → 调整位置…，可以精确设定坐标或一键吸附到屏幕角落。

Q：设置里改颜色时看不到预览？

A：预览区域在对话框顶部，拖动调色板时会实时刷新。

Q：会不会被某些程序挡住？

A：程序每 2 秒检查一次窗口层级，正常应用都能盖过去。以下情况无法置顶（Windows 系统限制）：

UAC 安全桌面

Ctrl+Alt+Del 界面

部分全屏独占游戏



# 🐟 Keyboard + Mouse Input Overlay
A lightweight Windows desktop utility based on "Big Blue Fat Fish". It displays your pressed **keyboard keys** and **mouse actions** in real‑time at a corner of your screen.
The window is fully **click‑through** when idle and will not block any mouse clicks. Right‑click the ring handle to open the menu for configuration.

> Ideal for screen recording, teaching demos, live streaming and remote support. Lets viewers instantly see which keys you are pressing.

---
## ✨ Features
- 🎯 **Real‑time key display**: Letters, numbers, symbols, F1‑F12, arrow keys and modifier keys (Ctrl / Shift / Alt / Win)
- 🖱️ **Mouse action display**: Left‑click, right‑click, middle‑click, scroll wheel up / down
- 🔗 **Combination key support**: Combinations such as `Ctrl+Shift+S` are shown as one single card instead of three separate ones
- ⏱️ **Long‑press duration tracking**: When a key is held longer than 0.6 seconds, its hold time like `A*2s` will be shown upon release
- 🖥️ **Click‑through window**: The window becomes completely transparent to mouse input while idle and never interferes with normal operations
- ⭕ **Ring handle**: The ring brightens when your mouse hovers over it; right‑click brings up the menu
- 🎨 **Color themes**: 5 built‑in themes, plus custom text and background colors for keyboard and mouse cards
- 🔤 **Custom fonts**: Supports `.ttf` / `.otf` / `.ttc` font files
- 🎬 **Smooth animations**: Cards slide in from off‑screen, arrange side‑by‑side, fade out, shrink and slide away upward or leftward
- 📌 **Always‑on‑top enforcement**: Periodically checks window layering to prevent losing top‑most status after switching input methods or windows
- 📦 **Single‑instance mode**: Re‑launching the program activates the existing window instead of opening duplicate instances
- ⚙️ **Instant‑apply settings**: All preferences are saved to QSettings and automatically restored on next launch

Requires Python environment, pyqt5 and pynput.

## ❓ FAQ
Q: Why are my keystrokes not showing up?
A: Please verify:
The option is enabled under *Settings → Keyboard Key Display*.
Your input method is set to English. Keystrokes from Chinese input methods cannot be reliably captured by this program.

Q: The window moved off‑screen and I cannot find it. What can I do?
A: Right‑click the tray icon → Settings → Adjust Position… You can set exact coordinates or snap the window to any screen corner with one click.

Q: I cannot see previews when changing colors in settings.
A: The preview area is at the top of the settings dialog. Previews refresh live as you drag the color picker.

Q: Can it display Chinese characters?
A: Not currently supported. On Windows, pynput can only read physical hardware keystrokes and cannot obtain candidate characters from input‑method software.

Q: Can some applications cover this overlay?
A: The program checks window layering every two seconds and stays above most regular applications. Certain scenarios are restricted by Windows system rules and cannot stay on top:
- UAC secure desktop
- Ctrl+Alt+Del screen
- Some full‑screen exclusive games








