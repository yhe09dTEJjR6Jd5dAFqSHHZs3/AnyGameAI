from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import atexit
import ast
import base64
import csv
import ctypes
import hashlib
import hmac
import heapq
import importlib
import json
import math
import os
import platform
import queue
import random
import re
import shutil
import sqlite3
import subprocess
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from collections import deque
from ctypes import wintypes
from datetime import datetime
from pathlib import Path, PurePosixPath

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:
    tk = None
    messagebox = None


APP_NAME = "AnyGameAI"
APP_VERSION = "67.0"
SCRIPT_NAME = "AnyGameAI.py"
RELEASE_SOURCE_SHA256 = "7df96b72a559bb7ff5509a09395a360390ead9fd3ea2dc2358d0818ee655ac28"
REQUIRED_PYTHON_VERSION = (3, 12)
MIN_WINDOWS_11_BUILD = 22000
SUPPORTED_X64_MACHINES = frozenset({"amd64", "x86_64"})
APP_SCHEMA = 11
CONFIG_SCHEMA = 28
PROFILE_SCHEMA = 20
MODEL_SCHEMA = 11
FEATURE_WIDTH = 40
FEATURE_HEIGHT = 24
COLOR_WIDTH = FEATURE_WIDTH // 2
COLOR_HEIGHT = FEATURE_HEIGHT // 2
COLOR_PIXELS = COLOR_WIDTH * COLOR_HEIGHT
LEGACY_FEATURE_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 2
V27_FEATURE_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 3
COLOR_FEATURE_DIM = COLOR_PIXELS * 2
FEATURE_DIM = V27_FEATURE_DIM + COLOR_FEATURE_DIM
MODEL_PIXEL_CHANNELS = 4
MODEL_GLOBAL_FEATURES = 72
V27_MODEL_INPUT_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * MODEL_PIXEL_CHANNELS + MODEL_GLOBAL_FEATURES
MODEL_INPUT_DIM = V27_MODEL_INPUT_DIM + COLOR_FEATURE_DIM
LEGACY_MODEL_INPUT_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 3 + MODEL_GLOBAL_FEATURES
MAX_COMPRESSED_FEATURE_BYTES = FEATURE_DIM * 2 + 256
DEFAULT_HIDDEN_SIZE = 192
TARGET_NETWORK_SYNC_STEPS_DEFAULT = 128
TARGET_NETWORK_SOFT_UPDATE_DEFAULT = 0.12
TARGET_ENSEMBLE_WEIGHT_DEFAULT = 0.28
MODEL_UNCERTAINTY_WEIGHT_DEFAULT = 0.14
ONLINE_REPRESENTATION_SCALE_DEFAULT = 0.08
ONLINE_INPUT_ADAPTATION_SCALE_DEFAULT = 0.16
ONLINE_INPUT_ADAPTATION_FEATURES_DEFAULT = 96
TARGET_WAIT_SECONDS = None
TARGET_GRACE_SECONDS = 1.0
SHUTDOWN_GRACE_SECONDS = 6.0
SHUTDOWN_POLL_MILLISECONDS = 50
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
CAPTURE_FAILURE_TIMEOUT_DEFAULT = 60.0
MOUSE_GRID_WIDTH = 32
MOUSE_GRID_HEIGHT = 18
INTEGRITY_SCHEMA = 4
RUNTIME_INTEGRITY_SCHEMA = 2
GLOBAL_PRIOR_SCHEMA = 11
NUMPY_REQUIREMENT = "numpy>=1.26,<3"
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
PYPI_NUMPY_JSON_URL = "https://pypi.org/pypi/numpy/json"
PYPI_INDEX_HOST = "pypi.org"
PYPI_FILE_HOST = "files.pythonhosted.org"
MAX_WHEEL_BYTES = 160 * 1024 * 1024
MAX_WHEEL_EXPANDED_BYTES = 768 * 1024 * 1024
MAX_WHEEL_MEMBERS = 50_000
MAX_SCRIPT_BYTES = 8 * 1024 * 1024
MIN_SCRIPT_BYTES = 256 * 1024
MAX_DISTRIBUTION_RECORDS = 20_000
MAX_RUNTIME_TREE_FILES = 30_000
MAX_RUNTIME_TREE_BYTES = MAX_WHEEL_EXPANDED_BYTES
MAX_PROCESS_OUTPUT_CHARS = 2 * 1024 * 1024
MAX_PROCESS_OUTPUT_QUEUE_LINES = 4096
MAX_LOG_BYTES = 4 * 1024 * 1024
MAX_SMALL_JSON_BYTES = 1024 * 1024
MAX_INDEX_JSON_BYTES = 32 * 1024 * 1024
MAX_PROFILE_JSON_BYTES = 64 * 1024 * 1024
MAX_MODEL_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MODEL_EXPANDED_BYTES = 192 * 1024 * 1024
MAX_MODEL_ARCHIVE_MEMBERS = 64
TRAINING_MEMMAP_THRESHOLD_BYTES = 320 * 1024 * 1024
GLOBAL_TRAINING_SAMPLE_LIMIT = 40_000
GLOBAL_TRAINING_MIN_PER_PROFILE = 16
POLICY_AVOIDANCE_WEIGHT = 0.30
CORRUPT_BACKUP_LIMIT = 3
UNIVERSAL_ACTION_SCHEMA = 11
UNIVERSAL_ACTION_LIMIT = 256
DELAYED_REWARD_HORIZON_DEFAULT = 6
DELAYED_REWARD_DISCOUNT_DEFAULT = 0.82
CONTROL_KINDS = ("idle", "keyboard", "pointer", "click", "wheel", "mixed")
SCENE_CONTEXTS = ("static_ui", "dynamic_world", "scrolling", "dark_scene", "mixed_scene")
COLD_START_PROBE_LIMIT = 24
STATE_MEMORY_BUCKET_BITS = 8
STATE_MEMORY_APPROXIMATE_DISTANCE = 11
STATE_MEMORY_BUCKET_LIMIT = 512
HUMAN_ACTION_MEMORY_LIMIT = 30_000
HUMAN_ACTION_MEMORY_WEIGHT = 0.52
HUMAN_ACTION_APPROXIMATE_WEIGHT = 0.24
PAIR_TRANSITION_LIMIT = 4096
PAIR_TRANSITION_NEXT_LIMIT = 64
CROSS_GAME_ACTION_PRIOR_LIMIT = 1024
VERSION_PATTERN = re.compile(r'^APP_VERSION\s*=\s*["\'](\d+(?:\.\d+)*)["\']', re.MULTILINE)
RELEASE_SOURCE_PATTERN = re.compile(
    r'^(?P<prefix>RELEASE_SOURCE_SHA256\s*=\s*)(?P<quote>["\'])'
    r'(?P<digest>[0-9a-f]{64})(?P=quote)(?P<suffix>\s*)$',
    re.MULTILINE,
)
STATE_MEMORY_KEY_PATTERN = re.compile(r"[0-9a-f]{8}:[0-9a-f]:[0-7]\Z")
MODEL_ARCHIVE_REQUIRED_MEMBERS = frozenset({
    "schema.npy", "input_dim.npy", "hidden_size.npy", "hidden2_size.npy",
    "output_size.npy", "w1.npy", "b1.npy", "w2.npy", "b2.npy",
    "wp.npy", "bp.npy", "wv.npy", "bv.npy", "trained_samples.npy",
    "training_rounds.npy", "action_hash.npy",
})
MODEL_ARCHIVE_ALLOWED_MEMBERS = MODEL_ARCHIVE_REQUIRED_MEMBERS | frozenset({
    "online_updates.npy", "action_signatures.npy", "updated_at.npy",
})
GLOBAL_ARCHIVE_REQUIRED_MEMBERS = frozenset({
    "schema.npy", "input_dim.npy", "hidden_size.npy", "hidden2_size.npy",
    "w1.npy", "b1.npy", "w2.npy", "b2.npy", "action_signatures.npy",
    "wp.npy", "bp.npy", "wv.npy", "bv.npy", "trained_samples.npy",
    "training_rounds.npy", "source_profile.npy",
})
GLOBAL_ARCHIVE_ALLOWED_MEMBERS = GLOBAL_ARCHIVE_REQUIRED_MEMBERS | frozenset({
    "updated_at.npy",
})
PROTECTED_TARGET_EXECUTABLES = {
    "explorer", "taskmgr", "regedit", "mmc", "cmd", "powershell", "pwsh",
    "wt", "windowsterminal", "conhost", "msiexec", "systemsettings", "control",
    "securityhealthservice", "securityhealthsystray", "lockapp", "logonui",
    "consent", "useraccountcontrolsettings",
}
PROTECTED_TARGET_CLASSES = {"Shell_TrayWnd", "Shell_SecondaryTrayWnd", "Progman", "WorkerW"}
WINDOWS_RESERVED_DEVICE_NAMES = frozenset({
    "con", "prn", "aux", "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
})
BROWSER_HOST_EXECUTABLES = frozenset({"chrome", "msedge", "firefox", "brave", "opera", "vivaldi"})
HOST_EXECUTABLES = frozenset({
    *BROWSER_HOST_EXECUTABLES,
    "retroarch", "pcsx2", "rpcs3", "dolphin", "dolphin-emu", "mame",
    "cemu", "yuzu", "ryujinx", "xenia", "ppssppwindows64",
    "java", "javaw", "python", "pythonw", "electron", "nw", "nwjs",
    "applicationframehost", "wwahost",
})
BROWSER_BLOCKED_CTRL_KEYS = frozenset({
    0x08, 0x09, 0x21, 0x22, 0x24, 0x25, 0x27,
    *range(0x30, 0x3A),
    0x41, 0x44, 0x46, 0x48, 0x4A, 0x4C, 0x4E, 0x4F, 0x50, 0x52, 0x53, 0x54, 0x55, 0x57,
})
SYSTEM_BLOCKED_KEY_COMBINATIONS = (
    frozenset({0x12, 0x09}),  # Alt+Tab
    frozenset({0x12, 0x20}),  # Alt+Space
    frozenset({0x12, 0x73}),  # Alt+F4
    frozenset({0x11, 0x12, 0x2E}),  # Ctrl+Alt+Delete
)
REQUIRED_SCRIPT_FUNCTIONS = frozenset({
    "main", "ensure_files", "record_human_session", "train_all_profiles",
    "run_ai_session", "runtime_self_check", "repair_main_script", "ensure_core_ready",
    "train_model", "temporal_policy_blend", "clip_gradients_by_global_norm",
    "clone_target_model", "soft_update_target_model",
    "model_ensemble_outputs", "masked_policy_weights",
    "adaptive_runtime_settings", "runtime_numeric_thread_budget",
    "load_human_action_memory", "save_human_action_memory",
    "human_action_memory_biases", "read_json_file", "validate_npz_archive",
    "training_vector_cache_limit", "adaptive_exploration_rate",
})
REQUIRED_APP_METHODS = frozenset({
    "file_mode", "human_mode", "upgrade_mode", "ai_mode", "on_escape",
})
REQUIRED_NATIVE_APP_METHODS = frozenset({
    "file_mode", "human_mode", "upgrade_mode", "ai_mode", "on_escape",
    "stop_and_close", "run_worker", "poll_worker", "worker_done", "run",
})
REQUIRED_SCRIPT_CALLS = {
    "main": frozenset({
        "configure_runtime_environment", "bootstrap_to_desktop",
        "AnyGameAIApp", "NativeAnyGameAIApp",
    }),
    "ensure_files": frozenset({
        "repair_main_script", "ensure_numpy", "runtime_self_check", "repair_profile",
        "verify_main_script_integrity",
    }),
    "ensure_runtime_ready": frozenset({
        "ensure_core_ready", "ensure_numpy", "import_numpy", "runtime_self_check",
    }),
    "record_human_session": frozenset({
        "ensure_core_ready", "profile_identity", "observe_human_action",
        "update_human_action_memory", "save_human_action_memory",
        "adaptive_runtime_settings",
    }),
    "train_all_profiles": frozenset({"ensure_runtime_ready", "train_model", "refresh_global_prior"}),
    "run_ai_session": frozenset({
        "ensure_runtime_ready", "profile_identity", "execute_action", "temporal_policy_blend",
        "load_human_action_memory", "human_action_memory_biases",
        "clone_target_model", "soft_update_target_model", "model_ensemble_outputs",
        "adaptive_exploration_rate", "adaptive_runtime_settings",
    }),
    "train_model": frozenset({"clip_gradients_by_global_norm"}),
    "load_training_data": frozenset({"training_vector_cache_limit"}),
    "online_model_update": frozenset({"temporal_difference_target"}),
    "configure_runtime_environment": frozenset({"runtime_numeric_thread_budget"}),
}
REQUIRED_APP_CALLS = {
    "__init__": frozenset({"file_mode", "human_mode", "upgrade_mode", "ai_mode", "poll_worker"}),
    "file_mode": frozenset({"ensure_files", "run_worker"}),
    "human_mode": frozenset({"wait_for_target_window", "record_human_session", "run_worker"}),
    "upgrade_mode": frozenset({"train_all_profiles", "run_worker"}),
    "ai_mode": frozenset({"wait_for_target_window", "run_ai_session", "run_worker"}),
    "on_escape": frozenset({"stop_and_close"}),
    "worker_done": frozenset({"stop_and_close"}),
}
REQUIRED_NATIVE_APP_CALLS = {
    "file_mode": frozenset({"ensure_files", "run_worker"}),
    "human_mode": frozenset({"wait_for_target_window", "record_human_session", "run_worker"}),
    "upgrade_mode": frozenset({"train_all_profiles", "run_worker"}),
    "ai_mode": frozenset({"wait_for_target_window", "run_ai_session", "run_worker"}),
    "on_escape": frozenset({"stop_and_close"}),
    "worker_done": frozenset({"stop_and_close"}),
}
REQUIRED_APP_ATTRIBUTES = frozenset({"file_button", "human_button", "upgrade_button", "ai_button"})
STRICT_UI_ACTIONS = ("文件", "人", "升级", "AI")
STRICT_UI_BUTTON_ATTRIBUTES = ("file_button", "human_button", "upgrade_button", "ai_button")
STRICT_UI_MODE_METHODS = ("file_mode", "human_mode", "upgrade_mode", "ai_mode")
LOG_LOCK = threading.RLock()
ACTIVE_PROCESS_LOCK = threading.RLock()
ACTIVE_PROCESSES: set[subprocess.Popen] = set()
SOURCE_SCRIPT_PATH = Path(__file__).resolve()


def desktop_dir() -> Path:
    if os.name == "nt":
        try:
            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", wintypes.DWORD),
                    ("Data2", wintypes.WORD),
                    ("Data3", wintypes.WORD),
                    ("Data4", ctypes.c_ubyte * 8),
                ]

            folder_id = GUID(
                0xB4BFCC3A,
                0xDB2C,
                0x424C,
                (ctypes.c_ubyte * 8)(0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41),
            )
            raw_path = ctypes.c_void_p()
            known_folder = ctypes.windll.shell32.SHGetKnownFolderPath
            known_folder.argtypes = [
                ctypes.POINTER(GUID),
                wintypes.DWORD,
                wintypes.HANDLE,
                ctypes.POINTER(ctypes.c_void_p),
            ]
            known_folder.restype = ctypes.c_long
            result = known_folder(ctypes.byref(folder_id), 0, None, ctypes.byref(raw_path))
            try:
                if result == 0 and raw_path.value:
                    return Path(ctypes.wstring_at(raw_path.value))
            finally:
                if raw_path.value:
                    free_memory = ctypes.windll.ole32.CoTaskMemFree
                    free_memory.argtypes = [ctypes.c_void_p]
                    free_memory.restype = None
                    free_memory(raw_path)
        except Exception:
            pass
        try:
            buffer = ctypes.create_unicode_buffer(32768)
            result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buffer)
            if result == 0 and buffer.value:
                return Path(buffer.value)
        except Exception:
            pass
        user_profile = os.environ.get("USERPROFILE", "").strip()
        if user_profile:
            return Path(user_profile) / "Desktop"
    return Path.home() / "Desktop"


def windows_build_number() -> int:
    if os.name != "nt":
        return 0
    try:
        class RTL_OSVERSIONINFOW(ctypes.Structure):
            _fields_ = [
                ("dwOSVersionInfoSize", wintypes.DWORD),
                ("dwMajorVersion", wintypes.DWORD),
                ("dwMinorVersion", wintypes.DWORD),
                ("dwBuildNumber", wintypes.DWORD),
                ("dwPlatformId", wintypes.DWORD),
                ("szCSDVersion", wintypes.WCHAR * 128),
            ]

        version = RTL_OSVERSIONINFOW()
        version.dwOSVersionInfoSize = ctypes.sizeof(version)
        rtl_get_version = ctypes.windll.ntdll.RtlGetVersion
        rtl_get_version.argtypes = [ctypes.POINTER(RTL_OSVERSIONINFOW)]
        rtl_get_version.restype = wintypes.LONG
        if rtl_get_version(ctypes.byref(version)) == 0:
            return int(version.dwBuildNumber)
    except Exception:
        pass
    try:
        return int(sys.getwindowsversion().build)
    except Exception:
        return 0


def available_physical_memory_bytes() -> int:
    if os.name != "nt":
        return 0
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", wintypes.DWORD),
                ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return max(0, int(status.ullAvailPhys))
    except Exception:
        pass
    return 0


def adaptive_training_settings(
    config: dict,
    available_memory_bytes: int | None = None,
    cpu_count: int | None = None,
) -> dict[str, int]:
    experience_limit = max(1000, int(config.get("experience_limit_per_game", 1000)))
    sample_limit = max(
        100,
        min(experience_limit, int(config.get("train_sample_limit_per_game", 100))),
    )
    epochs = max(1, int(config.get("training_epochs", 1)))
    batch_size = max(8, int(config.get("training_batch_size", 8)))
    memory = (
        available_physical_memory_bytes()
        if available_memory_bytes is None
        else max(0, int(available_memory_bytes))
    )
    processors = max(
        1,
        int(os.cpu_count() or 1) if cpu_count is None else int(cpu_count),
    )
    gib = 1024 ** 3
    if memory and memory < 768 * 1024 ** 2:
        sample_limit = min(sample_limit, 2500)
        epochs = min(epochs, 4)
        batch_size = min(batch_size, 32)
    elif memory and memory < 1536 * 1024 ** 2:
        sample_limit = min(sample_limit, 6000)
        epochs = min(epochs, 6)
        batch_size = min(batch_size, 64)
    elif memory and memory < 3 * gib:
        sample_limit = min(sample_limit, 10000)
        epochs = min(epochs, 8)
        batch_size = min(batch_size, 96)
    elif memory >= 24 * gib and processors >= 16:
        sample_limit = min(experience_limit, max(sample_limit, min(48000, sample_limit * 3)))
        epochs = max(epochs, min(20, epochs + 6))
        batch_size = max(batch_size, min(512, batch_size * 3))
    elif memory >= 12 * gib and processors >= 12:
        sample_limit = min(experience_limit, max(sample_limit, min(32000, sample_limit * 2)))
        epochs = max(epochs, min(18, epochs + 4))
        batch_size = max(batch_size, min(384, batch_size * 2))
    elif memory >= 6 * gib and processors >= 8:
        sample_limit = min(experience_limit, max(sample_limit, min(24000, sample_limit * 3 // 2)))
        epochs = max(epochs, min(14, epochs + 2))
        batch_size = max(batch_size, min(256, batch_size * 2))
    sample_limit = max(100, min(experience_limit, sample_limit))
    epochs = max(1, min(1000, epochs))
    batch_size = max(8, min(8192, batch_size))
    return {"sample_limit": sample_limit, "epochs": epochs, "batch_size": batch_size}


def runtime_numeric_thread_budget(
    available_memory_bytes: int | None = None,
    cpu_count: int | None = None,
) -> int:
    memory = (
        available_physical_memory_bytes()
        if available_memory_bytes is None
        else max(0, int(available_memory_bytes))
    )
    processors = max(
        1,
        int(os.cpu_count() or 1) if cpu_count is None else int(cpu_count),
    )
    gib = 1024 ** 3
    if processors <= 2 or (memory and memory < gib):
        return 1
    if processors <= 6 or (memory and memory < 3 * gib):
        return 2
    if processors <= 10 or (memory and memory < 8 * gib):
        return 3
    return 4


def adaptive_runtime_settings(
    config: dict,
    available_memory_bytes: int | None = None,
    cpu_count: int | None = None,
) -> dict[str, int | float]:
    memory = (
        available_physical_memory_bytes()
        if available_memory_bytes is None
        else max(0, int(available_memory_bytes))
    )
    processors = max(
        1,
        int(os.cpu_count() or 1) if cpu_count is None else int(cpu_count),
    )
    gib = 1024 ** 3
    sample_interval = max(0.02, min(1.0, float(config.get("sample_interval_seconds", 0.070))))
    step_pause = max(0.0, min(2.0, float(config.get("step_pause_seconds", 0.025))))
    confirmation_delay = max(
        0.0,
        min(0.25, float(config.get("confirmation_delay_seconds", 0.035))),
    )
    planning_horizon = max(1, min(6, int(config.get("planning_horizon", 4))))
    planning_refresh_steps = max(8, min(512, int(config.get("planning_refresh_steps", 48))))
    online_checkpoint_steps = max(32, min(10000, int(config.get("online_checkpoint_steps", 256))))
    translation_search_radius = max(1, min(4, int(config.get("translation_search_radius", 2))))

    if processors <= 2 or (memory and memory < 768 * 1024 ** 2):
        sample_interval = max(sample_interval, 0.100)
        step_pause = max(step_pause, 0.040)
        confirmation_delay = min(confirmation_delay, 0.025)
        planning_horizon = min(planning_horizon, 3)
        planning_refresh_steps = max(planning_refresh_steps, 96)
        online_checkpoint_steps = max(online_checkpoint_steps, 512)
        translation_search_radius = min(translation_search_radius, 1)
    elif processors <= 4 or (memory and memory < 2 * gib):
        sample_interval = max(sample_interval, 0.085)
        step_pause = max(step_pause, 0.032)
        confirmation_delay = min(confirmation_delay, 0.030)
        planning_horizon = min(planning_horizon, 3)
        planning_refresh_steps = max(planning_refresh_steps, 64)
        online_checkpoint_steps = max(online_checkpoint_steps, 384)
        translation_search_radius = min(translation_search_radius, 2)
    elif memory >= 16 * gib and processors >= 12:
        sample_interval = min(sample_interval, 0.055)
        step_pause = min(step_pause, 0.018)
        planning_horizon = max(planning_horizon, 5)
        planning_refresh_steps = min(planning_refresh_steps, 32)
        online_checkpoint_steps = min(online_checkpoint_steps, 192)
        translation_search_radius = max(translation_search_radius, 3)
    elif memory >= 8 * gib and processors >= 8:
        sample_interval = min(sample_interval, 0.060)
        step_pause = min(step_pause, 0.022)
        planning_horizon = max(planning_horizon, 4)
        planning_refresh_steps = min(planning_refresh_steps, 40)
        online_checkpoint_steps = min(online_checkpoint_steps, 224)
        translation_search_radius = max(translation_search_radius, 2)

    return {
        "sample_interval_seconds": max(0.02, min(1.0, sample_interval)),
        "step_pause_seconds": max(0.0, min(2.0, step_pause)),
        "confirmation_delay_seconds": max(0.0, min(0.25, confirmation_delay)),
        "planning_horizon": max(1, min(6, planning_horizon)),
        "planning_refresh_steps": max(8, min(512, planning_refresh_steps)),
        "online_checkpoint_steps": max(32, min(10000, online_checkpoint_steps)),
        "translation_search_radius": max(1, min(4, translation_search_radius)),
    }


def training_vector_cache_limit(
    sample_count: int,
    available_memory_bytes: int | None = None,
) -> int:
    samples = max(0, int(sample_count))
    memory = (
        available_physical_memory_bytes()
        if available_memory_bytes is None
        else max(0, int(available_memory_bytes))
    )
    gib = 1024 ** 3
    if memory and memory < 768 * 1024 ** 2:
        hardware_limit = 96
    elif memory and memory < 1536 * 1024 ** 2:
        hardware_limit = 256
    elif memory and memory < 3 * gib:
        hardware_limit = 768
    elif memory and memory < 6 * gib:
        hardware_limit = 1536
    elif memory and memory < 12 * gib:
        hardware_limit = 3072
    elif memory:
        hardware_limit = 8192
    else:
        hardware_limit = 1024
    useful_limit = max(64, min(8192, samples // 3 if samples >= 192 else samples))
    return max(0, min(samples, hardware_limit, useful_limit))


def adaptive_global_training_settings(
    config: dict,
    profile_count: int,
    available_memory_bytes: int | None = None,
    cpu_count: int | None = None,
) -> dict[str, int]:
    profiles = max(1, int(profile_count))
    local = adaptive_training_settings(config, available_memory_bytes, cpu_count)
    memory = (
        available_physical_memory_bytes()
        if available_memory_bytes is None
        else max(0, int(available_memory_bytes))
    )
    processors = max(
        1,
        int(os.cpu_count() or 1) if cpu_count is None else int(cpu_count),
    )
    gib = 1024 ** 3
    if memory and memory < 768 * 1024 ** 2:
        hardware_limit = 768
    elif memory and memory < 1536 * 1024 ** 2:
        hardware_limit = 1500
    elif memory and memory < 3 * gib:
        hardware_limit = 3000
    elif memory and memory < 6 * gib:
        hardware_limit = 6000
    elif memory and memory < 12 * gib:
        hardware_limit = 10_000
    elif memory and memory < 24 * gib:
        hardware_limit = 18_000
    elif memory:
        hardware_limit = GLOBAL_TRAINING_SAMPLE_LIMIT
    else:
        hardware_limit = 8000
    if processors <= 2:
        hardware_limit = min(hardware_limit, 2500)
    elif processors <= 4:
        hardware_limit = min(hardware_limit, 6000)
    requested = max(512, min(GLOBAL_TRAINING_SAMPLE_LIMIT, int(local["sample_limit"]) * 2))
    sample_limit = max(256, min(requested, hardware_limit))
    per_profile_limit = max(
        GLOBAL_TRAINING_MIN_PER_PROFILE,
        min(int(local["sample_limit"]), math.ceil(sample_limit / profiles)),
    )
    return {
        "sample_limit": int(sample_limit),
        "per_profile_limit": int(per_profile_limit),
        "epochs": max(2, min(int(local["epochs"]), max(3, int(local["epochs"]) // 2))),
        "batch_size": int(local["batch_size"]),
    }


APP_DIR = desktop_dir() / APP_NAME
LOCAL_SCRIPT_PATH = APP_DIR / SCRIPT_NAME
CONFIG_PATH = APP_DIR / "config.json"
INDEX_PATH = APP_DIR / "profiles.json"
LOG_PATH = APP_DIR / "AnyGameAI.log"
INTEGRITY_PATH = APP_DIR / "integrity.json"
RUNTIME_INTEGRITY_PATH = APP_DIR / "runtime_integrity.json"
BACKUP_DIR = APP_DIR / "backup"
BACKUP_SCRIPT_PATH = BACKUP_DIR / SCRIPT_NAME
RUNTIME_DIR = APP_DIR / "runtime"
SITE_PACKAGES = RUNTIME_DIR / "site-packages"
TEMP_DIR = RUNTIME_DIR / "temp"
PROFILES_DIR = APP_DIR / "profiles"
GLOBAL_PRIOR_PATH = APP_DIR / "global_prior.npz"

DEFAULT_CONFIG = {
    "schema": CONFIG_SCHEMA,
    "sample_interval_seconds": 0.070,
    "action_hold_seconds": 0.075,
    "step_pause_seconds": 0.025,
    "exploration": 0.07,
    "mouse_step_pixels": 24,
    "max_action_count": 384,
    "experience_limit_per_game": 90000,
    "train_sample_limit_per_game": 16000,
    "training_epochs": 10,
    "training_batch_size": 128,
    "learning_rate": 0.0015,
    "hidden_size": DEFAULT_HIDDEN_SIZE,
    "zero_shot_exploration": 0.26,
    "transfer_action_limit": 64,
    "delayed_reward_horizon": DELAYED_REWARD_HORIZON_DEFAULT,
    "delayed_reward_discount": DELAYED_REWARD_DISCOUNT_DEFAULT,
    "online_state_value_weight": 0.34,
    "state_memory_limit_per_game": 40000,
    "state_memory_weight": 0.45,
    "approximate_state_memory_weight": 0.24,
    "online_learning_rate": 0.16,
    "online_model_learning_rate": 0.0006,
    "online_td_discount": 0.72,
    "target_network_sync_steps": TARGET_NETWORK_SYNC_STEPS_DEFAULT,
    "target_network_soft_update": TARGET_NETWORK_SOFT_UPDATE_DEFAULT,
    "target_ensemble_weight": TARGET_ENSEMBLE_WEIGHT_DEFAULT,
    "model_uncertainty_weight": MODEL_UNCERTAINTY_WEIGHT_DEFAULT,
    "stuck_recovery_threshold": 7,
    "transition_novelty_weight": 0.18,
    "action_effect_weight": 0.24,
    "action_risk_weight": 0.38,
    "failure_cooldown_steps": 7,
    "world_progress_weight": 0.16,
    "cycle_penalty_weight": 0.30,
    "confirmation_delay_seconds": 0.035,
    "online_checkpoint_steps": 256,
    "sequence_prior_weight": 0.45,
    "planning_horizon": 4,
    "planning_discount": 0.68,
    "planning_weight": 0.28,
    "planning_refresh_steps": 48,
    "cross_game_control_weight": 0.35,
    "cross_game_scene_weight": 0.38,
    "cross_game_action_weight": 0.32,
    "scene_action_memory_weight": 0.30,
    "contextual_probe_weight": 0.55,
    "persistent_novelty_weight": 0.12,
    "successful_transition_threshold": 0.08,
    "adaptive_hold_strength": 0.35,
    "spatial_progress_weight": 0.22,
    "translation_search_radius": 2,
    "action_diversity_weight": 0.16,
    "fade_penalty_weight": 0.22,
    "scene_strategy_weight": 0.34,
    "color_progress_weight": 0.12,
    "persistent_frontier_reward_weight": 0.16,
    "state_bootstrap_weight": 0.22,
    "capture_failure_timeout_seconds": CAPTURE_FAILURE_TIMEOUT_DEFAULT,
    "database_integrity_scan_limit": 120000,
    "target_reacquire_seconds": 4.0,
}

DEFAULT_INDEX = {"schema": APP_SCHEMA, "profiles": {}}

PROFILE_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,80}\Z")
CONFIG_RANGES = {
    "sample_interval_seconds": (0.02, 1.0),
    "action_hold_seconds": (0.01, 1.0),
    "step_pause_seconds": (0.0, 2.0),
    "exploration": (0.0, 1.0),
    "mouse_step_pixels": (1, 1000),
    "max_action_count": (8, 1024),
    "experience_limit_per_game": (1000, 10_000_000),
    "train_sample_limit_per_game": (100, 1_000_000),
    "training_epochs": (1, 1000),
    "training_batch_size": (8, 8192),
    "learning_rate": (0.000001, 1.0),
    "hidden_size": (8, 2048),
    "zero_shot_exploration": (0.0, 1.0),
    "transfer_action_limit": (0, 256),
    "delayed_reward_horizon": (1, 24),
    "delayed_reward_discount": (0.1, 0.99),
    "online_state_value_weight": (0.0, 1.0),
    "state_memory_limit_per_game": (1000, 500_000),
    "state_memory_weight": (0.0, 1.0),
    "approximate_state_memory_weight": (0.0, 1.0),
    "online_learning_rate": (0.01, 1.0),
    "online_model_learning_rate": (0.0, 0.02),
    "online_td_discount": (0.0, 0.95),
    "target_network_sync_steps": (16, 4096),
    "target_network_soft_update": (0.01, 1.0),
    "target_ensemble_weight": (0.0, 0.5),
    "model_uncertainty_weight": (0.0, 0.5),
    "stuck_recovery_threshold": (3, 30),
    "transition_novelty_weight": (0.0, 1.0),
    "action_effect_weight": (0.0, 1.0),
    "action_risk_weight": (0.0, 1.0),
    "failure_cooldown_steps": (0, 60),
    "world_progress_weight": (0.0, 1.0),
    "cycle_penalty_weight": (0.0, 1.0),
    "confirmation_delay_seconds": (0.0, 0.25),
    "online_checkpoint_steps": (32, 10000),
    "sequence_prior_weight": (0.0, 1.0),
    "planning_horizon": (1, 6),
    "planning_discount": (0.1, 0.95),
    "planning_weight": (0.0, 1.0),
    "planning_refresh_steps": (8, 512),
    "cross_game_control_weight": (0.0, 1.0),
    "cross_game_scene_weight": (0.0, 1.0),
    "cross_game_action_weight": (0.0, 1.0),
    "scene_action_memory_weight": (0.0, 1.0),
    "contextual_probe_weight": (0.0, 1.0),
    "persistent_novelty_weight": (0.0, 1.0),
    "successful_transition_threshold": (-1.0, 1.0),
    "adaptive_hold_strength": (0.0, 1.0),
    "spatial_progress_weight": (0.0, 1.0),
    "translation_search_radius": (1, 4),
    "action_diversity_weight": (0.0, 1.0),
    "fade_penalty_weight": (0.0, 1.0),
    "scene_strategy_weight": (0.0, 1.0),
    "color_progress_weight": (0.0, 1.0),
    "persistent_frontier_reward_weight": (0.0, 1.0),
    "state_bootstrap_weight": (0.0, 0.75),
    "capture_failure_timeout_seconds": (10.0, 300.0),
    "database_integrity_scan_limit": (1000, 10000000),
    "target_reacquire_seconds": (0.0, 15.0),
}


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def raise_if_cancelled(stop_event: threading.Event | None) -> None:
    if stop_event is not None and stop_event.is_set():
        raise RuntimeError("操作已取消")


def temporary_sibling_path(path: Path, suffix: str = ".tmp") -> Path:
    token = (time.time_ns() ^ threading.get_ident() ^ os.getpid()) & 0xFFFFFFFFFFFFFFFF
    return path.with_name(f".{path.name}.{token:016x}{suffix}")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = temporary_sibling_path(path)
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def atomic_write_json(path: Path, data: object) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def read_json_file(path: Path, maximum_bytes: int) -> object:
    limit = max(2, int(maximum_bytes))
    if not path.is_file() or path.is_symlink():
        raise OSError("JSON 文件缺失或类型无效")
    size = int(path.stat().st_size)
    if size < 2 or size > limit:
        raise ValueError("JSON 文件大小无效")
    with path.open("rb") as file:
        payload = file.read(limit + 1)
    if len(payload) != size or len(payload) > limit:
        raise ValueError("JSON 文件在读取时发生变化或过大")
    try:
        text = payload.decode("utf-8", errors="strict")
        return json.loads(text)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("JSON 文件内容无效") from error


def validate_npz_archive(path: Path) -> set[str]:
    if path.is_symlink():
        raise OSError("模型文件缺失或类型无效")
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise OSError("模型文件缺失或类型无效")
    archive_size = int(path.stat().st_size)
    if archive_size < 128 or archive_size > MAX_MODEL_ARCHIVE_BYTES:
        raise ValueError("模型文件大小无效")
    names: set[str] = set()
    expanded_bytes = 0
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = archive.infolist()
            if not 8 <= len(members) <= MAX_MODEL_ARCHIVE_MEMBERS:
                raise ValueError("模型文件成员数量无效")
            for member in members:
                name = member.filename
                normalized_name = name.casefold()
                if (
                    member.is_dir()
                    or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}\.npy", name)
                    or normalized_name in names
                    or member.flag_bits & 0x1
                    or member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                    or member.file_size < 0
                    or member.compress_size < 0
                    or member.file_size > MAX_MODEL_EXPANDED_BYTES
                ):
                    raise ValueError("模型文件包含无效成员")
                expanded_bytes += int(member.file_size)
                if expanded_bytes > MAX_MODEL_EXPANDED_BYTES:
                    raise ValueError("模型文件解压后过大")
                names.add(normalized_name)
    except zipfile.BadZipFile as error:
        raise ValueError("模型文件不是有效的 NPZ 文件") from error
    return names


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verified_release_source_sha256(source: str) -> str | None:
    matches = list(RELEASE_SOURCE_PATTERN.finditer(source))
    if len(matches) != 1:
        return None
    match = matches[0]
    embedded = match.group("digest")
    canonical = source[:match.start("digest")] + ("0" * 64) + source[match.end("digest"):]
    actual = hashlib.sha256(canonical.encode("utf-8", errors="strict")).hexdigest()
    return actual if hmac.compare_digest(actual, embedded) else None


def _ast_called_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        function = child.func
        if isinstance(function, ast.Name):
            names.add(function.id)
        elif isinstance(function, ast.Attribute):
            names.add(function.attr)
    return names


def _ast_referenced_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
        elif isinstance(child, ast.Attribute):
            names.add(child.attr)
    return names


def _self_assigned_attributes(node: ast.AST) -> set[str]:
    attributes: set[str] = set()
    for child in ast.walk(node):
        targets = []
        if isinstance(child, ast.Assign):
            targets = list(child.targets)
        elif isinstance(child, ast.AnnAssign):
            targets = [child.target]
        elif isinstance(child, ast.AugAssign):
            targets = [child.target]
        for target in targets:
            for nested in ast.walk(target):
                if (
                    isinstance(nested, ast.Attribute)
                    and isinstance(nested.value, ast.Name)
                    and nested.value.id == "self"
                ):
                    attributes.add(nested.attr)
    return attributes


def _ast_self_attribute(node: ast.AST, attribute: str) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        and node.attr == attribute
    )


def _ast_tk_constructor(node: ast.AST, constructor: str) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "tk"
        and node.func.attr == constructor
    )


def _ast_keyword(call: ast.Call, name: str) -> ast.AST | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


def _ast_call_name(call: ast.Call) -> str:
    function = call.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return ""


def _ensure_numpy_download_values(node: ast.AST) -> list[bool | None]:
    values: list[bool | None] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call) or _ast_call_name(child) != "ensure_numpy":
            continue
        value = _ast_keyword(child, "download")
        if isinstance(value, ast.Constant) and isinstance(value.value, bool):
            values.append(value.value)
        else:
            values.append(None)
    return values


def _strict_runtime_component_policy_valid(
    tree: ast.Module,
    top_level_nodes: dict[str, ast.AST],
) -> bool:
    ensure_files_node = top_level_nodes.get("ensure_files")
    runtime_ready_node = top_level_nodes.get("ensure_runtime_ready")
    if not isinstance(ensure_files_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if not isinstance(runtime_ready_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if [argument.arg for argument in ensure_files_node.args.args] != ["stop_event"]:
        return False
    all_values = _ensure_numpy_download_values(tree)
    return (
        _ensure_numpy_download_values(ensure_files_node) == [True]
        and _ensure_numpy_download_values(runtime_ready_node) == [False]
        and all_values.count(True) == 1
        and all_values.count(False) == 1
        and all_values.count(None) == 0
    )


def _strict_ui_structure_valid(app_class: ast.ClassDef, methods: dict[str, ast.AST]) -> bool:
    initializer = methods.get("__init__")
    if initializer is None:
        return False
    interactive_widgets = {
        "Button", "Checkbutton", "Radiobutton", "Entry", "Text", "Listbox",
        "Spinbox", "Scale", "Scrollbar", "Menu", "Menubutton", "OptionMenu", "Toplevel",
    }
    button_calls = [
        child
        for child in ast.walk(app_class)
        if isinstance(child, ast.Call)
        and isinstance(child.func, ast.Attribute)
        and isinstance(child.func.value, ast.Name)
        and child.func.value.id == "tk"
        and child.func.attr in interactive_widgets
    ]
    if len(button_calls) != len(STRICT_UI_BUTTON_ATTRIBUTES):
        return False
    if any(not _ast_tk_constructor(call, "Button") for call in button_calls):
        return False
    specifications = {
        attribute: (index, method)
        for index, (attribute, method) in enumerate(
            zip(STRICT_UI_BUTTON_ATTRIBUTES, STRICT_UI_MODE_METHODS)
        )
    }
    matched: set[str] = set()
    for child in ast.walk(initializer):
        if not isinstance(child, ast.Assign) or len(child.targets) != 1:
            continue
        target = child.targets[0]
        if not isinstance(target, ast.Attribute) or not isinstance(target.value, ast.Name) or target.value.id != "self":
            continue
        specification = specifications.get(target.attr)
        if specification is None or not _ast_tk_constructor(child.value, "Button"):
            continue
        index, method_name = specification
        text_value = _ast_keyword(child.value, "text")
        command_value = _ast_keyword(child.value, "command")
        if not (
            isinstance(text_value, ast.Subscript)
            and isinstance(text_value.value, ast.Name)
            and text_value.value.id == "STRICT_UI_ACTIONS"
            and isinstance(text_value.slice, ast.Constant)
            and text_value.slice.value == index
            and _ast_self_attribute(command_value, method_name)
        ):
            return False
        matched.add(target.attr)
    if matched != set(STRICT_UI_BUTTON_ATTRIBUTES):
        return False
    escape_bindings = 0
    close_protocols = 0
    for child in ast.walk(initializer):
        if not isinstance(child, ast.Call) or not isinstance(child.func, ast.Attribute):
            continue
        owner = child.func.value
        if not _ast_self_attribute(owner, "root"):
            continue
        if (
            child.func.attr == "bind"
            and len(child.args) >= 2
            and isinstance(child.args[0], ast.Constant)
            and child.args[0].value == "<Escape>"
            and _ast_self_attribute(child.args[1], "on_escape")
        ):
            escape_bindings += 1
        if (
            child.func.attr == "protocol"
            and len(child.args) >= 2
            and isinstance(child.args[0], ast.Constant)
            and child.args[0].value == "WM_DELETE_WINDOW"
            and _ast_self_attribute(child.args[1], "stop_and_close")
        ):
            close_protocols += 1
    return escape_bindings == 1 and close_protocols == 1


def script_metadata(path: Path) -> dict | None:
    try:
        if not path.is_file() or path.is_symlink():
            return None
        size = path.stat().st_size
        if size < MIN_SCRIPT_BYTES or size > MAX_SCRIPT_BYTES:
            return None
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path), mode="exec", feature_version=(3, 12))
        constants: dict[str, str] = {}
        constant_counts: dict[str, int] = {}
        top_level_nodes: dict[str, ast.AST] = {}
        top_level_counts: dict[str, int] = {}
        app_class: ast.ClassDef | None = None
        app_class_count = 0
        app_method_nodes: dict[str, ast.AST] = {}
        app_method_counts: dict[str, int] = {}
        native_app_class_count = 0
        native_app_method_nodes: dict[str, ast.AST] = {}
        native_app_method_counts: dict[str, int] = {}
        main_entry_count = 0
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"APP_NAME", "APP_VERSION", "SCRIPT_NAME", "RELEASE_SOURCE_SHA256"}:
                        constants[target.id] = node.value.value
                        constant_counts[target.id] = constant_counts.get(target.id, 0) + 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                top_level_nodes[node.name] = node
                top_level_counts[node.name] = top_level_counts.get(node.name, 0) + 1
            elif isinstance(node, ast.ClassDef) and node.name == "AnyGameAIApp":
                app_class = node
                app_class_count += 1
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        app_method_nodes[child.name] = child
                        app_method_counts[child.name] = app_method_counts.get(child.name, 0) + 1
            elif isinstance(node, ast.ClassDef) and node.name == "NativeAnyGameAIApp":
                native_app_class_count += 1
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        native_app_method_nodes[child.name] = child
                        native_app_method_counts[child.name] = native_app_method_counts.get(child.name, 0) + 1
            elif isinstance(node, ast.If):
                test = node.test
                if (
                    isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value == "__main__"
                    and any(
                        isinstance(statement, ast.Expr)
                        and isinstance(statement.value, ast.Call)
                        and isinstance(statement.value.func, ast.Name)
                        and statement.value.func.id == "main"
                        and not statement.value.args
                        and not statement.value.keywords
                        for statement in node.body
                    )
                ):
                    main_entry_count += 1
        version_text = constants.get("APP_VERSION", "")
        release_hash = constants.get("RELEASE_SOURCE_SHA256", "")
        if (
            constants.get("APP_NAME") != APP_NAME
            or constants.get("SCRIPT_NAME") != SCRIPT_NAME
            or any(constant_counts.get(name, 0) != 1 for name in ("APP_NAME", "APP_VERSION", "SCRIPT_NAME", "RELEASE_SOURCE_SHA256"))
            or any(count != 1 for count in top_level_counts.values())
            or any(count != 1 for count in app_method_counts.values())
            or any(count != 1 for count in native_app_method_counts.values())
            or app_class_count != 1
            or native_app_class_count != 1
            or app_class is None
            or VERSION_PATTERN.fullmatch(f'APP_VERSION = "{version_text}"') is None
            or re.fullmatch(r"[0-9a-f]{64}", release_hash) is None
            or verified_release_source_sha256(source) != release_hash
            or not REQUIRED_SCRIPT_FUNCTIONS.issubset(top_level_nodes)
            or not REQUIRED_APP_METHODS.issubset(app_method_nodes)
            or not REQUIRED_NATIVE_APP_METHODS.issubset(native_app_method_nodes)
            or main_entry_count != 1
            or not _strict_ui_structure_valid(app_class, app_method_nodes)
            or not _strict_runtime_component_policy_valid(tree, top_level_nodes)
        ):
            return None
        for function_name, required_calls in REQUIRED_SCRIPT_CALLS.items():
            node = top_level_nodes.get(function_name)
            if node is None or not required_calls.issubset(_ast_called_names(node)):
                return None
        for method_name, required_calls in REQUIRED_APP_CALLS.items():
            node = app_method_nodes.get(method_name)
            if node is None or not required_calls.issubset(_ast_referenced_names(node)):
                return None
        for method_name, required_calls in REQUIRED_NATIVE_APP_CALLS.items():
            node = native_app_method_nodes.get(method_name)
            if node is None or not required_calls.issubset(_ast_referenced_names(node)):
                return None
        initializer = app_method_nodes.get("__init__")
        if initializer is None or not REQUIRED_APP_ATTRIBUTES.issubset(_self_assigned_attributes(initializer)):
            return None
        version = tuple(int(part) for part in version_text.split("."))
        if not version:
            return None
        return {"version": version, "size": size, "release_sha256": release_hash}
    except (OSError, UnicodeError, SyntaxError, ValueError, OverflowError, TypeError):
        return None


def script_version(path: Path) -> tuple[int, ...] | None:
    metadata = script_metadata(path)
    return metadata["version"] if metadata is not None else None


def valid_script(path: Path) -> bool:
    return script_metadata(path) is not None


def load_integrity_state() -> dict:
    try:
        data = read_json_file(INTEGRITY_PATH, MAX_SMALL_JSON_BYTES)
        schema = data.get("schema") if isinstance(data, dict) else None
        size_value = data.get("script_size", 0) if isinstance(data, dict) else 0
        version_value = data.get("app_version", "") if isinstance(data, dict) else ""
        backup_hash = data.get("backup_sha256", "") if isinstance(data, dict) else ""
        release_hash = data.get("release_sha256", "") if isinstance(data, dict) else ""
        if (
            isinstance(data, dict)
            and schema in (1, 2, 3, INTEGRITY_SCHEMA)
            and isinstance(data.get("script_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", data["script_sha256"])
            and (schema == 1 or (isinstance(size_value, int) and MIN_SCRIPT_BYTES <= size_value <= MAX_SCRIPT_BYTES))
            and (not version_value or re.fullmatch(r"\d+(?:\.\d+)*", str(version_value)))
            and (not backup_hash or re.fullmatch(r"[0-9a-f]{64}", str(backup_hash)))
            and (schema != INTEGRITY_SCHEMA or re.fullmatch(r"[0-9a-f]{64}", str(release_hash)))
        ):
            return data
    except Exception:
        pass
    return {}


def save_integrity_state(script_path: Path) -> None:
    metadata = script_metadata(script_path)
    if metadata is None:
        raise RuntimeError("主程序身份或结构校验失败")
    script_hash = sha256_file(script_path)
    backup_hash = ""
    if valid_script(BACKUP_SCRIPT_PATH):
        candidate_hash = sha256_file(BACKUP_SCRIPT_PATH)
        if hmac.compare_digest(candidate_hash, script_hash):
            backup_hash = candidate_hash
    atomic_write_json(
        INTEGRITY_PATH,
        {
            "schema": INTEGRITY_SCHEMA,
            "app_version": ".".join(str(part) for part in metadata["version"]),
            "script_size": int(metadata["size"]),
            "script_sha256": script_hash,
            "backup_sha256": backup_hash,
            "release_sha256": str(metadata["release_sha256"]),
            "updated_at": now_text(),
        },
    )


def refresh_script_backup(script_path: Path) -> bool:
    if not valid_script(script_path):
        raise RuntimeError("主程序文件损坏")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(script_path)
    changed = True
    if BACKUP_SCRIPT_PATH.exists() and valid_script(BACKUP_SCRIPT_PATH):
        changed = not hmac.compare_digest(sha256_file(BACKUP_SCRIPT_PATH), source_hash)
    if changed:
        temp = temporary_sibling_path(BACKUP_SCRIPT_PATH)
        shutil.copy2(script_path, temp)
        if not valid_script(temp) or not hmac.compare_digest(sha256_file(temp), source_hash):
            temp.unlink(missing_ok=True)
            raise RuntimeError("主程序备份校验失败")
        os.replace(temp, BACKUP_SCRIPT_PATH)
    save_integrity_state(script_path)
    return changed


def verify_main_script_integrity(script_path: Path = LOCAL_SCRIPT_PATH) -> None:
    metadata = script_metadata(script_path)
    if metadata is None:
        raise RuntimeError("主程序最终完整性校验失败")
    state = load_integrity_state()
    script_hash = sha256_file(script_path)
    expected_hash = str(state.get("script_sha256", ""))
    expected_size = state.get("script_size")
    expected_version = str(state.get("app_version", ""))
    expected_release_hash = str(state.get("release_sha256", ""))
    actual_version = ".".join(str(part) for part in metadata["version"])
    actual_release_hash = str(metadata["release_sha256"])
    if (
        not expected_hash
        or not hmac.compare_digest(script_hash, expected_hash)
        or expected_size != int(metadata["size"])
        or expected_version != actual_version
        or not expected_release_hash
        or not hmac.compare_digest(expected_release_hash, actual_release_hash)
    ):
        raise RuntimeError("主程序完整性基线不一致")
    if not valid_script(BACKUP_SCRIPT_PATH):
        raise RuntimeError("主程序可信备份缺失或损坏")
    backup_hash = sha256_file(BACKUP_SCRIPT_PATH)
    if not hmac.compare_digest(backup_hash, script_hash):
        raise RuntimeError("主程序与可信备份不一致")
    recorded_backup_hash = str(state.get("backup_sha256", ""))
    if not recorded_backup_hash or not hmac.compare_digest(recorded_backup_hash, backup_hash):
        raise RuntimeError("主程序备份完整性基线不一致")


def repair_main_script() -> tuple[int, bool]:
    current = SOURCE_SCRIPT_PATH
    local = LOCAL_SCRIPT_PATH.resolve()
    repaired = 0
    restart_required = False
    state = load_integrity_state()
    expected_hash = str(state.get("script_sha256", ""))
    expected_version = tuple(
        int(part) for part in str(state.get("app_version", "")).split(".") if part.isdigit()
    )

    def replace_local(source: Path, expected_source_hash: str) -> None:
        LOCAL_SCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp = temporary_sibling_path(LOCAL_SCRIPT_PATH)
        shutil.copy2(source, temp)
        if not valid_script(temp) or not hmac.compare_digest(sha256_file(temp), expected_source_hash):
            temp.unlink(missing_ok=True)
            raise RuntimeError("主程序复制校验失败")
        os.replace(temp, LOCAL_SCRIPT_PATH)

    current_metadata = script_metadata(current)
    if current_metadata is None:
        recovery_source: Path | None = None
        recovery_hash = ""
        if current != local:
            local_metadata = script_metadata(local) if local.exists() else None
            if local_metadata is not None:
                local_hash = sha256_file(local)
                local_version = tuple(local_metadata["version"])
                legitimate_local = (
                    not expected_hash
                    or hmac.compare_digest(local_hash, expected_hash)
                    or bool(expected_version and local_version > expected_version)
                )
                if legitimate_local:
                    recovery_source = local
                    recovery_hash = local_hash
        if recovery_source is None and valid_script(BACKUP_SCRIPT_PATH):
            backup_hash = sha256_file(BACKUP_SCRIPT_PATH)
            if not expected_hash or hmac.compare_digest(backup_hash, expected_hash):
                recovery_source = BACKUP_SCRIPT_PATH
                recovery_hash = backup_hash
        if recovery_source is None:
            raise RuntimeError("当前主程序文件损坏，且没有可信备份可恢复")
        if recovery_source.resolve() != local:
            replace_local(recovery_source, recovery_hash)
            repaired += 1
        if refresh_script_backup(LOCAL_SCRIPT_PATH):
            repaired += 1
        return repaired, current == local

    current_version = tuple(current_metadata["version"])
    current_hash = sha256_file(current)

    if current != local:
        local_metadata = script_metadata(local) if local.exists() else None
        local_version = tuple(local_metadata["version"]) if local_metadata is not None else ()
        local_hash = sha256_file(local) if local_metadata is not None else ""
        copy_current = local_metadata is None or current_version > local_version
        if current_version == local_version and not hmac.compare_digest(current_hash, local_hash):
            if expected_hash:
                if hmac.compare_digest(current_hash, expected_hash):
                    copy_current = True
                elif hmac.compare_digest(local_hash, expected_hash):
                    copy_current = False
                elif valid_script(BACKUP_SCRIPT_PATH) and hmac.compare_digest(
                    sha256_file(BACKUP_SCRIPT_PATH), expected_hash
                ):
                    replace_local(BACKUP_SCRIPT_PATH, expected_hash)
                    repaired += 1
                    copy_current = False
                else:
                    raise RuntimeError("同版本主程序内容冲突，且没有可信完整性副本")
            else:
                copy_current = True
        if copy_current:
            replace_local(current, current_hash)
            repaired += 1
        source = LOCAL_SCRIPT_PATH if valid_script(LOCAL_SCRIPT_PATH) else current
        if refresh_script_backup(source):
            repaired += 1
        return repaired, False

    if expected_hash and not hmac.compare_digest(current_hash, expected_hash):
        legitimate_upgrade = bool(expected_version and current_version > expected_version)
        if not expected_version and valid_script(BACKUP_SCRIPT_PATH):
            backup_version = script_version(BACKUP_SCRIPT_PATH) or ()
            legitimate_upgrade = bool(current_version > backup_version)
        if not legitimate_upgrade:
            if valid_script(BACKUP_SCRIPT_PATH) and hmac.compare_digest(
                sha256_file(BACKUP_SCRIPT_PATH), expected_hash
            ):
                replace_local(BACKUP_SCRIPT_PATH, expected_hash)
                repaired += 1
                restart_required = True
            else:
                raise RuntimeError("主程序完整性校验失败，且没有可信备份可恢复")
    if not restart_required and refresh_script_backup(LOCAL_SCRIPT_PATH):
        repaired += 1
    return repaired, restart_required


def backup_corrupt(path: Path) -> None:
    if not path.exists():
        return
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + f"_{time.time_ns() & 0xFFFF:04x}"
    destination = path.with_name(path.name + ".corrupt." + suffix)
    try:
        os.replace(path, destination)
    except OSError:
        try:
            shutil.copy2(path, destination)
            path.unlink(missing_ok=True)
        except Exception:
            pass


def log_text(text: str) -> None:
    try:
        with LOG_LOCK:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            if LOG_PATH.is_file() and LOG_PATH.stat().st_size > MAX_LOG_BYTES:
                with LOG_PATH.open("rb") as source:
                    source.seek(-min(LOG_PATH.stat().st_size, MAX_LOG_BYTES // 2), os.SEEK_END)
                    retained = source.read()
                first_newline = retained.find(b"\n")
                if first_newline >= 0:
                    retained = retained[first_newline + 1:]
                temp = temporary_sibling_path(LOG_PATH)
                with temp.open("wb") as target:
                    target.write(retained)
                    target.flush()
                    os.fsync(target.fileno())
                os.replace(temp, LOG_PATH)
            with LOG_PATH.open("a", encoding="utf-8") as file:
                file.write(f"[{now_text()}] {text}\n")
    except Exception:
        pass


def deep_copy_json(data: object):
    return json.loads(json.dumps(data, ensure_ascii=False))


def validate_config(data: object) -> bool:
    if not isinstance(data, dict) or data.get("schema") != CONFIG_SCHEMA:
        return False
    if set(data) != set(DEFAULT_CONFIG):
        return False
    for key, (minimum, maximum) in CONFIG_RANGES.items():
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        if not math.isfinite(float(value)) or not minimum <= float(value) <= maximum:
            return False
    if int(data["train_sample_limit_per_game"]) > int(data["experience_limit_per_game"]):
        return False
    return True


def valid_profile_id(profile_id: object) -> bool:
    return (
        isinstance(profile_id, str)
        and profile_id not in (".", "..")
        and PROFILE_ID_PATTERN.fullmatch(profile_id) is not None
    )


def load_config() -> dict:
    try:
        raw = read_json_file(CONFIG_PATH, MAX_SMALL_JSON_BYTES)
        if isinstance(raw, dict) and isinstance(raw.get("schema"), int) and 3 <= int(raw["schema"]) <= CONFIG_SCHEMA:
            source_schema = int(raw.get("schema", 0))
            merged = deep_copy_json(DEFAULT_CONFIG)
            for key in DEFAULT_CONFIG:
                if key in raw:
                    merged[key] = raw[key]
            if source_schema < 19 and int(merged.get("max_action_count", 0)) == 192:
                merged["max_action_count"] = 256
            if source_schema < CONFIG_SCHEMA:
                if source_schema < 26:
                    if int(merged.get("max_action_count", 0)) == 256:
                        merged["max_action_count"] = 384
                    if int(merged.get("transfer_action_limit", 0)) == 48:
                        merged["transfer_action_limit"] = 64
                if source_schema < 24 and int(merged.get("hidden_size", 0)) == 160:
                    merged["hidden_size"] = DEFAULT_HIDDEN_SIZE
                if source_schema < 25:
                    if float(merged.get("sequence_prior_weight", 0.0)) == 0.42:
                        merged["sequence_prior_weight"] = 0.45
                    if int(merged.get("planning_horizon", 0)) == 3:
                        merged["planning_horizon"] = 4
                    if float(merged.get("planning_weight", 0.0)) == 0.24:
                        merged["planning_weight"] = 0.28
                    if int(merged.get("planning_refresh_steps", 0)) == 64:
                        merged["planning_refresh_steps"] = 48
            merged["schema"] = CONFIG_SCHEMA
            if validate_config(merged):
                if merged != raw:
                    atomic_write_json(CONFIG_PATH, merged)
                return merged
    except Exception:
        pass
    backup_corrupt(CONFIG_PATH)
    config = deep_copy_json(DEFAULT_CONFIG)
    atomic_write_json(CONFIG_PATH, config)
    return config


def load_index() -> dict:
    try:
        raw = read_json_file(INDEX_PATH, MAX_INDEX_JSON_BYTES)
        if isinstance(raw, dict) and raw.get("schema") in (3, 4, 5, 6, 7, 8, 9, 10, APP_SCHEMA) and isinstance(raw.get("profiles"), dict):
            profiles = {
                profile_id: metadata
                for profile_id, metadata in raw["profiles"].items()
                if valid_profile_id(profile_id) and isinstance(metadata, dict)
            }
            migrated = {"schema": APP_SCHEMA, "profiles": profiles}
            if migrated != raw:
                atomic_write_json(INDEX_PATH, migrated)
            return migrated
    except Exception:
        pass
    backup_corrupt(INDEX_PATH)
    index = deep_copy_json(DEFAULT_INDEX)
    atomic_write_json(INDEX_PATH, index)
    return index


def save_index(index: dict) -> None:
    atomic_write_json(INDEX_PATH, index)


def sync_profile_index(index: dict | None = None) -> tuple[dict, int]:
    index = load_index() if index is None else index
    previous = deep_copy_json(index.get("profiles", {}))
    profiles: dict[str, dict] = {}
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    for directory in PROFILES_DIR.iterdir():
        if path_is_unsafe_managed_entry(directory) or not directory.is_dir() or not valid_profile_id(directory.name):
            continue
        try:
            paths = profile_paths(directory.name)
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
            profile = migrate_profile(candidate, directory.name)
            if profile is None:
                continue
            if profile != candidate:
                atomic_write_json(paths["profile"], profile)
            profiles[directory.name] = {
                "name": str(profile.get("name", directory.name)),
                "executable": str(profile.get("executable", "")),
                "updated_at": str(profile.get("updated_at", "")),
            }
        except Exception:
            continue
    index = {"schema": APP_SCHEMA, "profiles": profiles}
    changed = int(previous != profiles)
    if changed or not INDEX_PATH.exists():
        save_index(index)
    return index, changed


def cleanup_temporary_files(stop_event: threading.Event | None = None) -> int:
    removed = 0
    corrupt_groups: dict[tuple[Path, str], list[Path]] = {}
    if APP_DIR.exists():
        site_packages_resolved = SITE_PACKAGES.resolve()
        for root_text, directory_names, file_names in os.walk(APP_DIR, topdown=True, followlinks=False):
            raise_if_cancelled(stop_event)
            root = Path(root_text)
            retained_directories = []
            for name in directory_names:
                candidate = (root / name).resolve()
                if candidate == site_packages_resolved or name.startswith(".update-"):
                    continue
                retained_directories.append(name)
            directory_names[:] = retained_directories
            for name in file_names:
                path = root / name
                if ".corrupt." in name:
                    original_name = name.split(".corrupt.", 1)[0]
                    corrupt_groups.setdefault((root, original_name), []).append(path)
                if not name.endswith((".tmp", ".download")):
                    continue
                raise_if_cancelled(stop_event)
                try:
                    path.unlink()
                    removed += 1
                except OSError:
                    pass
    if TEMP_DIR.exists():
        raise_if_cancelled(stop_event)
        try:
            removed += sum(1 for path in TEMP_DIR.rglob("*") if path.is_file())
            shutil.rmtree(TEMP_DIR)
        except OSError:
            pass
    if RUNTIME_DIR.exists():
        for directory in RUNTIME_DIR.glob(".update-*"):
            raise_if_cancelled(stop_event)
            if not directory.is_dir():
                continue
            try:
                removed += sum(1 for path in directory.rglob("*") if path.is_file())
                shutil.rmtree(directory)
            except OSError:
                pass
    for paths in corrupt_groups.values():
        paths.sort(key=lambda item: item.stat().st_mtime_ns if item.exists() else 0, reverse=True)
        for old_path in paths[CORRUPT_BACKUP_LIMIT:]:
            try:
                old_path.unlink()
                removed += 1
            except OSError:
                pass
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return removed


def gui_python_executable() -> str:
    executable = Path(sys.executable)
    if os.name == "nt" and executable.name.lower() == "python.exe":
        candidate = executable.with_name("pythonw.exe")
        if candidate.exists():
            return str(candidate)
    return str(executable)


def launch_local_script() -> None:
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    environment = isolated_python_environment()
    environment["TEMP"] = str(TEMP_DIR)
    environment["TMP"] = str(TEMP_DIR)
    environment["PIP_CACHE_DIR"] = str(TEMP_DIR / "pip-cache")
    environment["SQLITE_TMPDIR"] = str(TEMP_DIR)
    environment["PYTHONNOUSERSITE"] = "1"
    subprocess.Popen(
        [gui_python_executable(), "-I", str(LOCAL_SCRIPT_PATH)],
        cwd=str(APP_DIR),
        creationflags=flags,
        env=environment,
    )


def bootstrap_to_desktop() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    source = SOURCE_SCRIPT_PATH
    target = LOCAL_SCRIPT_PATH.resolve()
    if source != target:
        repair_main_script()
        release_single_instance()
        launch_local_script()
        raise SystemExit
    _, restart_required = repair_main_script()
    if restart_required:
        release_single_instance()
        launch_local_script()
        raise SystemExit
    verify_main_script_integrity(LOCAL_SCRIPT_PATH)


def hide_console() -> None:
    if os.name != "nt":
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def release_version_tuple(value: object) -> tuple[int, int, int]:
    match = re.match(r"\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", str(value))
    if match is None:
        return (0, 0, 0)
    major, minor, patch = match.groups()
    return int(major or 0), int(minor or 0), int(patch or 0)


def supported_numpy_version(value: object) -> bool:
    version = release_version_tuple(value)
    return (1, 26, 0) <= version < (3, 0, 0)


def path_is_link_or_junction(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
    except OSError:
        return True
    junction_check = getattr(path, "is_junction", None)
    if callable(junction_check):
        try:
            if junction_check():
                return True
        except OSError:
            return True
    return False


def validate_managed_storage_layout() -> None:
    lexical_root = Path(os.path.abspath(APP_DIR))
    if APP_DIR.exists() and path_is_link_or_junction(APP_DIR):
        raise RuntimeError("桌面 AnyGameAI 文件夹不能是链接或目录联接")
    root = APP_DIR.resolve(strict=False)
    managed_paths = (
        LOCAL_SCRIPT_PATH,
        CONFIG_PATH,
        INDEX_PATH,
        LOG_PATH,
        INTEGRITY_PATH,
        RUNTIME_INTEGRITY_PATH,
        BACKUP_DIR,
        BACKUP_SCRIPT_PATH,
        RUNTIME_DIR,
        SITE_PACKAGES,
        TEMP_DIR,
        PROFILES_DIR,
        GLOBAL_PRIOR_PATH,
    )
    for path in managed_paths:
        lexical_path = Path(os.path.abspath(path))
        if lexical_path != lexical_root and lexical_root not in lexical_path.parents:
            raise RuntimeError("AnyGameAI 管理文件路径超出桌面 AnyGameAI 文件夹")
        resolved = path.resolve(strict=False)
        if resolved != root and root not in resolved.parents:
            raise RuntimeError("AnyGameAI 管理文件路径超出桌面 AnyGameAI 文件夹")
        relative = lexical_path.relative_to(lexical_root)
        cursor = APP_DIR
        for part in relative.parts:
            cursor = cursor / part
            if cursor.exists() and path_is_link_or_junction(cursor):
                raise RuntimeError("AnyGameAI 管理路径不能包含链接或目录联接")
            if cursor.exists() and cursor.is_file():
                try:
                    if int(cursor.stat(follow_symlinks=False).st_nlink) > 1:
                        raise RuntimeError("AnyGameAI 管理文件不能是硬链接")
                except OSError as error:
                    raise RuntimeError("无法验证 AnyGameAI 管理文件") from error


def ensure_app_storage_writable() -> None:
    validate_managed_storage_layout()
    for directory in (APP_DIR, RUNTIME_DIR, TEMP_DIR, PROFILES_DIR, BACKUP_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    validate_managed_storage_layout()
    probe = APP_DIR / f".write-probe-{os.getpid()}-{time.time_ns()}.tmp"
    try:
        with probe.open("xb") as file:
            file.write(b"AnyGameAI")
            file.flush()
            os.fsync(file.fileno())
    except OSError as error:
        raise RuntimeError("桌面 AnyGameAI 文件夹不可写") from error
    finally:
        probe.unlink(missing_ok=True)


def ensure_core_ready(
    stop_event: threading.Event | None = None,
) -> tuple[dict, dict]:
    raise_if_cancelled(stop_event)
    ensure_app_storage_writable()
    verify_main_script_integrity(LOCAL_SCRIPT_PATH)
    config = load_config()
    index, _ = sync_profile_index(load_index())
    raise_if_cancelled(stop_event)
    return config, index


def configure_runtime_environment() -> None:
    ensure_app_storage_writable()
    os.chdir(APP_DIR)
    os.environ["TEMP"] = str(TEMP_DIR)
    os.environ["TMP"] = str(TEMP_DIR)
    os.environ["PIP_CACHE_DIR"] = str(TEMP_DIR / "pip-cache")
    os.environ["SQLITE_TMPDIR"] = str(TEMP_DIR)
    os.environ["PYTHONNOUSERSITE"] = "1"
    numeric_threads = runtime_numeric_thread_budget()
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[variable] = str(numeric_threads)
    os.environ["OMP_DYNAMIC"] = "FALSE"
    os.environ["MKL_DYNAMIC"] = "FALSE"
    try:
        sys.pycache_prefix = str(RUNTIME_DIR / "pycache")
    except Exception:
        pass


def add_runtime_path() -> None:
    text = str(SITE_PACKAGES)
    if text not in sys.path:
        sys.path.insert(0, text)


def clear_numpy_modules() -> None:
    for name in list(sys.modules):
        if name == "numpy" or name.startswith("numpy."):
            sys.modules.pop(name, None)


def import_numpy(local_only: bool = True):
    add_runtime_path()
    runtime_path = SITE_PACKAGES.resolve()
    module = sys.modules.get("numpy")
    if module is not None and local_only:
        module_file = getattr(module, "__file__", "")
        module_path = Path(module_file).resolve() if module_file else Path()
        if module_path != runtime_path and runtime_path not in module_path.parents:
            clear_numpy_modules()
            module = None
    if module is None:
        importlib.invalidate_caches()
        module = importlib.import_module("numpy")
    module_path = Path(module.__file__).resolve()
    if local_only and module_path != runtime_path and runtime_path not in module_path.parents:
        raise RuntimeError("未使用 AnyGameAI 本地运行组件")
    if not supported_numpy_version(getattr(module, "__version__", "")):
        raise RuntimeError("本地 NumPy 版本不兼容")
    probe = module.arange(16, dtype=module.float32).reshape(4, 4)
    if float(probe.mean()) != 7.5:
        raise RuntimeError("NumPy 自检失败")
    return module



def allocate_training_matrix(np, rows: int, columns: int):
    rows = max(0, int(rows))
    columns = max(0, int(columns))
    required_bytes = rows * columns * 4
    available = available_physical_memory_bytes()
    threshold = TRAINING_MEMMAP_THRESHOLD_BYTES
    if available > 0:
        threshold = min(threshold, max(48 * 1024 * 1024, available // 8))
    if required_bytes <= threshold:
        return np.empty((rows, columns), dtype=np.float32)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    path = TEMP_DIR / f"training-{os.getpid()}-{time.time_ns()}.float32.tmp"
    return np.memmap(path, dtype=np.float32, mode="w+", shape=(rows, columns))


def release_training_matrix(matrix) -> None:
    if matrix is None:
        return
    filename = getattr(matrix, "filename", None)
    try:
        flush = getattr(matrix, "flush", None)
        if callable(flush):
            flush()
    except Exception:
        pass
    try:
        mapping = getattr(matrix, "_mmap", None)
        if mapping is not None:
            mapping.close()
    except Exception:
        pass
    if filename:
        try:
            path = Path(str(filename)).resolve(strict=False)
            root = TEMP_DIR.resolve(strict=False)
            if path != root and root in path.parents:
                path.unlink(missing_ok=True)
        except Exception:
            pass


def isolated_python_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONINSPECT",
        "PYTHONOPTIMIZE",
        "PYTHONBREAKPOINT",
    ):
        environment.pop(name, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def local_numpy_probe_command(site_packages: Path = SITE_PACKAGES) -> list[str]:
    code = (
        "import pathlib,re,sys;"
        f"root=pathlib.Path({str(site_packages)!r}).resolve();"
        "sys.path.insert(0,str(root));"
        "[sys.modules.pop(k,None) for k in list(sys.modules) if k=='numpy' or k.startswith('numpy.')];"
        "import numpy as n;"
        "path=pathlib.Path(n.__file__).resolve();"
        r"match=re.match(r'\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?',str(n.__version__));"
        "parts=tuple(int(x or 0) for x in match.groups()) if match else (0,0,0);"
        "ok=(path==root or root in path.parents) and (1,26,0)<=parts<(3,0,0);"
        "ok=ok and float(n.arange(16,dtype=n.float32).reshape(4,4).mean())==7.5;"
        "ok=ok and n.dtype('float32').itemsize==4 and n.dtype('int64').itemsize==8;"
        "raise SystemExit(0 if ok else 17)"
    )
    return [sys.executable, "-I", "-c", code]


def distribution_record_path(distribution_name: str, site_packages: Path = SITE_PACKAGES) -> Path:
    wanted = distribution_name.strip().lower().replace("_", "-")
    if not wanted:
        raise ValueError("依赖名称无效")
    for dist_info in site_packages.glob("*.dist-info"):
        metadata_path = dist_info / "METADATA"
        record_path = dist_info / "RECORD"
        if not metadata_path.is_file() or not record_path.is_file():
            continue
        try:
            name = ""
            with metadata_path.open("r", encoding="utf-8", errors="replace") as file:
                for line in file:
                    if line.lower().startswith("name:"):
                        name = line.split(":", 1)[1].strip().lower().replace("_", "-")
                        break
            if name == wanted:
                return record_path
        except OSError:
            continue
    raise RuntimeError(f"缺少 {distribution_name} 安装记录")


def verify_installed_distribution(
    distribution_name: str,
    stop_event: threading.Event | None,
    site_packages: Path = SITE_PACKAGES,
    collect_snapshot: bool = False,
) -> int | dict:
    root = site_packages.resolve()
    record_path = distribution_record_path(distribution_name, site_packages)
    verified = 0
    aggregate = hashlib.sha256()
    verified_files: dict[str, tuple[int, bytes]] = {}
    with record_path.open("r", encoding="utf-8", newline="") as file:
        for row_number, row in enumerate(csv.reader(file), 1):
            raise_if_cancelled(stop_event)
            if row_number > MAX_DISTRIBUTION_RECORDS:
                raise RuntimeError("依赖安装记录异常")
            if len(row) < 3 or not row[0]:
                raise RuntimeError("依赖安装记录包含无效条目")
            pure = PurePosixPath(row[0])
            if pure.is_absolute() or any(part in ("", ".") for part in pure.parts):
                raise RuntimeError("依赖安装记录包含非法路径")
            if ".." in pure.parts:
                # pip --target 可能用相对路径记录命令行脚本；这些文件由下方完整目录树校验覆盖。
                continue
            unresolved_candidate = site_packages / Path(*pure.parts)
            if unresolved_candidate.is_symlink():
                raise RuntimeError(f"依赖文件类型异常：{row[0]}")
            candidate = unresolved_candidate.resolve()
            if candidate != root and root not in candidate.parents:
                raise RuntimeError("依赖安装记录路径越界")
            if not candidate.is_file():
                raise RuntimeError(f"依赖文件缺失或类型异常：{row[0]}")
            actual_size = candidate.stat().st_size
            if row[2]:
                try:
                    expected_size = int(row[2])
                except ValueError as error:
                    raise RuntimeError("依赖安装记录包含非法文件大小") from error
                if actual_size != expected_size:
                    raise RuntimeError(f"依赖文件大小错误：{row[0]}")
            digest = hashlib.sha256()
            with candidate.open("rb") as dependency_file:
                for block in iter(lambda: dependency_file.read(DOWNLOAD_CHUNK_SIZE), b""):
                    raise_if_cancelled(stop_event)
                    digest.update(block)
            actual_digest = digest.digest()
            relative_text = candidate.relative_to(root).as_posix()
            verified_files[relative_text] = (actual_size, actual_digest)
            if row[1]:
                algorithm, separator, encoded_digest = row[1].partition("=")
                if separator != "=" or algorithm.lower() != "sha256" or not encoded_digest:
                    raise RuntimeError("依赖安装记录包含不支持的校验算法")
                actual = base64.urlsafe_b64encode(actual_digest).rstrip(b"=").decode("ascii")
                if not hmac.compare_digest(actual, encoded_digest):
                    raise RuntimeError(f"依赖文件损坏：{row[0]}")
                aggregate.update(PurePosixPath(row[0]).as_posix().encode("utf-8", errors="strict"))
                aggregate.update(b"\0")
                aggregate.update(str(actual_size).encode("ascii"))
                aggregate.update(b"\0")
                aggregate.update(actual_digest)
                aggregate.update(b"\n")
                verified += 1
    if verified < 8:
        raise RuntimeError("依赖安装记录不完整")

    tree_entries: list[tuple[str, int, bytes]] = []
    tree_bytes = 0
    for root_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        raise_if_cancelled(stop_event)
        directory = Path(root_text)
        retained_directories: list[str] = []
        for name in sorted(directory_names):
            child = directory / name
            if child.is_symlink():
                raise RuntimeError("本地运行组件包含链接目录")
            retained_directories.append(name)
        directory_names[:] = retained_directories
        for name in sorted(file_names):
            raise_if_cancelled(stop_event)
            candidate = directory / name
            if candidate.is_symlink() or not candidate.is_file():
                raise RuntimeError("本地运行组件包含异常文件类型")
            relative_text = candidate.relative_to(root).as_posix()
            cached = verified_files.get(relative_text)
            if cached is None:
                actual_size = candidate.stat().st_size
                digest = hashlib.sha256()
                with candidate.open("rb") as dependency_file:
                    for block in iter(lambda: dependency_file.read(DOWNLOAD_CHUNK_SIZE), b""):
                        raise_if_cancelled(stop_event)
                        digest.update(block)
                actual_digest = digest.digest()
            else:
                actual_size, actual_digest = cached
            tree_bytes += int(actual_size)
            if tree_bytes > MAX_RUNTIME_TREE_BYTES:
                raise RuntimeError("本地运行组件目录异常过大")
            tree_entries.append((relative_text, int(actual_size), actual_digest))
            if len(tree_entries) > MAX_RUNTIME_TREE_FILES:
                raise RuntimeError("本地运行组件文件数量异常")
    if len(tree_entries) < verified:
        raise RuntimeError("本地运行组件目录不完整")
    tree_entries.sort(key=lambda item: item[0])
    tree_aggregate = hashlib.sha256()
    for relative_text, actual_size, actual_digest in tree_entries:
        tree_aggregate.update(relative_text.encode("utf-8", errors="strict"))
        tree_aggregate.update(b"\0")
        tree_aggregate.update(str(actual_size).encode("ascii"))
        tree_aggregate.update(b"\0")
        tree_aggregate.update(actual_digest)
        tree_aggregate.update(b"\n")

    if not collect_snapshot:
        return verified
    version = ""
    metadata_path = record_path.parent / "METADATA"
    try:
        with metadata_path.open("r", encoding="utf-8", errors="replace") as metadata_file:
            for line in metadata_file:
                if line.lower().startswith("version:"):
                    version = line.split(":", 1)[1].strip()
                    break
    except OSError:
        version = ""
    if not supported_numpy_version(version):
        raise RuntimeError("本地 NumPy 版本不兼容")
    return {
        "schema": RUNTIME_INTEGRITY_SCHEMA,
        "distribution": distribution_name.strip().lower().replace("_", "-"),
        "version": version,
        "file_count": verified,
        "record_sha256": sha256_file(record_path),
        "content_sha256": aggregate.hexdigest(),
        "tree_file_count": len(tree_entries),
        "tree_size": tree_bytes,
        "tree_sha256": tree_aggregate.hexdigest(),
    }


def load_runtime_integrity_state() -> dict:
    try:
        data = read_json_file(RUNTIME_INTEGRITY_PATH, MAX_SMALL_JSON_BYTES)
        if (
            isinstance(data, dict)
            and data.get("schema") == RUNTIME_INTEGRITY_SCHEMA
            and data.get("distribution") == "numpy"
            and isinstance(data.get("version"), str)
            and supported_numpy_version(data["version"])
            and isinstance(data.get("file_count"), int)
            and 8 <= int(data["file_count"]) <= MAX_DISTRIBUTION_RECORDS
            and isinstance(data.get("record_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", data["record_sha256"])
            and isinstance(data.get("content_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", data["content_sha256"])
            and isinstance(data.get("tree_file_count"), int)
            and int(data["file_count"]) <= int(data["tree_file_count"]) <= MAX_RUNTIME_TREE_FILES
            and isinstance(data.get("tree_size"), int)
            and 1 <= int(data["tree_size"]) <= MAX_RUNTIME_TREE_BYTES
            and isinstance(data.get("tree_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", data["tree_sha256"])
        ):
            return data
    except Exception:
        pass
    return {}


def save_runtime_integrity_state(snapshot: dict) -> None:
    data = {
        "schema": RUNTIME_INTEGRITY_SCHEMA,
        "distribution": str(snapshot["distribution"]),
        "version": str(snapshot["version"]),
        "file_count": int(snapshot["file_count"]),
        "record_sha256": str(snapshot["record_sha256"]),
        "content_sha256": str(snapshot["content_sha256"]),
        "tree_file_count": int(snapshot["tree_file_count"]),
        "tree_size": int(snapshot["tree_size"]),
        "tree_sha256": str(snapshot["tree_sha256"]),
        "updated_at": now_text(),
    }
    atomic_write_json(RUNTIME_INTEGRITY_PATH, data)


def runtime_integrity_matches(snapshot: dict, state: dict) -> bool:
    return all(
        hmac.compare_digest(str(snapshot.get(key, "")), str(state.get(key, "")))
        for key in (
            "distribution",
            "version",
            "file_count",
            "record_sha256",
            "content_sha256",
            "tree_file_count",
            "tree_size",
            "tree_sha256",
        )
    )


def terminate_process_tree(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            pass
    if process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=2)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass


def register_active_process(process: subprocess.Popen) -> None:
    with ACTIVE_PROCESS_LOCK:
        ACTIVE_PROCESSES.add(process)


def unregister_active_process(process: subprocess.Popen) -> None:
    with ACTIVE_PROCESS_LOCK:
        ACTIVE_PROCESSES.discard(process)


def terminate_active_processes() -> None:
    with ACTIVE_PROCESS_LOCK:
        processes = tuple(ACTIVE_PROCESSES)
    for process in processes:
        terminate_process_tree(process)


def run_process_cancelable(
    command: list[str],
    stop_event: threading.Event | None,
    environment: dict[str, str] | None = None,
) -> tuple[int, str]:
    flags = (
        getattr(subprocess, "CREATE_NO_WINDOW", 0)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    )
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=flags,
        bufsize=1,
        env=environment,
    )
    register_active_process(process)
    output: deque[str] = deque()
    output_chars = 0
    output_queue: queue.Queue = queue.Queue(maxsize=MAX_PROCESS_OUTPUT_QUEUE_LINES)

    def keep_output(line: str) -> None:
        nonlocal output_chars
        output.append(line)
        output_chars += len(line)
        while output and output_chars > MAX_PROCESS_OUTPUT_CHARS:
            output_chars -= len(output.popleft())

    def drain_output() -> None:
        while True:
            try:
                keep_output(output_queue.get_nowait())
            except queue.Empty:
                break

    def read_output() -> None:
        if process.stdout is None:
            return
        for line in iter(process.stdout.readline, ""):
            try:
                output_queue.put_nowait(line)
            except queue.Full:
                try:
                    output_queue.get_nowait()
                except queue.Empty:
                    pass
                try:
                    output_queue.put_nowait(line)
                except queue.Full:
                    pass

    reader = threading.Thread(target=read_output, daemon=True, name="AnyGameAI-ProcessOutput")
    reader.start()
    try:
        while process.poll() is None:
            drain_output()
            if stop_event is not None and stop_event.is_set():
                terminate_process_tree(process)
                reader.join(timeout=1.0)
                drain_output()
                return -1, "操作已取消"
            time.sleep(0.05)
        reader.join(timeout=1.0)
        drain_output()
        return int(process.returncode or 0), "".join(output)
    finally:
        unregister_active_process(process)


def bundled_pip_wheel() -> Path | None:
    try:
        import ensurepip

        getter = getattr(ensurepip, "_get_pip_whl_path", None)
        if callable(getter):
            candidate = Path(getter()).resolve()
            if candidate.is_file() and candidate.suffix.lower() == ".whl":
                return candidate
        bundled = Path(ensurepip.__file__).resolve().parent / "_bundled"
        candidates = sorted(bundled.glob("pip-*.whl"), reverse=True)
        return candidates[0].resolve() if candidates else None
    except Exception:
        return None


def pip_install_commands(arguments: list[str]) -> list[list[str]]:
    commands: list[list[str]] = []
    wheel = bundled_pip_wheel()
    if wheel is not None:
        code = (
            "import sys;"
            f"sys.path.insert(0,{str(wheel)!r});"
            "from pip._internal.cli.main import main;"
            "raise SystemExit(main(sys.argv[1:]))"
        )
        commands.append([sys.executable, "-I", "-c", code, *arguments])
    commands.append([sys.executable, "-I", "-m", "pip", *arguments])
    return commands


def stable_release_tuple(value: object) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"\s*(\d+)\.(\d+)\.(\d+)\s*", str(value))
    if match is None:
        return None
    version = tuple(int(part) for part in match.groups())
    if not (1, 26, 0) <= version < (3, 0, 0):
        return None
    return version


def validate_https_response_destination(response, expected_host: str, description: str) -> None:
    final_url = str(response.geturl() or "")
    parsed = urllib.parse.urlparse(final_url)
    if (
        parsed.scheme.lower() != "https"
        or (parsed.hostname or "").lower() != expected_host.strip().lower()
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise RuntimeError(f"{description}重定向到不受信任的地址")
    content_encoding = str(response.headers.get("Content-Encoding", "")).strip().lower()
    if content_encoding not in ("", "identity"):
        raise RuntimeError(f"{description}使用了不支持的内容编码")


def fetch_json_document(url: str, stop_event: threading.Event | None) -> dict:
    raise_if_cancelled(stop_event)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{APP_NAME}/{APP_VERSION} CPython/{platform.python_version()}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if getattr(response, "status", 200) != 200:
                raise RuntimeError("组件索引服务器返回异常状态")
            validate_https_response_destination(response, PYPI_INDEX_HOST, "组件索引下载")
            content_type = str(response.headers.get("Content-Type", "")).split(";", 1)[0].strip().lower()
            if content_type and content_type not in {"application/json", "application/vnd.pypi.simple.v1+json"}:
                raise RuntimeError("组件索引服务器返回了非 JSON 数据")
            content_length = response.headers.get("Content-Length", "")
            if content_length:
                try:
                    if int(content_length) > 16 * 1024 * 1024:
                        raise RuntimeError("组件索引数据异常过大")
                except ValueError:
                    pass
            chunks: list[bytes] = []
            total = 0
            while True:
                raise_if_cancelled(stop_event)
                block = response.read(256 * 1024)
                if not block:
                    break
                total += len(block)
                if total > 16 * 1024 * 1024:
                    raise RuntimeError("组件索引数据异常过大")
                chunks.append(block)
    except urllib.error.URLError as error:
        raise RuntimeError("无法连接运行组件下载服务器") from error
    try:
        data = json.loads(b"".join(chunks).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("运行组件索引数据无效") from error
    if not isinstance(data, dict):
        raise RuntimeError("运行组件索引结构无效")
    return data


def select_numpy_wheel(index: dict) -> dict:
    releases = index.get("releases")
    if not isinstance(releases, dict):
        raise RuntimeError("运行组件索引缺少版本信息")
    candidates: list[tuple[tuple[int, int, int], dict]] = []
    for version_text, files in releases.items():
        version = stable_release_tuple(version_text)
        if version is None or not isinstance(files, list):
            continue
        for item in files:
            if not isinstance(item, dict) or item.get("packagetype") != "bdist_wheel" or item.get("yanked"):
                continue
            filename = str(item.get("filename", ""))
            lower = filename.lower()
            filename_match = re.fullmatch(
                r"numpy-(\d+\.\d+\.\d+)-cp312-(?:cp312|abi3)-win_amd64\.whl",
                lower,
            )
            if filename_match is None or stable_release_tuple(filename_match.group(1)) != version:
                continue
            url = str(item.get("url", ""))
            digest = str(item.get("digests", {}).get("sha256", "")) if isinstance(item.get("digests"), dict) else ""
            size = item.get("size", 0)
            try:
                size = int(size)
            except (TypeError, ValueError, OverflowError):
                size = 0
            parsed = urllib.parse.urlparse(url)
            if (
                parsed.scheme != "https"
                or parsed.hostname != PYPI_FILE_HOST
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or not 1_000_000 <= size <= MAX_WHEEL_BYTES
            ):
                continue
            candidates.append((version, {"filename": filename, "url": url, "sha256": digest, "size": size}))
    if not candidates:
        raise RuntimeError("没有找到适用于 CPython 3.12 x64 的 NumPy 组件")
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def download_verified_file(
    url: str,
    destination: Path,
    expected_sha256: str,
    expected_size: int,
    stop_event: threading.Event | None,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": f"{APP_NAME}/{APP_VERSION} CPython/{platform.python_version()}"},
        method="GET",
    )
    digest = hashlib.sha256()
    total = 0
    try:
        with urllib.request.urlopen(request, timeout=45) as response, destination.open("xb") as file:
            if getattr(response, "status", 200) != 200:
                raise RuntimeError("运行组件下载服务器返回异常状态")
            validate_https_response_destination(response, PYPI_FILE_HOST, "运行组件下载")
            content_length = str(response.headers.get("Content-Length", "")).strip()
            if content_length:
                try:
                    declared_size = int(content_length)
                except ValueError as error:
                    raise RuntimeError("运行组件下载大小信息无效") from error
                if declared_size != expected_size:
                    raise RuntimeError("运行组件下载大小与索引不一致")
            while True:
                raise_if_cancelled(stop_event)
                block = response.read(DOWNLOAD_CHUNK_SIZE)
                if not block:
                    break
                total += len(block)
                if total > MAX_WHEEL_BYTES or total > expected_size + DOWNLOAD_CHUNK_SIZE:
                    raise RuntimeError("运行组件下载大小异常")
                digest.update(block)
                file.write(block)
            file.flush()
            os.fsync(file.fileno())
    except urllib.error.URLError as error:
        destination.unlink(missing_ok=True)
        raise RuntimeError("运行组件下载失败") from error
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    if total != expected_size or not hmac.compare_digest(digest.hexdigest(), expected_sha256):
        destination.unlink(missing_ok=True)
        raise RuntimeError("运行组件下载完整性校验失败")


def wheel_member_destination(root: Path, member_name: str) -> Path | None:
    if (
        not isinstance(member_name, str)
        or not member_name
        or "\x00" in member_name
        or "\\" in member_name
        or ":" in member_name
    ):
        raise RuntimeError("运行组件压缩包包含非法路径")
    pure = PurePosixPath(member_name)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts:
        raise RuntimeError("运行组件压缩包包含非法路径")
    parts = list(pure.parts)
    if parts[0].endswith(".data"):
        if len(parts) < 3 or parts[1] not in {"purelib", "platlib"}:
            return None
        parts = parts[2:]
    if (
        not parts
        or any(part in ("", ".") or part[-1:] in (" ", ".") for part in parts)
        or any(part.split(".", 1)[0].lower() in WINDOWS_RESERVED_DEVICE_NAMES for part in parts)
    ):
        raise RuntimeError("运行组件压缩包包含非法路径")
    destination = (root / Path(*parts)).resolve(strict=False)
    resolved_root = root.resolve(strict=False)
    if destination != resolved_root and resolved_root not in destination.parents:
        raise RuntimeError("运行组件压缩包路径越界")
    return destination


def install_wheel_archive(
    wheel_path: Path,
    site_packages: Path,
    stop_event: threading.Event | None,
) -> int:
    site_packages.mkdir(parents=True, exist_ok=True)
    extracted = 0
    expanded_bytes = 0
    file_keys: set[str] = set()
    directory_keys: set[str] = set()
    root_resolved = site_packages.resolve(strict=False)
    try:
        with zipfile.ZipFile(wheel_path, "r") as archive:
            members = archive.infolist()
            if not members or len(members) > MAX_WHEEL_MEMBERS:
                raise RuntimeError("运行组件压缩包文件数量异常")
            for member in members:
                raise_if_cancelled(stop_event)
                mode = (member.external_attr >> 16) & 0o170000
                if mode not in (0, 0o040000, 0o100000):
                    raise RuntimeError("运行组件压缩包包含不支持的文件类型")
                if member.flag_bits & 0x1:
                    raise RuntimeError("运行组件压缩包包含加密成员")
                if member.file_size < 0 or member.compress_size < 0:
                    raise RuntimeError("运行组件压缩包成员大小无效")
                if member.file_size > 8 * 1024 * 1024 and member.compress_size == 0:
                    raise RuntimeError("运行组件压缩包成员压缩信息无效")
                if (
                    member.file_size > 32 * 1024 * 1024
                    and member.compress_size > 0
                    and member.file_size > member.compress_size * 300
                ):
                    raise RuntimeError("运行组件压缩包成员压缩率异常")
                expanded_bytes += int(member.file_size)
                if expanded_bytes > MAX_WHEEL_EXPANDED_BYTES:
                    raise RuntimeError("运行组件解压后大小异常")
                destination = wheel_member_destination(site_packages, member.filename)
                if destination is None:
                    continue
                relative_parts = destination.relative_to(root_resolved).parts
                normalized_parts = tuple(part.casefold() for part in relative_parts)
                destination_key = "/".join(normalized_parts)
                parent_keys = {
                    "/".join(normalized_parts[:index])
                    for index in range(1, len(normalized_parts))
                }
                if member.is_dir():
                    if destination_key in file_keys:
                        raise RuntimeError("运行组件压缩包包含文件与目录冲突")
                    directory_keys.add(destination_key)
                    continue
                if (
                    not destination_key
                    or destination_key in file_keys
                    or destination_key in directory_keys
                    or any(parent_key in file_keys for parent_key in parent_keys)
                ):
                    raise RuntimeError("运行组件压缩包包含重复或冲突路径")
                file_keys.add(destination_key)
                directory_keys.update(parent_keys)
                destination.parent.mkdir(parents=True, exist_ok=True)
                temp = temporary_sibling_path(destination)
                temp.unlink(missing_ok=True)
                try:
                    with archive.open(member, "r") as source, temp.open("xb") as target:
                        copied = 0
                        while True:
                            raise_if_cancelled(stop_event)
                            block = source.read(DOWNLOAD_CHUNK_SIZE)
                            if not block:
                                break
                            copied += len(block)
                            if copied > member.file_size:
                                raise RuntimeError("运行组件压缩包成员大小不一致")
                            target.write(block)
                        target.flush()
                        os.fsync(target.fileno())
                    if copied != member.file_size:
                        raise RuntimeError("运行组件压缩包成员不完整")
                    os.replace(temp, destination)
                    extracted += 1
                finally:
                    temp.unlink(missing_ok=True)
    except zipfile.BadZipFile as error:
        raise RuntimeError("运行组件压缩包损坏") from error
    if extracted < 8:
        raise RuntimeError("运行组件压缩包内容不完整")
    return extracted


def install_numpy_without_pip(
    staged_site_packages: Path,
    stop_event: threading.Event | None,
) -> str:
    index = fetch_json_document(PYPI_NUMPY_JSON_URL, stop_event)
    wheel = select_numpy_wheel(index)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    wheel_token = hashlib.sha256(wheel["filename"].encode("utf-8")).hexdigest()[:16]
    wheel_path = TEMP_DIR / f"numpy-{wheel_token}.whl.download"
    try:
        download_verified_file(
            wheel["url"],
            wheel_path,
            wheel["sha256"],
            int(wheel["size"]),
            stop_event,
        )
        install_wheel_archive(wheel_path, staged_site_packages, stop_event)
        verify_installed_distribution("numpy", stop_event, staged_site_packages)
        return str(wheel["filename"])
    finally:
        wheel_path.unlink(missing_ok=True)


def verify_runtime_integrity_baseline_fast(site_packages: Path = SITE_PACKAGES) -> None:
    state = load_runtime_integrity_state()
    if not state:
        raise RuntimeError("本地 NumPy 完整性基线缺失")
    record_path = distribution_record_path("numpy", site_packages)
    if not hmac.compare_digest(sha256_file(record_path), str(state.get("record_sha256", ""))):
        raise RuntimeError("本地 NumPy 安装记录已改变")
    metadata_path = record_path.parent / "METADATA"
    version = ""
    try:
        with metadata_path.open("r", encoding="utf-8", errors="replace") as metadata_file:
            for line in metadata_file:
                if line.lower().startswith("version:"):
                    version = line.split(":", 1)[1].strip()
                    break
    except OSError as error:
        raise RuntimeError("本地 NumPy 元数据缺失") from error
    if not supported_numpy_version(version) or not hmac.compare_digest(version, str(state.get("version", ""))):
        raise RuntimeError("本地 NumPy 版本与完整性基线不一致")


def ensure_numpy(download: bool, stop_event: threading.Event | None = None) -> bool:
    if download:
        probe_code, probe_output = run_process_cancelable(
            local_numpy_probe_command(SITE_PACKAGES),
            stop_event,
            isolated_python_environment(),
        )
        if probe_code == 0:
            try:
                snapshot = verify_installed_distribution(
                    "numpy",
                    stop_event,
                    SITE_PACKAGES,
                    collect_snapshot=True,
                )
                state = load_runtime_integrity_state()
                if not state:
                    raise RuntimeError("本地 NumPy 完整性基线缺失或需要升级")
                if not runtime_integrity_matches(snapshot, state):
                    raise RuntimeError("本地 NumPy 完整性基线不匹配")
                return False
            except RuntimeError as verify_error:
                if str(verify_error) == "操作已取消":
                    raise
                log_text("本地 NumPy 完整性检查失败，将重新安装：" + repr(verify_error))
        elif probe_output:
            log_text("本地 NumPy 自检失败，将重新安装：\n" + probe_output[-4000:])
    else:
        try:
            import_numpy(local_only=True)
            verify_runtime_integrity_baseline_fast(SITE_PACKAGES)
            return False
        except Exception as first_error:
            raise RuntimeError("缺少、损坏或未经“文件”按钮校验的本地 NumPy 运行组件，请先点击“文件”。") from first_error
    if stop_event is not None and stop_event.is_set():
        raise RuntimeError("操作已取消")
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(RUNTIME_DIR).free < 384 * 1024 * 1024:
        raise RuntimeError("磁盘可用空间不足，至少需要 384 MB。")
    transaction_root = RUNTIME_DIR / f".update-{os.getpid()}-{time.time_ns()}"
    staged_site_packages = transaction_root / "site-packages"
    rollback_site_packages = transaction_root / "rollback-site-packages"
    staged_site_packages.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    process_environment = isolated_python_environment()
    process_environment["TEMP"] = str(TEMP_DIR)
    process_environment["TMP"] = str(TEMP_DIR)
    process_environment["PIP_CACHE_DIR"] = str(TEMP_DIR / "pip-cache")
    pip_arguments = [
        "--isolated",
        "install",
        "--upgrade",
        "--disable-pip-version-check",
        "--no-input",
        "--no-cache-dir",
        "--no-compile",
        "--no-deps",
        "--no-warn-script-location",
        "--retries",
        "3",
        "--timeout",
        "30",
        "--only-binary=:all:",
        "--target",
        str(staged_site_packages),
        NUMPY_REQUIREMENT,
    ]
    install_commands = pip_install_commands(pip_arguments)
    committed = False
    had_previous = SITE_PACKAGES.exists()
    try:
        code = 1
        output_parts: list[str] = []
        for command in install_commands:
            code, command_output = run_process_cancelable(command, stop_event, process_environment)
            output_parts.append(command_output)
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            if code == 0:
                break
        output = "\n".join(part for part in output_parts if part)
        if code != 0:
            log_text("pip 方式安装运行组件失败，将尝试内置安全下载器:\n" + output[-12000:])
            shutil.rmtree(staged_site_packages, ignore_errors=True)
            staged_site_packages.mkdir(parents=True, exist_ok=True)
            try:
                wheel_name = install_numpy_without_pip(staged_site_packages, stop_event)
                log_text("内置安全下载器已安装：" + wheel_name)
                code = 0
            except RuntimeError as fallback_error:
                if str(fallback_error) == "操作已取消":
                    raise
                log_text("内置安全下载器安装失败:\n" + traceback.format_exc())
                raise RuntimeError("运行组件下载或安装失败；系统 Python 不会被修改，详情已写入日志。") from fallback_error
        probe_code, probe_output = run_process_cancelable(
            local_numpy_probe_command(staged_site_packages),
            stop_event,
            process_environment,
        )
        if probe_code != 0:
            log_text("运行组件自检失败:\n" + probe_output[-12000:])
            raise RuntimeError("运行组件安装后自检失败，详情已写入日志。")
        try:
            verify_installed_distribution("numpy", stop_event, staged_site_packages)
        except RuntimeError as verify_error:
            if str(verify_error) == "操作已取消":
                raise
            log_text("运行组件逐文件完整性检查失败:\n" + traceback.format_exc())
            raise RuntimeError("运行组件安装后完整性检查失败，详情已写入日志。") from verify_error
        except Exception as verify_error:
            log_text("运行组件逐文件完整性检查失败:\n" + traceback.format_exc())
            raise RuntimeError("运行组件安装后完整性检查失败，详情已写入日志。") from verify_error
        clear_numpy_modules()
        if had_previous:
            os.replace(SITE_PACKAGES, rollback_site_packages)
        os.replace(staged_site_packages, SITE_PACKAGES)
        committed = True
        try:
            importlib.invalidate_caches()
            import_numpy(local_only=True)
            snapshot = verify_installed_distribution(
                "numpy",
                None,
                SITE_PACKAGES,
                collect_snapshot=True,
            )
            save_runtime_integrity_state(snapshot)
        except Exception as commit_error:
            clear_numpy_modules()
            shutil.rmtree(SITE_PACKAGES, ignore_errors=True)
            if had_previous and rollback_site_packages.exists():
                os.replace(rollback_site_packages, SITE_PACKAGES)
            committed = False
            raise RuntimeError("运行组件替换后自检失败，已恢复原文件。") from commit_error
        return True
    finally:
        if not committed and had_previous and not SITE_PACKAGES.exists() and rollback_site_packages.exists():
            os.replace(rollback_site_packages, SITE_PACKAGES)
        shutil.rmtree(transaction_root, ignore_errors=True)
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

def ensure_runtime_ready(stop_event: threading.Event | None = None):
    ensure_core_ready(stop_event)
    ensure_numpy(download=False, stop_event=stop_event)
    np = import_numpy()
    runtime_self_check(np)
    return np



if os.name == "nt":
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    kernel32.SetThreadExecutionState.argtypes = [wintypes.DWORD]
    kernel32.SetThreadExecutionState.restype = wintypes.DWORD
    SRCCOPY = 0x00CC0020
    CAPTUREBLT = 0x40000000
    PW_CLIENTONLY = 0x00000001
    PW_RENDERFULLCONTENT = 0x00000002
    DIB_RGB_COLORS = 0
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
    MOUSEEVENTF_XDOWN = 0x0080
    MOUSEEVENTF_XUP = 0x0100
    MOUSEEVENTF_WHEEL = 0x0800
    WH_MOUSE_LL = 14
    HC_ACTION = 0
    WM_QUIT = 0x0012
    WM_MOUSEWHEEL = 0x020A
    WHEEL_DELTA = 120
    XBUTTON1 = 0x0001
    XBUTTON2 = 0x0002

    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetShellWindow.restype = wintypes.HWND
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.IsIconic.argtypes = [wintypes.HWND]
    user32.IsIconic.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetClientRect.restype = wintypes.BOOL
    user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    user32.ClientToScreen.restype = wintypes.BOOL
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype = ctypes.c_short
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    user32.SetCursorPos.restype = wintypes.BOOL
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT
    user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
    user32.MapVirtualKeyW.restype = wintypes.UINT
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    user32.PrintWindow.restype = wintypes.BOOL
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HANDLE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype = wintypes.HANDLE
    user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype = ctypes.c_ssize_t
    user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL
    user32.GetMessageW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.UINT]
    user32.GetMessageW.restype = wintypes.BOOL
    user32.TranslateMessage.argtypes = [ctypes.c_void_p]
    user32.TranslateMessage.restype = wintypes.BOOL
    user32.DispatchMessageW.argtypes = [ctypes.c_void_p]
    user32.DispatchMessageW.restype = ctypes.c_ssize_t
    user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostThreadMessageW.restype = wintypes.BOOL

    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.GetConsoleWindow.restype = wintypes.HWND
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.GetLastError.restype = wintypes.DWORD
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HANDLE

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

    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]

    class INPUTUNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", INPUTUNION)]

    class MSLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("pt", wintypes.POINT),
            ("mouseData", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("message", wintypes.UINT),
            ("wParam", wintypes.WPARAM),
            ("lParam", wintypes.LPARAM),
            ("time", wintypes.DWORD),
            ("pt", wintypes.POINT),
            ("lPrivate", wintypes.DWORD),
        ]

    LOW_LEVEL_MOUSE_PROC = ctypes.WINFUNCTYPE(
        ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
    )

    try:
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


ESC_VK = 0x1B
MOUSE_VKS = {"left": 0x01, "right": 0x02, "middle": 0x04, "x1": 0x05, "x2": 0x06}
SAFE_KEY_VKS = tuple(sorted(set(
    list(range(0x30, 0x3A))
    + list(range(0x41, 0x5B))
    + list(range(0x60, 0x70))
    + list(range(0x70, 0x88))
    + list(range(0xBA, 0xC1))
    + list(range(0xDB, 0xE0))
    + [0x08, 0x09, 0x0D, 0x10, 0x11, 0x12, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E]
)))
EXTENDED_KEY_VKS = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E, 0x6F, 0x90}
INSTANCE_MUTEX = None
INJECTED_INPUT_LOCK = threading.RLock()
INJECTED_KEYS: set[int] = set()
INJECTED_BUTTONS: set[str] = set()


def begin_runtime_activity(display_required: bool = False) -> bool:
    if os.name != "nt":
        return False
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    if display_required:
        flags |= ES_DISPLAY_REQUIRED
    try:
        return bool(kernel32.SetThreadExecutionState(flags))
    except Exception:
        return False


def end_runtime_activity(active: bool) -> None:
    if not active or os.name != "nt":
        return
    try:
        kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    except Exception:
        pass


def acquire_single_instance() -> bool:
    global INSTANCE_MUTEX
    handle = kernel32.CreateMutexW(None, False, "Local\\AnyGameAI-Python312-x64")
    if not handle:
        return True
    if int(kernel32.GetLastError()) == 183:
        kernel32.CloseHandle(handle)
        return False
    INSTANCE_MUTEX = handle
    return True


def release_single_instance() -> None:
    global INSTANCE_MUTEX
    if os.name == "nt" and INSTANCE_MUTEX:
        try:
            kernel32.CloseHandle(INSTANCE_MUTEX)
        except Exception:
            pass
        INSTANCE_MUTEX = None


def esc_pressed() -> bool:
    return bool(user32.GetAsyncKeyState(ESC_VK) & 0x8000)


def wait_esc_release(timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + max(0.0, float(timeout))
    while esc_pressed():
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.03)
    return True


class MouseWheelMonitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._pending_delta = 0
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._hook = 0
        self._callback = None
        self._ready = threading.Event()

    def _hook_callback(self, code: int, message: int, data_pointer: int) -> int:
        if code == HC_ACTION and int(message) == WM_MOUSEWHEEL:
            data = ctypes.cast(data_pointer, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            delta = int(ctypes.c_short((int(data.mouseData) >> 16) & 0xFFFF).value)
            if delta:
                with self._lock:
                    self._pending_delta = max(-WHEEL_DELTA * 32, min(WHEEL_DELTA * 32, self._pending_delta + delta))
        return int(user32.CallNextHookEx(self._hook, code, message, data_pointer))

    def _run(self) -> None:
        self._thread_id = int(kernel32.GetCurrentThreadId())
        self._callback = LOW_LEVEL_MOUSE_PROC(self._hook_callback)
        module = kernel32.GetModuleHandleW(None)
        self._hook = int(user32.SetWindowsHookExW(WH_MOUSE_LL, self._callback, module, 0) or 0)
        self._ready.set()
        if not self._hook:
            return
        message = MSG()
        try:
            while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        finally:
            if self._hook:
                user32.UnhookWindowsHookEx(self._hook)
                self._hook = 0

    def start(self) -> None:
        if os.name != "nt" or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True, name="AnyGameAI-MouseWheel")
        self._thread.start()
        self._ready.wait(1.0)

    def consume(self) -> int:
        with self._lock:
            steps = int(self._pending_delta / WHEEL_DELTA)
            if steps == 0:
                return 0
            consumed = max(-2, min(2, steps))
            self._pending_delta -= consumed * WHEEL_DELTA
            return consumed

    def clear(self) -> None:
        with self._lock:
            self._pending_delta = 0

    def stop(self) -> None:
        if os.name != "nt":
            return
        thread = self._thread
        if thread is None:
            return
        try:
            if self._thread_id:
                user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            thread.join(timeout=1.0)
        except Exception:
            pass
        finally:
            self._thread = None
            self._thread_id = 0
            self._callback = None
            self.clear()


def foreground_window() -> int:
    return int(user32.GetForegroundWindow())


def window_exists(window: int) -> bool:
    return bool(window and user32.IsWindow(window))


def usable_target_window(window: int) -> bool:
    if not window or window == int(user32.GetShellWindow()):
        return False
    if not user32.IsWindowVisible(window) or user32.IsIconic(window):
        return False
    process_id = wintypes.DWORD()
    user32.GetWindowThreadProcessId(window, ctypes.byref(process_id))
    if process_id.value in (0, os.getpid()):
        return False
    if protected_target_window(window):
        return False
    _, _, width, height = window_capture_rect(window)
    return width >= 160 and height >= 120


def wait_for_target_window(
    stop_event: threading.Event,
    timeout: float | None = TARGET_WAIT_SECONDS,
) -> int:
    wait_esc_release()
    started = time.monotonic()
    timeout_value = 0.0 if timeout is None else max(0.0, float(timeout))
    deadline = started + timeout_value if timeout_value > 0.0 else None
    accept_after = started + TARGET_GRACE_SECONDS
    candidate = 0
    stable = 0
    while not stop_event.is_set():
        if esc_pressed():
            return 0
        if deadline is not None and time.monotonic() >= deadline:
            return 0
        window = foreground_window()
        if usable_target_window(window):
            if window == candidate:
                stable += 1
            else:
                candidate = window
                stable = 1
            if time.monotonic() >= accept_after and stable >= 4:
                return window
        else:
            candidate = 0
            stable = 0
        time.sleep(0.1)
    return 0


def window_text(window: int) -> str:
    length = max(1, int(user32.GetWindowTextLengthW(window)) + 1)
    buffer = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(window, buffer, length)
    return buffer.value.strip()


def window_class(window: int) -> str:
    buffer = ctypes.create_unicode_buffer(512)
    user32.GetClassNameW(window, buffer, len(buffer))
    return buffer.value.strip()


def process_path(window: int) -> str:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(window, ctypes.byref(pid))
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return buffer.value
        return ""
    finally:
        kernel32.CloseHandle(handle)


def protected_target_window(window: int) -> bool:
    try:
        class_name = window_class(window)
        if class_name in PROTECTED_TARGET_CLASSES:
            return True
        executable = process_path(window)
        executable_name = Path(executable).stem.lower() if executable else ""
        return executable_name in PROTECTED_TARGET_EXECUTABLES
    except Exception:
        return False


def window_capture_rect(window: int) -> tuple[int, int, int, int]:
    client = wintypes.RECT()
    origin = wintypes.POINT(0, 0)
    if user32.GetClientRect(window, ctypes.byref(client)) and user32.ClientToScreen(window, ctypes.byref(origin)):
        width = int(client.right - client.left)
        height = int(client.bottom - client.top)
        if width > 8 and height > 8:
            return int(origin.x), int(origin.y), width, height
    rect = wintypes.RECT()
    if user32.GetWindowRect(window, ctypes.byref(rect)):
        return int(rect.left), int(rect.top), max(1, int(rect.right - rect.left)), max(1, int(rect.bottom - rect.top))
    return 0, 0, int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def stable_game_title(title: str) -> str:
    text = re.sub(r"\s+", " ", title).strip()
    suffixes = (
        " - Google Chrome",
        " - Microsoft Edge",
        " — Mozilla Firefox",
        " - Mozilla Firefox",
        " - Brave",
        " - Opera",
        " - Vivaldi",
    )
    lower = text.lower()
    for suffix in suffixes:
        if lower.endswith(suffix.lower()):
            text = text[:-len(suffix)].strip()
            break
    return text[:120]


def stable_identity_title(title: str) -> str:
    text = stable_game_title(title)
    text = re.sub(r"^\s*[\[(]\d+[\])]+\s*", "", text)
    text = re.sub(
        r"\b(?:score|level|stage|wave|round|fps|ping|time|lives?|points?|coins?|xp)\s*[:：=-]?\s*\d+(?:[.,]\d+)*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\s*[-—|]\s*\d+(?:[.,]\d+)*\s*(?:fps|ms|%|points?|coins?|xp)\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*[-—|:]\s*$", "", text)
    return re.sub(r"\s+", " ", text).strip()[:120]


def profile_identity(window: int) -> dict:
    title = window_text(window)
    class_name = window_class(window)
    executable = process_path(window)
    executable_name = Path(executable).stem.lower() if executable else ""
    game_title = stable_game_title(title)
    identity_title = stable_identity_title(title)
    use_title = executable_name in HOST_EXECUTABLES or not executable
    base = game_title if use_title and game_title else (Path(executable).stem if executable else (class_name or "game"))
    identity_parts = [executable.lower(), class_name.lower()]
    if use_title:
        identity_parts.append(identity_title.lower())
    identity = "|".join(identity_parts).encode("utf-8", errors="replace")
    digest = hashlib.sha256(identity).hexdigest()[:12]
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._-") or "game"
    profile_id = f"{safe[:48]}-{digest}"
    return {
        "id": profile_id,
        "name": base or title or "Game",
        "title": title,
        "identity_title": identity_title,
        "window_class": class_name,
        "executable": executable,
    }


def window_matches_identity(window: int, identity: dict) -> bool:
    if not usable_target_window(window):
        return False
    wanted_executable = str(identity.get("executable", "")).lower()
    candidate_executable = process_path(window).lower()
    if wanted_executable and candidate_executable and wanted_executable != candidate_executable:
        return False
    wanted_class = str(identity.get("window_class", "")).lower()
    candidate_class = window_class(window).lower()
    executable_name = Path(candidate_executable or wanted_executable).stem.lower()
    if executable_name in HOST_EXECUTABLES or not wanted_executable:
        wanted_title = str(identity.get("identity_title", "")).lower()
        candidate_title = stable_identity_title(window_text(window)).lower()
        if wanted_title and candidate_title and wanted_title != candidate_title:
            return False
        if wanted_class and candidate_class and wanted_class != candidate_class:
            return False
        return bool(candidate_title or candidate_class)
    if wanted_executable and candidate_executable:
        return True
    return bool(wanted_class and candidate_class == wanted_class)


def foreground_replacement_window(current: int, identity: dict) -> int:
    candidate = foreground_window()
    if candidate and candidate != current and window_matches_identity(candidate, identity):
        return candidate
    return 0


def wait_for_replacement_window(
    current: int,
    identity: dict,
    stop_event: threading.Event,
    timeout: float,
) -> int:
    deadline = time.monotonic() + max(0.0, float(timeout))
    candidate = 0
    stable = 0
    while time.monotonic() < deadline and not stop_event.is_set():
        if esc_pressed():
            return 0
        replacement = foreground_replacement_window(current, identity)
        if replacement:
            if replacement == candidate:
                stable += 1
            else:
                candidate = replacement
                stable = 1
            if stable >= 3:
                return replacement
        else:
            candidate = 0
            stable = 0
        time.sleep(0.08)
    return 0


class ScreenSampler:
    def __init__(self, target_window: int):
        self.window = target_window
        self.width = FEATURE_WIDTH
        self.height = FEATURE_HEIGHT
        self.screen_dc = user32.GetDC(0)
        if not self.screen_dc:
            raise OSError("无法获取屏幕设备上下文")
        self.memory_dc = gdi32.CreateCompatibleDC(self.screen_dc)
        self.bitmap = gdi32.CreateCompatibleBitmap(self.screen_dc, self.width, self.height)
        if not self.memory_dc or not self.bitmap:
            if self.bitmap:
                gdi32.DeleteObject(self.bitmap)
            if self.memory_dc:
                gdi32.DeleteDC(self.memory_dc)
            user32.ReleaseDC(0, self.screen_dc)
            raise OSError("无法创建画面采集缓冲区")
        self.old_object = gdi32.SelectObject(self.memory_dc, self.bitmap)
        self.print_dc = 0
        self.print_bitmap = 0
        self.print_old_object = 0
        self.print_width = 0
        self.print_height = 0
        self.buffer = ctypes.create_string_buffer(self.width * self.height * 4)
        self.info = BITMAPINFO()
        self.info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.info.bmiHeader.biWidth = self.width
        self.info.bmiHeader.biHeight = -self.height
        self.info.bmiHeader.biPlanes = 1
        self.info.bmiHeader.biBitCount = 32
        self.info.bmiHeader.biCompression = 0
        self.info.bmiHeader.biSizeImage = self.width * self.height * 4

    def _capture_from_dc(
        self,
        source_dc,
        x: int,
        y: int,
        source_width: int,
        source_height: int,
    ) -> tuple[bytes, bytes, bytes]:
        ok = gdi32.StretchBlt(
            self.memory_dc,
            0,
            0,
            self.width,
            self.height,
            source_dc,
            x,
            y,
            source_width,
            source_height,
            SRCCOPY | CAPTUREBLT,
        )
        if not ok:
            raise OSError("画面采集失败")
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
        chroma_blue_sum = [0] * COLOR_PIXELS
        chroma_red_sum = [0] * COLOR_PIXELS
        chroma_counts = [0] * COLOR_PIXELS
        target = 0
        for source in range(0, len(raw), 4):
            b = raw[source]
            g = raw[source + 1]
            r = raw[source + 2]
            gray[target] = (r * 77 + g * 150 + b * 29) >> 8
            pixel_x = target % self.width
            pixel_y = target // self.width
            color_index = (pixel_y // 2) * COLOR_WIDTH + pixel_x // 2
            chroma_blue_sum[color_index] += max(0, min(255, 128 + ((-43 * r - 85 * g + 128 * b) >> 8)))
            chroma_red_sum[color_index] += max(0, min(255, 128 + ((128 * r - 107 * g - 21 * b) >> 8)))
            chroma_counts[color_index] += 1
            target += 1
        chroma_blue = bytes(
            max(0, min(255, (total + max(1, chroma_counts[index]) // 2) // max(1, chroma_counts[index])))
            for index, total in enumerate(chroma_blue_sum)
        )
        chroma_red = bytes(
            max(0, min(255, (total + max(1, chroma_counts[index]) // 2) // max(1, chroma_counts[index])))
            for index, total in enumerate(chroma_red_sum)
        )
        return bytes(gray), chroma_blue, chroma_red

    def _release_print_surface(self) -> None:
        if self.print_dc:
            if self.print_old_object:
                gdi32.SelectObject(self.print_dc, self.print_old_object)
            if self.print_bitmap:
                gdi32.DeleteObject(self.print_bitmap)
            gdi32.DeleteDC(self.print_dc)
        self.print_dc = 0
        self.print_bitmap = 0
        self.print_old_object = 0
        self.print_width = 0
        self.print_height = 0

    def _capture_print_window(self, width: int, height: int) -> tuple[bytes, bytes, bytes] | None:
        if width <= 0 or height <= 0 or width * height > 32_000_000:
            return None
        if width != self.print_width or height != self.print_height or not self.print_dc:
            self._release_print_surface()
            print_dc = gdi32.CreateCompatibleDC(self.screen_dc)
            print_bitmap = gdi32.CreateCompatibleBitmap(self.screen_dc, width, height)
            if not print_dc or not print_bitmap:
                if print_bitmap:
                    gdi32.DeleteObject(print_bitmap)
                if print_dc:
                    gdi32.DeleteDC(print_dc)
                return None
            self.print_dc = print_dc
            self.print_bitmap = print_bitmap
            self.print_old_object = gdi32.SelectObject(print_dc, print_bitmap)
            self.print_width = width
            self.print_height = height
        rendered = False
        for flags in (PW_CLIENTONLY | PW_RENDERFULLCONTENT, PW_CLIENTONLY, 0):
            if user32.PrintWindow(self.window, self.print_dc, flags):
                rendered = True
                break
        if not rendered:
            return None
        return self._capture_from_dc(self.print_dc, 0, 0, width, height)

    @staticmethod
    def _frame_detail(frame: tuple[bytes, bytes, bytes]) -> float:
        gray, chroma_blue, chroma_red = frame
        gray_detail = max(gray) - min(gray)
        color_detail = (max(chroma_blue) - min(chroma_blue) + max(chroma_red) - min(chroma_red)) * 0.35
        color_presence = max(
            max(abs(value - 128) for value in chroma_blue),
            max(abs(value - 128) for value in chroma_red),
        ) * 0.04
        visible_luminance = max(gray) * 0.05
        return max(float(gray_detail), float(color_detail), float(color_presence), float(visible_luminance))

    def capture_frame(self) -> tuple[bytes, bytes, bytes]:
        x, y, source_width, source_height = window_capture_rect(self.window)
        screen_frame = self._capture_from_dc(self.screen_dc, x, y, source_width, source_height)
        best_frame = screen_frame
        best_detail = self._frame_detail(screen_frame)
        if best_detail >= 3:
            return best_frame
        window_dc = user32.GetDC(self.window)
        if window_dc:
            try:
                window_frame = self._capture_from_dc(window_dc, 0, 0, source_width, source_height)
                window_detail = self._frame_detail(window_frame)
                if window_detail > best_detail:
                    best_frame = window_frame
                    best_detail = window_detail
            except Exception:
                pass
            finally:
                user32.ReleaseDC(self.window, window_dc)
        if best_detail >= 3:
            return best_frame
        try:
            printed = self._capture_print_window(source_width, source_height)
            if printed is not None and self._frame_detail(printed) > best_detail:
                return printed
        except Exception:
            pass
        return best_frame

    def close(self) -> None:
        try:
            self._release_print_surface()
            gdi32.SelectObject(self.memory_dc, self.old_object)
            gdi32.DeleteObject(self.bitmap)
            gdi32.DeleteDC(self.memory_dc)
            user32.ReleaseDC(0, self.screen_dc)
        except Exception:
            pass


def frame_capture_failed(gray: bytes, chroma_blue: bytes, chroma_red: bytes) -> bool:
    if (
        len(gray) != FEATURE_WIDTH * FEATURE_HEIGHT
        or len(chroma_blue) != COLOR_PIXELS
        or len(chroma_red) != COLOR_PIXELS
    ):
        raise ValueError("画面尺寸无效")
    if max(gray) > 2:
        return False
    color_deviation = max(
        max(abs(value - 128) for value in chroma_blue),
        max(abs(value - 128) for value in chroma_red),
    )
    return color_deviation <= 2


def cursor_position() -> tuple[int, int]:
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return int(point.x), int(point.y)


def overlay_cursor_marker(gray: bytes, feature_x: int, feature_y: int) -> bytes:
    if len(gray) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    if not 0 <= feature_x < FEATURE_WIDTH or not 0 <= feature_y < FEATURE_HEIGHT:
        return gray
    marked = bytearray(gray)
    points = (
        (feature_x, feature_y, 255),
        (feature_x - 1, feature_y, 0),
        (feature_x + 1, feature_y, 0),
        (feature_x, feature_y - 1, 0),
        (feature_x, feature_y + 1, 0),
        (feature_x - 1, feature_y - 1, 255),
        (feature_x + 1, feature_y + 1, 255),
    )
    for x, y, value in points:
        if 0 <= x < FEATURE_WIDTH and 0 <= y < FEATURE_HEIGHT:
            marked[y * FEATURE_WIDTH + x] = value
    return bytes(marked)


def cursor_aware_frame(target: int, gray: bytes) -> bytes:
    left, top, width, height = window_capture_rect(target)
    if width <= 0 or height <= 0:
        return gray
    cursor_x, cursor_y = cursor_position()
    if not (left <= cursor_x < left + width and top <= cursor_y < top + height):
        return gray
    feature_x = min(FEATURE_WIDTH - 1, max(0, int((cursor_x - left) * FEATURE_WIDTH / width)))
    feature_y = min(FEATURE_HEIGHT - 1, max(0, int((cursor_y - top) * FEATURE_HEIGHT / height)))
    return overlay_cursor_marker(gray, feature_x, feature_y)


def visual_action_target_biases(current: bytes, previous: bytes | None, actions: list[dict]) -> list[float]:
    pixel_count = FEATURE_WIDTH * FEATURE_HEIGHT
    if len(current) != pixel_count or (previous is not None and len(previous) != pixel_count):
        raise ValueError("画面尺寸无效")
    result = [0.0] * len(actions)
    for index, raw_action in enumerate(actions):
        action = normalized_action(raw_action)
        if action["mouse_x"] < 0 or action["mouse_y"] < 0 or not action["buttons"]:
            continue
        center_x = min(FEATURE_WIDTH - 1, max(0, int((action["mouse_x"] + 0.5) * FEATURE_WIDTH / MOUSE_GRID_WIDTH)))
        center_y = min(FEATURE_HEIGHT - 1, max(0, int((action["mouse_y"] + 0.5) * FEATURE_HEIGHT / MOUSE_GRID_HEIGHT)))
        values = []
        motion_total = 0.0
        edge_total = 0.0
        samples = 0
        for y in range(max(0, center_y - 2), min(FEATURE_HEIGHT, center_y + 3)):
            offset = y * FEATURE_WIDTH
            for x in range(max(0, center_x - 2), min(FEATURE_WIDTH, center_x + 3)):
                position = offset + x
                value = current[position]
                values.append(value)
                if previous is not None:
                    motion_total += abs(value - previous[position]) / 255.0
                if x + 1 < FEATURE_WIDTH:
                    edge_total += abs(value - current[position + 1]) / 255.0
                if y + 1 < FEATURE_HEIGHT:
                    edge_total += abs(value - current[position + FEATURE_WIDTH]) / 255.0
                samples += 1
        if not values:
            continue
        contrast = (max(values) - min(values)) / 255.0
        motion = motion_total / max(1, samples)
        edge = edge_total / max(1, samples * 2)
        normalized_x = (center_x + 0.5) / FEATURE_WIDTH
        normalized_y = (center_y + 0.5) / FEATURE_HEIGHT
        center_prior = max(0.0, 1.0 - math.hypot(normalized_x - 0.5, normalized_y - 0.5) / 0.71)
        score = contrast * 0.42 + min(1.0, motion * 5.0) * 0.30 + min(1.0, edge * 4.0) * 0.20 + center_prior * 0.08
        if "right" in action["buttons"]:
            score *= 0.72
        if action["repeat"] > 1:
            score *= 0.88
        result[index] = max(0.0, min(1.0, score))
    return result



def infer_scene_context(
    current: bytes,
    previous: bytes | None,
    static_streak: int,
) -> tuple[str, dict[str, float]]:
    pixel_count = FEATURE_WIDTH * FEATURE_HEIGHT
    if len(current) != pixel_count or (previous is not None and len(previous) != pixel_count):
        raise ValueError("画面尺寸无效")
    minimum = min(current)
    maximum = max(current)
    mean_luminance = sum(current) / (pixel_count * 255.0)
    contrast = (maximum - minimum) / 255.0
    edge_total = 0
    edge_samples = 0
    for y in range(FEATURE_HEIGHT):
        row = y * FEATURE_WIDTH
        for x in range(FEATURE_WIDTH):
            position = row + x
            value = current[position]
            if x + 1 < FEATURE_WIDTH:
                edge_total += abs(value - current[position + 1])
                edge_samples += 1
            if y + 1 < FEATURE_HEIGHT:
                edge_total += abs(value - current[position + FEATURE_WIDTH])
                edge_samples += 1
    edge_activity = edge_total / max(1.0, edge_samples * 255.0)
    motion = 0.0
    changed_ratio = 0.0
    translation_dx = 0
    translation_dy = 0
    translation_confidence = 0.0
    if previous is not None:
        difference_total = 0
        changed = 0
        for before, after in zip(previous, current):
            difference = abs(after - before)
            difference_total += difference
            if difference >= 16:
                changed += 1
        motion = difference_total / (pixel_count * 255.0)
        changed_ratio = changed / pixel_count
        if motion >= 0.008 or changed_ratio >= 0.05:
            translation_dx, translation_dy, translation_confidence = estimate_visual_translation(previous, current, 2)
    scrolling = (
        previous is not None
        and translation_confidence >= 0.11
        and abs(translation_dy) >= max(1, abs(translation_dx) + 1)
        and motion >= 0.009
    )
    if mean_luminance <= 0.055 and contrast <= 0.16:
        context = "dark_scene"
    elif scrolling:
        context = "scrolling"
    elif motion >= 0.028 or changed_ratio >= 0.15 or translation_confidence >= 0.18:
        context = "dynamic_world"
    elif edge_activity >= 0.060 and contrast >= 0.18 and motion <= 0.018:
        context = "static_ui"
    else:
        context = "mixed_scene"
    biases = {kind: 0.0 for kind in CONTROL_KINDS}
    if context == "static_ui":
        biases.update({"idle": -0.10, "keyboard": 0.16, "pointer": 0.06, "click": 0.48, "wheel": 0.10, "mixed": -0.04})
    elif context == "dynamic_world":
        biases.update({"idle": -0.08, "keyboard": 0.34, "pointer": 0.14, "click": -0.10, "wheel": -0.20, "mixed": 0.25})
    elif context == "scrolling":
        biases.update({"idle": -0.10, "keyboard": 0.12, "pointer": 0.08, "click": -0.08, "wheel": 0.46, "mixed": 0.02})
    elif context == "dark_scene":
        biases.update({"idle": -0.06, "keyboard": 0.22, "pointer": 0.10, "click": -0.22, "wheel": -0.14, "mixed": 0.12})
    else:
        biases.update({"idle": -0.04, "keyboard": 0.14, "pointer": 0.07, "click": 0.08, "wheel": -0.03, "mixed": 0.10})
    if static_streak >= 4:
        strength = min(0.24, 0.025 * static_streak)
        biases["idle"] -= strength
        biases["keyboard"] += strength * 0.60
        biases["click"] += strength
        biases["wheel"] += strength * 0.45
    if motion >= 0.075 and context == "dynamic_world":
        biases["idle"] += 0.08
        biases["click"] -= 0.05
    return context, {kind: max(-0.55, min(0.60, float(value))) for kind, value in biases.items()}


def scene_control_response_evidence(profile: dict, context: str) -> dict[str, float]:
    if context not in SCENE_CONTEXTS:
        return {kind: 0.0 for kind in CONTROL_KINDS}
    reward_root = profile.get("scene_control_reward_ema", {})
    count_root = profile.get("scene_control_reward_counts", {})
    reward_values = reward_root.get(context, {}) if isinstance(reward_root, dict) else {}
    count_values = count_root.get(context, {}) if isinstance(count_root, dict) else {}
    result: dict[str, float] = {}
    for kind in CONTROL_KINDS:
        try:
            reward = float(reward_values.get(kind, 0.0)) if isinstance(reward_values, dict) else 0.0
            count = int(count_values.get(kind, 0)) if isinstance(count_values, dict) else 0
        except (TypeError, ValueError):
            reward = 0.0
            count = 0
        if not math.isfinite(reward):
            reward = 0.0
        confidence = max(0.0, min(1.0, math.log1p(max(0, count)) / math.log(21.0)))
        result[kind] = max(-1.0, min(1.0, reward)) * confidence
    return result


def update_scene_control_response(profile: dict, context: str, action_index: int, reward: float) -> None:
    if context not in SCENE_CONTEXTS or not 0 <= action_index < len(profile.get("actions", [])):
        return
    reward_root = profile.get("scene_control_reward_ema")
    count_root = profile.get("scene_control_reward_counts")
    if (
        not isinstance(reward_root, dict)
        or not isinstance(count_root, dict)
        or not isinstance(reward_root.get(context), dict)
        or not isinstance(count_root.get(context), dict)
    ):
        ensure_action_metadata(profile)
    kind = action_kind(profile["actions"][action_index])
    reward_values = profile["scene_control_reward_ema"][context]
    count_values = profile["scene_control_reward_counts"][context]
    count = int(count_values.get(kind, 0))
    previous = float(reward_values.get(kind, 0.0))
    bounded = max(-1.0, min(1.0, float(reward)))
    alpha = max(0.04, 1.0 / min(28, count + 1))
    reward_values[kind] = max(-1.0, min(1.0, previous + alpha * (bounded - previous)))
    count_values[kind] = min(1_000_000_000, count + 1)

def scene_action_response_evidence(profile: dict, context: str) -> list[float]:
    action_count = len(profile.get("actions", []))
    if context not in SCENE_CONTEXTS or action_count <= 0:
        return [0.0] * action_count
    reward_root = profile.get("scene_action_reward_ema", {})
    count_root = profile.get("scene_action_reward_counts", {})
    reward_values = reward_root.get(context, []) if isinstance(reward_root, dict) else []
    count_values = count_root.get(context, []) if isinstance(count_root, dict) else []
    result: list[float] = []
    for action_index in range(action_count):
        try:
            reward = float(reward_values[action_index])
            count = int(count_values[action_index])
        except (IndexError, TypeError, ValueError):
            reward = 0.0
            count = 0
        if not math.isfinite(reward):
            reward = 0.0
        confidence = max(0.0, min(1.0, math.log1p(max(0, count)) / math.log(25.0)))
        result.append(max(-1.0, min(1.0, reward)) * confidence)
    return result


def update_scene_action_response(profile: dict, context: str, action_index: int, reward: float) -> None:
    action_count = len(profile.get("actions", []))
    if context not in SCENE_CONTEXTS or not 0 <= action_index < action_count:
        return
    reward_root = profile.get("scene_action_reward_ema")
    count_root = profile.get("scene_action_reward_counts")
    if (
        not isinstance(reward_root, dict)
        or not isinstance(count_root, dict)
        or not isinstance(reward_root.get(context), list)
        or not isinstance(count_root.get(context), list)
        or len(reward_root[context]) != action_count
        or len(count_root[context]) != action_count
    ):
        ensure_action_metadata(profile)
    reward_values = profile["scene_action_reward_ema"][context]
    count_values = profile["scene_action_reward_counts"][context]
    count = int(count_values[action_index])
    previous = float(reward_values[action_index])
    bounded = max(-1.0, min(1.0, float(reward)))
    alpha = max(0.035, 1.0 / min(32, count + 1))
    reward_values[action_index] = max(-1.0, min(1.0, previous + alpha * (bounded - previous)))
    count_values[action_index] = min(1_000_000_000, count + 1)


def send_inputs(items: list) -> None:
    if not items:
        return
    array_type = INPUT * len(items)
    array = array_type(*items)
    sent = user32.SendInput(len(items), ctypes.byref(array), ctypes.sizeof(INPUT))
    if sent != len(items):
        raise OSError("输入发送失败")


def keyboard_input(vk: int, up: bool = False):
    scan_code = int(user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC))
    if scan_code:
        flags = KEYEVENTF_SCANCODE
        if vk in EXTENDED_KEY_VKS:
            flags |= KEYEVENTF_EXTENDEDKEY
        if up:
            flags |= KEYEVENTF_KEYUP
        return INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(0, scan_code & 0xFF, flags, 0, 0))
    flags = KEYEVENTF_KEYUP if up else 0
    return INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, 0, flags, 0, 0))


def mouse_input(dx: int = 0, dy: int = 0, flags: int = 0, data: int = 0):
    return INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dx, dy, data, flags, 0, 0))


def release_all_inputs() -> None:
    if os.name != "nt":
        return
    with INJECTED_INPUT_LOCK:
        keys = sorted(INJECTED_KEYS)
        buttons = tuple(INJECTED_BUTTONS)
        items = [keyboard_input(vk, True) for vk in keys]
        for name in buttons:
            if name == "left":
                items.append(mouse_input(flags=MOUSEEVENTF_LEFTUP))
            elif name == "right":
                items.append(mouse_input(flags=MOUSEEVENTF_RIGHTUP))
            elif name == "middle":
                items.append(mouse_input(flags=MOUSEEVENTF_MIDDLEUP))
            elif name == "x1":
                items.append(mouse_input(flags=MOUSEEVENTF_XUP, data=XBUTTON1))
            elif name == "x2":
                items.append(mouse_input(flags=MOUSEEVENTF_XUP, data=XBUTTON2))
        released = True
        for start in range(0, len(items), 48):
            try:
                send_inputs(items[start:start + 48])
            except Exception:
                released = False
        if released:
            INJECTED_KEYS.difference_update(keys)
            INJECTED_BUTTONS.difference_update(buttons)


def normalized_action(action: dict) -> dict:
    if not isinstance(action, dict):
        action = {}
    raw_keys = action.get("keys", [])
    if not isinstance(raw_keys, (list, tuple, set)):
        raw_keys = []
    keys_set: set[int] = set()
    for value in raw_keys:
        try:
            key = int(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if key in SAFE_KEY_VKS:
            keys_set.add(key)
    keys = sorted(keys_set)[:6]
    if any(combination.issubset(keys_set) for combination in SYSTEM_BLOCKED_KEY_COMBINATIONS):
        keys = []
    raw_buttons = action.get("buttons", [])
    if not isinstance(raw_buttons, (list, tuple, set)):
        raw_buttons = []
    button_set = {str(value).lower() for value in raw_buttons}
    buttons = [name for name in ("left", "right", "middle", "x1", "x2") if name in button_set]

    def bounded_integer(name: str, minimum: int, maximum: int, default: int = 0) -> int:
        try:
            value = int(action.get(name, default))
        except (TypeError, ValueError, OverflowError):
            value = default
        return max(minimum, min(maximum, value))

    dx = bounded_integer("mouse_dx", -2, 2)
    dy = bounded_integer("mouse_dy", -2, 2)
    wheel = bounded_integer("mouse_wheel", -2, 2)
    mouse_x = bounded_integer("mouse_x", -1, MOUSE_GRID_WIDTH - 1, -1)
    mouse_y = bounded_integer("mouse_y", -1, MOUSE_GRID_HEIGHT - 1, -1)
    repeat = bounded_integer("repeat", 1, 3, 1)
    if mouse_x < 0 or mouse_y < 0:
        mouse_x = -1
        mouse_y = -1
    if mouse_x >= 0:
        dx = 0
        dy = 0
    if keys == [0x12] and not (buttons or dx or dy or wheel or mouse_x >= 0):
        keys = []
    simple_left_click = (
        buttons == ["left"]
        and not keys
        and not dx
        and not dy
        and not wheel
    )
    if not simple_left_click:
        repeat = 1
    return {
        "keys": keys,
        "buttons": buttons,
        "mouse_dx": dx,
        "mouse_dy": dy,
        "mouse_wheel": wheel,
        "mouse_x": mouse_x,
        "mouse_y": mouse_y,
        "repeat": repeat,
    }

def universal_actions() -> list[dict]:
    raw_actions: list[dict] = [{}]
    movement_groups = (
        (0x57, 0x41, 0x53, 0x44),
        (0x26, 0x25, 0x28, 0x27),
        (0x49, 0x4A, 0x4B, 0x4C),
    )
    for up, left, down, right in movement_groups:
        raw_actions.extend(
            {"keys": keys}
            for keys in (
                [up], [left], [down], [right],
                [up, left], [up, right], [down, left], [down, right],
            )
        )
    raw_actions.extend(
        {"keys": [key]}
        for key in (0x68, 0x64, 0x62, 0x66, 0x67, 0x69, 0x61, 0x63)
    )
    common_keys = (
        0x20, 0x0D, 0x09, 0x08,
        0x45, 0x46, 0x51, 0x52, 0x54, 0x47,
        0x5A, 0x58, 0x43, 0x56, 0x42, 0x4E, 0x4D,
        0x48, 0x50, 0x55, 0x4F, 0x59,
    )
    raw_actions.extend({"keys": [key]} for key in common_keys)
    raw_actions.extend({"keys": [key]} for key in range(0x30, 0x3A))
    raw_actions.extend({"keys": [key]} for key in range(0x70, 0x7C))
    raw_actions.extend({"keys": [key]} for key in (0x21, 0x22, 0x23, 0x24, 0x2D, 0x2E))
    raw_actions.extend({"keys": [key]} for key in range(0xBA, 0xC1))
    raw_actions.extend({"keys": [key]} for key in range(0xDB, 0xE0))
    cardinal_movements = [
        [0x57], [0x41], [0x53], [0x44],
        [0x26], [0x25], [0x28], [0x27],
        [0x49], [0x4A], [0x4B], [0x4C],
    ]
    raw_actions.extend({"keys": movement + [0x10]} for movement in cardinal_movements)
    raw_actions.extend({"keys": movement + [0x20]} for movement in cardinal_movements)
    raw_actions.extend({"keys": [key]} for key in (0x60, 0x65, 0x6B, 0x6D, 0x6E, 0x6F))
    for modifier in (0x45, 0x46, 0x51, 0x52):
        for movement in cardinal_movements[:4]:
            raw_actions.append({"keys": movement + [modifier]})
    for movement in cardinal_movements[:8]:
        raw_actions.append({"keys": movement, "buttons": ["left"]})
    pointer_directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))
    for magnitude in (1, 2):
        for dx, dy in pointer_directions:
            raw_actions.append({"mouse_dx": dx * magnitude, "mouse_dy": dy * magnitude})
    for dx, dy in pointer_directions:
        raw_actions.append({"buttons": ["left"], "mouse_dx": dx, "mouse_dy": dy})
    raw_actions.extend(
        (
            {"buttons": ["left"]},
            {"buttons": ["right"]},
            {"buttons": ["middle"]},
            {"buttons": ["x1"]},
            {"buttons": ["x2"]},
            {"mouse_wheel": 1},
            {"mouse_wheel": -1},
            {"mouse_wheel": 2},
            {"mouse_wheel": -2},
        )
    )
    click_columns = (4, 10, 16, 22, 28)
    click_rows = (3, 9, 15)
    for mouse_y in click_rows:
        for mouse_x in click_columns:
            raw_actions.append({"buttons": ["left"], "mouse_x": mouse_x, "mouse_y": mouse_y})
    extra_click_columns = (2, 8, 24, 30)
    extra_click_rows = (2, 6, 10, 14, 16)
    for mouse_y in extra_click_rows:
        for mouse_x in extra_click_columns:
            raw_actions.append({"buttons": ["left"], "mouse_x": mouse_x, "mouse_y": mouse_y})
    adaptive_click_positions = (
        (16, 1), (16, 6), (16, 12), (16, 17),
        (6, 1), (6, 5), (6, 13), (6, 17),
        (14, 1), (14, 5), (14, 13), (14, 17),
        (18, 1), (18, 5), (18, 13), (18, 17),
        (26, 1), (26, 5), (26, 13), (26, 17),
        (12, 4), (12, 8), (12, 12), (12, 16),
        (20, 4), (20, 8), (20, 12), (20, 16),
    )
    raw_actions.extend(
        {"buttons": ["left"], "mouse_x": mouse_x, "mouse_y": mouse_y}
        for mouse_x, mouse_y in adaptive_click_positions
    )
    for mouse_x, mouse_y in ((16, 9), (8, 5), (24, 5), (8, 13), (24, 13)):
        raw_actions.append({"buttons": ["right"], "mouse_x": mouse_x, "mouse_y": mouse_y})
    for mouse_x, mouse_y in ((16, 9), (16, 5), (16, 13), (6, 5), (26, 5), (16, 17)):
        raw_actions.append({"buttons": ["left"], "mouse_x": mouse_x, "mouse_y": mouse_y, "repeat": 2})
    actions: list[dict] = []
    signatures: set[str] = set()
    for raw_action in raw_actions:
        action = normalized_action(raw_action)
        signature = json.dumps(action, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if signature in signatures:
            continue
        signatures.add(signature)
        actions.append(action)
        if len(actions) >= UNIVERSAL_ACTION_LIMIT:
            break
    return actions

def seed_universal_actions(profile: dict, limit: int = UNIVERSAL_ACTION_LIMIT) -> int:
    actions = profile.get("actions")
    if not isinstance(actions, list):
        actions = []
    actions = [normalized_action(action) for action in actions]
    origins = profile.get("action_origins")
    if not isinstance(origins, list):
        origins = []
    cleaned_origins = []
    for index in range(len(actions)):
        value = str(origins[index]) if index < len(origins) else "human"
        cleaned_origins.append(value if value in ("generic", "human", "transfer") else "human")
    existing = {action_signature(action) for action in actions}
    missing_actions = [action for action in universal_actions() if action_signature(action) not in existing]
    capacity = min(1024, max(len(actions), max(1, int(limit))))
    added = 0
    for action in missing_actions:
        if len(actions) >= capacity:
            break
        signature = action_signature(action)
        existing.add(signature)
        actions.append(action)
        cleaned_origins.append("generic")
        added += 1
    profile["actions"] = actions
    profile["action_origins"] = cleaned_origins
    profile["universal_action_schema"] = UNIVERSAL_ACTION_SCHEMA
    return added


def merge_prior_actions(profile: dict, prior: dict | None, max_actions: int, transfer_limit: int) -> int:
    if prior is None or transfer_limit <= 0:
        return 0
    actions = profile.get("actions")
    if not isinstance(actions, list):
        return 0
    origins = profile.get("action_origins")
    if not isinstance(origins, list):
        origins = ["human"] * len(actions)
    while len(origins) < len(actions):
        origins.append("human")
    existing = {action_signature(action) for action in actions}
    added = 0
    for signature in prior.get("action_signatures", []):
        if added >= transfer_limit or len(actions) >= max_actions:
            break
        if not isinstance(signature, str) or signature in existing:
            continue
        try:
            decoded = json.loads(signature)
            action = normalized_action(decoded)
        except Exception:
            continue
        normalized_signature = action_signature(action)
        if normalized_signature in existing:
            continue
        existing.add(normalized_signature)
        actions.append(action)
        origins.append("transfer")
        added += 1
    if added:
        profile["actions"] = actions
        profile["action_origins"] = origins[:len(actions)]
        profile["needs_training"] = True
    return added


def action_signature(action: dict) -> str:
    return json.dumps(normalized_action(action), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_action_signature_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    try:
        decoded = json.loads(value)
    except Exception:
        return ""
    return action_signature(decoded)


def action_kind(action: dict) -> str:
    action = normalized_action(action)
    has_keys = bool(action["keys"])
    has_click = bool(action["buttons"])
    has_pointer = bool(action["mouse_dx"] or action["mouse_dy"] or action["mouse_x"] >= 0)
    has_wheel = bool(action["mouse_wheel"])
    active_groups = int(has_keys) + int(has_click or has_pointer or has_wheel)
    if active_groups > 1:
        return "mixed"
    if has_click:
        return "click"
    if has_wheel:
        return "wheel"
    if has_pointer:
        return "pointer"
    if has_keys:
        return "keyboard"
    return "idle"


def learned_control_preferences(profile: dict, database_path: Path) -> dict[str, float]:
    actions = profile.get("actions", [])
    kind_counts: dict[str, int] = {}
    try:
        connection = sqlite3.connect(database_path, timeout=20)
        try:
            rows = connection.execute(
                "SELECT action, COUNT(*) FROM samples WHERE source='human' GROUP BY action"
            ).fetchall()
        finally:
            connection.close()
        for action_index, count in rows:
            index = int(action_index)
            if 0 <= index < len(actions):
                kind = action_kind(actions[index])
                kind_counts[kind] = kind_counts.get(kind, 0) + max(0, int(count))
    except Exception:
        kind_counts = {}
    active_counts = {kind: count for kind, count in kind_counts.items() if kind != "idle" and count > 0}
    if active_counts:
        maximum = max(active_counts.values())
        preferences = {
            kind: min(1.0, count / max(1, maximum))
            for kind, count in active_counts.items()
            if count >= max(2, sum(active_counts.values()) * 0.02)
        }
        if kind_counts.get("idle", 0) > 0:
            preferences["idle"] = min(0.35, kind_counts["idle"] / max(1, sum(kind_counts.values())))
        return preferences
    origins = profile.get("action_origins", [])
    fallback = {
        action_kind(action)
        for index, action in enumerate(actions)
        if index < len(origins) and origins[index] == "human" and action_kind(action) != "idle"
    }
    return {kind: 1.0 for kind in fallback}


def load_cross_game_control_prior(exclude_profile_id: str = "") -> dict[str, float]:
    totals = {kind: 0.0 for kind in CONTROL_KINDS}
    weights = {kind: 0.0 for kind in CONTROL_KINDS}
    if not PROFILES_DIR.is_dir():
        return {}
    for directory in PROFILES_DIR.iterdir():
        if path_is_unsafe_managed_entry(directory) or not directory.is_dir() or directory.name == exclude_profile_id or not valid_profile_id(directory.name):
            continue
        paths = profile_paths(directory.name)
        try:
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
            profile = migrate_profile(candidate, directory.name)
            if profile is None:
                continue
            local = learned_control_preferences(profile, paths["db"])
            response = control_response_evidence(profile)
            sessions = int(profile.get("human_sessions", 0)) + int(profile.get("ai_sessions", 0))
            reliability = 0.30 + 0.70 * min(1.0, math.log1p(max(0, sessions)) / math.log(9.0))
            for kind in CONTROL_KINDS:
                preference = max(0.0, min(1.0, float(local.get(kind, 0.0))))
                response_value = max(0.0, min(1.0, float(response.get(kind, 0.0))))
                evidence = preference * 0.72 + response_value * 0.28
                if evidence <= 0.0:
                    continue
                totals[kind] += evidence * reliability
                weights[kind] += reliability
        except Exception:
            continue
    averaged = {kind: totals[kind] / weights[kind] for kind in CONTROL_KINDS if weights[kind] > 0.0}
    active = [value for kind, value in averaged.items() if kind != "idle" and value > 0.0]
    if not active:
        return {}
    maximum = max(active)
    return {kind: max(0.0, min(1.0, value / maximum)) for kind, value in averaged.items()}


def blend_control_preferences(
    local: dict[str, float],
    cross_game: dict[str, float],
    human_samples: int,
    cross_game_weight: float,
) -> dict[str, float]:
    local_confidence = min(1.0, math.log1p(max(0, int(human_samples))) / math.log(65.0))
    transfer_weight = max(0.0, min(1.0, float(cross_game_weight))) * (1.0 - local_confidence)
    result: dict[str, float] = {}
    for kind in CONTROL_KINDS:
        local_value = max(0.0, min(1.0, float(local.get(kind, 0.0))))
        transfer_value = max(0.0, min(1.0, float(cross_game.get(kind, 0.0))))
        value = local_value * (0.55 + 0.45 * local_confidence) + transfer_value * transfer_weight
        if value > 0.0:
            result[kind] = value
    active = [value for kind, value in result.items() if kind != "idle" and value > 0.0]
    if active:
        scale = max(1.0, max(active))
        result = {kind: max(0.0, min(1.0, value / scale)) for kind, value in result.items()}
    return result


def load_cross_game_scene_control_prior(exclude_profile_id: str = "") -> dict[str, dict[str, float]]:
    totals = {context: {kind: 0.0 for kind in CONTROL_KINDS} for context in SCENE_CONTEXTS}
    weights = {context: {kind: 0.0 for kind in CONTROL_KINDS} for context in SCENE_CONTEXTS}
    if not PROFILES_DIR.is_dir():
        return {}
    for directory in PROFILES_DIR.iterdir():
        if path_is_unsafe_managed_entry(directory) or not directory.is_dir() or directory.name == exclude_profile_id or not valid_profile_id(directory.name):
            continue
        paths = profile_paths(directory.name)
        try:
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
            profile = migrate_profile(candidate, directory.name)
            if profile is None:
                continue
            sessions = int(profile.get("human_sessions", 0)) + int(profile.get("ai_sessions", 0))
            profile_reliability = 0.25 + 0.75 * min(1.0, math.log1p(max(0, sessions)) / math.log(13.0))
            reward_root = profile.get("scene_control_reward_ema", {})
            count_root = profile.get("scene_control_reward_counts", {})
            for context in SCENE_CONTEXTS:
                reward_values = reward_root.get(context, {}) if isinstance(reward_root, dict) else {}
                count_values = count_root.get(context, {}) if isinstance(count_root, dict) else {}
                for kind in CONTROL_KINDS:
                    try:
                        reward = float(reward_values.get(kind, 0.0)) if isinstance(reward_values, dict) else 0.0
                        count = int(count_values.get(kind, 0)) if isinstance(count_values, dict) else 0
                    except (TypeError, ValueError):
                        continue
                    if count <= 0 or not math.isfinite(reward):
                        continue
                    evidence_confidence = min(1.0, math.log1p(count) / math.log(33.0))
                    weight = profile_reliability * evidence_confidence
                    totals[context][kind] += max(-1.0, min(1.0, reward)) * weight
                    weights[context][kind] += weight
        except Exception:
            continue
    result: dict[str, dict[str, float]] = {}
    for context in SCENE_CONTEXTS:
        context_values = {
            kind: max(-1.0, min(1.0, totals[context][kind] / weights[context][kind]))
            for kind in CONTROL_KINDS
            if weights[context][kind] > 0.0
        }
        if context_values:
            result[context] = context_values
    return result


def load_cross_game_scene_action_prior(
    exclude_profile_id: str = "",
) -> dict[str, dict[str, tuple[float, float]]]:
    contexts = ("__all__", *SCENE_CONTEXTS)
    totals: dict[str, dict[str, float]] = {context: {} for context in contexts}
    weights: dict[str, dict[str, float]] = {context: {} for context in contexts}
    if not PROFILES_DIR.is_dir():
        return {}
    for directory in PROFILES_DIR.iterdir():
        if path_is_unsafe_managed_entry(directory) or not directory.is_dir() or directory.name == exclude_profile_id or not valid_profile_id(directory.name):
            continue
        paths = profile_paths(directory.name)
        try:
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
            profile = migrate_profile(candidate, directory.name)
            if profile is None:
                continue
            actions = profile.get("actions", [])
            sessions = int(profile.get("human_sessions", 0)) + int(profile.get("ai_sessions", 0))
            profile_reliability = 0.25 + 0.75 * min(1.0, math.log1p(max(0, sessions)) / math.log(13.0))
            reward_values = profile.get("action_reward_ema", [])
            reward_counts = profile.get("action_reward_counts", [])
            effect_values = profile.get("action_effect_ema", [])
            effect_counts = profile.get("action_effect_counts", [])
            risk_values = profile.get("action_risk_ema", [])
            risk_counts = profile.get("action_risk_counts", [])
            for action_index, action in enumerate(actions):
                try:
                    reward = float(reward_values[action_index])
                    reward_count = int(reward_counts[action_index])
                    effect = float(effect_values[action_index])
                    effect_count = int(effect_counts[action_index])
                    risk = float(risk_values[action_index])
                    risk_count = int(risk_counts[action_index])
                except (IndexError, TypeError, ValueError):
                    continue
                evidence_count = max(reward_count, effect_count, risk_count)
                if evidence_count <= 0 or not all(math.isfinite(value) for value in (reward, effect, risk)):
                    continue
                confidence = min(1.0, math.log1p(evidence_count) / math.log(49.0))
                weight = profile_reliability * confidence
                value = max(-1.0, min(1.0, reward * 0.62 + effect * 0.30 - risk * 0.38))
                signature = action_signature(action)
                totals["__all__"][signature] = totals["__all__"].get(signature, 0.0) + value * weight
                weights["__all__"][signature] = weights["__all__"].get(signature, 0.0) + weight
            scene_reward_root = profile.get("scene_action_reward_ema", {})
            scene_count_root = profile.get("scene_action_reward_counts", {})
            for context in SCENE_CONTEXTS:
                scene_rewards = scene_reward_root.get(context, []) if isinstance(scene_reward_root, dict) else []
                scene_counts = scene_count_root.get(context, []) if isinstance(scene_count_root, dict) else []
                for action_index, action in enumerate(actions):
                    try:
                        reward = float(scene_rewards[action_index])
                        count = int(scene_counts[action_index])
                    except (IndexError, TypeError, ValueError):
                        continue
                    if count <= 0 or not math.isfinite(reward):
                        continue
                    confidence = min(1.0, math.log1p(count) / math.log(41.0))
                    weight = profile_reliability * confidence
                    signature = action_signature(action)
                    totals[context][signature] = totals[context].get(signature, 0.0) + max(-1.0, min(1.0, reward)) * weight
                    weights[context][signature] = weights[context].get(signature, 0.0) + weight
        except Exception:
            continue
    result: dict[str, dict[str, tuple[float, float]]] = {}
    for context in contexts:
        ranked: list[tuple[float, str, tuple[float, float]]] = []
        for signature, total in totals[context].items():
            weight = weights[context].get(signature, 0.0)
            if weight <= 0.0:
                continue
            value = max(-1.0, min(1.0, total / weight))
            confidence = max(0.0, min(1.0, weight / 2.5))
            ranked.append((weight, signature, (value, confidence)))
        if ranked:
            ranked.sort(key=lambda item: (-item[0], item[1]))
            result[context] = {signature: data for _, signature, data in ranked[:CROSS_GAME_ACTION_PRIOR_LIMIT]}
    return result


def cross_game_scene_action_values(
    prior: dict[str, dict[str, tuple[float, float]]],
    context: str,
    actions: list[dict],
) -> list[float]:
    general = prior.get("__all__", {}) if isinstance(prior, dict) else {}
    contextual = prior.get(context, {}) if isinstance(prior, dict) and context in SCENE_CONTEXTS else {}
    result: list[float] = []
    for action in actions:
        signature = action_signature(action)
        general_value, general_confidence = general.get(signature, (0.0, 0.0))
        context_value, context_confidence = contextual.get(signature, (0.0, 0.0))
        general_confidence = max(0.0, min(1.0, float(general_confidence)))
        context_confidence = max(0.0, min(1.0, float(context_confidence)))
        value = (
            float(context_value) * context_confidence
            + float(general_value) * general_confidence * (1.0 - context_confidence) * 0.55
        )
        result.append(max(-1.0, min(1.0, value)))
    return result


def blended_scene_control_evidence(
    profile: dict,
    context: str,
    cross_game_prior: dict[str, dict[str, float]],
    cross_game_weight: float,
) -> dict[str, float]:
    local = scene_control_response_evidence(profile, context)
    count_root = profile.get("scene_control_reward_counts", {})
    count_values = count_root.get(context, {}) if isinstance(count_root, dict) else {}
    local_count = 0
    if isinstance(count_values, dict):
        for value in count_values.values():
            try:
                local_count += max(0, int(value))
            except (TypeError, ValueError):
                pass
    local_confidence = min(1.0, math.log1p(local_count) / math.log(97.0))
    transfer = max(0.0, min(1.0, float(cross_game_weight))) * (1.0 - local_confidence)
    transferred = cross_game_prior.get(context, {}) if isinstance(cross_game_prior, dict) else {}
    return {
        kind: max(
            -1.0,
            min(
                1.0,
                float(local.get(kind, 0.0))
                + transfer * float(transferred.get(kind, 0.0)),
            ),
        )
        for kind in CONTROL_KINDS
    }


def control_response_evidence(profile: dict) -> dict[str, float]:
    reward_values = profile.get("control_reward_ema", {})
    count_values = profile.get("control_reward_counts", {})
    result: dict[str, float] = {}
    for kind in CONTROL_KINDS:
        try:
            reward = float(reward_values.get(kind, 0.0)) if isinstance(reward_values, dict) else 0.0
            count = int(count_values.get(kind, 0)) if isinstance(count_values, dict) else 0
        except (TypeError, ValueError):
            reward = 0.0
            count = 0
        if not math.isfinite(reward):
            reward = 0.0
        confidence = max(0.0, min(1.0, count / 18.0))
        result[kind] = max(-1.0, min(1.0, reward)) * confidence
    return result


def update_control_response(profile: dict, action_index: int, reward: float) -> None:
    if not isinstance(profile.get("control_reward_ema"), dict) or not isinstance(profile.get("control_reward_counts"), dict):
        ensure_action_metadata(profile)
    if not 0 <= action_index < len(profile.get("actions", [])):
        return
    kind = action_kind(profile["actions"][action_index])
    reward_values = profile["control_reward_ema"]
    count_values = profile["control_reward_counts"]
    count = int(count_values.get(kind, 0))
    previous = float(reward_values.get(kind, 0.0))
    bounded = max(-1.0, min(1.0, float(reward)))
    alpha = max(0.035, 1.0 / min(32, count + 1))
    reward_values[kind] = max(-1.0, min(1.0, previous + alpha * (bounded - previous)))
    count_values[kind] = min(1_000_000_000, count + 1)


def cold_start_probe_actions(profile: dict, control_preferences: dict[str, float]) -> list[int]:
    actions = profile.get("actions", [])
    origins = profile.get("action_origins", [])
    movement_keys = {0x57, 0x41, 0x53, 0x44, 0x25, 0x26, 0x27, 0x28}
    interaction_keys = {0x20, 0x0D, 0x45, 0x46, 0x51, 0x52}
    caps = {"idle": 1, "keyboard": 12, "pointer": 4, "click": 7, "wheel": 2, "mixed": 2}
    ranked: list[tuple[float, int, str]] = []
    for index, raw_action in enumerate(actions):
        action = normalized_action(raw_action)
        kind = action_kind(action)
        keys = set(action["keys"])
        score = 0.0
        if kind == "idle":
            score = 120.0
        elif kind == "keyboard":
            score = 76.0
            if keys and keys.issubset(movement_keys):
                score += 34.0 - max(0, len(keys) - 1) * 5.0
            elif keys & interaction_keys:
                score += 22.0
            if any(0x70 <= key <= 0x87 for key in keys):
                score -= 42.0
            if keys & {0x10, 0x11, 0x12} and not keys & movement_keys:
                score -= 24.0
        elif kind == "pointer":
            score = 70.0
            if abs(action["mouse_dx"]) + abs(action["mouse_dy"]) == 1:
                score += 10.0
        elif kind == "click":
            if "left" not in action["buttons"]:
                continue
            score = 62.0
            if action["mouse_x"] >= 0:
                center_distance = abs(action["mouse_x"] - MOUSE_GRID_WIDTH // 2) + abs(action["mouse_y"] - MOUSE_GRID_HEIGHT // 2)
                score += max(0.0, 18.0 - center_distance * 0.8)
            else:
                score += 8.0
            if action["repeat"] > 1:
                score -= 10.0
        elif kind == "mixed":
            score = 48.0
            if keys & movement_keys and "left" in action["buttons"]:
                score += 12.0
        else:
            continue
        origin = origins[index] if index < len(origins) else "human"
        if origin == "human":
            score += 18.0
        elif origin == "transfer":
            score += 8.0
        score += 10.0 * float(control_preferences.get(kind, 0.0))
        ranked.append((score, index, kind))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    buckets: dict[str, list[int]] = {kind: [] for kind in CONTROL_KINDS}
    for _, index, kind in ranked:
        if len(buckets[kind]) < caps.get(kind, 0):
            buckets[kind].append(index)
    selected: list[int] = []
    cursors = {kind: 0 for kind in CONTROL_KINDS}
    probe_order = ("idle", "keyboard", "pointer", "click", "keyboard", "mixed", "keyboard", "pointer", "click")
    while len(selected) < COLD_START_PROBE_LIMIT:
        progressed = False
        for kind in probe_order:
            position = cursors[kind]
            if position >= len(buckets[kind]):
                continue
            selected.append(buckets[kind][position])
            cursors[kind] = position + 1
            progressed = True
            if len(selected) >= COLD_START_PROBE_LIMIT:
                break
        if not progressed:
            break
    return selected


def choose_contextual_probe_action(
    profile: dict,
    candidates: list[int],
    blocked_actions: set[int],
    state_action_visits: dict[tuple[str, int], int],
    current_state_key: str,
    scene_biases: dict[str, float],
    contextual_weight: float,
    step: int,
) -> int | None:
    actions = profile.get("actions", [])
    rewards = profile.get("action_reward_ema", [])
    effects = profile.get("action_effect_ema", [])
    risks = profile.get("action_risk_ema", [])
    best_position = -1
    best_score = -math.inf
    count = max(1, len(candidates))
    for position, action_index in enumerate(candidates):
        if not 0 <= action_index < len(actions) or action_index in blocked_actions:
            continue
        visits = state_action_visits.get((current_state_key, action_index), 0)
        if visits >= 2:
            continue
        kind = action_kind(actions[action_index])
        score = 0.22 * (count - position) / count
        score += max(0.0, min(1.0, contextual_weight)) * float(scene_biases.get(kind, 0.0))
        if step == 0 and kind == "idle":
            score += 2.0
        try:
            score += 0.16 * float(rewards[action_index])
        except (IndexError, TypeError, ValueError):
            pass
        try:
            score += 0.18 * float(effects[action_index])
        except (IndexError, TypeError, ValueError):
            pass
        try:
            score -= 0.34 * float(risks[action_index])
        except (IndexError, TypeError, ValueError):
            pass
        score -= 0.18 * visits
        if score > best_score:
            best_score = score
            best_position = position
    if best_position < 0:
        candidates.clear()
        return None
    return candidates.pop(best_position)


def action_policy_bias(
    action: dict,
    origin: str,
    cold_start: bool,
    static_streak: int,
    scene_motion: float,
    step: int,
    control_preferences: dict[str, float],
) -> float:
    action = normalized_action(action)
    kind = action_kind(action)
    keys = set(action["keys"])
    movement_keys = {0x57, 0x41, 0x53, 0x44, 0x25, 0x26, 0x27, 0x28}
    bias = 0.0
    if origin == "human":
        bias += 0.20
    elif origin == "transfer":
        bias += 0.08
    if control_preferences:
        preference = float(control_preferences.get(kind, 0.0))
        if preference > 0.0:
            bias += 0.10 + min(0.14, preference * 0.14)
        elif origin != "human":
            bias -= 0.18
    if kind == "idle":
        bias += 0.06 if scene_motion > 0.035 and static_streak < 2 else -0.18
    elif kind == "keyboard":
        bias += 0.10
        if keys & movement_keys:
            bias += 0.12
        if len(keys) > 1:
            bias -= 0.03
        if keys and keys.issubset({0x10, 0x11, 0x12}):
            bias -= 0.28
    elif kind == "pointer":
        bias += 0.03
    elif kind == "click":
        bias -= 0.16 if static_streak < 2 else 0.02
        if "right" in action["buttons"]:
            bias -= 0.12
        if action["repeat"] > 1:
            bias += 0.05 if static_streak >= 5 else -0.12
    elif kind == "wheel":
        bias -= 0.22 if static_streak < 4 else 0.02
    elif kind == "mixed":
        bias += 0.04
        if keys & movement_keys:
            bias += 0.10
        if "right" in action["buttons"]:
            bias -= 0.10
    else:
        bias -= 0.10
    if cold_start and step < 36:
        if kind in ("keyboard", "mixed") and keys & movement_keys:
            bias += 0.12
        elif kind in ("click", "wheel"):
            bias -= 0.06
    if static_streak >= 6:
        if kind in ("click", "wheel") or 0x0D in keys or 0x20 in keys or 0x45 in keys:
            bias += min(0.42, 0.05 * static_streak)
        elif kind == "idle":
            bias -= min(0.45, 0.04 * static_streak)
    return max(-0.65, min(0.65, bias))


def action_safety_penalty(
    action: dict,
    origin: str,
    executable_name: str,
    static_streak: int,
) -> float:
    action = normalized_action(action)
    keys = set(action["keys"])
    movement_keys = {0x57, 0x41, 0x53, 0x44, 0x25, 0x26, 0x27, 0x28, 0x49, 0x4A, 0x4B, 0x4C}
    modifier_keys = {0x10, 0x11, 0x12}
    penalty = 0.0
    if keys and keys.issubset(modifier_keys):
        penalty += 0.55
    if 0x12 in keys and not keys & movement_keys:
        penalty += 0.35
    if any(0x70 <= key <= 0x87 for key in keys):
        penalty += 0.30
    if "x1" in action["buttons"] or "x2" in action["buttons"]:
        penalty += 0.80
    if "middle" in action["buttons"]:
        penalty += 0.28
    if "right" in action["buttons"]:
        penalty += 0.12 if static_streak >= 5 else 0.30
    if abs(action["mouse_wheel"]) >= 2 and static_streak < 4:
        penalty += 0.16
    if action["repeat"] > 1 and static_streak < 4:
        penalty += 0.10
    if executable_name in BROWSER_HOST_EXECUTABLES:
        if "right" in action["buttons"]:
            penalty += 0.22
        if "x1" in action["buttons"] or "x2" in action["buttons"]:
            penalty += 0.50
        if 0x12 in keys or any(0x70 <= key <= 0x87 for key in keys):
            penalty += 0.18
    if origin == "human":
        penalty *= 0.22
    elif origin == "transfer":
        penalty *= 0.65
    return max(0.0, min(1.25, penalty))


def target_action_blocked(action: dict, origin: str, executable_name: str) -> bool:
    action = normalized_action(action)
    keys = set(action["keys"])
    buttons = set(action["buttons"])
    origin = origin if origin in ("generic", "human", "transfer") else "generic"
    executable_name = executable_name.lower().strip()
    modifier_keys = {0x10, 0x11, 0x12}
    if origin != "human" and keys and keys.issubset(modifier_keys):
        return True
    if any(combination.issubset(keys) for combination in SYSTEM_BLOCKED_KEY_COMBINATIONS):
        return True
    if executable_name not in BROWSER_HOST_EXECUTABLES:
        return False
    if buttons & {"x1", "x2"}:
        return True
    if origin != "human" and "middle" in buttons:
        return True
    if 0x12 in keys and len(keys) > 1:
        return True
    if 0x11 in keys:
        if origin != "human" or bool(keys & BROWSER_BLOCKED_CTRL_KEYS):
            return True
    if origin != "human" and any(0x70 <= key <= 0x7B for key in keys):
        return True
    if origin != "human" and 0 <= action["mouse_y"] <= 2:
        return True
    return False


def frame_hash_distance(left: str, right: str) -> int:
    try:
        return (int(left, 16) ^ int(right, 16)).bit_count()
    except (TypeError, ValueError):
        return max(64, len(str(left)) * 4, len(str(right)) * 4)


def recent_hash_match(digest: str, recent_hashes: list[str], maximum_distance: int = 3) -> bool:
    return any(frame_hash_distance(digest, previous) <= maximum_distance for previous in recent_hashes)


def regional_change_metrics(previous: bytes, current: bytes) -> tuple[float, float, float, float]:
    if len(previous) != len(current) or len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    columns = 8
    rows = 6
    tile_changes: list[float] = []
    previous_total = 0
    current_total = 0
    for tile_y in range(rows):
        top = tile_y * FEATURE_HEIGHT // rows
        bottom = (tile_y + 1) * FEATURE_HEIGHT // rows
        for tile_x in range(columns):
            left = tile_x * FEATURE_WIDTH // columns
            right = (tile_x + 1) * FEATURE_WIDTH // columns
            difference_total = 0
            count = 0
            for y in range(top, bottom):
                offset = y * FEATURE_WIDTH
                for x in range(left, right):
                    before = previous[offset + x]
                    after = current[offset + x]
                    difference_total += abs(after - before)
                    previous_total += before
                    current_total += after
                    count += 1
            tile_changes.append(difference_total / max(1, count) / 255.0)
    activity = sum(tile_changes) / max(1, len(tile_changes))
    change_total = sum(tile_changes)
    top_count = max(1, len(tile_changes) // 4)
    concentration = sum(sorted(tile_changes, reverse=True)[:top_count]) / max(1e-9, change_total)
    center_values = []
    for tile_y in range(1, rows - 1):
        for tile_x in range(2, columns - 2):
            center_values.append(tile_changes[tile_y * columns + tile_x])
    center_activity = sum(center_values) / max(1, len(center_values))
    center_ratio = min(3.0, center_activity / max(0.002, activity))
    global_shift = abs(current_total - previous_total) / max(1, len(current)) / 255.0
    return activity, concentration, center_ratio, global_shift


def scene_progress_metrics(previous: bytes, current: bytes) -> tuple[float, float, float]:
    if len(previous) != len(current) or len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    hud_total = 0
    hud_count = 0
    world_total = 0
    world_count = 0
    side_total = 0
    side_count = 0
    top_limit = max(1, FEATURE_HEIGHT // 6)
    bottom_limit = FEATURE_HEIGHT - max(1, FEATURE_HEIGHT // 8)
    side_width = max(1, FEATURE_WIDTH // 12)
    for y in range(FEATURE_HEIGHT):
        offset = y * FEATURE_WIDTH
        for x in range(FEATURE_WIDTH):
            difference = abs(current[offset + x] - previous[offset + x]) / 255.0
            if y < top_limit or y >= bottom_limit:
                hud_total += difference
                hud_count += 1
            elif x < side_width or x >= FEATURE_WIDTH - side_width:
                side_total += difference
                side_count += 1
            else:
                world_total += difference
                world_count += 1
    world_change = world_total / max(1, world_count)
    hud_change = hud_total / max(1, hud_count)
    side_change = side_total / max(1, side_count)
    return world_change, hud_change, side_change


def observe_human_action(
    target: int,
    previous_cursor: tuple[int, int],
    mouse_wheel: int = 0,
    mouse_threshold: int = 3,
) -> tuple[dict, tuple[int, int]]:
    keys = [vk for vk in SAFE_KEY_VKS if user32.GetAsyncKeyState(vk) & 0x8001]
    button_states = {name: int(user32.GetAsyncKeyState(vk)) for name, vk in MOUSE_VKS.items()}
    buttons = [name for name, state in button_states.items() if state & 0x8001]
    pressed_buttons = {name for name, state in button_states.items() if state & 0x0001}
    current = cursor_position()
    dx_raw = current[0] - previous_cursor[0]
    dy_raw = current[1] - previous_cursor[1]

    def movement_step(value: int) -> int:
        magnitude = abs(value)
        if magnitude < mouse_threshold:
            return 0
        step = 2 if magnitude >= max(12, mouse_threshold * 4) else 1
        return step if value > 0 else -step

    dx = movement_step(dx_raw)
    dy = movement_step(dy_raw)
    mouse_x = -1
    mouse_y = -1
    position_click = bool(buttons) and (not (dx or dy) or bool(pressed_buttons))
    if position_click:
        left, top, width, height = window_capture_rect(target)
        if width > 0 and height > 0 and left <= current[0] < left + width and top <= current[1] < top + height:
            mouse_x = min(MOUSE_GRID_WIDTH - 1, max(0, int((current[0] - left) * MOUSE_GRID_WIDTH / width)))
            mouse_y = min(MOUSE_GRID_HEIGHT - 1, max(0, int((current[1] - top) * MOUSE_GRID_HEIGHT / height)))
    action = normalized_action(
        {
            "keys": keys,
            "buttons": buttons,
            "mouse_dx": dx,
            "mouse_dy": dy,
            "mouse_wheel": mouse_wheel,
            "mouse_x": mouse_x,
            "mouse_y": mouse_y,
        }
    )
    return action, current


def sleep_cancelable(seconds: float, stop_event: threading.Event | None = None, target: int = 0) -> bool:
    deadline = time.monotonic() + max(0.0, float(seconds))
    while time.monotonic() < deadline:
        if stop_event is not None and stop_event.is_set():
            return False
        if os.name == "nt" and esc_pressed():
            if stop_event is not None:
                stop_event.set()
            return False
        if target and (not window_exists(target) or foreground_window() != target):
            return False
        time.sleep(min(0.015, max(0.0, deadline - time.monotonic())))
    return True


def execute_action(
    target: int,
    action: dict,
    hold_seconds: float,
    mouse_step: int,
    stop_event: threading.Event | None = None,
) -> bool:
    if not window_exists(target) or foreground_window() != target:
        return False
    action = normalized_action(action)
    down: list = []
    up: list = []
    for vk in action["keys"]:
        down.append(keyboard_input(vk, False))
        up.insert(0, keyboard_input(vk, True))
    if action["mouse_x"] >= 0 and action["mouse_y"] >= 0:
        left, top, width, height = window_capture_rect(target)
        target_x = left + int((action["mouse_x"] + 0.5) * width / MOUSE_GRID_WIDTH)
        target_y = top + int((action["mouse_y"] + 0.5) * height / MOUSE_GRID_HEIGHT)
        if not user32.SetCursorPos(target_x, target_y):
            raise OSError("鼠标定位失败")
    elif action["mouse_dx"] or action["mouse_dy"]:
        down.append(mouse_input(action["mouse_dx"] * mouse_step, action["mouse_dy"] * mouse_step, MOUSEEVENTF_MOVE))
    if action["mouse_wheel"]:
        wheel_data = (action["mouse_wheel"] * 120) & 0xFFFFFFFF
        down.append(mouse_input(flags=MOUSEEVENTF_WHEEL, data=wheel_data))
    for name in action["buttons"]:
        if name == "left":
            down.append(mouse_input(flags=MOUSEEVENTF_LEFTDOWN))
            up.append(mouse_input(flags=MOUSEEVENTF_LEFTUP))
        elif name == "right":
            down.append(mouse_input(flags=MOUSEEVENTF_RIGHTDOWN))
            up.append(mouse_input(flags=MOUSEEVENTF_RIGHTUP))
        elif name == "middle":
            down.append(mouse_input(flags=MOUSEEVENTF_MIDDLEDOWN))
            up.append(mouse_input(flags=MOUSEEVENTF_MIDDLEUP))
        elif name == "x1":
            down.append(mouse_input(flags=MOUSEEVENTF_XDOWN, data=XBUTTON1))
            up.append(mouse_input(flags=MOUSEEVENTF_XUP, data=XBUTTON1))
        elif name == "x2":
            down.append(mouse_input(flags=MOUSEEVENTF_XDOWN, data=XBUTTON2))
            up.append(mouse_input(flags=MOUSEEVENTF_XUP, data=XBUTTON2))
    if not window_exists(target) or foreground_window() != target:
        return False
    if not down:
        return sleep_cancelable(
            max(0.01, min(0.35, float(hold_seconds))),
            stop_event,
            target,
        )
    held_keys = set(action["keys"])
    held_buttons = set(action["buttons"])
    repeat = max(1, min(3, int(action.get("repeat", 1))))
    sent_down = False
    try:
        for repetition in range(repeat):
            with INJECTED_INPUT_LOCK:
                INJECTED_KEYS.update(held_keys)
                INJECTED_BUTTONS.update(held_buttons)
                sent_down = bool(down)
                send_inputs(down)
            if down and not sleep_cancelable(max(0.01, min(0.35, float(hold_seconds))), stop_event, target):
                return False
            with INJECTED_INPUT_LOCK:
                released = not sent_down
                if sent_down:
                    try:
                        send_inputs(up)
                        released = True
                    except Exception:
                        released = False
                if released:
                    INJECTED_KEYS.difference_update(held_keys)
                    INJECTED_BUTTONS.difference_update(held_buttons)
                    sent_down = False
            if sent_down:
                return False
            if repetition + 1 < repeat and not sleep_cancelable(0.055, stop_event, target):
                return False
        return True
    finally:
        with INJECTED_INPUT_LOCK:
            released = not sent_down
            if sent_down:
                try:
                    send_inputs(up)
                    released = True
                except Exception:
                    released = False
            if released:
                INJECTED_KEYS.difference_update(held_keys)
                INJECTED_BUTTONS.difference_update(held_buttons)


def make_feature(
    current: bytes,
    previous: bytes | None,
    chroma_blue: bytes | None = None,
    chroma_red: bytes | None = None,
) -> bytes:
    if len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面特征尺寸无效")
    if chroma_blue is None:
        chroma_blue = bytes([128]) * COLOR_PIXELS
    if chroma_red is None:
        chroma_red = bytes([128]) * COLOR_PIXELS
    if len(chroma_blue) != COLOR_PIXELS or len(chroma_red) != COLOR_PIXELS:
        raise ValueError("画面颜色特征尺寸无效")
    if previous is None or len(previous) != len(current):
        difference = bytes(len(current))
        signed_change = bytes([128]) * len(current)
    else:
        difference = bytes(abs(a - b) for a, b in zip(current, previous))
        signed_change = bytes(
            max(0, min(255, (int(after) - int(before) + 256) // 2))
            for after, before in zip(current, previous)
        )
    return current + difference + signed_change + chroma_blue + chroma_red


def feature_motion(feature: bytes) -> float:
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    if len(feature) not in (LEGACY_FEATURE_DIM, V27_FEATURE_DIM, FEATURE_DIM):
        raise ValueError("画面特征尺寸无效")
    difference = feature[pixels:pixels * 2]
    return sum(difference) / max(1, len(difference)) / 255.0


def feature_chroma(feature: bytes) -> tuple[bytes, bytes]:
    normalized = normalize_feature_bytes(feature)
    start = V27_FEATURE_DIM
    return (
        normalized[start:start + COLOR_PIXELS],
        normalized[start + COLOR_PIXELS:start + COLOR_FEATURE_DIM],
    )


def chroma_perceptual_hash(chroma_blue: bytes, chroma_red: bytes) -> int:
    if len(chroma_blue) != COLOR_PIXELS or len(chroma_red) != COLOR_PIXELS:
        raise ValueError("画面颜色尺寸无效")
    columns = 5
    rows = 2
    bits = 0
    bit_index = 0
    for channel in (chroma_blue, chroma_red):
        samples: list[int] = []
        for row in range(rows):
            top = row * COLOR_HEIGHT // rows
            bottom = (row + 1) * COLOR_HEIGHT // rows
            for column in range(columns):
                left = column * COLOR_WIDTH // columns
                right = (column + 1) * COLOR_WIDTH // columns
                total = 0
                count = 0
                for y in range(top, bottom):
                    offset = y * COLOR_WIDTH
                    for x in range(left, right):
                        total += channel[offset + x]
                        count += 1
                samples.append(total // max(1, count))
        for row in range(rows):
            offset = row * columns
            for column in range(columns - 1):
                if samples[offset + column] >= samples[offset + column + 1]:
                    bits |= 1 << bit_index
                bit_index += 1
    return bits


def frame_hash(
    gray: bytes,
    chroma_blue: bytes | None = None,
    chroma_red: bytes | None = None,
) -> str:
    if len(gray) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    columns = 9
    rows = 8
    samples: list[int] = []
    for row in range(rows):
        top = row * FEATURE_HEIGHT // rows
        bottom = (row + 1) * FEATURE_HEIGHT // rows
        for column in range(columns):
            left = column * FEATURE_WIDTH // columns
            right = (column + 1) * FEATURE_WIDTH // columns
            total = 0
            count = 0
            for y in range(top, bottom):
                offset = y * FEATURE_WIDTH
                for x in range(left, right):
                    total += gray[offset + x]
                    count += 1
            samples.append(total // max(1, count))
    bits = 0
    bit_index = 0
    for row in range(rows):
        offset = row * columns
        for column in range(columns - 1):
            if samples[offset + column] >= samples[offset + column + 1]:
                bits |= 1 << bit_index
            bit_index += 1
    if chroma_blue is None or chroma_red is None:
        return f"{bits:016x}"
    color_bits = chroma_perceptual_hash(chroma_blue, chroma_red)
    return f"{bits:016x}{color_bits:04x}"



def state_key(gray: bytes, feature: bytes) -> str:
    motion = feature_motion(feature)
    brightness = sum(gray) / max(1, len(gray)) / 255.0
    motion_bucket = max(0, min(31, int(motion * 96.0)))
    brightness_bucket = max(0, min(15, int(brightness * 16.0)))
    chroma_blue, chroma_red = feature_chroma(feature)
    return f"{frame_hash(gray, chroma_blue, chroma_red)}:{motion_bucket:02x}:{brightness_bucket:x}"


def memory_state_key(gray: bytes, feature: bytes) -> str:
    chroma_blue, chroma_red = feature_chroma(feature)
    digest = int(frame_hash(gray, chroma_blue, chroma_red), 16)
    folded = 0
    while digest:
        folded ^= digest & 0xFFFFFFFF
        digest >>= 32
    folded &= 0xFFFFFFFF
    motion = feature_motion(feature)
    brightness = sum(gray) / max(1, len(gray)) / 255.0
    motion_bucket = max(0, min(15, int(motion * 48.0)))
    brightness_bucket = max(0, min(7, int(brightness * 8.0)))
    return f"{folded:08x}:{motion_bucket:x}:{brightness_bucket:x}"

def visual_change_metrics(previous: bytes, current: bytes) -> tuple[float, float, float]:
    if len(previous) != len(current) or len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    total_difference = 0
    changed = 0
    strong = 0
    brightness_previous = 0
    brightness_current = 0
    for before, after in zip(previous, current):
        difference = abs(after - before)
        total_difference += difference
        brightness_previous += before
        brightness_current += after
        if difference >= 10:
            changed += 1
        if difference >= 32:
            strong += 1
    pixel_count = len(current)
    motion = total_difference / max(1, pixel_count) / 255.0
    changed_ratio = changed / max(1, pixel_count)
    strong_ratio = strong / max(1, pixel_count)
    brightness_shift = abs(brightness_current - brightness_previous) / max(1, pixel_count) / 255.0
    useful_motion = motion * (0.35 + min(1.0, changed_ratio * 2.0))
    flicker = max(0.0, brightness_shift - motion * 0.55) + max(0.0, strong_ratio - 0.92) * 0.25
    return useful_motion, changed_ratio, flicker


def chroma_change_metrics(
    previous_blue: bytes,
    previous_red: bytes,
    current_blue: bytes,
    current_red: bytes,
) -> tuple[float, float]:
    if not (
        len(previous_blue) == len(previous_red) == len(current_blue) == len(current_red) == COLOR_PIXELS
    ):
        raise ValueError("画面颜色尺寸无效")
    total_difference = 0
    changed = 0
    for before_blue, before_red, after_blue, after_red in zip(
        previous_blue,
        previous_red,
        current_blue,
        current_red,
    ):
        blue_difference = abs(after_blue - before_blue)
        red_difference = abs(after_red - before_red)
        total_difference += blue_difference + red_difference
        if max(blue_difference, red_difference) >= 10:
            changed += 1
    motion = total_difference / max(1, COLOR_PIXELS * 2) / 255.0
    changed_ratio = changed / max(1, COLOR_PIXELS)
    useful_motion = motion * (0.40 + min(1.0, changed_ratio * 1.8))
    return max(0.0, min(1.0, useful_motion)), max(0.0, min(1.0, changed_ratio))


def estimate_visual_translation(previous: bytes, current: bytes, radius: int = 2) -> tuple[int, int, float]:
    if len(previous) != len(current) or len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    radius = max(1, min(4, int(radius)))
    margin = radius
    baseline_total = 0
    texture_total = 0
    samples = 0
    for y in range(margin, FEATURE_HEIGHT - margin):
        row = y * FEATURE_WIDTH
        for x in range(margin, FEATURE_WIDTH - margin):
            position = row + x
            baseline_total += abs(current[position] - previous[position])
            texture_total += abs(previous[position] - previous[position - 1])
            texture_total += abs(previous[position] - previous[position - FEATURE_WIDTH])
            samples += 1
    if samples <= 0:
        return 0, 0, 0.0
    baseline = baseline_total / samples
    texture = texture_total / (samples * 2.0) / 255.0
    if baseline < 2.0 or texture < 0.006:
        return 0, 0, 0.0
    best_dx = 0
    best_dy = 0
    best_error = baseline
    best_samples = samples
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            total = 0
            count = 0
            left = max(margin, -dx)
            right = min(FEATURE_WIDTH - margin, FEATURE_WIDTH - dx)
            top = max(margin, -dy)
            bottom = min(FEATURE_HEIGHT - margin, FEATURE_HEIGHT - dy)
            if left >= right or top >= bottom:
                continue
            for y in range(top, bottom):
                previous_row = y * FEATURE_WIDTH
                current_row = (y + dy) * FEATURE_WIDTH
                for x in range(left, right):
                    total += abs(previous[previous_row + x] - current[current_row + x + dx])
                    count += 1
            error = total / max(1, count)
            if error < best_error:
                best_error = error
                best_dx = dx
                best_dy = dy
                best_samples = count
    improvement = max(0.0, (baseline - best_error) / max(8.0, baseline))
    coverage = best_samples / max(1, samples)
    texture_confidence = min(1.0, texture * 7.0)
    confidence = improvement * coverage * texture_confidence
    if best_dx == 0 and best_dy == 0:
        confidence = 0.0
    return best_dx, best_dy, max(0.0, min(1.0, confidence))


def uniform_brightness_change(previous: bytes, current: bytes) -> float:
    if len(previous) != len(current) or len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    deltas = [int(after) - int(before) for before, after in zip(previous, current)]
    mean_delta = sum(deltas) / max(1, len(deltas))
    magnitude = abs(mean_delta)
    if magnitude < 5.0:
        return 0.0
    residual = sum(abs(delta - mean_delta) for delta in deltas) / max(1, len(deltas))
    uniformity = max(0.0, 1.0 - residual / max(8.0, magnitude * 1.35))
    intensity = min(1.0, magnitude / 64.0)
    return max(0.0, min(1.0, uniformity * intensity))


def channel_persistence_metrics(before: bytes, immediate: bytes, settled: bytes) -> tuple[float, float]:
    if not before or len(before) != len(immediate) or len(before) != len(settled):
        raise ValueError("画面尺寸无效")
    immediate_changed = 0
    persistent_changed = 0
    transient_changed = 0
    for start, first, final in zip(before, immediate, settled):
        first_delta = first - start
        final_delta = final - start
        first_active = abs(first_delta) >= 10
        final_active = abs(final_delta) >= 10
        if first_active:
            immediate_changed += 1
            same_direction = (first_delta >= 0) == (final_delta >= 0)
            if final_active and same_direction:
                persistent_changed += 1
            elif not final_active:
                transient_changed += 1
    persistence = persistent_changed / max(1, immediate_changed)
    transient = transient_changed / max(1, len(before))
    return max(0.0, min(1.0, persistence)), max(0.0, min(1.0, transient))


def visual_persistence_metrics(before: bytes, immediate: bytes, settled: bytes) -> tuple[float, float]:
    if len(before) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面尺寸无效")
    return channel_persistence_metrics(before, immediate, settled)


def chroma_persistence_metrics(
    before_blue: bytes,
    before_red: bytes,
    immediate_blue: bytes,
    immediate_red: bytes,
    settled_blue: bytes,
    settled_red: bytes,
) -> tuple[float, float]:
    if not all(
        len(channel) == COLOR_PIXELS
        for channel in (
            before_blue,
            before_red,
            immediate_blue,
            immediate_red,
            settled_blue,
            settled_red,
        )
    ):
        raise ValueError("画面颜色尺寸无效")
    return channel_persistence_metrics(
        before_blue + before_red,
        immediate_blue + immediate_red,
        settled_blue + settled_red,
    )


def path_is_unsafe_managed_entry(path: Path) -> bool:
    if path_is_link_or_junction(path):
        return True
    if not path.exists():
        return False
    try:
        return path.is_file() and int(path.stat(follow_symlinks=False).st_nlink) > 1
    except OSError:
        return True


def remove_unsafe_managed_entry(path: Path) -> None:
    junction_check = getattr(path, "is_junction", None)
    is_junction = False
    if callable(junction_check):
        try:
            is_junction = bool(junction_check())
        except OSError:
            is_junction = True
    if not is_junction and not path.exists() and not path.is_symlink():
        return
    if is_junction:
        os.rmdir(path)
    else:
        path.unlink()


def profile_paths(profile_id: str, repair_unsafe: bool = False) -> dict[str, Path]:
    if not valid_profile_id(profile_id):
        raise ValueError("游戏档案标识无效")
    profiles_root = PROFILES_DIR.resolve(strict=False)
    root = PROFILES_DIR / profile_id
    if path_is_unsafe_managed_entry(root):
        if not repair_unsafe:
            raise RuntimeError("游戏档案目录不能是链接、目录联接或硬链接")
        remove_unsafe_managed_entry(root)
    resolved_root = root.resolve(strict=False)
    if resolved_root == profiles_root or profiles_root not in resolved_root.parents:
        raise RuntimeError("游戏档案路径超出桌面 AnyGameAI 文件夹")
    paths = {
        "root": root,
        "profile": root / "profile.json",
        "db": root / "experience.sqlite3",
        "model": root / "model.npz",
    }
    managed_files = (
        paths["profile"],
        paths["db"],
        paths["model"],
        Path(str(paths["db"]) + "-wal"),
        Path(str(paths["db"]) + "-shm"),
    )
    for path in managed_files:
        if path_is_unsafe_managed_entry(path):
            if not repair_unsafe:
                raise RuntimeError("游戏档案文件不能是链接、目录联接或硬链接")
            remove_unsafe_managed_entry(path)
        resolved = path.resolve(strict=False)
        if resolved == resolved_root or resolved_root not in resolved.parents:
            raise RuntimeError("游戏档案文件路径越界")
    return paths


def default_profile(identity: dict) -> dict:
    actions = universal_actions()
    return {
        "schema": PROFILE_SCHEMA,
        "id": identity["id"],
        "name": identity.get("name", identity["id"]),
        "title": identity.get("title", ""),
        "window_class": identity.get("window_class", ""),
        "executable": identity.get("executable", ""),
        "created_at": now_text(),
        "updated_at": now_text(),
        "actions": actions,
        "action_origins": ["generic"] * len(actions),
        "universal_action_schema": UNIVERSAL_ACTION_SCHEMA,
        "action_hold_seconds": [float(DEFAULT_CONFIG["action_hold_seconds"])] * len(actions),
        "action_duration_counts": [0] * len(actions),
        "action_reward_ema": [0.0] * len(actions),
        "action_reward_counts": [0] * len(actions),
        "action_effect_ema": [0.0] * len(actions),
        "action_effect_counts": [0] * len(actions),
        "action_risk_ema": [0.0] * len(actions),
        "action_risk_counts": [0] * len(actions),
        "transitions": {},
        "action_pair_transitions": {},
        "trained_samples": 0,
        "training_rounds": 0,
        "human_sessions": 0,
        "ai_sessions": 0,
        "ai_reward_ema": 0.0,
        "last_ai_mean_reward": 0.0,
        "control_reward_ema": {kind: 0.0 for kind in CONTROL_KINDS},
        "control_reward_counts": {kind: 0 for kind in CONTROL_KINDS},
        "scene_control_reward_ema": {
            context: {kind: 0.0 for kind in CONTROL_KINDS}
            for context in SCENE_CONTEXTS
        },
        "scene_control_reward_counts": {
            context: {kind: 0 for kind in CONTROL_KINDS}
            for context in SCENE_CONTEXTS
        },
        "scene_action_reward_ema": {
            context: [0.0] * len(actions)
            for context in SCENE_CONTEXTS
        },
        "scene_action_reward_counts": {
            context: [0] * len(actions)
            for context in SCENE_CONTEXTS
        },
        "passive_motion_ema": 0.0,
        "passive_change_ema": 0.0,
        "passive_color_ema": 0.0,
        "needs_training": True,
    }


def ensure_action_metadata(profile: dict) -> None:
    action_count = len(profile.get("actions", []))
    default_hold = float(DEFAULT_CONFIG["action_hold_seconds"])
    hold_values = profile.get("action_hold_seconds")
    if not isinstance(hold_values, list):
        hold_values = []
    cleaned_holds = []
    for index in range(action_count):
        try:
            value = float(hold_values[index])
        except (IndexError, TypeError, ValueError):
            value = default_hold
        if not math.isfinite(value):
            value = default_hold
        cleaned_holds.append(max(0.02, min(1.5, value)))
    duration_counts = profile.get("action_duration_counts")
    if not isinstance(duration_counts, list):
        duration_counts = []
    cleaned_counts = []
    for index in range(action_count):
        try:
            value = int(duration_counts[index])
        except (IndexError, TypeError, ValueError):
            value = 0
        cleaned_counts.append(max(0, min(1_000_000_000, value)))
    transitions = profile.get("transitions")
    cleaned_transitions: dict[str, dict[str, int]] = {}
    if isinstance(transitions, dict):
        for previous_text, next_map in transitions.items():
            try:
                previous = int(previous_text)
            except (TypeError, ValueError):
                continue
            if not 0 <= previous < action_count or not isinstance(next_map, dict):
                continue
            cleaned_next: dict[str, int] = {}
            for next_text, count_value in next_map.items():
                try:
                    next_index = int(next_text)
                    count = int(count_value)
                except (TypeError, ValueError):
                    continue
                if 0 <= next_index < action_count and next_index != previous and count > 0:
                    cleaned_next[str(next_index)] = min(1_000_000_000, count)
            if cleaned_next:
                cleaned_transitions[str(previous)] = cleaned_next
    reward_values = profile.get("action_reward_ema")
    if not isinstance(reward_values, list):
        reward_values = []
    cleaned_rewards = []
    for index in range(action_count):
        try:
            value = float(reward_values[index])
        except (IndexError, TypeError, ValueError):
            value = 0.0
        if not math.isfinite(value):
            value = 0.0
        cleaned_rewards.append(max(-1.0, min(1.0, value)))
    reward_counts = profile.get("action_reward_counts")
    if not isinstance(reward_counts, list):
        reward_counts = []
    cleaned_reward_counts = []
    for index in range(action_count):
        try:
            value = int(reward_counts[index])
        except (IndexError, TypeError, ValueError):
            value = 0
        cleaned_reward_counts.append(max(0, min(1_000_000_000, value)))
    effect_values = profile.get("action_effect_ema")
    if not isinstance(effect_values, list):
        effect_values = []
    cleaned_effects = []
    for index in range(action_count):
        try:
            value = float(effect_values[index])
        except (IndexError, TypeError, ValueError):
            value = 0.0
        if not math.isfinite(value):
            value = 0.0
        cleaned_effects.append(max(0.0, min(1.0, value)))
    effect_counts = profile.get("action_effect_counts")
    if not isinstance(effect_counts, list):
        effect_counts = []
    cleaned_effect_counts = []
    for index in range(action_count):
        try:
            value = int(effect_counts[index])
        except (IndexError, TypeError, ValueError):
            value = 0
        cleaned_effect_counts.append(max(0, min(1_000_000_000, value)))
    risk_values = profile.get("action_risk_ema")
    if not isinstance(risk_values, list):
        risk_values = []
    cleaned_risks = []
    for index in range(action_count):
        try:
            value = float(risk_values[index])
        except (IndexError, TypeError, ValueError):
            value = 0.0
        if not math.isfinite(value):
            value = 0.0
        cleaned_risks.append(max(0.0, min(1.0, value)))
    risk_counts = profile.get("action_risk_counts")
    if not isinstance(risk_counts, list):
        risk_counts = []
    cleaned_risk_counts = []
    for index in range(action_count):
        try:
            value = int(risk_counts[index])
        except (IndexError, TypeError, ValueError):
            value = 0
        cleaned_risk_counts.append(max(0, min(1_000_000_000, value)))
    origin_values = profile.get("action_origins")
    if not isinstance(origin_values, list):
        origin_values = []
    cleaned_origins = []
    for index in range(action_count):
        value = str(origin_values[index]) if index < len(origin_values) else "human"
        cleaned_origins.append(value if value in ("generic", "human", "transfer") else "human")
    profile["action_hold_seconds"] = cleaned_holds
    profile["action_duration_counts"] = cleaned_counts
    profile["action_reward_ema"] = cleaned_rewards
    profile["action_reward_counts"] = cleaned_reward_counts
    profile["action_effect_ema"] = cleaned_effects
    profile["action_effect_counts"] = cleaned_effect_counts
    profile["action_risk_ema"] = cleaned_risks
    profile["action_risk_counts"] = cleaned_risk_counts
    profile["action_origins"] = cleaned_origins
    pair_transitions = profile.get("action_pair_transitions")
    cleaned_pair_transitions: dict[str, dict[str, int]] = {}
    if isinstance(pair_transitions, dict):
        pair_items: list[tuple[int, str, dict[str, int]]] = []
        for pair_text, next_map in pair_transitions.items():
            parts = str(pair_text).split(",")
            if len(parts) != 2 or not isinstance(next_map, dict):
                continue
            try:
                first = int(parts[0])
                second = int(parts[1])
            except (TypeError, ValueError):
                continue
            if not (0 <= first < action_count and 0 <= second < action_count):
                continue
            cleaned_next: dict[str, int] = {}
            for next_text, count_value in next_map.items():
                try:
                    next_index = int(next_text)
                    count = int(count_value)
                except (TypeError, ValueError):
                    continue
                if 0 <= next_index < action_count and count > 0:
                    cleaned_next[str(next_index)] = min(1_000_000_000, count)
            if cleaned_next:
                ranked_next = sorted(cleaned_next.items(), key=lambda item: (-item[1], int(item[0])))[:PAIR_TRANSITION_NEXT_LIMIT]
                cleaned_next = dict(ranked_next)
                pair_items.append((sum(cleaned_next.values()), f"{first},{second}", cleaned_next))
        pair_items.sort(key=lambda item: (-item[0], item[1]))
        cleaned_pair_transitions = {key: values for _, key, values in pair_items[:PAIR_TRANSITION_LIMIT]}
    profile["universal_action_schema"] = UNIVERSAL_ACTION_SCHEMA
    profile["transitions"] = cleaned_transitions
    profile["action_pair_transitions"] = cleaned_pair_transitions
    profile["human_sessions"] = max(0, int(profile.get("human_sessions", 0) or 0))
    profile["ai_sessions"] = max(0, int(profile.get("ai_sessions", 0) or 0))
    for reward_key in ("ai_reward_ema", "last_ai_mean_reward"):
        try:
            reward_value = float(profile.get(reward_key, 0.0) or 0.0)
        except (TypeError, ValueError):
            reward_value = 0.0
        if not math.isfinite(reward_value):
            reward_value = 0.0
        profile[reward_key] = max(-1.0, min(1.0, reward_value))
    raw_control_rewards = profile.get("control_reward_ema")
    raw_control_counts = profile.get("control_reward_counts")
    cleaned_control_rewards: dict[str, float] = {}
    cleaned_control_counts: dict[str, int] = {}
    for kind in CONTROL_KINDS:
        try:
            value = float(raw_control_rewards.get(kind, 0.0)) if isinstance(raw_control_rewards, dict) else 0.0
        except (TypeError, ValueError):
            value = 0.0
        if not math.isfinite(value):
            value = 0.0
        try:
            count = int(raw_control_counts.get(kind, 0)) if isinstance(raw_control_counts, dict) else 0
        except (TypeError, ValueError):
            count = 0
        cleaned_control_rewards[kind] = max(-1.0, min(1.0, value))
        cleaned_control_counts[kind] = max(0, min(1_000_000_000, count))
    profile["control_reward_ema"] = cleaned_control_rewards
    profile["control_reward_counts"] = cleaned_control_counts
    raw_scene_rewards = profile.get("scene_control_reward_ema")
    raw_scene_counts = profile.get("scene_control_reward_counts")
    cleaned_scene_rewards: dict[str, dict[str, float]] = {}
    cleaned_scene_counts: dict[str, dict[str, int]] = {}
    for context in SCENE_CONTEXTS:
        source_rewards = raw_scene_rewards.get(context, {}) if isinstance(raw_scene_rewards, dict) else {}
        source_counts = raw_scene_counts.get(context, {}) if isinstance(raw_scene_counts, dict) else {}
        context_rewards: dict[str, float] = {}
        context_counts: dict[str, int] = {}
        for kind in CONTROL_KINDS:
            try:
                value = float(source_rewards.get(kind, 0.0)) if isinstance(source_rewards, dict) else 0.0
            except (TypeError, ValueError):
                value = 0.0
            if not math.isfinite(value):
                value = 0.0
            try:
                count = int(source_counts.get(kind, 0)) if isinstance(source_counts, dict) else 0
            except (TypeError, ValueError):
                count = 0
            context_rewards[kind] = max(-1.0, min(1.0, value))
            context_counts[kind] = max(0, min(1_000_000_000, count))
        cleaned_scene_rewards[context] = context_rewards
        cleaned_scene_counts[context] = context_counts
    profile["scene_control_reward_ema"] = cleaned_scene_rewards
    profile["scene_control_reward_counts"] = cleaned_scene_counts
    raw_scene_action_rewards = profile.get("scene_action_reward_ema")
    raw_scene_action_counts = profile.get("scene_action_reward_counts")
    cleaned_scene_action_rewards: dict[str, list[float]] = {}
    cleaned_scene_action_counts: dict[str, list[int]] = {}
    for context in SCENE_CONTEXTS:
        source_rewards = raw_scene_action_rewards.get(context, []) if isinstance(raw_scene_action_rewards, dict) else []
        source_counts = raw_scene_action_counts.get(context, []) if isinstance(raw_scene_action_counts, dict) else []
        context_rewards: list[float] = []
        context_counts: list[int] = []
        for action_index in range(action_count):
            try:
                value = float(source_rewards[action_index])
            except (IndexError, TypeError, ValueError):
                value = 0.0
            if not math.isfinite(value):
                value = 0.0
            try:
                count = int(source_counts[action_index])
            except (IndexError, TypeError, ValueError):
                count = 0
            context_rewards.append(max(-1.0, min(1.0, value)))
            context_counts.append(max(0, min(1_000_000_000, count)))
        cleaned_scene_action_rewards[context] = context_rewards
        cleaned_scene_action_counts[context] = context_counts
    profile["scene_action_reward_ema"] = cleaned_scene_action_rewards
    profile["scene_action_reward_counts"] = cleaned_scene_action_counts
    try:
        passive_motion = float(profile.get("passive_motion_ema", 0.0) or 0.0)
    except (TypeError, ValueError):
        passive_motion = 0.0
    if not math.isfinite(passive_motion):
        passive_motion = 0.0
    profile["passive_motion_ema"] = max(0.0, min(1.0, passive_motion))
    try:
        passive_change = float(profile.get("passive_change_ema", 0.0) or 0.0)
    except (TypeError, ValueError):
        passive_change = 0.0
    if not math.isfinite(passive_change):
        passive_change = 0.0
    profile["passive_change_ema"] = max(0.0, min(1.0, passive_change))
    try:
        passive_color = float(profile.get("passive_color_ema", 0.0) or 0.0)
    except (TypeError, ValueError):
        passive_color = 0.0
    if not math.isfinite(passive_color):
        passive_color = 0.0
    profile["passive_color_ema"] = max(0.0, min(1.0, passive_color))


def action_metadata_ready(profile: dict) -> bool:
    actions = profile.get("actions")
    if not isinstance(actions, list):
        return False
    action_count = len(actions)
    fields = (
        "action_origins",
        "action_hold_seconds",
        "action_duration_counts",
        "action_reward_ema",
        "action_reward_counts",
        "action_effect_ema",
        "action_effect_counts",
        "action_risk_ema",
        "action_risk_counts",
    )
    if not all(isinstance(profile.get(field), list) and len(profile[field]) == action_count for field in fields):
        return False
    for root_name in ("scene_action_reward_ema", "scene_action_reward_counts"):
        root = profile.get(root_name)
        if not isinstance(root, dict):
            return False
        if any(not isinstance(root.get(context), list) or len(root[context]) != action_count for context in SCENE_CONTEXTS):
            return False
    return True


def prepare_action_metadata(profile: dict) -> None:
    if not action_metadata_ready(profile):
        ensure_action_metadata(profile)


def migrate_profile(data: object, profile_id: str) -> dict | None:
    if not isinstance(data, dict) or data.get("id") != profile_id:
        return None
    if not isinstance(data.get("schema"), int) or not 2 <= int(data["schema"]) <= PROFILE_SCHEMA:
        return None
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions or len(actions) > 1024:
        return None
    try:
        migrated = dict(data)
        migrated["schema"] = PROFILE_SCHEMA
        migrated["actions"] = [normalized_action(action) for action in actions]
        migrated.setdefault("trained_samples", 0)
        migrated.setdefault("training_rounds", 0)
        migrated.setdefault("needs_training", True)
        added = seed_universal_actions(migrated)
        if added:
            migrated["needs_training"] = True
        ensure_action_metadata(migrated)
        return migrated
    except Exception:
        return None


def matching_existing_profile_id(identity: dict) -> str | None:
    wanted_title = str(identity.get("identity_title", "")).lower()
    wanted_executable = str(identity.get("executable", "")).lower()
    wanted_class = str(identity.get("window_class", "")).lower()
    if not wanted_title or not PROFILES_DIR.is_dir():
        return None
    matches = []
    for directory in PROFILES_DIR.iterdir():
        if path_is_unsafe_managed_entry(directory) or not directory.is_dir() or not valid_profile_id(directory.name):
            continue
        try:
            paths = profile_paths(directory.name)
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
        except Exception:
            continue
        candidate_executable = str(candidate.get("executable", "")).lower()
        candidate_class = str(candidate.get("window_class", "")).lower()
        candidate_title = stable_identity_title(str(candidate.get("title", ""))).lower()
        if candidate_title != wanted_title:
            continue
        if wanted_executable and candidate_executable and candidate_executable != wanted_executable:
            continue
        if wanted_class and candidate_class and candidate_class != wanted_class:
            continue
        matches.append(directory.name)
    return matches[0] if len(matches) == 1 else None


def load_or_create_profile(identity: dict) -> tuple[dict, dict[str, Path]]:
    existing_id = matching_existing_profile_id(identity)
    if existing_id is not None:
        identity = dict(identity)
        identity["id"] = existing_id
    paths = profile_paths(identity["id"])
    paths["root"].mkdir(parents=True, exist_ok=True)
    profile = None
    try:
        candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
        profile = migrate_profile(candidate, identity["id"])
    except Exception:
        pass
    if profile is None:
        backup_corrupt(paths["profile"])
        profile = default_profile(identity)
    else:
        profile["name"] = identity.get("name", profile.get("name", identity["id"]))
        profile["title"] = identity.get("title", profile.get("title", ""))
        profile["window_class"] = identity.get("window_class", profile.get("window_class", ""))
        profile["executable"] = identity.get("executable", profile.get("executable", ""))
        profile["updated_at"] = now_text()
    atomic_write_json(paths["profile"], profile)
    index = load_index()
    index["profiles"][identity["id"]] = {
        "name": profile["name"],
        "executable": profile.get("executable", ""),
        "updated_at": profile["updated_at"],
    }
    save_index(index)
    ensure_database(paths["db"])
    return profile, paths


def save_profile(profile: dict, paths: dict[str, Path]) -> None:
    profile["updated_at"] = now_text()
    atomic_write_json(paths["profile"], profile)
    index = load_index()
    index["profiles"][profile["id"]] = {
        "name": profile.get("name", profile["id"]),
        "executable": profile.get("executable", ""),
        "updated_at": profile["updated_at"],
    }
    save_index(index)


def remove_sqlite_sidecars(path: Path) -> None:
    for suffix in ("-wal", "-shm"):
        try:
            Path(str(path) + suffix).unlink(missing_ok=True)
        except Exception:
            pass


def install_sqlite_cancel_handler(
    connection: sqlite3.Connection,
    stop_event: threading.Event | None,
) -> None:
    if stop_event is not None:
        connection.set_progress_handler(lambda: int(stop_event.is_set()), 2000)


def raise_if_sqlite_cancelled(
    error: sqlite3.DatabaseError,
    stop_event: threading.Event | None,
) -> None:
    if stop_event is not None and stop_event.is_set():
        raise RuntimeError("操作已取消") from error


def ensure_database(path: Path) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        connection = sqlite3.connect(path, timeout=20)
        try:
            result = connection.execute("PRAGMA quick_check").fetchone()
            if result and result[0] != "ok":
                raise sqlite3.DatabaseError(result[0])
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS samples(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    source TEXT NOT NULL CHECK(source IN ('human','ai')),
                    action INTEGER NOT NULL,
                    reward REAL NOT NULL DEFAULT 0,
                    feature_dim INTEGER NOT NULL,
                    feature BLOB NOT NULL
                )
                """
            )
            columns = [row[1] for row in connection.execute("PRAGMA table_info(samples)")]
            if columns != ["id", "created_at", "source", "action", "reward", "feature_dim", "feature"]:
                raise sqlite3.DatabaseError("经验数据库结构无效")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_samples_source_action ON samples(source, action)")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS state_values(
                    state TEXT NOT NULL,
                    action INTEGER NOT NULL,
                    value REAL NOT NULL,
                    visits INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(state, action)
                ) WITHOUT ROWID
                """
            )
            memory_columns = [row[1] for row in connection.execute("PRAGMA table_info(state_values)")]
            if memory_columns != ["state", "action", "value", "visits", "updated_at"]:
                connection.execute("DROP TABLE state_values")
                connection.execute(
                    """
                    CREATE TABLE state_values(
                        state TEXT NOT NULL,
                        action INTEGER NOT NULL,
                        value REAL NOT NULL,
                        visits INTEGER NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY(state, action)
                    ) WITHOUT ROWID
                    """
                )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_state_values_rank ON state_values(visits DESC, updated_at DESC)")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS human_state_actions(
                    state TEXT NOT NULL,
                    action INTEGER NOT NULL,
                    demonstrations INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(state, action)
                ) WITHOUT ROWID
                """
            )
            human_memory_columns = [
                row[1] for row in connection.execute("PRAGMA table_info(human_state_actions)")
            ]
            if human_memory_columns != ["state", "action", "demonstrations", "updated_at"]:
                connection.execute("DROP TABLE human_state_actions")
                connection.execute(
                    """
                    CREATE TABLE human_state_actions(
                        state TEXT NOT NULL,
                        action INTEGER NOT NULL,
                        demonstrations INTEGER NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY(state, action)
                    ) WITHOUT ROWID
                    """
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_human_state_actions_rank "
                "ON human_state_actions(demonstrations DESC, updated_at DESC)"
            )
            connection.commit()
        finally:
            connection.close()
        return False
    except Exception:
        backup_corrupt(path)
        remove_sqlite_sidecars(path)
        connection = sqlite3.connect(path, timeout=20)
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute(
                """
                CREATE TABLE samples(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    source TEXT NOT NULL CHECK(source IN ('human','ai')),
                    action INTEGER NOT NULL,
                    reward REAL NOT NULL DEFAULT 0,
                    feature_dim INTEGER NOT NULL,
                    feature BLOB NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX idx_samples_source_action ON samples(source, action)")
            connection.execute(
                """
                CREATE TABLE state_values(
                    state TEXT NOT NULL,
                    action INTEGER NOT NULL,
                    value REAL NOT NULL,
                    visits INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(state, action)
                ) WITHOUT ROWID
                """
            )
            connection.execute("CREATE INDEX idx_state_values_rank ON state_values(visits DESC, updated_at DESC)")
            connection.execute(
                """
                CREATE TABLE human_state_actions(
                    state TEXT NOT NULL,
                    action INTEGER NOT NULL,
                    demonstrations INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(state, action)
                ) WITHOUT ROWID
                """
            )
            connection.execute(
                "CREATE INDEX idx_human_state_actions_rank "
                "ON human_state_actions(demonstrations DESC, updated_at DESC)"
            )
            connection.commit()
        finally:
            connection.close()
        return True


def verify_experience_database(
    path: Path,
    action_count: int,
    scan_limit: int,
    stop_event: threading.Event | None,
) -> dict:
    ensure_database(path)
    checked = 0
    invalid_ids: list[int] = []
    removed = 0
    connection = sqlite3.connect(path, timeout=60)
    install_sqlite_cancel_handler(connection, stop_event)
    try:
        integrity_rows = [str(row[0]) for row in connection.execute("PRAGMA integrity_check").fetchall()]
        if integrity_rows != ["ok"]:
            raise sqlite3.DatabaseError("；".join(integrity_rows[:8]))
        cursor = connection.execute(
            "SELECT id, action, reward, feature_dim, feature FROM samples ORDER BY id DESC LIMIT ?",
            (max(1, int(scan_limit)),),
        )
        for sample_id, action, reward, feature_dim, blob in cursor:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            checked += 1
            try:
                action_index = int(action)
                reward_value = float(reward)
                stored_feature_dim = int(feature_dim)
                if not 0 <= action_index < action_count:
                    raise ValueError
                if not math.isfinite(reward_value) or not -1.0001 <= reward_value <= 1.0001:
                    raise ValueError
                if stored_feature_dim not in (LEGACY_FEATURE_DIM, V27_FEATURE_DIM, FEATURE_DIM) or not isinstance(blob, bytes):
                    raise ValueError
                normalize_feature_bytes(decompress_feature(blob, stored_feature_dim))
            except Exception:
                invalid_ids.append(int(sample_id))
                if len(invalid_ids) >= 512:
                    connection.executemany("DELETE FROM samples WHERE id=?", ((value,) for value in invalid_ids))
                    removed += len(invalid_ids)
                    invalid_ids.clear()
        if invalid_ids:
            connection.executemany("DELETE FROM samples WHERE id=?", ((value,) for value in invalid_ids))
            removed += len(invalid_ids)
        connection.commit()
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        return {"checked": checked, "removed": removed}
    except sqlite3.OperationalError as error:
        raise_if_sqlite_cancelled(error, stop_event)
        raise
    finally:
        connection.close()


def load_state_value_memory(path: Path, action_count: int, limit: int) -> dict[tuple[str, int], tuple[float, int]]:
    ensure_database(path)
    result: dict[tuple[str, int], tuple[float, int]] = {}
    connection = sqlite3.connect(path, timeout=20)
    try:
        rows = connection.execute(
            "SELECT state, action, value, visits FROM state_values "
            "WHERE action>=0 AND action<? AND visits>0 AND value>=-1.0001 AND value<=1.0001 "
            "ORDER BY visits DESC, updated_at DESC LIMIT ?",
            (max(0, int(action_count)), max(1, int(limit))),
        )
        for state, action, value, visits in rows:
            state_text = str(state)
            if STATE_MEMORY_KEY_PATTERN.fullmatch(state_text) is None:
                continue
            value_float = float(value)
            visits_int = int(visits)
            if not math.isfinite(value_float) or visits_int <= 0:
                continue
            result[(state_text, int(action))] = (
                max(-1.0, min(1.0, value_float)),
                min(1_000_000_000, visits_int),
            )
        return result
    finally:
        connection.close()


def load_human_action_memory(
    path: Path,
    action_count: int,
    limit: int = HUMAN_ACTION_MEMORY_LIMIT,
) -> dict[tuple[str, int], int]:
    ensure_database(path)
    result: dict[tuple[str, int], int] = {}
    connection = sqlite3.connect(path, timeout=20)
    try:
        rows = connection.execute(
            "SELECT state, action, demonstrations FROM human_state_actions "
            "WHERE action>=0 AND action<? AND demonstrations>0 "
            "ORDER BY demonstrations DESC, updated_at DESC LIMIT ?",
            (max(0, int(action_count)), max(1, int(limit))),
        )
        for state, action, demonstrations in rows:
            state_text = str(state)
            try:
                action_index = int(action)
                count = int(demonstrations)
            except (TypeError, ValueError, OverflowError):
                continue
            if (
                STATE_MEMORY_KEY_PATTERN.fullmatch(state_text) is None
                or not 0 <= action_index < action_count
                or count <= 0
            ):
                continue
            result[(state_text, action_index)] = min(1_000_000_000, count)
        return result
    finally:
        connection.close()


def update_human_action_memory(
    memory: dict[tuple[str, int], int],
    key: tuple[str, int],
) -> None:
    state, action = key
    if STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None or action < 0:
        return
    try:
        previous = max(0, int(memory.get(key, 0)))
    except (TypeError, ValueError, OverflowError):
        previous = 0
    memory[key] = min(1_000_000_000, previous + 1)


def save_human_action_memory(
    path: Path,
    memory: dict[tuple[str, int], int],
    dirty_keys: set[tuple[str, int]],
) -> int:
    if not dirty_keys:
        return 0
    timestamp = now_text()
    rows = []
    for key in dirty_keys:
        if key not in memory:
            continue
        state, action = key
        try:
            count = int(memory[key])
        except (TypeError, ValueError, OverflowError):
            continue
        if STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None or action < 0 or count <= 0:
            continue
        rows.append((state, int(action), min(1_000_000_000, count), timestamp))
    if not rows:
        dirty_keys.clear()
        return 0
    ensure_database(path)
    connection = sqlite3.connect(path, timeout=30)
    try:
        connection.executemany(
            "INSERT INTO human_state_actions(state, action, demonstrations, updated_at) "
            "VALUES(?,?,?,?) ON CONFLICT(state, action) DO UPDATE SET "
            "demonstrations=excluded.demonstrations, updated_at=excluded.updated_at",
            rows,
        )
        connection.commit()
    finally:
        connection.close()
    dirty_keys.difference_update((row[0], row[1]) for row in rows)
    return len(rows)


def build_state_visit_totals(
    memory: dict[tuple[str, int], tuple[float, int]],
) -> dict[str, int]:
    totals: dict[str, int] = {}
    for (state, action), (_, visits) in memory.items():
        if STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None or action < 0:
            continue
        try:
            count = max(0, min(1_000_000_000, int(visits)))
        except (TypeError, ValueError, OverflowError):
            continue
        totals[state] = min(1_000_000_000_000, totals.get(state, 0) + count)
    return totals


def persistent_frontier_reward(
    visit_totals: dict[str, int],
    state: str,
    scene_distance: float,
    meaningful_transition: bool,
    weight: float,
) -> float:
    bounded_weight = max(0.0, min(1.0, float(weight)))
    if (
        bounded_weight <= 0.0
        or not meaningful_transition
        or STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None
    ):
        return 0.0
    visits = max(0, int(visit_totals.get(state, 0)))
    novelty = 1.0 / math.sqrt(1.0 + visits / 6.0)
    transition_strength = min(1.0, max(0.0, float(scene_distance)) * 4.0)
    return bounded_weight * novelty * (0.35 + 0.65 * transition_strength)


def bootstrapped_state_reward(
    memory: dict[tuple[str, int], tuple[float, int]],
    next_state: str,
    action_count: int,
    reward: float,
    weight: float,
) -> float:
    bounded_reward = max(-1.0, min(1.0, float(reward)))
    bounded_weight = max(0.0, min(0.75, float(weight)))
    if (
        bounded_weight <= 0.0
        or action_count <= 0
        or STATE_MEMORY_KEY_PATTERN.fullmatch(next_state) is None
    ):
        return bounded_reward
    best_future = 0.0
    for action in range(action_count):
        value, visits = memory.get((next_state, action), (0.0, 0))
        try:
            value = max(-1.0, min(1.0, float(value)))
            visits = max(0, int(visits))
        except (TypeError, ValueError, OverflowError):
            continue
        confidence = min(1.0, math.log1p(visits) / math.log(17.0))
        best_future = max(best_future, value * confidence)
    future_room = max(0.0, 1.0 - abs(bounded_reward))
    return max(
        -1.0,
        min(1.0, bounded_reward + bounded_weight * best_future * future_room),
    )


def parse_state_memory_key(state: str) -> tuple[int, int, int] | None:
    if STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None:
        return None
    try:
        return int(state[:8], 16), int(state[9], 16), int(state[11], 16)
    except ValueError:
        return None


def state_memory_bucket(state_hash: int) -> int:
    return int(state_hash) >> max(0, 32 - STATE_MEMORY_BUCKET_BITS)


def state_memory_neighbor_buckets(bucket: int) -> tuple[int, ...]:
    mask = (1 << STATE_MEMORY_BUCKET_BITS) - 1
    values = [bucket & mask]
    for bit in range(STATE_MEMORY_BUCKET_BITS):
        values.append((bucket ^ (1 << bit)) & mask)
    return tuple(values)


def build_state_memory_index(
    memory: dict[tuple[str, int], tuple[float, int]],
) -> dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]]:
    index: dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]] = {}
    for (state, action), (value, visits) in memory.items():
        parsed = parse_state_memory_key(state)
        if parsed is None or action < 0 or visits <= 0 or not math.isfinite(float(value)):
            continue
        state_hash, motion_bucket, brightness_bucket = parsed
        bucket = state_memory_bucket(state_hash)
        bucket_values = index.setdefault(bucket, {})
        if len(bucket_values) >= STATE_MEMORY_BUCKET_LIMIT:
            continue
        bucket_values[(state, int(action))] = (
            state_hash,
            motion_bucket,
            brightness_bucket,
            max(-1.0, min(1.0, float(value))),
            min(1_000_000_000, int(visits)),
        )
    return index


def update_state_memory_index(
    index: dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]],
    key: tuple[str, int],
    value: float,
    visits: int,
) -> None:
    state, action = key
    parsed = parse_state_memory_key(state)
    if parsed is None or action < 0 or visits <= 0 or not math.isfinite(float(value)):
        return
    state_hash, motion_bucket, brightness_bucket = parsed
    bucket = state_memory_bucket(state_hash)
    bucket_values = index.setdefault(bucket, {})
    item_key = (state, int(action))
    if item_key not in bucket_values and len(bucket_values) >= STATE_MEMORY_BUCKET_LIMIT:
        return
    bucket_values[item_key] = (
        state_hash,
        motion_bucket,
        brightness_bucket,
        max(-1.0, min(1.0, float(value))),
        min(1_000_000_000, int(visits)),
    )


def approximate_state_action_values(
    index: dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]],
    state: str,
    action_count: int,
) -> dict[int, tuple[float, float]]:
    parsed = parse_state_memory_key(state)
    if parsed is None or action_count <= 0 or not index:
        return {}
    state_hash, motion_bucket, brightness_bucket = parsed
    weighted_values: dict[int, float] = {}
    total_weights: dict[int, float] = {}
    strongest_weights: dict[int, float] = {}
    for bucket in state_memory_neighbor_buckets(state_memory_bucket(state_hash)):
        for (_, action), payload in index.get(bucket, {}).items():
            if not 0 <= action < action_count:
                continue
            candidate_hash, candidate_motion, candidate_brightness, value, visits = payload
            distance = (state_hash ^ candidate_hash).bit_count()
            distance += abs(motion_bucket - candidate_motion) * 2
            distance += abs(brightness_bucket - candidate_brightness) * 2
            if distance <= 0 or distance > STATE_MEMORY_APPROXIMATE_DISTANCE:
                continue
            similarity = 1.0 - distance / (STATE_MEMORY_APPROXIMATE_DISTANCE + 1.0)
            confidence = min(1.0, math.log1p(visits) / math.log(33.0))
            weight = similarity * similarity * confidence
            if weight <= 0.0:
                continue
            weighted_values[action] = weighted_values.get(action, 0.0) + value * weight
            total_weights[action] = total_weights.get(action, 0.0) + weight
            strongest_weights[action] = max(strongest_weights.get(action, 0.0), weight)
    result: dict[int, tuple[float, float]] = {}
    for action, total_weight in total_weights.items():
        if total_weight <= 1e-9:
            continue
        value = weighted_values[action] / total_weight
        confidence = min(1.0, strongest_weights.get(action, 0.0) * 1.8 + math.log1p(total_weight) / math.log(5.0) * 0.35)
        result[action] = (max(-1.0, min(1.0, value)), max(0.0, min(1.0, confidence)))
    return result


def build_human_action_memory_index(
    memory: dict[tuple[str, int], int],
) -> dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]]:
    index: dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]] = {}
    for (state, action), demonstrations in memory.items():
        parsed = parse_state_memory_key(state)
        try:
            count = int(demonstrations)
        except (TypeError, ValueError, OverflowError):
            continue
        if parsed is None or action < 0 or count <= 0:
            continue
        state_hash, motion_bucket, brightness_bucket = parsed
        bucket_values = index.setdefault(state_memory_bucket(state_hash), {})
        if len(bucket_values) >= STATE_MEMORY_BUCKET_LIMIT:
            continue
        bucket_values[(state, int(action))] = (
            state_hash,
            motion_bucket,
            brightness_bucket,
            1.0,
            min(1_000_000_000, count),
        )
    return index


def human_action_memory_biases(
    memory: dict[tuple[str, int], int],
    index: dict[int, dict[tuple[str, int], tuple[int, int, int, float, int]]],
    state: str,
    action_count: int,
) -> list[float]:
    if action_count <= 0 or STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None:
        return [0.0] * max(0, int(action_count))
    counts: dict[int, int] = {}
    total = 0
    for action in range(action_count):
        try:
            count = max(0, int(memory.get((state, action), 0)))
        except (TypeError, ValueError, OverflowError):
            count = 0
        if count:
            counts[action] = count
            total += count
    biases = [0.0] * action_count
    if total:
        state_confidence = min(1.0, math.log1p(total) / math.log(17.0))
        for action, count in counts.items():
            frequency = count / total
            action_confidence = min(1.0, math.log1p(count) / math.log(9.0))
            value = state_confidence * (0.22 + 0.78 * math.sqrt(frequency))
            value *= 0.58 + 0.42 * action_confidence
            if action == 0:
                value *= 0.45
            biases[action] = max(0.0, min(1.0, value))
    approximate = approximate_state_action_values(index, state, action_count)
    approximate_scale = min(
        1.0,
        HUMAN_ACTION_APPROXIMATE_WEIGHT / max(1e-8, HUMAN_ACTION_MEMORY_WEIGHT),
    )
    for action, (_, confidence) in approximate.items():
        if not 0 <= action < action_count:
            continue
        value = approximate_scale * max(0.0, min(1.0, float(confidence)))
        if action == 0:
            value *= 0.45
        biases[action] = min(1.0, biases[action] + value * (1.0 - biases[action]))
    return biases


def update_state_value_memory(
    memory: dict[tuple[str, int], tuple[float, int]],
    key: tuple[str, int],
    reward: float,
    learning_rate: float,
) -> None:
    state, action = key
    if STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None or action < 0:
        return
    bounded_reward = max(-1.0, min(1.0, float(reward)))
    previous, count = memory.get(key, (0.0, 0))
    count = max(0, int(count))
    base_rate = max(0.01, min(1.0, float(learning_rate)))
    alpha = max(base_rate, 1.0 / min(24, count + 1))
    updated = float(previous) + alpha * (bounded_reward - float(previous))
    memory[key] = (max(-1.0, min(1.0, updated)), min(1_000_000_000, count + 1))


def save_state_value_memory(
    path: Path,
    memory: dict[tuple[str, int], tuple[float, int]],
    dirty_keys: set[tuple[str, int]],
) -> int:
    if not dirty_keys:
        return 0
    rows = []
    timestamp = now_text()
    for key in dirty_keys:
        if key not in memory:
            continue
        state, action = key
        value, visits = memory[key]
        if STATE_MEMORY_KEY_PATTERN.fullmatch(state) is None or action < 0:
            continue
        if not math.isfinite(float(value)) or int(visits) <= 0:
            continue
        rows.append((state, int(action), max(-1.0, min(1.0, float(value))), min(1_000_000_000, int(visits)), timestamp))
    if not rows:
        dirty_keys.clear()
        return 0
    ensure_database(path)
    connection = sqlite3.connect(path, timeout=30)
    try:
        connection.executemany(
            "INSERT INTO state_values(state, action, value, visits, updated_at) VALUES(?,?,?,?,?) "
            "ON CONFLICT(state, action) DO UPDATE SET value=excluded.value, visits=excluded.visits, updated_at=excluded.updated_at",
            rows,
        )
        connection.commit()
    finally:
        connection.close()
    dirty_keys.difference_update((row[0], row[1]) for row in rows)
    return len(rows)


def compact_state_values(
    path: Path,
    limit: int,
    action_count: int,
    stop_event: threading.Event | None = None,
) -> dict:
    ensure_database(path)
    limit = max(1, int(limit))
    connection = sqlite3.connect(path, timeout=60)
    install_sqlite_cancel_handler(connection, stop_event)
    try:
        before = int(connection.execute("SELECT COUNT(*) FROM state_values").fetchone()[0])
        connection.execute(
            "DELETE FROM state_values WHERE action<0 OR action>=? OR visits<=0 OR visits>1000000000 "
            "OR value IS NULL OR value<-1.0001 OR value>1.0001 OR length(state)<>12 "
            "OR substr(state,9,1)<>':' OR substr(state,11,1)<>':' "
            "OR substr(state,1,8) GLOB '*[^0-9a-f]*' "
            "OR substr(state,10,1) NOT GLOB '[0-9a-f]' "
            "OR substr(state,12,1) NOT GLOB '[0-7]'",
            (max(0, int(action_count)),),
        )
        current = int(connection.execute("SELECT COUNT(*) FROM state_values").fetchone()[0])
        excess = max(0, current - limit)
        if excess:
            connection.execute(
                "DELETE FROM state_values WHERE (state, action) IN ("
                "SELECT state, action FROM state_values ORDER BY visits ASC, updated_at ASC LIMIT ?)",
                (excess,),
            )
        connection.commit()
        after = int(connection.execute("SELECT COUNT(*) FROM state_values").fetchone()[0])
        return {"records": after, "removed": before - after}
    except sqlite3.OperationalError as error:
        raise_if_sqlite_cancelled(error, stop_event)
        raise
    finally:
        connection.close()


def compact_human_action_memory(
    path: Path,
    limit: int,
    action_count: int,
    stop_event: threading.Event | None = None,
) -> dict:
    ensure_database(path)
    limit = max(1, int(limit))
    connection = sqlite3.connect(path, timeout=60)
    install_sqlite_cancel_handler(connection, stop_event)
    try:
        before = int(connection.execute("SELECT COUNT(*) FROM human_state_actions").fetchone()[0])
        connection.execute(
            "DELETE FROM human_state_actions WHERE action<0 OR action>=? "
            "OR demonstrations<=0 OR demonstrations>1000000000 OR length(state)<>12 "
            "OR substr(state,9,1)<>':' OR substr(state,11,1)<>':' "
            "OR substr(state,1,8) GLOB '*[^0-9a-f]*' "
            "OR substr(state,10,1) NOT GLOB '[0-9a-f]' "
            "OR substr(state,12,1) NOT GLOB '[0-7]'",
            (max(0, int(action_count)),),
        )
        current = int(connection.execute("SELECT COUNT(*) FROM human_state_actions").fetchone()[0])
        excess = max(0, current - limit)
        if excess:
            connection.execute(
                "DELETE FROM human_state_actions WHERE (state, action) IN ("
                "SELECT state, action FROM human_state_actions "
                "ORDER BY demonstrations ASC, updated_at ASC LIMIT ?)",
                (excess,),
            )
        connection.commit()
        after = int(connection.execute("SELECT COUNT(*) FROM human_state_actions").fetchone()[0])
        return {"records": after, "removed": before - after}
    except sqlite3.OperationalError as error:
        raise_if_sqlite_cancelled(error, stop_event)
        raise
    finally:
        connection.close()


def compress_feature(feature: bytes) -> bytes:
    return zlib.compress(feature, level=3)


def normalize_feature_bytes(feature: bytes) -> bytes:
    if len(feature) == FEATURE_DIM:
        return feature
    if len(feature) == V27_FEATURE_DIM:
        return feature + bytes([128]) * COLOR_FEATURE_DIM
    if len(feature) == LEGACY_FEATURE_DIM:
        return (
            feature
            + bytes([128]) * (FEATURE_WIDTH * FEATURE_HEIGHT)
            + bytes([128]) * COLOR_FEATURE_DIM
        )
    raise ValueError("经验特征尺寸错误")


def decompress_feature(blob: bytes, expected_dim: int) -> bytes:
    if len(blob) > MAX_COMPRESSED_FEATURE_BYTES:
        raise ValueError("经验特征压缩数据过大")
    decompressor = zlib.decompressobj()
    raw = decompressor.decompress(blob, expected_dim + 1)
    if len(raw) > expected_dim or decompressor.unconsumed_tail:
        raise ValueError("经验特征尺寸错误")
    raw += decompressor.flush()
    if len(raw) != expected_dim or not decompressor.eof or decompressor.unused_data:
        raise ValueError("经验特征尺寸错误")
    return raw


def insert_samples(path: Path, rows: list[tuple[str, str, int, float, int, bytes]]) -> None:
    if not rows:
        return
    connection = sqlite3.connect(path, timeout=30)
    try:
        connection.executemany(
            "INSERT INTO samples(created_at, source, action, reward, feature_dim, feature) VALUES(?,?,?,?,?,?)",
            rows,
        )
        connection.commit()
    finally:
        connection.close()


def count_samples(path: Path) -> tuple[int, int]:
    ensure_database(path)
    connection = sqlite3.connect(path, timeout=20)
    try:
        total = int(connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0])
        human = int(connection.execute("SELECT COUNT(*) FROM samples WHERE source='human'").fetchone()[0])
        return total, human
    finally:
        connection.close()


def compact_experience(
    path: Path,
    limit: int,
    action_count: int,
    stop_event: threading.Event | None = None,
) -> dict:
    ensure_database(path)
    connection = sqlite3.connect(path, timeout=60)
    install_sqlite_cancel_handler(connection, stop_event)
    try:
        before = int(connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0])
        connection.execute(
            "DELETE FROM samples WHERE feature_dim NOT IN (?,?,?) OR action<0 OR action>=? OR length(feature)>? "
            "OR reward IS NULL OR reward<-1.0001 OR reward>1.0001",
            (LEGACY_FEATURE_DIM, V27_FEATURE_DIM, FEATURE_DIM, action_count, MAX_COMPRESSED_FEATURE_BYTES),
        )
        try:
            connection.execute(
                """
                DELETE FROM samples WHERE id IN (
                    SELECT id FROM (
                        SELECT id, source,
                               ROW_NUMBER() OVER (
                                   PARTITION BY source, action, feature,
                                                CASE WHEN source='ai' AND reward<0 THEN -1
                                                     WHEN source='ai' AND reward>0 THEN 1 ELSE 0 END
                                   ORDER BY CASE WHEN source='human' THEN id ELSE ABS(reward) END DESC, id DESC
                               ) AS duplicate_rank
                        FROM samples
                    )
                    WHERE duplicate_rank > CASE WHEN source='human' THEN 4 ELSE 2 END
                )
                """
            )
        except sqlite3.DatabaseError as error:
            raise_if_sqlite_cancelled(error, stop_event)
            pass
        human_count = int(connection.execute("SELECT COUNT(*) FROM samples WHERE source='human'").fetchone()[0])
        ai_count = int(connection.execute("SELECT COUNT(*) FROM samples WHERE source='ai'").fetchone()[0])
        ai_reserve = min(ai_count, max(0, int(limit * 0.20)))
        human_keep = min(human_count, max(0, limit - ai_reserve))
        ai_keep = min(ai_count, max(0, limit - human_keep))

        if human_count > human_keep:
            if human_keep <= 0:
                connection.execute("DELETE FROM samples WHERE source='human'")
            else:
                cutoff = connection.execute(
                    "SELECT id FROM samples WHERE source='human' ORDER BY id DESC LIMIT 1 OFFSET ?",
                    (human_keep - 1,),
                ).fetchone()
                if cutoff:
                    connection.execute("DELETE FROM samples WHERE source='human' AND id<?", (int(cutoff[0]),))

        if ai_count > ai_keep:
            if ai_keep <= 0:
                connection.execute("DELETE FROM samples WHERE source='ai'")
            else:
                ai_rows = [
                    (int(sample_id), int(action), float(reward))
                    for sample_id, action, reward in connection.execute(
                        "SELECT id, action, reward FROM samples WHERE source='ai' ORDER BY id"
                    )
                ]
                grouped: dict[int, list[tuple[int, float]]] = {}
                for sample_id, action, reward in ai_rows:
                    grouped.setdefault(action, []).append((sample_id, reward))
                keep_ids: set[int] = set()
                active_actions = max(1, len(grouped))
                per_view = max(1, min(12, ai_keep // max(1, active_actions * 3)))

                def add_candidates(candidates, quota: int) -> None:
                    added = 0
                    for sample_id, _ in candidates:
                        if len(keep_ids) >= ai_keep or added >= quota:
                            break
                        if sample_id not in keep_ids:
                            keep_ids.add(sample_id)
                            added += 1

                for records in grouped.values():
                    add_candidates(reversed(records), per_view)
                    add_candidates(sorted(records, key=lambda item: (item[1], item[0]), reverse=True), per_view)
                    add_candidates(sorted(records, key=lambda item: (item[1], -item[0])), per_view)

                if len(keep_ids) < ai_keep:
                    oldest_id = ai_rows[0][0] if ai_rows else 0
                    newest_id = ai_rows[-1][0] if ai_rows else 1
                    id_span = max(1, newest_id - oldest_id)
                    ranked = sorted(
                        ai_rows,
                        key=lambda item: (
                            abs(item[2]) * 0.72 + ((item[0] - oldest_id) / id_span) * 0.28,
                            item[0],
                        ),
                        reverse=True,
                    )
                    for sample_id, _, _ in ranked:
                        if len(keep_ids) >= ai_keep:
                            break
                        keep_ids.add(sample_id)
                connection.execute("CREATE TEMP TABLE keep_ai_ids(id INTEGER PRIMARY KEY)")
                connection.executemany(
                    "INSERT OR IGNORE INTO keep_ai_ids(id) VALUES(?)",
                    ((sample_id,) for sample_id in keep_ids),
                )
                connection.execute(
                    "DELETE FROM samples WHERE source='ai' AND id NOT IN (SELECT id FROM keep_ai_ids)"
                )
                connection.execute("DROP TABLE keep_ai_ids")

        connection.commit()
        after = int(connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0])
        removed = before - after
        if removed > max(1000, before // 10):
            connection.execute("VACUUM")
        human = int(connection.execute("SELECT COUNT(*) FROM samples WHERE source='human'").fetchone()[0])
        ai = after - human
        return {"records": after, "human": human, "ai": ai, "removed": removed}
    except sqlite3.OperationalError as error:
        raise_if_sqlite_cancelled(error, stop_event)
        raise
    finally:
        connection.close()


def nearest_action_index(actions: list[dict], candidate: dict) -> int:
    candidate = normalized_action(candidate)
    candidate_keys = set(candidate["keys"])
    candidate_buttons = set(candidate["buttons"])
    best_index = 0
    best_score = -10_000.0
    for index, action in enumerate(actions):
        action = normalized_action(action)
        keys = set(action["keys"])
        buttons = set(action["buttons"])
        score = 3.0 * len(keys & candidate_keys) - 2.0 * len(keys ^ candidate_keys)
        score += 2.0 * len(buttons & candidate_buttons) - 2.0 * len(buttons ^ candidate_buttons)
        score += 1.5 if action["mouse_dx"] == candidate["mouse_dx"] else -0.5
        score += 1.5 if action["mouse_dy"] == candidate["mouse_dy"] else -0.5
        score += 1.3 if action["mouse_wheel"] == candidate["mouse_wheel"] else -0.7
        score += 1.0 if action["repeat"] == candidate["repeat"] else -0.8
        if action["mouse_x"] >= 0 and candidate["mouse_x"] >= 0:
            distance = abs(action["mouse_x"] - candidate["mouse_x"]) + abs(action["mouse_y"] - candidate["mouse_y"])
            score += max(-4.0, 4.0 - distance * 0.35)
        elif action["mouse_x"] != candidate["mouse_x"]:
            score -= 2.0
        if score > best_score:
            best_score = score
            best_index = index
    return best_index


def register_action(profile: dict, candidate: dict, max_actions: int, origin: str = "human") -> tuple[int, bool]:
    candidate = normalized_action(candidate)
    signature = action_signature(candidate)
    ensure_action_metadata(profile)
    normalized_origin = origin if origin in ("generic", "human", "transfer") else "human"
    for index, action in enumerate(profile["actions"]):
        if action_signature(action) == signature:
            if normalized_origin == "human":
                profile["action_origins"][index] = "human"
            return index, False
    if len(profile["actions"]) < max_actions:
        profile["actions"].append(candidate)
        profile["action_origins"].append(normalized_origin)
        ensure_action_metadata(profile)
        return len(profile["actions"]) - 1, True
    return nearest_action_index(profile["actions"], candidate), False


def actions_hash(actions: list[dict]) -> str:
    text = json.dumps(actions, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def record_transition(
    profile: dict,
    previous: int,
    current: int,
    previous_previous: int | None = None,
    weight: int = 1,
) -> None:
    action_count = len(profile.get("actions", []))
    if previous == current or not (0 <= previous < action_count) or not (0 <= current < action_count):
        return
    increment = max(1, min(1000, int(weight)))
    transitions = profile.setdefault("transitions", {})
    next_map = transitions.setdefault(str(previous), {})
    next_map[str(current)] = min(1_000_000_000, int(next_map.get(str(current), 0)) + increment)
    if previous_previous is None or not 0 <= int(previous_previous) < action_count:
        return
    pair_transitions = profile.setdefault("action_pair_transitions", {})
    pair_key = f"{int(previous_previous)},{previous}"
    if pair_key not in pair_transitions and len(pair_transitions) >= PAIR_TRANSITION_LIMIT:
        weakest_key = min(
            pair_transitions,
            key=lambda key: sum(max(0, int(value)) for value in pair_transitions.get(key, {}).values()),
        )
        if sum(max(0, int(value)) for value in pair_transitions.get(weakest_key, {}).values()) >= increment:
            return
        pair_transitions.pop(weakest_key, None)
    pair_map = pair_transitions.setdefault(pair_key, {})
    if str(current) not in pair_map and len(pair_map) >= PAIR_TRANSITION_NEXT_LIMIT:
        weakest_next = min(pair_map, key=lambda key: int(pair_map.get(key, 0)))
        if int(pair_map.get(weakest_next, 0)) >= increment:
            return
        pair_map.pop(weakest_next, None)
    pair_map[str(current)] = min(1_000_000_000, int(pair_map.get(str(current), 0)) + increment)


def record_action_duration(profile: dict, action_index: int, duration_seconds: float) -> None:
    prepare_action_metadata(profile)
    if not 0 <= action_index < len(profile["actions"]):
        return
    duration = max(0.02, min(1.5, float(duration_seconds)))
    count = int(profile["action_duration_counts"][action_index])
    old = float(profile["action_hold_seconds"][action_index])
    weight = min(64, count)
    profile["action_hold_seconds"][action_index] = (old * weight + duration) / (weight + 1)
    profile["action_duration_counts"][action_index] = min(1_000_000_000, count + 1)


def learned_action_hold(profile: dict, action_index: int, configured_hold: float) -> float:
    prepare_action_metadata(profile)
    learned = float(profile["action_hold_seconds"][action_index])
    count = int(profile["action_duration_counts"][action_index])
    confidence = min(0.8, count / 20.0)
    value = configured_hold * (1.0 - confidence) + learned * confidence
    return max(0.02, min(0.65, value))


def adaptive_action_hold(
    profile: dict,
    action_index: int,
    configured_hold: float,
    scene_motion: float,
    static_streak: int,
    strength: float,
) -> float:
    base = learned_action_hold(profile, action_index, configured_hold)
    action = normalized_action(profile["actions"][action_index])
    kind = action_kind(action)
    strength = max(0.0, min(1.0, float(strength)))
    effect = float(profile["action_effect_ema"][action_index])
    effect_count = int(profile["action_effect_counts"][action_index])
    risk = float(profile["action_risk_ema"][action_index])
    risk_count = int(profile["action_risk_counts"][action_index])
    effect_confidence = min(1.0, math.log1p(max(0, effect_count)) / math.log(25.0))
    risk_confidence = min(1.0, math.log1p(max(0, risk_count)) / math.log(25.0))
    multiplier = 1.0
    if kind in ("keyboard", "mixed"):
        multiplier += strength * (0.38 * effect * effect_confidence - 0.28 * risk * risk_confidence)
        if static_streak >= 5:
            multiplier += strength * min(0.40, static_streak * 0.025)
    elif kind == "pointer":
        multiplier -= strength * 0.18
    elif kind in ("click", "wheel"):
        multiplier -= strength * 0.30
        if action["repeat"] > 1 or static_streak >= 7:
            multiplier += strength * 0.16
    elif kind == "idle":
        multiplier = 0.70 if scene_motion < 0.02 else 1.10
    if scene_motion >= 0.08 and kind != "idle":
        multiplier -= strength * min(0.25, scene_motion * 1.5)
    return max(0.02, min(0.75, base * max(0.45, multiplier)))


def update_action_reward(profile: dict, action_index: int, reward: float) -> None:
    prepare_action_metadata(profile)
    if not 0 <= action_index < len(profile["actions"]):
        return
    bounded = max(-1.0, min(1.0, float(reward)))
    count = int(profile["action_reward_counts"][action_index])
    previous = float(profile["action_reward_ema"][action_index])
    alpha = max(0.02, 1.0 / min(64, count + 1))
    profile["action_reward_ema"][action_index] = previous + alpha * (bounded - previous)
    profile["action_reward_counts"][action_index] = min(1_000_000_000, count + 1)


def update_action_effect(profile: dict, action_index: int, effect: float) -> None:
    prepare_action_metadata(profile)
    if not 0 <= action_index < len(profile["actions"]):
        return
    bounded = max(0.0, min(1.0, float(effect)))
    count = int(profile["action_effect_counts"][action_index])
    previous = float(profile["action_effect_ema"][action_index])
    alpha = max(0.035, 1.0 / min(36, count + 1))
    profile["action_effect_ema"][action_index] = previous + alpha * (bounded - previous)
    profile["action_effect_counts"][action_index] = min(1_000_000_000, count + 1)


def update_action_risk(profile: dict, action_index: int, risk: float) -> None:
    prepare_action_metadata(profile)
    if not 0 <= action_index < len(profile["actions"]):
        return
    bounded = max(0.0, min(1.0, float(risk)))
    count = int(profile["action_risk_counts"][action_index])
    previous = float(profile["action_risk_ema"][action_index])
    alpha = max(0.035, 1.0 / min(32, count + 1))
    profile["action_risk_ema"][action_index] = max(0.0, min(1.0, previous + alpha * (bounded - previous)))
    profile["action_risk_counts"][action_index] = min(1_000_000_000, count + 1)


def visual_cycle_score(recent_hashes: list[str], candidate: str, maximum_period: int = 6) -> float:
    sequence = recent_hashes[-32:] + [candidate]
    best = 0.0
    for period in range(1, min(maximum_period, len(sequence) // 2) + 1):
        comparison_count = min(len(sequence) - period, period * 3)
        if comparison_count < period:
            continue
        matches = 0
        for offset in range(comparison_count):
            if frame_hash_distance(sequence[-1 - offset], sequence[-1 - offset - period]) <= 3:
                matches += 1
        ratio = matches / comparison_count
        if ratio < 0.72:
            continue
        repeats = comparison_count / period
        score = ratio * min(1.0, repeats / 2.0) / math.sqrt(period)
        best = max(best, score)
    return max(0.0, min(1.0, best))


def choose_recovery_action(
    profile: dict,
    current_state_key: str,
    state_action_visits: dict[tuple[str, int], int],
    recent_actions: list[int],
    static_streak: int,
    steps: int,
    control_preferences: dict[str, float],
    control_response: dict[str, float],
    scene_preferences: dict[str, float] | None = None,
) -> int | None:
    if static_streak < 3:
        return None
    actions = profile.get("actions", [])
    if len(actions) <= 1:
        return None
    origins = profile.get("action_origins", [])
    rewards = profile.get("action_reward_ema", [])
    reward_counts = profile.get("action_reward_counts", [])
    effects = profile.get("action_effect_ema", [])
    effect_counts = profile.get("action_effect_counts", [])
    movement_keys = {0x57, 0x41, 0x53, 0x44, 0x25, 0x26, 0x27, 0x28}
    interaction_keys = {0x20, 0x0D, 0x45, 0x46, 0x51, 0x52, 0x5A, 0x58, 0x43}
    phases = ("movement", "interaction", "click", "pointer", "mixed", "wheel")
    phase = phases[((steps // 2) + static_streak) % len(phases)]
    best_index = None
    best_score = -1e9
    recent_window = recent_actions[-10:]
    for index, raw_action in enumerate(actions):
        action = normalized_action(raw_action)
        kind = action_kind(action)
        if kind == "idle":
            continue
        keys = set(action["keys"])
        origin = origins[index] if index < len(origins) else "human"
        score = 0.0
        if origin == "human":
            score += 0.30
        elif origin == "transfer":
            score += 0.14
        score += 0.18 * float(control_preferences.get(kind, 0.0))
        score += 0.24 * float(control_response.get(kind, 0.0))
        if scene_preferences:
            score += 0.34 * float(scene_preferences.get(kind, 0.0))
        reward = float(rewards[index]) if index < len(rewards) else 0.0
        reward_count = int(reward_counts[index]) if index < len(reward_counts) else 0
        reward_confidence = min(1.0, math.log1p(max(0, reward_count)) / math.log(33.0))
        score += 0.30 * reward * reward_confidence
        effect = float(effects[index]) if index < len(effects) else 0.0
        effect_count = int(effect_counts[index]) if index < len(effect_counts) else 0
        effect_confidence = min(1.0, math.log1p(max(0, effect_count)) / math.log(25.0))
        score += 0.55 * effect * effect_confidence
        visits = state_action_visits.get((current_state_key, index), 0)
        score -= 0.22 * math.log2(visits + 1.0)
        score -= 0.16 * recent_window.count(index)
        if phase == "movement" and kind in ("keyboard", "mixed") and keys & movement_keys:
            score += 0.95
        elif phase == "interaction" and kind == "keyboard" and keys & interaction_keys:
            score += 0.90
        elif phase == "click" and kind == "click" and "left" in action["buttons"]:
            score += 0.88
        elif phase == "pointer" and kind == "pointer":
            score += 0.82
        elif phase == "mixed" and kind == "mixed":
            score += 0.80
        elif phase == "wheel" and kind == "wheel":
            score += 0.72
        elif kind in ("keyboard", "click", "pointer", "mixed"):
            score += 0.12
        if kind == "keyboard" and keys and keys.issubset({0x10, 0x11, 0x12}):
            score -= 0.75
        if any(0x70 <= key <= 0x87 for key in keys):
            score -= 0.35
        if "right" in action["buttons"]:
            score -= 0.18
        score += random.random() * 0.015
        if score > best_score:
            best_score = score
            best_index = index
    return best_index


def emit_delayed_experience(profile: dict, item: dict, rows: list) -> float:
    weight = max(1e-8, float(item.get("weight_sum", 1.0)))
    reward = max(-1.0, min(1.0, float(item.get("reward_sum", 0.0)) / weight))
    action_index = int(item["action"])
    feature = item["feature"]
    keep_sample = abs(reward) >= 0.025
    if not keep_sample:
        signature = zlib.crc32(feature, action_index & 0xFFFFFFFF)
        keep_sample = signature % 4 == 0
    if keep_sample:
        rows.append(
            (
                str(item["created_at"]),
                "ai",
                action_index,
                reward,
                FEATURE_DIM,
                compress_feature(feature),
            )
        )
    update_action_reward(profile, action_index, reward)
    return reward


def advance_delayed_experience(
    profile: dict,
    pending: list[dict],
    rows: list,
    feature: bytes,
    action_index: int,
    reward: float,
    horizon: int,
    discount: float,
) -> int:
    for item in pending:
        contribution = float(item["next_weight"])
        item["reward_sum"] += contribution * reward
        item["weight_sum"] += contribution
        item["next_weight"] *= discount
        item["age"] += 1
    pending.append(
        {
            "created_at": now_text(),
            "feature": feature,
            "action": int(action_index),
            "reward_sum": float(reward),
            "weight_sum": 1.0,
            "next_weight": float(discount),
            "age": 1,
        }
    )
    emitted = 0
    while pending and int(pending[0]["age"]) >= horizon:
        emit_delayed_experience(profile, pending.pop(0), rows)
        emitted += 1
    return emitted


def flush_delayed_experience(profile: dict, pending: list[dict], rows: list) -> int:
    emitted = 0
    while pending:
        emit_delayed_experience(profile, pending.pop(0), rows)
        emitted += 1
    return emitted


def update_online_state_value(memory: dict, key: tuple[str, int], reward: float, limit: int = 24_000) -> None:
    previous_value, previous_count = memory.get(key, (0.0, 0))
    count = int(previous_count) + 1
    alpha = max(0.06, 1.0 / min(24, count))
    value = float(previous_value) + alpha * (max(-1.0, min(1.0, float(reward))) - float(previous_value))
    memory[key] = (max(-1.0, min(1.0, value)), count)
    while len(memory) > limit:
        memory.pop(next(iter(memory)))


def transition_distribution(
    np,
    profile: dict,
    previous_action: int | None,
    action_count: int,
    previous_previous_action: int | None = None,
    sequence_weight: float = 0.42,
):
    if previous_action is None or not 0 <= previous_action < action_count:
        return np.full(action_count, 1.0 / max(1, action_count), dtype=np.float64)
    row = profile.get("transitions", {}).get(str(previous_action), {})
    counts = np.ones(action_count, dtype=np.float64)
    counts[previous_action] = 1.5
    if isinstance(row, dict):
        for next_text, value in row.items():
            try:
                next_index = int(next_text)
                count = int(value)
            except (TypeError, ValueError):
                continue
            if 0 <= next_index < action_count and count > 0:
                counts[next_index] += min(100_000, count)
    first_order = counts / counts.sum()
    if previous_previous_action is None or not 0 <= previous_previous_action < action_count:
        return first_order
    pair_key = f"{int(previous_previous_action)},{int(previous_action)}"
    pair_row = profile.get("action_pair_transitions", {}).get(pair_key, {})
    if not isinstance(pair_row, dict) or not pair_row:
        return first_order
    pair_counts = np.ones(action_count, dtype=np.float64) * 0.35
    evidence = 0
    for next_text, value in pair_row.items():
        try:
            next_index = int(next_text)
            count = int(value)
        except (TypeError, ValueError):
            continue
        if 0 <= next_index < action_count and count > 0:
            bounded = min(100_000, count)
            pair_counts[next_index] += bounded
            evidence += bounded
    if evidence <= 0:
        return first_order
    pair_order = pair_counts / pair_counts.sum()
    confidence = min(1.0, evidence / 12.0)
    blend = max(0.0, min(0.85, float(sequence_weight))) * confidence
    result = first_order * (1.0 - blend) + pair_order * blend
    result /= result.sum()
    return result


def sequence_plan_values(
    np,
    profile: dict,
    action_count: int,
    horizon: int,
    discount: float,
):
    action_count = max(0, int(action_count))
    if action_count <= 0:
        return np.zeros(0, dtype=np.float64)
    horizon = max(1, min(6, int(horizon)))
    discount = max(0.1, min(0.95, float(discount)))

    def numeric_array(name: str):
        source = profile.get(name, [])
        values = np.zeros(action_count, dtype=np.float64)
        if isinstance(source, list):
            for index in range(min(action_count, len(source))):
                try:
                    value = float(source[index])
                except (TypeError, ValueError, OverflowError):
                    continue
                if math.isfinite(value):
                    values[index] = max(-1.0, min(1.0, value))
        return values

    def count_array(name: str):
        source = profile.get(name, [])
        values = np.zeros(action_count, dtype=np.float64)
        if isinstance(source, list):
            for index in range(min(action_count, len(source))):
                try:
                    value = int(source[index])
                except (TypeError, ValueError, OverflowError):
                    continue
                values[index] = max(0, min(1_000_000_000, value))
        return values

    reward = numeric_array("action_reward_ema")
    effect = numeric_array("action_effect_ema")
    risk = np.maximum(0.0, numeric_array("action_risk_ema"))
    reward_confidence = np.minimum(1.0, np.log1p(count_array("action_reward_counts")) / math.log(17.0))
    effect_confidence = np.minimum(1.0, np.log1p(count_array("action_effect_counts")) / math.log(17.0))
    risk_confidence = np.minimum(1.0, np.log1p(count_array("action_risk_counts")) / math.log(17.0))
    immediate = np.clip(
        0.52 * reward * reward_confidence
        + 0.30 * effect * effect_confidence
        - 0.55 * risk * risk_confidence,
        -1.0,
        1.0,
    )
    if action_count:
        immediate[0] *= 0.35

    transitions = profile.get("transitions", {})
    if horizon <= 1 or not isinstance(transitions, dict):
        return np.zeros(action_count, dtype=np.float64)
    values = immediate.copy()
    for _ in range(horizon - 1):
        updated = immediate.copy()
        for action_index in range(action_count):
            row = transitions.get(str(action_index), {})
            if not isinstance(row, dict) or not row:
                continue
            weighted = 0.0
            evidence = 0
            for next_text, count_value in row.items():
                try:
                    next_index = int(next_text)
                    count = int(count_value)
                except (TypeError, ValueError, OverflowError):
                    continue
                if not 0 <= next_index < action_count or count <= 0:
                    continue
                bounded = min(100_000, count)
                weighted += bounded * float(values[next_index])
                evidence += bounded
            if evidence <= 0:
                continue
            confidence = min(1.0, math.log1p(evidence) / math.log(33.0))
            updated[action_index] = max(
                -1.0,
                min(1.0, float(immediate[action_index]) + discount * confidence * (weighted / evidence)),
            )
        values = updated
    return np.clip(values - immediate, -1.0, 1.0)


def feature_vector(np, feature: bytes):
    feature = normalize_feature_bytes(feature)
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    raw = np.frombuffer(feature, dtype=np.uint8).astype(np.float32) / 255.0
    image = raw[:pixels].reshape(FEATURE_HEIGHT, FEATURE_WIDTH)
    difference = raw[pixels:pixels * 2].reshape(FEATURE_HEIGHT, FEATURE_WIDTH)
    signed_change = np.clip(
        (raw[pixels * 2:pixels * 3] * 255.0 - 128.0) / 127.0,
        -1.0,
        1.0,
    ).reshape(FEATURE_HEIGHT, FEATURE_WIDTH)
    chroma_start = pixels * 3
    chroma_blue = np.clip(
        (raw[chroma_start:chroma_start + COLOR_PIXELS] * 255.0 - 128.0) / 127.0,
        -1.0,
        1.0,
    ).reshape(COLOR_HEIGHT, COLOR_WIDTH)
    chroma_red = np.clip(
        (
            raw[chroma_start + COLOR_PIXELS:chroma_start + COLOR_FEATURE_DIM] * 255.0
            - 128.0
        )
        / 127.0,
        -1.0,
        1.0,
    ).reshape(COLOR_HEIGHT, COLOR_WIDTH)
    mean = float(image.mean())
    deviation = float(image.std())
    centered = image - 0.5
    contrast = np.clip((image - mean) / max(0.08, deviation * 3.0), -1.0, 1.0)
    appearance = np.clip(centered * 0.45 + contrast * 0.55, -1.0, 1.0)
    temporal = np.sqrt(np.maximum(0.0, difference))
    horizontal = np.zeros_like(image)
    vertical = np.zeros_like(image)
    diagonal = np.zeros_like(image)
    horizontal[:, 1:] = np.abs(image[:, 1:] - image[:, :-1])
    vertical[1:, :] = np.abs(image[1:, :] - image[:-1, :])
    diagonal[1:, 1:] = np.abs(image[1:, 1:] - image[:-1, :-1])
    edges = np.minimum(1.0, horizontal * 0.8 + vertical * 0.8 + diagonal * 0.45)
    half_y = FEATURE_HEIGHT // 2
    half_x = FEATURE_WIDTH // 2
    quadrants = (
        difference[:half_y, :half_x],
        difference[:half_y, half_x:],
        difference[half_y:, :half_x],
        difference[half_y:, half_x:],
    )
    center = difference[FEATURE_HEIGHT // 4:FEATURE_HEIGHT * 3 // 4, FEATURE_WIDTH // 4:FEATURE_WIDTH * 3 // 4]
    border = np.concatenate(
        (
            difference[:3, :].reshape(-1),
            difference[-3:, :].reshape(-1),
            difference[3:-3, :4].reshape(-1),
            difference[3:-3, -4:].reshape(-1),
        )
    )

    pooled_appearance = []
    pooled_temporal = []
    for grid_y in range(4):
        top = grid_y * FEATURE_HEIGHT // 4
        bottom = (grid_y + 1) * FEATURE_HEIGHT // 4
        for grid_x in range(4):
            left = grid_x * FEATURE_WIDTH // 4
            right = (grid_x + 1) * FEATURE_WIDTH // 4
            pooled_appearance.append(float(appearance[top:bottom, left:right].mean()))
            pooled_temporal.append(float(temporal[top:bottom, left:right].mean()))

    motion_weights = difference.astype(np.float64, copy=False)
    motion_total = float(motion_weights.sum())
    if motion_total > 1e-9:
        x_axis = np.linspace(-1.0, 1.0, FEATURE_WIDTH, dtype=np.float64)
        y_axis = np.linspace(-1.0, 1.0, FEATURE_HEIGHT, dtype=np.float64)
        x_distribution = motion_weights.sum(axis=0)
        y_distribution = motion_weights.sum(axis=1)
        motion_x = float((x_distribution * x_axis).sum() / motion_total)
        motion_y = float((y_distribution * y_axis).sum() / motion_total)
        motion_spread_x = float((x_distribution * ((x_axis - motion_x) ** 2)).sum() / motion_total)
        motion_spread_y = float((y_distribution * ((y_axis - motion_y) ** 2)).sum() / motion_total)
    else:
        motion_x = 0.0
        motion_y = 0.0
        motion_spread_x = 0.0
        motion_spread_y = 0.0

    luminance_bins = np.minimum(7, (image * 8.0).astype(np.int32)).reshape(-1)
    motion_bins = np.minimum(7, (np.sqrt(np.maximum(0.0, difference)) * 8.0).astype(np.int32)).reshape(-1)
    luminance_histogram = np.bincount(luminance_bins, minlength=8).astype(np.float32) / max(1, pixels)
    motion_histogram = np.bincount(motion_bins, minlength=8).astype(np.float32) / max(1, pixels)

    global_features = np.asarray(
        [
            mean,
            deviation,
            float(image.min()),
            float(image.max()),
            float(difference.mean()),
            float(difference.std()),
            float(difference.max()),
            float(edges.mean()),
            float(edges.std()),
            float(edges.max()),
            float((difference >= 0.04).mean()),
            float((difference >= 0.15).mean()),
            *(float(region.mean()) for region in quadrants),
            float(center.mean()),
            float(border.mean()),
            float(horizontal.mean()),
            float(vertical.mean()),
            *pooled_appearance,
            *pooled_temporal,
            motion_x,
            motion_y,
            motion_spread_x,
            motion_spread_y,
            *(float(value) for value in luminance_histogram),
            *(float(value) for value in motion_histogram),
        ],
        dtype=np.float32,
    )
    result = np.concatenate(
        (
            appearance.reshape(-1),
            temporal.reshape(-1),
            edges.reshape(-1),
            global_features,
            signed_change.reshape(-1),
            chroma_blue.reshape(-1),
            chroma_red.reshape(-1),
        )
    ).astype(np.float32, copy=False)
    if len(result) != MODEL_INPUT_DIM:
        raise RuntimeError("模型输入特征尺寸无效")
    return result

def second_hidden_size(hidden_size: int) -> int:
    return max(24, min(512, int(hidden_size) // 2))


def initialize_model(np, input_dim: int, hidden_size: int, output_size: int) -> dict:
    hidden2 = second_hidden_size(hidden_size)
    scale1 = (2.0 / input_dim) ** 0.5
    scale2 = (2.0 / hidden_size) ** 0.5
    scale3 = (2.0 / hidden2) ** 0.5
    return {
        "schema": MODEL_SCHEMA,
        "input_dim": input_dim,
        "hidden_size": hidden_size,
        "hidden2_size": hidden2,
        "output_size": output_size,
        "W1": np.random.standard_normal((input_dim, hidden_size)).astype(np.float32) * scale1,
        "b1": np.zeros(hidden_size, dtype=np.float32),
        "W2": np.random.standard_normal((hidden_size, hidden2)).astype(np.float32) * scale2,
        "b2": np.zeros(hidden2, dtype=np.float32),
        "Wp": np.random.standard_normal((hidden2, output_size)).astype(np.float32) * scale3,
        "bp": np.zeros(output_size, dtype=np.float32),
        "Wv": np.random.standard_normal((hidden2, output_size)).astype(np.float32) * (scale3 * 0.35),
        "bv": np.zeros(output_size, dtype=np.float32),
        "trained_samples": 0,
        "training_rounds": 0,
        "online_updates": 0,
        "action_hash": "",
        "action_signatures": [],
    }


def load_model(np, path: Path, input_dim: int, hidden_size: int, output_size: int, action_list: list[dict]) -> tuple[dict, bool]:
    current_signatures = [action_signature(action) for action in action_list]
    current_hash = actions_hash(action_list)
    hidden2 = second_hidden_size(hidden_size)
    loaded = None
    changed = False
    try:
        archive_members = validate_npz_archive(path)
        if (
            not MODEL_ARCHIVE_REQUIRED_MEMBERS.issubset(archive_members)
            or not archive_members.issubset(MODEL_ARCHIVE_ALLOWED_MEMBERS)
        ):
            raise ValueError("模型文件成员集合无效")
        with np.load(path, allow_pickle=False) as data:
            schema = int(data["schema"][0])
            if schema not in (4, 5, 6, 7, 8, 9, 10, MODEL_SCHEMA):
                raise ValueError("模型版本不兼容")
            loaded_output_size = int(data["output_size"][0])
            loaded = {
                "schema": schema,
                "input_dim": int(data["input_dim"][0]),
                "hidden_size": int(data["hidden_size"][0]),
                "hidden2_size": int(data["hidden2_size"][0]),
                "output_size": loaded_output_size,
                "W1": data["W1"].astype(np.float32, copy=True),
                "b1": data["b1"].astype(np.float32, copy=True),
                "W2": data["W2"].astype(np.float32, copy=True),
                "b2": data["b2"].astype(np.float32, copy=True),
                "Wp": data["Wp"].astype(np.float32, copy=True),
                "bp": data["bp"].astype(np.float32, copy=True),
                "Wv": data["Wv"].astype(np.float32, copy=True),
                "bv": data["bv"].astype(np.float32, copy=True),
                "trained_samples": int(data["trained_samples"][0]),
                "training_rounds": int(data["training_rounds"][0]),
                "online_updates": int(data["online_updates"][0]) if "online_updates" in data.files else 0,
                "action_hash": str(data["action_hash"][0]),
                "action_signatures": (
                    [canonical_action_signature_text(str(value)) for value in data["action_signatures"].tolist()]
                    if schema >= 5 and "action_signatures" in data.files
                    else []
                ),
            }
        if loaded["hidden_size"] != hidden_size or loaded["hidden2_size"] != hidden2:
            raise ValueError("模型隐藏层结构变化")
        expected_shapes = {
            "W1": (loaded["input_dim"], hidden_size),
            "b1": (hidden_size,),
            "W2": (hidden_size, hidden2),
            "b2": (hidden2,),
            "Wp": (hidden2, loaded["output_size"]),
            "bp": (loaded["output_size"],),
            "Wv": (hidden2, loaded["output_size"]),
            "bv": (loaded["output_size"],),
        }
        for key, shape in expected_shapes.items():
            if loaded[key].shape != shape or not np.isfinite(loaded[key]).all():
                raise ValueError("模型参数尺寸或数值无效")
        if loaded["action_signatures"]:
            if (
                len(loaded["action_signatures"]) != loaded["output_size"]
                or any(not signature for signature in loaded["action_signatures"])
                or len(set(loaded["action_signatures"])) != loaded["output_size"]
            ):
                raise ValueError("模型动作映射无效")
    except FileNotFoundError:
        loaded = None
    except Exception:
        backup_corrupt(path)
        loaded = None
    model = initialize_model(np, input_dim, hidden_size, output_size)
    model["action_hash"] = current_hash
    model["action_signatures"] = current_signatures
    if loaded is None:
        return model, True
    copy_input = min(input_dim, loaded["input_dim"])
    model["W1"][:copy_input] = loaded["W1"][:copy_input]
    if input_dim > loaded["input_dim"]:
        model["W1"][loaded["input_dim"]:] = 0.0
    np.copyto(model["b1"], loaded["b1"])
    np.copyto(model["W2"], loaded["W2"])
    np.copyto(model["b2"], loaded["b2"])
    copied_heads = 0
    if loaded["action_signatures"]:
        source_by_signature = {signature: index for index, signature in enumerate(loaded["action_signatures"])}
        for target_index, signature in enumerate(current_signatures):
            source_index = source_by_signature.get(signature)
            if source_index is None:
                continue
            model["Wp"][:, target_index] = loaded["Wp"][:, source_index]
            model["bp"][target_index] = loaded["bp"][source_index]
            model["Wv"][:, target_index] = loaded["Wv"][:, source_index]
            model["bv"][target_index] = loaded["bv"][source_index]
            copied_heads += 1
    elif loaded["output_size"] == output_size and loaded.get("action_hash") == current_hash:
        np.copyto(model["Wp"], loaded["Wp"])
        np.copyto(model["bp"], loaded["bp"])
        np.copyto(model["Wv"], loaded["Wv"])
        np.copyto(model["bv"], loaded["bv"])
        copied_heads = output_size
    elif (
        loaded["schema"] == 4
        and loaded["output_size"] <= output_size
        and loaded.get("action_hash") == actions_hash(action_list[:loaded["output_size"]])
    ):
        old_size = loaded["output_size"]
        model["Wp"][:, :old_size] = loaded["Wp"]
        model["bp"][:old_size] = loaded["bp"]
        model["Wv"][:, :old_size] = loaded["Wv"]
        model["bv"][:old_size] = loaded["bv"]
        copied_heads = old_size
    model["trained_samples"] = max(0, loaded["trained_samples"])
    model["training_rounds"] = max(0, loaded["training_rounds"])
    model["online_updates"] = max(0, int(loaded.get("online_updates", 0)))
    changed = (
        loaded["schema"] != MODEL_SCHEMA
        or loaded["input_dim"] != input_dim
        or loaded["output_size"] != output_size
        or loaded.get("action_hash") != current_hash
        or loaded.get("action_signatures") != current_signatures
        or copied_heads != output_size
    )
    return model, changed

def load_global_prior(np) -> dict | None:
    try:
        archive_members = validate_npz_archive(GLOBAL_PRIOR_PATH)
        if (
            not GLOBAL_ARCHIVE_REQUIRED_MEMBERS.issubset(archive_members)
            or not archive_members.issubset(GLOBAL_ARCHIVE_ALLOWED_MEMBERS)
        ):
            raise ValueError("通用先验成员集合无效")
        with np.load(GLOBAL_PRIOR_PATH, allow_pickle=False) as data:
            prior = {
                "schema": int(data["schema"][0]),
                "input_dim": int(data["input_dim"][0]),
                "hidden_size": int(data["hidden_size"][0]),
                "hidden2_size": int(data["hidden2_size"][0]),
                "W1": data["W1"].astype(np.float32, copy=True),
                "b1": data["b1"].astype(np.float32, copy=True),
                "W2": data["W2"].astype(np.float32, copy=True),
                "b2": data["b2"].astype(np.float32, copy=True),
                "action_signatures": [
                    canonical_action_signature_text(str(value))
                    for value in data["action_signatures"].tolist()
                ],
                "Wp": data["Wp"].astype(np.float32, copy=True),
                "bp": data["bp"].astype(np.float32, copy=True),
                "Wv": data["Wv"].astype(np.float32, copy=True),
                "bv": data["bv"].astype(np.float32, copy=True),
                "trained_samples": int(data["trained_samples"][0]),
                "training_rounds": int(data["training_rounds"][0]),
                "source_profile": str(data["source_profile"][0]),
            }
        if prior["schema"] not in (3, 4, 5, 6, 7, 8, 9, 10, GLOBAL_PRIOR_SCHEMA):
            raise ValueError("通用先验版本不兼容")
        loaded_input_dim = prior["input_dim"]
        hidden_size = prior["hidden_size"]
        hidden2 = prior["hidden2_size"]
        action_count = len(prior["action_signatures"])
        expected_shapes = {
            "W1": (loaded_input_dim, hidden_size),
            "b1": (hidden_size,),
            "W2": (hidden_size, hidden2),
            "b2": (hidden2,),
            "Wp": (hidden2, action_count),
            "bp": (action_count,),
            "Wv": (hidden2, action_count),
            "bv": (action_count,),
        }
        if loaded_input_dim < LEGACY_MODEL_INPUT_DIM or hidden2 != second_hidden_size(hidden_size):
            raise ValueError("通用先验结构无效")
        if (
            action_count < 1
            or action_count > 1024
            or any(not signature for signature in prior["action_signatures"])
            or len(set(prior["action_signatures"])) != action_count
        ):
            raise ValueError("通用先验动作无效")
        for key, shape in expected_shapes.items():
            if prior[key].shape != shape or not np.isfinite(prior[key]).all():
                raise ValueError("通用先验参数无效")
        if loaded_input_dim != MODEL_INPUT_DIM:
            migrated_w1 = np.zeros((MODEL_INPUT_DIM, hidden_size), dtype=np.float32)
            copy_input = min(MODEL_INPUT_DIM, loaded_input_dim)
            migrated_w1[:copy_input] = prior["W1"][:copy_input]
            prior["W1"] = migrated_w1
            prior["input_dim"] = MODEL_INPUT_DIM
        prior["schema"] = GLOBAL_PRIOR_SCHEMA
        return prior
    except FileNotFoundError:
        return None
    except Exception:
        backup_corrupt(GLOBAL_PRIOR_PATH)
        log_text("通用先验损坏，已隔离：\n" + traceback.format_exc())
        return None

def apply_global_prior(np, model: dict, action_list: list[dict]) -> bool:
    if int(model.get("training_rounds", 0)) > 0:
        return False
    prior = load_global_prior(np)
    if prior is None:
        return False
    if (
        prior["input_dim"] != model["input_dim"]
        or prior["hidden_size"] != model["hidden_size"]
        or prior["hidden2_size"] != model["hidden2_size"]
    ):
        return False
    for key in ("W1", "b1", "W2", "b2"):
        np.copyto(model[key], prior[key])
    prior_actions = {signature: index for index, signature in enumerate(prior["action_signatures"])}
    for target_index, action in enumerate(action_list):
        source_index = prior_actions.get(action_signature(action))
        if source_index is None:
            continue
        model["Wp"][:, target_index] = prior["Wp"][:, source_index]
        model["bp"][target_index] = prior["bp"][source_index]
        model["Wv"][:, target_index] = prior["Wv"][:, source_index]
        model["bv"][target_index] = prior["bv"][source_index]
    model["trained_samples"] = max(int(model.get("trained_samples", 0)), int(prior.get("trained_samples", 0)))
    model["training_rounds"] = max(int(model.get("training_rounds", 0)), int(prior.get("training_rounds", 0)))
    return True


def apply_global_action_heads(
    np,
    model: dict,
    action_list: list[dict],
    action_origins: list[str],
    prior: dict | None = None,
) -> bool:
    prior = load_global_prior(np) if prior is None else prior
    if prior is None:
        return False
    if (
        prior["input_dim"] != model["input_dim"]
        or prior["hidden_size"] != model["hidden_size"]
        or prior["hidden2_size"] != model["hidden2_size"]
    ):
        return False
    prior_actions = {signature: index for index, signature in enumerate(prior["action_signatures"])}
    changed = False
    for target_index, action in enumerate(action_list):
        origin = action_origins[target_index] if target_index < len(action_origins) else "human"
        if origin not in ("generic", "transfer"):
            continue
        source_index = prior_actions.get(action_signature(action))
        if source_index is None:
            continue
        model["Wp"][:, target_index] = prior["Wp"][:, source_index]
        model["bp"][target_index] = prior["bp"][source_index]
        model["Wv"][:, target_index] = prior["Wv"][:, source_index]
        model["bv"][target_index] = prior["bv"][source_index]
        changed = True
    return changed


def verify_model_archive(np, path: Path, model: dict, signatures: list[str]) -> None:
    archive_members = validate_npz_archive(path)
    if archive_members != MODEL_ARCHIVE_ALLOWED_MEMBERS:
        raise RuntimeError("模型临时文件成员集合无效")
    with np.load(path, allow_pickle=False) as data:
        if int(data["schema"][0]) != MODEL_SCHEMA:
            raise RuntimeError("模型临时文件版本无效")
        expected_scalars = {
            "input_dim": int(model["input_dim"]),
            "hidden_size": int(model["hidden_size"]),
            "hidden2_size": int(model["hidden2_size"]),
            "output_size": int(model["output_size"]),
        }
        for key, expected in expected_scalars.items():
            if int(data[key][0]) != expected:
                raise RuntimeError("模型临时文件结构无效")
        if [str(value) for value in data["action_signatures"].tolist()] != signatures:
            raise RuntimeError("模型临时文件动作映射无效")
        for key in ("W1", "b1", "W2", "b2", "Wp", "bp", "Wv", "bv"):
            saved = data[key]
            expected = model[key]
            if saved.shape != expected.shape or not np.isfinite(saved).all():
                raise RuntimeError("模型临时文件参数无效")


def verify_global_prior_archive(np, path: Path, model: dict, signatures: list[str]) -> None:
    archive_members = validate_npz_archive(path)
    if archive_members != GLOBAL_ARCHIVE_ALLOWED_MEMBERS:
        raise RuntimeError("通用先验临时文件成员集合无效")
    with np.load(path, allow_pickle=False) as data:
        if int(data["schema"][0]) != GLOBAL_PRIOR_SCHEMA:
            raise RuntimeError("通用先验临时文件版本无效")
        if int(data["input_dim"][0]) != int(model["input_dim"]):
            raise RuntimeError("通用先验临时文件结构无效")
        if [str(value) for value in data["action_signatures"].tolist()] != signatures:
            raise RuntimeError("通用先验临时文件动作映射无效")
        for key in ("W1", "b1", "W2", "b2", "Wp", "bp", "Wv", "bv"):
            saved = data[key]
            expected = model[key]
            if saved.shape != expected.shape or not np.isfinite(saved).all():
                raise RuntimeError("通用先验临时文件参数无效")


def save_global_prior(np, model: dict, action_list: list[dict], source_profile: str) -> None:
    GLOBAL_PRIOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = temporary_sibling_path(GLOBAL_PRIOR_PATH)
    signatures = [action_signature(action) for action in action_list]
    temp.unlink(missing_ok=True)
    try:
        with temp.open("wb") as file:
            np.savez_compressed(
                file,
                schema=np.array([GLOBAL_PRIOR_SCHEMA], dtype=np.int32),
                input_dim=np.array([model["input_dim"]], dtype=np.int32),
                hidden_size=np.array([model["hidden_size"]], dtype=np.int32),
                hidden2_size=np.array([model["hidden2_size"]], dtype=np.int32),
                W1=model["W1"].astype(np.float32),
                b1=model["b1"].astype(np.float32),
                W2=model["W2"].astype(np.float32),
                b2=model["b2"].astype(np.float32),
                action_signatures=np.asarray(signatures),
                Wp=model["Wp"].astype(np.float32),
                bp=model["bp"].astype(np.float32),
                Wv=model["Wv"].astype(np.float32),
                bv=model["bv"].astype(np.float32),
                trained_samples=np.array([model.get("trained_samples", 0)], dtype=np.int64),
                training_rounds=np.array([model.get("training_rounds", 0)], dtype=np.int64),
                source_profile=np.asarray([source_profile]),
                updated_at=np.asarray([now_text()]),
            )
            file.flush()
            os.fsync(file.fileno())
        verify_global_prior_archive(np, temp, model, signatures)
        os.replace(temp, GLOBAL_PRIOR_PATH)
    finally:
        temp.unlink(missing_ok=True)


def model_from_global_prior(np, prior: dict | None, action_list: list[dict], hidden_size: int) -> dict:
    model = initialize_model(np, MODEL_INPUT_DIM, hidden_size, len(action_list))
    model["action_signatures"] = [action_signature(action) for action in action_list]
    if prior is None:
        model["action_hash"] = actions_hash(action_list)
        return model
    if (
        prior.get("input_dim") != MODEL_INPUT_DIM
        or prior.get("hidden_size") != hidden_size
        or prior.get("hidden2_size") != second_hidden_size(hidden_size)
    ):
        model["action_hash"] = actions_hash(action_list)
        return model
    for key in ("W1", "b1", "W2", "b2"):
        np.copyto(model[key], prior[key])
    prior_actions = {signature: index for index, signature in enumerate(prior["action_signatures"])}
    for target_index, action in enumerate(action_list):
        source_index = prior_actions.get(action_signature(action))
        if source_index is None:
            continue
        model["Wp"][:, target_index] = prior["Wp"][:, source_index]
        model["bp"][target_index] = prior["bp"][source_index]
        model["Wv"][:, target_index] = prior["Wv"][:, source_index]
        model["bv"][target_index] = prior["bv"][source_index]
    model["trained_samples"] = max(0, int(prior.get("trained_samples", 0)))
    model["training_rounds"] = max(0, int(prior.get("training_rounds", 0)))
    model["online_updates"] = 0
    model["action_hash"] = actions_hash(action_list)
    return model


def refresh_global_prior(np, index: dict, config: dict, stop_event: threading.Event | None) -> bool:
    candidates: list[tuple[str, dict, dict[str, Path]]] = []
    signature_scores: dict[str, float] = {}
    signature_actions: dict[str, dict] = {}
    for profile_id in sorted(index.get("profiles", {})):
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        paths = profile_paths(profile_id)
        if not paths["profile"].is_file() or not paths["db"].is_file():
            continue
        try:
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
            profile = migrate_profile(candidate, profile_id)
            if profile is None:
                continue
            total_count, human_count = count_samples(paths["db"])
            if human_count < 8 and total_count < 48:
                continue
            action_scores: dict[int, float] = {}
            connection = sqlite3.connect(paths["db"], timeout=20)
            install_sqlite_cancel_handler(connection, stop_event)
            try:
                for action_index, score_value in connection.execute(
                    "SELECT action, SUM(CASE WHEN source='human' "
                    "THEN 1.0+MAX(0.0,MIN(1.0,reward))*3.0 "
                    "WHEN reward>0.05 THEN 0.5+reward*2.5 ELSE 0.0 END) "
                    "FROM samples GROUP BY action"
                ):
                    action_scores[int(action_index)] = max(0.0, float(score_value or 0.0))
            except sqlite3.OperationalError as error:
                raise_if_sqlite_cancelled(error, stop_event)
                raise
            finally:
                connection.close()
            for action_index, action in enumerate(profile["actions"]):
                signature = action_signature(action)
                signature_actions.setdefault(signature, normalized_action(action))
                origin = profile.get("action_origins", [])[action_index] if action_index < len(profile.get("action_origins", [])) else "human"
                base_score = 0.15 if origin == "generic" else 0.35
                signature_scores[signature] = signature_scores.get(signature, 0.0) + base_score + action_scores.get(action_index, 0.0)
            candidates.append((profile_id, profile, paths))
        except RuntimeError:
            raise
        except Exception:
            log_text(f"读取通用训练候选 {profile_id} 失败：\n" + traceback.format_exc())
    if not candidates or not signature_actions:
        return False
    action_limit = min(512, max(64, int(config["max_action_count"]) * 4))
    ordered_signatures = sorted(signature_actions, key=lambda value: (-signature_scores.get(value, 0), value))[:action_limit]
    global_actions = [signature_actions[signature] for signature in ordered_signatures]
    global_indices = {signature: index for index, signature in enumerate(ordered_signatures)}
    training_settings = adaptive_global_training_settings(config, len(candidates))
    global_sample_limit = int(training_settings["sample_limit"])
    per_profile_limit = int(training_settings["per_profile_limit"])
    x_parts = []
    y_parts = []
    policy_parts = []
    value_target_parts = []
    value_weight_parts = []
    used_profiles = 0
    for profile_id, profile, paths in candidates:
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        loaded_x = None
        try:
            loaded_x, y, policy_weights, value_targets, value_weights, invalid = load_training_data(
                np,
                paths["db"],
                len(profile["actions"]),
                per_profile_limit,
                stop_event,
            )
            if loaded_x is None:
                continue
            mapping = np.full(len(profile["actions"]), -1, dtype=np.int64)
            for action_index, action in enumerate(profile["actions"]):
                mapping[action_index] = global_indices.get(action_signature(action), -1)
            mapped = mapping[y]
            valid = mapped >= 0
            if not bool(valid.any()):
                continue
            selected_x = np.asarray(loaded_x[valid], dtype=np.float32).copy()
            mapped = mapped[valid].copy()
            policy_weights = policy_weights[valid].copy()
            value_targets = value_targets[valid].copy()
            value_weights = value_weights[valid].copy()
            fairness = min(2.5, max(0.65, math.sqrt(per_profile_limit / max(1, len(selected_x)))))
            x_parts.append(selected_x)
            y_parts.append(mapped)
            policy_parts.append(policy_weights * fairness)
            value_target_parts.append(value_targets)
            value_weight_parts.append(value_weights * fairness)
            used_profiles += 1
            if invalid:
                log_text(f"{profile_id} 通用训练时忽略损坏经验 {invalid} 条")
        except RuntimeError:
            raise
        except Exception:
            log_text(f"汇总通用训练数据 {profile_id} 失败：\n" + traceback.format_exc())
        finally:
            release_training_matrix(loaded_x)
    if not x_parts:
        return False
    x = np.concatenate(x_parts, axis=0)
    y = np.concatenate(y_parts, axis=0)
    policy_weights = np.concatenate(policy_parts, axis=0)
    value_targets = np.concatenate(value_target_parts, axis=0)
    value_weights = np.concatenate(value_weight_parts, axis=0)
    x_parts.clear()
    y_parts.clear()
    policy_parts.clear()
    value_target_parts.clear()
    value_weight_parts.clear()
    if len(x) > global_sample_limit:
        selected = np.random.choice(len(x), size=global_sample_limit, replace=False)
        x = x[selected]
        y = y[selected]
        policy_weights = policy_weights[selected]
        value_targets = value_targets[selected]
        value_weights = value_weights[selected]
    prior = load_global_prior(np)
    model = model_from_global_prior(np, prior, global_actions, int(config["hidden_size"]))
    metrics = train_model(
        np,
        model,
        x,
        y,
        policy_weights,
        value_targets,
        value_weights,
        int(training_settings["epochs"]),
        int(training_settings["batch_size"]),
        float(config["learning_rate"]) * 0.8,
        stop_event,
    )
    model["action_hash"] = actions_hash(global_actions)
    save_global_prior(np, model, global_actions, f"aggregate:{used_profiles}:{metrics['samples']}")
    return True

def save_model(np, path: Path, model: dict) -> None:
    signatures = [str(value) for value in model.get("action_signatures", [])]
    if len(signatures) != int(model.get("output_size", 0)) or len(set(signatures)) != len(signatures):
        raise RuntimeError("模型动作映射无效")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = temporary_sibling_path(path)
    temp.unlink(missing_ok=True)
    try:
        with temp.open("wb") as file:
            np.savez_compressed(
                file,
                schema=np.array([MODEL_SCHEMA], dtype=np.int32),
                input_dim=np.array([model["input_dim"]], dtype=np.int32),
                hidden_size=np.array([model["hidden_size"]], dtype=np.int32),
                hidden2_size=np.array([model["hidden2_size"]], dtype=np.int32),
                output_size=np.array([model["output_size"]], dtype=np.int32),
                W1=model["W1"].astype(np.float32),
                b1=model["b1"].astype(np.float32),
                W2=model["W2"].astype(np.float32),
                b2=model["b2"].astype(np.float32),
                Wp=model["Wp"].astype(np.float32),
                bp=model["bp"].astype(np.float32),
                Wv=model["Wv"].astype(np.float32),
                bv=model["bv"].astype(np.float32),
                trained_samples=np.array([model.get("trained_samples", 0)], dtype=np.int64),
                training_rounds=np.array([model.get("training_rounds", 0)], dtype=np.int64),
                online_updates=np.array([model.get("online_updates", 0)], dtype=np.int64),
                action_hash=np.array([model.get("action_hash", "")]),
                action_signatures=np.asarray(signatures),
                updated_at=np.array([now_text()]),
            )
            file.flush()
            os.fsync(file.fileno())
        verify_model_archive(np, temp, model, signatures)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _model_hidden_state_from_vector(np, model: dict, vector):
    hidden1 = np.maximum(0.0, vector @ model["W1"] + model["b1"])
    return np.maximum(0.0, hidden1 @ model["W2"] + model["b2"])


def _model_hidden_state(np, model: dict, feature: bytes):
    return _model_hidden_state_from_vector(np, model, feature_vector(np, feature))


def _model_head_outputs(np, model: dict, hidden2):
    logits = hidden2 @ model["Wp"] + model["bp"]
    logits -= float(logits.max())
    probabilities = np.exp(logits)
    probabilities /= max(1e-8, float(probabilities.sum()))
    values = np.tanh(hidden2 @ model["Wv"] + model["bv"])
    return probabilities, values


def model_outputs(np, model: dict, feature: bytes):
    return _model_head_outputs(np, model, _model_hidden_state(np, model, feature))


def model_ensemble_outputs(
    np,
    model: dict,
    target_model: dict | None,
    feature: bytes,
    target_weight: float,
):
    vector = feature_vector(np, feature)
    hidden2 = _model_hidden_state_from_vector(np, model, vector)
    probabilities, values = _model_head_outputs(np, model, hidden2)
    action_count = len(probabilities)
    uncertainty = np.zeros(action_count, dtype=np.float64)
    try:
        weight = float(target_weight)
    except (TypeError, ValueError, OverflowError):
        weight = 0.0
    if (
        target_model is None
        or not math.isfinite(weight)
        or weight <= 0.0
        or action_count <= 0
    ):
        return probabilities, values, uncertainty, 0.0
    weight = max(0.0, min(0.5, weight))
    try:
        target_hidden2 = _model_hidden_state_from_vector(np, target_model, vector)
        target_probabilities, target_values = _model_head_outputs(
            np,
            target_model,
            target_hidden2,
        )
    except (KeyError, TypeError, ValueError, FloatingPointError):
        return probabilities, values, uncertainty, 0.0
    if (
        target_probabilities.shape != probabilities.shape
        or target_values.shape != values.shape
        or not np.isfinite(target_probabilities).all()
        or not np.isfinite(target_values).all()
    ):
        return probabilities, values, uncertainty, 0.0
    blended_logits = (
        (1.0 - weight) * np.log(np.maximum(probabilities.astype(np.float64, copy=False), 1e-12))
        + weight * np.log(np.maximum(target_probabilities.astype(np.float64, copy=False), 1e-12))
    )
    blended_logits -= float(blended_logits.max())
    blended_probabilities = np.exp(blended_logits)
    blended_probabilities /= max(1e-12, float(blended_probabilities.sum()))
    blended_values = (
        (1.0 - weight) * values.astype(np.float64, copy=False)
        + weight * target_values.astype(np.float64, copy=False)
    )
    uncertainty = np.clip(
        0.45 * np.abs(probabilities - target_probabilities)
        + 0.55 * np.abs(values - target_values),
        0.0,
        1.0,
    )
    disagreement = float(np.dot(blended_probabilities, uncertainty))
    if not math.isfinite(disagreement):
        disagreement = 0.0
    return (
        blended_probabilities,
        np.clip(blended_values, -1.0, 1.0),
        uncertainty,
        max(0.0, min(1.0, disagreement)),
    )


def clone_target_model(np, model: dict) -> dict:
    parameter_names = ("W1", "b1", "W2", "b2", "Wp", "bp", "Wv", "bv")
    target = dict(model)
    for name in parameter_names:
        try:
            value = np.asarray(model[name], dtype=np.float32)
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError("在线模型缺少目标网络参数") from error
        if value.ndim == 0 or not np.isfinite(value).all():
            raise RuntimeError("在线模型目标网络参数无效")
        target[name] = value.copy()
    signatures = model.get("action_signatures", [])
    target["action_signatures"] = list(signatures) if isinstance(signatures, list) else []
    return target


def soft_update_target_model(np, target: dict, source: dict, rate: float) -> None:
    try:
        bounded_rate = float(rate)
    except (TypeError, ValueError, OverflowError) as error:
        raise RuntimeError("目标网络同步比例无效") from error
    if not math.isfinite(bounded_rate) or not 0.0 < bounded_rate <= 1.0:
        raise RuntimeError("目标网络同步比例无效")
    parameter_names = ("W1", "b1", "W2", "b2", "Wp", "bp", "Wv", "bv")
    pairs = []
    for name in parameter_names:
        try:
            target_value = np.asarray(target[name])
            source_value = np.asarray(source[name])
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError("目标网络同步参数缺失") from error
        if (
            target_value.shape != source_value.shape
            or target_value.dtype.kind != "f"
            or source_value.dtype.kind != "f"
            or not np.isfinite(target_value).all()
            or not np.isfinite(source_value).all()
        ):
            raise RuntimeError("目标网络同步参数无效")
        pairs.append((target_value, source_value))
    for target_value, source_value in pairs:
        if bounded_rate >= 1.0:
            np.copyto(target_value, source_value)
        else:
            target_value *= 1.0 - bounded_rate
            target_value += bounded_rate * source_value
    for name in (
        "schema", "input_dim", "hidden_size", "hidden2_size", "output_size",
        "trained_samples", "training_rounds", "online_updates", "action_hash",
    ):
        if name in source:
            target[name] = source[name]
    signatures = source.get("action_signatures", [])
    target["action_signatures"] = list(signatures) if isinstance(signatures, list) else []


def online_update_reliability(
    persistence: float,
    flicker: float,
    fade_score: float,
    global_shift: float,
    next_black: bool,
) -> float:
    persistence_value = max(0.0, min(1.0, float(persistence)))
    flicker_value = max(0.0, min(1.0, float(flicker)))
    fade_value = max(0.0, min(1.0, float(fade_score)))
    shift_value = max(0.0, min(1.0, float(global_shift)))
    stability = (0.20 + 0.80 * persistence_value)
    stability *= 1.0 - 0.82 * flicker_value
    stability *= 1.0 - 0.52 * fade_value
    stability *= 1.0 - 0.36 * shift_value
    if next_black:
        stability *= 0.45
    return max(0.05, min(1.0, stability))


def temporal_difference_target(
    np,
    model: dict,
    reward: float,
    next_feature: bytes | None = None,
    discount: float = 0.0,
    terminal: bool = False,
    target_model: dict | None = None,
) -> float:
    try:
        reward_value = float(reward)
    except (TypeError, ValueError, OverflowError):
        return math.nan
    if not math.isfinite(reward_value):
        return math.nan
    immediate = max(-1.0, min(1.0, reward_value))
    try:
        discount_value = float(discount)
    except (TypeError, ValueError, OverflowError):
        return immediate
    if not math.isfinite(discount_value):
        return immediate
    discount_value = max(0.0, min(0.95, discount_value))
    if terminal or next_feature is None or discount_value <= 0.0:
        return immediate
    next_probabilities, next_values = model_outputs(np, model, next_feature)
    if (
        next_probabilities.shape != next_values.shape
        or not np.isfinite(next_probabilities).all()
        or not np.isfinite(next_values).all()
    ):
        return immediate
    target_values = next_values
    target_disagreement = 0.0
    if target_model is not None:
        _, target_values = model_outputs(np, target_model, next_feature)
        if target_values.shape != next_probabilities.shape or not np.isfinite(target_values).all():
            return immediate
    online_scores = (
        np.log(np.maximum(next_probabilities.astype(np.float64, copy=False), 1e-12))
        + 0.42 * next_values.astype(np.float64, copy=False)
    )
    selected_action = int(np.argmax(online_scores))
    selected_target_value = float(target_values[selected_action])
    expected_target_value = float(
        np.dot(
            next_probabilities.astype(np.float64, copy=False),
            target_values.astype(np.float64, copy=False),
        )
    )
    if target_model is not None:
        target_disagreement = min(1.0, abs(selected_target_value - float(next_values[selected_action])))
    expected_next_value = 0.72 * selected_target_value + 0.28 * expected_target_value
    if not math.isfinite(expected_next_value):
        return immediate
    try:
        evidence_count = max(
            0,
            int(model.get("trained_samples", 0)) + int(model.get("online_updates", 0)),
        )
    except (TypeError, ValueError, OverflowError):
        evidence_count = 0
    evidence_confidence = min(1.0, math.log1p(evidence_count) / math.log(129.0))
    policy_confidence = calibrated_policy_confidence(np, next_probabilities, next_values)
    bootstrap_confidence = evidence_confidence * (0.35 + 0.65 * policy_confidence)
    bootstrap_confidence *= 1.0 - 0.45 * target_disagreement
    target = immediate + discount_value * bootstrap_confidence * expected_next_value
    return max(-1.0, min(1.0, target))


def online_model_update(
    np,
    model: dict,
    feature: bytes,
    action_index: int,
    reward: float,
    learning_rate: float,
    next_feature: bytes | None = None,
    discount: float = 0.0,
    terminal: bool = False,
    target_model: dict | None = None,
) -> bool:
    output_size = int(model.get("output_size", 0))
    rate = max(0.0, min(0.02, float(learning_rate)))
    if rate <= 0.0 or not 0 <= action_index < output_size:
        return False
    bounded_reward = temporal_difference_target(
        np,
        model,
        reward,
        next_feature,
        discount,
        terminal,
        target_model,
    )
    if not math.isfinite(bounded_reward) or abs(bounded_reward) < 0.015:
        return False
    x = feature_vector(np, feature)
    hidden1 = np.maximum(0.0, x @ model["W1"] + model["b1"])
    hidden2 = np.maximum(0.0, hidden1 @ model["W2"] + model["b2"])
    hidden1_norm = max(1.0, float(np.linalg.norm(hidden1)) / math.sqrt(max(1, len(hidden1))))
    normalized_hidden1 = hidden1 / hidden1_norm
    hidden_norm = max(1.0, float(np.linalg.norm(hidden2)) / math.sqrt(max(1, len(hidden2))))
    normalized_hidden = hidden2 / hidden_norm
    logits = hidden2 @ model["Wp"] + model["bp"]
    logits -= float(logits.max())
    probabilities = np.exp(logits)
    probabilities /= max(1e-8, float(probabilities.sum()))
    raw_values = hidden2 @ model["Wv"] + model["bv"]
    values = np.tanh(raw_values)
    predicted_value = float(values[action_index])
    baseline = float((probabilities * values).sum())
    value_error = max(-1.0, min(1.0, bounded_reward - predicted_value))
    value_gradient = value_error * (1.0 - predicted_value * predicted_value)
    value_rate = rate * (0.55 + 0.45 * min(1.0, abs(value_error)))
    advantage = max(-1.0, min(1.0, bounded_reward - baseline))
    policy_gradient = -probabilities
    policy_gradient[action_index] += 1.0
    representation_signal = (
        value_gradient * model["Wv"][:, action_index]
        + 0.35 * advantage * (model["Wp"] @ policy_gradient)
    )
    representation_signal = np.asarray(representation_signal, dtype=np.float32)
    representation_signal[hidden2 <= 0.0] = 0.0
    signal_norm = float(np.linalg.norm(representation_signal))
    if signal_norm > 3.0:
        representation_signal *= 3.0 / signal_norm
        signal_norm = 3.0
    input_signal = representation_signal @ model["W2"].T
    input_signal = np.asarray(input_signal, dtype=np.float32)
    input_signal[hidden1 <= 0.0] = 0.0
    input_signal_norm = float(np.linalg.norm(input_signal))
    if input_signal_norm > 2.0:
        input_signal *= 2.0 / input_signal_norm
        input_signal_norm = 2.0
    model["Wv"][:, action_index] += value_rate * value_gradient * normalized_hidden
    model["bv"][action_index] += value_rate * value_gradient
    policy_rate = rate * 0.35 * advantage
    model["Wp"] += policy_rate * np.outer(normalized_hidden, policy_gradient)
    model["bp"] += policy_rate * policy_gradient
    representation_rate = (
        rate
        * ONLINE_REPRESENTATION_SCALE_DEFAULT
        * (0.50 + 0.50 * min(1.0, abs(value_error)))
    )
    if representation_rate > 0.0 and signal_norm > 1e-10:
        model["W2"] += representation_rate * np.outer(
            normalized_hidden1,
            representation_signal,
        )
        model["b2"] += representation_rate * representation_signal
        if input_signal_norm > 1e-10:
            feature_budget = min(
                len(x),
                max(16, int(ONLINE_INPUT_ADAPTATION_FEATURES_DEFAULT)),
            )
            if feature_budget < len(x):
                selected_features = np.argpartition(np.abs(x), -feature_budget)[-feature_budget:]
            else:
                selected_features = np.arange(len(x))
            selected_input = x[selected_features]
            selected_norm = max(
                1.0,
                float(np.linalg.norm(selected_input)) / math.sqrt(max(1, len(selected_input))),
            )
            input_rate = representation_rate * ONLINE_INPUT_ADAPTATION_SCALE_DEFAULT
            model["W1"][selected_features] += input_rate * np.outer(
                selected_input / selected_norm,
                input_signal,
            )
            model["b1"] += input_rate * 0.25 * input_signal
    np.clip(model["W1"], -5.0, 5.0, out=model["W1"])
    np.clip(model["b1"], -5.0, 5.0, out=model["b1"])
    np.clip(model["W2"], -5.0, 5.0, out=model["W2"])
    np.clip(model["b2"], -5.0, 5.0, out=model["b2"])
    np.clip(model["Wp"], -5.0, 5.0, out=model["Wp"])
    np.clip(model["bp"], -5.0, 5.0, out=model["bp"])
    np.clip(model["Wv"], -5.0, 5.0, out=model["Wv"])
    np.clip(model["bv"], -5.0, 5.0, out=model["bv"])
    model["online_updates"] = min(1_000_000_000, int(model.get("online_updates", 0)) + 1)
    return True


def calibrated_policy_confidence(np, probabilities, values) -> float:
    probabilities = np.asarray(probabilities, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    action_count = len(probabilities)
    if action_count <= 1:
        return 1.0
    if values.shape != probabilities.shape or not np.isfinite(probabilities).all() or not np.isfinite(values).all():
        return 0.0
    probability_total = float(probabilities.sum())
    if probability_total <= 1e-12:
        return 0.0
    probabilities = np.maximum(probabilities / probability_total, 1e-12)
    probabilities /= float(probabilities.sum())
    entropy = float(-(probabilities * np.log(probabilities)).sum())
    entropy_confidence = max(0.0, min(1.0, 1.0 - entropy / math.log(action_count)))
    ordered = np.sort(probabilities)
    probability_margin = float(ordered[-1] - ordered[-2]) if action_count > 1 else 1.0
    policy_action = int(np.argmax(probabilities))
    value_action = int(np.argmax(values))
    value_spread = float(values.max() - values.min())
    value_margin = 0.0
    if value_spread > 1e-8:
        ordered_values = np.sort(values)
        value_margin = max(0.0, min(1.0, float(ordered_values[-1] - ordered_values[-2]) / value_spread))
    agreement = 1.0 if policy_action == value_action else 0.0
    confidence = (
        entropy_confidence * 0.52
        + max(0.0, min(1.0, probability_margin * 2.5)) * 0.20
        + value_margin * 0.12
        + agreement * 0.16
    )
    return max(0.0, min(1.0, confidence))



def signed_policy_objective(
    np,
    probabilities,
    labels,
    signed_weights,
    with_gradient: bool = False,
):
    probabilities = np.asarray(probabilities)
    labels = np.asarray(labels, dtype=np.int64)
    signed_weights = np.asarray(signed_weights, dtype=np.float64)
    if probabilities.ndim != 2 or len(labels) != len(probabilities) or len(signed_weights) != len(probabilities):
        raise ValueError("策略训练批次尺寸无效")
    row_count, action_count = probabilities.shape
    if row_count == 0 or action_count <= 0 or np.any(labels < 0) or np.any(labels >= action_count):
        raise ValueError("策略训练标签无效")
    rows = np.arange(row_count)
    chosen = np.clip(probabilities[rows, labels], 1e-8, 1.0 - 1e-8)
    positive_weights = np.maximum(signed_weights, 0.0)
    avoidance_weights = np.maximum(-signed_weights, 0.0)
    positive_total = float(positive_weights.sum())
    avoidance_total = float(avoidance_weights.sum())
    loss = 0.0
    gradient = np.zeros_like(probabilities) if with_gradient else None
    if positive_total > 1e-8:
        label_smoothing = 0.015 if action_count > 1 else 0.0
        if label_smoothing:
            log_probabilities = np.log(np.clip(probabilities, 1e-8, 1.0))
            positive_losses = (
                -(1.0 - label_smoothing) * np.log(chosen)
                - label_smoothing * log_probabilities.mean(axis=1)
            )
        else:
            positive_losses = -np.log(chosen)
        loss += float((positive_losses * positive_weights).sum() / positive_total)
        if with_gradient:
            positive_gradient = probabilities.copy()
            if label_smoothing:
                positive_gradient -= label_smoothing / action_count
                positive_gradient[rows, labels] -= 1.0 - label_smoothing
            else:
                positive_gradient[rows, labels] -= 1.0
            positive_gradient *= (positive_weights / positive_total)[:, None]
            gradient += positive_gradient
    if avoidance_total > 1e-8 and action_count > 1:
        avoidance_loss = float(((-np.log1p(-chosen)) * avoidance_weights).sum() / avoidance_total)
        loss += POLICY_AVOIDANCE_WEIGHT * avoidance_loss
        if with_gradient:
            factor = chosen / np.maximum(1e-8, 1.0 - chosen)
            avoidance_gradient = -probabilities * factor[:, None]
            avoidance_gradient[rows, labels] += factor
            avoidance_gradient *= (avoidance_weights / avoidance_total)[:, None]
            gradient += POLICY_AVOIDANCE_WEIGHT * avoidance_gradient
    return loss, gradient


def temporal_policy_blend(
    np,
    probabilities,
    values,
    previous_probabilities,
    previous_values,
    scene_motion: float,
    static_streak: int,
):
    current_probabilities = np.asarray(probabilities, dtype=np.float64)
    current_values = np.asarray(values, dtype=np.float64)
    if (
        previous_probabilities is None
        or previous_values is None
        or len(previous_probabilities) != len(current_probabilities)
        or len(previous_values) != len(current_values)
    ):
        normalized = current_probabilities.copy()
        normalized /= max(1e-12, float(normalized.sum()))
        return normalized, current_values.copy(), 0.0
    previous_probabilities = np.asarray(previous_probabilities, dtype=np.float64)
    previous_values = np.asarray(previous_values, dtype=np.float64)
    drift = 0.5 * float(np.abs(current_probabilities - previous_probabilities).sum())
    abrupt_transition = scene_motion >= 0.11 or drift >= 0.58
    if abrupt_transition:
        current_weight = 1.0
    else:
        motion_weight = min(0.34, max(0.0, scene_motion) * 4.5)
        drift_weight = min(0.24, drift * 0.55)
        recovery_weight = min(0.16, max(0, int(static_streak) - 2) * 0.025)
        current_weight = min(0.92, 0.48 + motion_weight + drift_weight + recovery_weight)
    blended_probabilities = (
        current_weight * current_probabilities
        + (1.0 - current_weight) * previous_probabilities
    )
    blended_probabilities /= max(1e-12, float(blended_probabilities.sum()))
    blended_values = current_weight * current_values + (1.0 - current_weight) * previous_values
    return blended_probabilities, blended_values, drift


def adaptive_exploration_rate(
    base_exploration: float,
    confidence: float,
    state_familiarity: float,
    policy_drift: float,
    recent_reward: float,
    reward_observations: int,
) -> float:
    def finite_unit(value: float, default: float = 0.0) -> float:
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            result = default
        if not math.isfinite(result):
            result = default
        return max(0.0, min(1.0, result))

    base = finite_unit(base_exploration)
    confidence_value = finite_unit(confidence)
    familiarity = finite_unit(state_familiarity)
    drift = finite_unit(policy_drift)
    try:
        reward_value = float(recent_reward)
    except (TypeError, ValueError, OverflowError):
        reward_value = 0.0
    if not math.isfinite(reward_value):
        reward_value = 0.0
    reward_value = max(-1.0, min(1.0, reward_value))
    try:
        observation_count = max(0, int(reward_observations))
    except (TypeError, ValueError, OverflowError):
        observation_count = 0
    reward_confidence = min(1.0, observation_count / 8.0)
    reward_pressure = max(-0.04, min(0.12, (0.10 - reward_value) * 0.20))
    rate = (
        base
        + (1.0 - confidence_value) * 0.14
        - confidence_value * 0.025
        + (0.5 - familiarity) * 0.06
        + min(0.08, drift * 0.12)
        + reward_pressure * reward_confidence
    )
    return max(0.0, min(0.75, rate))


def masked_policy_weights(np, scores, blocked_actions: set[int] | None = None):
    values = np.asarray(scores, dtype=np.float64)
    if values.ndim != 1 or len(values) <= 0:
        raise ValueError("策略分数尺寸无效")
    allowed = np.ones(len(values), dtype=bool)
    if blocked_actions:
        for action_index in blocked_actions:
            if 0 < action_index < len(values):
                allowed[action_index] = False
    finite_allowed = allowed & np.isfinite(values)
    if not bool(finite_allowed.any()):
        result = np.zeros(len(values), dtype=np.float64)
        result[0] = 1.0
        return result
    maximum = float(values[finite_allowed].max())
    result = np.zeros(len(values), dtype=np.float64)
    result[finite_allowed] = np.exp(np.clip(values[finite_allowed] - maximum, -745.0, 0.0))
    total = float(result.sum())
    if not math.isfinite(total) or total <= 1e-12:
        result.fill(0.0)
        result[0] = 1.0
        return result
    result /= total
    return result


def choose_policy_action(
    np,
    probabilities,
    values,
    transition_prior,
    exploration: float,
    recent_actions: list[int],
    static_streak: int,
    blocked_actions: set[int] | None = None,
) -> int:
    action_count = len(probabilities)
    if action_count <= 1:
        return 0
    scores = np.log(np.maximum(probabilities.astype(np.float64, copy=False), 1e-12))
    scores += 0.42 * np.asarray(values, dtype=np.float64)
    if transition_prior is not None and len(transition_prior) == action_count:
        scores += 0.30 * np.log(np.maximum(transition_prior, 1e-12))
    if recent_actions:
        previous_action = recent_actions[-1]
        if 0 <= previous_action < action_count and static_streak < 3:
            scores[previous_action] += 0.12
    if len(recent_actions) >= 4 and len(set(recent_actions[-4:])) == 1:
        scores[recent_actions[-1]] -= 1.25
    if len(recent_actions) >= 6:
        even_cycle = recent_actions[-6::2]
        odd_cycle = recent_actions[-5::2]
        if len(set(even_cycle)) == 1 and len(set(odd_cycle)) == 1 and even_cycle[0] != odd_cycle[0]:
            scores[even_cycle[0]] -= 0.38
            scores[odd_cycle[0]] -= 0.38
    if static_streak >= 5:
        for action_index in set(recent_actions[-min(8, len(recent_actions)):]):
            scores[action_index] -= min(2.2, 0.18 * static_streak)
        scores[0] -= min(1.8, 0.14 * static_streak)
    temperature = max(0.55, 0.95 - min(0.35, static_streak * 0.018))
    weights = masked_policy_weights(np, scores / temperature, blocked_actions)
    dynamic_exploration = min(0.65, exploration + min(0.48, static_streak * 0.05))
    if random.random() < dynamic_exploration:
        sampling = np.sqrt(weights)
        sampling_total = float(sampling.sum())
        if math.isfinite(sampling_total) and sampling_total > 1e-12:
            sampling /= sampling_total
            selected = int(np.random.choice(action_count, p=sampling))
            if not blocked_actions or selected == 0 or selected not in blocked_actions:
                return selected
    selected = int(np.argmax(weights))
    if blocked_actions and selected != 0 and selected in blocked_actions:
        return 0
    return selected


def reservoir_add(bucket: list, value, seen_count: int, capacity: int) -> None:
    if len(bucket) < capacity:
        bucket.append(value)
        return
    position = random.randrange(seen_count)
    if position < capacity:
        bucket[position] = value


def human_training_signal(reward: float) -> tuple[float, float, float]:
    quality = max(0.0, min(1.0, float(reward)))
    policy_multiplier = 0.30 + 0.70 * quality
    value_target = 0.10 + 0.80 * quality
    value_weight = 0.18 + 0.22 * quality
    return policy_multiplier, value_target, value_weight


def empirical_action_guidance(
    np,
    reward_values,
    reward_counts,
    effect_values,
    effect_counts,
    risk_values,
    risk_counts,
    cold_start: bool,
):
    arrays = [
        np.asarray(reward_values, dtype=np.float64),
        np.asarray(reward_counts, dtype=np.float64),
        np.asarray(effect_values, dtype=np.float64),
        np.asarray(effect_counts, dtype=np.float64),
        np.asarray(risk_values, dtype=np.float64),
        np.asarray(risk_counts, dtype=np.float64),
    ]
    if not arrays or any(value.shape != arrays[0].shape for value in arrays):
        size = len(arrays[0]) if arrays else 0
        zero = np.zeros(size, dtype=np.float64)
        return zero, zero.copy(), zero.copy(), zero.copy()
    if any(not np.isfinite(value).all() for value in arrays):
        size = len(arrays[0])
        zero = np.zeros(size, dtype=np.float64)
        return zero, zero.copy(), zero.copy(), zero.copy()
    reward_values, reward_counts, effect_values, effect_counts, risk_values, risk_counts = arrays
    reward_counts = np.maximum(0.0, reward_counts)
    effect_counts = np.maximum(0.0, effect_counts)
    risk_counts = np.maximum(0.0, risk_counts)
    reward_confidence = np.minimum(1.0, np.log1p(reward_counts) / math.log(33.0))
    effect_confidence = np.minimum(1.0, np.log1p(effect_counts) / math.log(25.0))
    risk_confidence = np.minimum(1.0, np.log1p(risk_counts) / math.log(25.0))
    reward_guidance = np.clip(reward_values, -1.0, 1.0) * reward_confidence
    effect_guidance = np.clip(effect_values, 0.0, 1.0) * effect_confidence
    risk_guidance = np.clip(risk_values, 0.0, 1.0) * risk_confidence
    uncertainty_scale = 0.09 if cold_start else 0.14
    uncertainty_bonus = uncertainty_scale * (1.0 - reward_confidence) / np.sqrt(reward_counts + 1.0)
    if len(uncertainty_bonus):
        uncertainty_bonus[0] = 0.0
    return reward_guidance, effect_guidance, risk_guidance, uncertainty_bonus


def load_training_data(np, db_path: Path, action_count: int, sample_limit: int, stop_event: threading.Event | None):
    ensure_database(db_path)
    per_action = max(32, math.ceil(sample_limit / max(1, action_count)))
    human_capacity = max(24, int(per_action * 0.78))
    ai_capacity = max(8, per_action - human_capacity)
    historical_buckets: dict[tuple[str, int], list] = {}
    priority_buckets: dict[tuple[str, int], list] = {}
    recent_buckets: dict[tuple[str, int], deque] = {}
    historical_seen: dict[tuple[str, int], int] = {}
    invalid = 0
    invalid_ids: list[int] = []

    def retain_historical(key: tuple[str, int], sample: tuple, sample_id: int, capacity: int) -> None:
        if capacity <= 0:
            return
        source = key[0]
        priority_capacity = max(1, capacity // 2) if source == "ai" and capacity >= 2 else 0
        reservoir_capacity = max(0, capacity - priority_capacity)
        if priority_capacity:
            reward_value = float(sample[2])
            priority = abs(reward_value) + 0.18 * max(0.0, reward_value)
            item = (priority, int(sample_id), sample)
            heap = priority_buckets.setdefault(key, [])
            if len(heap) < priority_capacity:
                heapq.heappush(heap, item)
                return
            if item[:2] > heap[0][:2]:
                displaced = heapq.heapreplace(heap, item)[2]
                historical_seen[key] = historical_seen.get(key, 0) + 1
                if reservoir_capacity:
                    reservoir_add(
                        historical_buckets.setdefault(key, []),
                        displaced,
                        historical_seen[key],
                        reservoir_capacity,
                    )
                return
        historical_seen[key] = historical_seen.get(key, 0) + 1
        if reservoir_capacity:
            reservoir_add(
                historical_buckets.setdefault(key, []),
                sample,
                historical_seen[key],
                reservoir_capacity,
            )

    connection = sqlite3.connect(db_path, timeout=30)
    try:
        cursor = connection.execute("SELECT id, source, action, reward, feature_dim, feature FROM samples ORDER BY id")
        for sample_id, source, action, reward, feature_dim, blob in cursor:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            try:
                action_index = int(action)
                reward_value = float(reward)
                stored_feature_dim = int(feature_dim)
            except (TypeError, ValueError, OverflowError):
                action_index = -1
                reward_value = math.nan
                stored_feature_dim = -1
            if (
                stored_feature_dim not in (LEGACY_FEATURE_DIM, V27_FEATURE_DIM, FEATURE_DIM)
                or not (0 <= action_index < action_count)
                or source not in ("human", "ai")
                or not math.isfinite(reward_value)
                or not -1.0001 <= reward_value <= 1.0001
            ):
                invalid += 1
                invalid_ids.append(int(sample_id))
                continue
            try:
                feature = normalize_feature_bytes(decompress_feature(blob, stored_feature_dim))
            except Exception:
                invalid += 1
                invalid_ids.append(int(sample_id))
                continue
            key = (source, action_index)
            capacity = human_capacity if source == "human" else ai_capacity
            recent_capacity = max(4, min(capacity, math.ceil(capacity * 0.35)))
            historical_capacity = max(0, capacity - recent_capacity)
            recent = recent_buckets.setdefault(key, deque(maxlen=recent_capacity))
            if len(recent) == recent.maxlen:
                evicted_feature, evicted_action, evicted_reward, evicted_source, evicted_id = recent[0]
                retain_historical(
                    key,
                    (evicted_feature, evicted_action, evicted_reward, evicted_source),
                    evicted_id,
                    historical_capacity,
                )
            recent.append((feature, action_index, reward_value, source, int(sample_id)))
    finally:
        if invalid_ids:
            for offset in range(0, len(invalid_ids), 500):
                connection.executemany(
                    "DELETE FROM samples WHERE id=?",
                    ((sample_id,) for sample_id in invalid_ids[offset:offset + 500]),
                )
            connection.commit()
        connection.close()
    samples = []
    for bucket in historical_buckets.values():
        samples.extend((*item, 1.0) for item in bucket)
    for heap in priority_buckets.values():
        samples.extend((*item[2], 1.12) for item in heap)
    for bucket in recent_buckets.values():
        samples.extend((*item[:4], 1.18) for item in bucket)
    if len(samples) > sample_limit:
        samples.sort(
            key=lambda item: (
                float(item[4]),
                1 if item[3] == "human" else abs(float(item[2])),
                random.random(),
            ),
            reverse=True,
        )
        samples = samples[:sample_limit]
    random.shuffle(samples)
    if not samples:
        return None, None, None, None, None, invalid
    x = None
    try:
        x = allocate_training_matrix(np, len(samples), MODEL_INPUT_DIM)
        y = np.empty(len(samples), dtype=np.int64)
        policy_weights = np.empty(len(samples), dtype=np.float32)
        value_targets = np.empty(len(samples), dtype=np.float32)
        value_weights = np.empty(len(samples), dtype=np.float32)
        counts: dict[int, int] = {}
        for _, action, _, _, _ in samples:
            counts[action] = counts.get(action, 0) + 1
        mean_count = sum(counts.values()) / max(1, len(counts))
        vector_cache: dict[bytes, object] = {}
        vector_cache_limit = training_vector_cache_limit(len(samples))
        for index, (feature, action, reward, source, recency_weight) in enumerate(samples):
            cache_key = feature
            vector = vector_cache.get(cache_key)
            if vector is None:
                vector = feature_vector(np, feature)
                if len(vector_cache) < vector_cache_limit:
                    vector_cache[cache_key] = vector
            x[index] = vector
            y[index] = action
            class_weight = min(3.0, max(0.55, (mean_count / max(1, counts[action])) ** 0.5))
            weighted_class = class_weight * float(recency_weight)
            if source == "human":
                policy_multiplier, value_target, value_weight = human_training_signal(reward)
                policy_weights[index] = weighted_class * policy_multiplier
                value_targets[index] = value_target
                value_weights[index] = value_weight * float(recency_weight)
            else:
                bounded_reward = max(-1.0, min(1.0, reward))
                positive_reward = max(0.0, bounded_reward)
                if positive_reward >= 0.02:
                    policy_weights[index] = weighted_class * min(0.60, 0.05 + positive_reward * 0.55)
                elif bounded_reward <= -0.08:
                    policy_weights[index] = -weighted_class * min(0.36, 0.04 + abs(bounded_reward) * 0.32)
                else:
                    policy_weights[index] = 0.0
                value_targets[index] = bounded_reward
                value_weights[index] = float(recency_weight) * (0.58 + 0.42 * abs(bounded_reward))
        return x, y, policy_weights, value_targets, value_weights, invalid
    except Exception:
        release_training_matrix(x)
        raise


def stratified_train_validation_indices(np, labels):
    sample_count = int(len(labels))
    all_indices = np.arange(sample_count, dtype=np.int64)
    if sample_count < 40:
        return all_indices, np.array([], dtype=np.int64)
    train_parts = []
    validation_parts = []
    for label in np.unique(labels):
        indices = np.flatnonzero(labels == label).astype(np.int64, copy=False)
        np.random.shuffle(indices)
        validation_count = 0
        if len(indices) >= 8:
            validation_count = min(len(indices) - 4, max(1, int(round(len(indices) * 0.10))))
        if validation_count:
            validation_parts.append(indices[:validation_count])
            train_parts.append(indices[validation_count:])
        else:
            train_parts.append(indices)
    train_indices = np.concatenate(train_parts) if train_parts else all_indices
    validation_indices = (
        np.concatenate(validation_parts)
        if validation_parts
        else np.array([], dtype=np.int64)
    )
    np.random.shuffle(train_indices)
    if len(validation_indices):
        np.random.shuffle(validation_indices)
    return train_indices, validation_indices


def clip_gradients_by_global_norm(np, gradients: list, maximum_norm: float = 8.0) -> float:
    maximum = max(1e-6, float(maximum_norm))
    global_norm = 0.0
    for gradient in gradients:
        if not np.isfinite(gradient).all():
            raise RuntimeError("训练梯度包含无效数值")
        component_norm = float(np.linalg.norm(gradient))
        global_norm = math.hypot(global_norm, component_norm)
    if global_norm > maximum:
        scale = maximum / max(global_norm, 1e-12)
        for gradient in gradients:
            gradient *= scale
    return global_norm


def train_model(
    np,
    model: dict,
    x,
    y,
    policy_weights,
    value_targets,
    value_weights,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    stop_event: threading.Event | None,
) -> dict:
    sample_count = len(x)
    if sample_count < 8:
        raise RuntimeError("有效经验太少，请先使用“人”或“AI”模式积累经验。")
    train_indices, validation_indices = stratified_train_validation_indices(np, y)
    evaluation_indices = validation_indices if len(validation_indices) else np.arange(sample_count)
    parameters = [
        model["W1"], model["b1"], model["W2"], model["b2"],
        model["Wp"], model["bp"], model["Wv"], model["bv"],
    ]
    moments = [np.zeros_like(value) for value in parameters]
    variances = [np.zeros_like(value) for value in parameters]
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    step = 0

    def evaluate(indices) -> dict:
        eval_x = x[indices]
        eval_y = y[indices]
        hidden1 = np.maximum(0.0, eval_x @ model["W1"] + model["b1"])
        hidden2 = np.maximum(0.0, hidden1 @ model["W2"] + model["b2"])
        logits = hidden2 @ model["Wp"] + model["bp"]
        logits -= logits.max(axis=1, keepdims=True)
        probabilities = np.exp(logits)
        probabilities /= np.maximum(1e-8, probabilities.sum(axis=1, keepdims=True))
        eval_policy_weights = policy_weights[indices].astype(np.float64, copy=False)
        policy_loss, _ = signed_policy_objective(
            np,
            probabilities,
            eval_y,
            eval_policy_weights,
            with_gradient=False,
        )
        positive_policy_weights = np.maximum(eval_policy_weights, 0.0)
        positive_total = float(positive_policy_weights.sum())
        predictions = np.argmax(probabilities, axis=1)
        if positive_total > 1e-8:
            accuracy = float(((predictions == eval_y) * positive_policy_weights).sum() / positive_total)
        else:
            accuracy = 0.0
        eval_values = np.tanh(hidden2 @ model["Wv"] + model["bv"])
        selected_values = eval_values[np.arange(len(indices)), eval_y]
        value_errors = selected_values - value_targets[indices]
        eval_value_weights = value_weights[indices].astype(np.float64, copy=False)
        value_total = max(1e-8, float(eval_value_weights.sum()))
        value_loss = float(((value_errors * value_errors) * eval_value_weights).sum() / value_total)
        value_mae = float((np.abs(value_errors) * eval_value_weights).sum() / value_total)
        score = policy_loss + 0.35 * value_mae - 0.12 * accuracy
        return {
            "loss": policy_loss,
            "value_loss": value_loss,
            "accuracy": accuracy,
            "value_mae": value_mae,
            "score": score,
        }

    best_metrics = evaluate(evaluation_indices)
    previous_training_rounds = int(model.get("training_rounds", 0))
    best_score = float(best_metrics["score"]) if previous_training_rounds > 0 else math.inf
    best_parameters = [parameter.copy() for parameter in parameters]
    epochs_without_improvement = 0
    epochs_completed = 0
    patience = max(2, min(5, max(1, int(epochs)) // 3 + 1))
    for _ in range(max(1, epochs)):
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        epoch_learning_rate = learning_rate * (0.92 ** epochs_completed)
        np.random.shuffle(train_indices)
        for start in range(0, len(train_indices), max(8, batch_size)):
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            indices = train_indices[start:start + max(8, batch_size)]
            batch_x = x[indices].copy()
            pixel_count = FEATURE_WIDTH * FEATURE_HEIGHT
            augmentation_count = len(indices)
            if augmentation_count:
                appearance_gain = np.random.uniform(0.94, 1.06, size=(augmentation_count, 1)).astype(np.float32)
                appearance_shift = np.random.uniform(-0.025, 0.025, size=(augmentation_count, 1)).astype(np.float32)
                batch_x[:, :pixel_count] = np.clip(
                    batch_x[:, :pixel_count] * appearance_gain + appearance_shift,
                    -1.0,
                    1.0,
                )
                temporal_gain = np.random.uniform(0.92, 1.08, size=(augmentation_count, 1)).astype(np.float32)
                batch_x[:, pixel_count:pixel_count * 2] = np.clip(
                    batch_x[:, pixel_count:pixel_count * 2] * temporal_gain,
                    0.0,
                    1.0,
                )
                edge_gain = np.random.uniform(0.94, 1.06, size=(augmentation_count, 1)).astype(np.float32)
                batch_x[:, pixel_count * 2:pixel_count * 3] = np.clip(
                    batch_x[:, pixel_count * 2:pixel_count * 3] * edge_gain,
                    0.0,
                    1.0,
                )
                signed_gain = np.random.uniform(0.92, 1.08, size=(augmentation_count, 1)).astype(np.float32)
                batch_x[:, LEGACY_MODEL_INPUT_DIM:V27_MODEL_INPUT_DIM] = np.clip(
                    batch_x[:, LEGACY_MODEL_INPUT_DIM:V27_MODEL_INPUT_DIM] * signed_gain,
                    -1.0,
                    1.0,
                )
                chroma_gain = np.random.uniform(0.90, 1.10, size=(augmentation_count, 1)).astype(np.float32)
                batch_x[:, V27_MODEL_INPUT_DIM:] = np.clip(
                    batch_x[:, V27_MODEL_INPUT_DIM:] * chroma_gain,
                    -1.0,
                    1.0,
                )
            batch_y = y[indices]
            batch_policy_weights = policy_weights[indices]
            batch_value_targets = value_targets[indices]
            batch_value_weights = value_weights[indices]
            z1 = batch_x @ model["W1"] + model["b1"]
            hidden1 = np.maximum(0.0, z1)
            z2 = hidden1 @ model["W2"] + model["b2"]
            hidden2 = np.maximum(0.0, z2)
            logits = hidden2 @ model["Wp"] + model["bp"]
            logits -= logits.max(axis=1, keepdims=True)
            probabilities = np.exp(logits)
            probabilities /= np.maximum(1e-8, probabilities.sum(axis=1, keepdims=True))
            _, gradient_logits = signed_policy_objective(
                np,
                probabilities,
                batch_y,
                batch_policy_weights,
                with_gradient=True,
            )
            gradient_wp = hidden2.T @ gradient_logits + 1e-5 * model["Wp"]
            gradient_bp = gradient_logits.sum(axis=0)
            gradient_hidden2 = gradient_logits @ model["Wp"].T

            raw_values = hidden2 @ model["Wv"] + model["bv"]
            values = np.tanh(raw_values)
            chosen_values = values[np.arange(len(indices)), batch_y]
            value_errors = chosen_values - batch_value_targets
            value_total = max(1e-6, float(batch_value_weights.sum()))
            huber_delta = 0.45
            robust_value_gradient = np.where(
                np.abs(value_errors) <= huber_delta,
                value_errors,
                huber_delta * np.sign(value_errors),
            )
            gradient_values = np.zeros_like(values)
            gradient_values[np.arange(len(indices)), batch_y] = (
                0.70 * robust_value_gradient * batch_value_weights / value_total
            )
            gradient_raw_values = gradient_values * (1.0 - values * values)
            gradient_wv = hidden2.T @ gradient_raw_values + 1e-5 * model["Wv"]
            gradient_bv = gradient_raw_values.sum(axis=0)
            gradient_hidden2 += gradient_raw_values @ model["Wv"].T

            gradient_hidden2[z2 <= 0] = 0
            gradient_w2 = hidden1.T @ gradient_hidden2 + 1e-5 * model["W2"]
            gradient_b2 = gradient_hidden2.sum(axis=0)
            gradient_hidden1 = gradient_hidden2 @ model["W2"].T
            gradient_hidden1[z1 <= 0] = 0
            gradient_w1 = batch_x.T @ gradient_hidden1 + 1e-5 * model["W1"]
            gradient_b1 = gradient_hidden1.sum(axis=0)
            gradients = [
                gradient_w1, gradient_b1, gradient_w2, gradient_b2,
                gradient_wp, gradient_bp, gradient_wv, gradient_bv,
            ]
            clip_gradients_by_global_norm(np, gradients, 8.0)
            step += 1
            for index, (parameter, gradient) in enumerate(zip(parameters, gradients)):
                np.clip(gradient, -3.0, 3.0, out=gradient)
                moments[index] = beta1 * moments[index] + (1.0 - beta1) * gradient
                variances[index] = beta2 * variances[index] + (1.0 - beta2) * (gradient * gradient)
                corrected_m = moments[index] / (1.0 - beta1 ** step)
                corrected_v = variances[index] / (1.0 - beta2 ** step)
                parameter -= epoch_learning_rate * corrected_m / (np.sqrt(corrected_v) + epsilon)
        epochs_completed += 1
        current_metrics = evaluate(evaluation_indices)
        current_score = float(current_metrics["score"])
        if current_score < best_score - 1e-4:
            best_score = current_score
            best_metrics = current_metrics
            best_parameters = [parameter.copy() for parameter in parameters]
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break
    for parameter, best_parameter in zip(parameters, best_parameters):
        np.copyto(parameter, best_parameter)
    model["trained_samples"] = int(model.get("trained_samples", 0)) + sample_count
    model["training_rounds"] = int(model.get("training_rounds", 0)) + 1
    return {
        "samples": sample_count,
        "loss": float(best_metrics["loss"]),
        "value_loss": float(best_metrics["value_loss"]),
        "accuracy": float(best_metrics["accuracy"]),
        "value_mae": float(best_metrics["value_mae"]),
        "epochs": epochs_completed,
    }

def runtime_self_check(np) -> None:
    if (
        REQUIRED_PYTHON_VERSION != (3, 12)
        or MIN_WINDOWS_11_BUILD != 22000
        or SUPPORTED_X64_MACHINES != frozenset({"amd64", "x86_64"})
        or SCRIPT_NAME != "AnyGameAI.py"
        or STRICT_UI_ACTIONS != ("文件", "人", "升级", "AI")
        or tuple(specification[1] for specification in NativeAnyGameAIApp.BUTTON_SPECS)
        != STRICT_UI_ACTIONS
        or len({specification[0] for specification in NativeAnyGameAIApp.BUTTON_SPECS}) != 4
        or release_version_tuple(APP_VERSION) < (67, 0, 0)
        or CONFIG_SCHEMA < 28
        or INTEGRITY_SCHEMA < 4
        or RUNTIME_INTEGRITY_SCHEMA < 2
        or MAX_RUNTIME_TREE_FILES < MAX_DISTRIBUTION_RECORDS
        or MAX_RUNTIME_TREE_BYTES < MAX_WHEEL_EXPANDED_BYTES
        or int(DEFAULT_CONFIG.get("planning_horizon", 0)) < 4
        or float(DEFAULT_CONFIG.get("planning_weight", 0.0)) < 0.28
        or int(DEFAULT_CONFIG.get("planning_refresh_steps", 9999)) > 48
        or not 0.60 <= float(DEFAULT_CONFIG.get("online_td_discount", -1.0)) <= 0.90
        or not 16 <= int(DEFAULT_CONFIG.get("target_network_sync_steps", 0)) <= 4096
        or not 0.01 <= float(DEFAULT_CONFIG.get("target_network_soft_update", 0.0)) <= 1.0
        or not 0.0 < float(DEFAULT_CONFIG.get("target_ensemble_weight", 0.0)) <= 0.5
        or not 0.0 < float(DEFAULT_CONFIG.get("model_uncertainty_weight", 0.0)) <= 0.5
        or not 0.0 < ONLINE_REPRESENTATION_SCALE_DEFAULT <= 0.15
        or not 0.0 < ONLINE_INPUT_ADAPTATION_SCALE_DEFAULT <= 0.25
        or not 16 <= ONLINE_INPUT_ADAPTATION_FEATURES_DEFAULT <= 256
        or MAX_PROCESS_OUTPUT_QUEUE_LINES < 256
        or DEFAULT_HIDDEN_SIZE < 192
        or MAX_MODEL_EXPANDED_BYTES < MAX_MODEL_ARCHIVE_BYTES
        or not 0.0 < HUMAN_ACTION_APPROXIMATE_WEIGHT < HUMAN_ACTION_MEMORY_WEIGHT <= 1.0
        or HUMAN_ACTION_MEMORY_LIMIT < 1000
    ):
        raise RuntimeError("运行平台约束自检失败")
    if set(CONFIG_RANGES) != set(DEFAULT_CONFIG) - {"schema"} or not validate_config(deep_copy_json(DEFAULT_CONFIG)):
        raise RuntimeError("默认配置自检失败")
    low_training = adaptive_training_settings(DEFAULT_CONFIG, 512 * 1024 ** 2, 2)
    high_training = adaptive_training_settings(DEFAULT_CONFIG, 32 * 1024 ** 3, 16)
    low_global_training = adaptive_global_training_settings(
        DEFAULT_CONFIG,
        12,
        512 * 1024 ** 2,
        2,
    )
    high_global_training = adaptive_global_training_settings(
        DEFAULT_CONFIG,
        12,
        32 * 1024 ** 3,
        16,
    )
    if (
        low_training["sample_limit"] > int(DEFAULT_CONFIG["train_sample_limit_per_game"])
        or low_training["epochs"] > int(DEFAULT_CONFIG["training_epochs"])
        or low_training["batch_size"] > int(DEFAULT_CONFIG["training_batch_size"])
        or high_training["sample_limit"] < int(DEFAULT_CONFIG["train_sample_limit_per_game"])
        or high_training["epochs"] < int(DEFAULT_CONFIG["training_epochs"])
        or high_training["batch_size"] < int(DEFAULT_CONFIG["training_batch_size"])
        or high_training["sample_limit"] > int(DEFAULT_CONFIG["experience_limit_per_game"])
        or low_global_training["sample_limit"] > high_global_training["sample_limit"]
        or low_global_training["per_profile_limit"] > low_global_training["sample_limit"]
        or high_global_training["sample_limit"] > GLOBAL_TRAINING_SAMPLE_LIMIT
        or high_global_training["epochs"] > high_training["epochs"]
        or high_global_training["batch_size"] != high_training["batch_size"]
    ):
        raise RuntimeError("自适应训练预算自检失败")
    low_runtime = adaptive_runtime_settings(DEFAULT_CONFIG, 512 * 1024 ** 2, 2)
    medium_runtime = adaptive_runtime_settings(DEFAULT_CONFIG, 6 * 1024 ** 3, 8)
    high_runtime = adaptive_runtime_settings(DEFAULT_CONFIG, 32 * 1024 ** 3, 16)
    if (
        float(low_runtime["sample_interval_seconds"])
        <= float(medium_runtime["sample_interval_seconds"])
        or float(medium_runtime["sample_interval_seconds"])
        <= float(high_runtime["sample_interval_seconds"])
        or float(low_runtime["step_pause_seconds"])
        <= float(high_runtime["step_pause_seconds"])
        or int(low_runtime["planning_horizon"]) >= int(high_runtime["planning_horizon"])
        or int(low_runtime["planning_refresh_steps"])
        <= int(high_runtime["planning_refresh_steps"])
        or int(low_runtime["online_checkpoint_steps"])
        <= int(high_runtime["online_checkpoint_steps"])
        or int(low_runtime["translation_search_radius"])
        >= int(high_runtime["translation_search_radius"])
        or runtime_numeric_thread_budget(512 * 1024 ** 2, 2) != 1
        or runtime_numeric_thread_budget(4 * 1024 ** 3, 6) != 2
        or runtime_numeric_thread_budget(12 * 1024 ** 3, 10) != 3
        or runtime_numeric_thread_budget(32 * 1024 ** 3, 16) != 4
    ):
        raise RuntimeError("运行期硬件自适应自检失败")
    low_cache = training_vector_cache_limit(16000, 512 * 1024 ** 2)
    medium_cache = training_vector_cache_limit(16000, 4 * 1024 ** 3)
    high_cache = training_vector_cache_limit(16000, 32 * 1024 ** 3)
    if not 64 <= low_cache < medium_cache < high_cache <= 8192:
        raise RuntimeError("训练特征缓存预算自检失败")
    gradient_a = np.asarray([3.0, 4.0], dtype=np.float32)
    gradient_b = np.asarray([0.0, 12.0], dtype=np.float32)
    original_gradient_norm = clip_gradients_by_global_norm(np, [gradient_a, gradient_b], 6.5)
    clipped_gradient_norm = math.hypot(
        float(np.linalg.norm(gradient_a)),
        float(np.linalg.norm(gradient_b)),
    )
    if not (12.9 < original_gradient_norm < 13.1 and clipped_gradient_norm <= 6.5001):
        raise RuntimeError("训练梯度稳定器自检失败")
    blend_probabilities, blend_values, blend_drift = temporal_policy_blend(
        np,
        np.asarray([0.92, 0.08], dtype=np.float64),
        np.asarray([0.7, -0.2], dtype=np.float64),
        np.asarray([0.10, 0.90], dtype=np.float64),
        np.asarray([-0.1, 0.4], dtype=np.float64),
        0.14,
        0,
    )
    if not (
        blend_probabilities[0] > 0.90
        and blend_values[0] > 0.65
        and blend_drift > 0.80
        and abs(float(blend_probabilities.sum()) - 1.0) <= 1e-8
    ):
        raise RuntimeError("场景切换策略响应自检失败")
    uncertain_exploration = adaptive_exploration_rate(0.07, 0.10, 0.0, 0.20, -0.60, 16)
    confident_exploration = adaptive_exploration_rate(0.07, 0.95, 1.0, 0.0, 0.70, 16)
    cold_exploration = adaptive_exploration_rate(0.26, 0.0, 0.0, 1.0, 0.0, 0)
    if not (
        0.0 <= confident_exploration < uncertain_exploration <= 0.75
        and cold_exploration > uncertain_exploration
        and adaptive_exploration_rate(5.0, math.nan, math.inf, -math.inf, math.nan, -1) == 0.75
    ):
        raise RuntimeError("会话奖励自适应探索自检失败")
    guidance = empirical_action_guidance(
        np,
        [0.6, 0.8, -0.4],
        [32, 0, 1],
        [0.5, 0.9, 0.2],
        [32, 0, 1],
        [0.1, 0.8, 0.5],
        [32, 0, 1],
        False,
    )
    if (
        any(value.shape != (3,) or not np.isfinite(value).all() for value in guidance)
        or guidance[0][0] <= 0.0
        or guidance[0][1] != 0.0
        or guidance[3][1] <= guidance[3][2]
    ):
        raise RuntimeError("经验置信度引导自检失败")
    validate_managed_storage_layout()
    if not SOURCE_SCRIPT_PATH.is_absolute():
        raise RuntimeError("主程序源路径自检失败")
    idle_demonstration = human_demonstration_reward(True)
    active_demonstration = human_demonstration_reward(False)
    weak_effect_reward = human_observed_effect_reward(False, 0.0)
    strong_effect_reward = human_observed_effect_reward(False, 1.0)
    if not (
        idle_demonstration == 0.08
        and active_demonstration == 0.90
        and 0.70 <= weak_effect_reward < strong_effect_reward <= 1.0
    ):
        raise RuntimeError("人工示范因果反馈自检失败")
    idle_signal = human_training_signal(idle_demonstration)
    active_signal = human_training_signal(active_demonstration)
    if (
        not all(math.isfinite(value) for value in idle_signal + active_signal)
        or not all(active > idle for idle, active in zip(idle_signal, active_signal))
        or human_training_signal(-1.0) != human_training_signal(0.0)
        or human_training_signal(2.0) != human_training_signal(1.0)
    ):
        raise RuntimeError("人工示范质量自检失败")
    actions = universal_actions()
    if not actions or len(actions) > UNIVERSAL_ACTION_LIMIT:
        raise RuntimeError("通用动作集自检失败")
    signatures = [action_signature(action) for action in actions]
    if len(signatures) != len(set(signatures)):
        raise RuntimeError("通用动作集包含重复项")
    if any(ESC_VK in action["keys"] for action in actions):
        raise RuntimeError("通用动作集包含安全退出键")
    if any(action["keys"] and set(action["keys"]).issubset({0x10, 0x11, 0x12}) for action in actions):
        raise RuntimeError("通用动作集包含独立修饰键")
    if any(0x11 in action["keys"] for action in actions):
        raise RuntimeError("通用动作集包含高风险 Ctrl 组合")
    if not target_action_blocked({"keys": [0x11, 0x57]}, "generic", "chrome"):
        raise RuntimeError("浏览器快捷键隔离自检失败")
    if normalized_action({"keys": [0x12, 0x09]})["keys"]:
        raise RuntimeError("系统切换快捷键隔离自检失败")
    if normalized_action({"keys": [0x12, 0x20]})["keys"]:
        raise RuntimeError("系统菜单快捷键隔离自检失败")
    if target_action_blocked({"keys": [0x57]}, "generic", "chrome"):
        raise RuntimeError("浏览器游戏按键隔离过度")
    if not target_action_blocked({"keys": [0x74]}, "generic", "chrome"):
        raise RuntimeError("浏览器功能键隔离自检失败")
    if target_action_blocked({"keys": [0x74]}, "human", "chrome"):
        raise RuntimeError("浏览器人工功能键隔离过度")
    if not any(abs(action["mouse_dx"]) == 2 or abs(action["mouse_dy"]) == 2 for action in actions):
        raise RuntimeError("通用动作集缺少粗粒度鼠标移动")
    if sum(action["mouse_x"] >= 0 and "left" in action["buttons"] for action in actions) < 30:
        raise RuntimeError("通用动作集缺少点击区域覆盖")
    if len(actions) < 250:
        raise RuntimeError("通用动作集覆盖不足")
    if sum(action["repeat"] == 2 and action["buttons"] == ["left"] for action in actions) < 6:
        raise RuntimeError("通用动作集缺少双击动作")
    malformed_action = normalized_action(
        {"keys": ["invalid", 0x57, None], "buttons": "left", "mouse_dx": "invalid", "mouse_x": 999}
    )
    if malformed_action["keys"] != [0x57] or malformed_action["buttons"] or malformed_action["mouse_x"] != -1:
        raise RuntimeError("动作数据清洗自检失败")
    if normalized_action({"keys": [0x10]})["keys"] != [0x10]:
        raise RuntimeError("人工 Shift 动作保留自检失败")
    if normalized_action({"keys": [0x11]})["keys"] != [0x11]:
        raise RuntimeError("人工 Ctrl 动作保留自检失败")
    if normalized_action({"keys": [0x12]})["keys"]:
        raise RuntimeError("独立 Alt 动作隔离自检失败")
    if target_action_blocked({"keys": [0x11]}, "human", "game"):
        raise RuntimeError("人工 Ctrl 动作隔离过度")
    if not target_action_blocked({"keys": [0x11]}, "generic", "game"):
        raise RuntimeError("通用 Ctrl 动作隔离不足")
    probe_profile = default_profile({"id": "self-check", "name": "self-check"})
    ensure_action_metadata(probe_profile)
    probe_actions = cold_start_probe_actions(probe_profile, {})
    if not probe_actions or len(probe_actions) > COLD_START_PROBE_LIMIT:
        raise RuntimeError("通用控制探测自检失败")
    update_control_response(probe_profile, probe_actions[0], 0.25)
    update_action_effect(probe_profile, probe_actions[0], 0.40)
    evidence = control_response_evidence(probe_profile)
    if set(evidence) != set(CONTROL_KINDS) or not all(math.isfinite(value) for value in evidence.values()):
        raise RuntimeError("控制反馈自检失败")
    if probe_profile["action_effect_counts"][probe_actions[0]] != 1:
        raise RuntimeError("动作可控性自检失败")
    update_action_risk(probe_profile, probe_actions[0], 0.60)
    if probe_profile["action_risk_counts"][probe_actions[0]] != 1:
        raise RuntimeError("动作风险自检失败")
    if len(actions) >= 3:
        record_transition(probe_profile, 0, 1)
        record_transition(probe_profile, 1, 2, 0, 8)
        sequence = transition_distribution(np, probe_profile, 1, len(actions), 0, 0.8)
        if sequence.shape != (len(actions),) or int(np.argmax(sequence)) != 2:
            raise RuntimeError("动作序列学习自检失败")
        hold = adaptive_action_hold(probe_profile, 1, 0.075, 0.01, 8, 0.35)
        if not math.isfinite(hold) or not 0.02 <= hold <= 0.75:
            raise RuntimeError("自适应动作时长自检失败")
        planning_profile = default_profile({"id": "planning-check", "name": "planning-check"})
        ensure_action_metadata(planning_profile)
        planning_profile["action_reward_ema"][2] = 0.9
        planning_profile["action_reward_counts"][2] = 32
        planning_profile["action_effect_ema"][2] = 0.8
        planning_profile["action_effect_counts"][2] = 32
        record_transition(planning_profile, 0, 1, None, 16)
        record_transition(planning_profile, 1, 2, None, 16)
        planning = sequence_plan_values(np, planning_profile, len(actions), 3, 0.68)
        if planning.shape != (len(actions),) or planning[0] <= 0.05 or not np.isfinite(planning).all():
            raise RuntimeError("多步动作规划自检失败")
    if stable_release_tuple("2.1.3") != (2, 1, 3) or stable_release_tuple("3.0.0") is not None:
        raise RuntimeError("运行组件版本选择自检失败")
    wheel_probe = select_numpy_wheel(
        {
            "releases": {
                "2.1.0": [
                    {
                        "packagetype": "bdist_wheel",
                        "yanked": False,
                        "filename": "numpy-2.1.0-cp312-cp312-win_amd64.whl",
                        "url": "https://files.pythonhosted.org/packages/numpy.whl",
                        "digests": {"sha256": "a" * 64},
                        "size": 10_000_000,
                    }
                ]
            }
        }
    )
    if wheel_probe.get("filename") != "numpy-2.1.0-cp312-cp312-win_amd64.whl":
        raise RuntimeError("运行组件安全下载器自检失败")
    try:
        select_numpy_wheel(
            {
                "releases": {
                    "2.1.0": [
                        {
                            "packagetype": "bdist_wheel",
                            "yanked": False,
                            "filename": "numpy-2.0.0-cp312-cp312-win_amd64.whl",
                            "url": "https://files.pythonhosted.org/packages/numpy.whl",
                            "digests": {"sha256": "b" * 64},
                            "size": 10_000_000,
                        }
                    ]
                }
            }
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError("运行组件版本与文件名一致性自检失败")
    runtime_snapshot_probe = {
        "distribution": "numpy",
        "version": "2.1.0",
        "file_count": 100,
        "record_sha256": "1" * 64,
        "content_sha256": "2" * 64,
        "tree_file_count": 104,
        "tree_size": 4096,
        "tree_sha256": "3" * 64,
    }
    if (
        not runtime_integrity_matches(runtime_snapshot_probe, dict(runtime_snapshot_probe))
        or runtime_integrity_matches(
            runtime_snapshot_probe,
            {**runtime_snapshot_probe, "tree_sha256": "4" * 64},
        )
    ):
        raise RuntimeError("运行组件完整目录基线自检失败")
    for unsafe_member in ("../escape", "folder\\escape", "file:stream", "CON.txt", "name. "):
        try:
            wheel_member_destination(APP_DIR, unsafe_member)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("运行组件路径隔离自检失败")
    blended = blend_control_preferences({"keyboard": 0.2}, {"click": 1.0}, 0, 0.5)
    if blended.get("click", 0.0) <= 0.0 or blended.get("keyboard", 0.0) <= 0.0:
        raise RuntimeError("跨游戏控制迁移自检失败")
    cycle = visual_cycle_score(["0" * 16] * 4, "0" * 16)
    if not 0.5 <= cycle <= 1.0:
        raise RuntimeError("状态循环识别自检失败")
    before = bytes(FEATURE_WIDTH * FEATURE_HEIGHT)
    marked = overlay_cursor_marker(before, FEATURE_WIDTH // 2, FEATURE_HEIGHT // 2)
    if marked == before or len(marked) != len(before):
        raise RuntimeError("鼠标位置视觉编码自检失败")
    target_biases = visual_action_target_biases(marked, before, actions)
    if len(target_biases) != len(actions) or not all(math.isfinite(value) for value in target_biases):
        raise RuntimeError("视觉点击目标自检失败")
    ui_frame = bytes(
        240 if ((index % FEATURE_WIDTH) // 2 + (index // FEATURE_WIDTH) // 2) % 2 else 16
        for index in range(FEATURE_WIDTH * FEATURE_HEIGHT)
    )
    context_name, context_biases = infer_scene_context(ui_frame, ui_frame, 0)
    if context_name != "static_ui" or context_biases.get("click", 0.0) <= context_biases.get("idle", 0.0):
        raise RuntimeError("通用场景控制路由自检失败")
    update_scene_control_response(probe_profile, context_name, probe_actions[0], 0.35)
    scene_evidence = scene_control_response_evidence(probe_profile, context_name)
    if not all(math.isfinite(value) for value in scene_evidence.values()):
        raise RuntimeError("场景控制反馈自检失败")
    update_scene_action_response(probe_profile, context_name, probe_actions[0], 0.45)
    scene_action_evidence = scene_action_response_evidence(probe_profile, context_name)
    if (
        len(scene_action_evidence) != len(actions)
        or scene_action_evidence[probe_actions[0]] <= 0.0
        or not all(math.isfinite(value) for value in scene_action_evidence)
    ):
        raise RuntimeError("场景动作记忆自检失败")
    signature = action_signature(actions[probe_actions[0]])
    transferred_action_values = cross_game_scene_action_values(
        {context_name: {signature: (0.70, 1.0)}},
        context_name,
        actions,
    )
    if transferred_action_values[probe_actions[0]] <= 0.60:
        raise RuntimeError("跨游戏动作迁移自检失败")
    transferred_scene = blended_scene_control_evidence(
        probe_profile,
        context_name,
        {context_name: {"click": 0.8}},
        0.5,
    )
    if transferred_scene.get("click", 0.0) <= 0.0:
        raise RuntimeError("跨游戏场景迁移自检失败")
    contextual_candidates = probe_actions[:]
    contextual_choice = choose_contextual_probe_action(
        probe_profile,
        contextual_candidates,
        set(),
        {},
        "self-check",
        context_biases,
        0.55,
        1,
    )
    if contextual_choice is None or len(contextual_candidates) != len(probe_actions) - 1:
        raise RuntimeError("场景化探测自检失败")
    immediate = bytearray(before)
    settled = bytearray(before)
    for index in range(100):
        immediate[index] = 48
    for index in range(80):
        settled[index] = 40
    persistence, transient = visual_persistence_metrics(before, bytes(immediate), bytes(settled))
    if not 0.75 <= persistence <= 0.85 or not 0.0 < transient < 0.05:
        raise RuntimeError("画面变化持续性自检失败")
    neutral_chroma = bytes([128]) * COLOR_PIXELS
    if not frame_capture_failed(before, neutral_chroma, neutral_chroma):
        raise RuntimeError("无效画面识别自检失败")
    if frame_capture_failed(bytes([64]) * len(before), neutral_chroma, neutral_chroma):
        raise RuntimeError("有效纯色画面识别自检失败")
    textured = bytes((index * 37 + (index // FEATURE_WIDTH) * 19) & 0xFF for index in range(FEATURE_WIDTH * FEATURE_HEIGHT))
    translated = bytearray(textured)
    for y in range(FEATURE_HEIGHT):
        row = y * FEATURE_WIDTH
        for x in range(1, FEATURE_WIDTH):
            translated[row + x] = textured[row + x - 1]
    translation_dx, translation_dy, translation_confidence = estimate_visual_translation(textured, bytes(translated), 2)
    if translation_dx == 0 and translation_dy == 0 or translation_confidence <= 0.05:
        raise RuntimeError("画面空间进展自检失败")
    if uniform_brightness_change(before, bytes([64]) * len(before)) <= 0.55:
        raise RuntimeError("全屏明暗变化抑制自检失败")
    world_change, hud_change, side_change = scene_progress_metrics(before, bytes(settled))
    if not all(math.isfinite(value) and value >= 0.0 for value in (world_change, hud_change, side_change)):
        raise RuntimeError("场景进展特征自检失败")
    chooser_probe = choose_policy_action(
        np,
        np.full(len(actions), 1.0 / len(actions), dtype=np.float64),
        np.zeros(len(actions), dtype=np.float64),
        None,
        0.0,
        [],
        0,
        {1} if len(actions) > 1 else set(),
    )
    if len(actions) > 1 and chooser_probe == 1:
        raise RuntimeError("动作冷却自检失败")
    masked_probe = masked_policy_weights(
        np,
        np.asarray([0.0, 100.0, 80.0], dtype=np.float64),
        {1, 2},
    )
    if (
        masked_probe.shape != (3,)
        or masked_probe[0] != 1.0
        or masked_probe[1] != 0.0
        or masked_probe[2] != 0.0
    ):
        raise RuntimeError("封锁动作零概率自检失败")
    recovery = choose_recovery_action(
        probe_profile,
        "self-check",
        {},
        [],
        8,
        12,
        {},
        evidence,
    )
    if recovery is None or not 0 <= recovery < len(actions) or action_kind(actions[recovery]) == "idle":
        raise RuntimeError("卡死恢复自检失败")
    pixel_count = FEATURE_WIDTH * FEATURE_HEIGHT
    current = bytes((index * 37 + 19) & 0xFF for index in range(pixel_count))
    previous = bytes((index * 17 + 7) & 0xFF for index in range(pixel_count))
    chroma_blue = bytes(max(0, min(255, 128 + ((index % COLOR_WIDTH) - COLOR_WIDTH // 2) * 4)) for index in range(COLOR_PIXELS))
    chroma_red = bytes(max(0, min(255, 128 + ((index // COLOR_WIDTH) - COLOR_HEIGHT // 2) * 6)) for index in range(COLOR_PIXELS))
    feature = make_feature(current, previous, chroma_blue, chroma_red)
    color_motion, color_ratio = chroma_change_metrics(
        neutral_chroma,
        neutral_chroma,
        chroma_blue,
        chroma_red,
    )
    if color_motion <= 0.0 or color_ratio <= 0.0:
        raise RuntimeError("颜色变化识别自检失败")
    color_hash = frame_hash(current, chroma_blue, chroma_red)
    neutral_hash = frame_hash(current, neutral_chroma, neutral_chroma)
    if len(color_hash) != 20 or color_hash == neutral_hash:
        raise RuntimeError("颜色场景指纹自检失败")
    memory_key = memory_state_key(current, feature)
    if STATE_MEMORY_KEY_PATTERN.fullmatch(memory_key) is None:
        raise RuntimeError("场景记忆键自检失败")
    memory: dict[tuple[str, int], tuple[float, int]] = {}
    update_state_value_memory(memory, (memory_key, 0), 0.5, 0.16)
    if memory.get((memory_key, 0), (0.0, 0))[1] != 1:
        raise RuntimeError("场景记忆更新自检失败")
    visit_totals = build_state_visit_totals(memory)
    if visit_totals.get(memory_key) != 1:
        raise RuntimeError("跨会话场景访问统计自检失败")
    frontier_value = persistent_frontier_reward({}, memory_key, 0.20, True, 0.16)
    if not 0.0 < frontier_value <= 0.16:
        raise RuntimeError("跨会话探索前沿自检失败")
    bootstrapped_value = bootstrapped_state_reward(memory, memory_key, len(actions), 0.10, 0.22)
    if not 0.10 < bootstrapped_value <= 1.0:
        raise RuntimeError("长期状态价值回传自检失败")
    memory_index = build_state_memory_index(memory)
    neighboring_hash = (int(memory_key[:8], 16) ^ 1) & 0xFFFFFFFF
    neighboring_key = f"{neighboring_hash:08x}:{memory_key[9]}:{memory_key[11]}"
    approximate_values = approximate_state_action_values(memory_index, neighboring_key, len(actions))
    if 0 not in approximate_values or approximate_values[0][0] <= 0.0:
        raise RuntimeError("近似场景记忆自检失败")
    human_memory: dict[tuple[str, int], int] = {}
    demonstrated_action = 1 if len(actions) > 1 else 0
    update_human_action_memory(human_memory, (memory_key, demonstrated_action))
    update_human_action_memory(human_memory, (memory_key, demonstrated_action))
    human_memory_index = build_human_action_memory_index(human_memory)
    exact_human_biases = human_action_memory_biases(
        human_memory,
        human_memory_index,
        memory_key,
        len(actions),
    )
    approximate_human_biases = human_action_memory_biases(
        human_memory,
        human_memory_index,
        neighboring_key,
        len(actions),
    )
    if (
        human_memory.get((memory_key, demonstrated_action)) != 2
        or exact_human_biases[demonstrated_action] <= 0.0
        or approximate_human_biases[demonstrated_action] <= 0.0
        or exact_human_biases[demonstrated_action]
        <= approximate_human_biases[demonstrated_action]
    ):
        raise RuntimeError("人工示范场景记忆自检失败")
    if decompress_feature(compress_feature(feature), FEATURE_DIM) != feature:
        raise RuntimeError("经验压缩自检失败")
    legacy_feature = feature[:LEGACY_FEATURE_DIM]
    normalized_legacy = normalize_feature_bytes(legacy_feature)
    if (
        len(normalized_legacy) != FEATURE_DIM
        or normalized_legacy[LEGACY_FEATURE_DIM:V27_FEATURE_DIM] != bytes([128]) * pixel_count
        or normalized_legacy[V27_FEATURE_DIM:] != bytes([128]) * COLOR_FEATURE_DIM
    ):
        raise RuntimeError("旧经验兼容自检失败")
    normalized_v27 = normalize_feature_bytes(feature[:V27_FEATURE_DIM])
    if normalized_v27[V27_FEATURE_DIM:] != bytes([128]) * COLOR_FEATURE_DIM:
        raise RuntimeError("上一版经验兼容自检失败")
    vector = feature_vector(np, feature)
    if vector.shape != (MODEL_INPUT_DIM,) or not np.isfinite(vector).all():
        raise RuntimeError("视觉特征自检失败")
    histogram_features = vector[LEGACY_MODEL_INPUT_DIM - 16:LEGACY_MODEL_INPUT_DIM]
    if abs(float(histogram_features[:8].sum()) - 1.0) > 1e-4 or abs(float(histogram_features[8:].sum()) - 1.0) > 1e-4:
        raise RuntimeError("视觉分布特征自检失败")
    signed_features = vector[LEGACY_MODEL_INPUT_DIM:V27_MODEL_INPUT_DIM]
    if signed_features.shape != (pixel_count,) or not np.any(np.abs(signed_features) > 0.001):
        raise RuntimeError("方向变化特征自检失败")
    color_features = vector[V27_MODEL_INPUT_DIM:]
    if color_features.shape != (COLOR_FEATURE_DIM,) or not np.any(np.abs(color_features) > 0.001):
        raise RuntimeError("颜色视觉特征自检失败")
    split_labels = np.repeat(np.arange(3, dtype=np.int64), 15)
    split_train, split_validation = stratified_train_validation_indices(np, split_labels)
    if not len(split_validation) or set(split_labels[split_validation].tolist()) - set(split_labels[split_train].tolist()):
        raise RuntimeError("分层训练验证拆分自检失败")
    uniform_confidence = calibrated_policy_confidence(
        np,
        np.full(4, 0.25, dtype=np.float64),
        np.zeros(4, dtype=np.float64),
    )
    aligned_confidence = calibrated_policy_confidence(
        np,
        np.asarray([0.88, 0.05, 0.04, 0.03], dtype=np.float64),
        np.asarray([0.80, 0.10, -0.10, -0.20], dtype=np.float64),
    )
    disagreed_confidence = calibrated_policy_confidence(
        np,
        np.asarray([0.88, 0.05, 0.04, 0.03], dtype=np.float64),
        np.asarray([-0.20, 0.80, 0.10, -0.10], dtype=np.float64),
    )
    if not 0.0 <= uniform_confidence < disagreed_confidence < aligned_confidence <= 1.0:
        raise RuntimeError("策略价值置信度自检失败")
    policy_probe = np.asarray([[0.80, 0.10, 0.10]], dtype=np.float64)
    positive_loss, positive_gradient = signed_policy_objective(
        np, policy_probe, np.asarray([0]), np.asarray([1.0]), with_gradient=True
    )
    avoidance_loss, avoidance_gradient = signed_policy_objective(
        np, policy_probe, np.asarray([0]), np.asarray([-1.0]), with_gradient=True
    )
    if (
        not math.isfinite(positive_loss)
        or not math.isfinite(avoidance_loss)
        or positive_gradient[0, 0] >= 0.0
        or avoidance_gradient[0, 0] <= 0.0
        or not np.all(avoidance_gradient[0, 1:] < 0.0)
    ):
        raise RuntimeError("失败动作反向学习自检失败")
    clean_online_reliability = online_update_reliability(1.0, 0.0, 0.0, 0.0, False)
    noisy_online_reliability = online_update_reliability(0.2, 0.8, 0.6, 0.8, False)
    black_online_reliability = online_update_reliability(1.0, 0.0, 0.0, 0.0, True)
    if (
        not 0.95 <= clean_online_reliability <= 1.0
        or not 0.05 <= noisy_online_reliability < black_online_reliability < clean_online_reliability
    ):
        raise RuntimeError("在线学习抗噪权重自检失败")
    model = initialize_model(np, MODEL_INPUT_DIM, 24, len(actions))
    model["action_signatures"] = signatures
    model["action_hash"] = actions_hash(actions)
    target_probe = clone_target_model(np, model)
    source_bias = float(model["bv"][0])
    target_bias = float(target_probe["bv"][0])
    model["bv"][0] = source_bias + 0.8
    if abs(float(target_probe["bv"][0]) - target_bias) > 1e-8:
        raise RuntimeError("目标网络独立副本自检失败")
    soft_update_target_model(np, target_probe, model, 0.25)
    if abs(float(target_probe["bv"][0]) - (target_bias + 0.2)) > 1e-5:
        raise RuntimeError("目标网络软同步自检失败")
    online_probabilities, online_values = model_outputs(np, model, feature)
    target_probabilities, target_values = model_outputs(np, target_probe, feature)
    ensemble_probabilities, ensemble_values, ensemble_uncertainty, ensemble_disagreement = (
        model_ensemble_outputs(
            np,
            model,
            target_probe,
            feature,
            TARGET_ENSEMBLE_WEIGHT_DEFAULT,
        )
    )
    lower_value = min(float(online_values[0]), float(target_values[0]))
    upper_value = max(float(online_values[0]), float(target_values[0]))
    if (
        ensemble_probabilities.shape != online_probabilities.shape
        or ensemble_values.shape != online_values.shape
        or ensemble_uncertainty.shape != online_values.shape
        or not np.isfinite(ensemble_probabilities).all()
        or not np.isfinite(ensemble_values).all()
        or not np.isfinite(ensemble_uncertainty).all()
        or abs(float(ensemble_probabilities.sum()) - 1.0) > 1e-8
        or not lower_value <= float(ensemble_values[0]) <= upper_value
        or ensemble_uncertainty[0] <= 0.0
        or ensemble_disagreement <= 0.0
    ):
        raise RuntimeError("目标网络稳定集成自检失败")
    model["bv"][0] = source_bias
    probabilities, values = model_outputs(np, model, feature)
    original_value_weights = model["Wv"].copy()
    original_value_bias = model["bv"].copy()
    model["Wv"].fill(0.0)
    model["bv"].fill(float(np.arctanh(0.5)))
    model["trained_samples"] = 128
    immediate_target = temporal_difference_target(np, model, 0.2)
    bootstrapped_target = temporal_difference_target(np, model, 0.2, feature, 0.72, False)
    terminal_target = temporal_difference_target(np, model, 0.2, feature, 0.72, True)
    conservative_target_model = clone_target_model(np, model)
    conservative_target_model["Wv"].fill(0.0)
    conservative_target_model["bv"].fill(float(np.arctanh(-0.5)))
    conservative_target = temporal_difference_target(
        np,
        model,
        0.2,
        feature,
        0.72,
        False,
        conservative_target_model,
    )
    np.copyto(model["Wv"], original_value_weights)
    np.copyto(model["bv"], original_value_bias)
    model["trained_samples"] = 0
    if not (
        abs(immediate_target - 0.2) <= 1e-8
        and 0.32 < bootstrapped_target <= 0.56
        and abs(terminal_target - immediate_target) <= 1e-8
        and conservative_target < immediate_target
    ):
        raise RuntimeError("目标网络时序差分自检失败")
    previous_updates = int(model.get("online_updates", 0))
    online_target_model = clone_target_model(np, model)
    input_representation_before = model["W1"].copy()
    representation_before = model["W2"].copy()
    if not online_model_update(
        np,
        model,
        feature,
        0,
        0.5,
        0.005,
        target_model=online_target_model,
    ):
        raise RuntimeError("在线模型适应自检失败")
    if int(model.get("online_updates", 0)) != previous_updates + 1:
        raise RuntimeError("在线模型更新计数自检失败")
    if not np.any(model["W2"] != representation_before):
        raise RuntimeError("在线场景表征适应自检失败")
    changed_input_rows = int(np.count_nonzero(np.any(model["W1"] != input_representation_before, axis=1)))
    if not 1 <= changed_input_rows <= ONLINE_INPUT_ADAPTATION_FEATURES_DEFAULT:
        raise RuntimeError("在线视觉表征稀疏适应自检失败")
    probabilities, values = model_outputs(np, model, feature)
    if (
        probabilities.shape != (len(actions),)
        or values.shape != (len(actions),)
        or not np.isfinite(probabilities).all()
        or not np.isfinite(values).all()
        or abs(float(probabilities.sum()) - 1.0) > 1e-4
    ):
        raise RuntimeError("AI模型自检失败")


def validate_model_file(path: Path, profile: dict, config: dict) -> bool:
    np = import_numpy()
    model, changed = load_model(
        np,
        path,
        MODEL_INPUT_DIM,
        int(config["hidden_size"]),
        len(profile["actions"]),
        profile["actions"],
    )
    if changed or not path.is_file():
        save_model(np, path, model)
        return True
    return False


def repair_profile(profile_id: str, config: dict, stop_event: threading.Event | None = None) -> dict:
    paths = profile_paths(profile_id, repair_unsafe=True)
    repaired = 0
    removed = 0
    try:
        candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
        profile = migrate_profile(candidate, profile_id)
        if profile is None:
            raise ValueError
        if profile != candidate:
            atomic_write_json(paths["profile"], profile)
            repaired += 1
    except Exception:
        backup_corrupt(paths["profile"])
        identity = {"id": profile_id, "name": profile_id, "title": "", "window_class": "", "executable": ""}
        profile = default_profile(identity)
        atomic_write_json(paths["profile"], profile)
        repaired += 1
    try:
        if ensure_database(paths["db"]):
            repaired += 1
        result = compact_experience(
            paths["db"],
            int(config["experience_limit_per_game"]),
            len(profile["actions"]),
            stop_event,
        )
        memory_result = compact_state_values(
            paths["db"],
            int(config["state_memory_limit_per_game"]),
            len(profile["actions"]),
            stop_event,
        )
        human_memory_result = compact_human_action_memory(
            paths["db"],
            HUMAN_ACTION_MEMORY_LIMIT,
            len(profile["actions"]),
            stop_event,
        )
        verification = verify_experience_database(
            paths["db"],
            len(profile["actions"]),
            int(config["database_integrity_scan_limit"]),
            stop_event,
        )
        removed += (
            result["removed"]
            + memory_result["removed"]
            + human_memory_result["removed"]
            + verification["removed"]
        )
        if verification["removed"]:
            result = compact_experience(
                paths["db"],
                int(config["experience_limit_per_game"]),
                len(profile["actions"]),
                stop_event,
            )
            removed += result["removed"]
    except RuntimeError as error:
        if str(error) == "操作已取消":
            raise
        log_text(f"经验数据库修复 {profile_id} 失败，将隔离重建：\n" + traceback.format_exc())
        for database_file in (paths["db"], Path(str(paths["db"]) + "-wal"), Path(str(paths["db"]) + "-shm")):
            backup_corrupt(database_file)
        remove_sqlite_sidecars(paths["db"])
        ensure_database(paths["db"])
        repaired += 1
        result = {"records": 0, "removed": 0}
        memory_result = {"records": 0, "removed": 0}
        human_memory_result = {"records": 0, "removed": 0}
    except Exception:
        log_text(f"经验数据库修复 {profile_id} 失败，将隔离重建：\n" + traceback.format_exc())
        for database_file in (paths["db"], Path(str(paths["db"]) + "-wal"), Path(str(paths["db"]) + "-shm")):
            backup_corrupt(database_file)
        remove_sqlite_sidecars(paths["db"])
        ensure_database(paths["db"])
        repaired += 1
        result = {"records": 0, "removed": 0}
        memory_result = {"records": 0, "removed": 0}
        human_memory_result = {"records": 0, "removed": 0}
    try:
        if validate_model_file(paths["model"], profile, config):
            repaired += 1
    except Exception:
        backup_corrupt(paths["model"])
        np = import_numpy()
        model = initialize_model(
            np,
            MODEL_INPUT_DIM,
            int(config["hidden_size"]),
            len(profile["actions"]),
        )
        model["action_hash"] = actions_hash(profile["actions"])
        model["action_signatures"] = [action_signature(action) for action in profile["actions"]]
        save_model(np, paths["model"], model)
        repaired += 1
    return {
        "repaired": repaired,
        "removed": removed,
        "records": result["records"],
        "memory_records": memory_result["records"],
        "human_memory_records": human_memory_result["records"],
    }


def ensure_files(stop_event: threading.Event | None) -> dict:
    raise_if_cancelled(stop_event)
    ensure_app_storage_writable()
    repaired = 0
    downloaded = 0
    removed = 0
    records = 0
    memory_records = 0
    human_memory_records = 0
    restart_required = False
    removed += cleanup_temporary_files(stop_event)
    raise_if_cancelled(stop_event)
    main_repaired, main_restart = repair_main_script()
    repaired += main_repaired
    restart_required = restart_required or main_restart
    raise_if_cancelled(stop_event)
    config = load_config()
    index = load_index()
    profile_ids = set(index.get("profiles", {}))
    for directory in PROFILES_DIR.iterdir():
        if path_is_unsafe_managed_entry(directory):
            if valid_profile_id(directory.name):
                remove_unsafe_managed_entry(directory)
                repaired += 1
            continue
        if not directory.is_dir() or not valid_profile_id(directory.name):
            continue
        profile_ids.add(directory.name)
    raise_if_cancelled(stop_event)
    if ensure_numpy(download=True, stop_event=stop_event):
        downloaded += 1
    raise_if_cancelled(stop_event)
    np = import_numpy()
    runtime_self_check(np)
    prior_existed = GLOBAL_PRIOR_PATH.exists()
    if prior_existed and load_global_prior(np) is None:
        repaired += 1
    for profile_id in sorted(profile_ids):
        raise_if_cancelled(stop_event)
        result = repair_profile(profile_id, config, stop_event)
        repaired += result["repaired"]
        removed += result["removed"]
        records += result["records"]
        memory_records += result["memory_records"]
        human_memory_records += result["human_memory_records"]
    raise_if_cancelled(stop_event)
    _, index_changed = sync_profile_index(index)
    repaired += index_changed
    validate_managed_storage_layout()
    verify_runtime_integrity_baseline_fast(SITE_PACKAGES)
    verify_main_script_integrity(LOCAL_SCRIPT_PATH)
    return {
        "repaired": repaired,
        "downloaded": downloaded,
        "removed": removed,
        "records": records,
        "memory_records": memory_records,
        "human_memory_records": human_memory_records,
        "restart_required": restart_required,
    }


def human_demonstration_reward(idle: bool) -> float:
    return 0.08 if idle else 0.90


def human_observed_effect_reward(idle: bool, observed_effect: float) -> float:
    if idle:
        return 0.08
    effect = max(0.0, min(1.0, float(observed_effect)))
    return min(1.0, 0.72 + effect * 0.28)


def record_human_session(target: int, stop_event: threading.Event) -> str:
    config, _ = ensure_core_ready(stop_event)
    identity = profile_identity(target)
    profile, paths = load_or_create_profile(identity)
    ensure_action_metadata(profile)
    runtime_settings = adaptive_runtime_settings(config)
    interval = max(0.04, min(0.25, float(runtime_settings["sample_interval_seconds"])))
    reacquire_seconds = max(0.0, min(15.0, float(config["target_reacquire_seconds"])))
    max_actions = max(8, int(config["max_action_count"]))
    state_memory_limit = max(1000, int(config["state_memory_limit_per_game"]))
    state_memory = load_state_value_memory(
        paths["db"],
        len(profile["actions"]),
        state_memory_limit,
    )
    dirty_state_values: set[tuple[str, int]] = set()
    human_action_memory = load_human_action_memory(
        paths["db"],
        len(profile["actions"]),
        HUMAN_ACTION_MEMORY_LIMIT,
    )
    dirty_human_actions: set[tuple[str, int]] = set()
    sampler = ScreenSampler(target)
    wheel_monitor = MouseWheelMonitor()
    wheel_monitor.start()
    previous_frame = None
    previous_raw_frame = None
    previous_raw_chroma_blue = None
    previous_raw_chroma_red = None
    previous_cursor = cursor_position()
    rows = []
    recorded = 0
    captured = 0
    idle_streak = 0
    new_actions = 0
    black_frames = 0
    last_action_index: int | None = None
    previous_previous_action: int | None = None
    last_recorded_action: int | None = None
    last_recorded_digest = ""
    duplicate_streak = 0
    previous_effect_action_index: int | None = None
    previous_effect_scene_context = "mixed_scene"
    previous_effect_idle = True
    action_started = time.monotonic()
    try:
        while not stop_event.is_set():
            if esc_pressed():
                break
            replacement = foreground_replacement_window(target, identity)
            if not window_exists(target):
                replacement = replacement or wait_for_replacement_window(
                    target,
                    identity,
                    stop_event,
                    reacquire_seconds,
                )
                if not replacement:
                    break
            if replacement:
                if last_action_index is not None:
                    record_action_duration(profile, last_action_index, time.monotonic() - action_started)
                    last_action_index = None
                    previous_previous_action = None
                sampler.close()
                target = replacement
                sampler = ScreenSampler(target)
                wheel_monitor.clear()
                previous_frame = None
                previous_raw_frame = None
                previous_raw_chroma_blue = None
                previous_raw_chroma_red = None
                previous_cursor = cursor_position()
                previous_effect_action_index = None
                previous_effect_scene_context = "mixed_scene"
                previous_effect_idle = True
                action_started = time.monotonic()
                continue
            if foreground_window() != target:
                wheel_monitor.clear()
                time.sleep(0.08)
                previous_frame = None
                previous_raw_frame = None
                previous_raw_chroma_blue = None
                previous_raw_chroma_red = None
                previous_cursor = cursor_position()
                if last_action_index is not None:
                    record_action_duration(profile, last_action_index, time.monotonic() - action_started)
                    last_action_index = None
                    previous_previous_action = None
                previous_effect_action_index = None
                previous_effect_scene_context = "mixed_scene"
                previous_effect_idle = True
                action_started = time.monotonic()
                continue
            started = time.monotonic()
            action, previous_cursor = observe_human_action(
                target,
                previous_cursor,
                wheel_monitor.consume(),
            )
            current, current_chroma_blue, current_chroma_red = sampler.capture_frame()
            captured += 1
            black = frame_capture_failed(current, current_chroma_blue, current_chroma_red)
            if black:
                black_frames += 1
            scene_context_name, _ = infer_scene_context(current, previous_raw_frame, idle_streak)
            if previous_raw_frame is not None and not black:
                human_motion, human_changed_ratio, human_flicker = visual_change_metrics(previous_raw_frame, current)
                if previous_raw_chroma_blue is not None and previous_raw_chroma_red is not None:
                    human_color_motion, human_color_ratio = chroma_change_metrics(
                        previous_raw_chroma_blue,
                        previous_raw_chroma_red,
                        current_chroma_blue,
                        current_chroma_red,
                    )
                else:
                    human_color_motion = 0.0
                    human_color_ratio = 0.0
                human_effect = max(
                    0.0,
                    min(
                        1.0,
                        human_motion * 8.0
                        + human_changed_ratio * 1.2
                        + human_color_motion * 5.0
                        + human_color_ratio * 0.6
                        - human_flicker * 0.55,
                    ),
                )
            else:
                human_effect = 0.0
            if black:
                previous_raw_frame = None
                previous_raw_chroma_blue = None
                previous_raw_chroma_red = None
            else:
                previous_raw_frame = current
                previous_raw_chroma_blue = current_chroma_blue
                previous_raw_chroma_red = current_chroma_red
            model_frame = cursor_aware_frame(target, current)
            feature = make_feature(
                model_frame,
                previous_frame if not black else None,
                current_chroma_blue,
                current_chroma_red,
            )
            current_memory_state = memory_state_key(current, feature)
            previous_frame = model_frame if not black else None
            action_index, added = register_action(profile, action, max_actions, origin="human")
            if added:
                new_actions += 1
                profile["needs_training"] = True
                save_profile(profile, paths)
            if last_action_index is None:
                last_action_index = action_index
                action_started = started
            elif action_index != last_action_index:
                record_action_duration(profile, last_action_index, started - action_started)
                record_transition(profile, last_action_index, action_index, previous_previous_action)
                previous_previous_action = last_action_index
                last_action_index = action_index
                action_started = started
            idle = (
                not action["keys"]
                and not action["buttons"]
                and not action["mouse_dx"]
                and not action["mouse_dy"]
                and not action["mouse_wheel"]
            )
            if idle and feature_motion(feature) < 0.004:
                idle_streak += 1
            else:
                idle_streak = 0
            demonstration_reward = human_demonstration_reward(idle)
            if not black:
                if previous_effect_action_index is not None:
                    observed_reward = human_observed_effect_reward(
                        previous_effect_idle,
                        human_effect,
                    )
                    update_action_reward(profile, previous_effect_action_index, observed_reward)
                    update_action_effect(profile, previous_effect_action_index, human_effect)
                    update_control_response(profile, previous_effect_action_index, observed_reward)
                    update_scene_control_response(
                        profile,
                        previous_effect_scene_context,
                        previous_effect_action_index,
                        observed_reward,
                    )
                    update_scene_action_response(
                        profile,
                        previous_effect_scene_context,
                        previous_effect_action_index,
                        observed_reward,
                    )
                memory_key = (current_memory_state, action_index)
                update_state_value_memory(state_memory, memory_key, 0.18 if idle else 0.88, 0.30)
                dirty_state_values.add(memory_key)
                if len(dirty_state_values) >= 256:
                    save_state_value_memory(paths["db"], state_memory, dirty_state_values)
                previous_effect_action_index = action_index
                previous_effect_scene_context = scene_context_name
                previous_effect_idle = idle
            else:
                previous_effect_action_index = None
                previous_effect_scene_context = "mixed_scene"
                previous_effect_idle = True
            digest = frame_hash(current, current_chroma_blue, current_chroma_red)
            near_duplicate = (
                last_recorded_action == action_index
                and bool(last_recorded_digest)
                and frame_hash_distance(digest, last_recorded_digest) <= 1
                and feature_motion(feature) < 0.006
            )
            duplicate_streak = duplicate_streak + 1 if near_duplicate else 0
            keep_sample = (
                (idle_streak <= 2 or idle_streak % 6 == 0)
                and not black
                and (not near_duplicate or duplicate_streak % 5 == 0)
            )
            if keep_sample:
                human_memory_key = (current_memory_state, action_index)
                update_human_action_memory(human_action_memory, human_memory_key)
                dirty_human_actions.add(human_memory_key)
                if len(dirty_human_actions) >= 256:
                    save_human_action_memory(
                        paths["db"],
                        human_action_memory,
                        dirty_human_actions,
                    )
                rows.append(
                    (
                        now_text(),
                        "human",
                        action_index,
                        demonstration_reward,
                        FEATURE_DIM,
                        compress_feature(feature),
                    )
                )
                recorded += 1
                last_recorded_action = action_index
                last_recorded_digest = digest
                profile["needs_training"] = True
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
            delay = interval - (time.monotonic() - started)
            if delay > 0 and not sleep_cancelable(delay, stop_event):
                break
    finally:
        if last_action_index is not None:
            record_action_duration(profile, last_action_index, time.monotonic() - action_started)
        if rows:
            insert_samples(paths["db"], rows)
        save_state_value_memory(paths["db"], state_memory, dirty_state_values)
        save_human_action_memory(paths["db"], human_action_memory, dirty_human_actions)
        wheel_monitor.stop()
        sampler.close()
        profile["human_sessions"] = int(profile.get("human_sessions", 0)) + int(recorded > 0)
        save_profile(profile, paths)
        compact_experience(paths["db"], int(config["experience_limit_per_game"]), len(profile["actions"]))
        compact_state_values(paths["db"], state_memory_limit, len(profile["actions"]))
        compact_human_action_memory(
            paths["db"],
            HUMAN_ACTION_MEMORY_LIMIT,
            len(profile["actions"]),
        )
        wait_esc_release()
    warning = "；画面可能未被正确采集" if black_frames > max(20, captured // 2) else ""
    return f"人玩结束：{profile['name']}；记录 {recorded} 条；新增动作 {new_actions} 个{warning}"


def train_all_profiles(stop_event: threading.Event) -> str:
    np = ensure_runtime_ready(stop_event)
    config = load_config()
    training_settings = adaptive_training_settings(config)
    index, _ = sync_profile_index(load_index())
    if not index.get("profiles"):
        return "没有可升级的游戏；请先使用“人”或“AI”模式积累经验"
    summaries = []
    total_profiles = 0
    total_samples = 0
    total_removed = 0
    for profile_id in list(index["profiles"]):
        if stop_event.is_set():
            break
        paths = profile_paths(profile_id)
        x = None
        try:
            health = repair_profile(profile_id, config, stop_event)
            total_removed += int(health.get("removed", 0))
            candidate = read_json_file(paths["profile"], MAX_PROFILE_JSON_BYTES)
            profile = migrate_profile(candidate, profile_id)
            if profile is None:
                raise ValueError("档案损坏")
            if profile != candidate:
                atomic_write_json(paths["profile"], profile)
            pool = compact_experience(
                paths["db"],
                int(config["experience_limit_per_game"]),
                len(profile["actions"]),
                stop_event,
            )
            memory_pool = compact_state_values(
                paths["db"],
                int(config["state_memory_limit_per_game"]),
                len(profile["actions"]),
                stop_event,
            )
            total_removed += int(pool.get("removed", 0)) + int(memory_pool.get("removed", 0))
            if not bool(profile.get("needs_training", True)) and paths["model"].is_file():
                summaries.append(f"{profile['name']}：模型已是最新")
                continue
            if pool["human"] < 8 and pool["records"] < 32:
                summaries.append(f"{profile['name']}：经验不足")
                continue
            model, _ = load_model(
                np,
                paths["model"],
                MODEL_INPUT_DIM,
                int(config["hidden_size"]),
                len(profile["actions"]),
                profile["actions"],
            )
            apply_global_prior(np, model, profile["actions"])
            x, y, policy_weights, value_targets, value_weights, invalid = load_training_data(
                np,
                paths["db"],
                len(profile["actions"]),
                int(training_settings["sample_limit"]),
                stop_event,
            )
            if x is None:
                summaries.append(f"{profile['name']}：无有效经验")
                continue
            metrics = train_model(
                np,
                model,
                x,
                y,
                policy_weights,
                value_targets,
                value_weights,
                int(training_settings["epochs"]),
                int(training_settings["batch_size"]),
                float(config["learning_rate"]),
                stop_event,
            )
            model["action_hash"] = actions_hash(profile["actions"])
            save_model(np, paths["model"], model)
            profile["trained_samples"] = int(profile.get("trained_samples", 0)) + metrics["samples"]
            profile["training_rounds"] = int(profile.get("training_rounds", 0)) + 1
            profile["needs_training"] = False
            save_profile(profile, paths)
            total_profiles += 1
            total_samples += metrics["samples"]
            summaries.append(
                f"{profile['name']}：{metrics['samples']}条，动作准确率{metrics['accuracy']:.0%}，价值误差{metrics['value_mae']:.2f}"
            )
            if invalid:
                log_text(f"{profile_id} 训练时忽略损坏经验 {invalid} 条")
        except RuntimeError as error:
            if str(error) == "操作已取消":
                raise
            log_text(f"训练 {profile_id} 失败:\n" + traceback.format_exc())
            summaries.append(f"{profile_id}：失败")
        except Exception:
            log_text(f"训练 {profile_id} 失败:\n" + traceback.format_exc())
            summaries.append(f"{profile_id}：失败")
        finally:
            release_training_matrix(x)
    if stop_event.is_set():
        return "升级已取消"
    prior_updated = refresh_global_prior(np, index, config, stop_event)
    detail = "；".join(summaries[:4])
    if len(summaries) > 4:
        detail += f"；另有 {len(summaries) - 4} 个游戏"
    prior_text = "；已更新跨游戏通用先验" if prior_updated else ""
    pool_text = f"；整理经验池 {total_removed} 条" if total_removed else ""
    return f"升级完成：{total_profiles} 个游戏，训练 {total_samples} 条{pool_text}{prior_text}。{detail}"


def run_ai_session(target: int, stop_event: threading.Event) -> str:
    np = ensure_runtime_ready(stop_event)
    config = load_config()
    identity = profile_identity(target)
    target_executable_name = Path(str(identity.get("executable", ""))).stem.lower()
    profile, paths = load_or_create_profile(identity)
    ensure_action_metadata(profile)
    prior = load_global_prior(np)
    transferred_actions = merge_prior_actions(
        profile,
        prior,
        max(8, int(config["max_action_count"])),
        max(0, int(config["transfer_action_limit"])),
    )
    if transferred_actions:
        ensure_action_metadata(profile)
        save_profile(profile, paths)
    action_origins = profile.get("action_origins", [])
    target_blocked_actions = {
        action_index
        for action_index, action in enumerate(profile["actions"])
        if target_action_blocked(
            action,
            str(action_origins[action_index]) if action_index < len(action_origins) else "generic",
            target_executable_name,
        )
    }
    state_memory_limit = max(1000, int(config["state_memory_limit_per_game"]))
    persistent_state_values = load_state_value_memory(
        paths["db"],
        len(profile["actions"]),
        state_memory_limit,
    )
    human_action_memory = load_human_action_memory(
        paths["db"],
        len(profile["actions"]),
        HUMAN_ACTION_MEMORY_LIMIT,
    )
    human_action_memory_index = build_human_action_memory_index(human_action_memory)
    dirty_state_values: set[tuple[str, int]] = set()
    state_memory_index = build_state_memory_index(persistent_state_values)
    state_visit_totals = build_state_visit_totals(persistent_state_values)
    total, human = count_samples(paths["db"])
    local_control_preferences = learned_control_preferences(profile, paths["db"])
    cross_game_control_prior = load_cross_game_control_prior(profile["id"])
    cross_game_scene_prior = load_cross_game_scene_control_prior(profile["id"])
    cross_game_action_prior = load_cross_game_scene_action_prior(profile["id"])
    cross_game_action_vectors = {
        context: cross_game_scene_action_values(cross_game_action_prior, context, profile["actions"])
        for context in SCENE_CONTEXTS
    }
    control_preferences = blend_control_preferences(
        local_control_preferences,
        cross_game_control_prior,
        human,
        float(config["cross_game_control_weight"]),
    )
    model_exists = paths["model"].is_file()
    if model_exists:
        model, changed = load_model(
            np,
            paths["model"],
            MODEL_INPUT_DIM,
            int(config["hidden_size"]),
            len(profile["actions"]),
            profile["actions"],
        )
        transferred_model = apply_global_prior(np, model, profile["actions"])
        if (transferred_actions or changed) and apply_global_action_heads(
            np,
            model,
            profile["actions"],
            profile.get("action_origins", []),
            prior,
        ):
            changed = True
    else:
        model = model_from_global_prior(np, prior, profile["actions"], int(config["hidden_size"]))
        changed = True
        transferred_model = prior is not None and int(model.get("training_rounds", 0)) > 0
    if changed or transferred_model or not model_exists:
        save_model(np, paths["model"], model)
    target_model = clone_target_model(np, model)
    cold_start = int(model.get("training_rounds", 0)) <= 0 and not transferred_model
    if cold_start:
        mode_text = "通用探索"
    elif human < 8:
        mode_text = "跨游戏迁移"
    else:
        mode_text = "游戏模型"
    probe_actions = cold_start_probe_actions(profile, control_preferences)
    probe_limit = min(len(probe_actions), 24 if cold_start else (12 if human < 8 else 0))
    probe_actions = probe_actions[:probe_limit]
    sampler = ScreenSampler(target)
    previous_frame = None
    previous_raw_frame = None
    previous_raw_chroma_blue = None
    previous_raw_chroma_red = None
    state_visits: dict[str, int] = {}
    state_action_visits: dict[tuple[str, int], int] = {}
    state_action_values: dict[tuple[str, int], tuple[float, int]] = {}
    edge_visits: dict[tuple[str, int, str], int] = {}
    recent_frame_hashes: list[str] = []
    recent_state_keys: list[str] = []
    recent_actions: list[int] = []
    action_block_until: dict[int, int] = {}
    pending_experiences: list[dict] = []
    rows = []
    steps = 0
    reward_sum = 0.0
    recent_reward_ema = 0.0
    recent_reward_observations = 0
    black_frames = 0
    black_streak = 0
    static_streak = 0
    passive_motion_ema = max(0.0, min(1.0, float(profile.get("passive_motion_ema", 0.0))))
    passive_change_ema = max(0.0, min(1.0, float(profile.get("passive_change_ema", 0.0))))
    passive_color_ema = max(0.0, min(1.0, float(profile.get("passive_color_ema", 0.0))))
    smoothed_probabilities = None
    smoothed_values = None
    base_exploration = max(0.0, min(0.45, float(config["exploration"])))
    zero_shot_exploration = max(0.0, min(0.75, float(config["zero_shot_exploration"])))
    historical_reward = float(profile.get("ai_reward_ema", 0.0))
    reward_adjustment = max(-0.04, min(0.12, (0.12 - historical_reward) * 0.20))
    exploration = max(0.0, min(0.65, base_exploration + reward_adjustment))
    if cold_start:
        exploration = max(exploration, zero_shot_exploration)
    elif human < 8:
        exploration = max(exploration, zero_shot_exploration * 0.55)
    runtime_settings = adaptive_runtime_settings(config)
    configured_hold = float(config["action_hold_seconds"])
    pause = max(0.0, min(0.5, float(runtime_settings["step_pause_seconds"])))
    reacquire_seconds = max(0.0, min(15.0, float(config["target_reacquire_seconds"])))
    mouse_step = max(1, min(200, int(config["mouse_step_pixels"])))
    delayed_horizon = max(1, min(24, int(config["delayed_reward_horizon"])))
    delayed_discount = max(0.1, min(0.99, float(config["delayed_reward_discount"])))
    online_state_value_weight = max(0.0, min(1.0, float(config["online_state_value_weight"])))
    state_memory_weight = max(0.0, min(1.0, float(config["state_memory_weight"])))
    approximate_state_memory_weight = max(0.0, min(1.0, float(config["approximate_state_memory_weight"])))
    online_learning_rate = max(0.01, min(1.0, float(config["online_learning_rate"])))
    online_model_learning_rate = max(0.0, min(0.02, float(config["online_model_learning_rate"])))
    online_td_discount = max(0.0, min(0.95, float(config["online_td_discount"])))
    target_network_sync_steps = max(
        16,
        min(4096, int(config["target_network_sync_steps"])),
    )
    target_network_soft_update = max(
        0.01,
        min(1.0, float(config["target_network_soft_update"])),
    )
    target_ensemble_weight = max(
        0.0,
        min(0.5, float(config["target_ensemble_weight"])),
    )
    model_uncertainty_weight = max(
        0.0,
        min(0.5, float(config["model_uncertainty_weight"])),
    )
    stuck_recovery_threshold = max(3, min(30, int(config["stuck_recovery_threshold"])))
    transition_novelty_weight = max(0.0, min(1.0, float(config["transition_novelty_weight"])))
    action_effect_weight = max(0.0, min(1.0, float(config["action_effect_weight"])))
    action_risk_weight = max(0.0, min(1.0, float(config["action_risk_weight"])))
    failure_cooldown_steps = max(0, min(60, int(config["failure_cooldown_steps"])))
    world_progress_weight = max(0.0, min(1.0, float(config["world_progress_weight"])))
    cycle_penalty_weight = max(0.0, min(1.0, float(config["cycle_penalty_weight"])))
    confirmation_delay = max(
        0.0,
        min(0.25, float(runtime_settings["confirmation_delay_seconds"])),
    )
    online_checkpoint_steps = max(
        32,
        min(10000, int(runtime_settings["online_checkpoint_steps"])),
    )
    sequence_prior_weight = max(0.0, min(1.0, float(config["sequence_prior_weight"])))
    planning_horizon = max(1, min(6, int(runtime_settings["planning_horizon"])))
    planning_discount = max(0.1, min(0.95, float(config["planning_discount"])))
    planning_weight = max(0.0, min(1.0, float(config["planning_weight"])))
    planning_refresh_steps = max(
        8,
        min(512, int(runtime_settings["planning_refresh_steps"])),
    )
    cross_game_scene_weight = max(0.0, min(1.0, float(config["cross_game_scene_weight"])))
    cross_game_action_weight = max(0.0, min(1.0, float(config["cross_game_action_weight"])))
    scene_action_memory_weight = max(0.0, min(1.0, float(config["scene_action_memory_weight"])))
    contextual_probe_weight = max(0.0, min(1.0, float(config["contextual_probe_weight"])))
    persistent_novelty_weight = max(0.0, min(1.0, float(config["persistent_novelty_weight"])))
    successful_transition_threshold = max(-1.0, min(1.0, float(config["successful_transition_threshold"])))
    adaptive_hold_strength = max(0.0, min(1.0, float(config["adaptive_hold_strength"])))
    spatial_progress_weight = max(0.0, min(1.0, float(config["spatial_progress_weight"])))
    translation_search_radius = max(
        1,
        min(4, int(runtime_settings["translation_search_radius"])),
    )
    action_diversity_weight = max(0.0, min(1.0, float(config["action_diversity_weight"])))
    fade_penalty_weight = max(0.0, min(1.0, float(config["fade_penalty_weight"])))
    scene_strategy_weight = max(0.0, min(1.0, float(config["scene_strategy_weight"])))
    color_progress_weight = max(0.0, min(1.0, float(config["color_progress_weight"])))
    persistent_frontier_reward_weight = max(
        0.0,
        min(1.0, float(config["persistent_frontier_reward_weight"])),
    )
    state_bootstrap_weight = max(0.0, min(0.75, float(config["state_bootstrap_weight"])))
    capture_failure_timeout = max(
        10.0,
        min(300.0, float(config["capture_failure_timeout_seconds"])),
    )
    planning_values = sequence_plan_values(
        np,
        profile,
        len(profile["actions"]),
        planning_horizon,
        planning_discount,
    )
    online_model_changed = False
    black_started_at: float | None = None
    try:
        while not stop_event.is_set():
            if esc_pressed():
                break
            replacement = foreground_replacement_window(target, identity)
            if not window_exists(target):
                replacement = replacement or wait_for_replacement_window(
                    target,
                    identity,
                    stop_event,
                    reacquire_seconds,
                )
                if not replacement:
                    break
            if replacement:
                release_all_inputs()
                flush_delayed_experience(profile, pending_experiences, rows)
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
                save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
                sampler.close()
                target = replacement
                sampler = ScreenSampler(target)
                previous_frame = None
                previous_raw_frame = None
                previous_raw_chroma_blue = None
                previous_raw_chroma_red = None
                black_streak = 0
                black_started_at = None
                static_streak = 0
                recent_actions.clear()
                recent_frame_hashes.clear()
                recent_state_keys.clear()
                state_action_visits.clear()
                state_action_values.clear()
                edge_visits.clear()
                smoothed_probabilities = None
                smoothed_values = None
                continue
            if foreground_window() != target:
                release_all_inputs()
                flush_delayed_experience(profile, pending_experiences, rows)
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
                save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
                previous_frame = None
                previous_raw_frame = None
                previous_raw_chroma_blue = None
                previous_raw_chroma_red = None
                black_streak = 0
                black_started_at = None
                static_streak = 0
                recent_actions.clear()
                recent_frame_hashes.clear()
                recent_state_keys.clear()
                state_action_visits.clear()
                state_action_values.clear()
                edge_visits.clear()
                smoothed_probabilities = None
                smoothed_values = None
                time.sleep(0.08)
                continue
            current, current_chroma_blue, current_chroma_red = sampler.capture_frame()
            black = frame_capture_failed(current, current_chroma_blue, current_chroma_red)
            if black:
                black_frames += 1
                black_streak += 1
                if black_started_at is None:
                    black_started_at = time.monotonic()
                release_all_inputs()
                flush_delayed_experience(profile, pending_experiences, rows)
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
                save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
                previous_frame = None
                previous_raw_frame = None
                previous_raw_chroma_blue = None
                previous_raw_chroma_red = None
                if black_streak % 25 == 0 and window_exists(target) and foreground_window() == target:
                    sampler.close()
                    sampler = ScreenSampler(target)
                time.sleep(0.08)
                if time.monotonic() - black_started_at >= capture_failure_timeout:
                    break
                continue
            black_streak = 0
            black_started_at = None
            model_frame = cursor_aware_frame(target, current)
            feature = make_feature(
                model_frame,
                previous_frame,
                current_chroma_blue,
                current_chroma_red,
            )
            visual_target_biases = visual_action_target_biases(current, previous_raw_frame, profile["actions"])
            if previous_raw_chroma_blue is not None and previous_raw_chroma_red is not None:
                scene_color_motion, _ = chroma_change_metrics(
                    previous_raw_chroma_blue,
                    previous_raw_chroma_red,
                    current_chroma_blue,
                    current_chroma_red,
                )
            else:
                scene_color_motion = 0.0
            scene_context_name, scene_heuristic_biases = infer_scene_context(
                current,
                previous_raw_frame,
                static_streak,
            )
            scene_learned_biases = blended_scene_control_evidence(
                profile,
                scene_context_name,
                cross_game_scene_prior,
                cross_game_scene_weight,
            )
            scene_combined_biases = {
                kind: float(scene_heuristic_biases.get(kind, 0.0))
                + 0.85 * float(scene_learned_biases.get(kind, 0.0))
                for kind in CONTROL_KINDS
            }
            local_scene_action_values = scene_action_response_evidence(profile, scene_context_name)
            transferred_scene_action_values = cross_game_action_vectors.get(
                scene_context_name,
                [0.0] * len(profile["actions"]),
            )
            cross_game_action_scale = max(
                0.18,
                1.0 - min(0.82, math.log1p(max(0, human)) / math.log(257.0)),
            )
            previous_frame = model_frame
            previous_raw_frame = current
            previous_raw_chroma_blue = current_chroma_blue
            previous_raw_chroma_red = current_chroma_red
            current_state_key = state_key(current, feature)
            current_memory_state = memory_state_key(current, feature)
            probabilities, values, model_uncertainty, model_disagreement = model_ensemble_outputs(
                np,
                model,
                target_model,
                feature,
                target_ensemble_weight,
            )
            if cold_start and len(probabilities) > 1:
                probabilities = probabilities * 0.25 + (0.75 / len(probabilities))
                probabilities /= max(1e-12, float(probabilities.sum()))
            scene_motion = feature_motion(feature)
            smoothed_probabilities, smoothed_values, policy_drift = temporal_policy_blend(
                np,
                probabilities,
                values,
                smoothed_probabilities,
                smoothed_values,
                scene_motion,
                static_streak,
            )
            reward_prior = np.asarray(profile["action_reward_ema"], dtype=np.float64)
            reward_counts = np.asarray(profile["action_reward_counts"], dtype=np.float64)
            effect_prior = np.asarray(profile["action_effect_ema"], dtype=np.float64)
            effect_counts = np.asarray(profile["action_effect_counts"], dtype=np.float64)
            risk_prior = np.asarray(profile["action_risk_ema"], dtype=np.float64)
            risk_counts = np.asarray(profile["action_risk_counts"], dtype=np.float64)
            control_response = control_response_evidence(profile)
            approximate_memory_values = approximate_state_action_values(
                state_memory_index,
                current_memory_state,
                len(profile["actions"]),
            )
            human_memory_biases = human_action_memory_biases(
                human_action_memory,
                human_action_memory_index,
                current_memory_state,
                len(profile["actions"]),
            )
            persistent_state_visits = min(
                1_000_000_000,
                int(state_visit_totals.get(current_memory_state, 0)),
            )
            persistent_state_familiarity = min(
                1.0,
                math.log1p(persistent_state_visits) / math.log(1025.0),
            )
            if steps and steps % planning_refresh_steps == 0:
                planning_values = sequence_plan_values(
                    np,
                    profile,
                    len(profile["actions"]),
                    planning_horizon,
                    planning_discount,
                )
            policy_values = np.asarray(smoothed_values, dtype=np.float64).copy()
            if len(reward_prior) == len(policy_values):
                reward_guidance, effect_guidance, risk_guidance, uncertainty_bonus = empirical_action_guidance(
                    np,
                    reward_prior,
                    reward_counts,
                    effect_prior,
                    effect_counts,
                    risk_prior,
                    risk_counts,
                    cold_start,
                )
                adaptive_bias = np.zeros(len(policy_values), dtype=np.float64)
                origins = profile.get("action_origins", [])
                recent_kind_counts: dict[str, int] = {}
                for recent_action in recent_actions[-10:]:
                    if 0 <= recent_action < len(profile["actions"]):
                        recent_kind = action_kind(profile["actions"][recent_action])
                        recent_kind_counts[recent_kind] = recent_kind_counts.get(recent_kind, 0) + 1
                recent_kind_total = sum(recent_kind_counts.values())
                for action_position, action in enumerate(profile["actions"]):
                    origin = origins[action_position] if action_position < len(origins) else "human"
                    adaptive_bias[action_position] = action_policy_bias(
                        action,
                        origin,
                        cold_start,
                        static_streak,
                        scene_motion,
                        steps,
                        control_preferences,
                    )
                    current_kind = action_kind(action)
                    adaptive_bias[action_position] += 0.24 * float(control_response.get(current_kind, 0.0))
                    adaptive_bias[action_position] += scene_strategy_weight * float(
                        scene_combined_biases.get(current_kind, 0.0)
                    )
                    if action_position < len(local_scene_action_values):
                        adaptive_bias[action_position] += (
                            scene_action_memory_weight * float(local_scene_action_values[action_position])
                        )
                    if action_position < len(transferred_scene_action_values):
                        adaptive_bias[action_position] += (
                            cross_game_action_weight
                            * cross_game_action_scale
                            * float(transferred_scene_action_values[action_position])
                        )
                    if recent_kind_total >= 4 and current_kind != "idle":
                        kind_frequency = recent_kind_counts.get(current_kind, 0) / recent_kind_total
                        adaptive_bias[action_position] -= action_diversity_weight * max(0.0, kind_frequency - 0.34)
                        if static_streak >= 3 and current_kind not in recent_kind_counts:
                            adaptive_bias[action_position] += action_diversity_weight * 0.22
                    if action_position < len(visual_target_biases) and action["mouse_x"] >= 0:
                        adaptive_bias[action_position] += (0.34 if cold_start else 0.20) * visual_target_biases[action_position]
                    adaptive_bias[action_position] -= action_safety_penalty(
                        action,
                        origin,
                        target_executable_name,
                        static_streak,
                    )
                    state_action_key = (current_state_key, action_position)
                    visits = state_action_visits.get(state_action_key, 0)
                    if visits:
                        adaptive_bias[action_position] -= min(0.60, 0.12 * math.log2(visits + 1.0))
                    online_value, online_count = state_action_values.get(state_action_key, (0.0, 0))
                    adaptive_bias[action_position] += online_state_value_weight * float(online_value)
                    memory_value, memory_count = persistent_state_values.get(
                        (current_memory_state, action_position),
                        (0.0, 0),
                    )
                    memory_confidence = min(1.0, math.log1p(int(memory_count)) / math.log(17.0))
                    adaptive_bias[action_position] += state_memory_weight * float(memory_value) * memory_confidence
                    persistent_bonus = (
                        persistent_novelty_weight
                        * (0.45 + 0.55 * persistent_state_familiarity)
                        / math.sqrt(int(memory_count) + 1.0)
                    )
                    adaptive_bias[action_position] += persistent_bonus * (0.18 if action_position == 0 else 1.0)
                    approximate_value, approximate_confidence = approximate_memory_values.get(action_position, (0.0, 0.0))
                    adaptive_bias[action_position] += (
                        approximate_state_memory_weight
                        * float(approximate_value)
                        * float(approximate_confidence)
                    )
                    if action_position < len(human_memory_biases):
                        adaptive_bias[action_position] += (
                            HUMAN_ACTION_MEMORY_WEIGHT
                            * float(human_memory_biases[action_position])
                        )
                    if action_position != 0:
                        adaptive_bias[action_position] += 0.035 / math.sqrt(int(online_count) + 1.0)
                        if memory_count <= 0:
                            adaptive_bias[action_position] += 0.018
                policy_values = np.clip(
                    policy_values
                    + 0.34 * reward_guidance
                    + action_effect_weight * effect_guidance
                    - action_risk_weight * risk_guidance
                    + uncertainty_bonus
                    + adaptive_bias
                    + planning_weight * planning_values,
                    -1.0,
                    1.0,
                )
            uncertainty_direction = 0.55 - persistent_state_familiarity
            policy_values = np.clip(
                policy_values
                + model_uncertainty_weight * uncertainty_direction * model_uncertainty,
                -1.0,
                1.0,
            )
            confidence = calibrated_policy_confidence(
                np,
                smoothed_probabilities,
                policy_values,
            )
            confidence *= 1.0 - min(0.55, model_disagreement * 0.65)
            exploration_drift = max(
                policy_drift,
                min(1.0, model_disagreement * 1.35),
            )
            adaptive_exploration = adaptive_exploration_rate(
                exploration,
                confidence,
                persistent_state_familiarity,
                exploration_drift,
                recent_reward_ema,
                recent_reward_observations,
            )
            previous_action = recent_actions[-1] if recent_actions else None
            previous_previous_action = recent_actions[-2] if len(recent_actions) >= 2 else None
            transition_prior = transition_distribution(
                np,
                profile,
                previous_action,
                len(profile["actions"]),
                previous_previous_action,
                sequence_prior_weight,
            )
            blocked_actions = set(target_blocked_actions)
            blocked_actions.update(index for index, until in action_block_until.items() if steps < until)
            if action_block_until:
                action_block_until = {index: until for index, until in action_block_until.items() if steps < until}
            probe_action_index: int | None = None
            probe_due = bool(probe_actions) and (steps < 6 or static_streak >= 4 or steps % 4 == 0)
            if probe_due:
                probe_action_index = choose_contextual_probe_action(
                    profile,
                    probe_actions,
                    blocked_actions,
                    state_action_visits,
                    current_state_key,
                    scene_combined_biases,
                    contextual_probe_weight,
                    steps,
                )
            recovery_action_index: int | None = None
            if probe_action_index is None and static_streak >= stuck_recovery_threshold:
                recovery_action_index = choose_recovery_action(
                    profile,
                    current_state_key,
                    state_action_visits,
                    recent_actions,
                    static_streak,
                    steps,
                    control_preferences,
                    control_response,
                    scene_combined_biases,
                )
                if recovery_action_index in blocked_actions:
                    recovery_action_index = None
            if probe_action_index is not None:
                action_index = probe_action_index
            elif recovery_action_index is not None:
                action_index = recovery_action_index
            else:
                action_index = choose_policy_action(
                    np,
                    smoothed_probabilities,
                    policy_values,
                    transition_prior,
                    adaptive_exploration,
                    recent_actions,
                    static_streak,
                    blocked_actions,
                )
            if action_index in target_blocked_actions:
                action_index = 0
            hold = adaptive_action_hold(
                profile,
                action_index,
                configured_hold,
                scene_motion,
                static_streak,
                adaptive_hold_strength,
            )
            if not execute_action(target, profile["actions"][action_index], hold, mouse_step, stop_event):
                if stop_event.is_set() or esc_pressed():
                    break
                continue
            if pause and not sleep_cancelable(pause, stop_event, target):
                if stop_event.is_set() or esc_pressed():
                    break
                continue
            immediate_frame, immediate_chroma_blue, immediate_chroma_red = sampler.capture_frame()
            immediate_black = frame_capture_failed(
                immediate_frame,
                immediate_chroma_blue,
                immediate_chroma_red,
            )
            next_frame = immediate_frame
            next_chroma_blue = immediate_chroma_blue
            next_chroma_red = immediate_chroma_red
            persistence = 1.0
            transient_change = 0.0
            if confirmation_delay > 0.0:
                confirmation_completed = sleep_cancelable(confirmation_delay, stop_event, target)
                if confirmation_completed:
                    settled_frame, settled_chroma_blue, settled_chroma_red = sampler.capture_frame()
                    settled_black = frame_capture_failed(
                        settled_frame,
                        settled_chroma_blue,
                        settled_chroma_red,
                    )
                    if not settled_black:
                        if not immediate_black:
                            gray_persistence, gray_transient = visual_persistence_metrics(
                                current,
                                immediate_frame,
                                settled_frame,
                            )
                            color_persistence, color_transient = chroma_persistence_metrics(
                                current_chroma_blue,
                                current_chroma_red,
                                immediate_chroma_blue,
                                immediate_chroma_red,
                                settled_chroma_blue,
                                settled_chroma_red,
                            )
                            persistence = max(gray_persistence, color_persistence)
                            transient_change = max(gray_transient, color_transient)
                        next_frame = settled_frame
                        next_chroma_blue = settled_chroma_blue
                        next_chroma_red = settled_chroma_red
                elif stop_event.is_set() or esc_pressed():
                    break
                else:
                    release_all_inputs()
                    previous_frame = None
                    previous_raw_frame = None
                    previous_raw_chroma_blue = None
                    previous_raw_chroma_red = None
                    continue
            next_black = frame_capture_failed(next_frame, next_chroma_blue, next_chroma_red)
            useful_motion, changed_ratio, flicker = visual_change_metrics(current, next_frame)
            color_motion, color_changed_ratio = chroma_change_metrics(
                current_chroma_blue,
                current_chroma_red,
                next_chroma_blue,
                next_chroma_red,
            )
            flicker = min(1.0, flicker + transient_change * 1.6)
            regional_activity, change_concentration, center_ratio, global_shift = regional_change_metrics(current, next_frame)
            world_change, hud_change, side_change = scene_progress_metrics(current, next_frame)
            translation_dx, translation_dy, translation_confidence = estimate_visual_translation(
                current,
                next_frame,
                translation_search_radius,
            )
            fade_score = uniform_brightness_change(current, next_frame)
            current_digest = frame_hash(current, current_chroma_blue, current_chroma_red)
            digest = frame_hash(next_frame, next_chroma_blue, next_chroma_red)
            hash_bits = max(len(current_digest), len(digest)) * 4
            scene_distance = frame_hash_distance(current_digest, digest) / max(1.0, float(hash_bits))
            next_model_frame = cursor_aware_frame(target, next_frame)
            next_feature = make_feature(
                next_model_frame,
                model_frame,
                next_chroma_blue,
                next_chroma_red,
            )
            next_state_key = state_key(next_frame, next_feature)
            next_memory_state = memory_state_key(next_frame, next_feature)
            visit_count = state_visits.get(next_state_key, 0)
            looped = recent_hash_match(digest, recent_frame_hashes[-64:], 3)
            cycle_score = visual_cycle_score(recent_frame_hashes, digest)
            edge_key = (current_state_key, action_index, next_state_key)
            edge_count = edge_visits.get(edge_key, 0)
            if (
                useful_motion < 0.0045
                and changed_ratio < 0.025
                and color_motion < 0.0035
                and color_changed_ratio < 0.025
            ):
                static_streak += 1
            else:
                static_streak = 0
            selected_kind = action_kind(profile["actions"][action_index])
            if selected_kind == "idle":
                passive_motion_ema = passive_motion_ema * 0.82 + useful_motion * 0.18
                passive_change_ema = passive_change_ema * 0.82 + changed_ratio * 0.18
                passive_color_ema = passive_color_ema * 0.82 + color_motion * 0.18
            else:
                passive_motion_ema = passive_motion_ema * 0.992 + min(scene_motion, useful_motion) * 0.008
                passive_change_ema = passive_change_ema * 0.995 + min(changed_ratio, max(0.02, passive_change_ema)) * 0.005
                passive_color_ema = passive_color_ema * 0.992 + min(scene_color_motion, color_motion) * 0.008
            passive_reference = max(scene_motion * 0.60, passive_motion_ema * 0.85)
            passive_change_reference = max(passive_change_ema * 0.85, min(0.12, scene_motion * 1.35))
            passive_color_reference = max(scene_color_motion * 0.60, passive_color_ema * 0.85)
            passive_motion = min(useful_motion, passive_reference)
            passive_color = min(color_motion, passive_color_reference)
            causal_motion = max(0.0, useful_motion - passive_reference)
            causal_change = max(0.0, changed_ratio - passive_change_reference)
            causal_color = max(0.0, color_motion - passive_color_reference)
            persistence_factor = 0.45 + 0.55 * persistence
            stable_causal_motion = causal_motion * persistence_factor
            stable_causal_change = causal_change * persistence_factor
            stable_causal_color = causal_color * persistence_factor
            translation_magnitude = min(1.0, math.hypot(translation_dx, translation_dy) / max(1.0, translation_search_radius))
            spatial_progress = translation_confidence * (0.40 + 0.60 * translation_magnitude)
            action_effect = min(
                1.0,
                stable_causal_motion * 10.0
                + stable_causal_change * 1.8
                + stable_causal_color * 6.0
                + max(0.0, change_concentration - 0.28) * regional_activity * 4.5 * persistence_factor
                + spatial_progress * 0.85,
            )
            if next_black:
                action_effect = 0.0
            update_action_effect(profile, action_index, action_effect)
            motion_reward = min(0.48, stable_causal_motion * 8.5)
            change_reward = min(0.16, stable_causal_change * 0.65) if stable_causal_motion >= 0.0012 else 0.0
            structured_reward = min(
                0.18,
                max(0.0, change_concentration - 0.28) * regional_activity * 7.0,
            )
            center_reward = min(0.08, max(0.0, center_ratio - 1.0) * causal_motion * 1.8)
            world_progress = max(0.0, world_change - hud_change * 0.35 - side_change * 0.10)
            world_progress_reward = min(world_progress_weight, world_progress * 2.4 * persistence_factor)
            color_reward = min(color_progress_weight, stable_causal_color * 5.0)
            spatial_reward = min(
                spatial_progress_weight,
                spatial_progress * (0.70 if selected_kind in ("keyboard", "mixed", "pointer") else 0.35),
            )
            hud_only_penalty = min(0.12, max(0.0, hud_change - world_change * 1.4) * 0.75)
            fade_penalty = min(fade_penalty_weight, fade_score * (0.55 + 0.45 * global_shift))
            meaningful_transition = (
                not next_black
                and scene_distance >= 0.075
                and (
                    stable_causal_motion >= 0.002
                    or stable_causal_change >= 0.012
                    or stable_causal_color >= 0.003
                )
            )
            transition_reward = (
                transition_novelty_weight / math.sqrt(edge_count + 1.0)
                if meaningful_transition and cycle_score < 0.72
                else 0.0
            )
            novel_state = visit_count == 0 and not looped
            novelty_reward = (
                0.18 / math.sqrt(visit_count + 1.0)
                if useful_motion >= 0.0025 or color_motion >= 0.0035
                else 0.0
            )
            progress_reward = (
                0.18
                if (
                    novel_state
                    and scene_distance >= 0.10
                    and (
                        (stable_causal_motion >= 0.0035 and stable_causal_change >= 0.012)
                        or stable_causal_color >= 0.005
                    )
                )
                else 0.0
            )
            frontier_reward = persistent_frontier_reward(
                state_visit_totals,
                next_memory_state,
                scene_distance,
                meaningful_transition,
                persistent_frontier_reward_weight,
            )
            loop_penalty = 0.14 if looped and not novel_state else 0.0
            cycle_penalty = cycle_penalty_weight * cycle_score
            static_penalty = min(0.70, static_streak * 0.047) if action_index != 0 else min(0.34, static_streak * 0.024)
            repetition_penalty = 0.0
            if len(recent_actions) >= 5 and len(set(recent_actions[-5:])) == 1 and recent_actions[-1] == action_index:
                repetition_penalty = min(0.38, 0.055 * (len(recent_actions[-8:]) - 4))
            passive_penalty = min(0.18, passive_motion * 2.2 + passive_color * 1.4)
            flicker_penalty = min(0.38, flicker * 1.9)
            uniform_change_penalty = min(
                0.20,
                max(0.0, 0.30 - change_concentration) * stable_causal_motion * 4.0 + global_shift * 0.30,
            )
            repeated_state_action = state_action_visits.get((current_state_key, action_index), 0)
            repeated_state_action_penalty = min(0.24, repeated_state_action * 0.035)
            black_penalty = 0.75 if black or next_black else 0.0
            reward = max(
                -1.0,
                min(
                    1.0,
                    motion_reward
                    + change_reward
                    + structured_reward
                    + center_reward
                    + world_progress_reward
                    + color_reward
                    + spatial_reward
                    + transition_reward
                    + novelty_reward
                    + progress_reward
                    + frontier_reward
                    - loop_penalty
                    - cycle_penalty
                    - static_penalty
                    - repetition_penalty
                    - passive_penalty
                    - hud_only_penalty
                    - flicker_penalty
                    - uniform_change_penalty
                    - fade_penalty
                    - repeated_state_action_penalty
                    - black_penalty,
                ),
            )
            risk_signal = max(0.0, -reward)
            if next_black:
                risk_signal = 1.0
            elif action_effect < 0.01 and static_streak >= stuck_recovery_threshold:
                risk_signal = max(risk_signal, 0.42)
            elif hud_only_penalty >= 0.08 and world_progress_reward <= 0.01:
                risk_signal = max(risk_signal, 0.30)
            elif fade_penalty >= 0.10 and spatial_reward <= 0.01:
                risk_signal = max(risk_signal, 0.34)
            update_action_risk(profile, action_index, risk_signal)
            if failure_cooldown_steps > 0 and risk_signal >= 0.55 and action_index != 0:
                action_block_until[action_index] = max(
                    action_block_until.get(action_index, 0),
                    steps + failure_cooldown_steps,
                )
            elif reward >= 0.20:
                action_block_until.pop(action_index, None)
            reward_sum += reward
            recent_reward_observations = min(1_000_000_000, recent_reward_observations + 1)
            reward_alpha = 1.0 if recent_reward_observations == 1 else 0.18
            recent_reward_ema += reward_alpha * (reward - recent_reward_ema)
            update_control_response(profile, action_index, reward)
            update_scene_control_response(profile, scene_context_name, action_index, reward)
            update_scene_action_response(profile, scene_context_name, action_index, reward)
            if reward >= successful_transition_threshold and recent_actions:
                transition_weight = 1 + min(4, max(0, int((reward - successful_transition_threshold) * 6.0)))
                record_transition(
                    profile,
                    recent_actions[-1],
                    action_index,
                    recent_actions[-2] if len(recent_actions) >= 2 else None,
                    transition_weight,
                )
            state_action_key = (current_state_key, action_index)
            update_online_state_value(state_action_values, state_action_key, reward)
            persistent_key = (current_memory_state, action_index)
            state_reward = bootstrapped_state_reward(
                persistent_state_values,
                next_memory_state,
                len(profile["actions"]),
                reward,
                state_bootstrap_weight,
            )
            previous_memory_visits = int(
                persistent_state_values.get(persistent_key, (0.0, 0))[1]
            )
            update_state_value_memory(
                persistent_state_values,
                persistent_key,
                state_reward,
                online_learning_rate,
            )
            dirty_state_values.add(persistent_key)
            memory_value, memory_visits = persistent_state_values.get(persistent_key, (0.0, 0))
            visit_delta = max(0, int(memory_visits) - previous_memory_visits)
            state_visit_totals[current_memory_state] = min(
                1_000_000_000_000,
                state_visit_totals.get(current_memory_state, 0) + visit_delta,
            )
            update_state_memory_index(
                state_memory_index,
                persistent_key,
                memory_value,
                memory_visits,
            )
            online_reliability = online_update_reliability(
                persistence,
                flicker,
                fade_score,
                global_shift,
                next_black,
            )
            model_updated = online_model_update(
                np,
                model,
                feature,
                action_index,
                reward,
                online_model_learning_rate * online_reliability,
                next_feature,
                online_td_discount,
                next_black,
                target_model,
            )
            if model_updated:
                online_model_changed = True
                if int(model.get("online_updates", 0)) % target_network_sync_steps == 0:
                    soft_update_target_model(
                        np,
                        target_model,
                        model,
                        target_network_soft_update,
                    )
            advance_delayed_experience(
                profile,
                pending_experiences,
                rows,
                feature,
                action_index,
                reward,
                delayed_horizon,
                delayed_discount,
            )
            if len(rows) >= 100:
                insert_samples(paths["db"], rows)
                rows.clear()
            if len(dirty_state_values) >= 256:
                save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
            state_visits[next_state_key] = visit_count + 1
            state_action_visits[state_action_key] = state_action_visits.get(state_action_key, 0) + 1
            edge_visits[edge_key] = edge_count + 1
            if len(state_action_visits) > 16384:
                state_action_visits.clear()
            if len(edge_visits) > 24576:
                edge_visits.clear()
            if len(state_visits) > 8192:
                retained = {key: state_visits.get(key, 1) for key in recent_state_keys[-128:]}
                state_visits.clear()
                state_visits.update(retained)
            recent_frame_hashes.append(digest)
            if len(recent_frame_hashes) > 128:
                recent_frame_hashes.pop(0)
            recent_state_keys.append(next_state_key)
            if len(recent_state_keys) > 128:
                recent_state_keys.pop(0)
            recent_actions.append(action_index)
            if len(recent_actions) > 20:
                recent_actions.pop(0)
            steps += 1
            if online_model_changed and steps % online_checkpoint_steps == 0:
                model["action_hash"] = actions_hash(profile["actions"])
                model["action_signatures"] = [action_signature(action) for action in profile["actions"]]
                save_model(np, paths["model"], model)
                online_model_changed = False
    finally:
        release_all_inputs()
        flush_delayed_experience(profile, pending_experiences, rows)
        if rows:
            insert_samples(paths["db"], rows)
        save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
        sampler.close()
        if online_model_changed:
            model["action_hash"] = actions_hash(profile["actions"])
            model["action_signatures"] = [action_signature(action) for action in profile["actions"]]
            save_model(np, paths["model"], model)
        if steps:
            mean_reward = max(-1.0, min(1.0, reward_sum / steps))
            old_session_reward = float(profile.get("ai_reward_ema", 0.0))
            completed_sessions = int(profile.get("ai_sessions", 0))
            session_alpha = 1.0 if completed_sessions <= 0 else 0.20
            profile["last_ai_mean_reward"] = mean_reward
            profile["ai_reward_ema"] = old_session_reward + session_alpha * (mean_reward - old_session_reward)
            profile["ai_sessions"] = completed_sessions + 1
            profile["passive_motion_ema"] = max(0.0, min(1.0, passive_motion_ema))
            profile["passive_change_ema"] = max(0.0, min(1.0, passive_change_ema))
            profile["passive_color_ema"] = max(0.0, min(1.0, passive_color_ema))
            profile["needs_training"] = True
            save_profile(profile, paths)
        compact_experience(paths["db"], int(config["experience_limit_per_game"]), len(profile["actions"]))
        compact_state_values(paths["db"], state_memory_limit, len(profile["actions"]))
        wait_esc_release()
    warning = "；画面可能未被正确采集" if black_frames > max(20, steps // 2) else ""
    mean_text = f"；平均反馈 {reward_sum / steps:.2f}" if steps else ""
    return f"AI结束：{profile['name']}；模式 {mode_text}；执行 {steps} 步；经验池原有 {total} 条{mean_text}{warning}"


class AnyGameAIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("620x230")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.stop_and_close)
        self.root.attributes("-topmost", True)
        self.root.after(700, lambda: self.root.attributes("-topmost", False))
        self.stop_event = threading.Event()
        self.worker_messages: queue.Queue = queue.Queue()
        self.busy = False
        self.closing = False
        self.close_requested = False
        self.worker_thread: threading.Thread | None = None
        self.shutdown_deadline = 0.0
        self.escape_was_down = esc_pressed() if os.name == "nt" else False

        tk.Label(self.root, text=f"AnyGameAI {APP_VERSION}", font=("Segoe UI", 24, "bold")).pack(pady=(22, 8))
        tk.Label(
            self.root,
            text="选择一项任务；切换到游戏窗口后，ESC 安全结束并退出",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 14))

        button_frame = tk.Frame(self.root)
        button_frame.pack()
        self.file_button = tk.Button(button_frame, text=STRICT_UI_ACTIONS[0], width=11, height=2, command=self.file_mode)
        self.human_button = tk.Button(button_frame, text=STRICT_UI_ACTIONS[1], width=11, height=2, command=self.human_mode)
        self.upgrade_button = tk.Button(button_frame, text=STRICT_UI_ACTIONS[2], width=11, height=2, command=self.upgrade_mode)
        self.ai_button = tk.Button(button_frame, text=STRICT_UI_ACTIONS[3], width=11, height=2, command=self.ai_mode)
        for column, button in enumerate((self.file_button, self.human_button, self.upgrade_button, self.ai_button)):
            button.grid(row=0, column=column, padx=7)

        self.status = tk.StringVar(value="就绪")
        tk.Label(self.root, textvariable=self.status, font=("Segoe UI", 10), wraplength=580).pack(pady=18)
        self.root.bind("<Escape>", self.on_escape)
        self.root.after(60, self.poll_worker)

    def on_escape(self, _event=None) -> None:
        self.escape_was_down = True
        self.stop_and_close()

    def set_busy(self, value: bool) -> None:
        self.busy = value
        state = tk.DISABLED if value else tk.NORMAL
        for button in (self.file_button, self.human_button, self.upgrade_button, self.ai_button):
            button.config(state=state)

    def stop_and_close(self) -> None:
        if self.closing:
            return
        self.closing = True
        self.close_requested = True
        self.stop_event.set()
        self.shutdown_deadline = time.monotonic() + SHUTDOWN_GRACE_SECONDS
        if os.name == "nt":
            release_all_inputs()
        self.set_busy(True)
        try:
            self.root.withdraw()
        except Exception:
            pass
        self._poll_shutdown()

    def _poll_shutdown(self) -> None:
        worker_alive = self.worker_thread is not None and self.worker_thread.is_alive()
        if worker_alive and time.monotonic() < self.shutdown_deadline:
            try:
                self.root.after(SHUTDOWN_POLL_MILLISECONDS, self._poll_shutdown)
            except Exception:
                pass
            return
        if worker_alive:
            terminate_active_processes()
        if os.name == "nt":
            release_all_inputs()
        try:
            self.root.destroy()
        except Exception:
            pass

    def run_worker(self, status: str, worker, hide: bool = False) -> None:
        if self.busy:
            return
        self.stop_event.clear()
        self.close_requested = False
        self.set_busy(True)
        self.status.set(status)
        if hide:
            self.root.withdraw()

        def task() -> None:
            result = None
            error = None
            activity = begin_runtime_activity(display_required=hide)
            try:
                result = worker()
            except RuntimeError as exception:
                if str(exception) == "操作已取消":
                    error = "操作已取消"
                else:
                    error = str(exception).strip() or "运行失败"
                    log_text(traceback.format_exc())
            except Exception:
                error = traceback.format_exc()
                log_text(error)
            finally:
                end_runtime_activity(activity)
            self.worker_messages.put((result, error, hide))

        self.worker_thread = threading.Thread(
            target=task,
            daemon=True,
            name="AnyGameAI-Worker",
        )
        self.worker_thread.start()

    def poll_worker(self) -> None:
        if self.closing:
            return
        if os.name == "nt":
            escape_is_down = esc_pressed()
            if escape_is_down and not self.escape_was_down:
                self.escape_was_down = True
                self.stop_and_close()
                return
            elif not escape_is_down:
                self.escape_was_down = False
        try:
            while True:
                result, error, hidden = self.worker_messages.get_nowait()
                self.worker_done(result, error, hidden)
        except queue.Empty:
            pass
        if not self.closing:
            self.root.after(60, self.poll_worker)

    def worker_done(self, result, error: str | None, _hidden: bool) -> None:
        self.worker_thread = None
        if os.name == "nt":
            release_all_inputs()
        self.set_busy(False)
        if error and "操作已取消" not in error:
            detail = error.strip().splitlines()[-1] if error.strip() else "未知错误"
            self.status.set(f"运行失败：{detail}；详情见桌面 AnyGameAI 文件夹中的日志")
        else:
            self.status.set(str(result) if result else "已结束")
        self.close_requested = False
        self.root.after(180, self.stop_and_close)

    def file_mode(self) -> None:
        def work():
            result = ensure_files(self.stop_event)
            if self.stop_event.is_set():
                return "文件检查已结束"
            parts = [
                f"修复 {result['repaired']} 项",
                f"下载 {result['downloaded']} 项",
                f"经验 {result['records']} 条",
                f"场景记忆 {result['memory_records']} 条",
                f"人工示范记忆 {result['human_memory_records']} 条",
                f"清理 {result['removed']} 条",
            ]
            if result.get("restart_required"):
                parts.append("主程序已更新")
            return "文件检查完成：" + "；".join(parts)

        self.run_worker("正在检查、下载、补全和修复文件…", work)

    def human_mode(self) -> None:
        def work():
            target = wait_for_target_window(self.stop_event)
            if not target:
                wait_esc_release()
                return "未检测到游戏窗口，人玩模式已结束"
            return record_human_session(target, self.stop_event)

        self.run_worker("请切换到游戏窗口；正在学习你的键盘和鼠标操作；ESC 结束", work, hide=True)

    def upgrade_mode(self) -> None:
        self.run_worker(
            "正在升级策略、动作价值、动作序列、多步规划依据、场景动作记忆和跨游戏通用先验，并整理经验池；ESC 可取消",
            lambda: train_all_profiles(self.stop_event),
        )

    def ai_mode(self) -> None:
        def work():
            target = wait_for_target_window(self.stop_event)
            if not target:
                wait_esc_release()
                return "未检测到游戏窗口，AI 模式已结束"
            return run_ai_session(target, self.stop_event)

        self.run_worker(
            "请切换到游戏窗口；AI 将自动使用游戏模型、人工示范记忆、多步动作规划、场景动作记忆、在线适应、跨游戏迁移或通用探索；ESC 结束",
            work,
            hide=True,
        )

    def run(self) -> None:
        self.root.mainloop()


class NativeAnyGameAIApp:
    WM_CLOSE = 0x0010
    WM_DESTROY = 0x0002
    WM_COMMAND = 0x0111
    WM_KEYDOWN = 0x0100
    WM_TIMER = 0x0113
    WM_SETFONT = 0x0030
    BN_CLICKED = 0
    TIMER_ID = 1
    BUTTON_SPECS = (
        (1001, "文件", "file_mode"),
        (1002, "人", "human_mode"),
        (1003, "升级", "upgrade_mode"),
        (1004, "AI", "ai_mode"),
    )

    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("Windows 原生界面只能在 Windows 上运行")
        self.stop_event = threading.Event()
        self.worker_messages: queue.Queue = queue.Queue()
        self.busy = False
        self.closing = False
        self.close_requested = False
        self.worker_thread: threading.Thread | None = None
        self.shutdown_deadline = 0.0
        self.close_after = 0.0
        self.escape_was_down = esc_pressed()
        self.hwnd = 0
        self.status_handle = 0
        self.button_handles: list[int] = []
        self._commands = {
            identifier: getattr(self, method_name)
            for identifier, _, method_name in self.BUTTON_SPECS
        }
        self._class_name = f"{APP_NAME}.NativeUI.{os.getpid()}"
        self._window_proc_type = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        )
        self._window_proc = self._window_proc_type(self._window_procedure)
        self._create_window()

    def _create_window(self) -> None:
        callback_type = self._window_proc_type

        class WNDCLASSEXW(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("style", wintypes.UINT),
                ("lpfnWndProc", callback_type),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HANDLE),
                ("hIcon", wintypes.HANDLE),
                ("hCursor", wintypes.HANDLE),
                ("hbrBackground", wintypes.HANDLE),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
                ("hIconSm", wintypes.HANDLE),
            ]

        user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
        user32.RegisterClassExW.restype = wintypes.WORD
        user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HANDLE]
        user32.UnregisterClassW.restype = wintypes.BOOL
        user32.CreateWindowExW.argtypes = [
            wintypes.DWORD,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            wintypes.HANDLE,
            wintypes.HANDLE,
            ctypes.c_void_p,
        ]
        user32.CreateWindowExW.restype = wintypes.HWND
        user32.DefWindowProcW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.DefWindowProcW.restype = ctypes.c_ssize_t
        user32.DestroyWindow.argtypes = [wintypes.HWND]
        user32.DestroyWindow.restype = wintypes.BOOL
        user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
        user32.EnableWindow.restype = wintypes.BOOL
        user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
        user32.SetWindowTextW.restype = wintypes.BOOL
        user32.SendMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.SendMessageW.restype = ctypes.c_ssize_t
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = wintypes.BOOL
        user32.UpdateWindow.argtypes = [wintypes.HWND]
        user32.UpdateWindow.restype = wintypes.BOOL
        user32.SetTimer.argtypes = [wintypes.HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
        user32.SetTimer.restype = ctypes.c_size_t
        user32.KillTimer.argtypes = [wintypes.HWND, ctypes.c_size_t]
        user32.KillTimer.restype = wintypes.BOOL
        user32.PostQuitMessage.argtypes = [ctypes.c_int]
        user32.PostQuitMessage.restype = None
        user32.LoadCursorW.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
        user32.LoadCursorW.restype = wintypes.HANDLE
        gdi32.GetStockObject.argtypes = [ctypes.c_int]
        gdi32.GetStockObject.restype = wintypes.HANDLE

        self._instance = kernel32.GetModuleHandleW(None)
        window_class = WNDCLASSEXW()
        window_class.cbSize = ctypes.sizeof(WNDCLASSEXW)
        window_class.style = 0x0003
        window_class.lpfnWndProc = self._window_proc
        window_class.hInstance = self._instance
        window_class.hCursor = user32.LoadCursorW(None, ctypes.c_void_p(32512))
        window_class.hbrBackground = wintypes.HANDLE(16)
        window_class.lpszClassName = self._class_name
        if not user32.RegisterClassExW(ctypes.byref(window_class)):
            raise ctypes.WinError()

        width = 640
        height = 270
        x = max(0, (int(user32.GetSystemMetrics(0)) - width) // 2)
        y = max(0, (int(user32.GetSystemMetrics(1)) - height) // 2)
        self.hwnd = int(
            user32.CreateWindowExW(
                0,
                self._class_name,
                f"{APP_NAME} {APP_VERSION}",
                0x00CA0000,
                x,
                y,
                width,
                height,
                None,
                None,
                self._instance,
                None,
            )
            or 0
        )
        if not self.hwnd:
            user32.UnregisterClassW(self._class_name, self._instance)
            raise ctypes.WinError()

        child_style = 0x50000000
        center_style = child_style | 0x00000001
        controls: list[int] = []

        def create_control(
            class_name: str,
            text: str,
            style: int,
            left: int,
            top: int,
            control_width: int,
            control_height: int,
            identifier: int = 0,
        ) -> int:
            handle = int(
                user32.CreateWindowExW(
                    0,
                    class_name,
                    text,
                    style,
                    left,
                    top,
                    control_width,
                    control_height,
                    self.hwnd,
                    wintypes.HANDLE(identifier) if identifier else None,
                    self._instance,
                    None,
                )
                or 0
            )
            if not handle:
                raise ctypes.WinError()
            controls.append(handle)
            return handle

        create_control(
            "STATIC",
            f"{APP_NAME} {APP_VERSION}",
            center_style,
            20,
            22,
            600,
            28,
        )
        create_control(
            "STATIC",
            "选择一项任务；切换到游戏窗口后，ESC 安全结束并退出",
            center_style,
            20,
            56,
            600,
            24,
        )
        for column, (identifier, text, _) in enumerate(self.BUTTON_SPECS):
            self.button_handles.append(
                create_control(
                    "BUTTON",
                    text,
                    child_style | 0x00000000,
                    42 + column * 146,
                    94,
                    118,
                    46,
                    identifier,
                )
            )
        self.status_handle = create_control(
            "STATIC",
            "就绪",
            center_style,
            24,
            164,
            592,
            42,
        )
        font = int(gdi32.GetStockObject(17) or 0)
        if font:
            for handle in controls:
                user32.SendMessageW(handle, self.WM_SETFONT, font, 1)
        if not user32.SetTimer(self.hwnd, self.TIMER_ID, SHUTDOWN_POLL_MILLISECONDS, None):
            raise ctypes.WinError()
        user32.ShowWindow(self.hwnd, 5)
        user32.UpdateWindow(self.hwnd)

    def _window_procedure(self, window, message, wparam, lparam):
        try:
            if message == self.WM_COMMAND:
                identifier = int(wparam) & 0xFFFF
                notification = (int(wparam) >> 16) & 0xFFFF
                command = self._commands.get(identifier)
                if notification == self.BN_CLICKED and command is not None:
                    command()
                    return 0
            elif message == self.WM_KEYDOWN and int(wparam) == ESC_VK:
                self.on_escape()
                return 0
            elif message == self.WM_TIMER and int(wparam) == self.TIMER_ID:
                self.poll_worker()
                return 0
            elif message == self.WM_CLOSE:
                self.stop_and_close()
                return 0
            elif message == self.WM_DESTROY:
                if window:
                    user32.KillTimer(window, self.TIMER_ID)
                self.hwnd = 0
                user32.PostQuitMessage(0)
                return 0
        except Exception:
            log_text("Windows 原生界面异常:\n" + traceback.format_exc())
            try:
                self.stop_and_close()
            except Exception:
                pass
            return 0
        return user32.DefWindowProcW(window, message, wparam, lparam)

    def _set_status(self, text: str) -> None:
        if self.status_handle:
            user32.SetWindowTextW(self.status_handle, str(text))

    def on_escape(self, _event=None) -> None:
        self.escape_was_down = True
        self.stop_and_close()

    def set_busy(self, value: bool) -> None:
        self.busy = value
        for button in self.button_handles:
            user32.EnableWindow(button, not value)

    def stop_and_close(self) -> None:
        if self.closing:
            return
        self.closing = True
        self.close_requested = True
        self.stop_event.set()
        self.shutdown_deadline = time.monotonic() + SHUTDOWN_GRACE_SECONDS
        release_all_inputs()
        self.set_busy(True)
        if self.hwnd:
            user32.ShowWindow(self.hwnd, 0)
        self._poll_shutdown()

    def _poll_shutdown(self) -> None:
        worker_alive = self.worker_thread is not None and self.worker_thread.is_alive()
        if worker_alive and time.monotonic() < self.shutdown_deadline:
            return
        if worker_alive:
            terminate_active_processes()
        release_all_inputs()
        window = self.hwnd
        if window:
            user32.DestroyWindow(window)

    def run_worker(self, status: str, worker, hide: bool = False) -> None:
        if self.busy:
            return
        self.stop_event.clear()
        self.close_requested = False
        self.close_after = 0.0
        self.set_busy(True)
        self._set_status(status)
        if hide and self.hwnd:
            user32.ShowWindow(self.hwnd, 0)

        def task() -> None:
            result = None
            error = None
            activity = begin_runtime_activity(display_required=hide)
            try:
                result = worker()
            except RuntimeError as exception:
                if str(exception) == "操作已取消":
                    error = "操作已取消"
                else:
                    error = str(exception).strip() or "运行失败"
                    log_text(traceback.format_exc())
            except Exception:
                error = traceback.format_exc()
                log_text(error)
            finally:
                end_runtime_activity(activity)
            self.worker_messages.put((result, error, hide))

        self.worker_thread = threading.Thread(
            target=task,
            daemon=True,
            name="AnyGameAI-Native-Worker",
        )
        self.worker_thread.start()

    def poll_worker(self) -> None:
        if self.closing:
            self._poll_shutdown()
            return
        escape_is_down = esc_pressed()
        if escape_is_down and not self.escape_was_down:
            self.escape_was_down = True
            self.stop_and_close()
            return
        if not escape_is_down:
            self.escape_was_down = False
        try:
            while True:
                result, error, hidden = self.worker_messages.get_nowait()
                self.worker_done(result, error, hidden)
        except queue.Empty:
            pass
        if self.close_after and time.monotonic() >= self.close_after:
            self.stop_and_close()

    def worker_done(self, result, error: str | None, _hidden: bool) -> None:
        self.worker_thread = None
        release_all_inputs()
        self.set_busy(False)
        if error and "操作已取消" not in error:
            detail = error.strip().splitlines()[-1] if error.strip() else "未知错误"
            self._set_status(f"运行失败：{detail}；详情见桌面 AnyGameAI 文件夹中的日志")
        else:
            self._set_status(str(result) if result else "已结束")
        if self.close_requested:
            self.stop_and_close()
            return
        self.close_after = time.monotonic() + 0.18

    def file_mode(self) -> None:
        def work():
            result = ensure_files(self.stop_event)
            if self.stop_event.is_set():
                return "文件检查已结束"
            parts = [
                f"修复 {result['repaired']} 项",
                f"下载 {result['downloaded']} 项",
                f"经验 {result['records']} 条",
                f"场景记忆 {result['memory_records']} 条",
                f"人工示范记忆 {result['human_memory_records']} 条",
                f"清理 {result['removed']} 条",
            ]
            if result.get("restart_required"):
                parts.append("主程序已更新")
            return "文件检查完成：" + "；".join(parts)

        self.run_worker("正在检查、下载、补全和修复文件…", work)

    def human_mode(self) -> None:
        def work():
            target = wait_for_target_window(self.stop_event)
            if not target:
                wait_esc_release()
                return "未检测到游戏窗口，人玩模式已结束"
            return record_human_session(target, self.stop_event)

        self.run_worker("请切换到游戏窗口；正在学习你的键盘和鼠标操作；ESC 结束", work, hide=True)

    def upgrade_mode(self) -> None:
        self.run_worker(
            "正在升级策略、动作价值、动作序列、多步规划依据、场景动作记忆和跨游戏通用先验，并整理经验池；ESC 可取消",
            lambda: train_all_profiles(self.stop_event),
        )

    def ai_mode(self) -> None:
        def work():
            target = wait_for_target_window(self.stop_event)
            if not target:
                wait_esc_release()
                return "未检测到游戏窗口，AI 模式已结束"
            return run_ai_session(target, self.stop_event)

        self.run_worker(
            "请切换到游戏窗口；AI 将自动使用游戏模型、人工示范记忆、多步动作规划、场景动作记忆、在线适应、跨游戏迁移或通用探索；ESC 结束",
            work,
            hide=True,
        )

    def run(self) -> None:
        message = MSG()
        try:
            while True:
                result = int(user32.GetMessageW(ctypes.byref(message), None, 0, 0))
                if result == 0:
                    break
                if result < 0:
                    raise ctypes.WinError()
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        finally:
            release_all_inputs()
            if self.hwnd:
                user32.DestroyWindow(self.hwnd)
            user32.UnregisterClassW(self._class_name, self._instance)


def show_startup_error(text: str) -> None:
    if tk is not None and messagebox is not None:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(APP_NAME, text)
            root.destroy()
            return
        except Exception:
            pass
    if os.name == "nt":
        native_user32 = ctypes.windll.user32
        native_user32.MessageBoxW.argtypes = [
            wintypes.HWND,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.UINT,
        ]
        native_user32.MessageBoxW.restype = ctypes.c_int
        native_user32.MessageBoxW(None, str(text), APP_NAME, 0x00000010)
        return
    sys.stderr.write(f"{APP_NAME}: {text}\n")


def unhandled_exception(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    detail = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_text("未处理异常:\n" + detail)
    try:
        show_startup_error("程序发生异常，详情已写入桌面 AnyGameAI 文件夹中的日志。")
    except Exception:
        pass


def supported_host_error() -> str | None:
    if os.name != "nt":
        return "此程序仅支持 Windows 11 x64。"
    machine = platform.machine().strip().lower()
    native_machine = (
        os.environ.get("PROCESSOR_ARCHITEW6432")
        or os.environ.get("PROCESSOR_ARCHITECTURE")
        or machine
    ).strip().lower()
    if (
        sys.maxsize <= 2**32
        or ctypes.sizeof(ctypes.c_void_p) != 8
        or machine not in SUPPORTED_X64_MACHINES
        or native_machine not in SUPPORTED_X64_MACHINES
    ):
        return "需要 Windows 11 x64 和 x64 版 Python。"
    if (
        sys.version_info[:2] != REQUIRED_PYTHON_VERSION
        or sys.version_info.releaselevel != "final"
        or platform.python_implementation() != "CPython"
    ):
        return "需要正式版 CPython 3.12 x64。"
    if windows_build_number() < MIN_WINDOWS_11_BUILD:
        return "需要 Windows 11 x64。"
    return None


def main() -> None:
    sys.excepthook = unhandled_exception
    host_error = supported_host_error()
    if host_error is not None:
        show_startup_error(host_error)
        return
    hide_console()
    if not acquire_single_instance():
        show_startup_error("AnyGameAI 已经在运行。")
        return
    atexit.register(release_single_instance)
    atexit.register(terminate_active_processes)
    atexit.register(release_all_inputs)
    configure_runtime_environment()
    bootstrap_to_desktop()
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    if tk is not None:
        try:
            app = AnyGameAIApp()
        except Exception:
            log_text("Tk 图形界面不可用，切换到 Windows 原生界面：\n" + traceback.format_exc())
            app = NativeAnyGameAIApp()
    else:
        app = NativeAnyGameAIApp()
    app.run()


if __name__ == "__main__":
    main()
