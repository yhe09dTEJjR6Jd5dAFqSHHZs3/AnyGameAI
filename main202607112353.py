from __future__ import annotations

import csv
import ctypes
import hashlib
import json
import math
import os
import queue
import random
import shutil
import sys
import threading
import time
import traceback
import tracemalloc
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Sequence

if sys.platform != "win32":
    raise SystemExit("此程序仅支持 Windows 11/Windows 10。")

from ctypes import wintypes

try:
    import cv2
    import joblib
    import mss
    import numpy as np
    from pynput import keyboard, mouse
    from sklearn import __version__ as sklearn_version
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
    from sklearn.metrics import balanced_accuracy_score
    from threadpoolctl import threadpool_limits
except ImportError as exc:
    missing = getattr(exc, "name", str(exc))
    raise SystemExit(
        f"缺少依赖：{missing}\n\n"
        "请在命令提示符中运行：\n"
        "python -m pip install numpy opencv-python-headless mss pynput "
        "scikit-learn joblib threadpoolctl"
    ) from exc

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk


APP_NAME = "通用鼠标游戏 AI（安全模仿学习版）"
APP_VERSION = "2.0.0"
MODEL_VERSION = 2
DATASET_VERSION = 2
FEATURE_WIDTH = 32
FEATURE_HEIGHT = 18
GRID_COLS = 8
GRID_ROWS = 6
VISUAL_FEATURE_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 6 + GRID_COLS * GRID_ROWS * 6
STATE_FEATURE_DIM = 7
FEATURE_DIM = VISUAL_FEATURE_DIM + STATE_FEATURE_DIM
MAX_TRAIN_SAMPLES = 30000
MIN_SESSIONS = 3
MIN_VALIDATION_SECONDS = 60.0
MIN_MOVE_SAMPLES = 500
MIN_BUTTON_TRANSITIONS = 50
MIN_FREE_DISK_BYTES = 1 * 1024**3
CHUNK_SIZE = 256
FOCUS_WARMUP_FRAMES = 3
INPUT_MARKER = 0x47414932
MAX_INPUT_EVENTS_PER_SECOND = 120
MODEL_FILENAME = "game_ai_model.joblib"
MODEL_HASH_FILENAME = "game_ai_model.sha256"
GA_ROOT = 2
SW_RESTORE = 9
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_VIRTUALDESK = 0x4000
MOUSEEVENTF_ABSOLUTE = 0x8000
INPUT_MOUSE = 0
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
LLMHF_INJECTED = 0x00000001

BUTTONS = ("left", "right", "middle")
BUTTON_CN = {"left": "左键", "right": "右键", "middle": "中键"}

PALETTE = {
    "red": "#E53935",
    "orange": "#FB8C00",
    "yellow": "#FDD835",
    "green": "#43A047",
    "cyan": "#00ACC1",
    "blue": "#1E88E5",
    "purple": "#8E24AA",
    "black": "#151515",
    "white": "#FAFAFA",
    "gray": "#757575",
    "light_gray": "#E0E0E0",
}


# ---------------------------------------------------------------------------
# Win32 declarations. Every ctypes call used below has explicit argtypes/restype.
# ---------------------------------------------------------------------------

USER32 = ctypes.WinDLL("user32", use_last_error=True)
KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
try:
    SHCORE = ctypes.WinDLL("shcore", use_last_error=True)
except OSError:
    SHCORE = None

ULONG_PTR = ctypes.c_size_t


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

USER32.GetForegroundWindow.argtypes = []
USER32.GetForegroundWindow.restype = wintypes.HWND
USER32.IsWindow.argtypes = [wintypes.HWND]
USER32.IsWindow.restype = wintypes.BOOL
USER32.IsWindowVisible.argtypes = [wintypes.HWND]
USER32.IsWindowVisible.restype = wintypes.BOOL
USER32.IsIconic.argtypes = [wintypes.HWND]
USER32.IsIconic.restype = wintypes.BOOL
USER32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
USER32.GetAncestor.restype = wintypes.HWND
USER32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
USER32.GetWindowThreadProcessId.restype = wintypes.DWORD
USER32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
USER32.GetClientRect.restype = wintypes.BOOL
USER32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
USER32.ClientToScreen.restype = wintypes.BOOL
USER32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
USER32.GetWindowTextLengthW.restype = ctypes.c_int
USER32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
USER32.GetWindowTextW.restype = ctypes.c_int
USER32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
USER32.GetClassNameW.restype = ctypes.c_int
USER32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
USER32.EnumWindows.restype = wintypes.BOOL
USER32.SetForegroundWindow.argtypes = [wintypes.HWND]
USER32.SetForegroundWindow.restype = wintypes.BOOL
USER32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
USER32.ShowWindow.restype = wintypes.BOOL
USER32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
USER32.GetCursorPos.restype = wintypes.BOOL
USER32.GetAsyncKeyState.argtypes = [ctypes.c_int]
USER32.GetAsyncKeyState.restype = ctypes.c_short
USER32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
USER32.SendInput.restype = wintypes.UINT
USER32.GetSystemMetrics.argtypes = [ctypes.c_int]
USER32.GetSystemMetrics.restype = ctypes.c_int
USER32.SetProcessDPIAware.argtypes = []
USER32.SetProcessDPIAware.restype = wintypes.BOOL

KERNEL32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
KERNEL32.OpenProcess.restype = wintypes.HANDLE
KERNEL32.CloseHandle.argtypes = [wintypes.HANDLE]
KERNEL32.CloseHandle.restype = wintypes.BOOL
KERNEL32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
KERNEL32.QueryFullProcessImageNameW.restype = wintypes.BOOL
KERNEL32.GetProcessTimes.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
]
KERNEL32.GetProcessTimes.restype = wintypes.BOOL
KERNEL32.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
KERNEL32.GetFileAttributesW.restype = wintypes.DWORD

if SHCORE is not None:
    SHCORE.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
    SHCORE.SetProcessDpiAwareness.restype = ctypes.c_long


def _win_error(message: str) -> OSError:
    error = ctypes.get_last_error()
    if error:
        return ctypes.WinError(error)
    return OSError(message)


def _check_bool(ok: int, message: str) -> None:
    if not ok:
        raise _win_error(message)


def set_dpi_awareness() -> None:
    if SHCORE is not None:
        result = int(SHCORE.SetProcessDpiAwareness(2))
        if result == 0 or (result & 0xFFFFFFFF) == 0x80070005:
            return
    USER32.SetProcessDPIAware()


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def monotonic_ns() -> int:
    return time.perf_counter_ns()


def atomic_json_dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(temp, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_imwrite(path: Path, image: np.ndarray, quality: int = 82) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError(f"图像编码失败：{path.name}")
    temp = path.with_suffix(path.suffix + ".tmp")
    encoded.tofile(str(temp))
    os.replace(temp, path)


def safe_imread(path: Path) -> np.ndarray | None:
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        if data.size == 0:
            return None
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def normalize_title(title: str) -> str:
    return " ".join(title.split()).strip()


def title_prefix(title: str, limit: int = 24) -> str:
    clean = normalize_title(title)
    for separator in (" - ", " — ", " | ", "["):
        if separator in clean:
            clean = clean.split(separator, 1)[0].strip()
    return clean[:limit]


def normalize_process_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(path)).replace("/", "\\")


def path_hash(path: str) -> str:
    return hashlib.sha256(normalize_process_path(path).encode("utf-8", "surrogatepass")).hexdigest()


def is_hex_uuid(value: str) -> bool:
    return len(value) == 32 and all(ch in "0123456789abcdefABCDEF" for ch in value)


def path_is_reparse(path: Path) -> bool:
    attrs = int(KERNEL32.GetFileAttributesW(str(path)))
    if attrs == INVALID_FILE_ATTRIBUTES:
        return False
    return bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT)


def ensure_within(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise RuntimeError(f"路径越界：{resolved_candidate}") from exc
    return resolved_candidate


def safe_child_dir(root: Path, *parts: str, create: bool = True) -> Path:
    root = root.resolve(strict=False)
    if root.is_symlink() or (root.exists() and path_is_reparse(root)):
        raise RuntimeError(f"根目录不能是链接或 reparse point：{root}")
    current = root
    for part in parts:
        if not part or Path(part).name != part:
            raise RuntimeError(f"无效子目录名称：{part!r}")
        current = current / part
        ensure_within(root, current)
        if current.exists() and (current.is_symlink() or path_is_reparse(current)):
            raise RuntimeError(f"子目录不能是链接或 reparse point：{current}")
        if create:
            current.mkdir(exist_ok=True)
    return ensure_within(root, current)


def validate_tree_no_links(path: Path) -> None:
    if path.is_symlink() or path_is_reparse(path):
        raise RuntimeError(f"拒绝操作符号链接、目录联接点或 reparse point：{path}")
    if not path.exists():
        return
    for current, dirnames, filenames in os.walk(path, topdown=True, followlinks=False):
        current_path = Path(current)
        if current_path.is_symlink() or path_is_reparse(current_path):
            raise RuntimeError(f"目录树包含链接或 reparse point：{current_path}")
        for name in [*dirnames, *filenames]:
            child = current_path / name
            if child.is_symlink() or path_is_reparse(child):
                raise RuntimeError(f"目录树包含链接或 reparse point：{child}")


@dataclass(frozen=True)
class ClientRect:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x < self.right and self.top <= y < self.bottom

    def normalize(self, x: int, y: int) -> tuple[float, float]:
        nx = (x - self.left) / max(1, self.width - 1)
        ny = (y - self.top) / max(1, self.height - 1)
        return clamp(nx, 0.0, 1.0), clamp(ny, 0.0, 1.0)

    def denormalize(self, nx: float, ny: float) -> tuple[int, int]:
        x = self.left + round(clamp(nx, 0.0, 1.0) * max(1, self.width - 1))
        y = self.top + round(clamp(ny, 0.0, 1.0) * max(1, self.height - 1))
        return int(x), int(y)


@dataclass(frozen=True)
class WindowIdentity:
    hwnd: int
    pid: int
    process_creation_time: int
    process_name: str
    process_path: str
    process_path_hash: str
    window_class: str
    title: str
    title_prefix: str

    def persistent(self) -> dict[str, str]:
        return {
            "process_name": self.process_name,
            "process_path_hash": self.process_path_hash,
            "window_class": self.window_class,
            "title_prefix": self.title_prefix,
        }


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    title: str
    process_name: str
    window_class: str

    @property
    def display(self) -> str:
        clean = normalize_title(self.title)
        if len(clean) > 62:
            clean = clean[:59] + "..."
        return f"{clean}  [{self.process_name} · {self.window_class} · HWND {self.hwnd}]"


def get_window_title(hwnd: int) -> str:
    length = max(0, int(USER32.GetWindowTextLengthW(hwnd)))
    buffer = ctypes.create_unicode_buffer(length + 1)
    USER32.GetWindowTextW(hwnd, buffer, len(buffer))
    return buffer.value


def get_window_class(hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(512)
    count = int(USER32.GetClassNameW(hwnd, buffer, len(buffer)))
    if count <= 0:
        raise _win_error("GetClassNameW 失败")
    return buffer.value


def get_window_pid(hwnd: int) -> int:
    pid = wintypes.DWORD()
    thread_id = int(USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)))
    if thread_id == 0 or pid.value == 0:
        raise _win_error("GetWindowThreadProcessId 失败")
    return int(pid.value)


def query_process(pid: int) -> tuple[str, int]:
    handle = KERNEL32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        raise _win_error(f"OpenProcess({pid}) 失败")
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        _check_bool(
            KERNEL32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)),
            "QueryFullProcessImageNameW 失败",
        )
        creation = FILETIME()
        exit_time = FILETIME()
        kernel = FILETIME()
        user = FILETIME()
        _check_bool(
            KERNEL32.GetProcessTimes(
                handle,
                ctypes.byref(creation),
                ctypes.byref(exit_time),
                ctypes.byref(kernel),
                ctypes.byref(user),
            ),
            "GetProcessTimes 失败",
        )
        creation_value = (int(creation.dwHighDateTime) << 32) | int(creation.dwLowDateTime)
        return normalize_process_path(buffer.value), creation_value
    finally:
        KERNEL32.CloseHandle(handle)


def get_window_identity(hwnd: int) -> WindowIdentity:
    if not USER32.IsWindow(hwnd):
        raise RuntimeError("所选窗口已关闭。")
    pid = get_window_pid(hwnd)
    process_path, creation_time = query_process(pid)
    title = get_window_title(hwnd)
    return WindowIdentity(
        hwnd=int(hwnd),
        pid=pid,
        process_creation_time=creation_time,
        process_name=Path(process_path).name.casefold(),
        process_path=process_path,
        process_path_hash=path_hash(process_path),
        window_class=get_window_class(hwnd),
        title=title,
        title_prefix=title_prefix(title),
    )


def persistent_identity_matches(expected: dict[str, Any], current: WindowIdentity) -> bool:
    expected_hash = str(expected.get("process_path_hash", ""))
    expected_name = str(expected.get("process_name", "")).casefold()
    expected_class = str(expected.get("window_class", ""))
    if expected_hash and expected_hash != current.process_path_hash:
        return False
    if expected_name and expected_name != current.process_name:
        return False
    if expected_class and expected_class != current.window_class:
        return False
    return True


class WindowGuard:
    def __init__(self, hwnd: int, expected_persistent: dict[str, Any] | None = None) -> None:
        self.runtime = get_window_identity(hwnd)
        self.expected_persistent = expected_persistent
        if expected_persistent and not persistent_identity_matches(expected_persistent, self.runtime):
            raise RuntimeError("当前窗口的进程路径或窗口类与模型不一致。")
        self._last_deep_check_ns = 0

    def verify(self, deep_interval_seconds: float = 2.0) -> WindowIdentity:
        if not USER32.IsWindow(self.runtime.hwnd):
            raise RuntimeError("目标窗口已关闭。")
        pid = get_window_pid(self.runtime.hwnd)
        if pid != self.runtime.pid:
            raise RuntimeError("目标窗口 PID 已变化，已停止以防止操作错误窗口。")
        if get_window_class(self.runtime.hwnd) != self.runtime.window_class:
            raise RuntimeError("目标窗口类已变化，已停止。")
        now_ns = monotonic_ns()
        if now_ns - self._last_deep_check_ns >= int(deep_interval_seconds * 1e9):
            current = get_window_identity(self.runtime.hwnd)
            if current.process_creation_time != self.runtime.process_creation_time:
                raise RuntimeError("目标进程实例已变化，已停止。")
            if current.process_path_hash != self.runtime.process_path_hash:
                raise RuntimeError("目标进程路径已变化，已停止。")
            if self.expected_persistent and not persistent_identity_matches(self.expected_persistent, current):
                raise RuntimeError("目标窗口不再符合模型身份。")
            self._last_deep_check_ns = now_ns
        return self.runtime

    def is_foreground(self) -> bool:
        foreground = USER32.GetForegroundWindow()
        if not foreground:
            return False
        expected_root = USER32.GetAncestor(self.runtime.hwnd, GA_ROOT) or self.runtime.hwnd
        actual_root = USER32.GetAncestor(foreground, GA_ROOT) or foreground
        return int(expected_root) == int(actual_root)


