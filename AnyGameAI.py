from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import random
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
from ctypes import wintypes
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


APP_NAME = "AnyGameAI"
SCRIPT_NAME = "AnyGameAI.py"
MODEL_SCHEMA = 1
CONFIG_SCHEMA = 1
EXPERIENCE_LIMIT = 50000
CAPTURE_WIDTH = 128
CAPTURE_HEIGHT = 72

DEFAULT_CONFIG = {
    "schema": CONFIG_SCHEMA,
    "action_hold_seconds": 0.09,
    "step_pause_seconds": 0.035,
    "epsilon": 0.18,
    "learning_rate": 0.20,
    "discount": 0.92,
    "experience_limit": EXPERIENCE_LIMIT,
    "update_manifest_url": "",
    "actions": [
        [],
        ["left"],
        ["right"],
        ["up"],
        ["down"],
        ["w"],
        ["a"],
        ["s"],
        ["d"],
        ["space"],
        ["z"],
        ["x"],
        ["left", "space"],
        ["right", "space"],
        ["a", "space"],
        ["d", "space"]
    ]
}

DEFAULT_MODEL = {
    "schema": MODEL_SCHEMA,
    "version": 1,
    "training_rounds": 0,
    "steps": 0,
    "q": {},
    "updated_at": ""
}

VK = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "escape": 0x1B,
    "space": 0x20,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "a": 0x41,
    "d": 0x44,
    "s": 0x53,
    "w": 0x57,
    "x": 0x58,
    "z": 0x5A
}


def desktop_dir() -> Path:
    if os.name == "nt":
        try:
            buffer = ctypes.create_unicode_buffer(32768)
            result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buffer)
            if result == 0 and buffer.value:
                return Path(buffer.value)
        except Exception:
            pass
    return Path.home() / "Desktop"

APP_DIR = desktop_dir() / APP_NAME
CONFIG_PATH = APP_DIR / "config.json"
MODEL_PATH = APP_DIR / "model.json"
EXPERIENCE_PATH = APP_DIR / "experience.jsonl"
LOG_PATH = APP_DIR / "AnyGameAI.log"
LOCAL_SCRIPT_PATH = APP_DIR / SCRIPT_NAME


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def save_json(path: Path, data: dict) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, separators=(",", ":")))


def backup_corrupt(path: Path) -> None:
    if not path.exists():
        return
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(path.name + ".corrupt." + suffix)
    try:
        os.replace(path, backup)
    except OSError:
        shutil.copy2(path, backup)


def log_error(text: str) -> None:
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(f"[{now_text()}] {text}\n")
    except Exception:
        pass


def validate_config(data: object) -> bool:
    if not isinstance(data, dict) or data.get("schema") != CONFIG_SCHEMA:
        return False
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        return False
    for action in actions:
        if not isinstance(action, list) or any(key not in VK for key in action):
            return False
    numeric_keys = (
        "action_hold_seconds",
        "step_pause_seconds",
        "epsilon",
        "learning_rate",
        "discount",
        "experience_limit",
    )
    return all(isinstance(data.get(key), (int, float)) for key in numeric_keys)


def validate_model(data: object) -> bool:
    if not isinstance(data, dict) or data.get("schema") != MODEL_SCHEMA:
        return False
    if not isinstance(data.get("q"), dict):
        return False
    if not isinstance(data.get("steps"), int):
        return False
    return True


