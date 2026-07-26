import ctypes
import hashlib
import json
import math
import os
import queue
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
import uuid
import winreg
from collections import deque
from ctypes import wintypes
from dataclasses import dataclass, field
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_NAME = "AnyGameAI"
SCRIPT_NAME = "AnyGameAI.py"
CONFIG_NAME = "config.json"
DATABASE_NAME = "agent.sqlite3"
LOG_NAME = "AnyGameAI.log"
ERROR_ALREADY_EXISTS = 183
VK_ESCAPE = 0x1B
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
MAPVK_VK_TO_VSC = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C
WM_QUIT = 0x0012
LLKHF_INJECTED = 0x10
LLMHF_INJECTED = 0x01
SRCCOPY = 0x00CC0020
CAPTUREBLT = 0x40000000
BI_RGB = 0
DIB_RGB_COLORS = 0
HALFTONE = 4
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
TOKEN_QUERY = 0x0008
TOKEN_INTEGRITY_LEVEL = 25
COINIT_MULTITHREADED = 0x0
CLSCTX_ALL = 23
ERENDER = 0
EMULTIMEDIA = 1

DEFAULT_CONFIG = {
    "切换游戏窗口等待秒数": 3.0,
    "人类采样秒数": 0.025,
    "AI动作后等待秒数": 0.055,
    "初始随机探索概率": 0.28,
    "最低随机探索概率": 0.04,
    "随机探索衰减": 0.9994,
    "学习率": 0.16,
    "折扣因子": 0.82,
    "示范先验": 1.20,
    "状态相似阈值": 0.145,
    "每桶代表状态数": 4,
    "每个游戏最大状态数": 12000,
    "每个游戏最大动作数": 128,
    "采样宽度": 64,
    "采样高度": 36,
    "状态宽度": 12,
    "状态高度": 7,
    "动作时长毫秒": [50, 100, 200, 400, 800],
    "鼠标移动档位像素": [12, 36, 96],
    "无变化阈值": 0.006,
    "停滞步数": 10,
    "黑帧比例": 0.985,
    "黑帧持续秒数": 2.0,
    "连续捕获失败次数": 20,
    "奖励区域": [],
    "正反馈键": "F8",
    "负反馈键": "F9",
    "启用音频状态": False,
    "启用手柄观察": False,
    "数据库批量条数": 256,
    "数据库刷新秒数": 1.0
}

KEY_CODES = {
    "BACKSPACE": 0x08, "TAB": 0x09, "ENTER": 0x0D, "SHIFT": 0x10,
    "CTRL": 0x11, "ALT": 0x12, "PAUSE": 0x13, "CAPSLOCK": 0x14,
    "SPACE": 0x20, "PAGEUP": 0x21, "PAGEDOWN": 0x22, "END": 0x23,
    "HOME": 0x24, "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27,
    "DOWN": 0x28, "INSERT": 0x2D, "DELETE": 0x2E,
    "NUMLOCK": 0x90, "SCROLLLOCK": 0x91,
    "LSHIFT": 0xA0, "RSHIFT": 0xA1, "LCTRL": 0xA2, "RCTRL": 0xA3,
    "LALT": 0xA4, "RALT": 0xA5,
    "SEMICOLON": 0xBA, "PLUS": 0xBB, "COMMA": 0xBC, "MINUS": 0xBD,
    "PERIOD": 0xBE, "SLASH": 0xBF, "BACKTICK": 0xC0,
    "LBRACKET": 0xDB, "BACKSLASH": 0xDC, "RBRACKET": 0xDD, "QUOTE": 0xDE,
    **{str(index): 0x30 + index for index in range(10)},
    **{chr(65 + index): 0x41 + index for index in range(26)},
    **{f"NUM{index}": 0x60 + index for index in range(10)},
    "MULTIPLY": 0x6A, "ADD": 0x6B, "SUBTRACT": 0x6D, "DECIMAL": 0x6E, "DIVIDE": 0x6F,
    **{f"F{index}": 0x6F + index for index in range(1, 25)}
}
VK_NAMES = {value: key for key, value in KEY_CODES.items()}
EXTENDED_KEYS = {"LEFT", "UP", "RIGHT", "DOWN", "HOME", "END", "PAGEUP", "PAGEDOWN", "INSERT", "DELETE",
                 "RCTRL", "RALT", "DIVIDE"}
SYSTEM_FORBIDDEN_KEYS = {"LWIN", "RWIN", "APPS", "SLEEP"}


def has_forbidden_system_combination(keys):
    key_set = set(keys)
    alt = bool(key_set.intersection({"ALT", "LALT", "RALT"}))
    ctrl = bool(key_set.intersection({"CTRL", "LCTRL", "RCTRL"}))
    if alt and key_set.intersection({"F4", "TAB", "ESC", "SPACE"}):
        return True
    if ctrl and "ESC" in key_set:
        return True
    if ctrl and alt and "DELETE" in key_set:
        return True
    return False


MOUSE_BUTTONS = {"LEFT", "RIGHT", "MIDDLE", "X1", "X2"}
MOUSE_FLAG_MAP = {
    "LEFT": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, 0),
    "RIGHT": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, 0),
    "MIDDLE": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP, 0),
    "X1": (MOUSEEVENTF_XDOWN, MOUSEEVENTF_XUP, XBUTTON1),
    "X2": (MOUSEEVENTF_XDOWN, MOUSEEVENTF_XUP, XBUTTON2)
}
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
LRESULT = ctypes.c_ssize_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", INPUT_UNION)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD), ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]


class RGBQUAD(ctypes.Structure):
    _fields_ = [("rgbBlue", ctypes.c_ubyte), ("rgbGreen", ctypes.c_ubyte),
                ("rgbRed", ctypes.c_ubyte), ("rgbReserved", ctypes.c_ubyte)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", RGBQUAD * 1)]


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wintypes.POINT), ("mouseData", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Sid", wintypes.LPVOID), ("Attributes", wintypes.DWORD)]


class TOKEN_MANDATORY_LABEL_STRUCT(ctypes.Structure):
    _fields_ = [("Label", SID_AND_ATTRIBUTES)]


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8)]

    @classmethod
    def from_string(cls, value):
        raw = uuid.UUID(value).bytes_le
        return cls.from_buffer_copy(raw)


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [("wButtons", wintypes.WORD), ("bLeftTrigger", ctypes.c_ubyte),
                ("bRightTrigger", ctypes.c_ubyte), ("sThumbLX", ctypes.c_short),
                ("sThumbLY", ctypes.c_short), ("sThumbRX", ctypes.c_short), ("sThumbRY", ctypes.c_short)]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [("dwPacketNumber", wintypes.DWORD), ("Gamepad", XINPUT_GAMEPAD)]


user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
ole32 = ctypes.WinDLL("ole32", use_last_error=True)

HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
kernel32.PostThreadMessageW.restype = wintypes.BOOL

advapi32.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
advapi32.OpenProcessToken.restype = wintypes.BOOL
advapi32.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
advapi32.GetTokenInformation.restype = wintypes.BOOL
advapi32.GetSidSubAuthorityCount.argtypes = [wintypes.LPVOID]
advapi32.GetSidSubAuthorityCount.restype = ctypes.POINTER(ctypes.c_ubyte)
advapi32.GetSidSubAuthority.argtypes = [wintypes.LPVOID, wintypes.DWORD]
advapi32.GetSidSubAuthority.restype = ctypes.POINTER(wintypes.DWORD)

user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
user32.ClientToScreen.restype = wintypes.BOOL
user32.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
user32.ScreenToClient.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ReleaseDC.restype = ctypes.c_int
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = wintypes.SHORT
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = LRESULT
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = LRESULT

gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.SetStretchBltMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.SetStretchBltMode.restype = ctypes.c_int
gdi32.StretchBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                             wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.DWORD]
gdi32.StretchBlt.restype = wintypes.BOOL
gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT,
                            wintypes.LPVOID, ctypes.POINTER(BITMAPINFO), wintypes.UINT]
gdi32.GetDIBits.restype = ctypes.c_int
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.DeleteDC.restype = wintypes.BOOL

