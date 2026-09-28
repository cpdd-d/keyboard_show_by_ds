#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""键盘 + 鼠标 输入显示"""
import math
import os
import sys
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMenu, QAction, QActionGroup,
    QSystemTrayIcon, QColorDialog, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox,
    QGridLayout, QSpinBox,
)
from PyQt5.QtCore import (
    Qt, QTimer, QRectF, QPointF, QPoint, QSettings,
    QCoreApplication, pyqtSignal,
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QFont, QFontDatabase, QFontMetrics,
    QIcon, QPixmap, QRegion,
)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_NAME = "BlueFatFishPet_SingleInstance_v1"

# ---------- 逻辑尺寸 ----------
BASE_W, BASE_H = 380, 110
CARD_H = 28
CARD_PAD = 22
CARD_GAP = 6
CARD_RADIUS = 9
CARD_PEN_W = 1.8
RING_R = 16
RING_HIT_PAD = 10

ROW_KB_Y = 34
ROW_MS_Y = 78

DEFAULT_FONT_SIZE = 10
IDLE_RING_DELAY = 5.0
DEFAULT_FPS = 60
MAX_VISIBLE = 3
FADE_IN = 0.12
FADE_OUT = 0.30
SLIDE_IN_DIST = 60
SLIDE_OUT_DIST = 45

MIN_VISIBLE = 40
LONG_PRESS_THRESHOLD = 0.6
TOPMOST_INTERVAL = 2000
KEY_STUCK_TIMEOUT = 5.0
RENDER_PAUSE_TIMEOUT = 30.0

# ---------- 颜色 ----------
C_RING = QColor(0x3A, 0x5A, 0xB0)
C_RING_HOVER = QColor(0x60, 0x88, 0xE8)
C_KB_EDGE = QColor(0x1E, 0x30, 0x68)
C_MS_EDGE = QColor(0xE0, 0x80, 0x30)
C_ADJUST_BORDER = QColor(0xFF, 0x88, 0x00, 200)

DEFAULT_THEME = {
    "kb_text": "#243366",
    "kb_bg": "#FFFFFF",
    "ms_text": "#804010",
    "ms_bg": "#FFF3E0",
}

THEMES = {
    "默认蓝橙": dict(DEFAULT_THEME),
    "暗夜": {
        "kb_text": "#EAEAEA", "kb_bg": "#2A2D34",
        "ms_text": "#FFD08A", "ms_bg": "#3A3F48",
    },
    "清新绿": {
        "kb_text": "#1B5E20", "kb_bg": "#E8F5E9",
        "ms_text": "#00695C", "ms_bg": "#E0F2F1",
    },
    "樱花粉": {
        "kb_text": "#880E4F", "kb_bg": "#FCE4EC",
        "ms_text": "#6A1B9A", "ms_bg": "#F3E5F5",
    },
    "极简灰": {
        "kb_text": "#222222", "kb_bg": "#F5F5F5",
        "ms_text": "#222222", "ms_bg": "#E8E8E8",
    },
}

DUR_OPTIONS = [("1 秒", 1.0), ("1.5 秒", 1.5),
               ("2 秒", 2.0), ("3 秒", 3.0)]
SCALE_OPTIONS = [("小", 0.8), ("中", 1.0), ("大", 1.3)]
CARDSIZE_OPTIONS = [("紧凑", 0.85), ("标准", 1.0), ("宽松", 1.2)]
FPS_OPTIONS = [("30 fps", 30), ("60 fps", 60),
               ("90 fps", 90), ("120 fps", 120)]
FSIZE_OPTIONS = [("小 8", 8), ("中 10", 10),
                 ("大 12", 12), ("特大 14", 14)]


# ==========================================================
#  位置对话框
# ==========================================================
class PositionDialog(QDialog):
    def __init__(self, pet):
        super().__init__(pet)
        self.pet = pet
        self.setWindowTitle("调整位置")
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(300)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(-20000, 20000)
        self.x_spin.setValue(pet.x())
        self.x_spin.setFixedWidth(90)
        self.x_spin.valueChanged.connect(self._on_spin_changed)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(-20000, 20000)
        self.y_spin.setValue(pet.y())
        self.y_spin.setFixedWidth(90)
        self.y_spin.valueChanged.connect(self._on_spin_changed)

        row_xy = QHBoxLayout()
        row_xy.addWidget(QLabel("X:"))
        row_xy.addWidget(self.x_spin)
        row_xy.addSpacing(10)
        row_xy.addWidget(QLabel("Y:"))
        row_xy.addWidget(self.y_spin)
        row_xy.addStretch(1)

        grid = QGridLayout()
        grid.setSpacing(6)
        presets = [
            ("↖ 左上", "tl", 0, 0),
            ("↑ 顶部", "tc", 0, 1),
            ("↗ 右上", "tr", 0, 2),
            ("↙ 左下", "bl", 1, 0),
            ("↓ 底部", "bc", 1, 1),
            ("↘ 右下", "br", 1, 2),
        ]
        for label, key, r, c in presets:
            btn = QPushButton(label)
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda _=False, k=key: self._preset(k))
            grid.addWidget(btn, r, c)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        row_bottom = QHBoxLayout()
        row_bottom.addStretch(1)
        row_bottom.addWidget(btn_close)

        vbox = QVBoxLayout(self)
        vbox.addLayout(row_xy)
        vbox.addWidget(QLabel("快速吸附到屏幕："))
        vbox.addLayout(grid)
        vbox.addLayout(row_bottom)

    def sync_from_pet(self):
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.x_spin.setValue(self.pet.x())
        self.y_spin.setValue(self.pet.y())
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)

    def _on_spin_changed(self, _):
        self.pet.move(self.x_spin.value(), self.y_spin.value())
        self.pet._save_position()
        self.pet._update_ring_cache()

    def _preset(self, key):
        screen = QApplication.screenAt(self.pet.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        avail = screen.availableGeometry()
        w, h = self.pet.width(), self.pet.height()
        L, T = avail.left(), avail.top()
        R, B = avail.right(), avail.bottom()

        if key == "tl":
            x, y = L, T
        elif key == "tc":
            x, y = L + (avail.width() - w) // 2, T
        elif key == "tr":
            x, y = R - w + 1, T
        elif key == "bl":
            x, y = L, B - h + 1
        elif key == "bc":
            x, y = L + (avail.width() - w) // 2, B - h + 1
        elif key == "br":
            x, y = R - w + 1, B - h + 1
        else:
            return
        self.pet.move(x, y)
        self.pet._save_position()
        self.pet._update_ring_cache()
        self.sync_from_pet()


# ==========================================================
#  颜色预览 + 主题自定义
# ==========================================================
class ColorPreviewDialog(QDialog):
    def __init__(self, parent, initial_color, preview_type,
                    font_family, font_size, card_size,
                    kb_text, ms_text, kb_bg, ms_bg):
        super().__init__(parent)
        self.setWindowTitle("自定义颜色")
        self.color = QColor(initial_color)
        self.preview_type = preview_type
        self.font_family = font_family
        self.font_size = font_size
        self.card_size = card_size
        self.kb_text = kb_text
        self.ms_text = ms_text
        self.kb_bg = kb_bg
        self.ms_bg = ms_bg

        self.preview = QLabel()
        self.preview.setFixedSize(280, 90)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet(
            "background-color: #2b2b2b; border-radius: 6px;")

        self.cd = QColorDialog(self.color)
        self.cd.setWindowFlags(Qt.Widget)
        self.cd.setOption(QColorDialog.DontUseNativeDialog, True)
        self.cd.setOption(QColorDialog.NoButtons, True)
        self.cd.currentColorChanged.connect(self._on_color_changed)

        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.preview, alignment=Qt.AlignCenter)
        vbox.addWidget(self.cd)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_ok)
        hbox.addWidget(btn_cancel)
        vbox.addLayout(hbox)

        self.resize(420, 520)
        self._refresh_preview()

    def _on_color_changed(self, c):
        self.color = c
        self._refresh_preview()

    def _refresh_preview(self):
        pm = _paint_card_preview(
            self.preview.size(), self.preview_type, self.color,
            self.font_family, self.font_size, self.card_size,
            self.kb_text, self.ms_text, self.kb_bg, self.ms_bg)
        self.preview.setPixmap(pm)