def get_client_rect(hwnd: int) -> ClientRect:
    if not USER32.IsWindow(hwnd):
        raise RuntimeError("所选窗口已关闭。")
    rect = RECT()
    _check_bool(USER32.GetClientRect(hwnd, ctypes.byref(rect)), "GetClientRect 失败")
    top_left = POINT(rect.left, rect.top)
    bottom_right = POINT(rect.right, rect.bottom)
    _check_bool(USER32.ClientToScreen(hwnd, ctypes.byref(top_left)), "ClientToScreen 失败")
    _check_bool(USER32.ClientToScreen(hwnd, ctypes.byref(bottom_right)), "ClientToScreen 失败")
    width = int(bottom_right.x - top_left.x)
    height = int(bottom_right.y - top_left.y)
    if width <= 0 or height <= 0:
        raise RuntimeError("窗口客户区尺寸无效，窗口可能已最小化。")
    return ClientRect(int(top_left.x), int(top_left.y), width, height)


def get_cursor_pos() -> tuple[int, int]:
    point = POINT()
    _check_bool(USER32.GetCursorPos(ctypes.byref(point)), "GetCursorPos 失败")
    return int(point.x), int(point.y)


def get_physical_buttons() -> dict[str, bool]:
    return {
        "left": bool(USER32.GetAsyncKeyState(VK_LBUTTON) & 0x8000),
        "right": bool(USER32.GetAsyncKeyState(VK_RBUTTON) & 0x8000),
        "middle": bool(USER32.GetAsyncKeyState(VK_MBUTTON) & 0x8000),
    }


def bring_window_to_front(hwnd: int) -> None:
    if USER32.IsIconic(hwnd):
        USER32.ShowWindow(hwnd, SW_RESTORE)
    USER32.SetForegroundWindow(hwnd)


def enumerate_windows() -> list[WindowInfo]:
    windows: list[WindowInfo] = []

    @WNDENUMPROC
    def callback(hwnd: int, _: int) -> bool:
        try:
            if not USER32.IsWindowVisible(hwnd) or USER32.IsIconic(hwnd):
                return True
            title = get_window_title(hwnd).strip()
            if not title:
                return True
            rect = get_client_rect(hwnd)
            if rect.width < 120 or rect.height < 80:
                return True
            identity = get_window_identity(hwnd)
            windows.append(
                WindowInfo(
                    hwnd=int(hwnd),
                    title=title,
                    process_name=identity.process_name,
                    window_class=identity.window_class,
                )
            )
        except Exception:
            pass
        return True

    _check_bool(USER32.EnumWindows(callback, 0), "EnumWindows 失败")
    windows.sort(key=lambda item: (item.process_name, item.title.casefold()))
    return windows


def capture_client(sct: mss.mss, rect: ClientRect) -> np.ndarray:
    shot = sct.grab({"left": rect.left, "top": rect.top, "width": rect.width, "height": rect.height})
    bgra = np.asarray(shot, dtype=np.uint8)
    return cv2.cvtColor(bgra, cv2.COLOR_BGRA2BGR)


def vectorized_grid_stats(hsv: np.ndarray) -> np.ndarray:
    # FEATURE_HEIGHT=18 and FEATURE_WIDTH=32 divide exactly into 6x8 cells.
    cell_h = FEATURE_HEIGHT // GRID_ROWS
    cell_w = FEATURE_WIDTH // GRID_COLS
    blocks = hsv.reshape(GRID_ROWS, cell_h, GRID_COLS, cell_w, 3).transpose(0, 2, 1, 3, 4)
    means = blocks.mean(axis=(2, 3))
    stds = blocks.std(axis=(2, 3))
    return np.clip(np.concatenate((means, stds), axis=2), 0, 255).astype(np.uint8).ravel()