def load_config() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if validate_config(data):
            return data
    except Exception:
        pass
    backup_corrupt(CONFIG_PATH)
    save_json(CONFIG_PATH, DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def load_model() -> dict:
    try:
        data = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
        if validate_model(data):
            return data
    except Exception:
        pass
    backup_corrupt(MODEL_PATH)
    model = json.loads(json.dumps(DEFAULT_MODEL))
    model["updated_at"] = now_text()
    save_json(MODEL_PATH, model)
    return model


def sanitize_experience(limit: int) -> tuple[int, int]:
    if not EXPERIENCE_PATH.exists():
        EXPERIENCE_PATH.touch()
        return 0, 0
    valid = []
    invalid = 0
    try:
        with EXPERIENCE_PATH.open("r", encoding="utf-8", errors="replace") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    required = {"s", "a", "r", "n"}
                    if (
                        isinstance(item, dict)
                        and required.issubset(item)
                        and isinstance(item["s"], str)
                        and isinstance(item["a"], int)
                        and isinstance(item["r"], (int, float))
                        and isinstance(item["n"], str)
                    ):
                        valid.append(item)
                    else:
                        invalid += 1
                except Exception:
                    invalid += 1
    except Exception:
        backup_corrupt(EXPERIENCE_PATH)
        EXPERIENCE_PATH.touch()
        return 0, 1
    if len(valid) > limit:
        valid = valid[-limit:]
    text = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in valid)
    atomic_write_text(EXPERIENCE_PATH, text)
    return len(valid), invalid


def bootstrap_to_desktop() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve()
    target = LOCAL_SCRIPT_PATH.resolve()
    try:
        same = source == target
    except Exception:
        same = False
    if same:
        return
    replace = not target.exists()
    if target.exists():
        try:
            replace = sha256_file(source) != sha256_file(target)
        except Exception:
            replace = True
    if replace:
        shutil.copy2(source, target)
    subprocess.Popen(
        [sys.executable, str(target)],
        cwd=str(APP_DIR),
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    raise SystemExit


def hide_console() -> None:
    if os.name != "nt":
        return
    try:
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def download_updates(config: dict, stop_event: threading.Event | None = None) -> int:
    manifest_url = str(config.get("update_manifest_url", "")).strip()
    if not manifest_url:
        return 0
    if stop_event is not None and stop_event.is_set():
        return 0
    with urllib.request.urlopen(manifest_url, timeout=15) as response:
        manifest = json.loads(response.read().decode("utf-8"))
    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise ValueError("远程清单格式错误")
    changed = 0
    for item in files:
        if stop_event is not None and stop_event.is_set():
            break
        relative = Path(str(item["path"]))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("远程清单包含非法路径")
        expected = str(item["sha256"]).lower()
        url = str(item["url"])
        target = APP_DIR / relative
        healthy = target.exists() and sha256_file(target).lower() == expected
        if healthy:
            continue
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read()
        if stop_event is not None and stop_event.is_set():
            break
        if hashlib.sha256(content).hexdigest().lower() != expected:
            raise ValueError(f"{relative} 下载校验失败")
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(target.suffix + ".download")
        temp.write_bytes(content)
        os.replace(temp, target)
        changed += 1
    return changed


def ensure_files(stop_event: threading.Event | None = None, check_remote: bool = True) -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    result = {"repaired": 0, "removed_records": 0, "records": 0, "downloaded": 0}
    current = Path(__file__).resolve()
    try:
        if not LOCAL_SCRIPT_PATH.exists() or sha256_file(current) != sha256_file(LOCAL_SCRIPT_PATH):
            shutil.copy2(current, LOCAL_SCRIPT_PATH)
            result["repaired"] += 1
    except Exception:
        pass

    try:
        config_data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not validate_config(config_data):
            raise ValueError
    except Exception:
        backup_corrupt(CONFIG_PATH)
        save_json(CONFIG_PATH, DEFAULT_CONFIG)
        result["repaired"] += 1

    try:
        model_data = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
        if not validate_model(model_data):
            raise ValueError
    except Exception:
        backup_corrupt(MODEL_PATH)
        model = json.loads(json.dumps(DEFAULT_MODEL))
        model["updated_at"] = now_text()
        save_json(MODEL_PATH, model)
        result["repaired"] += 1

    config = load_config()
    records, invalid = sanitize_experience(int(config.get("experience_limit", EXPERIENCE_LIMIT)))
    result["records"] = records
    result["removed_records"] = invalid
    if invalid:
        result["repaired"] += 1

    try:
        if check_remote and not (stop_event is not None and stop_event.is_set()):
            result["downloaded"] = download_updates(config, stop_event)
    except Exception as exc:
        log_error("更新下载失败: " + repr(exc))
        result["download_error"] = str(exc)
    return result


if os.name == "nt":
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32

    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    user32.GetForegroundWindow.argtypes = []
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetShellWindow.argtypes = []
    user32.GetShellWindow.restype = wintypes.HWND
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    kernel32.GetConsoleWindow.argtypes = []
    kernel32.GetConsoleWindow.restype = wintypes.HWND
    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype = ctypes.c_short
    user32.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, wintypes.DWORD, ctypes.c_void_p]
    user32.keybd_event.restype = None
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.CreateCompatibleBitmap.restype = wintypes.HANDLE
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HANDLE]
    gdi32.SelectObject.restype = wintypes.HANDLE
    gdi32.DeleteObject.argtypes = [wintypes.HANDLE]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL
    gdi32.StretchBlt.argtypes = [
        wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.DWORD,
    ]
    gdi32.StretchBlt.restype = wintypes.BOOL
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass

    SRCCOPY = 0x00CC0020
    DIB_RGB_COLORS = 0
    KEYEVENTF_KEYUP = 0x0002

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wintypes.DWORD),
            ("biWidth", wintypes.LONG),
            ("biHeight", wintypes.LONG),
            ("biPlanes", wintypes.WORD),
            ("biBitCount", wintypes.WORD),
            ("biCompression", wintypes.DWORD),
            ("biSizeImage", wintypes.DWORD),
            ("biXPelsPerMeter", wintypes.LONG),
            ("biYPelsPerMeter", wintypes.LONG),
            ("biClrUsed", wintypes.DWORD),
            ("biClrImportant", wintypes.DWORD),
        ]

    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]

    gdi32.GetDIBits.argtypes = [
        wintypes.HDC,
        wintypes.HANDLE,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.c_void_p,
        ctypes.POINTER(BITMAPINFO),
        wintypes.UINT,
    ]
    gdi32.GetDIBits.restype = ctypes.c_int