class ThemeDialog(QDialog):
    def __init__(self, parent, theme_dict,
                    font_family, font_size, card_size):
        super().__init__(parent)
        self.setWindowTitle("自定义主题")
        self.kb_text = QColor(theme_dict["kb_text"])
        self.ms_text = QColor(theme_dict["ms_text"])
        self.kb_bg = QColor(theme_dict["kb_bg"])
        self.ms_bg = QColor(theme_dict["ms_bg"])
        self.font_family = font_family
        self.font_size = font_size
        self.card_size = card_size

        self.kb_preview = QLabel()
        self.kb_preview.setFixedSize(200, 56)
        self.ms_preview = QLabel()
        self.ms_preview.setFixedSize(200, 56)

        grid = QGridLayout()
        grid.addWidget(QLabel("键盘"), 0, 0, 1, 2)
        grid.addWidget(self.kb_preview, 1, 0, 1, 2)
        btn_kb_text = QPushButton("文字颜色…")
        btn_kb_text.clicked.connect(lambda: self._pick("kb_text"))
        btn_kb_bg = QPushButton("背景颜色…")
        btn_kb_bg.clicked.connect(lambda: self._pick("kb_bg"))
        grid.addWidget(btn_kb_text, 2, 0)
        grid.addWidget(btn_kb_bg, 2, 1)

        grid.addWidget(QLabel("鼠标"), 3, 0, 1, 2)
        grid.addWidget(self.ms_preview, 4, 0, 1, 2)
        btn_ms_text = QPushButton("文字颜色…")
        btn_ms_text.clicked.connect(lambda: self._pick("ms_text"))
        btn_ms_bg = QPushButton("背景颜色…")
        btn_ms_bg.clicked.connect(lambda: self._pick("ms_bg"))
        grid.addWidget(btn_ms_text, 5, 0)
        grid.addWidget(btn_ms_bg, 5, 1)

        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_ok)
        hbox.addWidget(btn_cancel)

        vbox = QVBoxLayout(self)
        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        self._refresh()

    def _pick(self, key):
        cur = getattr(self, key)
        c = QColorDialog.getColor(cur, self, "选择颜色")
        if not c.isValid():
            return
        setattr(self, key, c)
        self._refresh()

    def _refresh(self):
        theme = {
            "kb_text": self.kb_text.name(),
            "ms_text": self.ms_text.name(),
            "kb_bg": self.kb_bg.name(),
            "ms_bg": self.ms_bg.name(),
        }
        self.kb_preview.setPixmap(_paint_card_preview(
            self.kb_preview.size(), "kb_text", self.kb_text,
            self.font_family, self.font_size, self.card_size,
            theme["kb_text"], theme["ms_text"],
            theme["kb_bg"], theme["ms_bg"]))
        self.ms_preview.setPixmap(_paint_card_preview(
            self.ms_preview.size(), "ms_text", self.ms_text,
            self.font_family, self.font_size, self.card_size,
            theme["kb_text"], theme["ms_text"],
            theme["kb_bg"], theme["ms_bg"]))

    def result_theme(self):
        return {
            "kb_text": self.kb_text.name(),
            "ms_text": self.ms_text.name(),
            "kb_bg": self.kb_bg.name(),
            "ms_bg": self.ms_bg.name(),
        }


def _paint_card_preview(size, preview_type, focus_color,
                        font_family, font_size, card_size,
                        kb_text, ms_text, kb_bg, ms_bg):
    pm = QPixmap(size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)

    card_h = CARD_H * card_size
    card_pad = CARD_PAD * card_size
    radius = CARD_RADIUS * card_size
    pen_w = CARD_PEN_W * card_size

    f = QFont(font_family)
    f.setPixelSize(max(8, int(round(font_size * 1.33))))
    f.setBold(True)
    fm = QFontMetrics(f)

    is_kb = preview_type.startswith("kb")
    if is_kb:
        edge = C_KB_EDGE
        fill = QColor(kb_bg)
        tcol = QColor(kb_text)
        text = "AB C"
    else:
        edge = C_MS_EDGE
        fill = QColor(ms_bg)
        tcol = QColor(ms_text)
        text = "左键"

    if preview_type == "kb_text":
        tcol = focus_color
    elif preview_type == "kb_bg":
        fill = focus_color
    elif preview_type == "ms_text":
        tcol = focus_color
    elif preview_type == "ms_bg":
        fill = focus_color

    w = fm.horizontalAdvance(text) + card_pad
    x = (pm.width() - w) / 2
    y = (pm.height() - card_h) / 2

    p.setPen(QPen(edge, pen_w))
    p.setBrush(fill)
    p.drawRoundedRect(QRectF(x, y, w, card_h), radius, radius)
    p.setFont(f)
    p.setPen(tcol)
    p.drawText(QRectF(x, y, w, card_h),
                         Qt.AlignHCenter | Qt.AlignVCenter, text)
    p.end()
    return pm