ole32.CoInitializeEx.argtypes = [wintypes.LPVOID, wintypes.DWORD]
ole32.CoInitializeEx.restype = ctypes.c_long
ole32.CoUninitialize.argtypes = []
ole32.CoUninitialize.restype = None
ole32.CoCreateInstance.argtypes = [ctypes.POINTER(GUID), wintypes.LPVOID, wintypes.DWORD,
                                   ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
ole32.CoCreateInstance.restype = ctypes.c_long


def desktop_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
            value, _ = winreg.QueryValueEx(key, "Desktop")
            return Path(os.path.expandvars(value)).resolve()
    except OSError:
        return (Path.home() / "Desktop").resolve()


WORK_DIR = desktop_path() / APP_NAME
DATA_DIR = WORK_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
LOG_DIR = WORK_DIR / "logs"
MODEL_DIR = WORK_DIR / "models"
RUNTIME_DIR = WORK_DIR / "runtime"
CACHE_DIR = WORK_DIR / "cache"
CONFIG_PATH = WORK_DIR / CONFIG_NAME
DATABASE_PATH = DATA_DIR / DATABASE_NAME
LOG_PATH = LOG_DIR / LOG_NAME
LEGACY_STATE_PATH = WORK_DIR / "agent_state.json"


def ensure_directories():
    for path in (WORK_DIR, DATA_DIR, BACKUP_DIR, LOG_DIR, MODEL_DIR, RUNTIME_DIR, CACHE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def write_log(text):
    try:
        ensure_directories()
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(f"[{stamp}] {text}\n")
    except OSError:
        pass


def relocate():
    ensure_directories()
    source = Path(__file__).resolve()
    target = (WORK_DIR / SCRIPT_NAME).resolve()
    if source != target:
        shutil.copy2(source, target)
        subprocess.Popen([sys.executable, str(target)], cwd=str(WORK_DIR),
                         creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        return True
    os.chdir(WORK_DIR)
    return False


def ensure_single_instance():
    ctypes.set_last_error(0)
    handle = kernel32.CreateMutexW(None, False, "Local\\AnyGameAI.Python312.V4")
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return None
    return handle


def clamp_float(value, minimum, maximum, fallback):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = fallback
    return max(minimum, min(maximum, number))


def clamp_int(value, minimum, maximum, fallback):
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = fallback
    return max(minimum, min(maximum, number))


def load_config():
    ensure_directories()
    data = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update(loaded)
        except (OSError, json.JSONDecodeError):
            try:
                shutil.copy2(CONFIG_PATH, CONFIG_PATH.with_suffix(".损坏.json"))
            except OSError:
                pass
    data["切换游戏窗口等待秒数"] = clamp_float(data.get("切换游戏窗口等待秒数"), 0.5, 20.0, 3.0)
    data["人类采样秒数"] = clamp_float(data.get("人类采样秒数"), 0.01, 0.20, 0.025)
    data["AI动作后等待秒数"] = clamp_float(data.get("AI动作后等待秒数"), 0.01, 1.0, 0.055)
    data["初始随机探索概率"] = clamp_float(data.get("初始随机探索概率"), 0.0, 1.0, 0.28)
    data["最低随机探索概率"] = clamp_float(data.get("最低随机探索概率"), 0.0, 1.0, 0.04)
    data["随机探索衰减"] = clamp_float(data.get("随机探索衰减"), 0.90, 1.0, 0.9994)
    data["学习率"] = clamp_float(data.get("学习率"), 0.01, 1.0, 0.16)
    data["折扣因子"] = clamp_float(data.get("折扣因子"), 0.0, 0.999, 0.82)
    data["示范先验"] = clamp_float(data.get("示范先验"), 0.0, 10.0, 1.20)
    data["状态相似阈值"] = clamp_float(data.get("状态相似阈值"), 0.02, 0.50, 0.145)
    data["每桶代表状态数"] = clamp_int(data.get("每桶代表状态数"), 1, 12, 4)
    data["每个游戏最大状态数"] = clamp_int(data.get("每个游戏最大状态数"), 500, 100000, 12000)
    data["每个游戏最大动作数"] = clamp_int(data.get("每个游戏最大动作数"), 64, 512, 128)
    data["采样宽度"] = clamp_int(data.get("采样宽度"), 24, 192, 64)
    data["采样高度"] = clamp_int(data.get("采样高度"), 14, 108, 36)
    data["状态宽度"] = clamp_int(data.get("状态宽度"), 4, data["采样宽度"], 12)
    data["状态高度"] = clamp_int(data.get("状态高度"), 3, data["采样高度"], 7)
    durations = data.get("动作时长毫秒")
    if not isinstance(durations, list):
        durations = [50, 100, 200, 400]
    durations = sorted({clamp_int(value, 20, 2000, 100) for value in durations})
    data["动作时长毫秒"] = durations or [50, 100, 200, 400, 800]
    mouse_steps = data.get("鼠标移动档位像素")
    if not isinstance(mouse_steps, list):
        legacy_step = clamp_int(data.get("鼠标移动像素"), 4, 500, 36)
        mouse_steps = [max(4, legacy_step // 3), legacy_step, min(500, legacy_step * 3)]
    mouse_steps = sorted({clamp_int(value, 4, 1000, 36) for value in mouse_steps})[:3]
    data["鼠标移动档位像素"] = mouse_steps or [12, 36, 96]
    data.pop("鼠标移动像素", None)
    data["无变化阈值"] = clamp_float(data.get("无变化阈值"), 0.0005, 0.10, 0.006)
    data["停滞步数"] = clamp_int(data.get("停滞步数"), 3, 100, 10)
    data["黑帧比例"] = clamp_float(data.get("黑帧比例"), 0.80, 1.0, 0.985)
    data["黑帧持续秒数"] = clamp_float(data.get("黑帧持续秒数"), 0.5, 10.0, 2.0)
    data["连续捕获失败次数"] = clamp_int(data.get("连续捕获失败次数"), 3, 500, 20)
    if not isinstance(data.get("奖励区域"), list):
        data["奖励区域"] = []
    for key, fallback in (("正反馈键", "F8"), ("负反馈键", "F9")):
        name = str(data.get(key, fallback)).upper()
        data[key] = name if name in KEY_CODES and name != "ESC" else fallback
    if data["正反馈键"] == data["负反馈键"]:
        data["负反馈键"] = "F9" if data["正反馈键"] != "F9" else "F8"
    data["启用音频状态"] = bool(data.get("启用音频状态", False))
    data["启用手柄观察"] = bool(data.get("启用手柄观察", False))
    data["数据库批量条数"] = clamp_int(data.get("数据库批量条数"), 32, 4096, 256)
    data["数据库刷新秒数"] = clamp_float(data.get("数据库刷新秒数"), 0.2, 5.0, 1.0)
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return "未命名窗口"
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, len(buffer))
    return buffer.value or "未命名窗口"


def window_process_id(hwnd):
    process_id = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    return int(process_id.value)


def process_path(process_id):
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return buffer.value.lower()
    finally:
        kernel32.CloseHandle(handle)
    return ""


def window_class(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    if user32.GetClassNameW(hwnd, buffer, len(buffer)):
        return buffer.value.lower()
    return ""


def client_size(hwnd):
    rect = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return 0, 0
    return max(0, rect.right - rect.left), max(0, rect.bottom - rect.top)


def normalize_title(title):
    value = re.sub(r"\d+(?:[.,:]\d+)*", "#", title.lower())
    value = re.sub(r"\s+", " ", value).strip(" -_|:")
    return value[:180] or "未命名窗口"


def window_identity(hwnd, title):
    pid = window_process_id(hwnd)
    path = process_path(pid)
    class_name = window_class(hwnd)
    width, height = client_size(hwnd)
    normalized = normalize_title(title)
    identity = f"{path}|{class_name}"
    return identity, path, class_name, width, height, normalized


def valid_target_window(hwnd):
    return bool(hwnd and user32.IsWindow(hwnd) and user32.IsWindowVisible(hwnd)
                and window_process_id(hwnd) != os.getpid())


def integrity_level_from_handle(process_handle):
    token = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(process_handle, TOKEN_QUERY, ctypes.byref(token)):
        return None
    try:
        needed = wintypes.DWORD()
        advapi32.GetTokenInformation(token, TOKEN_INTEGRITY_LEVEL, None, 0, ctypes.byref(needed))
        if not needed.value:
            return None
        buffer = ctypes.create_string_buffer(needed.value)
        if not advapi32.GetTokenInformation(token, TOKEN_INTEGRITY_LEVEL, buffer, needed.value, ctypes.byref(needed)):
            return None
        label = ctypes.cast(buffer, ctypes.POINTER(TOKEN_MANDATORY_LABEL_STRUCT)).contents
        count_ptr = advapi32.GetSidSubAuthorityCount(label.Label.Sid)
        if not count_ptr:
            return None
        count = int(count_ptr.contents.value)
        if count <= 0:
            return None
        value_ptr = advapi32.GetSidSubAuthority(label.Label.Sid, count - 1)
        return int(value_ptr.contents.value) if value_ptr else None
    finally:
        kernel32.CloseHandle(token)


def process_integrity_level(process_id=None):
    if process_id is None or process_id == os.getpid():
        return integrity_level_from_handle(kernel32.GetCurrentProcess())
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    if not handle:
        return None
    try:
        return integrity_level_from_handle(handle)
    finally:
        kernel32.CloseHandle(handle)


def send_inputs(items):
    if not items:
        return
    array_type = INPUT * len(items)
    array = array_type(*items)
    sent = user32.SendInput(len(items), array, ctypes.sizeof(INPUT))
    if sent != len(items):
        raise OSError(ctypes.get_last_error(), f"SendInput 仅发送 {sent}/{len(items)} 个输入")


def keyboard_input(name, key_up=False):
    virtual_key = KEY_CODES[name]
    scan_code = user32.MapVirtualKeyW(virtual_key, MAPVK_VK_TO_VSC)
    flags = KEYEVENTF_KEYUP if key_up else 0
    if name in EXTENDED_KEYS:
        flags |= KEYEVENTF_EXTENDEDKEY
    if scan_code:
        flags |= KEYEVENTF_SCANCODE
        data = KEYBDINPUT(0, scan_code, flags, 0, 0)
    else:
        data = KEYBDINPUT(virtual_key, 0, flags, 0, 0)
    return INPUT(type=INPUT_KEYBOARD, ki=data)


def mouse_input(flags, data=0, dx=0, dy=0):
    return INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dx, dy, data, flags, 0, 0))


def current_cursor():
    point = wintypes.POINT()
    if user32.GetCursorPos(ctypes.byref(point)):
        return point.x, point.y
    return 0, 0


@dataclass(frozen=True)
class ActionSpec:
    keys: tuple = ()
    mouse_buttons: tuple = ()
    mouse_dx: int = 0
    mouse_dy: int = 0
    wheel: int = 0
    hold_ms: int = 100

    def normalized(self):
        keys = tuple(sorted({key for key in self.keys if key in KEY_CODES and key != "ESC"
                             and key not in SYSTEM_FORBIDDEN_KEYS}))
        if has_forbidden_system_combination(keys):
            keys = ()
        buttons = tuple(sorted({button for button in self.mouse_buttons if button in MOUSE_BUTTONS}))
        return ActionSpec(keys, buttons, max(-3, min(3, int(self.mouse_dx))),
                          max(-3, min(3, int(self.mouse_dy))), max(-1, min(1, int(self.wheel))),
                          max(20, min(2000, int(self.hold_ms))))

    def signature(self):
        spec = self.normalized()
        return json.dumps({"k": spec.keys, "b": spec.mouse_buttons, "x": spec.mouse_dx,
                           "y": spec.mouse_dy, "w": spec.wheel, "h": spec.hold_ms},
                          ensure_ascii=False, separators=(",", ":"))

    def is_noop(self):
        return not self.keys and not self.mouse_buttons and not self.mouse_dx and not self.mouse_dy and not self.wheel

    @classmethod
    def from_signature(cls, signature):
        raw = json.loads(signature)
        return cls(tuple(raw.get("k", ())), tuple(raw.get("b", ())), int(raw.get("x", 0)),
                   int(raw.get("y", 0)), int(raw.get("w", 0)), int(raw.get("h", 100))).normalized()


@dataclass
class InputEvent:
    time_ns: int
    device: str
    code: str
    event: str
    value: int = 0


class InputMonitor:
    def __init__(self):
        self.events = queue.Queue()
        self.lock = threading.RLock()
        self.pressed_keys = set()
        self.pressed_buttons = set()
        self.blocked_keys = set()
        self.closed = threading.Event()
        self.thread_id = 0
        self.keyboard_proc = HOOKPROC(self._keyboard_callback)
        self.mouse_proc = HOOKPROC(self._mouse_callback)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _keyboard_callback(self, code, wparam, lparam):
        if code >= 0:
            data = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            if not (data.flags & LLKHF_INJECTED):
                name = VK_NAMES.get(int(data.vkCode))
                if name and name != "ESC":
                    blocked = name in self.blocked_keys
                    if wparam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                        with self.lock:
                            first = name not in self.pressed_keys
                            self.pressed_keys.add(name)
                        if first:
                            self.events.put(InputEvent(time.perf_counter_ns(), "keyboard", name, "down"))
                    elif wparam in (WM_KEYUP, WM_SYSKEYUP):
                        with self.lock:
                            self.pressed_keys.discard(name)
                        self.events.put(InputEvent(time.perf_counter_ns(), "keyboard", name, "up"))
                    if blocked:
                        return 1
        return user32.CallNextHookEx(None, code, wparam, lparam)

    def _mouse_callback(self, code, wparam, lparam):
        if code >= 0:
            data = ctypes.cast(lparam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            if not (data.flags & LLMHF_INJECTED):
                button = None
                event = None
                if wparam == WM_LBUTTONDOWN:
                    button, event = "LEFT", "down"
                elif wparam == WM_LBUTTONUP:
                    button, event = "LEFT", "up"
                elif wparam == WM_RBUTTONDOWN:
                    button, event = "RIGHT", "down"
                elif wparam == WM_RBUTTONUP:
                    button, event = "RIGHT", "up"
                elif wparam == WM_MBUTTONDOWN:
                    button, event = "MIDDLE", "down"
                elif wparam == WM_MBUTTONUP:
                    button, event = "MIDDLE", "up"
                elif wparam in (WM_XBUTTONDOWN, WM_XBUTTONUP):
                    high = (int(data.mouseData) >> 16) & 0xFFFF
                    button = "X1" if high == XBUTTON1 else "X2"
                    event = "down" if wparam == WM_XBUTTONDOWN else "up"
                elif wparam == WM_MOUSEWHEEL:
                    delta = ctypes.c_short((int(data.mouseData) >> 16) & 0xFFFF).value
                    self.events.put(InputEvent(time.perf_counter_ns(), "mouse", "WHEEL", "wheel", 1 if delta > 0 else -1))
                if button and event:
                    with self.lock:
                        if event == "down":
                            first = button not in self.pressed_buttons
                            self.pressed_buttons.add(button)
                        else:
                            first = True
                            self.pressed_buttons.discard(button)
                    if first:
                        self.events.put(InputEvent(time.perf_counter_ns(), "mouse", button, event))
        return user32.CallNextHookEx(None, code, wparam, lparam)

    def _run(self):
        self.thread_id = int(kernel32.GetCurrentThreadId())
        module = kernel32.GetModuleHandleW(None)
        keyboard_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self.keyboard_proc, module, 0)
        mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self.mouse_proc, module, 0)
        if not keyboard_hook or not mouse_hook:
            write_log(f"低级输入钩子初始化失败: {ctypes.get_last_error()}")
        message = wintypes.MSG()
        try:
            while not self.closed.is_set() and user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        finally:
            if keyboard_hook:
                user32.UnhookWindowsHookEx(keyboard_hook)
            if mouse_hook:
                user32.UnhookWindowsHookEx(mouse_hook)

    def set_blocked_keys(self, keys):
        with self.lock:
            self.blocked_keys = {key for key in keys if key in KEY_CODES and key != "ESC"}

    def clear(self):
        while True:
            try:
                self.events.get_nowait()
            except queue.Empty:
                break

    def drain(self):
        result = []
        while True:
            try:
                result.append(self.events.get_nowait())
            except queue.Empty:
                return result

    def snapshot(self):
        with self.lock:
            return set(self.pressed_keys), set(self.pressed_buttons)

    def close(self):
        self.closed.set()
        if self.thread_id:
            kernel32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)


class XInputSampler:
    def __init__(self):
        self.dll = None
        self.get_state = None
        for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
            try:
                self.dll = ctypes.WinDLL(name)
                self.get_state = self.dll.XInputGetState
                self.get_state.argtypes = [wintypes.DWORD, ctypes.POINTER(XINPUT_STATE)]
                self.get_state.restype = wintypes.DWORD
                break
            except (OSError, AttributeError):
                self.dll = None
                self.get_state = None

    def snapshot(self):
        if not self.get_state:
            return (0,) * 9
        for index in range(4):
            state = XINPUT_STATE()
            if self.get_state(index, ctypes.byref(state)) == 0:
                gamepad = state.Gamepad
                return (1, int(gamepad.wButtons), int(gamepad.bLeftTrigger), int(gamepad.bRightTrigger),
                        int(gamepad.sThumbLX), int(gamepad.sThumbLY), int(gamepad.sThumbRX),
                        int(gamepad.sThumbRY), index)
        return (0,) * 9


class AudioPeakSampler:
    CLSID_ENUMERATOR = GUID.from_string("BCDE0395-E52F-467C-8E3D-C4579291692E")
    IID_ENUMERATOR = GUID.from_string("A95664D2-9614-4F35-A746-DE8DB63617E6")
    IID_METER = GUID.from_string("C02216F6-8C67-4B5B-9D00-D008E73E0064")

    def __init__(self):
        self.initialized = False
        self.enumerator = ctypes.c_void_p()
        self.device = ctypes.c_void_p()
        self.meter = ctypes.c_void_p()
        try:
            result = ole32.CoInitializeEx(None, COINIT_MULTITHREADED)
            if result >= 0 or result == -2147417850:
                self.initialized = result >= 0
            result = ole32.CoCreateInstance(ctypes.byref(self.CLSID_ENUMERATOR), None, CLSCTX_ALL,
                                            ctypes.byref(self.IID_ENUMERATOR), ctypes.byref(self.enumerator))
            if result < 0 or not self.enumerator:
                return
            method = self._method(self.enumerator, 4, ctypes.c_long, wintypes.DWORD, wintypes.DWORD,
                                  ctypes.POINTER(ctypes.c_void_p))
            result = method(self.enumerator, ERENDER, EMULTIMEDIA, ctypes.byref(self.device))
            if result < 0 or not self.device:
                return
            activate = self._method(self.device, 3, ctypes.c_long, ctypes.POINTER(GUID), wintypes.DWORD,
                                    wintypes.LPVOID, ctypes.POINTER(ctypes.c_void_p))
            result = activate(self.device, ctypes.byref(self.IID_METER), CLSCTX_ALL, None, ctypes.byref(self.meter))
            if result < 0:
                self.meter = ctypes.c_void_p()
        except Exception:
            self.close()

    @staticmethod
    def _method(pointer, index, result_type, *argument_types):
        table = ctypes.cast(pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        address = table[index]
        return ctypes.WINFUNCTYPE(result_type, ctypes.c_void_p, *argument_types)(address)

    def peak(self):
        if not self.meter:
            return 0.0
        value = ctypes.c_float()
        try:
            method = self._method(self.meter, 3, ctypes.c_long, ctypes.POINTER(ctypes.c_float))
            result = method(self.meter, ctypes.byref(value))
            return max(0.0, min(1.0, float(value.value))) if result >= 0 else 0.0
        except Exception:
            return 0.0

    def close(self):
        for pointer in (self.meter, self.device, self.enumerator):
            if pointer:
                try:
                    release = self._method(pointer, 2, wintypes.ULONG)
                    release(pointer)
                except Exception:
                    pass
        self.meter = ctypes.c_void_p()
        self.device = ctypes.c_void_p()
        self.enumerator = ctypes.c_void_p()
        if self.initialized:
            ole32.CoUninitialize()
            self.initialized = False


class GDICapture:
    def __init__(self, sample_width, sample_height):
        self.sample_width = sample_width
        self.sample_height = sample_height
        self.screen_dc = user32.GetDC(None)
        self.memory_dc = gdi32.CreateCompatibleDC(self.screen_dc) if self.screen_dc else None
        self.bitmap = gdi32.CreateCompatibleBitmap(self.screen_dc, sample_width, sample_height) if self.screen_dc else None
        self.old_object = gdi32.SelectObject(self.memory_dc, self.bitmap) if self.memory_dc and self.bitmap else None
        if self.memory_dc:
            gdi32.SetStretchBltMode(self.memory_dc, HALFTONE)
        self.info = BITMAPINFO()
        self.info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.info.bmiHeader.biWidth = sample_width
        self.info.bmiHeader.biHeight = -sample_height
        self.info.bmiHeader.biPlanes = 1
        self.info.bmiHeader.biBitCount = 32
        self.info.bmiHeader.biCompression = BI_RGB
        self.raw_buffer = ctypes.create_string_buffer(sample_width * sample_height * 4)
        self.closed = False

    def capture(self, hwnd):
        if self.closed or not self.screen_dc or not self.memory_dc or not self.bitmap:
            return None, (0, 0)
        rect = wintypes.RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return None, (0, 0)
        source_width = rect.right - rect.left
        source_height = rect.bottom - rect.top
        if source_width < 2 or source_height < 2:
            return None, (source_width, source_height)
        origin = wintypes.POINT(0, 0)
        if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
            return None, (source_width, source_height)
        copied = gdi32.StretchBlt(self.memory_dc, 0, 0, self.sample_width, self.sample_height,
                                  self.screen_dc, origin.x, origin.y, source_width, source_height,
                                  SRCCOPY | CAPTUREBLT)
        if not copied:
            return None, (source_width, source_height)
        rows = gdi32.GetDIBits(self.memory_dc, self.bitmap, 0, self.sample_height, self.raw_buffer,
                               ctypes.byref(self.info), DIB_RGB_COLORS)
        if rows != self.sample_height:
            return None, (source_width, source_height)
        raw = self.raw_buffer.raw
        gray = bytearray(self.sample_width * self.sample_height)
        source_index = 0
        for target_index in range(len(gray)):
            blue = raw[source_index]
            green = raw[source_index + 1]
            red = raw[source_index + 2]
            gray[target_index] = (red * 77 + green * 150 + blue * 29) >> 8
            source_index += 4
        return bytes(gray), (source_width, source_height)

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.old_object and self.memory_dc:
            gdi32.SelectObject(self.memory_dc, self.old_object)
        if self.bitmap:
            gdi32.DeleteObject(self.bitmap)
        if self.memory_dc:
            gdi32.DeleteDC(self.memory_dc)
        if self.screen_dc:
            user32.ReleaseDC(None, self.screen_dc)


class CaptureHealth:
    def __init__(self, config):
        self.config = config
        self.failures = 0
        self.black_since = None
        self.identical = 0
        self.last_frame = None
        self.last_time = None
        self.fps = 0.0
        self.size = None
        self.size_changes = 0

    def failure(self):
        self.failures += 1
        if self.failures >= self.config["连续捕获失败次数"]:
            return "无法读取游戏画面：连续捕获失败。请取消最小化，并尝试无边框窗口模式。"
        return None

    def observe(self, frame, size):
        now = time.monotonic()
        self.failures = 0
        if self.last_time is not None:
            elapsed = max(1e-6, now - self.last_time)
            instant = 1.0 / elapsed
            self.fps = instant if self.fps == 0.0 else self.fps * 0.92 + instant * 0.08
        self.last_time = now
        if self.size is not None and size != self.size:
            self.size_changes += 1
        self.size = size
        black_ratio = sum(1 for value in frame if value <= 4) / max(1, len(frame))
        mean = sum(frame) / max(1, len(frame))
        variance = sum((value - mean) ** 2 for value in frame) / max(1, len(frame))
        black = black_ratio >= self.config["黑帧比例"] and variance < 9.0
        if black:
            if self.black_since is None:
                self.black_since = now
            elif now - self.black_since >= self.config["黑帧持续秒数"]:
                return "无法读取游戏画面：连续获取到黑帧。请使用无边框窗口模式或避免窗口被遮挡。"
        else:
            self.black_since = None
        if self.last_frame == frame:
            self.identical += 1
        else:
            self.identical = 0
        self.last_frame = frame
        return None


class SQLiteStore:
    def __init__(self, path, batch_size=256, flush_interval=1.0):
        self.path = path
        self.batch_size = max(32, int(batch_size))
        self.flush_interval = max(0.2, float(flush_interval))
        self.commands = queue.Queue()
        self.ready = threading.Event()
        self.closed = False
        self.init_error = None
        self.thread = threading.Thread(target=self._run, name="AnyGameAI-Database", daemon=True)
        self.thread.start()
        self.ready.wait()
        if self.init_error is not None:
            raise self.init_error

    @staticmethod
    def _create_schema(connection):
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS games(
                id INTEGER PRIMARY KEY,
                profile_key TEXT NOT NULL UNIQUE,
                identity TEXT NOT NULL,
                title TEXT NOT NULL,
                normalized_title TEXT NOT NULL,
                client_width INTEGER NOT NULL,
                client_height INTEGER NOT NULL,
                human_steps INTEGER NOT NULL DEFAULT 0,
                ai_steps INTEGER NOT NULL DEFAULT 0,
                episodes INTEGER NOT NULL DEFAULT 0,
                idle_change REAL NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS actions(
                id INTEGER PRIMARY KEY,
                game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
                signature TEXT NOT NULL,
                human_count INTEGER NOT NULL DEFAULT 0,
                ai_count INTEGER NOT NULL DEFAULT 0,
                global_visits INTEGER NOT NULL DEFAULT 0,
                global_value REAL NOT NULL DEFAULT 0,
                UNIQUE(game_id, signature)
            );
            CREATE TABLE IF NOT EXISTS states(
                id INTEGER PRIMARY KEY,
                game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
                bucket_base TEXT NOT NULL,
                slot INTEGER NOT NULL,
                feature BLOB NOT NULL,
                visits INTEGER NOT NULL DEFAULT 0,
                demo_visits INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                UNIQUE(game_id, bucket_base, slot)
            );
            CREATE TABLE IF NOT EXISTS q_values(
                state_id INTEGER NOT NULL REFERENCES states(id) ON DELETE CASCADE,
                action_id INTEGER NOT NULL REFERENCES actions(id) ON DELETE CASCADE,
                visits INTEGER NOT NULL DEFAULT 0,
                q_value REAL NOT NULL DEFAULT 0,
                demo_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(state_id, action_id)
            );
            CREATE TABLE IF NOT EXISTS episodes(
                id INTEGER PRIMARY KEY,
                game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
                mode TEXT NOT NULL,
                started_at REAL NOT NULL,
                ended_at REAL,
                total_reward REAL NOT NULL DEFAULT 0,
                steps INTEGER NOT NULL DEFAULT 0,
                terminal_reason TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS metrics(
                id INTEGER PRIMARY KEY,
                game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
                created_at REAL NOT NULL,
                name TEXT NOT NULL,
                value REAL NOT NULL
            );
            INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', '5');
        """)
        connection.commit()

    def _run(self):
        connection = None
        pending = 0
        next_flush = time.monotonic() + self.flush_interval
        try:
            connection = sqlite3.connect(self.path, timeout=30.0)
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute("PRAGMA foreign_keys=ON")
            self._create_schema(connection)
        except Exception as error:
            self.init_error = error
            self.ready.set()
            if connection is not None:
                connection.close()
            return
        self.ready.set()
        try:
            while True:
                timeout = max(0.0, next_flush - time.monotonic()) if pending else 0.5
                try:
                    command = self.commands.get(timeout=timeout)
                except queue.Empty:
                    command = None
                if command is None:
                    if pending and time.monotonic() >= next_flush:
                        try:
                            connection.commit()
                        except Exception as error:
                            write_log(f"数据库定时提交失败: {error}")
                            try:
                                connection.rollback()
                            except Exception:
                                pass
                        pending = 0
                        next_flush = time.monotonic() + self.flush_interval
                    continue
                kind, sql, params, event, result = command
                if kind == "close":
                    try:
                        if pending:
                            connection.commit()
                        result.append(None)
                    except Exception as error:
                        result.append(error)
                    event.set()
                    break
                try:
                    if kind == "query":
                        result.append(connection.execute(sql, params).fetchall())
                    elif kind == "execute":
                        cursor = connection.execute(sql, params)
                        pending += 1
                        result.append(cursor.lastrowid)
                    elif kind == "queue":
                        connection.execute(sql, params)
                        pending += 1
                    elif kind == "flush":
                        connection.commit()
                        pending = 0
                        result.append(None)
                    if pending >= self.batch_size:
                        connection.commit()
                        pending = 0
                    next_flush = time.monotonic() + self.flush_interval
                except Exception as error:
                    try:
                        connection.rollback()
                    except Exception:
                        pass
                    pending = 0
                    if event is None:
                        write_log(f"数据库异步写入失败: {error}")
                    else:
                        result.append(error)
                finally:
                    if event is not None:
                        event.set()
        finally:
            try:
                connection.commit()
            except Exception:
                pass
            connection.close()

    def _request(self, kind, sql="", params=()):
        if self.closed and kind != "close":
            raise RuntimeError("数据库已经关闭")
        event = threading.Event()
        result = []
        self.commands.put((kind, sql, tuple(params), event, result))
        while not event.wait(0.5):
            if not self.thread.is_alive():
                raise RuntimeError("数据库线程意外停止")
        if result and isinstance(result[-1], Exception):
            raise result[-1]
        return result[0] if result else None

    def query(self, sql, params=()):
        return self._request("query", sql, params)

    def execute_now(self, sql, params=()):
        return self._request("execute", sql, params)

    def queue(self, sql, params=()):
        if self.closed:
            return
        self.commands.put(("queue", sql, tuple(params), None, None))

    def flush(self):
        self._request("flush")

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self._request("close")
        finally:
            self.thread.join(timeout=5.0)


@dataclass
class ActionRecord:
    id: int
    spec: ActionSpec
    human_count: int = 0
    ai_count: int = 0
    global_visits: int = 0
    global_value: float = 0.0


@dataclass
class StateRecord:
    id: int
    bucket_base: str
    slot: int
    feature: bytes
    visits: int = 0
    demo_visits: int = 0
    q: dict = field(default_factory=dict)


@dataclass
class GameProfile:
    key: str
    id: int
    identity: str
    title: str
    normalized_title: str
    width: int
    height: int
    human_steps: int = 0
    ai_steps: int = 0
    episodes: int = 0
    idle_change: float = 0.0
    actions: dict = field(default_factory=dict)
    action_by_signature: dict = field(default_factory=dict)
    buckets: dict = field(default_factory=dict)
    states: dict = field(default_factory=dict)
    safe_action_ids: set = field(default_factory=set)


class LearningAgent:
    def __init__(self, config):
        self.config = config
        self.store = SQLiteStore(DATABASE_PATH, config["数据库批量条数"], config["数据库刷新秒数"])
        self.lock = threading.RLock()
        self.profiles = {}
        self._archive_legacy_state()

    def _archive_legacy_state(self):
        if LEGACY_STATE_PATH.exists():
            target = LEGACY_STATE_PATH.with_suffix(".旧版.json")
            if not target.exists():
                try:
                    LEGACY_STATE_PATH.replace(target)
                    write_log("旧版 JSON 状态已保留为 agent_state.旧版.json；新版从 SQLite 开始学习。")
                except OSError:
                    pass

    def activate(self, identity, title, normalized_title, width, height):
        key = hashlib.sha256(identity.encode("utf-8", "replace")).hexdigest()[:24]
        with self.lock:
            if key in self.profiles:
                return key
            now = time.time()
            rows = self.store.query("SELECT id,human_steps,ai_steps,episodes,idle_change FROM games WHERE profile_key=?", (key,))
            if not rows:
                legacy = self.store.query(
                    "SELECT id,human_steps,ai_steps,episodes,idle_change FROM games "
                    "WHERE identity LIKE ? ORDER BY updated_at DESC LIMIT 1", (identity + "|%",))
                if legacy:
                    rows = legacy
                    self.store.execute_now("UPDATE games SET profile_key=?,identity=? WHERE id=?",
                                           (key, identity, int(legacy[0][0])))
            if rows:
                game_id, human_steps, ai_steps, episodes, idle_change = rows[0]
                self.store.queue("UPDATE games SET identity=?,title=?,normalized_title=?,client_width=?,client_height=?,updated_at=? WHERE id=?",
                                 (identity, title, normalized_title, width, height, now, game_id))
            else:
                game_id = self.store.execute_now(
                    "INSERT INTO games(profile_key,identity,title,normalized_title,client_width,client_height,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                    (key, identity, title, normalized_title, width, height, now, now))
                human_steps = ai_steps = episodes = 0
                idle_change = 0.0
            profile = GameProfile(key, int(game_id), identity, title, normalized_title, width, height,
                                  int(human_steps), int(ai_steps), int(episodes), float(idle_change))
            for row in self.store.query("SELECT id,signature,human_count,ai_count,global_visits,global_value FROM actions WHERE game_id=?", (game_id,)):
                action = ActionRecord(int(row[0]), ActionSpec.from_signature(row[1]), int(row[2]), int(row[3]), int(row[4]), float(row[5]))
                profile.actions[action.id] = action
                profile.action_by_signature[action.spec.signature()] = action.id
            for row in self.store.query("SELECT id,bucket_base,slot,feature,visits,demo_visits FROM states WHERE game_id=?", (game_id,)):
                state = StateRecord(int(row[0]), row[1], int(row[2]), bytes(row[3]), int(row[4]), int(row[5]))
                profile.states[state.id] = state
                profile.buckets.setdefault(state.bucket_base, []).append(state)
            if profile.states:
                ids = tuple(profile.states)
                for start in range(0, len(ids), 800):
                    chunk = ids[start:start + 800]
                    placeholders = ",".join("?" for _ in chunk)
                    for row in self.store.query(f"SELECT state_id,action_id,visits,q_value,demo_count FROM q_values WHERE state_id IN ({placeholders})", chunk):
                        state = profile.states.get(int(row[0]))
                        if state:
                            state.q[int(row[1])] = [int(row[2]), float(row[3]), int(row[4])]
            self.profiles[key] = profile
            self._ensure_basic_actions(profile)
            return key

    def _ensure_basic_actions(self, profile):
        durations = self.config["动作时长毫秒"]
        short = min(durations, key=lambda value: abs(value - 100))
        long = min(durations, key=lambda value: abs(value - 400))
        specs = [ActionSpec(hold_ms=short)]
        single_keys = ("W", "A", "S", "D", "UP", "DOWN", "LEFT", "RIGHT",
                       "SPACE", "ENTER", "SHIFT", "CTRL", "E", "Q", "R", "F", "TAB")
        specs.extend(ActionSpec(keys=(key,), hold_ms=short) for key in single_keys)
        specs.extend(ActionSpec(keys=(key,), hold_ms=long)
                     for key in ("W", "A", "S", "D", "UP", "DOWN", "LEFT", "RIGHT"))
        for keys in (("W", "SHIFT"), ("W", "SPACE"), ("A", "SPACE"), ("D", "SPACE"),
                     ("W", "LEFT"), ("W", "RIGHT"), ("W", "CTRL")):
            specs.append(ActionSpec(keys=keys, hold_ms=short))
        for magnitude in (1, 2):
            for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0),
                           (1, 0), (-1, 1), (0, 1), (1, 1)):
                specs.append(ActionSpec(mouse_dx=dx * magnitude, mouse_dy=dy * magnitude, hold_ms=short))
        specs.extend(ActionSpec(mouse_buttons=(button,), hold_ms=short)
                     for button in ("LEFT", "RIGHT", "MIDDLE"))
        specs.extend((ActionSpec(wheel=1, hold_ms=short), ActionSpec(wheel=-1, hold_ms=short)))
        for spec in specs:
            action = self._register_action(profile, spec, False)
            if action is not None:
                profile.safe_action_ids.add(action.id)

    def profile(self, profile_key):
        profile = self.profiles.get(profile_key)
        if profile is None:
            raise RuntimeError("游戏档案未激活")
        return profile

    def _register_action(self, profile, spec, human):
        spec = spec.normalized()
        signature = spec.signature()
        existing = profile.action_by_signature.get(signature)
        if existing is not None:
            action = profile.actions[existing]
            if human:
                action.human_count += 1
                self.store.queue("UPDATE actions SET human_count=? WHERE id=?", (action.human_count, action.id))
            return action
        if len(profile.actions) >= self.config["每个游戏最大动作数"]:
            return self._nearest_action(profile, spec)
        action_id = self.store.execute_now(
            "INSERT INTO actions(game_id,signature,human_count) VALUES(?,?,?)",
            (profile.id, signature, 1 if human else 0))
        action = ActionRecord(int(action_id), spec, 1 if human else 0)
        profile.actions[action.id] = action
        profile.action_by_signature[signature] = action.id
        return action

    def _nearest_action(self, profile, spec):
        best = None
        best_score = float("inf")
        keys = set(spec.keys)
        buttons = set(spec.mouse_buttons)
        for action in profile.actions.values():
            other = action.spec
            score = len(keys.symmetric_difference(other.keys)) + len(buttons.symmetric_difference(other.mouse_buttons))
            score += abs(spec.mouse_dx - other.mouse_dx) + abs(spec.mouse_dy - other.mouse_dy)
            score += abs(spec.wheel - other.wheel) + abs(spec.hold_ms - other.hold_ms) / 200.0
            if score < best_score:
                best, best_score = action, score
        return best

    def register_human_action(self, profile_key, spec):
        with self.lock:
            return self._register_action(self.profile(profile_key), spec, True)

    @staticmethod
    def _feature_distance(first, second):
        if len(first) != len(second) or not first:
            return 1.0
        return sum(abs(left - right) for left, right in zip(first, second)) / (len(first) * 255.0)

    def resolve_state(self, profile_key, bucket_base, feature):
        with self.lock:
            profile = self.profile(profile_key)
            candidates = profile.buckets.get(bucket_base, [])
            nearest = None
            nearest_distance = float("inf")
            for state in candidates:
                distance = self._feature_distance(feature, state.feature)
                if distance < nearest_distance:
                    nearest, nearest_distance = state, distance
            if nearest is not None and nearest_distance <= self.config["状态相似阈值"]:
                state = nearest
            elif len(candidates) < self.config["每桶代表状态数"]:
                slot = len(candidates)
                now = time.time()
                state_id = self.store.execute_now(
                    "INSERT INTO states(game_id,bucket_base,slot,feature,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                    (profile.id, bucket_base, slot, sqlite3.Binary(feature), now, now))
                state = StateRecord(int(state_id), bucket_base, slot, feature)
                profile.states[state.id] = state
                profile.buckets.setdefault(bucket_base, []).append(state)
                self._prune(profile)
            else:
                state = nearest
            state.visits += 1
            self.store.queue("UPDATE states SET visits=?,updated_at=? WHERE id=?", (state.visits, time.time(), state.id))
            return state.id

    def _prune(self, profile):
        maximum = self.config["每个游戏最大状态数"]
        if len(profile.states) <= int(maximum * 1.05):
            return
        keep_count = max(1, int(maximum * 0.90))
        ranked = sorted(profile.states.values(), key=lambda state: state.visits + state.demo_visits * 3, reverse=True)
        remove = ranked[keep_count:]
        remove_ids = [state.id for state in remove]
        for state in remove:
            profile.states.pop(state.id, None)
            bucket = profile.buckets.get(state.bucket_base, [])
            profile.buckets[state.bucket_base] = [item for item in bucket if item.id != state.id]
            if not profile.buckets[state.bucket_base]:
                profile.buckets.pop(state.bucket_base, None)
        for start in range(0, len(remove_ids), 800):
            chunk = remove_ids[start:start + 800]
            placeholders = ",".join("?" for _ in chunk)
            self.store.execute_now(f"DELETE FROM states WHERE id IN ({placeholders})", chunk)

    def demonstrate(self, profile_key, state_id, action_id):
        with self.lock:
            profile = self.profile(profile_key)
            state = profile.states[state_id]
            entry = state.q.setdefault(action_id, [0, 0.0, 0])
            entry[2] += 1
            state.demo_visits += 1
            profile.human_steps += 1
            self.store.queue("INSERT INTO q_values(state_id,action_id,visits,q_value,demo_count) VALUES(?,?,?,?,?) "
                             "ON CONFLICT(state_id,action_id) DO UPDATE SET demo_count=excluded.demo_count",
                             (state_id, action_id, entry[0], entry[1], entry[2]))
            self.store.queue("UPDATE states SET demo_visits=? WHERE id=?", (state.demo_visits, state_id))
            self.store.queue("UPDATE games SET human_steps=?,updated_at=? WHERE id=?",
                             (profile.human_steps, time.time(), profile.id))

    def imitation_score(self, profile_key, state_id, action_id):
        with self.lock:
            state = self.profile(profile_key).states[state_id]
            total = sum(value[2] for value in state.q.values())
            return state.q.get(action_id, [0, 0.0, 0])[2] / total if total else 0.0

    def state_visits(self, profile_key, state_id):
        with self.lock:
            return self.profile(profile_key).states[state_id].visits

    def idle_change(self, profile_key):
        with self.lock:
            return self.profile(profile_key).idle_change

    def observe_idle_change(self, profile_key, value):
        with self.lock:
            profile = self.profile(profile_key)
            profile.idle_change = profile.idle_change * 0.97 + value * 0.03
            self.store.queue("UPDATE games SET idle_change=? WHERE id=?", (profile.idle_change, profile.id))

    def choose(self, profile_key, state_id):
        with self.lock:
            profile = self.profile(profile_key)
            candidates = [action for action in profile.actions.values()
                          if action.id in profile.safe_action_ids or action.human_count > 0]
            if not candidates:
                raise RuntimeError("没有可用的安全动作")
            if len(candidates) == 1:
                return candidates[0]
            epsilon = max(self.config["最低随机探索概率"],
                          self.config["初始随机探索概率"] * (self.config["随机探索衰减"] ** profile.ai_steps))
            if random.random() < epsilon:
                weights = [4.0 if action.human_count > 0 else 1.0 for action in candidates]
                return random.choices(candidates, weights=weights, k=1)[0]
            state = profile.states[state_id]
            total_visits = sum(state.q.get(action.id, [0, 0.0, 0])[0] for action in candidates)
            scores = []
            for action in candidates:
                visits, q_value, demos = state.q.get(action.id, [0, 0.0, 0])
                exploration = 0.02 * math.sqrt(math.log(total_visits + 2.0) / (visits + 1.0))
                demo_bonus = self.config["示范先验"] * demos / max(1, state.demo_visits)
                demo_bonus /= math.sqrt(1.0 + visits)
                noop_bonus = 0.01 if action.spec.is_noop() and state.demo_visits == 0 else 0.0
                scores.append((q_value + exploration + demo_bonus + noop_bonus, action))
            best = max(score for score, _ in scores)
            return random.choice([action for score, action in scores if abs(score - best) < 1e-12])

    def update(self, profile_key, state_id, action_id, reward, next_state_id, terminal, source):
        with self.lock:
            profile = self.profile(profile_key)
            state = profile.states[state_id]
            next_state = profile.states[next_state_id]
            entry = state.q.setdefault(action_id, [0, 0.0, 0])
            visits = entry[0] + 1
            next_best = max((value[1] for value in next_state.q.values()), default=0.0)
            target = reward if terminal else reward + self.config["折扣因子"] * next_best
            rate = max(0.03, self.config["学习率"] / math.sqrt(1.0 + visits * 0.02))
            q_value = entry[1] + rate * (target - entry[1])
            entry[0] = visits
            entry[1] = q_value
            action = profile.actions[action_id]
            action.global_visits += 1
            global_rate = max(0.01, rate * 0.20)
            action.global_value += global_rate * (reward - action.global_value)
            if source == "AI":
                action.ai_count += 1
                profile.ai_steps += 1
            self.store.queue("INSERT INTO q_values(state_id,action_id,visits,q_value,demo_count) VALUES(?,?,?,?,?) "
                             "ON CONFLICT(state_id,action_id) DO UPDATE SET visits=excluded.visits,q_value=excluded.q_value,demo_count=excluded.demo_count",
                             (state_id, action_id, visits, q_value, entry[2]))
            self.store.queue("UPDATE actions SET ai_count=?,global_visits=?,global_value=? WHERE id=?",
                             (action.ai_count, action.global_visits, action.global_value, action.id))
            if source == "AI":
                self.store.queue("UPDATE games SET ai_steps=?,updated_at=? WHERE id=?",
                                 (profile.ai_steps, time.time(), profile.id))

    def start_episode(self, profile_key, mode):
        with self.lock:
            profile = self.profile(profile_key)
            profile.episodes += 1
            self.store.queue("UPDATE games SET episodes=?,updated_at=? WHERE id=?", (profile.episodes, time.time(), profile.id))
            return self.store.execute_now("INSERT INTO episodes(game_id,mode,started_at) VALUES(?,?,?)",
                                          (profile.id, mode, time.time()))

    def end_episode(self, episode_id, reward, steps, reason):
        self.store.queue("UPDATE episodes SET ended_at=?,total_reward=?,steps=?,terminal_reason=? WHERE id=?",
                         (time.time(), reward, steps, reason, episode_id))

    def metric(self, profile_key, name, value):
        with self.lock:
            profile = self.profile(profile_key)
            self.store.queue("INSERT INTO metrics(game_id,created_at,name,value) VALUES(?,?,?,?)",
                             (profile.id, time.time(), name, float(value)))

    def flush(self):
        self.store.flush()

    def close(self):
        self.store.close()


class TemporalStateEncoder:
    def __init__(self, config):
        self.config = config
        self.width = config["采样宽度"]
        self.height = config["采样高度"]
        self.state_width = config["状态宽度"]
        self.state_height = config["状态高度"]
        self.history = deque(maxlen=4)

    def reset(self):
        self.history.clear()

    def add(self, frame):
        self.history.append(frame)

    def _blocks(self, frame):
        values = []
        for state_y in range(self.state_height):
            y0 = state_y * self.height // self.state_height
            y1 = max(y0 + 1, (state_y + 1) * self.height // self.state_height)
            for state_x in range(self.state_width):
                x0 = state_x * self.width // self.state_width
                x1 = max(x0 + 1, (state_x + 1) * self.width // self.state_width)
                total = 0
                count = 0
                for y in range(y0, min(y1, self.height)):
                    block = frame[y * self.width + x0:y * self.width + min(x1, self.width)]
                    total += sum(block)
                    count += len(block)
                values.append(total / max(1, count))
        return values

    @staticmethod
    def _quantize_signed(value, scale):
        normalized = max(-1.0, min(1.0, value / max(1.0, scale)))
        return max(0, min(8, int(round((normalized + 1.0) * 4.0))))

    def encode(self, previous_action, mouse_position, client_dimensions, gamepad, audio_peak):
        current = self.history[-1]
        current_blocks = self._blocks(current)
        features = bytearray([max(0, min(15, int(sum(current_blocks) / max(1, len(current_blocks)) / 16)))])
        features.extend(max(0, min(15, int(value / 16))) for value in current_blocks)
        for lag in range(1, 4):
            if len(self.history) > lag:
                earlier_blocks = self._blocks(self.history[-1 - lag])
                features.extend(self._quantize_signed(now - old, 96.0) for now, old in zip(current_blocks, earlier_blocks))
            else:
                features.extend([4] * len(current_blocks))
        previous = self.history[-2] if len(self.history) > 1 else current
        differences = [abs(left - right) for left, right in zip(current, previous)]
        for x in range(self.state_width):
            x0 = x * self.width // self.state_width
            x1 = max(x0 + 1, (x + 1) * self.width // self.state_width)
            values = [differences[y * self.width + px] for y in range(self.height) for px in range(x0, min(x1, self.width))]
            features.append(max(0, min(15, int(sum(values) / max(1, len(values)) / 16))))
        for y in range(self.state_height):
            y0 = y * self.height // self.state_height
            y1 = max(y0 + 1, (y + 1) * self.height // self.state_height)
            values = differences[y0 * self.width:min(y1, self.height) * self.width]
            features.append(max(0, min(15, int(sum(values) / max(1, len(values)) / 16))))
        edge = 0
        for y in range(self.height):
            row = y * self.width
            for x in range(1, self.width):
                edge += abs(current[row + x] - current[row + x - 1])
        features.append(max(0, min(15, int(edge / max(1, self.height * (self.width - 1)) / 16))))
        mouse_x, mouse_y = mouse_position
        client_width, client_height = client_dimensions
        features.append(max(0, min(15, int(mouse_x * 16 / max(1, client_width)))))
        features.append(max(0, min(15, int(mouse_y * 16 / max(1, client_height)))))
        connected, buttons, left_trigger, right_trigger, lx, ly, rx, ry, controller = gamepad
        features.extend([connected, buttons & 0xFF, (buttons >> 8) & 0xFF,
                         left_trigger // 16, right_trigger // 16,
                         self._quantize_signed(lx, 32767), self._quantize_signed(ly, 32767),
                         self._quantize_signed(rx, 32767), self._quantize_signed(ry, 32767),
                         controller if connected else 0])
        features.append(max(0, min(15, int(audio_peak * 15))))
        signature = previous_action.signature() if previous_action else ""
        action_hash = hashlib.blake2b(signature.encode("utf-8"), digest_size=2).digest()
        features.extend(action_hash)
        features.append(min(15, previous_action.hold_ms // 50) if previous_action else 0)
        coarse = bytearray()
        for index, value in enumerate(features):
            if index < 1 + len(current_blocks) * 4:
                coarse.append(value // 2)
            else:
                coarse.append(value)
        bucket = hashlib.blake2b(coarse, digest_size=10).hexdigest()
        return bucket, bytes(features)


def frame_difference(first, second):
    if not first or not second or len(first) != len(second):
        return 0.0
    return sum(abs(left - right) for left, right in zip(first, second)) / (len(first) * 255.0)


def region_mean(frame, width, height, region):
    try:
        x = max(0.0, min(1.0, float(region.get("x", 0.0))))
        y = max(0.0, min(1.0, float(region.get("y", 0.0))))
        w = max(0.0, min(1.0 - x, float(region.get("w", 1.0))))
        h = max(0.0, min(1.0 - y, float(region.get("h", 1.0))))
    except (TypeError, ValueError):
        return 0.0
    x0, x1 = int(x * width), max(int((x + w) * width), int(x * width) + 1)
    y0, y1 = int(y * height), max(int((y + h) * height), int(y * height) + 1)
    values = []
    for row in range(y0, min(y1, height)):
        values.extend(frame[row * width + x0:row * width + min(x1, width)])
    return sum(values) / max(1, len(values)) / 255.0


class RewardProvider:
    def __init__(self, config, agent, profile_key):
        self.config = config
        self.agent = agent
        self.profile_key = profile_key
        self.width = config["采样宽度"]
        self.height = config["采样高度"]

    def calculate(self, previous_frame, frame, previous_state_id, state_id, action_id, stuck_count,
                  human_feedback=0.0):
        change = frame_difference(previous_frame, frame)
        action = self.agent.profile(self.profile_key).actions[action_id]
        if action.spec.is_noop():
            self.agent.observe_idle_change(self.profile_key, change)
        idle_baseline = self.agent.idle_change(self.profile_key)
        task_reward = 0.0
        task_event = False
        terminal = False
        for region in self.config["奖励区域"]:
            if not isinstance(region, dict) or region.get("启用", True) is False:
                continue
            previous_value = region_mean(previous_frame, self.width, self.height, region)
            current_value = region_mean(frame, self.width, self.height, region)
            delta = current_value - previous_value
            direction = str(region.get("方向", "增加"))
            weight = clamp_float(region.get("权重", 1.0), -20.0, 20.0, 1.0)
            threshold = clamp_float(region.get("阈值", 0.01), 0.0, 1.0, 0.01)
            if direction == "减少":
                delta = -delta
            elif direction == "变化":
                delta = abs(delta)
            if abs(delta) >= threshold:
                task_event = True
                task_reward += weight * delta
            if region.get("回合结束") and abs(delta) >= threshold:
                terminal = True
        if task_event and task_reward != 0.0:
            task_component = math.copysign(min(1.0, 0.72 + abs(task_reward) * 2.0), task_reward)
        else:
            task_component = 0.0
        feedback_component = max(-1.0, min(1.0, float(human_feedback))) * 0.52
        imitation = self.agent.imitation_score(self.profile_key, previous_state_id, action_id)
        novelty = 1.0 / math.sqrt(self.agent.state_visits(self.profile_key, state_id) + 1.0)
        stagnation = 0.0
        if stuck_count >= self.config["停滞步数"]:
            stagnation = min(1.0, (stuck_count - self.config["停滞步数"] + 1) / self.config["停滞步数"])
        activity_threshold = max(self.config["无变化阈值"], idle_baseline * 1.5)
        activity = 0.003 if change >= activity_threshold else -0.003
        reward = task_component + feedback_component + 0.16 * imitation + 0.015 * novelty
        reward += activity - 0.20 * stagnation
        return max(-1.0, min(1.0, reward)), terminal, change


@dataclass
class Session:
    session_id: int
    mode: str
    stop_event: threading.Event = field(default_factory=threading.Event)
    hwnd: int = 0
    title: str = ""
    identity: str = ""
    profile_key: str = ""
    episode_id: int = 0
    thread: object = None
    held_keys: set = field(default_factory=set)
    held_buttons: set = field(default_factory=set)
    end_reason: str = "已结束"
    end_error: bool = False
    total_reward: float = 0.0
    steps: int = 0


class AnyGameAI:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.agent = LearningAgent(config)
        self.input_monitor = InputMonitor()
        self.xinput = XInputSampler()
        self.events = queue.Queue()
        self.state_lock = threading.RLock()
        self.input_lock = threading.RLock()
        self.active_session = None
        self.next_session_id = 1
        self.closed = False
        self.status_var = tk.StringVar(value="请选择模式")
        self.detail_var = tk.StringVar(
            value=f"人：示范；AI：学习与安全探索；{config['正反馈键']}/{config['负反馈键']}：正/负反馈；ESC：结束")
        self.build_ui()
        self.root.after(50, self.process_events)
        threading.Thread(target=self.escape_watch_loop, daemon=True).start()

    def build_ui(self):
        self.root.title(APP_NAME)
        self.root.geometry("520x330")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=APP_NAME, font=("Microsoft YaHei UI", 22, "bold")).pack(pady=(0, 8))
        ttk.Label(frame, textvariable=self.detail_var, anchor="center", justify="center", wraplength=460).pack(pady=(0, 18))
        buttons = ttk.Frame(frame)
        buttons.pack()
        self.human_button = ttk.Button(buttons, text="人", command=lambda: self.begin("人"), width=15)
        self.human_button.grid(row=0, column=0, padx=10, ipadx=4, ipady=15)
        self.ai_button = ttk.Button(buttons, text="AI", command=lambda: self.begin("AI"), width=15)
        self.ai_button.grid(row=0, column=1, padx=10, ipadx=4, ipady=15)
        ttk.Label(frame, textvariable=self.status_var, font=("Microsoft YaHei UI", 10), wraplength=470).pack(pady=(20, 0))
        ttk.Button(frame, text="打开工作目录", command=self.open_work_dir).pack(pady=(13, 0))

    def open_work_dir(self):
        os.startfile(WORK_DIR)

    def set_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        self.human_button.configure(state=state)
        self.ai_button.configure(state=state)

    def begin(self, mode):
        with self.state_lock:
            if self.active_session is not None:
                return
            session = Session(self.next_session_id, mode)
            self.next_session_id += 1
            self.active_session = session
        self.set_buttons(False)
        delay = self.config["切换游戏窗口等待秒数"]
        self.status_var.set(f"{delay:g} 秒内切到游戏窗口")
        self.root.withdraw()
        session.thread = threading.Thread(target=self.arm_session, args=(session, delay), daemon=True)
        session.thread.start()

    def is_current(self, session):
        with self.state_lock:
            return self.active_session is session and self.active_session.session_id == session.session_id

    def arm_session(self, session, delay):
        try:
            deadline = time.monotonic() + delay
            while time.monotonic() < deadline:
                if session.stop_event.wait(0.03) or not self.is_current(session):
                    return
            hwnd = user32.GetForegroundWindow()
            if not valid_target_window(hwnd):
                session.end_reason = "没有检测到可用的游戏窗口"
                session.end_error = True
                return
            title = window_title(hwnd)
            identity, path, class_name, width, height, normalized = window_identity(hwnd, title)
            current_level = process_integrity_level(os.getpid())
            target_level = process_integrity_level(window_process_id(hwnd))
            if current_level is not None and target_level is not None and target_level > current_level:
                session.end_reason = "游戏权限高于 AnyGameAI。请让两者使用相同权限级别后重试。"
                session.end_error = True
                return
            session.hwnd = hwnd
            session.title = title
            session.identity = identity
            session.profile_key = self.agent.activate(identity, title, normalized, width, height)
            session.episode_id = self.agent.start_episode(session.profile_key, session.mode)
            self.events.put(("armed", session.session_id))
            return
        except Exception:
            write_log(traceback.format_exc())
            session.end_reason = "准备游戏会话时发生错误，详情见日志"
            session.end_error = True
        finally:
            if not session.hwnd or session.end_error or session.stop_event.is_set():
                self.events.put(("worker_finished", session.session_id))

    def activate_session(self, session):
        if not self.is_current(session) or session.stop_event.is_set():
            return
        self.status_var.set(f"{session.mode}模式：{session.title}")
        self.input_monitor.set_blocked_keys({self.config["正反馈键"], self.config["负反馈键"]})
        self.input_monitor.clear()
        target = self.ai_loop if session.mode == "AI" else self.human_loop
        session.thread = threading.Thread(target=target, args=(session,), daemon=True)
        session.thread.start()

    def stop_session(self, reason="已结束", error=False):
        with self.state_lock:
            session = self.active_session
            if session is None:
                return
            if session.stop_event.is_set():
                if error:
                    session.end_error = True
                    session.end_reason = reason
                return
            session.end_reason = reason
            session.end_error = error
            session.stop_event.set()
        self.status_var.set("正在结束当前会话…")
        self.release_session_inputs(session)

    def finalize_session(self, session):
        if session.episode_id:
            try:
                self.agent.end_episode(session.episode_id, session.total_reward, session.steps, session.end_reason)
            except Exception:
                write_log(traceback.format_exc())
        try:
            self.agent.flush()
        except Exception:
            write_log(traceback.format_exc())
        with self.state_lock:
            if self.active_session is not session:
                return
            self.active_session = None
        self.input_monitor.set_blocked_keys(set())
        self.status_var.set(session.end_reason)
        self.detail_var.set(
            f"人：示范；AI：学习与安全探索；{self.config['正反馈键']}/{self.config['负反馈键']}：正/负反馈；ESC：结束")
        self.set_buttons(True)
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(250, lambda: self.root.attributes("-topmost", False))
        if session.end_error:
            messagebox.showerror(APP_NAME, session.end_reason)

    def press_action(self, session, action):
        if user32.GetForegroundWindow() != session.hwnd:
            return False
        items = []
        for name in action.keys:
            items.append(keyboard_input(name, False))
        for button in action.mouse_buttons:
            down, _, data = MOUSE_FLAG_MAP[button]
            items.append(mouse_input(down, data))
        if action.mouse_dx or action.mouse_dy:
            steps = self.config["鼠标移动档位像素"]
            def movement(value):
                if not value:
                    return 0
                index = min(abs(value), len(steps)) - 1
                return (1 if value > 0 else -1) * steps[index]
            items.append(mouse_input(MOUSEEVENTF_MOVE, 0, movement(action.mouse_dx), movement(action.mouse_dy)))
        if action.wheel:
            items.append(mouse_input(MOUSEEVENTF_WHEEL, action.wheel * 120))
        try:
            with self.input_lock:
                send_inputs(items)
                session.held_keys.update(action.keys)
                session.held_buttons.update(action.mouse_buttons)
            return True
        except OSError as error:
            write_log(f"发送输入失败: {error}")
            self.release_session_inputs(session)
            return False

    def release_session_inputs(self, session, action=None):
        with self.input_lock:
            keys = list(session.held_keys if action is None else action.keys)
            buttons = list(session.held_buttons if action is None else action.mouse_buttons)
            items = []
            for name in reversed(keys):
                items.append(keyboard_input(name, True))
            for button in reversed(buttons):
                _, up, data = MOUSE_FLAG_MAP[button]
                items.append(mouse_input(up, data))
            try:
                send_inputs(items)
            except OSError as error:
                write_log(f"释放输入失败: {error}")
            for name in keys:
                session.held_keys.discard(name)
            for button in buttons:
                session.held_buttons.discard(button)

    def cursor_in_client(self, hwnd):
        x, y = current_cursor()
        point = wintypes.POINT(x, y)
        if user32.ScreenToClient(hwnd, ctypes.byref(point)):
            return point.x, point.y
        return 0, 0

    def split_feedback(self, events):
        positive = self.config["正反馈键"]
        negative = self.config["负反馈键"]
        feedback = 0
        filtered = []
        for event in events:
            if event.device == "keyboard" and event.code in (positive, negative):
                if event.event == "down":
                    feedback += 1 if event.code == positive else -1
                continue
            filtered.append(event)
        return filtered, max(-1, min(1, feedback))

    @staticmethod
    def quantize_mouse_delta(value):
        magnitude = abs(int(value))
        if magnitude < 3:
            return 0
        level = 1 if magnitude < 14 else 2 if magnitude < 48 else 3
        return level if value > 0 else -level

    def human_action(self, events, previous_cursor, current_cursor_position, down_times):
        keys_down = set()
        buttons_down = set()
        wheel = 0
        durations = []
        now_ns = time.perf_counter_ns()
        for event in events:
            key = (event.device, event.code)
            if event.event == "down":
                down_times.setdefault(key, event.time_ns)
                if event.device == "keyboard":
                    keys_down.add(event.code)
                elif event.device == "mouse":
                    buttons_down.add(event.code)
            elif event.event == "up":
                start = down_times.pop(key, None)
                if event.device == "keyboard":
                    keys_down.add(event.code)
                elif event.device == "mouse":
                    buttons_down.add(event.code)
                if start is not None:
                    durations.append((event.time_ns - start) / 1_000_000.0)
            elif event.event == "wheel":
                wheel += event.value
        pressed_keys, pressed_buttons = self.input_monitor.snapshot()
        pressed_keys.discard(self.config["正反馈键"])
        pressed_keys.discard(self.config["负反馈键"])
        keys_down.update(pressed_keys)
        buttons_down.update(pressed_buttons)
        for device, codes in (("keyboard", pressed_keys), ("mouse", pressed_buttons)):
            for code in codes:
                started = down_times.get((device, code))
                if started is not None:
                    durations.append((now_ns - started) / 1_000_000.0)
        dx = current_cursor_position[0] - previous_cursor[0]
        dy = current_cursor_position[1] - previous_cursor[1]
        mouse_dx = self.quantize_mouse_delta(dx)
        mouse_dy = self.quantize_mouse_delta(dy)
        durations.append(self.config["人类采样秒数"] * 1000.0)
        raw_hold = max(durations) if durations else 100.0
        hold_ms = min(self.config["动作时长毫秒"], key=lambda value: abs(value - raw_hold))
        return ActionSpec(tuple(keys_down), tuple(buttons_down), mouse_dx, mouse_dy,
                          1 if wheel > 0 else -1 if wheel < 0 else 0, hold_ms).normalized()

    def capture_state(self, session, capture, health, encoder, previous_action, audio):
        frame, size = capture.capture(session.hwnd)
        if frame is None:
            error = health.failure()
            return None, None, error, size
        error = health.observe(frame, size)
        if error:
            return None, None, error, size
        encoder.add(frame)
        mouse = self.cursor_in_client(session.hwnd)
        gamepad = self.xinput.snapshot() if self.config["启用手柄观察"] else (0,) * 9
        peak = audio.peak() if audio is not None and self.config["启用音频状态"] else 0.0
        bucket, feature = encoder.encode(previous_action, mouse, size, gamepad, peak)
        state_id = self.agent.resolve_state(session.profile_key, bucket, feature)
        return frame, state_id, None, size

    def human_loop(self, session):
        capture = GDICapture(self.config["采样宽度"], self.config["采样高度"])
        health = CaptureHealth(self.config)
        encoder = TemporalStateEncoder(self.config)
        audio = AudioPeakSampler() if self.config["启用音频状态"] else None
        reward_provider = RewardProvider(self.config, self.agent, session.profile_key)
        previous_frame = None
        previous_state = None
        previous_cursor = current_cursor()
        stuck_count = 0
        self.input_monitor.clear()
        down_times = {}
        try:
            while self.is_current(session) and not session.stop_event.is_set():
                if not valid_target_window(session.hwnd):
                    session.end_reason = "目标窗口已关闭"
                    break
                if user32.GetForegroundWindow() != session.hwnd:
                    previous_frame = None
                    previous_state = None
                    previous_cursor = current_cursor()
                    down_times.clear()
                    self.input_monitor.clear()
                    encoder.reset()
                    session.stop_event.wait(0.08)
                    continue
                if previous_frame is None:
                    previous_frame, previous_state, error, _ = self.capture_state(
                        session, capture, health, encoder, None, audio)
                    if error:
                        session.end_reason = error
                        session.end_error = True
                        break
                    if previous_frame is None:
                        session.stop_event.wait(0.04)
                        continue
                    previous_cursor = current_cursor()
                    self.input_monitor.clear()
                    if session.stop_event.wait(self.config["人类采样秒数"]):
                        break
                    continue
                events, human_feedback = self.split_feedback(self.input_monitor.drain())
                cursor_now = current_cursor()
                action_spec = self.human_action(events, previous_cursor, cursor_now, down_times)
                previous_cursor = cursor_now
                action_record = self.agent.register_human_action(session.profile_key, action_spec)
                frame, state_id, error, _ = self.capture_state(
                    session, capture, health, encoder, action_spec, audio)
                if error:
                    session.end_reason = error
                    session.end_error = True
                    break
                if frame is None:
                    session.stop_event.wait(0.04)
                    continue
                self.agent.demonstrate(session.profile_key, previous_state, action_record.id)
                change = frame_difference(previous_frame, frame)
                stuck_count = stuck_count + 1 if change < self.config["无变化阈值"] else 0
                reward, terminal, _ = reward_provider.calculate(
                    previous_frame, frame, previous_state, state_id, action_record.id, stuck_count,
                    human_feedback)
                self.agent.update(session.profile_key, previous_state, action_record.id,
                                  reward, state_id, terminal, "人")
                session.total_reward += reward
                session.steps += 1
                if terminal:
                    previous_frame = None
                    previous_state = None
                    encoder.reset()
                    stuck_count = 0
                else:
                    previous_frame = frame
                    previous_state = state_id
                if session.stop_event.wait(self.config["人类采样秒数"]):
                    break
        except Exception:
            write_log(traceback.format_exc())
            session.end_reason = "人类示范学习发生错误，详情见日志"
            session.end_error = True
        finally:
            capture.close()
            if audio is not None:
                audio.close()
            self.agent.metric(session.profile_key, "capture_fps", health.fps)
            self.agent.metric(session.profile_key, "capture_size_changes", health.size_changes)
            self.agent.flush()
            self.events.put(("worker_finished", session.session_id))

    def ai_loop(self, session):
        capture = GDICapture(self.config["采样宽度"], self.config["采样高度"])
        health = CaptureHealth(self.config)
        encoder = TemporalStateEncoder(self.config)
        audio = AudioPeakSampler() if self.config["启用音频状态"] else None
        reward_provider = RewardProvider(self.config, self.agent, session.profile_key)
        previous_frame = None
        previous_state = None
        previous_action = None
        stuck_count = 0
        try:
            while self.is_current(session) and not session.stop_event.is_set():
                if not valid_target_window(session.hwnd):
                    session.end_reason = "目标窗口已关闭"
                    break
                if user32.GetForegroundWindow() != session.hwnd:
                    self.release_session_inputs(session)
                    previous_frame = None
                    previous_state = None
                    previous_action = None
                    encoder.reset()
                    session.stop_event.wait(0.08)
                    continue
                if previous_frame is None:
                    previous_frame, previous_state, error, _ = self.capture_state(
                        session, capture, health, encoder, previous_action.spec if previous_action else None, audio)
                    if error:
                        session.end_reason = error
                        session.end_error = True
                        break
                    if previous_frame is None:
                        session.stop_event.wait(0.04)
                        continue
                action = self.agent.choose(session.profile_key, previous_state)
                if not self.press_action(session, action.spec):
                    session.end_reason = "无法向目标窗口发送输入。请检查权限级别和游戏是否允许自动化。"
                    session.end_error = True
                    break
                if session.stop_event.wait(action.spec.hold_ms / 1000.0):
                    self.release_session_inputs(session, action.spec)
                    break
                self.release_session_inputs(session, action.spec)
                if session.stop_event.wait(self.config["AI动作后等待秒数"]):
                    break
                _, human_feedback = self.split_feedback(self.input_monitor.drain())
                frame, state_id, error, _ = self.capture_state(session, capture, health, encoder, action.spec, audio)
                if error:
                    session.end_reason = error
                    session.end_error = True
                    break
                if frame is None:
                    previous_frame = None
                    previous_state = None
                    encoder.reset()
                    continue
                change = frame_difference(previous_frame, frame)
                stuck_count = stuck_count + 1 if change < self.config["无变化阈值"] else 0
                reward, terminal, _ = reward_provider.calculate(
                    previous_frame, frame, previous_state, state_id, action.id, stuck_count,
                    human_feedback)
                self.agent.update(session.profile_key, previous_state, action.id, reward, state_id, terminal, "AI")
                session.total_reward += reward
                session.steps += 1
                if terminal:
                    previous_frame = None
                    previous_state = None
                    previous_action = None
                    encoder.reset()
                    stuck_count = 0
                else:
                    previous_frame = frame
                    previous_state = state_id
                    previous_action = action
        except Exception:
            write_log(traceback.format_exc())
            session.end_reason = "AI 运行时发生错误，详情见日志"
            session.end_error = True
        finally:
            self.release_session_inputs(session)
            capture.close()
            if audio is not None:
                audio.close()
            self.agent.metric(session.profile_key, "capture_fps", health.fps)
            self.agent.metric(session.profile_key, "capture_size_changes", health.size_changes)
            self.agent.flush()
            self.events.put(("worker_finished", session.session_id))

    def escape_watch_loop(self):
        previous_down = False
        while not self.closed:
            down = bool(user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000)
            with self.state_lock:
                session = self.active_session
            if session is not None and down and not previous_down:
                self.events.put(("stop", session.session_id, "已按 ESC 结束", False))
            previous_down = down
            time.sleep(0.02)

    def process_events(self):
        while True:
            try:
                item = self.events.get_nowait()
            except queue.Empty:
                break
            kind = item[0]
            with self.state_lock:
                session = self.active_session
            if session is None:
                continue
            if item[1] != session.session_id:
                continue
            if kind == "armed":
                self.activate_session(session)
            elif kind == "stop":
                self.stop_session(item[2], item[3])
            elif kind == "worker_finished":
                self.finalize_session(session)
        if not self.closed:
            self.root.after(50, self.process_events)

    def close(self):
        self.closed = True
        with self.state_lock:
            session = self.active_session
        if session:
            session.stop_event.set()
            self.release_session_inputs(session)
        self.input_monitor.set_blocked_keys(set())
        self.input_monitor.close()
        worker_alive = False
        if session and session.thread and session.thread.is_alive():
            session.thread.join(timeout=1.5)
            worker_alive = session.thread.is_alive()
        try:
            self.agent.flush()
            if not worker_alive:
                self.agent.close()
        except Exception:
            pass
        self.root.destroy()


def enable_dpi_awareness():
    try:
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError, OSError):
        try:
            user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def run():
    if os.name != "nt" or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("本程序仅支持 Windows x64")
    enable_dpi_awareness()
    if relocate():
        return
    mutex = ensure_single_instance()
    if mutex is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(APP_NAME, "AnyGameAI 已经在运行")
        root.destroy()
        return
    config = load_config()
    root = tk.Tk()
    AnyGameAI(root, config)
    try:
        root.mainloop()
    finally:
        kernel32.CloseHandle(mutex)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        error_text = traceback.format_exc()
        try:
            write_log(error_text)
        except Exception:
            pass
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(APP_NAME, error_text)
            root.destroy()
        except Exception:
            pass