class ScreenSampler:
    def __init__(self, target_window: int, width: int = CAPTURE_WIDTH, height: int = CAPTURE_HEIGHT):
        self.width = width
        self.height = height
        rect = wintypes.RECT()
        if target_window and user32.GetWindowRect(target_window, ctypes.byref(rect)):
            self.source_x = int(rect.left)
            self.source_y = int(rect.top)
            self.source_width = max(1, int(rect.right - rect.left))
            self.source_height = max(1, int(rect.bottom - rect.top))
        else:
            self.source_x = 0
            self.source_y = 0
            self.source_width = user32.GetSystemMetrics(0)
            self.source_height = user32.GetSystemMetrics(1)
        self.screen_dc = user32.GetDC(0)
        self.memory_dc = gdi32.CreateCompatibleDC(self.screen_dc)
        self.bitmap = gdi32.CreateCompatibleBitmap(self.screen_dc, width, height)
        self.old_object = gdi32.SelectObject(self.memory_dc, self.bitmap)
        self.buffer = ctypes.create_string_buffer(width * height * 4)
        self.info = BITMAPINFO()
        self.info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.info.bmiHeader.biWidth = width
        self.info.bmiHeader.biHeight = -height
        self.info.bmiHeader.biPlanes = 1
        self.info.bmiHeader.biBitCount = 32
        self.info.bmiHeader.biCompression = 0
        self.info.bmiHeader.biSizeImage = width * height * 4

    def capture_gray(self) -> bytes:
        ok = gdi32.StretchBlt(
            self.memory_dc,
            0,
            0,
            self.width,
            self.height,
            self.screen_dc,
            self.source_x,
            self.source_y,
            self.source_width,
            self.source_height,
            SRCCOPY,
        )
        if not ok:
            raise OSError("屏幕采集失败")
        rows = gdi32.GetDIBits(
            self.memory_dc,
            self.bitmap,
            0,
            self.height,
            self.buffer,
            ctypes.byref(self.info),
            DIB_RGB_COLORS,
        )
        if rows != self.height:
            raise OSError("屏幕读取失败")
        raw = self.buffer.raw
        gray = bytearray(self.width * self.height)
        gi = 0
        for i in range(0, len(raw), 4):
            b = raw[i]
            g = raw[i + 1]
            r = raw[i + 2]
            gray[gi] = (r * 77 + g * 150 + b * 29) >> 8
            gi += 1
        return bytes(gray)

    def close(self) -> None:
        try:
            gdi32.SelectObject(self.memory_dc, self.old_object)
            gdi32.DeleteObject(self.bitmap)
            gdi32.DeleteDC(self.memory_dc)
            user32.ReleaseDC(0, self.screen_dc)
        except Exception:
            pass