# ==========================================================
#  主窗口
# ==========================================================
class InputPet(QWidget):
    card_signal = pyqtSignal(str, str)
    hover_signal = pyqtSignal(bool)
    show_menu_signal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        QCoreApplication.setOrganizationName("BlueFatFish")
        QCoreApplication.setApplicationName("BlueFatFishPet")
        self.settings = QSettings(
            QSettings.IniFormat, QSettings.UserScope,
            "BlueFatFish", "BlueFatFishPet")

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.kb_enabled = self.settings.value("kb_enabled", True, type=bool)
        self.mouse_enabled = self.settings.value(
            "mouse_enabled", True, type=bool)
        self.kb_dur = float(self.settings.value("kb_dur", 1.5))
        self.scale = float(self.settings.value("scale", 1.0))
        self.auto_start = self.settings.value("auto_start", False, type=bool)
        self.adjust_mode = self.settings.value(
            "adjust_mode", False, type=bool)
        self.font_key = self.settings.value("font_key", "默认")
        self.font_size = int(self.settings.value(
            "font_size", DEFAULT_FONT_SIZE))
        self.fps = int(self.settings.value("fps", DEFAULT_FPS))
        self.card_size = float(self.settings.value("card_size", 1.0))

        self.theme_name = self.settings.value("theme_name", "默认蓝橙")
        self.kb_text_color = self.settings.value(
            "kb_text_color", DEFAULT_THEME["kb_text"])
        self.ms_text_color = self.settings.value(
            "ms_text_color", DEFAULT_THEME["ms_text"])
        self.kb_bg_color = self.settings.value(
            "kb_bg_color", DEFAULT_THEME["kb_bg"])
        self.ms_bg_color = self.settings.value(
            "ms_bg_color", DEFAULT_THEME["ms_bg"])

        self._custom_family = None
        custom_path = self.settings.value("custom_font_path", "")
        if custom_path and os.path.exists(custom_path):
            fam = self._load_custom_font(custom_path)
            if fam:
                self._custom_family = fam

        self.cards = []
        self.last_activity = 0.0
        self.show_ring = True
        self._ring_hover = False
        self._dragging = False
        self._drag_pos = None
        self._last_tick = time.time()
        self._rendering_paused = False
        self._paused_since = 0.0
        self._kb_listener = None
        self._kb_mods = set()
        self._kb_pending_mods = set()
        self._kb_pressed_times = {}
        self._mouse_listener = None
        self._pos_dialog = None
        self._ring_menu = None
        self._menu_showing = False
        self._right_press_in_ring = False

        self._ring_center_global = (0, 0)
        self._ring_radius_global = (RING_R + RING_HIT_PAD)

        self.setFixedSize(int(BASE_W * self.scale),
                                 int(BASE_H * self.scale))
        avail = QApplication.primaryScreen().availableGeometry()
        saved_x = int(self.settings.value("pos_x", -1))
        saved_y = int(self.settings.value("pos_y", -1))
        if saved_x >= 0 and saved_y >= 0:
            self.move(saved_x, saved_y)
            self._clamp_to_screen()
        else:
            self.move(avail.center().x() - self.width() // 2,
                                                         avail.bottom() - self.height() - 40)

        self.build_tray()

        self.card_signal.connect(self._add_card)
        self.hover_signal.connect(self._on_hover_change)
        self.show_menu_signal.connect(self._show_ring_menu)

        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(max(8, int(1000 / self.fps)))
        self.anim_timer.timeout.connect(self._on_anim_tick)

        self._topmost_timer = QTimer(self)
        self._topmost_timer.setInterval(TOPMOST_INTERVAL)
        self._topmost_timer.timeout.connect(self._enforce_topmost)
        self._topmost_timer.start()

        self._pos_sync_timer = QTimer(self)
        self._pos_sync_timer.setInterval(300)
        self._pos_sync_timer.timeout.connect(self._sync_pos_dialog)
        self._pos_sync_timer.start()

        self._update_ring_cache()
        self._apply_mouse_mode()

        self._start_kb_listener()
        self._start_mouse_listener()
        self._apply_auto_start()

    # =================================================== 圆环缓存 / 掩码
    def _update_ring_cache(self):
        wx, wy = self.x(), self.y()
        self._ring_center_global = (
            wx + self.width() // 2,
            wy + self.height() // 2)
        self._ring_radius_global = (RING_R + RING_HIT_PAD) * self.scale

    def _set_click_through(self, on):
        """非拖动模式下让 Qt 忽略窗口自身的鼠标事件。

        注意：这个属性在 Windows 上并不会设置 WS_EX_TRANSPARENT（实测
        exstyle 完全不变），所以它既不负责"穿透"也不负责"挡住桌面" ——
        真正的分区穿透由 _refresh_mask() 的窗口掩码完成。这里只保证
        非拖动模式下 Qt 不去处理落在圆环上的鼠标事件（右键菜单走全局钩子）。
        """
        self.setAttribute(Qt.WA_TransparentForMouseEvents, bool(on))

    def _apply_mouse_mode(self):
        # 穿透完全交给窗口掩码（见 _refresh_mask），不使用 WS_EX_TRANSPARENT：
        # 该样式位会让系统在命中测试时跳过整个窗口，圆环随之收不到右键，
        # 点击穿到桌面会弹出系统右键菜单并抢走焦点，导致程序菜单无法关闭。
        self._set_click_through(not self.adjust_mode)
        self._refresh_mask()
        self.update()

    def _ring_region(self):
        s = self.scale
        cx = int(BASE_W * s / 2)
        cy = int(BASE_H * s / 2)
        r = int((RING_R + RING_HIT_PAD) * s)
        return QRegion(cx - r, cy - r, 2 * r, 2 * r, QRegion.Ellipse)

    def _refresh_mask(self):
        """按模式设置窗口掩码。

        掩码是 Windows 上唯一能"分区域穿透"的机制：掩码以外的点击系统不会
        派发给本窗口，从而落到下层窗口；掩码以内的点击会被本窗口接收。
        （WS_EX_TRANSPARENT 与 WM_NCHITTEST→HTTRANSPARENT 实测都做不到分区域：
        前者让整个窗口被系统跳过、圆环也随之失效，后者对本窗口完全不起作用。）

        代价：setMask 会裁剪绘制，所以掩码必须覆盖所有需要显示的内容 ——
        非拖动模式下有卡片时要把卡片一起并进来，否则卡片会被裁掉。
        """
        s = self.scale
        region = self._ring_region()
        if not self.adjust_mode and not self.cards:
            # 静止状态：只有圆环需要接收鼠标，其余区域全部穿透
            self.setMask(region)
            return
        card_h = int(CARD_H * self.card_size * s)
        for c in self.cards:
            cw = c.get("w", 0)
            if cw <= 0:
                continue
            # 同时覆盖"动画进行中的位置"和"目标位置"，否则卡片滑入途中会被裁掉
            xs = [c.get("x"), c.get("target_x")]
            ys = [c.get("y"), c.get("target_y")]
            for cx_ in [v for v in xs if v is not None]:
                for cy_ in [v for v in ys if v is not None]:
                    x = int(cx_ * s) - 4
                    y = int(cy_ * s) - 4
                    w = int(cw * s) + 8
                    h = card_h + 8
                    region = region.united(QRegion(x, y, w, h))
        # 掩码不能超出窗口，否则 Qt 会按窗口裁剪，越界部分没有意义
        self.setMask(region.intersected(QRegion(self.rect())))

    def set_adjust_mode(self, on):
        self.adjust_mode = bool(on)
        self.settings.setValue("adjust_mode", self.adjust_mode)
        self._apply_mouse_mode()

    def _on_hover_change(self, hovering):
        if self._ring_hover != hovering:
            self._ring_hover = hovering
            self.update()

    def moveEvent(self, e):
        super().moveEvent(e)
        self._update_ring_cache()

    # =================================================== 位置保存 / 位置对话框
    def _save_position(self):
        self.settings.setValue("pos_x", self.x())
        self.settings.setValue("pos_y", self.y())

    def _sync_pos_dialog(self):
        if self._pos_dialog is not None and self._pos_dialog.isVisible():
            self._pos_dialog.sync_from_pet()

    def open_position_dialog(self):
        if self._pos_dialog is None:
            self._pos_dialog = PositionDialog(self)
        self._pos_dialog.sync_from_pet()
        self._pos_dialog.show()
        self._pos_dialog.raise_()
        self._pos_dialog.activateWindow()

    # =================================================== 圆环菜单
    def _show_ring_menu(self, gx, gy):
        # 防重入：exec_() 会阻塞嵌套事件循环
        if getattr(self, "_menu_showing", False):
            return
        self._menu_showing = True
        try:
            menu = QMenu()
            menu.setWindowFlags(
                menu.windowFlags() | Qt.WindowStaysOnTopHint)

            # 一级：拖动模式
            act_adjust = QAction("拖动模式", menu, checkable=True)
            act_adjust.setChecked(self.adjust_mode)
            act_adjust.toggled.connect(self.set_adjust_mode)
            menu.addAction(act_adjust)

            # 一级：设置（二级菜单 = 原操作面板）
            settings_menu = menu.addMenu("设置")
            self._populate_settings_menu(settings_menu)

            menu.addSeparator()

            # 一级：退出
            act_quit = QAction("退出", menu)
            act_quit.triggered.connect(QApplication.quit)
            menu.addAction(act_quit)

            # 用 exec_()：阻塞等待用户选择，右键的 release 已经过去，
            # 不会再被菜单当作"立即确认"。
            menu.exec_(QPoint(int(gx), int(gy)))
        finally:
            self._menu_showing = False

    def _populate_settings_menu(self, parent):
            # 键盘按键显示
        act_kb = QAction("键盘按键显示", parent, checkable=True)
        act_kb.setChecked(self.kb_enabled)
        act_kb.toggled.connect(self._on_toggle_kb)
        parent.addAction(act_kb)

        # 鼠标点击显示
        act_ms = QAction("鼠标点击显示", parent, checkable=True)
        act_ms.setChecked(self.mouse_enabled)
        act_ms.toggled.connect(self._on_toggle_mouse)
        parent.addAction(act_ms)

        # 显示时长
        dur_menu = parent.addMenu("显示时长")
        dur_group = QActionGroup(parent)
        for label, sec in DUR_OPTIONS:
            act = QAction(label, parent, checkable=True)
            act.setChecked(abs(sec - self.kb_dur) < 0.01)
            act.triggered.connect(
                lambda _=False, s=sec: self.set_kb_dur(s))
            dur_menu.addAction(act)
            dur_group.addAction(act)

        # 面板大小
        scale_menu = parent.addMenu("面板大小")
        scale_group = QActionGroup(parent)
        for label, val in SCALE_OPTIONS:
            act = QAction(label, parent, checkable=True)
            act.setChecked(abs(val - self.scale) < 0.01)
            act.triggered.connect(
                lambda _=False, v=val: self.set_scale(v))
            scale_menu.addAction(act)
            scale_group.addAction(act)

        # 卡片尺寸
        csize_menu = parent.addMenu("卡片尺寸")
        csize_group = QActionGroup(parent)
        for label, val in CARDSIZE_OPTIONS:
            act = QAction(label, parent, checkable=True)
            act.setChecked(abs(val - self.card_size) < 0.01)
            act.triggered.connect(
                lambda _=False, v=val: self.set_card_size(v))
            csize_menu.addAction(act)
            csize_group.addAction(act)

        # 刷新率
        fps_menu = parent.addMenu("刷新率")
        fps_group = QActionGroup(parent)
        for label, val in FPS_OPTIONS:
            act = QAction(label, parent, checkable=True)
            act.setChecked(val == self.fps)
            act.triggered.connect(
                lambda _=False, v=val: self.set_fps(v))
            fps_menu.addAction(act)
            fps_group.addAction(act)

        # 主题色
        theme_menu = parent.addMenu("主题色")
        theme_group = QActionGroup(parent)
        for name in THEMES.keys():
            act = QAction(name, parent, checkable=True)
            act.setChecked(name == self.theme_name)
            act.triggered.connect(
                lambda _=False, n=name: self.apply_theme(n))
            theme_menu.addAction(act)
            theme_group.addAction(act)
        theme_menu.addSeparator()
        act_custom = QAction("自定义颜色…", parent)
        act_custom.triggered.connect(self._on_custom_theme)
        theme_menu.addAction(act_custom)

        # 字体
        font_menu = parent.addMenu("字体")
        font_group = QActionGroup(parent)
        act_default = QAction("默认", parent, checkable=True)
        act_default.setChecked(self.font_key == "默认")
        act_default.triggered.connect(lambda: self.set_font("默认"))
        font_menu.addAction(act_default)
        font_group.addAction(act_default)
        if self._custom_family:
            act_c = QAction(self._custom_family, parent, checkable=True)
            act_c.setChecked(self.font_key == self._custom_family)
            act_c.triggered.connect(
                lambda: self.set_font(self._custom_family))
            font_menu.addAction(act_c)
            font_group.addAction(act_c)
        font_menu.addSeparator()
        act_browse = QAction("浏览字体文件…", parent)
        act_browse.triggered.connect(self._on_browse_font)
        font_menu.addAction(act_browse)

        # 字号
        fsize_menu = parent.addMenu("字号")
        fsize_group = QActionGroup(parent)
        for label, sz in FSIZE_OPTIONS:
            act = QAction(label, parent, checkable=True)
            act.setChecked(sz == self.font_size)
            act.triggered.connect(
                lambda _=False, s=sz: self.set_font_size(s))
            fsize_menu.addAction(act)
            fsize_group.addAction(act)

        parent.addSeparator()

        # 调整位置
        act_pos = QAction("调整位置…", parent)
        act_pos.triggered.connect(self.open_position_dialog)
        parent.addAction(act_pos)

        # 开机自启动
        act_auto = QAction("开机自启动", parent, checkable=True)
        act_auto.setChecked(self.auto_start)
        act_auto.toggled.connect(self._on_toggle_autostart)
        parent.addAction(act_auto)

        # =================================================== 菜单回调
    def _on_toggle_kb(self, checked):
        self.kb_enabled = checked
        self.settings.setValue("kb_enabled", checked)
        if not checked:
            self.cards = [c for c in self.cards if c["kind"] != "kb"]
            self._relayout()
        self.update()

    def _on_toggle_mouse(self, checked):
        self.mouse_enabled = checked
        self.settings.setValue("mouse_enabled", checked)
        if not checked:
            self.cards = [c for c in self.cards if c["kind"] != "mouse"]
            self._relayout()
        self.update()

    def _on_toggle_autostart(self, checked):
        self.auto_start = checked
        self.settings.setValue("auto_start", checked)
        self._apply_auto_start()

    def _on_custom_theme(self):
        cur = {
            "kb_text": self.kb_text_color,
            "ms_text": self.ms_text_color,
            "kb_bg": self.kb_bg_color,
            "ms_bg": self.ms_bg_color,
        }
        dlg = ThemeDialog(self, cur,
                             self._resolve_font_family(),
                                                    self.font_size, self.card_size)
        if dlg.exec_() != QDialog.Accepted:
            return
        theme = dlg.result_theme()
        self.theme_name = "自定义"
        self.kb_text_color = theme["kb_text"]
        self.ms_text_color = theme["ms_text"]
        self.kb_bg_color = theme["kb_bg"]
        self.ms_bg_color = theme["ms_bg"]
        self.settings.setValue("theme_name", "自定义")
        self.settings.setValue("kb_text_color", self.kb_text_color)
        self.settings.setValue("ms_text_color", self.ms_text_color)
        self.settings.setValue("kb_bg_color", self.kb_bg_color)
        self.settings.setValue("ms_bg_color", self.ms_bg_color)
        self.update()

    def _on_browse_font(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择字体文件", "",
            "字体文件 (*.ttf *.otf *.ttc);;所有文件 (*)")
        if not path:
            return
        family = self._load_custom_font(path)
        if not family:
            QMessageBox.warning(self, "加载失败",
                                "无法加载该字体文件，请确认格式正确。")
            return
        self._custom_family = family
        self.settings.setValue("custom_font_path", path)
        self.set_font(family)

    # =================================================== 强制置顶
    def _enforce_topmost(self):
        if not self.isVisible():
            return
        try:
            if sys.platform == "win32":
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_TOPMOST = 0x00000008
                ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                if not (ex & WS_EX_TOPMOST):
                    HWND_TOPMOST = -1
                    SWP_NOSIZE = 0x0001
                    SWP_NOMOVE = 0x0002
                    SWP_NOACTIVATE = 0x0010
                    user32.SetWindowPos(
                        hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)
            else:
                self.raise_()
        except Exception:
            pass

    # =================================================== 字体
    def _load_custom_font(self, path):
        try:
            fid = QFontDatabase.addApplicationFont(path)
            if fid < 0:
                return None
            fams = QFontDatabase.applicationFontFamilies(fid)
            return fams[0] if fams else None
        except Exception:
            return None

    def _resolve_font_family(self):
        if self.font_key == "默认":
            return "Microsoft YaHei"
        if self._custom_family and self.font_key == self._custom_family:
            return self._custom_family
        return "Microsoft YaHei"

    def _make_font(self):
        f = QFont(self._resolve_font_family())
        f.setPixelSize(max(8, int(round(self.font_size * 1.33))))
        f.setBold(True)
        return f

    # =================================================== 边界限制
    def _clamp_to_screen(self, ref_pos=None):
        if ref_pos is not None:
            screen = QApplication.screenAt(ref_pos)
        else:
            screen = QApplication.screenAt(self.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        avail = screen.availableGeometry()

        w, h = self.width(), self.height()
        L, T = avail.left(), avail.top()
        R, B = avail.right(), avail.bottom()

        min_x = L - w + MIN_VISIBLE
        max_x = R - MIN_VISIBLE + 1
        min_y = T - h + MIN_VISIBLE
        max_y = B - MIN_VISIBLE + 1

        nx = max(min_x, min(self.x(), max_x))
        ny = max(min_y, min(self.y(), max_y))
        if nx != self.x() or ny != self.y():
            self.move(nx, ny)

    # =================================================== 系统托盘
    def _app_icon(self):
        """仓库自带图标文件；按 ips.png -> ips.ico -> icon.png 顺序查找。"""
        for name in ("ips.png", "ips.ico", "icon.png"):
            path = os.path.join(BASE_DIR, name)
            if os.path.exists(path):
                ico = QIcon(path)
                if not ico.isNull():
                    return ico
        return None

    def _make_tray_icon(self):
        ico = self._app_icon()
        if ico is not None:
            return ico
        pm = QPixmap(64, 64)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(0x3A, 0x5A, 0xB0), 5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(9, 9, 46, 46)
        p.end()
        return QIcon(pm)

    def build_tray(self):
        self.tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon = self._make_tray_icon()
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("键盘 + 鼠标 输入显示")

        # 托盘的菜单和圆环菜单结构一致，方便一致体验
        tmenu = QMenu(self)

        act_adjust = QAction("拖动模式", self, checkable=True)
        act_adjust.setChecked(self.adjust_mode)

        def _sync_check(checked):
            self.set_adjust_mode(checked)
            act_adjust.setChecked(self.adjust_mode)

        act_adjust.toggled.connect(_sync_check)
        tmenu.addAction(act_adjust)

        settings_menu = tmenu.addMenu("设置")
        self._populate_settings_menu(settings_menu)

        tmenu.addSeparator()

        act_show = QAction("显示 / 隐藏", self)
        act_show.triggered.connect(self.toggle_visible)
        tmenu.addAction(act_show)

        tmenu.addSeparator()

        act_quit = QAction("退出", self)
        act_quit.triggered.connect(QApplication.quit)
        tmenu.addAction(act_quit)

        self.tray.setContextMenu(tmenu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.toggle_visible()

    # =================================================== 主题
    def apply_theme(self, name):
        if name not in THEMES:
            return
        theme = THEMES[name]
        self.theme_name = name
        self.kb_text_color = theme["kb_text"]
        self.ms_text_color = theme["ms_text"]
        self.kb_bg_color = theme["kb_bg"]
        self.ms_bg_color = theme["ms_bg"]
        self.settings.setValue("theme_name", name)
        self.settings.setValue("kb_text_color", self.kb_text_color)
        self.settings.setValue("ms_text_color", self.ms_text_color)
        self.settings.setValue("kb_bg_color", self.kb_bg_color)
        self.settings.setValue("ms_bg_color", self.ms_bg_color)
        self.update()

    # =================================================== 设置动作
    def set_kb_dur(self, s):
        self.kb_dur = s
        self.settings.setValue("kb_dur", s)

    def set_scale(self, v):
        old_center = self.geometry().center()
        self.scale = v
        self.settings.setValue("scale", v)
        new_w = int(BASE_W * v)
        new_h = int(BASE_H * v)
        self.setFixedSize(new_w, new_h)
        self.move(old_center.x() - new_w // 2,
                                  old_center.y() - new_h // 2)
        self._clamp_to_screen()
        self._save_position()
        self._update_ring_cache()
        self._relayout()
        self._apply_mouse_mode()
        self.update()

    def set_card_size(self, v):
        self.card_size = float(v)
        self.settings.setValue("card_size", v)
        self._relayout()
        self.update()

    def set_font(self, key):
        self.font_key = key
        self.settings.setValue("font_key", key)
        self._relayout()
        self.update()

    def set_font_size(self, sz):
        self.font_size = int(sz)
        self.settings.setValue("font_size", int(sz))
        self._relayout()
        self.update()

    def set_fps(self, v):
        self.fps = int(v)
        self.settings.setValue("fps", int(v))
        self.anim_timer.setInterval(max(8, int(1000 / self.fps)))

    def _apply_auto_start(self):
        if sys.platform != "win32":
            return
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            if self.auto_start:
                if getattr(sys, "frozen", False):
                    exe = sys.executable
                else:
                    exe = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "BlueFatFishPet", 0,
                                  winreg.REG_SZ, f'"{exe}"')
            else:
                try:
                    winreg.DeleteValue(key, "BlueFatFishPet")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def toggle_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self._update_ring_cache()
            self._enforce_topmost()

    # =================================================== 事件
    def mousePressEvent(self, e):
        # 调整模式下才可能收到鼠标事件（掩码已限制可点区域）
        if not self.adjust_mode:
            return
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_pos = (
                e.globalPos() - self.frameGeometry().topLeft())
            self.update()
            e.accept()

    def mouseMoveEvent(self, e):
        if (self.adjust_mode and self._dragging
                and self._drag_pos is not None):
            self.move(e.globalPos() - self._drag_pos)
            self._clamp_to_screen(e.globalPos())

    def mouseReleaseEvent(self, e):
        if self._dragging:
            self._dragging = False
            self._drag_pos = None
            self._clamp_to_screen()
            self._save_position()
            self.update()

    # =================================================== 卡片
    def _add_card(self, text, kind):
        if self._rendering_paused:
            if time.time() - self._paused_since > RENDER_PAUSE_TIMEOUT:
                self._rendering_paused = False
            else:
                return

        now = time.time()

        same_kind = [c for c in self.cards if c["kind"] == kind]
        if len(same_kind) >= MAX_VISIBLE:
            self.cards.remove(same_kind[0])

        card = {
            "text": text, "kind": kind, "start": now,
            "x": None, "y": None, "w": 0,
            "target_x": 0, "target_y": 0,
        }
        self.cards.append(card)
        self._relayout()

        for c in self.cards:
            if c["x"] is None:
                if c["kind"] == "kb":
                    c["x"] = BASE_W + SLIDE_IN_DIST
                    c["y"] = c["target_y"]
                else:
                    c["x"] = c["target_x"]
                    c["y"] = BASE_H + SLIDE_IN_DIST

        self.last_activity = now
        self.show_ring = False
        self.update()

        if not self.anim_timer.isActive():
            self._last_tick = now
            self.anim_timer.start()

        # 有卡片时必须重设掩码：setMask 会裁剪绘制，掩码里没有卡片的位置
        # 卡片就画不出来（静止时掩码只含圆环）。
        self._refresh_mask()

    def _relayout(self):
        if not self.cards:
            return
        f = self._make_font()
        fm = QFontMetrics(f)
        card_h = CARD_H * self.card_size
        card_pad = CARD_PAD * self.card_size

        kb_cards = [c for c in self.cards if c["kind"] == "kb"]
        ms_cards = [c for c in self.cards if c["kind"] == "mouse"]

        self._layout_row(kb_cards, fm, ROW_KB_Y, card_h, card_pad)
        self._layout_row(ms_cards, fm, ROW_MS_Y, card_h, card_pad)

    def _layout_row(self, cards, fm, row_center_y, card_h, card_pad):
        if not cards:
            return
        widths = [fm.horizontalAdvance(c["text"]) + card_pad
                       for c in cards]
        total = sum(widths) + CARD_GAP * (len(widths) - 1)
        x = (BASE_W - total) / 2
        for c, w in zip(cards, widths):
            c["w"] = w
            c["target_x"] = x
            c["target_y"] = row_center_y - card_h / 2
            x += w + CARD_GAP

    def _on_anim_tick(self):
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now

        before = len(self.cards)
        self.cards = [c for c in self.cards
                      if now - c["start"] < self.kb_dur]
        if len(self.cards) != before:
            self._relayout()
            for c in self.cards:
                if c["x"] is None:
                    c["x"] = c["target_x"]
                if c["y"] is None:
                    c["y"] = c["target_y"]
            if not self.cards:
                # 卡片全部消失：掩码缩回圆环，其余区域恢复穿透
                self._refresh_mask()

        k = 1 - math.exp(-dt / 0.055)
        for c in self.cards:
            if c["x"] is not None and c["target_x"] is not None:
                c["x"] += (c["target_x"] - c["x"]) * k
            if c["y"] is not None and c["target_y"] is not None:
                c["y"] += (c["target_y"] - c["y"]) * k

        if not self.cards:
            if now - self.last_activity >= IDLE_RING_DELAY:
                self.show_ring = True
                self.anim_timer.stop()

        self.update()

        if self.adjust_mode:
            self._refresh_mask()

    # =================================================== 绘制
    def paintEvent(self, _):
        if self._rendering_paused:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.scale, self.scale)

        p.fillRect(QRectF(0, 0, BASE_W, BASE_H), QColor(0, 0, 0, 1))

        cx, cy = BASE_W / 2, BASE_H / 2

        if self.cards:
            self._draw_cards(p, time.time())
        elif self.show_ring or self.adjust_mode or self._ring_hover:
            self._draw_ring(p, cx, cy,
                            highlight=self._dragging or self._ring_hover)

        if self.adjust_mode:
            p.setPen(QPen(C_ADJUST_BORDER, 2, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(cx, cy),
                                     RING_R + 6, RING_R + 6)

        p.end()

    def _draw_ring(self, p, cx, cy, highlight=False):
        if highlight:
            col = QColor(C_RING_HOVER)
            col.setAlpha(255)
            p.setPen(QPen(col, 3.0))
        else:
            col = QColor(C_RING)
            col.setAlpha(190)
            p.setPen(QPen(col, 2.2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), RING_R, RING_R)

    def _draw_cards(self, p, now):
        f = self._make_font()
        kb_col = QColor(self.kb_text_color)
        ms_col = QColor(self.ms_text_color)
        kb_bg = QColor(self.kb_bg_color)
        ms_bg = QColor(self.ms_bg_color)

        card_h = CARD_H * self.card_size
        radius = CARD_RADIUS * self.card_size
        pen_w = CARD_PEN_W * self.card_size

        for c in self.cards:
            age = now - c["start"]

            slide_x = 0.0
            slide_y = 0.0
            if age < FADE_IN:
                t = age / FADE_IN
                a = t
                scale_anim = 0.88 + 0.12 * t
            elif age > self.kb_dur - FADE_OUT:
                t = (age - (self.kb_dur - FADE_OUT)) / FADE_OUT
                t = max(0.0, min(1.0, t))
                a = 1.0 - t
                scale_anim = 1.0 - 0.25 * t
                if c["kind"] == "kb":
                    slide_x = -SLIDE_OUT_DIST * t
                else:
                    slide_y = -SLIDE_OUT_DIST * t
            else:
                a = 1.0
                scale_anim = 1.0

            if c["kind"] == "mouse":
                edge, fill, tcol = C_MS_EDGE, ms_bg, ms_col
            else:
                edge, fill, tcol = C_KB_EDGE, kb_bg, kb_col

            w = c["w"]
            x = c["x"] + slide_x
            y = c["y"] + slide_y

            p.save()
            p.setOpacity(a)
            p.translate(x + w / 2, y + card_h / 2)
            p.scale(scale_anim, scale_anim)
            p.translate(-(x + w / 2), -(y + card_h / 2))
            p.setPen(QPen(edge, pen_w))
            p.setBrush(fill)
            p.drawRoundedRect(QRectF(x, y, w, card_h), radius, radius)
            p.setFont(f)
            p.setPen(tcol)
            p.drawText(QRectF(x, y, w, card_h),
                       Qt.AlignHCenter | Qt.AlignVCenter, c["text"])
            p.restore()

    # =================================================== 键盘监听
    def _start_kb_listener(self):
        try:
            from pynput import keyboard
        except Exception:
            return

        MOD = {
            keyboard.Key.ctrl_l: "Ctrl", keyboard.Key.ctrl_r: "Ctrl",
            keyboard.Key.shift: "Shift", keyboard.Key.shift_r: "Shift",
            keyboard.Key.alt: "Alt", keyboard.Key.alt_r: "Alt",
            keyboard.Key.alt_gr: "Alt",
            keyboard.Key.cmd: "Win", keyboard.Key.cmd_r: "Win",
        }
        NAMED = {
            keyboard.Key.enter: "Enter", keyboard.Key.tab: "Tab",
            keyboard.Key.space: "Space",
            keyboard.Key.backspace: "Backspace",
            keyboard.Key.delete: "Del", keyboard.Key.home: "Home",
            keyboard.Key.end: "End",
            keyboard.Key.page_up: "PgUp",
            keyboard.Key.page_down: "PgDn",
            keyboard.Key.insert: "Ins", keyboard.Key.esc: "Esc",
            keyboard.Key.up: "↑", keyboard.Key.down: "↓",
            keyboard.Key.left: "←", keyboard.Key.right: "→",
            keyboard.Key.caps_lock: "Caps",
        }
        for i in range(1, 13):
            k = getattr(keyboard.Key, f"f{i}", None)
            if k is not None:
                NAMED[k] = f"F{i}"

        def _label_from_keycode(kc):
            v = getattr(kc, "char", None)
            if isinstance(v, str) and len(v) >= 1:
                ch = v[0]
                if ch.isprintable() and 32 <= ord(ch) < 128:
                    return "Space" if ch == " " else ch.upper()
            vk = getattr(kc, "vk", None)
            if isinstance(vk, int):
                if 48 <= vk <= 57:
                    return chr(vk)
                if 65 <= vk <= 90:
                    return chr(vk)
            return None

        def _format_duration(text, dur):
            if abs(dur - round(dur)) < 0.1:
                return f"{text}*{int(round(dur))}s"
            return f"{text}*{dur:.1f}s"

        def _is_stuck(label):
            prev = self._kb_pressed_times.get(label)
            if prev is None:
                return False
            if isinstance(prev, float):
                return time.time() - prev > KEY_STUCK_TIMEOUT
            return False

        def on_press(key):
            try:
                if not self.kb_enabled:
                    return
                if isinstance(key, keyboard.Key) and key in MOD:
                    label = MOD[key]
                    self._kb_mods.add(label)
                    self._kb_pending_mods.add(label)
                    if (label in self._kb_pressed_times
                            and not _is_stuck(label)):
                        return
                    self._kb_pressed_times[label] = time.time()
                    return

                if isinstance(key, keyboard.Key):
                    lab = NAMED.get(key)
                else:
                    lab = _label_from_keycode(key)
                if not lab:
                    return

                if (lab in self._kb_pressed_times
                        and not _is_stuck(lab)):
                    return

                has_mods = bool(self._kb_mods)
                self._kb_pending_mods.clear()

                if has_mods:
                    self._kb_pressed_times[lab] = None
                    parts = [m for m in ("Ctrl", "Alt", "Shift", "Win")
                                              if m in self._kb_mods]
                    text = "+".join(parts + [lab])
                else:
                    self._kb_pressed_times[lab] = time.time()
                    text = lab

                self.card_signal.emit(text, "kb")
            except Exception:
                pass

        def on_release(key):
            try:
                if isinstance(key, keyboard.Key) and key in MOD:
                    label = MOD[key]
                    self._kb_mods.discard(label)
                    was_pending = label in self._kb_pending_mods
                    self._kb_pending_mods.discard(label)
                    start = self._kb_pressed_times.pop(label, None)
                    if was_pending and isinstance(start, float):
                        dur = time.time() - start
                        if dur >= LONG_PRESS_THRESHOLD:
                            self.card_signal.emit(
                                _format_duration(label, dur), "kb")
                        else:
                            self.card_signal.emit(label, "kb")
                    return

                if isinstance(key, keyboard.Key):
                    lab = NAMED.get(key)
                else:
                    lab = _label_from_keycode(key)
                if not lab:
                    return

                start = self._kb_pressed_times.pop(lab, None)
                if isinstance(start, float):
                    dur = time.time() - start
                    if dur >= LONG_PRESS_THRESHOLD:
                        self.card_signal.emit(
                            _format_duration(lab, dur), "kb")
            except Exception:
                pass

        try:
            self._kb_listener = keyboard.Listener(
                on_press=on_press, on_release=on_release, daemon=True)
            self._kb_listener.start()
        except Exception:
            self._kb_listener = None

    # =================================================== 鼠标监听
    def _start_mouse_listener(self):
        try:
            from pynput import mouse
        except Exception:
            return

        BUTTON_NAME = {
            mouse.Button.left: "左键",
            mouse.Button.right: "右键",
            mouse.Button.middle: "中键",
        }

        def _in_ring(gx, gy):
            cx, cy = self._ring_center_global
            r = self._ring_radius_global
            dx = gx - cx
            dy = gy - cy
            return dx * dx + dy * dy <= r * r

        def on_click(x, y, button, pressed):
            try:
                # 右键：按下时在圆环内记一笔，抬起时弹菜单；
                # 同时和左键/中键一样显示卡片，不再直接 return 掉。
                if (button == mouse.Button.right
                        and self.isVisible()):
                    if pressed:
                        self._right_press_in_ring = _in_ring(x, y)
                    else:
                        was_in = getattr(
                            self, "_right_press_in_ring", False)
                        self._right_press_in_ring = False
                        if was_in:
                            self.show_menu_signal.emit(
                                int(x), int(y))

                if not pressed:
                    return
                if not self.mouse_enabled:
                    return
                name = BUTTON_NAME.get(button)
                if name is None:
                    return
                self.card_signal.emit(name, "mouse")
            except Exception:
                pass

        def on_scroll(x, y, dx, dy):
            try:
                if not self.mouse_enabled:
                    return
                if dy > 0:
                    self.card_signal.emit("滚轮↑", "mouse")
                elif dy < 0:
                    self.card_signal.emit("滚轮↓", "mouse")
            except Exception:
                pass

        def on_move(x, y):
            try:
                if not self.isVisible():
                    if self._ring_hover:
                        self.hover_signal.emit(False)
                    return
                h = _in_ring(x, y)
                if h != self._ring_hover:
                    self.hover_signal.emit(h)
            except Exception:
                pass

        try:
            self._mouse_listener = mouse.Listener(
                on_click=on_click, on_scroll=on_scroll,
                on_move=on_move, daemon=True)
            self._mouse_listener.start()
        except Exception:
            self._mouse_listener = None


# ==========================================================
#  单实例
# ==========================================================
def _notify_existing_instance():
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(300):
        socket.write(b"show\n")
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
        return True
    return False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("输入显示")
    app.setQuitOnLastWindowClosed(False)
    f = QFont()
    f.setFamilies(["Noto Sans CJK SC", "WenQuanYi Micro Hei",
                   "Microsoft YaHei", "PingFang SC", "sans-serif"])
    app.setFont(f)

    if _notify_existing_instance():
        sys.exit(0)

    QLocalServer.removeServer(SERVER_NAME)
    server = QLocalServer()
    server.listen(SERVER_NAME)

    pet = InputPet()
    pet.show()
    pet._update_ring_cache()
    pet._enforce_topmost()

    def on_new_connection():
        while server.hasPendingConnections():
            conn = server.nextPendingConnection()
            conn.readyRead.connect(lambda c=conn: _handle_client(c))
            conn.disconnected.connect(conn.deleteLater)

    def _handle_client(conn):
        try:
            data = bytes(conn.readAll()).strip()
            if data.startswith(b"show"):
                pet.show()
                pet._update_ring_cache()
                pet._enforce_topmost()
        except Exception:
            pass

    server.newConnection.connect(on_new_connection)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()