def make_visual_feature(image_bgr: np.ndarray, prev_gray: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    resized = cv2.resize(image_bgr, (FEATURE_WIDTH, FEATURE_HEIGHT), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    hsv[:, :, 0] = np.clip(hsv[:, :, 0].astype(np.float32) * (255.0 / 179.0), 0, 255).astype(np.uint8)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    diff = np.zeros_like(gray) if prev_gray is None else cv2.absdiff(gray, prev_gray)
    edge = cv2.Canny(gray, 48, 128)
    stats = vectorized_grid_stats(hsv)
    feature = np.concatenate((hsv.ravel(), gray.ravel(), diff.ravel(), edge.ravel(), stats)).astype(np.uint8)
    if feature.size != VISUAL_FEATURE_DIM:
        raise RuntimeError(f"视觉特征维数异常：{feature.size} != {VISUAL_FEATURE_DIM}")
    return feature, gray


def make_state_feature(
    x_norm: float,
    y_norm: float,
    buttons: dict[str, bool],
    dt: float,
    recording_ready: bool = True,
) -> np.ndarray:
    return np.asarray(
        [
            round(clamp(x_norm, 0.0, 1.0) * 255),
            round(clamp(y_norm, 0.0, 1.0) * 255),
            255 if buttons.get("left", False) else 0,
            255 if buttons.get("right", False) else 0,
            255 if buttons.get("middle", False) else 0,
            round(clamp(dt, 0.0, 0.25) / 0.25 * 255),
            255 if recording_ready else 0,
        ],
        dtype=np.uint8,
    )


def combine_feature(visual: np.ndarray, state: np.ndarray) -> np.ndarray:
    feature = np.concatenate((visual, state)).astype(np.uint8, copy=False)
    if feature.size != FEATURE_DIM:
        raise RuntimeError(f"总特征维数异常：{feature.size} != {FEATURE_DIM}")
    return feature


class GameRegistry:
    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root.resolve(strict=False)
        if self.data_root.is_symlink() or path_is_reparse(self.data_root):
            raise RuntimeError("数据根目录不能是符号链接、目录联接点或 reparse point。")
        self.games_root = self.data_root / "games"
        self.index_path = self.data_root / "games.json"
        self.games_root.mkdir(parents=True, exist_ok=True)
        if self.games_root.is_symlink() or path_is_reparse(self.games_root):
            raise RuntimeError("games 目录不能是符号链接、目录联接点或 reparse point。")

    def load(self) -> list[dict[str, str]]:
        if not self.index_path.exists():
            return []
        try:
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
        except Exception as exc:
            backup = self.index_path.with_name(f"games.broken_{now_stamp()}.json")
            shutil.copy2(self.index_path, backup)
            raise RuntimeError(f"games.json 解析失败，已备份为 {backup.name}：{exc}") from exc
        if not isinstance(data, list):
            raise RuntimeError("games.json 顶层必须是数组。")
        result: list[dict[str, str]] = []
        seen_ids: set[str] = set()
        for item in data:
            if not isinstance(item, dict):
                raise RuntimeError("games.json 含有无效项目。")
            game_id = str(item.get("id", ""))
            name = str(item.get("name", "")).strip()
            normalized_id = game_id.lower()
            if not is_hex_uuid(game_id) or not name or normalized_id in seen_ids:
                raise RuntimeError("games.json 含有无效或重复的游戏 ID/名称。")
            seen_ids.add(normalized_id)
            self.game_dir(normalized_id, create=False)
            result.append({"id": normalized_id, "name": name})
        return result

    def save(self, games: list[dict[str, str]]) -> None:
        checked: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in games:
            game_id = str(item.get("id", "")).lower()
            name = str(item.get("name", "")).strip()
            if not is_hex_uuid(game_id) or not name or game_id in seen:
                raise RuntimeError("拒绝保存无效 games.json。")
            seen.add(game_id)
            checked.append({"id": game_id, "name": name})
        atomic_json_dump(self.index_path, checked)

    def game_dir(self, game_id: str, create: bool = True) -> Path:
        if not is_hex_uuid(game_id):
            raise RuntimeError("游戏 ID 必须是 32 位十六进制 UUID。")
        candidate = self.games_root / game_id.lower()
        resolved = ensure_within(self.games_root, candidate)
        if candidate.exists() and (candidate.is_symlink() or path_is_reparse(candidate)):
            raise RuntimeError("游戏目录不能是符号链接、目录联接点或 reparse point。")
        if create:
            candidate.mkdir(parents=True, exist_ok=True)
        return resolved

    def create(self, games: list[dict[str, str]], name: str) -> dict[str, str]:
        clean = name.strip()
        if not clean:
            raise RuntimeError("游戏名称不能为空。")
        item = {"id": uuid.uuid4().hex, "name": clean}
        self.game_dir(item["id"], create=True)
        games.append(item)
        self.save(games)
        return item

    def rename(self, games: list[dict[str, str]], game_id: str, name: str) -> None:
        clean = name.strip()
        if not clean:
            raise RuntimeError("游戏名称不能为空。")
        for item in games:
            if item["id"] == game_id:
                item["name"] = clean
                self.save(games)
                return
        raise RuntimeError("没有找到要修改的游戏。")

    def delete(self, games: list[dict[str, str]], game_id: str) -> None:
        if not is_hex_uuid(game_id):
            raise RuntimeError("无效游戏 ID。")
        target = self.game_dir(game_id, create=False)
        target = ensure_within(self.games_root, target)
        if target.exists():
            validate_tree_no_links(target)
            target = ensure_within(self.games_root, target)
            if target.is_symlink() or path_is_reparse(target):
                raise RuntimeError("删除前复检发现链接或 reparse point。")
            shutil.rmtree(target)
        games[:] = [item for item in games if item["id"] != game_id]
        self.save(games)


class EscWatcher:
    def __init__(self, stop_event: threading.Event) -> None:
        self.stop_event = stop_event
        self.listener: keyboard.Listener | None = None

    def start(self) -> None:
        def on_press(key: keyboard.Key | keyboard.KeyCode) -> bool | None:
            if key == keyboard.Key.esc:
                self.stop_event.set()
                return False
            return None

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

    def stop(self) -> None:
        if self.listener is not None:
            try:
                self.listener.stop()
                self.listener.join(timeout=1.0)
            except Exception:
                pass
            self.listener = None


@dataclass
class RawMouseEvent:
    timestamp_ns: int
    kind: str
    x: int
    y: int
    button: str | None = None
    pressed: bool | None = None
    dx: int = 0
    dy: int = 0


@dataclass
class WriteItem:
    frame_name: str
    frame: np.ndarray
    row: dict[str, Any]


class SessionChunkWriter:
    def __init__(self, session_dir: Path, chunk_size: int = CHUNK_SIZE) -> None:
        self.session_dir = session_dir
        self.frames_dir = session_dir / "frames"
        self.chunks_dir = session_dir / "chunks"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size
        self.queue: queue.Queue[WriteItem | None] = queue.Queue(maxsize=64)
        self.error: BaseException | None = None
        self.manifest_chunks: list[dict[str, Any]] = []
        self._thread = threading.Thread(target=self._run, name="SessionChunkWriter", daemon=False)
        self._started = False
        self._count = 0

    def start(self) -> None:
        self._thread.start()
        self._started = True

    def submit(self, item: WriteItem) -> None:
        if self.error is not None:
            raise RuntimeError(f"写入线程已失败：{self.error}") from self.error
        try:
            self.queue.put(item, timeout=2.0)
        except queue.Full as exc:
            raise RuntimeError("写入队列已满，已停止学习以避免丢失样本。") from exc

    def close(self) -> None:
        if not self._started:
            return
        deadline = time.monotonic() + 10.0
        sentinel_sent = False
        while self._thread.is_alive() and not sentinel_sent and time.monotonic() < deadline:
            try:
                self.queue.put(None, timeout=0.25)
                sentinel_sent = True
            except queue.Full:
                if self.error is not None:
                    break
        self._thread.join(timeout=15.0)
        if self._thread.is_alive():
            raise RuntimeError("写入线程未能在限定时间内退出。")
        if self.error is not None:
            raise RuntimeError(f"写入线程失败：{self.error}") from self.error

    def _run(self) -> None:
        rows: list[dict[str, Any]] = []
        chunk_index = 0
        try:
            while True:
                item = self.queue.get()
                if item is None:
                    break
                safe_imwrite(self.frames_dir / item.frame_name, item.frame)
                rows.append(item.row)
                self._count += 1
                if len(rows) >= self.chunk_size:
                    self._flush_chunk(rows, chunk_index)
                    rows = []
                    chunk_index += 1
            if rows:
                self._flush_chunk(rows, chunk_index)
        except BaseException as exc:
            self.error = exc

    def _flush_chunk(self, rows: list[dict[str, Any]], chunk_index: int) -> None:
        name = f"chunk_{chunk_index:06d}.jsonl"
        path = self.chunks_dir / name
        temp = path.with_suffix(path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp, path)
        self.manifest_chunks.append(
            {
                "file": f"chunks/{name}",
                "samples": len(rows),
                "sha256": sha256_file(path),
            }
        )


class LearningRecorder:
    def __init__(
        self,
        hwnd: int,
        output_root: Path,
        fps: int,
        stop_event: threading.Event,
        status: Callable[[str], None],
        progress: Callable[[float], None],
    ) -> None:
        self.hwnd = hwnd
        self.output_root = output_root
        self.fps = fps
        self.stop_event = stop_event
        self.status = status
        self.progress = progress
        self.guard = WindowGuard(hwnd)
        self.raw_events: queue.Queue[RawMouseEvent] = queue.Queue()
        self.mouse_listener: mouse.Listener | None = None
        self.esc = EscWatcher(stop_event)
        self.recording_enabled = False
        self.accepted_down = {name: False for name in BUTTONS}
        self.frame_count = 0
        self.sample_count = 0

    @staticmethod
    def _button_name(button: mouse.Button) -> str | None:
        if button == mouse.Button.left:
            return "left"
        if button == mouse.Button.right:
            return "right"
        if button == mouse.Button.middle:
            return "middle"
        return None

    def _win32_event_filter(self, _msg: int, data: Any) -> bool:
        try:
            flags = int(getattr(data, "flags", 0))
            extra = int(getattr(data, "dwExtraInfo", 0))
            return not (flags & LLMHF_INJECTED or extra == INPUT_MARKER)
        except Exception:
            return True

    def _on_move(self, x: int, y: int) -> None:
        if not self.recording_enabled:
            return
        self.raw_events.put(RawMouseEvent(monotonic_ns(), "move", int(x), int(y)))

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if not self.recording_enabled:
            return
        name = self._button_name(button)
        if name is None:
            return
        self.raw_events.put(
            RawMouseEvent(
                monotonic_ns(),
                "button",
                int(x),
                int(y),
                button=name,
                pressed=bool(pressed),
            )
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self.recording_enabled:
            return
        self.raw_events.put(
            RawMouseEvent(monotonic_ns(), "scroll", int(x), int(y), dx=int(dx), dy=int(dy))
        )

    def _start_listeners(self) -> None:
        kwargs: dict[str, Any] = {
            "on_move": self._on_move,
            "on_click": self._on_click,
            "on_scroll": self._on_scroll,
        }
        if sys.platform == "win32":
            kwargs["win32_event_filter"] = self._win32_event_filter
        self.mouse_listener = mouse.Listener(**kwargs)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        self.esc.start()

    def _stop_listeners(self) -> None:
        self.recording_enabled = False
        self.esc.stop()
        if self.mouse_listener is not None:
            try:
                self.mouse_listener.stop()
                self.mouse_listener.join(timeout=1.5)
            except Exception:
                pass
            self.mouse_listener = None

    def _clear_event_queue(self) -> None:
        while True:
            try:
                self.raw_events.get_nowait()
            except queue.Empty:
                break

    def _reset_focus_state(self) -> None:
        self.recording_enabled = False
        self._clear_event_queue()
        for name in BUTTONS:
            self.accepted_down[name] = False

    def _process_events(self, rect: ClientRect) -> tuple[list[str], int, int]:
        edges: list[str] = []
        wheel_v = 0
        wheel_h = 0
        while True:
            try:
                event = self.raw_events.get_nowait()
            except queue.Empty:
                break
            if event.kind == "button" and event.button is not None and event.pressed is not None:
                name = event.button
                if event.pressed:
                    if rect.contains(event.x, event.y) and not self.accepted_down[name]:
                        self.accepted_down[name] = True
                        edges.append(f"{name}_down")
                else:
                    if self.accepted_down[name]:
                        self.accepted_down[name] = False
                        edges.append(f"{name}_up")
            elif event.kind == "scroll" and rect.contains(event.x, event.y):
                wheel_h += event.dx
                wheel_v += event.dy
        return edges, wheel_v, wheel_h

    def run(self) -> dict[str, Any]:
        sessions_dir = safe_child_dir(self.output_root, "sessions")
        session_name = f"session_{now_stamp()}"
        session_dir = safe_child_dir(sessions_dir, session_name, create=False)
        session_dir.mkdir(exist_ok=False)
        writer = SessionChunkWriter(session_dir)
        initial_rect = get_client_rect(self.hwnd)
        identity = self.guard.runtime
        manifest: dict[str, Any] = {
            "dataset_version": DATASET_VERSION,
            "app": APP_NAME,
            "app_version": APP_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "clock": "time.perf_counter_ns",
            "window_identity": identity.persistent(),
            "runtime_diagnostics": {
                "hwnd": identity.hwnd,
                "pid": identity.pid,
                "process_creation_time": identity.process_creation_time,
                "process_path": identity.process_path,
                "initial_title": identity.title,
            },
            "fps_requested": self.fps,
            "initial_client_size": [initial_rect.width, initial_rect.height],
            "feature_size": [FEATURE_WIDTH, FEATURE_HEIGHT],
            "status": "recording",
            "chunks": [],
        }
        atomic_json_dump(session_dir / "manifest.json", manifest)
        writer.start()
        self._start_listeners()
        bring_window_to_front(self.hwnd)
        self.status("学习中：只记录前台客户区内开始的鼠标操作；按 ESC 结束。")

        period_ns = int(1e9 / max(1, self.fps))
        next_tick_ns = monotonic_ns()
        last_frame_ns: int | None = None
        last_norm: tuple[float, float] | None = None
        focus_stable = 0
        focus_epoch = -1
        was_foreground = False
        last_status_ns = 0
        disk_check_counter = 0

        try:
            with mss.mss() as sct:
                while not self.stop_event.is_set():
                    if writer.error is not None:
                        raise RuntimeError(f"写入线程异常：{writer.error}") from writer.error
                    self.guard.verify()
                    rect = get_client_rect(self.hwnd)
                    foreground = self.guard.is_foreground()
                    now_ns = monotonic_ns()

                    if not foreground:
                        if was_foreground:
                            self._reset_focus_state()
                            last_frame_ns = None
                            last_norm = None
                            focus_stable = 0
                        was_foreground = False
                        if now_ns - last_status_ns >= 1_000_000_000:
                            self.status("学习暂停：前台已丢失；聚焦点击不会写入训练数据。")
                            last_status_ns = now_ns
                        time.sleep(0.08)
                        next_tick_ns = monotonic_ns()
                        continue

                    if not was_foreground:
                        self._reset_focus_state()
                        get_cursor_pos()
                        get_physical_buttons()
                        focus_epoch += 1
                        focus_stable = 0
                        last_frame_ns = None
                        last_norm = None
                    was_foreground = True

                    frame = capture_client(sct, rect)
                    cursor_x, cursor_y = get_cursor_pos()
                    nx, ny = rect.normalize(cursor_x, cursor_y)

                    if focus_stable < FOCUS_WARMUP_FRAMES:
                        physical_buttons = get_physical_buttons()
                        self._clear_event_queue()
                        self.recording_enabled = False
                        last_norm = (nx, ny)
                        last_frame_ns = now_ns
                        if any(physical_buttons.values()):
                            focus_stable = 0
                            if now_ns - last_status_ns >= 500_000_000:
                                self.status("学习恢复准备：请先释放所有鼠标按键……")
                                last_status_ns = now_ns
                        else:
                            focus_stable += 1
                            if now_ns - last_status_ns >= 500_000_000:
                                self.status(f"学习恢复准备：等待新画面 {focus_stable}/{FOCUS_WARMUP_FRAMES}……")
                                last_status_ns = now_ns
                    else:
                        self.recording_enabled = True
                        edges, wheel_v, wheel_h = self._process_events(rect)
                        dt = (
                            clamp((now_ns - last_frame_ns) / 1e9, 1e-4, 0.5)
                            if last_frame_ns is not None
                            else 1.0 / max(1, self.fps)
                        )
                        if last_norm is None:
                            vx = vy = 0.0
                        else:
                            vx = (nx - last_norm[0]) / dt
                            vy = (ny - last_norm[1]) / dt
                        frame_name = f"{self.frame_count:08d}.jpg"
                        row = {
                            "sample_id": self.sample_count,
                            "timestamp_ns": now_ns,
                            "dt": round(dt, 9),
                            "frame": f"frames/{frame_name}",
                            "x_norm": round(nx, 7),
                            "y_norm": round(ny, 7),
                            "vx": round(vx, 7),
                            "vy": round(vy, 7),
                            "left_down": bool(self.accepted_down["left"]),
                            "right_down": bool(self.accepted_down["right"]),
                            "middle_down": bool(self.accepted_down["middle"]),
                            "button_edges": edges,
                            "wheel_v": int(wheel_v),
                            "wheel_h": int(wheel_h),
                            "client_width": rect.width,
                            "client_height": rect.height,
                            "focus_epoch": focus_epoch,
                        }
                        writer.submit(WriteItem(frame_name, frame.copy(), row))
                        self.frame_count += 1
                        self.sample_count += 1
                        last_norm = (nx, ny)
                        last_frame_ns = now_ns

                    disk_check_counter += 1
                    if disk_check_counter >= max(10, self.fps * 2):
                        disk_check_counter = 0
                        free = shutil.disk_usage(session_dir).free
                        if free < MIN_FREE_DISK_BYTES:
                            raise RuntimeError(
                                f"剩余磁盘空间低于 {MIN_FREE_DISK_BYTES / 1024**3:.1f} GB，已停止学习。"
                            )

                    if now_ns - last_status_ns >= 1_000_000_000 and self.recording_enabled:
                        self.status(f"学习中：{self.frame_count} 帧，{self.sample_count} 条连续样本；ESC 结束。")
                        self.progress((self.frame_count % 100) / 100.0)
                        last_status_ns = now_ns

                    next_tick_ns += period_ns
                    sleep_ns = next_tick_ns - monotonic_ns()
                    if sleep_ns > 0:
                        time.sleep(sleep_ns / 1e9)
                    else:
                        next_tick_ns = monotonic_ns()
        finally:
            self._stop_listeners()
            close_error: BaseException | None = None
            try:
                writer.close()
            except BaseException as exc:
                close_error = exc
            manifest["ended_at"] = datetime.now().isoformat(timespec="seconds")
            manifest["frames"] = self.frame_count
            manifest["samples"] = self.sample_count
            manifest["chunks"] = writer.manifest_chunks
            manifest["status"] = "complete" if self.sample_count and close_error is None else "failed"
            if close_error is not None:
                manifest["writer_error"] = str(close_error)
            atomic_json_dump(session_dir / "manifest.json", manifest)
            if close_error is not None:
                raise close_error

        return {
            "session_dir": str(session_dir),
            "frames": self.frame_count,
            "samples": self.sample_count,
        }


@dataclass
class LoadedSession:
    path: Path
    manifest: dict[str, Any]
    rows: list[dict[str, Any]]
    duration: float
    damaged_chunks: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass
class FrameSample:
    visual: np.ndarray
    dt: float
    x_norm: float
    y_norm: float
    vx: float
    vy: float
    buttons: dict[str, bool]
    wheel_v_rate: float
    wheel_h_rate: float
    client_width: int
    client_height: int
    edges: tuple[str, ...]
    focus_epoch: int = 0

    @property
    def moving(self) -> bool:
        return math.hypot(self.vx, self.vy) >= 0.012


@dataclass(frozen=True)
class PolicyConfig:
    move_threshold: float = 0.72
    press_threshold: float = 0.84
    release_threshold: float = 0.78
    pending_seconds: float = 0.035
    min_hold_seconds: float = 0.065
    max_hold_seconds: float = 1.6
    click_refractory_seconds: float = 0.075
    velocity_smoothing: float = 0.45
    max_speed_norm_per_second: float = 2.2
    max_step_norm: float = 0.08
    wheel_threshold: float = 0.80
    wheel_cooldown_seconds: float = 0.10
    max_wheel_delta: int = 3

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class ModelPrediction:
    move_probability: float
    vx: float
    vy: float
    button_press_probabilities: dict[str, float]
    button_release_probabilities: dict[str, float]
    wheel_v_probability: float = 0.0
    wheel_h_probability: float = 0.0
    wheel_v_rate: float = 0.0
    wheel_h_rate: float = 0.0


@dataclass
class PlannedActions:
    dx_norm: float = 0.0
    dy_norm: float = 0.0
    button_events: list[str] = field(default_factory=list)
    wheel_v: int = 0
    wheel_h: int = 0


@dataclass
class ButtonFSM:
    state: str = "UP"
    pending_seconds: float = 0.0
    held_seconds: float = 0.0
    since_transition: float = 999.0
    release_latched: bool = False


class PolicyState:
    def __init__(self, config: PolicyConfig, x_norm: float = 0.5, y_norm: float = 0.5) -> None:
        self.config = config
        self.x_norm = clamp(x_norm, 0.0, 1.0)
        self.y_norm = clamp(y_norm, 0.0, 1.0)
        self.buttons = {name: False for name in BUTTONS}
        self.fsms = {name: ButtonFSM() for name in BUTTONS}
        self.smooth_vx = 0.0
        self.smooth_vy = 0.0
        self.wheel_since = {"v": 999.0, "h": 999.0}

    def reset_buttons(self) -> list[str]:
        releases: list[str] = []
        for name in BUTTONS:
            if self.buttons[name]:
                releases.append(f"{name}_up")
            self.buttons[name] = False
            self.fsms[name] = ButtonFSM()
        return releases

    def step(self, prediction: ModelPrediction, dt: float) -> PlannedActions:
        dt = clamp(float(dt), 1e-4, 0.5)
        result = PlannedActions()
        alpha = self.config.velocity_smoothing
        if prediction.move_probability >= self.config.move_threshold:
            target_vx = float(prediction.vx)
            target_vy = float(prediction.vy)
        else:
            target_vx = target_vy = 0.0
        speed = math.hypot(target_vx, target_vy)
        if speed > self.config.max_speed_norm_per_second:
            scale = self.config.max_speed_norm_per_second / max(speed, 1e-9)
            target_vx *= scale
            target_vy *= scale
        self.smooth_vx = alpha * target_vx + (1.0 - alpha) * self.smooth_vx
        self.smooth_vy = alpha * target_vy + (1.0 - alpha) * self.smooth_vy
        dx = self.smooth_vx * dt
        dy = self.smooth_vy * dt
        step = math.hypot(dx, dy)
        if step > self.config.max_step_norm:
            scale = self.config.max_step_norm / max(step, 1e-9)
            dx *= scale
            dy *= scale
        result.dx_norm = dx
        result.dy_norm = dy
        self.x_norm = clamp(self.x_norm + dx, 0.0, 1.0)
        self.y_norm = clamp(self.y_norm + dy, 0.0, 1.0)

        for name in BUTTONS:
            fsm = self.fsms[name]
            fsm.since_transition += dt
            if self.buttons[name]:
                fsm.held_seconds += dt
            press_probability = clamp(prediction.button_press_probabilities.get(name, 0.0), 0.0, 1.0)
            release_probability = clamp(prediction.button_release_probabilities.get(name, 0.0), 0.0, 1.0)

            if self.buttons[name] and fsm.held_seconds >= self.config.max_hold_seconds:
                result.button_events.append(f"{name}_up")
                self.buttons[name] = False
                self.fsms[name] = ButtonFSM(since_transition=0.0)
                continue

            if fsm.since_transition < self.config.click_refractory_seconds:
                continue

            if not self.buttons[name]:
                if press_probability >= self.config.press_threshold:
                    if fsm.state != "PRESS_PENDING":
                        fsm.state = "PRESS_PENDING"
                        fsm.pending_seconds = dt
                    else:
                        fsm.pending_seconds += dt
                    if fsm.pending_seconds >= self.config.pending_seconds:
                        result.button_events.append(f"{name}_down")
                        self.buttons[name] = True
                        self.fsms[name] = ButtonFSM(
                            state="DOWN",
                            held_seconds=0.0,
                            since_transition=0.0,
                            release_latched=(
                                release_probability >= self.config.release_threshold
                            ),
                        )
                else:
                    fsm.state = "UP"
                    fsm.pending_seconds = 0.0
            else:
                if (release_probability >= self.config.release_threshold or fsm.release_latched) and fsm.held_seconds >= self.config.min_hold_seconds:
                    if fsm.state != "RELEASE_PENDING":
                        fsm.state = "RELEASE_PENDING"
                        fsm.pending_seconds = dt
                    else:
                        fsm.pending_seconds += dt
                    if fsm.pending_seconds >= self.config.pending_seconds:
                        result.button_events.append(f"{name}_up")
                        self.buttons[name] = False
                        self.fsms[name] = ButtonFSM(since_transition=0.0)
                else:
                    fsm.state = "DOWN"
                    fsm.pending_seconds = 0.0

        self.wheel_since["v"] += dt
        self.wheel_since["h"] += dt
        if (
            prediction.wheel_v_probability >= self.config.wheel_threshold
            and self.wheel_since["v"] >= self.config.wheel_cooldown_seconds
        ):
            delta = int(round(prediction.wheel_v_rate * dt))
            result.wheel_v = int(clamp(delta, -self.config.max_wheel_delta, self.config.max_wheel_delta))
            if result.wheel_v:
                self.wheel_since["v"] = 0.0
        if (
            prediction.wheel_h_probability >= self.config.wheel_threshold
            and self.wheel_since["h"] >= self.config.wheel_cooldown_seconds
        ):
            delta = int(round(prediction.wheel_h_rate * dt))
            result.wheel_h = int(clamp(delta, -self.config.max_wheel_delta, self.config.max_wheel_delta))
            if result.wheel_h:
                self.wheel_since["h"] = 0.0
        return result


def positive_probability(model: Any, feature: np.ndarray) -> float:
    probabilities = model.predict_proba(feature)[0]
    classes = [int(value) for value in model.classes_]
    if 1 not in classes:
        return 0.0
    return float(probabilities[classes.index(1)])


def build_prediction(models: dict[str, Any], feature: np.ndarray) -> ModelPrediction:
    move_probability = positive_probability(models["move_gate"], feature)
    vx = vy = 0.0
    movement_regressor = models.get("movement_regressor")
    if movement_regressor is not None:
        velocity = movement_regressor.predict(feature)[0]
        vx, vy = float(velocity[0]), float(velocity[1])
    button_press_probabilities = {
        name: positive_probability(models["button_models"][name]["press"], feature)
        for name in BUTTONS
    }
    button_release_probabilities = {
        name: positive_probability(models["button_models"][name]["release"], feature)
        for name in BUTTONS
    }
    wheel_v_probability = wheel_h_probability = 0.0
    wheel_v_rate = wheel_h_rate = 0.0
    wheel_models = models.get("wheel_models") or {}
    if wheel_models.get("v_gate") is not None:
        wheel_v_probability = positive_probability(wheel_models["v_gate"], feature)
    if wheel_models.get("h_gate") is not None:
        wheel_h_probability = positive_probability(wheel_models["h_gate"], feature)
    if wheel_models.get("regressor") is not None:
        wheel = wheel_models["regressor"].predict(feature)[0]
        wheel_v_rate, wheel_h_rate = float(wheel[0]), float(wheel[1])
    return ModelPrediction(
        move_probability=move_probability,
        vx=vx,
        vy=vy,
        button_press_probabilities=button_press_probabilities,
        button_release_probabilities=button_release_probabilities,
        wheel_v_probability=wheel_v_probability,
        wheel_h_probability=wheel_h_probability,
        wheel_v_rate=wheel_v_rate,
        wheel_h_rate=wheel_h_rate,
    )


class DatasetReviewer:
    def __init__(
        self,
        output_root: Path,
        stop_event: threading.Event,
        status: Callable[[str], None],
        progress: Callable[[float], None],
    ) -> None:
        self.output_root = output_root
        self.stop_event = stop_event
        self.status = status
        self.progress = progress
        self.esc = EscWatcher(stop_event)
        self.invalid_samples = 0
        self.damaged_chunks = 0
        self.warnings: list[str] = []
        self.n_jobs = max(1, (os.cpu_count() or 2) - 1)

    def run(self) -> dict[str, Any]:
        self.esc.start()
        review_started_ns = monotonic_ns()
        tracemalloc.start()
        try:
            sessions = self._load_sessions()
            if not sessions:
                raise RuntimeError("没有找到完整学习会话。")
            sessions_found = len(sessions)
            identity = self._validate_session_identities(sessions)
            session_samples = self._extract_all_sessions(sessions)
            del sessions
            session_samples = {key: value for key, value in session_samples.items() if value}
            if not session_samples:
                raise RuntimeError("所有学习会话都无法提取有效特征。")

            weighted_training_fps = self._weighted_fps(session_samples)
            client_size_reference = self._reference_size(session_samples)
            ordered_ids = sorted(session_samples)
            publish_prerequisites = self._minimum_requirements(session_samples)
            enough_sessions = len(ordered_ids) >= MIN_SESSIONS
            if enough_sessions:
                validation_count = max(1, round(len(ordered_ids) * 0.25))
                validation_ids = ordered_ids[-validation_count:]
                train_ids = ordered_ids[:-validation_count]
                if len(train_ids) < 2:
                    train_ids = ordered_ids[:-1]
                    validation_ids = ordered_ids[-1:]
            else:
                train_ids = ordered_ids
                validation_ids = []

            train_samples = [sample for sid in train_ids for sample in session_samples[sid]]
            validation_sessions = [session_samples[sid] for sid in validation_ids]
            sampled_train = self._sample_training_only(train_samples)
            if len(sampled_train) < 100:
                raise RuntimeError(f"有效训练样本只有 {len(sampled_train)} 条，无法建立稳定模型。")

            train_samples_before_sampling = len(train_samples)
            train_samples_used = len(sampled_train)
            X_train, targets = self._training_arrays(sampled_train)
            for session_id in train_ids:
                session_samples.pop(session_id, None)
            del train_samples
            del sampled_train
            training_started_ns = monotonic_ns()
            self.status(
                f"复习中：训练 {len(train_ids)} 个会话，完整验证 {len(validation_ids)} 个会话；"
                f"训练采样 {train_samples_used} 条。"
            )

            if validation_sessions:
                best_training, best_config, metrics = self._select_and_train(
                    X_train, targets, validation_sessions
                )
                models = self._fit_models(X_train, targets, **best_training)
                metrics = self._evaluate_policy(models, best_config, validation_sessions)
            else:
                best_training = {
                    "tree_count": 64,
                    "max_depth": 22,
                    "reg_max_features": 0.35,
                }
                best_config = PolicyConfig()
                models = self._fit_models(X_train, targets, **best_training)
                metrics = {
                    "validated": False,
                    "reason": "少于 3 个独立会话，未执行完整会话验证。",
                    "validation_sessions": 0,
                }

            training_elapsed_seconds = (monotonic_ns() - training_started_ns) / 1e9
            validation_seconds = float(metrics.get("validation_seconds", 0.0))
            validation_ok = bool(metrics.get("passed", False)) if validation_sessions else False
            publishable = (
                enough_sessions
                and publish_prerequisites["passed"]
                and validation_seconds >= MIN_VALIDATION_SECONDS
                and validation_ok
                and self.damaged_chunks == 0
                and self.invalid_samples == 0
            )

            review_dir = safe_child_dir(self.output_root, "review")
            model_dir = safe_child_dir(self.output_root, "model")
            stamp = now_stamp()
            model_data = {
                "model_version": MODEL_VERSION,
                "app_version": APP_VERSION,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "feature_width": FEATURE_WIDTH,
                "feature_height": FEATURE_HEIGHT,
                "visual_feature_dim": VISUAL_FEATURE_DIM,
                "feature_dim": FEATURE_DIM,
                "sklearn_version": sklearn_version,
                "window_identity": identity,
                "models": models,
                "policy_config": best_config.as_dict(),
                "training_fps": weighted_training_fps,
                "client_size_reference": client_size_reference,
                "training_config": best_training,
                "metrics": metrics,
                "publishable": publishable,
            }

            experimental_path = review_dir / f"experimental_model_{stamp}.joblib"
            self._atomic_joblib_dump(model_data, experimental_path)
            model_path: Path | None = None
            if publishable:
                model_path = model_dir / MODEL_FILENAME
                self._publish_model(model_data, model_dir)

            _current_memory, peak_memory = tracemalloc.get_traced_memory()
            review_elapsed_seconds = (monotonic_ns() - review_started_ns) / 1e9
            report = {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "review_elapsed_seconds": round(review_elapsed_seconds, 3),
                "training_elapsed_seconds": round(training_elapsed_seconds, 3),
                "peak_python_memory_mb": round(peak_memory / 1024**2, 3),
                "experimental_model_size_mb": round(experimental_path.stat().st_size / 1024**2, 3),
                "published_model_size_mb": (
                    round(model_path.stat().st_size / 1024**2, 3) if model_path else None
                ),
                "sessions_found": sessions_found,
                "train_sessions": train_ids,
                "validation_sessions": validation_ids,
                "train_samples_before_sampling": train_samples_before_sampling,
                "train_samples_used": train_samples_used,
                "validation_samples_kept_complete": sum(len(s) for s in validation_sessions),
                "invalid_samples": self.invalid_samples,
                "damaged_chunks": self.damaged_chunks,
                "warnings": self.warnings,
                "minimum_requirements": publish_prerequisites,
                "metrics": metrics,
                "training_config": best_training,
                "policy_config": best_config.as_dict(),
                "publishable": publishable,
                "published_model": str(model_path) if model_path else None,
                "experimental_model": str(experimental_path),
                "integrity_notice": (
                    "SHA-256 仅用于完整性校验，不是可信签名。joblib 基于 pickle，"
                    "只能加载本程序在当前游戏目录内生成且通过结构校验的固定文件。"
                ),
            }
            report_path = review_dir / f"report_{stamp}.json"
            atomic_json_dump(report_path, report)
            self._write_metrics_csv(review_dir / f"session_metrics_{stamp}.csv", metrics)
            self.progress(1.0)
            return {
                "samples": train_samples_used,
                "metrics": metrics,
                "publishable": publishable,
                "model_path": str(model_path) if model_path else "",
                "experimental_path": str(experimental_path),
                "report_path": str(report_path),
            }
        finally:
            if tracemalloc.is_tracing():
                tracemalloc.stop()
            self.esc.stop()

    def _load_sessions(self) -> list[LoadedSession]:
        sessions_dir = safe_child_dir(self.output_root, "sessions", create=False)
        if not sessions_dir.exists():
            return []
        result: list[LoadedSession] = []
        paths = sorted(path for path in sessions_dir.glob("session_*") if path.is_dir())
        for index, session_dir in enumerate(paths):
            if session_dir.is_symlink() or path_is_reparse(session_dir):
                self.warnings.append(f"{session_dir.name}: 拒绝读取链接或 reparse point 会话")
                continue
            if self.stop_event.is_set():
                raise InterruptedError("复习已由 ESC 停止。")
            manifest_path = session_dir / "manifest.json"
            if not manifest_path.exists():
                self.warnings.append(f"{session_dir.name}: 缺少 manifest.json")
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception as exc:
                self.warnings.append(f"{session_dir.name}: manifest 损坏：{exc}")
                continue
            if manifest.get("status") != "complete":
                self.warnings.append(f"{session_dir.name}: 会话状态不是 complete")
                continue
            rows: list[dict[str, Any]] = []
            damaged = 0
            chunks = manifest.get("chunks")
            if isinstance(chunks, list) and chunks:
                for chunk in chunks:
                    try:
                        relative = str(chunk["file"])
                        path = ensure_within(session_dir, session_dir / relative)
                        expected = str(chunk["sha256"])
                        if not path.exists() or sha256_file(path) != expected:
                            damaged += 1
                            continue
                        with path.open("r", encoding="utf-8") as fh:
                            for line in fh:
                                rows.append(json.loads(line))
                    except Exception:
                        damaged += 1
                if damaged:
                    self.damaged_chunks += damaged
                    warning = f"{session_dir.name}: {damaged} 个 chunk 损坏，已明确排除并禁止发布模型"
                    self.warnings.append(warning)
                    self.status("警告：" + warning)
            else:
                legacy = session_dir / "actions.jsonl"
                if legacy.exists():
                    self.warnings.append(f"{session_dir.name}: 旧格式无 chunk 校验，按兼容模式读取")
                    rows = self._read_legacy_rows(legacy)
            if not rows:
                continue
            rows.sort(key=lambda row: int(row.get("timestamp_ns", 0)))
            duration = sum(clamp(float(row.get("dt", 0.0)), 0.0, 0.5) for row in rows)
            result.append(LoadedSession(session_dir, manifest, rows, duration, damaged))
            self.status(f"复习中：读取会话 {index + 1}/{len(paths)}……")
            self.progress(0.08 * (index + 1) / max(1, len(paths)))
        return result

    def _read_legacy_rows(self, action_path: Path) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        last_timestamp: float | None = None
        last_x = last_y = 0.5
        buttons = {name: False for name in BUTTONS}
        with action_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    old = json.loads(line)
                    timestamp = float(old.get("timestamp", 0.0))
                    dt = clamp(timestamp - last_timestamp, 1e-4, 0.5) if last_timestamp else 0.1
                    x = clamp(float(old.get("x_norm", 0.5)), 0.0, 1.0)
                    y = clamp(float(old.get("y_norm", 0.5)), 0.0, 1.0)
                    action = str(old.get("action", "idle"))
                    edges: list[str] = []
                    if action.endswith("_down") or action.endswith("_up"):
                        name, edge = action.split("_", 1)
                        if name in BUTTONS:
                            buttons[name] = edge == "down"
                            edges.append(action)
                    rows.append(
                        {
                            "timestamp_ns": int(timestamp * 1e9),
                            "dt": dt,
                            "frame": old.get("frame"),
                            "x_norm": x,
                            "y_norm": y,
                            "vx": (x - last_x) / dt,
                            "vy": (y - last_y) / dt,
                            "left_down": bool(old.get("left_down", buttons["left"])),
                            "right_down": bool(old.get("right_down", buttons["right"])),
                            "middle_down": bool(old.get("middle_down", buttons["middle"])),
                            "button_edges": edges,
                            "wheel_v": 0,
                            "wheel_h": 0,
                            "client_width": int(old.get("client_width", 1)),
                            "client_height": int(old.get("client_height", 1)),
                            "focus_epoch": 0,
                        }
                    )
                    last_timestamp = timestamp
                    last_x, last_y = x, y
                except Exception:
                    self.invalid_samples += 1
        return rows

    def _validate_session_identities(self, sessions: Sequence[LoadedSession]) -> dict[str, str]:
        identities = [session.manifest.get("window_identity") for session in sessions]
        valid = [item for item in identities if isinstance(item, dict)]
        if not valid:
            raise RuntimeError("学习会话缺少持久窗口身份，请重新学习。")
        canonical = {
            "process_name": str(valid[0].get("process_name", "")),
            "process_path_hash": str(valid[0].get("process_path_hash", "")),
            "window_class": str(valid[0].get("window_class", "")),
            "title_prefix": str(valid[0].get("title_prefix", "")),
        }
        for identity in valid[1:]:
            for key in ("process_name", "process_path_hash", "window_class"):
                if str(identity.get(key, "")) != canonical[key]:
                    raise RuntimeError("学习会话来自不同进程路径或窗口类，拒绝混合训练。")
        return canonical

    def _extract_all_sessions(
        self, sessions: Sequence[LoadedSession]
    ) -> dict[str, list[FrameSample]]:
        result: dict[str, list[FrameSample]] = {}
        total_rows = sum(len(session.rows) for session in sessions)
        processed = 0
        for session in sessions:
            previous_gray: np.ndarray | None = None
            previous_epoch: int | None = None
            samples: list[FrameSample] = []
            for row in session.rows:
                if self.stop_event.is_set():
                    raise InterruptedError("复习已由 ESC 停止。")
                try:
                    epoch = int(row.get("focus_epoch", 0))
                    if previous_epoch is None or epoch != previous_epoch:
                        previous_gray = None
                    previous_epoch = epoch
                    frame = ensure_within(session.path, session.path / str(row["frame"]))
                    image = safe_imread(frame)
                    if image is None:
                        raise ValueError("图像读取失败")
                    visual, previous_gray = make_visual_feature(image, previous_gray)
                    dt = clamp(float(row.get("dt", 0.1)), 1e-4, 0.5)
                    sample = FrameSample(
                        visual=visual,
                        dt=dt,
                        x_norm=clamp(float(row.get("x_norm", 0.5)), 0.0, 1.0),
                        y_norm=clamp(float(row.get("y_norm", 0.5)), 0.0, 1.0),
                        vx=float(row.get("vx", 0.0)),
                        vy=float(row.get("vy", 0.0)),
                        buttons={name: bool(row.get(f"{name}_down", False)) for name in BUTTONS},
                        wheel_v_rate=float(row.get("wheel_v", 0)) / dt,
                        wheel_h_rate=float(row.get("wheel_h", 0)) / dt,
                        client_width=max(1, int(row.get("client_width", 1))),
                        client_height=max(1, int(row.get("client_height", 1))),
                        edges=tuple(str(value) for value in row.get("button_edges", [])),
                        focus_epoch=epoch,
                    )
                    samples.append(sample)
                except Exception:
                    self.invalid_samples += 1
                processed += 1
                if processed % 100 == 0 or processed == total_rows:
                    self.status(f"复习中：提取颜色、差分、边缘特征 {processed}/{total_rows}……")
                    self.progress(0.08 + 0.32 * processed / max(1, total_rows))
            result[session.path.name] = samples
        return result

    def _sample_training_only(self, samples: list[FrameSample]) -> list[FrameSample]:
        if len(samples) <= MAX_TRAIN_SAMPLES:
            return samples
        interesting: list[FrameSample] = []
        idle: list[FrameSample] = []
        for sample in samples:
            if sample.moving or sample.edges or sample.wheel_v_rate or sample.wheel_h_rate:
                interesting.append(sample)
            else:
                idle.append(sample)
        rng = random.Random(42)
        budget = max(0, MAX_TRAIN_SAMPLES - len(interesting))
        if len(interesting) > MAX_TRAIN_SAMPLES:
            edge_samples = [sample for sample in interesting if sample.edges]
            other = [sample for sample in interesting if not sample.edges]
            keep_other = max(0, MAX_TRAIN_SAMPLES - len(edge_samples))
            if len(other) > keep_other:
                other = rng.sample(other, keep_other)
            sampled = edge_samples[:MAX_TRAIN_SAMPLES] + other
        else:
            sampled_idle = rng.sample(idle, min(len(idle), budget))
            sampled = interesting + sampled_idle
        rng.shuffle(sampled)
        return sampled

    def _training_arrays(self, samples: Sequence[FrameSample]) -> tuple[np.ndarray, dict[str, Any]]:
        X = np.empty((len(samples), FEATURE_DIM), dtype=np.uint8)
        move_y = np.empty(len(samples), dtype=np.uint8)
        velocity = np.empty((len(samples), 2), dtype=np.float32)
        button_edges = {
            name: {
                "press": np.empty(len(samples), dtype=np.uint8),
                "release": np.empty(len(samples), dtype=np.uint8),
            }
            for name in BUTTONS
        }
        wheel_gate_v = np.empty(len(samples), dtype=np.uint8)
        wheel_gate_h = np.empty(len(samples), dtype=np.uint8)
        wheel_rate = np.empty((len(samples), 2), dtype=np.float32)
        for index, sample in enumerate(samples):
            X[index] = combine_feature(
                sample.visual,
                make_state_feature(sample.x_norm, sample.y_norm, sample.buttons, sample.dt),
            )
            move_y[index] = 1 if sample.moving else 0
            velocity[index] = (sample.vx, sample.vy)
            edge_set = set(sample.edges)
            for name in BUTTONS:
                button_edges[name]["press"][index] = 1 if f"{name}_down" in edge_set else 0
                button_edges[name]["release"][index] = 1 if f"{name}_up" in edge_set else 0
            wheel_gate_v[index] = 1 if abs(sample.wheel_v_rate) > 1e-6 else 0
            wheel_gate_h[index] = 1 if abs(sample.wheel_h_rate) > 1e-6 else 0
            wheel_rate[index] = (sample.wheel_v_rate, sample.wheel_h_rate)
        return X, {
            "move_y": move_y,
            "velocity": velocity,
            "button_edges": button_edges,
            "wheel_gate_v": wheel_gate_v,
            "wheel_gate_h": wheel_gate_h,
            "wheel_rate": wheel_rate,
        }

    def _binary_classifier(
        self, y: np.ndarray, tree_count: int, seed: int, max_depth: int
    ) -> Any:
        unique = np.unique(y)
        if unique.size < 2:
            model = DummyClassifier(strategy="constant", constant=int(unique[0]))
            return model
        return ExtraTreesClassifier(
            n_estimators=0,
            max_depth=max_depth,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced",
            random_state=seed,
            n_jobs=self.n_jobs,
            warm_start=True,
        )

    def _fit_estimator_cancellable(
        self, model: Any, X: np.ndarray, y: np.ndarray, total_trees: int
    ) -> Any:
        if isinstance(model, DummyClassifier):
            model.fit(X, y)
            return model
        step = 16
        for count in range(step, total_trees + step, step):
            if self.stop_event.is_set():
                raise InterruptedError("复习已由 ESC 停止。")
            model.set_params(n_estimators=min(count, total_trees))
            model.fit(X, y)
            if count >= total_trees:
                break
        return model

    def _fit_models(
        self,
        X: np.ndarray,
        targets: dict[str, Any],
        tree_count: int,
        max_depth: int = 22,
        reg_max_features: float = 0.35,
    ) -> dict[str, Any]:
        with threadpool_limits(limits=self.n_jobs):
            move_gate = self._binary_classifier(targets["move_y"], tree_count, 41, max_depth)
            self._fit_estimator_cancellable(move_gate, X, targets["move_y"], tree_count)
            button_models: dict[str, Any] = {}
            for offset, name in enumerate(BUTTONS):
                press_y = targets["button_edges"][name]["press"]
                release_y = targets["button_edges"][name]["release"]
                press_model = self._binary_classifier(press_y, tree_count, 50 + offset * 2, max_depth)
                release_model = self._binary_classifier(release_y, tree_count, 51 + offset * 2, max_depth)
                self._fit_estimator_cancellable(press_model, X, press_y, tree_count)
                self._fit_estimator_cancellable(release_model, X, release_y, tree_count)
                button_models[name] = {"press": press_model, "release": release_model}
            move_mask = targets["move_y"].astype(bool)
            movement_regressor: ExtraTreesRegressor | None = None
            if int(move_mask.sum()) >= 20:
                movement_regressor = ExtraTreesRegressor(
                    n_estimators=0,
                    max_depth=max_depth,
                    min_samples_leaf=2,
                    max_features=reg_max_features,
                    random_state=61,
                    n_jobs=self.n_jobs,
                    warm_start=True,
                )
                self._fit_estimator_cancellable(
                    movement_regressor, X[move_mask], targets["velocity"][move_mask], tree_count
                )
            v_gate = self._binary_classifier(targets["wheel_gate_v"], tree_count, 71, max_depth)
            h_gate = self._binary_classifier(targets["wheel_gate_h"], tree_count, 72, max_depth)
            self._fit_estimator_cancellable(v_gate, X, targets["wheel_gate_v"], tree_count)
            self._fit_estimator_cancellable(h_gate, X, targets["wheel_gate_h"], tree_count)
            wheel_mask = targets["wheel_gate_v"].astype(bool) | targets["wheel_gate_h"].astype(bool)
            wheel_regressor: ExtraTreesRegressor | None = None
            if int(wheel_mask.sum()) >= 20:
                wheel_regressor = ExtraTreesRegressor(
                    n_estimators=0,
                    max_depth=max(14, max_depth - 4),
                    min_samples_leaf=2,
                    max_features=reg_max_features,
                    random_state=73,
                    n_jobs=self.n_jobs,
                    warm_start=True,
                )
                wheel_trees = max(32, tree_count // 2)
                self._fit_estimator_cancellable(
                    wheel_regressor, X[wheel_mask], targets["wheel_rate"][wheel_mask], wheel_trees
                )
        return {
            "move_gate": move_gate,
            "movement_regressor": movement_regressor,
            "button_models": button_models,
            "wheel_models": {
                "v_gate": v_gate,
                "h_gate": h_gate,
                "regressor": wheel_regressor,
            },
        }

    def _select_and_train(
        self,
        X: np.ndarray,
        targets: dict[str, Any],
        validation_sessions: Sequence[Sequence[FrameSample]],
    ) -> tuple[dict[str, Any], PolicyConfig, dict[str, Any]]:
        training_candidates = (
            {"tree_count": 48, "max_depth": 18, "reg_max_features": 0.20},
            {"tree_count": 72, "max_depth": 22, "reg_max_features": 0.35},
            {"tree_count": 96, "max_depth": 22, "reg_max_features": 0.50},
        )
        configs = (
            PolicyConfig(move_threshold=0.64, press_threshold=0.78, release_threshold=0.74),
            PolicyConfig(move_threshold=0.72, press_threshold=0.84, release_threshold=0.80),
            PolicyConfig(move_threshold=0.80, press_threshold=0.88, release_threshold=0.84),
            PolicyConfig(move_threshold=0.86, press_threshold=0.92, release_threshold=0.88),
        )
        best_score = float("inf")
        best_training = dict(training_candidates[0])
        best_config = configs[0]
        best_metrics: dict[str, Any] = {}
        for index, training in enumerate(training_candidates):
            if self.stop_event.is_set():
                raise InterruptedError("复习已由 ESC 停止。")
            self.status(
                "复习中：候选模型 "
                f"树={training['tree_count']}，深度={training['max_depth']}，"
                f"回归特征比例={training['reg_max_features']:.2f}……"
            )
            models = self._fit_models(X, targets, **training)
            for config in configs:
                metrics = self._evaluate_policy(models, config, validation_sessions)
                score = float(metrics["selection_score"])
                if score < best_score:
                    best_score = score
                    best_training = dict(training)
                    best_config = config
                    best_metrics = metrics
            self.progress(0.45 + 0.35 * (index + 1) / len(training_candidates))
        return best_training, best_config, best_metrics

    def _evaluate_policy(
        self,
        models: dict[str, Any],
        config: PolicyConfig,
        validation_sessions: Sequence[Sequence[FrameSample]],
    ) -> dict[str, Any]:
        total_seconds = 0.0
        false_presses = 0
        false_releases = 0
        idle_drift_pixels = 0.0
        missed_presses = 0
        true_presses = 0
        drag_interruptions = 0
        stuck_buttons = 0
        total_planned_actions = 0
        per_session: list[dict[str, Any]] = []
        move_truth: list[int] = []
        move_pred: list[int] = []
        tolerance_seconds = 0.22

        def match_events(
            truth_times: list[float], predicted_times: list[float], tolerance: float
        ) -> tuple[set[int], set[int]]:
            matched_truth: set[int] = set()
            matched_predicted: set[int] = set()
            for pred_index, predicted_time in enumerate(predicted_times):
                best_index: int | None = None
                best_distance = tolerance + 1.0
                for truth_index, truth_time in enumerate(truth_times):
                    if truth_index in matched_truth:
                        continue
                    distance = abs(predicted_time - truth_time)
                    if distance <= tolerance and distance < best_distance:
                        best_distance = distance
                        best_index = truth_index
                if best_index is not None:
                    matched_truth.add(best_index)
                    matched_predicted.add(pred_index)
            return matched_truth, matched_predicted

        for session_index, samples in enumerate(validation_sessions):
            if not samples:
                continue
            policy = PolicyState(config, samples[0].x_norm, samples[0].y_norm)
            current_epoch = samples[0].focus_epoch
            session_seconds = 0.0
            session_actions = 0
            demonstration_actions = 0
            predicted_stuck_time = {name: 0.0 for name in BUTTONS}
            stuck_counted = {name: False for name in BUTTONS}
            truth_events = {f"{name}_{edge}": [] for name in BUTTONS for edge in ("down", "up")}
            planned_events = {f"{name}_{edge}": [] for name in BUTTONS for edge in ("down", "up")}
            release_context: dict[str, list[bool]] = {name: [] for name in BUTTONS}

            for sample in samples:
                if sample.focus_epoch != current_epoch:
                    current_epoch = sample.focus_epoch
                    policy = PolicyState(config, sample.x_norm, sample.y_norm)
                    predicted_stuck_time = {name: 0.0 for name in BUTTONS}
                    stuck_counted = {name: False for name in BUTTONS}
                state_feature = make_state_feature(
                    policy.x_norm, policy.y_norm, policy.buttons, sample.dt
                )
                feature = combine_feature(sample.visual, state_feature).reshape(1, -1)
                prediction = build_prediction(models, feature)
                plan = policy.step(prediction, sample.dt)
                gt_moving = sample.moving
                move_truth.append(1 if gt_moving else 0)
                move_pred.append(1 if prediction.move_probability >= config.move_threshold else 0)
                session_seconds += sample.dt
                total_seconds += sample.dt
                for edge in sample.edges:
                    if edge in truth_events:
                        truth_events[edge].append(session_seconds)
                if not gt_moving:
                    idle_drift_pixels += math.hypot(
                        plan.dx_norm * sample.client_width,
                        plan.dy_norm * sample.client_height,
                    )

                for event in plan.button_events:
                    if event in planned_events:
                        planned_events[event].append(session_seconds)
                        if event.endswith("_up"):
                            name = event.split("_", 1)[0]
                            release_context[name].append(bool(sample.buttons[name] and gt_moving))

                for name in BUTTONS:
                    gt_down = sample.buttons[name]
                    if policy.buttons[name] and not gt_down:
                        predicted_stuck_time[name] += sample.dt
                        if (
                            predicted_stuck_time[name] >= config.max_hold_seconds
                            and not stuck_counted[name]
                        ):
                            stuck_buttons += 1
                            stuck_counted[name] = True
                    else:
                        predicted_stuck_time[name] = 0.0
                        stuck_counted[name] = False

                demonstration_actions += len(sample.edges)
                if sample.moving:
                    demonstration_actions += 1
                if sample.wheel_v_rate or sample.wheel_h_rate:
                    demonstration_actions += 1
                action_increment = len(plan.button_events)
                if abs(plan.dx_norm) + abs(plan.dy_norm) > 1e-7:
                    action_increment += 1
                if plan.wheel_v or plan.wheel_h:
                    action_increment += 1
                session_actions += action_increment
                total_planned_actions += action_increment

            for name in BUTTONS:
                if policy.buttons[name]:
                    stuck_buttons += 1
                down_key = f"{name}_down"
                up_key = f"{name}_up"
                matched_truth_down, matched_pred_down = match_events(
                    truth_events[down_key], planned_events[down_key], tolerance_seconds
                )
                matched_truth_up, matched_pred_up = match_events(
                    truth_events[up_key], planned_events[up_key], tolerance_seconds
                )
                true_presses += len(truth_events[down_key])
                missed_presses += len(truth_events[down_key]) - len(matched_truth_down)
                false_presses += len(planned_events[down_key]) - len(matched_pred_down)
                unmatched_release_indices = set(range(len(planned_events[up_key]))) - matched_pred_up
                false_releases += len(unmatched_release_indices)
                contexts = release_context[name]
                drag_interruptions += sum(
                    1
                    for index in unmatched_release_indices
                    if index < len(contexts) and contexts[index]
                )

            per_session.append(
                {
                    "session_index": session_index,
                    "duration_seconds": round(session_seconds, 3),
                    "planned_actions": session_actions,
                    "policy_action_frequency_per_minute": round(
                        session_actions * 60.0 / max(session_seconds, 1e-6), 3
                    ),
                    "demonstration_action_frequency_per_minute": round(
                        demonstration_actions * 60.0 / max(session_seconds, 1e-6), 3
                    ),
                }
            )

        hours = total_seconds / 3600.0
        minutes = total_seconds / 60.0
        false_press_rate = false_presses / max(hours, 1e-9)
        false_release_rate = false_releases / max(hours, 1e-9)
        drift_rate = idle_drift_pixels / max(minutes, 1e-9)
        miss_rate = missed_presses / max(true_presses, 1)
        try:
            move_balanced_accuracy = float(balanced_accuracy_score(move_truth, move_pred))
        except Exception:
            move_balanced_accuracy = 0.0
        passed = (
            false_press_rate <= 5.0
            and false_release_rate <= 5.0
            and drift_rate <= 30.0
            and miss_rate <= 0.35
            and drag_interruptions <= max(2, len(validation_sessions))
            and stuck_buttons == 0
        )
        selection_score = (
            false_press_rate * 8.0
            + false_release_rate * 6.0
            + drift_rate * 0.4
            + miss_rate * 100.0
            + drag_interruptions * 20.0
            + stuck_buttons * 80.0
            + (1.0 - move_balanced_accuracy) * 30.0
        )
        return {
            "validated": True,
            "passed": passed,
            "validation_sessions": len(validation_sessions),
            "validation_seconds": round(total_seconds, 3),
            "event_match_tolerance_seconds": tolerance_seconds,
            "false_presses": false_presses,
            "false_releases": false_releases,
            "false_presses_per_hour": round(false_press_rate, 4),
            "false_releases_per_hour": round(false_release_rate, 4),
            "idle_drift_pixels_per_minute": round(drift_rate, 4),
            "click_miss_rate": round(miss_rate, 5),
            "drag_interruptions": drag_interruptions,
            "stuck_buttons": stuck_buttons,
            "move_balanced_accuracy": round(move_balanced_accuracy, 5),
            "planned_actions": total_planned_actions,
            "per_session": per_session,
            "selection_score": round(selection_score, 5),
        }

    def _minimum_requirements(
        self, session_samples: dict[str, Sequence[FrameSample]]
    ) -> dict[str, Any]:
        samples = [sample for values in session_samples.values() for sample in values]
        transitions = {name: {"down": 0, "up": 0} for name in BUTTONS}
        for values in session_samples.values():
            for sample in values:
                edge_set = set(sample.edges)
                for name in BUTTONS:
                    if f"{name}_down" in edge_set:
                        transitions[name]["down"] += 1
                    if f"{name}_up" in edge_set:
                        transitions[name]["up"] += 1
        used_button_failures: list[str] = []
        for name in BUTTONS:
            counts = transitions[name]
            if counts["down"] or counts["up"]:
                if counts["down"] < MIN_BUTTON_TRANSITIONS or counts["up"] < MIN_BUTTON_TRANSITIONS:
                    used_button_failures.append(
                        f"{BUTTON_CN[name]}按下/释放不足 {MIN_BUTTON_TRANSITIONS} 次"
                    )
        move_count = sum(1 for sample in samples if sample.moving)
        failures: list[str] = []
        if len(session_samples) < MIN_SESSIONS:
            failures.append(f"独立会话少于 {MIN_SESSIONS} 个")
        if move_count < MIN_MOVE_SAMPLES:
            failures.append(f"有效移动样本少于 {MIN_MOVE_SAMPLES} 条")
        failures.extend(used_button_failures)
        return {
            "passed": not failures,
            "failures": failures,
            "sessions": len(session_samples),
            "move_samples": move_count,
            "button_transitions": transitions,
        }

    @staticmethod
    def _reference_size(session_samples: dict[str, Sequence[FrameSample]]) -> list[int]:
        widths = [sample.client_width for values in session_samples.values() for sample in values]
        heights = [sample.client_height for values in session_samples.values() for sample in values]
        if not widths or not heights:
            return [1, 1]
        return [int(np.median(np.asarray(widths))), int(np.median(np.asarray(heights)))]

    @staticmethod
    def _weighted_fps(session_samples: dict[str, Sequence[FrameSample]]) -> float:
        total_frames = sum(len(values) for values in session_samples.values())
        total_seconds = sum(sample.dt for values in session_samples.values() for sample in values)
        return round(total_frames / max(total_seconds, 1e-9), 4)

    @staticmethod
    def _publish_model(data: dict[str, Any], model_dir: Path) -> None:
        model_dir.mkdir(parents=True, exist_ok=True)
        if model_dir.is_symlink() or path_is_reparse(model_dir):
            raise RuntimeError("模型目录不能是链接或 reparse point。")
        model_path = model_dir / MODEL_FILENAME
        hash_path = model_dir / MODEL_HASH_FILENAME
        new_model = model_dir / (MODEL_FILENAME + ".new")
        new_hash = model_dir / (MODEL_HASH_FILENAME + ".new")
        backup_model = model_dir / (MODEL_FILENAME + ".bak")
        backup_hash = model_dir / (MODEL_HASH_FILENAME + ".bak")
        for path in (new_model, new_hash, backup_model, backup_hash):
            path.unlink(missing_ok=True)
        joblib.dump(data, new_model, compress=3)
        new_hash.write_text(sha256_file(new_model) + "\n", encoding="ascii")
        try:
            if model_path.exists():
                os.replace(model_path, backup_model)
            if hash_path.exists():
                os.replace(hash_path, backup_hash)
            os.replace(new_model, model_path)
            os.replace(new_hash, hash_path)
        except Exception:
            model_path.unlink(missing_ok=True)
            hash_path.unlink(missing_ok=True)
            if backup_model.exists():
                os.replace(backup_model, model_path)
            if backup_hash.exists():
                os.replace(backup_hash, hash_path)
            raise
        else:
            backup_model.unlink(missing_ok=True)
            backup_hash.unlink(missing_ok=True)

    @staticmethod
    def _atomic_joblib_dump(data: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".tmp")
        joblib.dump(data, temp, compress=3)
        os.replace(temp, path)

    @staticmethod
    def _write_metrics_csv(path: Path, metrics: dict[str, Any]) -> None:
        rows = metrics.get("per_session", [])
        if not isinstance(rows, list) or not rows:
            return
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


class MouseExecutor:
    FLAG_MAP = {
        "left_down": MOUSEEVENTF_LEFTDOWN,
        "left_up": MOUSEEVENTF_LEFTUP,
        "right_down": MOUSEEVENTF_RIGHTDOWN,
        "right_up": MOUSEEVENTF_RIGHTUP,
        "middle_down": MOUSEEVENTF_MIDDLEDOWN,
        "middle_up": MOUSEEVENTF_MIDDLEUP,
    }

    def __init__(self) -> None:
        self.down = {name: False for name in BUTTONS}
        self.down_since_ns = {name: 0 for name in BUTTONS}
        self.last_click_ns = 0
        self.event_times: deque[int] = deque()
        self.consecutive_failures = 0

    def _reserve_events(self, count: int) -> None:
        now_ns = monotonic_ns()
        cutoff = now_ns - 1_000_000_000
        while self.event_times and self.event_times[0] < cutoff:
            self.event_times.popleft()
        if len(self.event_times) + count > MAX_INPUT_EVENTS_PER_SECOND:
            raise RuntimeError("输入事件速率超过安全上限，已触发熔断。")
        self.event_times.extend([now_ns] * count)

    def _send(self, flags: int, mouse_data: int = 0, dx: int = 0, dy: int = 0) -> None:
        self._reserve_events(1)
        item = INPUT(
            type=INPUT_MOUSE,
            mi=MOUSEINPUT(
                dx=int(dx),
                dy=int(dy),
                mouseData=int(mouse_data) & 0xFFFFFFFF,
                dwFlags=int(flags),
                time=0,
                dwExtraInfo=INPUT_MARKER,
            ),
        )
        sent = int(USER32.SendInput(1, ctypes.byref(item), ctypes.sizeof(INPUT)))
        if sent != 1:
            self.consecutive_failures += 1
            error = ctypes.get_last_error()
            if self.consecutive_failures >= 3:
                raise RuntimeError(f"SendInput 连续失败，错误码 {error}，已触发熔断。")
            raise ctypes.WinError(error) if error else RuntimeError("SendInput 未发送完整事件。")
        self.consecutive_failures = 0

    def move_to(self, x: int, y: int) -> None:
        left = USER32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        top = USER32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        width = max(1, USER32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
        height = max(1, USER32.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        absolute_x = round((int(x) - left) * 65535 / max(1, width - 1))
        absolute_y = round((int(y) - top) * 65535 / max(1, height - 1))
        self._send(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK,
            dx=int(clamp(absolute_x, 0, 65535)),
            dy=int(clamp(absolute_y, 0, 65535)),
        )

    def perform(self, action: str, min_click_interval: float = 0.055) -> bool:
        if action not in self.FLAG_MAP:
            return False
        name, edge = action.split("_", 1)
        desired_down = edge == "down"
        if self.down[name] == desired_down:
            return False
        now_ns = monotonic_ns()
        if now_ns - self.last_click_ns < int(min_click_interval * 1e9):
            return False
        self._send(self.FLAG_MAP[action])
        self.down[name] = desired_down
        self.down_since_ns[name] = now_ns if desired_down else 0
        self.last_click_ns = now_ns
        return True

    def scroll(self, vertical: int = 0, horizontal: int = 0) -> int:
        count = 0
        if vertical:
            data = ctypes.c_long(int(vertical) * 120).value
            self._send(MOUSEEVENTF_WHEEL, mouse_data=data)
            count += 1
        if horizontal:
            data = ctypes.c_long(int(horizontal) * 120).value
            self._send(MOUSEEVENTF_HWHEEL, mouse_data=data)
            count += 1
        return count

    def release_expired(self, max_hold_seconds: float = 1.6) -> list[str]:
        now_ns = monotonic_ns()
        released: list[str] = []
        for name in BUTTONS:
            if self.down[name] and now_ns - self.down_since_ns[name] >= int(max_hold_seconds * 1e9):
                if self.perform(f"{name}_up", min_click_interval=0.0):
                    released.append(f"{name}_up")
        return released

    def release_all(self) -> None:
        for name in BUTTONS:
            if self.down[name]:
                try:
                    self.perform(f"{name}_up", min_click_interval=0.0)
                except Exception:
                    pass
        self.down = {name: False for name in BUTTONS}


def _validate_model_structure(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RuntimeError("模型结构无效。")
    if int(data.get("model_version", -1)) != MODEL_VERSION:
        raise RuntimeError("模型版本不兼容，请重新复习。")
    if int(data.get("feature_dim", -1)) != FEATURE_DIM:
        raise RuntimeError("模型特征维数不兼容，请重新复习。")
    if data.get("publishable") is not True:
        raise RuntimeError("该模型是实验模型，未通过完整会话验证，禁止运行。")
    stored_sklearn = str(data.get("sklearn_version", ""))
    if stored_sklearn and stored_sklearn.split(".")[:2] != sklearn_version.split(".")[:2]:
        raise RuntimeError(
            f"模型使用 scikit-learn {stored_sklearn} 生成，当前为 {sklearn_version}，请重新复习。"
        )
    identity = data.get("window_identity")
    models = data.get("models")
    config = data.get("policy_config")
    if not isinstance(identity, dict) or not isinstance(models, dict) or not isinstance(config, dict):
        raise RuntimeError("模型缺少必要字段。")
    allowed_classifiers = (ExtraTreesClassifier, DummyClassifier)
    move_gate = models.get("move_gate")
    button_models = models.get("button_models")
    if not isinstance(move_gate, allowed_classifiers) or not isinstance(button_models, dict):
        raise RuntimeError("模型分类器类型无效。")
    for name in BUTTONS:
        pair = button_models.get(name)
        if not isinstance(pair, dict):
            raise RuntimeError(f"{BUTTON_CN[name]}模型结构无效。")
        if not isinstance(pair.get("press"), allowed_classifiers):
            raise RuntimeError(f"{BUTTON_CN[name]}按下模型类型无效。")
        if not isinstance(pair.get("release"), allowed_classifiers):
            raise RuntimeError(f"{BUTTON_CN[name]}释放模型类型无效。")
    regressor = models.get("movement_regressor")
    if regressor is not None and not isinstance(regressor, ExtraTreesRegressor):
        raise RuntimeError("移动回归器类型无效。")
    wheel_models = models.get("wheel_models")
    if not isinstance(wheel_models, dict):
        raise RuntimeError("滚轮模型结构无效。")
    for key in ("v_gate", "h_gate"):
        if not isinstance(wheel_models.get(key), allowed_classifiers):
            raise RuntimeError("滚轮门控模型类型无效。")
    wheel_regressor = wheel_models.get("regressor")
    if wheel_regressor is not None and not isinstance(wheel_regressor, ExtraTreesRegressor):
        raise RuntimeError("滚轮回归器类型无效。")
    edge_models = [pair[edge] for pair in button_models.values() for edge in ("press", "release")]
    for model in [move_gate, *edge_models, wheel_models["v_gate"], wheel_models["h_gate"]]:
        n_features = getattr(model, "n_features_in_", FEATURE_DIM)
        if int(n_features) != FEATURE_DIM:
            raise RuntimeError("分类器输入维数异常。")
    for model in (regressor, wheel_regressor):
        if model is not None and int(getattr(model, "n_features_in_", -1)) != FEATURE_DIM:
            raise RuntimeError("回归器输入维数异常。")
    return data


def load_published_model(output_root: Path) -> dict[str, Any]:
    model_dir = (output_root / "model").resolve(strict=False)
    if model_dir.is_symlink() or path_is_reparse(model_dir):
        raise RuntimeError("模型目录不能是链接或 reparse point。")
    model_path = ensure_within(model_dir, model_dir / MODEL_FILENAME)
    hash_path = ensure_within(model_dir, model_dir / MODEL_HASH_FILENAME)
    if model_path.name != MODEL_FILENAME or hash_path.name != MODEL_HASH_FILENAME:
        raise RuntimeError("模型文件名不符合固定约束。")
    if not model_path.exists() or not hash_path.exists():
        raise RuntimeError("没有找到已通过验证的模型。请先完成复习。")
    if (
        model_path.is_symlink()
        or hash_path.is_symlink()
        or path_is_reparse(model_path)
        or path_is_reparse(hash_path)
    ):
        raise RuntimeError("拒绝加载链接或 reparse point 模型/校验文件。")
    expected_hash = hash_path.read_text(encoding="ascii").strip().lower()
    actual_hash = sha256_file(model_path)
    if len(expected_hash) != 64 or expected_hash != actual_hash:
        raise RuntimeError("模型完整性校验失败。")
    # joblib is pickle-based. Loading is restricted to the fixed local game path after hash/path checks.
    return _validate_model_structure(joblib.load(model_path))


class AutoPlayer:
    def __init__(
        self,
        hwnd: int,
        output_root: Path,
        fps: int,
        stop_event: threading.Event,
        status: Callable[[str], None],
        progress: Callable[[float], None],
    ) -> None:
        self.hwnd = hwnd
        self.output_root = output_root
        self.fps = fps
        self.stop_event = stop_event
        self.status = status
        self.progress = progress
        self.esc = EscWatcher(stop_event)
        self.executor = MouseExecutor()

    def run(self) -> dict[str, Any]:
        model_data = load_published_model(self.output_root)
        expected_identity = model_data["window_identity"]
        guard = WindowGuard(self.hwnd, expected_identity)
        models = model_data["models"]
        config = PolicyConfig(**model_data["policy_config"])
        training_fps = float(model_data.get("training_fps", self.fps))
        reference_size = model_data.get("client_size_reference")

        runs_dir = safe_child_dir(self.output_root, "runs")
        run_name = f"run_{now_stamp()}"
        run_dir = safe_child_dir(runs_dir, run_name, create=False)
        run_dir.mkdir(exist_ok=False)
        log_path = run_dir / "actions.jsonl"
        self.esc.start()
        bring_window_to_front(self.hwnd)
        period_ns = int(1e9 / max(1, self.fps))
        next_tick_ns = monotonic_ns()
        previous_tick_ns: int | None = None
        previous_gray: np.ndarray | None = None
        focus_stable = 0
        frame_count = 0
        action_count = 0
        last_status_ns = 0
        policy = PolicyState(config)
        self.status(
            f"AI 运行中：速度按真实 dt 计算；请求 {self.fps} FPS，训练加权 FPS {training_fps:.2f}。"
        )

        try:
            with log_path.open("w", encoding="utf-8", buffering=1) as log_file:
                with mss.mss() as sct:
                    while not self.stop_event.is_set():
                        guard.verify()
                        rect = get_client_rect(self.hwnd)
                        if reference_size and isinstance(reference_size, (list, tuple)) and len(reference_size) == 2:
                            ref_w, ref_h = max(1, int(reference_size[0])), max(1, int(reference_size[1]))
                            size_ratio = max(rect.width / ref_w, ref_w / rect.width, rect.height / ref_h, ref_h / rect.height)
                            if size_ratio > 1.35:
                                raise RuntimeError("当前窗口尺寸与训练数据差异超过 35%，已停止。")

                        now_ns = monotonic_ns()
                        if not guard.is_foreground():
                            self.executor.release_all()
                            policy.reset_buttons()
                            previous_gray = None
                            previous_tick_ns = None
                            focus_stable = 0
                            if now_ns - last_status_ns >= 1_000_000_000:
                                self.status("AI 已暂停：目标窗口不在前台，所有按键已释放。")
                                last_status_ns = now_ns
                            time.sleep(0.08)
                            next_tick_ns = monotonic_ns()
                            continue

                        frame = capture_client(sct, rect)
                        visual, gray = make_visual_feature(frame, previous_gray)
                        previous_gray = gray
                        cursor_x, cursor_y = get_cursor_pos()
                        policy.x_norm, policy.y_norm = rect.normalize(cursor_x, cursor_y)
                        policy.buttons = dict(self.executor.down)
                        dt = (
                            clamp((now_ns - previous_tick_ns) / 1e9, 1e-4, 0.5)
                            if previous_tick_ns is not None
                            else 1.0 / max(1, self.fps)
                        )
                        previous_tick_ns = now_ns

                        if focus_stable < FOCUS_WARMUP_FRAMES:
                            focus_stable += 1
                            next_tick_ns += period_ns
                            sleep_ns = next_tick_ns - monotonic_ns()
                            if sleep_ns > 0:
                                time.sleep(sleep_ns / 1e9)
                            continue

                        feature = combine_feature(
                            visual,
                            make_state_feature(policy.x_norm, policy.y_norm, policy.buttons, dt),
                        ).reshape(1, -1)
                        prediction = build_prediction(models, feature)
                        plan = policy.step(prediction, dt)
                        performed: list[str] = []

                        if abs(plan.dx_norm) + abs(plan.dy_norm) > 1e-7:
                            target_x, target_y = rect.denormalize(policy.x_norm, policy.y_norm)
                            if not rect.contains(target_x, target_y):
                                raise RuntimeError("计划鼠标位置越出客户区，已触发熔断。")
                            guard.verify()
                            if not guard.is_foreground():
                                raise RuntimeError("执行前前台状态变化，已停止。")
                            self.executor.move_to(target_x, target_y)
                            performed.append("move")

                        for action in plan.button_events:
                            guard.verify()
                            if not guard.is_foreground():
                                raise RuntimeError("执行按键前前台状态变化，已停止。")
                            if self.executor.perform(action, config.click_refractory_seconds):
                                performed.append(action)
                            else:
                                name = action.split("_", 1)[0]
                                policy.buttons[name] = self.executor.down[name]
                                policy.fsms[name] = ButtonFSM(
                                    state="DOWN" if self.executor.down[name] else "UP",
                                    since_transition=0.0,
                                )
                        if plan.wheel_v or plan.wheel_h:
                            guard.verify()
                            if not guard.is_foreground():
                                raise RuntimeError("执行滚轮前前台状态变化，已停止。")
                            self.executor.scroll(plan.wheel_v, plan.wheel_h)
                            performed.append(f"wheel({plan.wheel_v},{plan.wheel_h})")
                        performed.extend(self.executor.release_expired(config.max_hold_seconds))
                        action_count += len(performed)

                        log_file.write(
                            json.dumps(
                                {
                                    "timestamp_ns": now_ns,
                                    "frame_index": frame_count,
                                    "dt": round(dt, 9),
                                    "move_probability": round(prediction.move_probability, 6),
                                    "predicted_velocity": [round(prediction.vx, 6), round(prediction.vy, 6)],
                                    "button_press_probabilities": {
                                        key: round(value, 6)
                                        for key, value in prediction.button_press_probabilities.items()
                                    },
                                    "button_release_probabilities": {
                                        key: round(value, 6)
                                        for key, value in prediction.button_release_probabilities.items()
                                    },
                                    "performed": performed,
                                    "cursor_norm": [round(policy.x_norm, 7), round(policy.y_norm, 7)],
                                },
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                        frame_count += 1

                        if now_ns - last_status_ns >= 1_000_000_000:
                            self.status(
                                f"AI 运行中：移动概率 {prediction.move_probability:.0%}，"
                                f"已执行 {action_count} 个输入事件；ESC 结束。"
                            )
                            self.progress((frame_count % 100) / 100.0)
                            last_status_ns = now_ns

                        next_tick_ns += period_ns
                        sleep_ns = next_tick_ns - monotonic_ns()
                        if sleep_ns > 0:
                            time.sleep(sleep_ns / 1e9)
                        else:
                            next_tick_ns = monotonic_ns()
        finally:
            self.executor.release_all()
            self.esc.stop()
            atomic_json_dump(
                run_dir / "summary.json",
                {
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "frames": frame_count,
                    "performed_actions": action_count,
                    "requested_fps": self.fps,
                    "training_weighted_fps": training_fps,
                    "stopped_by_user": self.stop_event.is_set(),
                },
            )
        return {"run_dir": str(run_dir), "frames": frame_count, "actions": action_count}


class GameAIApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1080x790")
        self.root.minsize(920, 700)
        self.root.configure(bg=PALETTE["black"])
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.windows: list[WindowInfo] = []
        self.window_by_display: dict[str, WindowInfo] = {}
        self.registry: GameRegistry | None = None
        self.games: list[dict[str, str]] = []
        self.game_by_display: dict[str, dict[str, str]] = {}
        self.locked_root: Path | None = None
        self.active_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.mode: str | None = None
        self.ui_queue: queue.Queue[tuple[Any, ...]] = queue.Queue()

        self.window_var = tk.StringVar()
        self.folder_var = tk.StringVar()
        self.game_var = tk.StringVar()
        self.fps_var = tk.IntVar(value=12)
        self.status_var = tk.StringVar(value="请选择数据文件夹、游戏名称和目标窗口。")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._configure_style()
        self._build_ui()
        self.refresh_windows()
        self.root.after(40, self._poll_ui_queue)
        self._log(f"{APP_NAME} v{APP_VERSION}")
        self._log("模型发布必须经过完整会话验证；ESC 为全局安全停止键。")

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Game.TCombobox",
            fieldbackground=PALETTE["white"],
            background=PALETTE["light_gray"],
            foreground=PALETTE["black"],
            padding=7,
        )
        style.configure(
            "Game.Horizontal.TProgressbar",
            troughcolor="#303030",
            background=PALETTE["yellow"],
            bordercolor="#303030",
            lightcolor=PALETTE["yellow"],
            darkcolor=PALETTE["orange"],
        )

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, bg=PALETTE["black"])
        top.pack(fill="x")
        for name in (
            "red",
            "orange",
            "yellow",
            "green",
            "cyan",
            "blue",
            "purple",
            "black",
            "white",
            "gray",
        ):
            tk.Frame(top, bg=PALETTE[name], height=10).pack(side="left", fill="x", expand=True)

        header = tk.Frame(self.root, bg=PALETTE["black"], padx=22, pady=14)
        header.pack(fill="x")
        tk.Label(
            header,
            text=APP_NAME,
            bg=PALETTE["black"],
            fg=PALETTE["white"],
            font=("Microsoft YaHei UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Windows 11 · 会话级验证 · SendInput · 颜色特征 · 时间归一化",
            bg=PALETTE["black"],
            fg=PALETTE["light_gray"],
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        setup = tk.Frame(
            self.root,
            bg="#262626",
            padx=18,
            pady=14,
            highlightthickness=1,
            highlightbackground=PALETTE["gray"],
        )
        setup.pack(fill="x", padx=22, pady=(0, 12))

        tk.Label(setup, text="数据文件夹", bg="#262626", fg=PALETTE["yellow"], font=("Microsoft YaHei UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.folder_entry = tk.Entry(
            setup,
            textvariable=self.folder_var,
            state="readonly",
            readonlybackground=PALETTE["white"],
            fg=PALETTE["black"],
            relief="flat",
            font=("Microsoft YaHei UI", 10),
        )
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5, ipady=7)
        self.folder_button = self._make_button(setup, "选择文件夹", PALETTE["blue"], self.choose_folder, 12)
        self.folder_button.grid(row=0, column=2, pady=5)

        tk.Label(setup, text="游戏名称", bg="#262626", fg=PALETTE["yellow"], font=("Microsoft YaHei UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.game_combo = ttk.Combobox(setup, textvariable=self.game_var, state="readonly", style="Game.TCombobox")
        self.game_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        game_buttons = tk.Frame(setup, bg="#262626")
        game_buttons.grid(row=1, column=2, sticky="e")
        self.new_game_button = self._make_button(game_buttons, "新建", PALETTE["green"], self.create_game, 6)
        self.edit_game_button = self._make_button(game_buttons, "编辑", PALETTE["orange"], self.rename_game, 6)
        self.delete_game_button = self._make_button(game_buttons, "删除", PALETTE["red"], self.delete_game, 6)
        self.new_game_button.pack(side="left", padx=2)
        self.edit_game_button.pack(side="left", padx=2)
        self.delete_game_button.pack(side="left", padx=2)

        tk.Label(setup, text="目标窗口", bg="#262626", fg=PALETTE["yellow"], font=("Microsoft YaHei UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.window_combo = ttk.Combobox(setup, textvariable=self.window_var, state="readonly", style="Game.TCombobox")
        self.window_combo.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.refresh_button = self._make_button(setup, "刷新窗口", PALETTE["cyan"], self.refresh_windows, 12)
        self.refresh_button.grid(row=2, column=2, pady=5)

        options = tk.Frame(setup, bg="#262626")
        options.grid(row=3, column=1, sticky="w", padx=10, pady=(8, 0))
        tk.Label(options, text="运行 FPS", bg="#262626", fg=PALETTE["white"], font=("Microsoft YaHei UI", 9)).pack(side="left")
        self.fps_spin = tk.Spinbox(
            options,
            from_=4,
            to=30,
            textvariable=self.fps_var,
            width=5,
            bg=PALETTE["white"],
            relief="flat",
        )
        self.fps_spin.pack(side="left", padx=(6, 18), ipady=3)
        tk.Label(
            options,
            text="位移按真实 dt 计算；点击阈值由完整验证会话自动校准",
            bg="#262626",
            fg=PALETTE["light_gray"],
            font=("Microsoft YaHei UI", 9),
        ).pack(side="left")
        setup.columnconfigure(1, weight=1)

        controls = tk.Frame(self.root, bg=PALETTE["black"], padx=22, pady=5)
        controls.pack(fill="x")
        self.learn_button = self._make_button(controls, "① 学习", PALETTE["green"], self.start_learning, 16, 2)
        self.review_button = self._make_button(controls, "② 复习 / 验证", PALETTE["orange"], self.start_review, 18, 2)
        self.train_button = self._make_button(controls, "③ AI运行", PALETTE["red"], self.start_training, 16, 2)
        self.stop_button = self._make_button(controls, "ESC / 停止", PALETTE["purple"], self.request_stop, 16, 2)
        for button in (self.learn_button, self.review_button, self.train_button, self.stop_button):
            button.pack(side="left", expand=True, padx=5)
        self.stop_button.configure(state="disabled")
        self.train_button.configure(state="disabled")

        status_frame = tk.Frame(
            self.root,
            bg="#262626",
            padx=18,
            pady=12,
            highlightthickness=1,
            highlightbackground=PALETTE["gray"],
        )
        status_frame.pack(fill="x", padx=22, pady=12)
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg="#262626",
            fg=PALETTE["yellow"],
            anchor="w",
            font=("Microsoft YaHei UI", 10, "bold"),
            wraplength=980,
        ).pack(fill="x")
        ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=1.0,
            style="Game.Horizontal.TProgressbar",
        ).pack(fill="x", pady=(10, 0))

        notes = tk.Frame(self.root, bg=PALETTE["white"], padx=16, pady=11)
        notes.pack(fill="x", padx=22, pady=(0, 12))
        note_text = (
            "安全约束：仅当前前台窗口、同一 HWND/PID/进程创建时间、相同进程路径与窗口类允许执行；"
            "标题动态变化不会单独终止。\n"
            "模型文件采用 SHA-256 完整性校验，不是可信签名；不要复制或加载来源不明的 joblib 文件。"
        )
        tk.Label(
            notes,
            text=note_text,
            bg=PALETTE["white"],
            fg=PALETTE["black"],
            justify="left",
            anchor="w",
            font=("Microsoft YaHei UI", 9),
            wraplength=980,
        ).pack(fill="x")

        log_frame = tk.Frame(self.root, bg=PALETTE["gray"], padx=1, pady=1)
        log_frame.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        self.log_text = tk.Text(
            log_frame,
            bg="#111111",
            fg=PALETTE["light_gray"],
            insertbackground=PALETTE["white"],
            relief="flat",
            font=("Consolas", 9),
            wrap="word",
            state="disabled",
            height=10,
        )
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    @staticmethod
    def _make_button(
        parent: tk.Widget,
        text: str,
        color: str,
        command: Callable[[], None],
        width: int,
        height: int = 1,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=PALETTE["white"] if color not in (PALETTE["yellow"], PALETTE["white"]) else PALETTE["black"],
            activebackground=color,
            activeforeground=PALETTE["white"],
            relief="flat",
            cursor="hand2",
            font=("Microsoft YaHei UI", 10, "bold"),
            width=width,
            height=height,
            padx=8,
            pady=5,
        )

    def choose_folder(self) -> None:
        if self.locked_root is not None:
            messagebox.showinfo("需要重启", "本次运行已锁定数据根目录。要切换文件夹，请重启程序。")
            return
        selected = filedialog.askdirectory(title="选择 AI 数据根目录")
        if not selected:
            return
        try:
            root = Path(selected).expanduser().resolve()
            root.mkdir(parents=True, exist_ok=True)
            test = root / ".game_ai_write_test"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
            self.registry = GameRegistry(root)
            self.games = self.registry.load()
            self.folder_var.set(str(root))
            self._refresh_games()
            self._log(f"数据根目录：{root}")
        except Exception as exc:
            self._show_error("选择文件夹失败", exc)

    def _refresh_games(self, select_id: str | None = None) -> None:
        self.game_by_display = {
            f"{item['name']}  [{item['id'][:8]}]": item for item in self.games
        }
        values = list(self.game_by_display)
        self.game_combo["values"] = values
        selected_display = ""
        if select_id:
            for display, item in self.game_by_display.items():
                if item["id"] == select_id:
                    selected_display = display
                    break
        if not selected_display and self.game_var.get() in self.game_by_display:
            selected_display = self.game_var.get()
        if not selected_display and values:
            selected_display = values[0]
        self.game_var.set(selected_display)
        self._refresh_train_state()

    def create_game(self) -> None:
        if self.registry is None:
            messagebox.showwarning("请选择文件夹", "请先选择数据文件夹。")
            return
        name = simpledialog.askstring("新建游戏", "游戏名称：", parent=self.root)
        if name is None:
            return
        try:
            item = self.registry.create(self.games, name)
            self._refresh_games(item["id"])
            self._log(f"已新建游戏：{item['name']}")
        except Exception as exc:
            self._show_error("新建游戏失败", exc)

    def rename_game(self) -> None:
        item = self.game_by_display.get(self.game_var.get())
        if self.registry is None or item is None:
            messagebox.showwarning("请选择游戏", "请先选择游戏。")
            return
        name = simpledialog.askstring("编辑游戏", "游戏名称：", initialvalue=item["name"], parent=self.root)
        if name is None:
            return
        try:
            self.registry.rename(self.games, item["id"], name)
            self._refresh_games(item["id"])
            self._log(f"已修改游戏名称：{name.strip()}")
        except Exception as exc:
            self._show_error("编辑游戏失败", exc)

    def delete_game(self) -> None:
        item = self.game_by_display.get(self.game_var.get())
        if self.registry is None or item is None:
            messagebox.showwarning("请选择游戏", "请先选择游戏。")
            return
        if not messagebox.askyesno(
            "确认删除",
            f"将删除游戏“{item['name']}”及其全部学习数据、模型和日志。\n此操作不可撤销。",
        ):
            return
        try:
            self.registry.delete(self.games, item["id"])
            self._refresh_games()
            self._log(f"已删除游戏：{item['name']}")
        except Exception as exc:
            self._show_error("删除游戏失败", exc)

    def refresh_windows(self) -> None:
        try:
            self.windows = enumerate_windows()
            self.window_by_display = {item.display: item for item in self.windows}
            values = list(self.window_by_display)
            self.window_combo["values"] = values
            current = self.window_var.get()
            if current not in self.window_by_display:
                self.window_var.set(values[0] if values else "")
            self._log(f"已发现 {len(values)} 个可选窗口。")
        except Exception as exc:
            self._show_error("刷新窗口失败", exc)

    def _selected_game_root(self) -> Path | None:
        if self.registry is None:
            messagebox.showwarning("请选择文件夹", "请先选择数据文件夹。")
            return None
        item = self.game_by_display.get(self.game_var.get())
        if item is None:
            messagebox.showwarning("请选择游戏", "请先新建或选择游戏名称。")
            return None
        try:
            return self.registry.game_dir(item["id"], create=True)
        except Exception as exc:
            self._show_error("游戏目录无效", exc)
            return None

    def _validate_context(self, needs_model: bool) -> tuple[int, Path] | None:
        selected = self.window_by_display.get(self.window_var.get())
        if selected is None or not USER32.IsWindow(selected.hwnd):
            messagebox.showwarning("请选择窗口", "请先选择一个仍在运行的目标窗口。")
            return None
        root = self._selected_game_root()
        if root is None:
            return None
        if needs_model:
            try:
                load_published_model(root)
            except Exception as exc:
                messagebox.showwarning("模型不可运行", str(exc))
                return None
        return selected.hwnd, root

    def _validated_fps(self) -> int:
        try:
            return int(clamp(int(self.fps_var.get()), 4, 30))
        except Exception:
            return 12

    def start_learning(self) -> None:
        context = self._validate_context(needs_model=False)
        if context is None:
            return
        hwnd, game_root = context
        self._start_worker(
            "学习",
            lambda: LearningRecorder(
                hwnd,
                game_root,
                self._validated_fps(),
                self.stop_event,
                self._queue_status,
                self._queue_progress,
            ).run(),
        )

    def start_review(self) -> None:
        game_root = self._selected_game_root()
        if game_root is None:
            return
        self._start_worker(
            "复习",
            lambda: DatasetReviewer(
                game_root,
                self.stop_event,
                self._queue_status,
                self._queue_progress,
            ).run(),
        )

    def start_training(self) -> None:
        context = self._validate_context(needs_model=True)
        if context is None:
            return
        hwnd, game_root = context
        self._start_worker(
            "AI运行",
            lambda: AutoPlayer(
                hwnd,
                game_root,
                self._validated_fps(),
                self.stop_event,
                self._queue_status,
                self._queue_progress,
            ).run(),
        )

    def _start_worker(self, mode: str, target: Callable[[], dict[str, Any]]) -> None:
        if self.active_thread and self.active_thread.is_alive():
            messagebox.showinfo("任务正在运行", "请先按 ESC 或点击停止。")
            return
        if self.locked_root is None and self.folder_var.get():
            self.locked_root = Path(self.folder_var.get()).resolve()
            self.folder_button.configure(state="disabled")
            self._log("数据根目录已锁定；切换目录需要重启程序。")
        self.mode = mode
        self.stop_event = threading.Event()
        self._set_busy(True)
        self.progress_var.set(0.0)
        self.status_var.set(f"正在启动{mode}……")
        self._log(f"开始：{mode}")

        def worker() -> None:
            try:
                result = target()
                self.ui_queue.put(("finish_success", mode, result))
            except InterruptedError as exc:
                self.ui_queue.put(("finish_stopped", mode, str(exc)))
            except Exception as exc:
                self.ui_queue.put(("finish_error", mode, exc, traceback.format_exc()))

        self.active_thread = threading.Thread(target=worker, name=f"GameAI-{mode}", daemon=True)
        self.active_thread.start()

    def _queue_status(self, text: str) -> None:
        self.ui_queue.put(("status", text))

    def _queue_progress(self, value: float) -> None:
        self.ui_queue.put(("progress", clamp(float(value), 0.0, 1.0)))

    def _poll_ui_queue(self) -> None:
        try:
            while True:
                item = self.ui_queue.get_nowait()
                kind = item[0]
                if kind == "status":
                    self.status_var.set(str(item[1]))
                elif kind == "progress":
                    self.progress_var.set(float(item[1]))
                elif kind == "log":
                    self._log(str(item[1]))
                elif kind == "finish_success":
                    self._finish_success(str(item[1]), item[2])
                elif kind == "finish_stopped":
                    self._finish_stopped(str(item[1]), str(item[2]))
                elif kind == "finish_error":
                    self._finish_error(str(item[1]), item[2], str(item[3]))
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(40, self._poll_ui_queue)

    def request_stop(self) -> None:
        if self.active_thread and self.active_thread.is_alive():
            self.stop_event.set()
            self.status_var.set("正在安全停止并释放鼠标按键……")
            self._log("收到停止请求。")

    def _finish_success(self, mode: str, result: dict[str, Any]) -> None:
        self._set_busy(False)
        self.progress_var.set(1.0)
        if mode == "学习":
            text = f"学习结束：{result.get('frames', 0)} 帧，{result.get('samples', 0)} 条连续样本。"
        elif mode == "复习":
            metrics = result.get("metrics", {})
            if result.get("publishable"):
                text = (
                    "复习完成并发布模型："
                    f"错误按下 {metrics.get('false_presses_per_hour', 0):.2f}/小时，"
                    f"空闲漂移 {metrics.get('idle_drift_pixels_per_minute', 0):.2f} 像素/分钟。"
                )
            else:
                text = "复习完成，但验证或最低数据门槛未通过；旧模型已保留，实验模型不可运行。"
        else:
            text = f"AI运行结束：处理 {result.get('frames', 0)} 帧，执行 {result.get('actions', 0)} 个输入事件。"
        self.status_var.set(text)
        self._log(text)
        for key in (
            "session_dir",
            "model_path",
            "experimental_path",
            "report_path",
            "run_dir",
        ):
            if result.get(key):
                self._log(f"{key}: {result[key]}")
        self.mode = None
        self._refresh_train_state()

    def _finish_stopped(self, mode: str, message: str) -> None:
        self._set_busy(False)
        text = message or f"{mode}已停止。"
        self.status_var.set(text)
        self._log(text)
        self.mode = None
        self._refresh_train_state()

    def _finish_error(self, mode: str, exc: Exception, details: str) -> None:
        self._set_busy(False)
        self.status_var.set(f"{mode}失败：{exc}")
        self._log(f"错误：{exc}\n{details}")
        messagebox.showerror(f"{mode}失败", str(exc))
        self.mode = None
        self._refresh_train_state()

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        for widget in (
            self.learn_button,
            self.review_button,
            self.refresh_button,
            self.new_game_button,
            self.edit_game_button,
            self.delete_game_button,
            self.fps_spin,
        ):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
        if self.locked_root is None:
            self.folder_button.configure(state=state)
        else:
            self.folder_button.configure(state="disabled")
        self.window_combo.configure(state="disabled" if busy else "readonly")
        self.game_combo.configure(state="disabled" if busy else "readonly")
        self.stop_button.configure(state="normal" if busy else "disabled")
        if busy:
            self.train_button.configure(state="disabled")
        else:
            self._refresh_train_state()

    def _refresh_train_state(self) -> None:
        if self.active_thread and self.active_thread.is_alive():
            self.train_button.configure(state="disabled")
            return
        item = self.game_by_display.get(self.game_var.get())
        if self.registry is None or item is None:
            self.train_button.configure(state="disabled")
            return
        try:
            root = self.registry.game_dir(item["id"], create=False)
            model_exists = (root / "model" / MODEL_FILENAME).exists() and (
                root / "model" / MODEL_HASH_FILENAME
            ).exists()
        except Exception:
            model_exists = False
        self.train_button.configure(state="normal" if model_exists else "disabled")

    def _log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {text}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _show_error(self, title: str, exc: Exception) -> None:
        self._log(f"{title}: {exc}")
        messagebox.showerror(title, str(exc))

    def _on_close(self) -> None:
        if self.active_thread and self.active_thread.is_alive():
            self.request_stop()
            self.root.after(200, self._wait_then_close)
        else:
            self.root.destroy()

    def _wait_then_close(self) -> None:
        if self.active_thread and self.active_thread.is_alive():
            self.root.after(200, self._wait_then_close)
        else:
            self.root.destroy()


def main() -> None:
    set_dpi_awareness()
    root = tk.Tk()
    GameAIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