def key_down(name: str) -> None:
    user32.keybd_event(VK[name], 0, 0, 0)


def key_up(name: str) -> None:
    user32.keybd_event(VK[name], 0, KEYEVENTF_KEYUP, 0)


def release_all_keys() -> None:
    for name in VK:
        try:
            key_up(name)
        except Exception:
            pass


def press_action(action: list[str], hold: float) -> None:
    for key in action:
        key_down(key)
    time.sleep(max(0.01, min(float(hold), 0.5)))
    for key in reversed(action):
        key_up(key)


def esc_pressed() -> bool:
    return bool(user32.GetAsyncKeyState(VK["escape"]) & 0x8000)


def wait_esc_release() -> None:
    while esc_pressed():
        time.sleep(0.03)


def foreground_window() -> int:
    return int(user32.GetForegroundWindow())


def frame_state(gray: bytes, previous: bytes | None = None) -> tuple[str, float]:
    width = CAPTURE_WIDTH
    height = CAPTURE_HEIGHT
    block_w = width // 8
    block_h = height // 8
    values = []
    for by in range(8):
        y0 = by * block_h
        for bx in range(8):
            x0 = bx * block_w
            total = 0
            count = 0
            for y in range(y0, min(y0 + block_h, height), 3):
                base = y * width
                for x in range(x0, min(x0 + block_w, width), 3):
                    total += gray[base + x]
                    count += 1
            values.append(total // max(1, count))
    mean = sum(values) / len(values)
    bits = 0
    for index, value in enumerate(values):
        if value >= mean:
            bits |= 1 << index
    motion = 0.0
    if previous is not None and len(previous) == len(gray):
        total = 0
        count = 0
        for index in range(0, len(gray), 4):
            total += abs(gray[index] - previous[index])
            count += 1
        motion = total / max(1, count) / 255.0
    bucket = min(7, int(motion * 32))
    state = f"{bits:016x}{bucket:x}"
    return state, motion


def q_row(model: dict, state: str, action_count: int) -> list[float]:
    q = model.setdefault("q", {})
    row = q.get(state)
    if not isinstance(row, list) or len(row) != action_count:
        row = [0.0] * action_count
        q[state] = row
    return row


def choose_action(model: dict, state: str, action_count: int, epsilon: float) -> int:
    row = q_row(model, state, action_count)
    if random.random() < epsilon:
        return random.randrange(action_count)
    best_value = max(row)
    choices = [index for index, value in enumerate(row) if value == best_value]
    return random.choice(choices)


def update_q(model: dict, state: str, action: int, reward: float, next_state: str, action_count: int, alpha: float, gamma: float) -> None:
    current = q_row(model, state, action_count)
    following = q_row(model, next_state, action_count)
    current[action] += alpha * (reward + gamma * max(following) - current[action])


def append_experience(item: dict) -> None:
    with EXPERIENCE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def save_model(model: dict) -> None:
    model["updated_at"] = now_text()
    save_json(MODEL_PATH, model)


def upgrade_agent(stop_event: threading.Event | None = None) -> dict:
    config = load_config()
    model = load_model()
    limit = int(config.get("experience_limit", EXPERIENCE_LIMIT))
    records, invalid = sanitize_experience(limit)
    experiences = []
    if EXPERIENCE_PATH.exists():
        with EXPERIENCE_PATH.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    experiences.append(json.loads(line))
    action_count = len(config["actions"])
    alpha = float(config["learning_rate"])
    gamma = float(config["discount"])
    for _ in range(3):
        if stop_event is not None and stop_event.is_set():
            break
        random.shuffle(experiences)
        for item in experiences:
            if stop_event is not None and stop_event.is_set():
                break
            action = int(item["a"])
            if 0 <= action < action_count:
                update_q(
                    model,
                    item["s"],
                    action,
                    float(item["r"]),
                    item["n"],
                    action_count,
                    alpha,
                    gamma,
                )
    model["training_rounds"] = int(model.get("training_rounds", 0)) + 1
    save_model(model)
    return {
        "records": records,
        "invalid": invalid,
        "states": len(model.get("q", {})),
        "rounds": model["training_rounds"],
    }


class AnyGameAIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("560x210")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.stop_and_close)
        self.root.attributes("-topmost", True)
        self.root.after(600, lambda: self.root.attributes("-topmost", False))
        self.stop_event = threading.Event()
        self.busy = False

        title = tk.Label(self.root, text="AnyGameAI", font=("Segoe UI", 22, "bold"))
        title.pack(pady=(20, 14))

        buttons = tk.Frame(self.root)
        buttons.pack()
        self.file_button = tk.Button(buttons, text="文件", width=10, height=2, command=self.file_mode)
        self.human_button = tk.Button(buttons, text="人", width=10, height=2, command=self.human_mode)
        self.upgrade_button = tk.Button(buttons, text="升级", width=10, height=2, command=self.upgrade_mode)
        self.ai_button = tk.Button(buttons, text="AI", width=10, height=2, command=self.ai_mode)
        for index, button in enumerate((self.file_button, self.human_button, self.upgrade_button, self.ai_button)):
            button.grid(row=0, column=index, padx=7)

        self.status = tk.StringVar(value="就绪；ESC 可结束当前模式")
        tk.Label(self.root, textvariable=self.status, font=("Segoe UI", 10)).pack(pady=18)

        self.root.bind("<Escape>", lambda _event: self.request_stop())

    def set_busy(self, value: bool) -> None:
        self.busy = value
        state = tk.DISABLED if value else tk.NORMAL
        for button in (self.file_button, self.human_button, self.upgrade_button, self.ai_button):
            button.config(state=state)

    def request_stop(self) -> None:
        self.stop_event.set()

    def stop_and_close(self) -> None:
        self.stop_event.set()
        release_all_keys()
        self.root.destroy()

    def run_worker(self, status: str, worker, hide: bool = False) -> None:
        if self.busy:
            return
        self.stop_event.clear()
        self.set_busy(True)
        self.status.set(status)
        if hide:
            self.root.withdraw()

        def task():
            error = None
            result = None
            try:
                result = worker()
            except Exception:
                error = traceback.format_exc()
                log_error(error)
            self.root.after(0, lambda: self.worker_done(result, error, hide))

        threading.Thread(target=task, daemon=True).start()

    def worker_done(self, result, error: str | None, hidden: bool) -> None:
        release_all_keys()
        if hidden:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        self.set_busy(False)
        if error:
            self.status.set("失败")
            messagebox.showerror(APP_NAME, "运行失败，详情已写入桌面 AnyGameAI 文件夹中的日志。")
            return
        self.status.set(str(result) if result else "已结束")

    def file_mode(self) -> None:
        def work():
            result = ensure_files(self.stop_event, check_remote=True)
            parts = [
                f"修复 {result['repaired']} 项",
                f"经验 {result['records']} 条",
                f"清除损坏记录 {result['removed_records']} 条",
            ]
            if result.get("downloaded"):
                parts.append(f"下载 {result['downloaded']} 项")
            if result.get("download_error"):
                parts.append("远程更新失败，已保留本地可用文件")
            return "文件检查完成：" + "；".join(parts)

        self.run_worker("正在检查、补全和修复文件…", work)

    def human_mode(self) -> None:
        def work():
            wait_esc_release()
            while not self.stop_event.is_set():
                if esc_pressed():
                    break
                time.sleep(0.05)
            wait_esc_release()
            return "人玩模式已结束"

        self.run_worker("人玩模式运行中；按 ESC 结束", work, hide=True)

    def upgrade_mode(self) -> None:
        def work():
            result = upgrade_agent(self.stop_event)
            return (
                f"升级完成：经验 {result['records']} 条；"
                f"状态 {result['states']} 个；训练轮次 {result['rounds']}"
            )

        self.run_worker("正在升级模型并整理经验池…", work)

    def ai_mode(self) -> None:
        def work():
            config = load_config()
            model = load_model()
            actions = config["actions"]
            action_count = len(actions)
            alpha = float(config["learning_rate"])
            gamma = float(config["discount"])
            epsilon_base = float(config["epsilon"])
            hold = float(config["action_hold_seconds"])
            pause = float(config["step_pause_seconds"])

            wait_esc_release()
            time.sleep(1.0)
            target = foreground_window()
            if not target or target == int(user32.GetShellWindow()):
                return "未检测到游戏窗口，AI 模式已结束"

            sampler = ScreenSampler(target)
            previous = None
            seen = set()
            recent_states = []
            steps_since_save = 0
            try:
                gray = sampler.capture_gray()
                state, _ = frame_state(gray, previous)
                previous = gray
                seen.add(state)
                while not self.stop_event.is_set():
                    if esc_pressed():
                        break
                    if foreground_window() != target:
                        time.sleep(0.08)
                        continue

                    model_steps = int(model.get("steps", 0))
                    epsilon = max(0.04, epsilon_base / math.sqrt(1.0 + model_steps / 2500.0))
                    action_index = choose_action(model, state, action_count, epsilon)
                    press_action(actions[action_index], hold)
                    if pause > 0:
                        time.sleep(min(pause, 0.5))

                    next_gray = sampler.capture_gray()
                    next_state, motion = frame_state(next_gray, previous)
                    previous = next_gray

                    novelty = 0.22 if next_state not in seen else 0.0
                    static_penalty = 0.45 if motion < 0.008 else 0.0
                    repeat_penalty = 0.18 if recent_states.count(next_state) >= 3 else 0.0
                    reward = min(1.4, motion * 7.0) + novelty - static_penalty - repeat_penalty

                    update_q(
                        model,
                        state,
                        action_index,
                        reward,
                        next_state,
                        action_count,
                        alpha,
                        gamma,
                    )
                    model["steps"] = model_steps + 1
                    append_experience(
                        {
                            "t": now_text(),
                            "s": state,
                            "a": action_index,
                            "r": round(reward, 6),
                            "n": next_state,
                        }
                    )

                    seen.add(next_state)
                    recent_states.append(next_state)
                    if len(recent_states) > 10:
                        recent_states.pop(0)
                    state = next_state
                    steps_since_save += 1
                    if steps_since_save >= 100:
                        save_model(model)
                        steps_since_save = 0
                        if model["steps"] % 1000 == 0:
                            sanitize_experience(int(config.get("experience_limit", EXPERIENCE_LIMIT)))
            finally:
                release_all_keys()
                sampler.close()
                save_model(model)
                sanitize_experience(int(config.get("experience_limit", EXPERIENCE_LIMIT)))
                wait_esc_release()
            return f"AI 模式已结束；累计步骤 {model.get('steps', 0)}"

        self.run_worker("AI 模式运行中；切换窗口会暂停；按 ESC 结束", work, hide=True)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    if os.name != "nt":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP_NAME, "此程序仅支持 Windows 11 x64。")
        root.destroy()
        return
    if sys.version_info < (3, 12):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP_NAME, "需要 Python 3.12 或更高版本。")
        root.destroy()
        return
    bootstrap_to_desktop()
    hide_console()
    ensure_files(check_remote=False)
    AnyGameAIApp().run()


if __name__ == "__main__":
    main()
