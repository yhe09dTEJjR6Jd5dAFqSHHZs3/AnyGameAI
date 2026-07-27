from __future__ import annotations

import atexit
import base64
import csv
import ctypes
import hashlib
import hmac
import importlib
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
import urllib.parse
import urllib.request
import zlib
from ctypes import wintypes
from datetime import datetime
from pathlib import Path, PurePosixPath
import tkinter as tk
from tkinter import messagebox


APP_NAME = "AnyGameAI"
APP_VERSION = "17.0"
SCRIPT_NAME = "AnyGameAI.py"
APP_SCHEMA = 8
CONFIG_SCHEMA = 8
PROFILE_SCHEMA = 9
MODEL_SCHEMA = 5
FEATURE_WIDTH = 40
FEATURE_HEIGHT = 24
FEATURE_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 2
MODEL_PIXEL_CHANNELS = 3
MODEL_GLOBAL_FEATURES = 20
MODEL_INPUT_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * MODEL_PIXEL_CHANNELS + MODEL_GLOBAL_FEATURES
MAX_COMPRESSED_FEATURE_BYTES = FEATURE_DIM * 2 + 256
DEFAULT_HIDDEN_SIZE = 128
TARGET_WAIT_SECONDS = 15.0
MOUSE_GRID_WIDTH = 32
MOUSE_GRID_HEIGHT = 18
INTEGRITY_SCHEMA = 1
GLOBAL_PRIOR_SCHEMA = 4
NUMPY_REQUIREMENT = "numpy>=1.26,<3"
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_REMOTE_FILE_BYTES = 512 * 1024 * 1024
MAX_SCRIPT_BYTES = 8 * 1024 * 1024
MAX_DISTRIBUTION_RECORDS = 20_000
UNIVERSAL_ACTION_SCHEMA = 4
UNIVERSAL_ACTION_LIMIT = 160
DELAYED_REWARD_HORIZON_DEFAULT = 6
DELAYED_REWARD_DISCOUNT_DEFAULT = 0.82
CONTROL_KINDS = ("idle", "keyboard", "pointer", "click", "wheel", "mixed")
COLD_START_PROBE_LIMIT = 24
WINDOWS_RESERVED_NAMES = {"con", "prn", "aux", "nul", *(f"com{index}" for index in range(1, 10)), *(f"lpt{index}" for index in range(1, 10))}
WINDOWS_INVALID_NAME_PATTERN = re.compile(r'[<>:"|?*\x00-\x1f]')
VERSION_PATTERN = re.compile(r'^APP_VERSION\s*=\s*["\'](\d+(?:\.\d+)*)["\']', re.MULTILINE)
STATE_MEMORY_KEY_PATTERN = re.compile(r"[0-9a-f]{8}:[0-9a-f]:[0-7]\Z")


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
LOCAL_SCRIPT_PATH = APP_DIR / SCRIPT_NAME
CONFIG_PATH = APP_DIR / "config.json"
INDEX_PATH = APP_DIR / "profiles.json"
LOG_PATH = APP_DIR / "AnyGameAI.log"
INTEGRITY_PATH = APP_DIR / "integrity.json"
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
    "max_action_count": 192,
    "experience_limit_per_game": 90000,
    "train_sample_limit_per_game": 16000,
    "training_epochs": 10,
    "training_batch_size": 128,
    "learning_rate": 0.0015,
    "hidden_size": DEFAULT_HIDDEN_SIZE,
    "zero_shot_exploration": 0.26,
    "transfer_action_limit": 48,
    "delayed_reward_horizon": DELAYED_REWARD_HORIZON_DEFAULT,
    "delayed_reward_discount": DELAYED_REWARD_DISCOUNT_DEFAULT,
    "online_state_value_weight": 0.34,
    "state_memory_limit_per_game": 40000,
    "state_memory_weight": 0.45,
    "online_learning_rate": 0.16,
    "remote_manifest_url": "",
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
    "online_learning_rate": (0.01, 1.0),
}


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as file:
        file.write(text)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, path)


def atomic_write_json(path: Path, data: object) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def script_version(path: Path) -> tuple[int, ...] | None:
    try:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
        match = VERSION_PATTERN.search(source)
        if match is None:
            return None
        return tuple(int(part) for part in match.group(1).split("."))
    except Exception:
        return None


def valid_script(path: Path) -> bool:
    try:
        if not path.is_file() or path.stat().st_size > MAX_SCRIPT_BYTES:
            return False
        return script_version(path) is not None
    except OSError:
        return False


def load_integrity_state() -> dict:
    try:
        data = json.loads(INTEGRITY_PATH.read_text(encoding="utf-8"))
        if (
            isinstance(data, dict)
            and data.get("schema") == INTEGRITY_SCHEMA
            and isinstance(data.get("script_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", data["script_sha256"])
        ):
            return data
    except Exception:
        pass
    return {}


def save_integrity_state(script_path: Path) -> None:
    atomic_write_json(
        INTEGRITY_PATH,
        {
            "schema": INTEGRITY_SCHEMA,
            "app_version": ".".join(str(part) for part in (script_version(script_path) or ())),
            "script_sha256": sha256_file(script_path),
            "updated_at": now_text(),
        },
    )


def refresh_script_backup(script_path: Path) -> bool:
    if not valid_script(script_path):
        raise RuntimeError("主程序文件损坏")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    changed = True
    if BACKUP_SCRIPT_PATH.exists() and valid_script(BACKUP_SCRIPT_PATH):
        changed = sha256_file(BACKUP_SCRIPT_PATH) != sha256_file(script_path)
    if changed:
        temp = BACKUP_SCRIPT_PATH.with_name(BACKUP_SCRIPT_PATH.name + ".tmp")
        shutil.copy2(script_path, temp)
        if not valid_script(temp):
            temp.unlink(missing_ok=True)
            raise RuntimeError("主程序备份校验失败")
        os.replace(temp, BACKUP_SCRIPT_PATH)
    save_integrity_state(script_path)
    return changed


def repair_main_script() -> tuple[int, bool]:
    current = Path(__file__).resolve()
    local = LOCAL_SCRIPT_PATH.resolve()
    repaired = 0
    restart_required = False
    if not valid_script(current):
        raise RuntimeError("当前主程序文件损坏")
    if current != local:
        current_version = script_version(current) or ()
        local_version = script_version(local) if local.exists() else None
        if local_version is None or current_version >= local_version:
            if not local.exists() or sha256_file(current) != sha256_file(local):
                LOCAL_SCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
                temp = LOCAL_SCRIPT_PATH.with_name(LOCAL_SCRIPT_PATH.name + ".tmp")
                shutil.copy2(current, temp)
                if not valid_script(temp):
                    temp.unlink(missing_ok=True)
                    raise RuntimeError("主程序复制校验失败")
                os.replace(temp, LOCAL_SCRIPT_PATH)
                repaired += 1
        source = LOCAL_SCRIPT_PATH if valid_script(LOCAL_SCRIPT_PATH) else current
        if refresh_script_backup(source):
            repaired += 1
        return repaired, False
    state = load_integrity_state()
    expected_hash = state.get("script_sha256", "")
    current_hash = sha256_file(current)
    if expected_hash and current_hash != expected_hash and valid_script(BACKUP_SCRIPT_PATH):
        if sha256_file(BACKUP_SCRIPT_PATH) == expected_hash:
            temp = LOCAL_SCRIPT_PATH.with_name(LOCAL_SCRIPT_PATH.name + ".tmp")
            shutil.copy2(BACKUP_SCRIPT_PATH, temp)
            if valid_script(temp):
                os.replace(temp, LOCAL_SCRIPT_PATH)
                repaired += 1
                restart_required = True
            else:
                temp.unlink(missing_ok=True)
    if not restart_required:
        if refresh_script_backup(LOCAL_SCRIPT_PATH):
            repaired += 1
    return repaired, restart_required


def backup_corrupt(path: Path) -> None:
    if not path.exists():
        return
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
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
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(f"[{now_text()}] {text}\n")
    except Exception:
        pass


def deep_copy_json(data: object):
    return json.loads(json.dumps(data, ensure_ascii=False))


def validate_config(data: object) -> bool:
    if not isinstance(data, dict) or data.get("schema") != CONFIG_SCHEMA:
        return False
    for key, (minimum, maximum) in CONFIG_RANGES.items():
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        if not math.isfinite(float(value)) or not minimum <= float(value) <= maximum:
            return False
    if int(data["train_sample_limit_per_game"]) > int(data["experience_limit_per_game"]):
        return False
    return isinstance(data.get("remote_manifest_url"), str)


def valid_profile_id(profile_id: object) -> bool:
    return (
        isinstance(profile_id, str)
        and profile_id not in (".", "..")
        and PROFILE_ID_PATTERN.fullmatch(profile_id) is not None
    )


def load_config() -> dict:
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and raw.get("schema") in (3, 4, 5, 6, 7, CONFIG_SCHEMA):
            merged = deep_copy_json(DEFAULT_CONFIG)
            merged.update(raw)
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
        raw = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and raw.get("schema") in (3, 4, 5, 6, 7, APP_SCHEMA) and isinstance(raw.get("profiles"), dict):
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
        if not directory.is_dir() or not valid_profile_id(directory.name):
            continue
        profile_path = directory / "profile.json"
        try:
            candidate = json.loads(profile_path.read_text(encoding="utf-8"))
            profile = migrate_profile(candidate, directory.name)
            if profile is None:
                continue
            if profile != candidate:
                atomic_write_json(profile_path, profile)
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


def cleanup_temporary_files() -> int:
    removed = 0
    for path in APP_DIR.rglob("*"):
        if not path.is_file() or not (path.name.endswith(".tmp") or path.name.endswith(".download")):
            continue
        try:
            path.unlink()
            removed += 1
        except OSError:
            pass
    if TEMP_DIR.exists():
        try:
            removed += sum(1 for path in TEMP_DIR.rglob("*") if path.is_file())
            shutil.rmtree(TEMP_DIR)
        except OSError:
            pass
    if RUNTIME_DIR.exists():
        for directory in RUNTIME_DIR.glob(".update-*"):
            if not directory.is_dir():
                continue
            try:
                removed += sum(1 for path in directory.rglob("*") if path.is_file())
                shutil.rmtree(directory)
            except OSError:
                pass
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
    subprocess.Popen([gui_python_executable(), str(LOCAL_SCRIPT_PATH)], cwd=str(APP_DIR), creationflags=flags)


def bootstrap_to_desktop() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve()
    target = LOCAL_SCRIPT_PATH.resolve()
    if source != target:
        repair_main_script()
        launch_local_script()
        raise SystemExit
    _, restart_required = repair_main_script()
    if restart_required:
        launch_local_script()
        raise SystemExit


def hide_console() -> None:
    if os.name != "nt":
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
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
    probe = module.arange(16, dtype=module.float32).reshape(4, 4)
    if float(probe.mean()) != 7.5:
        raise RuntimeError("NumPy 自检失败")
    return module


def local_numpy_probe_command(site_packages: Path = SITE_PACKAGES) -> list[str]:
    code = (
        "import pathlib,sys;"
        f"root=pathlib.Path({str(site_packages)!r}).resolve();"
        "sys.path.insert(0,str(root));"
        "[sys.modules.pop(k,None) for k in list(sys.modules) if k=='numpy' or k.startswith('numpy.')];"
        "import numpy as n;"
        "path=pathlib.Path(n.__file__).resolve();"
        "assert path==root or root in path.parents;"
        "assert float(n.arange(16,dtype=n.float32).reshape(4,4).mean())==7.5;"
        "assert n.dtype('float32').itemsize==4"
    )
    return [sys.executable, "-c", code]


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
) -> int:
    root = site_packages.resolve()
    record_path = distribution_record_path(distribution_name, site_packages)
    verified = 0
    with record_path.open("r", encoding="utf-8", newline="") as file:
        for row_number, row in enumerate(csv.reader(file), 1):
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            if row_number > MAX_DISTRIBUTION_RECORDS:
                raise RuntimeError("依赖安装记录异常")
            if len(row) < 3 or not row[0] or not row[1]:
                continue
            algorithm, separator, encoded_digest = row[1].partition("=")
            if separator != "=" or algorithm.lower() != "sha256" or not encoded_digest:
                raise RuntimeError("依赖安装记录包含不支持的校验算法")
            pure = PurePosixPath(row[0])
            if pure.is_absolute() or any(part in ("", ".") for part in pure.parts):
                raise RuntimeError("依赖安装记录包含非法路径")
            if ".." in pure.parts:
                continue
            candidate = (site_packages / Path(*pure.parts)).resolve()
            if candidate != root and root not in candidate.parents:
                continue
            if not candidate.is_file():
                raise RuntimeError(f"依赖文件缺失：{row[0]}")
            if row[2]:
                try:
                    expected_size = int(row[2])
                except ValueError as error:
                    raise RuntimeError("依赖安装记录包含非法文件大小") from error
                if candidate.stat().st_size != expected_size:
                    raise RuntimeError(f"依赖文件大小错误：{row[0]}")
            digest = hashlib.sha256()
            with candidate.open("rb") as dependency_file:
                for block in iter(lambda: dependency_file.read(DOWNLOAD_CHUNK_SIZE), b""):
                    if stop_event is not None and stop_event.is_set():
                        raise RuntimeError("操作已取消")
                    digest.update(block)
            actual = base64.urlsafe_b64encode(digest.digest()).rstrip(b"=").decode("ascii")
            if not hmac.compare_digest(actual, encoded_digest):
                raise RuntimeError(f"依赖文件损坏：{row[0]}")
            verified += 1
    if verified < 8:
        raise RuntimeError("依赖安装记录不完整")
    return verified

def run_process_cancelable(
    command: list[str],
    stop_event: threading.Event | None,
    environment: dict[str, str] | None = None,
) -> tuple[int, str]:
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
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
    output: list[str] = []
    output_queue: queue.Queue = queue.Queue()

    def read_output() -> None:
        if process.stdout is None:
            return
        for line in iter(process.stdout.readline, ""):
            output_queue.put(line)

    threading.Thread(target=read_output, daemon=True).start()
    while process.poll() is None:
        while True:
            try:
                output.append(output_queue.get_nowait())
            except queue.Empty:
                break
        if stop_event is not None and stop_event.is_set():
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            return -1, "操作已取消"
        time.sleep(0.05)
    while True:
        try:
            output.append(output_queue.get_nowait())
        except queue.Empty:
            break
    return int(process.returncode or 0), "".join(output)


def ensure_numpy(download: bool, stop_event: threading.Event | None = None) -> bool:
    if download:
        probe_code, probe_output = run_process_cancelable(local_numpy_probe_command(SITE_PACKAGES), stop_event)
        if probe_code == 0:
            try:
                verify_installed_distribution("numpy", stop_event, SITE_PACKAGES)
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
            return False
        except Exception as first_error:
            raise RuntimeError("缺少或损坏的本地 NumPy 运行组件，请先点击“文件”。") from first_error
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
    process_environment = os.environ.copy()
    process_environment["TEMP"] = str(TEMP_DIR)
    process_environment["TMP"] = str(TEMP_DIR)
    process_environment["PIP_CACHE_DIR"] = str(TEMP_DIR / "pip-cache")
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--disable-pip-version-check",
        "--no-input",
        "--no-cache-dir",
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
    committed = False
    had_previous = SITE_PACKAGES.exists()
    try:
        code, output = run_process_cancelable(command, stop_event, process_environment)
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        if code != 0:
            ensure_code, ensure_output = run_process_cancelable(
                [sys.executable, "-m", "ensurepip", "--upgrade"],
                stop_event,
                process_environment,
            )
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            if ensure_code == 0:
                code, output = run_process_cancelable(command, stop_event, process_environment)
                if stop_event is not None and stop_event.is_set():
                    raise RuntimeError("操作已取消")
            else:
                output += "\n" + ensure_output
        if code != 0:
            log_text("运行组件安装失败:\n" + output[-12000:])
            raise RuntimeError("运行组件下载或安装失败，详情已写入日志。")
        probe_code, probe_output = run_process_cancelable(
            local_numpy_probe_command(staged_site_packages),
            stop_event,
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
            verify_installed_distribution("numpy", None, SITE_PACKAGES)
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

def checked_remote_url(value: str, base_url: str = "") -> str:
    candidate = urllib.parse.urljoin(base_url, value.strip())
    parsed = urllib.parse.urlsplit(candidate)
    if parsed.scheme not in ("https", "file"):
        raise ValueError("更新地址必须使用 HTTPS 或本地 file URL")
    if parsed.scheme == "https" and not parsed.netloc:
        raise ValueError("更新地址无效")
    return candidate


def open_remote(url: str, timeout: float):
    initial_url = checked_remote_url(url)
    request = urllib.request.Request(
        initial_url,
        headers={"User-Agent": f"{APP_NAME}/{APP_VERSION} Python/{sys.version_info.major}.{sys.version_info.minor}"},
    )
    response = urllib.request.urlopen(request, timeout=timeout)
    try:
        final_url = checked_remote_url(response.geturl(), initial_url)
        initial_scheme = urllib.parse.urlsplit(initial_url).scheme
        final_scheme = urllib.parse.urlsplit(final_url).scheme
        if initial_scheme == "https" and final_scheme != "https":
            raise ValueError("远程下载禁止从 HTTPS 降级")
        return response
    except Exception:
        response.close()
        raise


def read_remote_limited(url: str, limit: int, stop_event: threading.Event | None) -> bytes:
    result = bytearray()
    with open_remote(url, 25) as response:
        length_text = response.headers.get("Content-Length", "")
        if length_text.isdigit() and int(length_text) > limit:
            raise ValueError("远程文件超过允许大小")
        while True:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            block = response.read(min(DOWNLOAD_CHUNK_SIZE, limit + 1 - len(result)))
            if not block:
                break
            result.extend(block)
            if len(result) > limit:
                raise ValueError("远程文件超过允许大小")
    return bytes(result)


def safe_manifest_target(path_text: str) -> tuple[Path, Path]:
    stripped = path_text.strip()
    if path_text != stripped:
        raise ValueError("远程文件清单包含非法路径")
    normalized = stripped.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if not normalized or not pure.parts or pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError("远程文件清单包含非法路径")
    for part in pure.parts:
        stem = part.split(".", 1)[0].lower()
        if stem in WINDOWS_RESERVED_NAMES or part.endswith((" ", ".")) or WINDOWS_INVALID_NAME_PATTERN.search(part):
            raise ValueError("远程文件清单包含 Windows 非法文件名")
    relative = Path(*pure.parts)
    protected = {"config.json", "profiles.json", "anygameai.log", "integrity.json", "global_prior.npz"}
    lowered_parts = tuple(part.lower() for part in relative.parts)
    if (
        lowered_parts[0] in ("profiles", "backup")
        or lowered_parts[:2] == ("runtime", "site-packages")
        or relative.as_posix().lower() in protected
    ):
        raise ValueError("远程文件清单不能覆盖用户数据或本地依赖")
    root = APP_DIR.resolve()
    target = (APP_DIR / relative).resolve()
    if target != root and root not in target.parents:
        raise ValueError("远程文件清单包含越界路径")
    return relative, target


def download_verified_file(
    url: str,
    target: Path,
    expected_hash: str,
    expected_size: int | None,
    stop_event: threading.Event | None,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".download")
    digest = hashlib.sha256()
    total = 0
    try:
        with open_remote(url, 60) as response, temp.open("wb") as file:
            length_text = response.headers.get("Content-Length", "")
            if length_text.isdigit() and int(length_text) > MAX_REMOTE_FILE_BYTES:
                raise ValueError("下载文件超过允许大小")
            while True:
                if stop_event is not None and stop_event.is_set():
                    raise RuntimeError("操作已取消")
                block = response.read(DOWNLOAD_CHUNK_SIZE)
                if not block:
                    break
                total += len(block)
                if total > MAX_REMOTE_FILE_BYTES:
                    raise ValueError("下载文件超过允许大小")
                digest.update(block)
                file.write(block)
            file.flush()
            os.fsync(file.fileno())
        if expected_size is not None and total != expected_size:
            raise ValueError("下载文件大小校验失败")
        if digest.hexdigest().lower() != expected_hash:
            raise ValueError("下载文件哈希校验失败")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


def download_remote_files(config: dict, stop_event: threading.Event | None) -> tuple[int, bool]:
    configured_url = str(config.get("remote_manifest_url", "")).strip()
    if not configured_url:
        return 0, False
    manifest_url = checked_remote_url(configured_url)
    manifest_data = read_remote_limited(manifest_url, MAX_MANIFEST_BYTES, stop_event)
    manifest = json.loads(manifest_data.decode("utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("远程文件清单无效")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) > 512:
        raise ValueError("远程文件清单无效")
    entries = []
    seen_targets: set[Path] = set()
    for item in files:
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        if not isinstance(item, dict):
            raise ValueError("远程文件清单项目无效")
        relative, target = safe_manifest_target(str(item.get("path", "")))
        if target in seen_targets:
            raise ValueError("远程文件清单包含重复路径")
        seen_targets.add(target)
        expected = str(item.get("sha256", "")).strip().lower()
        if re.fullmatch(r"[0-9a-f]{64}", expected) is None:
            raise ValueError("远程文件清单包含非法校验值")
        size_value = item.get("size")
        if size_value is None:
            expected_size = None
        elif isinstance(size_value, bool) or not isinstance(size_value, int) or not 0 <= size_value <= MAX_REMOTE_FILE_BYTES:
            raise ValueError("远程文件清单包含非法文件大小")
        else:
            expected_size = size_value
        file_url_text = str(item.get("url", "")).strip()
        if not file_url_text:
            raise ValueError("远程文件清单包含空下载地址")
        file_url = checked_remote_url(file_url_text, manifest_url)
        if target.exists():
            try:
                if (expected_size is None or target.stat().st_size == expected_size) and sha256_file(target).lower() == expected:
                    continue
            except OSError:
                pass
        entries.append((relative, target, file_url, expected, expected_size))
    if not entries:
        return 0, False
    stage_root = RUNTIME_DIR / f".update-{os.getpid()}-{time.time_ns()}"
    files_root = stage_root / "files"
    rollback_root = stage_root / "rollback"
    committed: list[tuple[Path, Path | None]] = []
    restart_required = False
    try:
        for relative, target, file_url, expected, expected_size in entries:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            staged = files_root / relative
            download_verified_file(file_url, staged, expected, expected_size, stop_event)
            if target == LOCAL_SCRIPT_PATH.resolve():
                if not valid_script(staged):
                    raise ValueError("下载的主程序校验失败")
                downloaded_version = script_version(staged) or ()
                installed_version = script_version(LOCAL_SCRIPT_PATH) if LOCAL_SCRIPT_PATH.exists() else None
                if installed_version is not None and downloaded_version < installed_version:
                    raise ValueError("拒绝安装较旧的主程序")
        for relative, target, _, _, _ in entries:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            staged = files_root / relative
            backup = None
            moved_old = False
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    backup = rollback_root / relative
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(target, backup)
                    moved_old = True
                os.replace(staged, target)
                committed.append((target, backup))
                if target == LOCAL_SCRIPT_PATH.resolve():
                    restart_required = True
            except Exception:
                target.unlink(missing_ok=True)
                if moved_old and backup is not None and backup.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(backup, target)
                raise
        return len(entries), restart_required
    except Exception:
        for target, backup in reversed(committed):
            try:
                target.unlink(missing_ok=True)
                if backup is not None and backup.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(backup, target)
            except OSError:
                pass
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


if os.name == "nt":
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    SRCCOPY = 0x00CC0020
    CAPTUREBLT = 0x40000000
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


def esc_pressed() -> bool:
    return bool(user32.GetAsyncKeyState(ESC_VK) & 0x8000)


def wait_esc_release() -> None:
    while esc_pressed():
        time.sleep(0.03)


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
    _, _, width, height = window_capture_rect(window)
    return width >= 160 and height >= 120


def wait_for_target_window(stop_event: threading.Event, timeout: float = TARGET_WAIT_SECONDS) -> int:
    wait_esc_release()
    deadline = time.monotonic() + timeout
    candidate = 0
    stable = 0
    while time.monotonic() < deadline and not stop_event.is_set():
        if esc_pressed():
            return 0
        window = foreground_window()
        if usable_target_window(window):
            if window == candidate:
                stable += 1
            else:
                candidate = window
                stable = 1
            if stable >= 4:
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
    host_executables = {
        "chrome", "msedge", "firefox", "brave", "opera", "vivaldi",
        "retroarch", "pcsx2", "rpcs3", "dolphin", "dolphin-emu", "mame",
        "cemu", "yuzu", "ryujinx", "xenia", "ppssppwindows64",
        "java", "javaw", "python", "pythonw", "electron", "nw", "nwjs",
    }
    game_title = stable_game_title(title)
    identity_title = stable_identity_title(title)
    use_title = executable_name in host_executables or not executable
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
        self.buffer = ctypes.create_string_buffer(self.width * self.height * 4)
        self.info = BITMAPINFO()
        self.info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.info.bmiHeader.biWidth = self.width
        self.info.bmiHeader.biHeight = -self.height
        self.info.bmiHeader.biPlanes = 1
        self.info.bmiHeader.biBitCount = 32
        self.info.bmiHeader.biCompression = 0
        self.info.bmiHeader.biSizeImage = self.width * self.height * 4

    def _capture_from_dc(self, source_dc, x: int, y: int, source_width: int, source_height: int) -> bytes:
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
        target = 0
        for source in range(0, len(raw), 4):
            b = raw[source]
            g = raw[source + 1]
            r = raw[source + 2]
            gray[target] = (r * 77 + g * 150 + b * 29) >> 8
            target += 1
        return bytes(gray)

    def capture_gray(self) -> bytes:
        x, y, source_width, source_height = window_capture_rect(self.window)
        screen_frame = self._capture_from_dc(self.screen_dc, x, y, source_width, source_height)
        screen_contrast = max(screen_frame) - min(screen_frame)
        if screen_contrast >= 3:
            return screen_frame
        window_dc = user32.GetDC(self.window)
        if not window_dc:
            return screen_frame
        try:
            window_frame = self._capture_from_dc(window_dc, 0, 0, source_width, source_height)
        except Exception:
            return screen_frame
        finally:
            user32.ReleaseDC(self.window, window_dc)
        if max(window_frame) - min(window_frame) > screen_contrast:
            return window_frame
        return screen_frame

    def close(self) -> None:
        try:
            gdi32.SelectObject(self.memory_dc, self.old_object)
            gdi32.DeleteObject(self.bitmap)
            gdi32.DeleteDC(self.memory_dc)
            user32.ReleaseDC(0, self.screen_dc)
        except Exception:
            pass


def cursor_position() -> tuple[int, int]:
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return int(point.x), int(point.y)


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
    items = [keyboard_input(vk, True) for vk in SAFE_KEY_VKS]
    items.extend(
        [
            mouse_input(flags=MOUSEEVENTF_LEFTUP),
            mouse_input(flags=MOUSEEVENTF_RIGHTUP),
            mouse_input(flags=MOUSEEVENTF_MIDDLEUP),
            mouse_input(flags=MOUSEEVENTF_XUP, data=XBUTTON1),
            mouse_input(flags=MOUSEEVENTF_XUP, data=XBUTTON2),
        ]
    )
    for start in range(0, len(items), 48):
        try:
            send_inputs(items[start:start + 48])
        except Exception:
            pass


def normalized_action(action: dict) -> dict:
    keys = sorted({int(value) for value in action.get("keys", []) if int(value) in SAFE_KEY_VKS})[:6]
    dangerous_combinations = (
        {0x12, 0x73},
        {0x12, 0x09},
        {0x11, 0x12, 0x2E},
        {0x12, 0x20},
    )
    if any(combination.issubset(keys) for combination in dangerous_combinations):
        keys = []
    buttons = [name for name in ("left", "right", "middle", "x1", "x2") if name in action.get("buttons", [])]
    dx = int(max(-1, min(1, int(action.get("mouse_dx", 0)))))
    dy = int(max(-1, min(1, int(action.get("mouse_dy", 0)))))
    wheel = int(max(-1, min(1, int(action.get("mouse_wheel", 0)))))
    mouse_x = int(action.get("mouse_x", -1))
    mouse_y = int(action.get("mouse_y", -1))
    if not 0 <= mouse_x < MOUSE_GRID_WIDTH or not 0 <= mouse_y < MOUSE_GRID_HEIGHT:
        mouse_x = -1
        mouse_y = -1
    if mouse_x >= 0:
        dx = 0
        dy = 0
    return {
        "keys": keys,
        "buttons": buttons,
        "mouse_dx": dx,
        "mouse_dy": dy,
        "mouse_wheel": wheel,
        "mouse_x": mouse_x,
        "mouse_y": mouse_y,
    }

def universal_actions() -> list[dict]:
    raw_actions: list[dict] = [{}]
    movement_sets = (
        [0x57], [0x41], [0x53], [0x44],
        [0x26], [0x25], [0x28], [0x27],
        [0x57, 0x41], [0x57, 0x44], [0x53, 0x41], [0x53, 0x44],
        [0x26, 0x25], [0x26, 0x27], [0x28, 0x25], [0x28, 0x27],
    )
    raw_actions.extend({"keys": keys} for keys in movement_sets)
    common_keys = (
        0x20, 0x0D, 0x10, 0x11, 0x09,
        0x45, 0x46, 0x51, 0x52, 0x54, 0x47,
        0x5A, 0x58, 0x43, 0x56, 0x42, 0x4E, 0x4D,
        0x48, 0x4A, 0x4B, 0x4C, 0x50, 0x55, 0x49, 0x4F, 0x59,
    )
    raw_actions.extend({"keys": [key]} for key in common_keys)
    raw_actions.extend({"keys": [key]} for key in range(0x30, 0x3A))
    for movement in ([0x57], [0x41], [0x53], [0x44], [0x26], [0x25], [0x28], [0x27]):
        raw_actions.append({"keys": movement + [0x10]})
    for movement in ([0x57], [0x41], [0x53], [0x44]):
        raw_actions.append({"keys": movement + [0x11]})
    for movement in ([0x57], [0x41], [0x53], [0x44], [0x26], [0x25], [0x28], [0x27]):
        raw_actions.append({"keys": movement + [0x20]})
    for modifier in (0x45, 0x46, 0x51, 0x52):
        for movement in ([0x57], [0x41], [0x53], [0x44]):
            raw_actions.append({"keys": movement + [modifier]})
    for key in range(0x70, 0x78):
        raw_actions.append({"keys": [key]})
    for movement in ([0x57], [0x41], [0x53], [0x44], [0x26], [0x25], [0x28], [0x27]):
        raw_actions.append({"keys": movement, "buttons": ["left"]})
    pointer_directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))
    for dx, dy in pointer_directions:
        raw_actions.append({"mouse_dx": dx, "mouse_dy": dy})
    for dx, dy in pointer_directions:
        raw_actions.append({"buttons": ["left"], "mouse_dx": dx, "mouse_dy": dy})
    raw_actions.extend(({"buttons": ["left"]}, {"buttons": ["right"]}, {"mouse_wheel": 1}, {"mouse_wheel": -1}))
    click_columns = (4, 10, 16, 22, 28)
    click_rows = (3, 9, 15)
    for mouse_y in click_rows:
        for mouse_x in click_columns:
            raw_actions.append({"buttons": ["left"], "mouse_x": mouse_x, "mouse_y": mouse_y})
    for mouse_x, mouse_y in ((16, 9), (8, 5), (24, 5), (8, 13), (24, 13)):
        raw_actions.append({"buttons": ["right"], "mouse_x": mouse_x, "mouse_y": mouse_y})
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
    added = 0
    for action in universal_actions():
        if len(actions) >= max(1, int(limit)):
            break
        signature = action_signature(action)
        if signature in existing:
            continue
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
    caps = {"idle": 1, "keyboard": 12, "pointer": 4, "click": 5, "wheel": 0, "mixed": 2}
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


def frame_hash_distance(left: str, right: str) -> int:
    try:
        return (int(left, 16) ^ int(right, 16)).bit_count()
    except (TypeError, ValueError):
        return 64


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


def observe_human_action(target: int, previous_cursor: tuple[int, int], mouse_threshold: int = 3) -> tuple[dict, tuple[int, int]]:
    keys = [vk for vk in SAFE_KEY_VKS if user32.GetAsyncKeyState(vk) & 0x8001]
    buttons = [name for name, vk in MOUSE_VKS.items() if user32.GetAsyncKeyState(vk) & 0x8001]
    current = cursor_position()
    dx_raw = current[0] - previous_cursor[0]
    dy_raw = current[1] - previous_cursor[1]
    dx = 0 if abs(dx_raw) < mouse_threshold else (1 if dx_raw > 0 else -1)
    dy = 0 if abs(dy_raw) < mouse_threshold else (1 if dy_raw > 0 else -1)
    mouse_x = -1
    mouse_y = -1
    if buttons:
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
            "mouse_wheel": 0,
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
    try:
        send_inputs(down)
        if down and not sleep_cancelable(max(0.01, min(0.35, float(hold_seconds))), stop_event, target):
            return False
        return True
    finally:
        send_inputs(up)


def make_feature(current: bytes, previous: bytes | None) -> bytes:
    if len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面特征尺寸无效")
    if previous is None or len(previous) != len(current):
        difference = bytes(len(current))
    else:
        difference = bytes(abs(a - b) for a, b in zip(current, previous))
    return current + difference


def feature_motion(feature: bytes) -> float:
    difference = feature[FEATURE_WIDTH * FEATURE_HEIGHT:]
    return sum(difference) / max(1, len(difference)) / 255.0


def frame_hash(gray: bytes) -> str:
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
    return f"{bits:016x}"



def state_key(gray: bytes, feature: bytes) -> str:
    motion = feature_motion(feature)
    brightness = sum(gray) / max(1, len(gray)) / 255.0
    motion_bucket = max(0, min(31, int(motion * 96.0)))
    brightness_bucket = max(0, min(15, int(brightness * 16.0)))
    return f"{frame_hash(gray)}:{motion_bucket:02x}:{brightness_bucket:x}"


def memory_state_key(gray: bytes, feature: bytes) -> str:
    digest = int(frame_hash(gray), 16)
    folded = (digest ^ (digest >> 32)) & 0xFFFFFFFF
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


def profile_paths(profile_id: str) -> dict[str, Path]:
    if not valid_profile_id(profile_id):
        raise ValueError("游戏档案标识无效")
    root = PROFILES_DIR / profile_id
    return {
        "root": root,
        "profile": root / "profile.json",
        "db": root / "experience.sqlite3",
        "model": root / "model.npz",
    }


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
        "transitions": {},
        "trained_samples": 0,
        "training_rounds": 0,
        "human_sessions": 0,
        "ai_sessions": 0,
        "ai_reward_ema": 0.0,
        "last_ai_mean_reward": 0.0,
        "control_reward_ema": {kind: 0.0 for kind in CONTROL_KINDS},
        "control_reward_counts": {kind: 0 for kind in CONTROL_KINDS},
        "passive_motion_ema": 0.0,
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
    profile["action_origins"] = cleaned_origins
    profile["universal_action_schema"] = UNIVERSAL_ACTION_SCHEMA
    profile["transitions"] = cleaned_transitions
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
    try:
        passive_motion = float(profile.get("passive_motion_ema", 0.0) or 0.0)
    except (TypeError, ValueError):
        passive_motion = 0.0
    if not math.isfinite(passive_motion):
        passive_motion = 0.0
    profile["passive_motion_ema"] = max(0.0, min(1.0, passive_motion))


def migrate_profile(data: object, profile_id: str) -> dict | None:
    if not isinstance(data, dict) or data.get("id") != profile_id:
        return None
    if data.get("schema") not in (2, 3, 4, 5, 6, 7, 8, PROFILE_SCHEMA):
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
        if not directory.is_dir() or not valid_profile_id(directory.name):
            continue
        try:
            candidate = json.loads((directory / "profile.json").read_text(encoding="utf-8"))
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
        candidate = json.loads(paths["profile"].read_text(encoding="utf-8"))
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


def ensure_database(path: Path) -> None:
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
            connection.commit()
        finally:
            connection.close()
    except Exception:
        backup_corrupt(path)
        remove_sqlite_sidecars(path)
        connection = sqlite3.connect(path, timeout=20)
        try:
            connection.execute("PRAGMA journal_mode=WAL")
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
            connection.commit()
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


def compact_state_values(path: Path, limit: int, action_count: int) -> dict:
    ensure_database(path)
    limit = max(1, int(limit))
    connection = sqlite3.connect(path, timeout=60)
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
    finally:
        connection.close()

def compress_feature(feature: bytes) -> bytes:
    return zlib.compress(feature, level=3)


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


def compact_experience(path: Path, limit: int, action_count: int) -> dict:
    ensure_database(path)
    connection = sqlite3.connect(path, timeout=60)
    try:
        before = int(connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0])
        connection.execute(
            "DELETE FROM samples WHERE feature_dim<>? OR action<0 OR action>=? OR length(feature)>? "
            "OR reward IS NULL OR reward<-1.0001 OR reward>1.0001",
            (FEATURE_DIM, action_count, MAX_COMPRESSED_FEATURE_BYTES),
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
        except sqlite3.DatabaseError:
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


def record_transition(profile: dict, previous: int, current: int) -> None:
    if previous == current or not (0 <= previous < len(profile["actions"])) or not (0 <= current < len(profile["actions"])):
        return
    transitions = profile.setdefault("transitions", {})
    next_map = transitions.setdefault(str(previous), {})
    next_map[str(current)] = min(1_000_000_000, int(next_map.get(str(current), 0)) + 1)


def record_action_duration(profile: dict, action_index: int, duration_seconds: float) -> None:
    ensure_action_metadata(profile)
    if not 0 <= action_index < len(profile["actions"]):
        return
    duration = max(0.02, min(1.5, float(duration_seconds)))
    count = int(profile["action_duration_counts"][action_index])
    old = float(profile["action_hold_seconds"][action_index])
    weight = min(64, count)
    profile["action_hold_seconds"][action_index] = (old * weight + duration) / (weight + 1)
    profile["action_duration_counts"][action_index] = min(1_000_000_000, count + 1)


def learned_action_hold(profile: dict, action_index: int, configured_hold: float) -> float:
    ensure_action_metadata(profile)
    learned = float(profile["action_hold_seconds"][action_index])
    count = int(profile["action_duration_counts"][action_index])
    confidence = min(0.8, count / 20.0)
    value = configured_hold * (1.0 - confidence) + learned * confidence
    return max(0.02, min(0.65, value))


def update_action_reward(profile: dict, action_index: int, reward: float) -> None:
    ensure_action_metadata(profile)
    if not 0 <= action_index < len(profile["actions"]):
        return
    bounded = max(-1.0, min(1.0, float(reward)))
    count = int(profile["action_reward_counts"][action_index])
    previous = float(profile["action_reward_ema"][action_index])
    alpha = max(0.02, 1.0 / min(64, count + 1))
    profile["action_reward_ema"][action_index] = previous + alpha * (bounded - previous)
    profile["action_reward_counts"][action_index] = min(1_000_000_000, count + 1)


def emit_delayed_experience(profile: dict, item: dict, rows: list) -> float:
    weight = max(1e-8, float(item.get("weight_sum", 1.0)))
    reward = max(-1.0, min(1.0, float(item.get("reward_sum", 0.0)) / weight))
    action_index = int(item["action"])
    rows.append(
        (
            str(item["created_at"]),
            "ai",
            action_index,
            reward,
            FEATURE_DIM,
            compress_feature(item["feature"]),
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


def transition_distribution(np, profile: dict, previous_action: int | None, action_count: int):
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
    counts /= counts.sum()
    return counts


def feature_vector(np, feature: bytes):
    if len(feature) != FEATURE_DIM:
        raise ValueError("画面特征尺寸无效")
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    raw = np.frombuffer(feature, dtype=np.uint8).astype(np.float32) / 255.0
    image = raw[:pixels].reshape(FEATURE_HEIGHT, FEATURE_WIDTH)
    difference = raw[pixels:].reshape(FEATURE_HEIGHT, FEATURE_WIDTH)
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
        ],
        dtype=np.float32,
    )
    result = np.concatenate(
        (
            appearance.reshape(-1),
            temporal.reshape(-1),
            edges.reshape(-1),
            global_features,
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
        with np.load(path, allow_pickle=False) as data:
            schema = int(data["schema"][0])
            if schema not in (4, MODEL_SCHEMA):
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
                "action_hash": str(data["action_hash"][0]),
                "action_signatures": (
                    [str(value) for value in data["action_signatures"].tolist()]
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
            if len(loaded["action_signatures"]) != loaded["output_size"] or len(set(loaded["action_signatures"])) != loaded["output_size"]:
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
                "action_signatures": [str(value) for value in data["action_signatures"].tolist()],
                "Wp": data["Wp"].astype(np.float32, copy=True),
                "bp": data["bp"].astype(np.float32, copy=True),
                "Wv": data["Wv"].astype(np.float32, copy=True),
                "bv": data["bv"].astype(np.float32, copy=True),
                "trained_samples": int(data["trained_samples"][0]),
                "training_rounds": int(data["training_rounds"][0]),
                "source_profile": str(data["source_profile"][0]),
            }
        if prior["schema"] not in (3, GLOBAL_PRIOR_SCHEMA):
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
        if loaded_input_dim < FEATURE_WIDTH * FEATURE_HEIGHT * MODEL_PIXEL_CHANNELS or hidden2 != second_hidden_size(hidden_size):
            raise ValueError("通用先验结构无效")
        if action_count < 1 or action_count > 1024 or len(set(prior["action_signatures"])) != action_count:
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


def save_global_prior(np, model: dict, action_list: list[dict], source_profile: str) -> None:
    GLOBAL_PRIOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = GLOBAL_PRIOR_PATH.with_name(GLOBAL_PRIOR_PATH.name + ".tmp")
    signatures = [action_signature(action) for action in action_list]
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
    os.replace(temp, GLOBAL_PRIOR_PATH)


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
            candidate = json.loads(paths["profile"].read_text(encoding="utf-8"))
            profile = migrate_profile(candidate, profile_id)
            if profile is None:
                continue
            total_count, human_count = count_samples(paths["db"])
            if human_count < 8 and total_count < 48:
                continue
            action_scores: dict[int, float] = {}
            connection = sqlite3.connect(paths["db"], timeout=20)
            try:
                for action_index, score_value in connection.execute(
                    "SELECT action, SUM(CASE WHEN source='human' THEN 4.0 "
                    "WHEN reward>0.05 THEN 0.5+reward*2.5 ELSE 0.0 END) "
                    "FROM samples GROUP BY action"
                ):
                    action_scores[int(action_index)] = max(0.0, float(score_value or 0.0))
            finally:
                connection.close()
            for action_index, action in enumerate(profile["actions"]):
                signature = action_signature(action)
                signature_actions.setdefault(signature, normalized_action(action))
                origin = profile.get("action_origins", [])[action_index] if action_index < len(profile.get("action_origins", [])) else "human"
                base_score = 0.15 if origin == "generic" else 0.35
                signature_scores[signature] = signature_scores.get(signature, 0.0) + base_score + action_scores.get(action_index, 0.0)
            candidates.append((profile_id, profile, paths))
        except Exception:
            log_text(f"读取通用训练候选 {profile_id} 失败：\n" + traceback.format_exc())
    if not candidates or not signature_actions:
        return False
    action_limit = min(512, max(64, int(config["max_action_count"]) * 4))
    ordered_signatures = sorted(signature_actions, key=lambda value: (-signature_scores.get(value, 0), value))[:action_limit]
    global_actions = [signature_actions[signature] for signature in ordered_signatures]
    global_indices = {signature: index for index, signature in enumerate(ordered_signatures)}
    global_sample_limit = min(60_000, max(4_000, int(config["train_sample_limit_per_game"]) * 2))
    per_profile_limit = max(256, min(int(config["train_sample_limit_per_game"]), math.ceil(global_sample_limit / len(candidates))))
    x_parts = []
    y_parts = []
    policy_parts = []
    value_target_parts = []
    value_weight_parts = []
    used_profiles = 0
    for profile_id, profile, paths in candidates:
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        try:
            x, y, policy_weights, value_targets, value_weights, invalid = load_training_data(
                np,
                paths["db"],
                len(profile["actions"]),
                per_profile_limit,
                stop_event,
            )
            if x is None:
                continue
            mapping = np.full(len(profile["actions"]), -1, dtype=np.int64)
            for action_index, action in enumerate(profile["actions"]):
                mapping[action_index] = global_indices.get(action_signature(action), -1)
            mapped = mapping[y]
            valid = mapped >= 0
            if not bool(valid.any()):
                continue
            x = x[valid]
            mapped = mapped[valid]
            policy_weights = policy_weights[valid]
            value_targets = value_targets[valid]
            value_weights = value_weights[valid]
            fairness = min(2.5, max(0.65, math.sqrt(per_profile_limit / max(1, len(x)))))
            x_parts.append(x)
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
    if not x_parts:
        return False
    x = np.concatenate(x_parts, axis=0)
    y = np.concatenate(y_parts, axis=0)
    policy_weights = np.concatenate(policy_parts, axis=0)
    value_targets = np.concatenate(value_target_parts, axis=0)
    value_weights = np.concatenate(value_weight_parts, axis=0)
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
        max(2, min(int(config["training_epochs"]), max(3, int(config["training_epochs"]) // 2))),
        int(config["training_batch_size"]),
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
    temp = path.with_name(path.name + ".tmp")
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
            action_hash=np.array([model.get("action_hash", "")]),
            action_signatures=np.asarray(signatures),
            updated_at=np.array([now_text()]),
        )
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, path)


def model_outputs(np, model: dict, feature: bytes):
    x = feature_vector(np, feature)
    hidden1 = np.maximum(0.0, x @ model["W1"] + model["b1"])
    hidden2 = np.maximum(0.0, hidden1 @ model["W2"] + model["b2"])
    logits = hidden2 @ model["Wp"] + model["bp"]
    logits -= float(logits.max())
    probabilities = np.exp(logits)
    probabilities /= max(1e-8, float(probabilities.sum()))
    values = np.tanh(hidden2 @ model["Wv"] + model["bv"])
    return probabilities, values


def choose_policy_action(
    np,
    probabilities,
    values,
    transition_prior,
    exploration: float,
    recent_actions: list[int],
    static_streak: int,
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
    scores = (scores - float(scores.max())) / temperature
    weights = np.exp(scores)
    weights /= max(1e-12, float(weights.sum()))
    dynamic_exploration = min(0.65, exploration + min(0.48, static_streak * 0.05))
    if random.random() < dynamic_exploration:
        sampling = np.sqrt(np.maximum(weights, 1e-12))
        sampling /= sampling.sum()
        return int(np.random.choice(action_count, p=sampling))
    return int(np.argmax(weights))


def reservoir_add(bucket: list, value, seen_count: int, capacity: int) -> None:
    if len(bucket) < capacity:
        bucket.append(value)
        return
    position = random.randrange(seen_count)
    if position < capacity:
        bucket[position] = value


def load_training_data(np, db_path: Path, action_count: int, sample_limit: int, stop_event: threading.Event | None):
    ensure_database(db_path)
    per_action = max(32, math.ceil(sample_limit / max(1, action_count)))
    human_capacity = max(24, int(per_action * 0.78))
    ai_capacity = max(8, per_action - human_capacity)
    buckets: dict[tuple[str, int], list] = {}
    seen: dict[tuple[str, int], int] = {}
    invalid = 0
    invalid_ids: list[int] = []
    connection = sqlite3.connect(db_path, timeout=30)
    try:
        cursor = connection.execute("SELECT id, source, action, reward, feature_dim, feature FROM samples ORDER BY id")
        for sample_id, source, action, reward, feature_dim, blob in cursor:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            action = int(action)
            try:
                reward_value = float(reward)
            except (TypeError, ValueError):
                reward_value = math.nan
            if (
                int(feature_dim) != FEATURE_DIM
                or not (0 <= action < action_count)
                or source not in ("human", "ai")
                or not math.isfinite(reward_value)
                or not -1.0001 <= reward_value <= 1.0001
            ):
                invalid += 1
                invalid_ids.append(int(sample_id))
                continue
            try:
                feature = decompress_feature(blob, FEATURE_DIM)
            except Exception:
                invalid += 1
                invalid_ids.append(int(sample_id))
                continue
            key = (source, action)
            seen[key] = seen.get(key, 0) + 1
            capacity = human_capacity if source == "human" else ai_capacity
            reservoir_add(buckets.setdefault(key, []), (feature, action, reward_value, source), seen[key], capacity)
    finally:
        if invalid_ids:
            for offset in range(0, len(invalid_ids), 500):
                connection.executemany(
                    "DELETE FROM samples WHERE id=?",
                    ((sample_id,) for sample_id in invalid_ids[offset:offset + 500]),
                )
            connection.commit()
        connection.close()
    samples = [item for bucket in buckets.values() for item in bucket]
    if len(samples) > sample_limit:
        random.shuffle(samples)
        samples = samples[:sample_limit]
    random.shuffle(samples)
    if not samples:
        return None, None, None, None, None, invalid
    x = np.empty((len(samples), MODEL_INPUT_DIM), dtype=np.float32)
    y = np.empty(len(samples), dtype=np.int64)
    policy_weights = np.empty(len(samples), dtype=np.float32)
    value_targets = np.empty(len(samples), dtype=np.float32)
    value_weights = np.empty(len(samples), dtype=np.float32)
    counts: dict[int, int] = {}
    for _, action, _, _ in samples:
        counts[action] = counts.get(action, 0) + 1
    mean_count = sum(counts.values()) / max(1, len(counts))
    for index, (feature, action, reward, source) in enumerate(samples):
        x[index] = feature_vector(np, feature)
        y[index] = action
        class_weight = min(3.0, max(0.55, (mean_count / max(1, counts[action])) ** 0.5))
        if source == "human":
            policy_weights[index] = class_weight
            value_targets[index] = 0.85
            value_weights[index] = 0.25
        else:
            bounded_reward = max(-1.0, min(1.0, reward))
            positive_reward = max(0.0, bounded_reward)
            policy_weights[index] = (
                0.0
                if positive_reward < 0.02
                else class_weight * min(0.55, 0.05 + positive_reward * 0.50)
            )
            value_targets[index] = bounded_reward
            value_weights[index] = 1.0
    return x, y, policy_weights, value_targets, value_weights, invalid

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
    order = np.arange(sample_count)
    np.random.shuffle(order)
    split = max(1, int(sample_count * 0.1)) if sample_count >= 40 else 0
    if split:
        validation_indices = order[-split:].copy()
        train_indices = order[:-split].copy()
    else:
        validation_indices = np.array([], dtype=np.int64)
        train_indices = order.copy()
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
        chosen_probabilities = probabilities[np.arange(len(indices)), eval_y]
        eval_policy_weights = policy_weights[indices].astype(np.float64, copy=False)
        policy_total = float(eval_policy_weights.sum())
        predictions = np.argmax(probabilities, axis=1)
        if policy_total > 1e-8:
            policy_loss = float(((-np.log(chosen_probabilities + 1e-8)) * eval_policy_weights).sum() / policy_total)
            accuracy = float(((predictions == eval_y) * eval_policy_weights).sum() / policy_total)
        else:
            policy_loss = 0.0
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
            policy_total = max(1e-6, float(batch_policy_weights.sum()))
            gradient_logits = probabilities.copy()
            label_smoothing = 0.015 if model["output_size"] > 1 else 0.0
            if label_smoothing:
                gradient_logits -= label_smoothing / model["output_size"]
                gradient_logits[np.arange(len(indices)), batch_y] -= 1.0 - label_smoothing
            else:
                gradient_logits[np.arange(len(indices)), batch_y] -= 1.0
            gradient_logits *= (batch_policy_weights / policy_total)[:, None]
            gradient_wp = hidden2.T @ gradient_logits + 1e-5 * model["Wp"]
            gradient_bp = gradient_logits.sum(axis=0)
            gradient_hidden2 = gradient_logits @ model["Wp"].T

            raw_values = hidden2 @ model["Wv"] + model["bv"]
            values = np.tanh(raw_values)
            chosen_values = values[np.arange(len(indices)), batch_y]
            value_errors = chosen_values - batch_value_targets
            value_total = max(1e-6, float(batch_value_weights.sum()))
            gradient_values = np.zeros_like(values)
            gradient_values[np.arange(len(indices)), batch_y] = (
                0.70 * 2.0 * value_errors * batch_value_weights / value_total
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
    actions = universal_actions()
    if not actions or len(actions) > UNIVERSAL_ACTION_LIMIT:
        raise RuntimeError("通用动作集自检失败")
    signatures = [action_signature(action) for action in actions]
    if len(signatures) != len(set(signatures)):
        raise RuntimeError("通用动作集包含重复项")
    if any(ESC_VK in action["keys"] for action in actions):
        raise RuntimeError("通用动作集包含安全退出键")
    probe_profile = default_profile({"id": "self-check", "name": "self-check"})
    ensure_action_metadata(probe_profile)
    probe_actions = cold_start_probe_actions(probe_profile, {})
    if not probe_actions or len(probe_actions) > COLD_START_PROBE_LIMIT:
        raise RuntimeError("通用控制探测自检失败")
    update_control_response(probe_profile, probe_actions[0], 0.25)
    evidence = control_response_evidence(probe_profile)
    if set(evidence) != set(CONTROL_KINDS) or not all(math.isfinite(value) for value in evidence.values()):
        raise RuntimeError("控制反馈自检失败")
    pixel_count = FEATURE_WIDTH * FEATURE_HEIGHT
    current = bytes((index * 37 + 19) & 0xFF for index in range(pixel_count))
    previous = bytes((index * 17 + 7) & 0xFF for index in range(pixel_count))
    feature = make_feature(current, previous)
    memory_key = memory_state_key(current, feature)
    if STATE_MEMORY_KEY_PATTERN.fullmatch(memory_key) is None:
        raise RuntimeError("场景记忆键自检失败")
    memory: dict[tuple[str, int], tuple[float, int]] = {}
    update_state_value_memory(memory, (memory_key, 0), 0.5, 0.16)
    if memory.get((memory_key, 0), (0.0, 0))[1] != 1:
        raise RuntimeError("场景记忆更新自检失败")
    if decompress_feature(compress_feature(feature), FEATURE_DIM) != feature:
        raise RuntimeError("经验压缩自检失败")
    vector = feature_vector(np, feature)
    if vector.shape != (MODEL_INPUT_DIM,) or not np.isfinite(vector).all():
        raise RuntimeError("视觉特征自检失败")
    model = initialize_model(np, MODEL_INPUT_DIM, 24, len(actions))
    model["action_signatures"] = signatures
    model["action_hash"] = actions_hash(actions)
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
    if not path.exists():
        return True
    np = import_numpy()
    model, changed = load_model(
        np,
        path,
        MODEL_INPUT_DIM,
        int(config["hidden_size"]),
        len(profile["actions"]),
        profile["actions"],
    )
    if changed:
        save_model(np, path, model)
    return True


def repair_profile(profile_id: str, config: dict) -> dict:
    paths = profile_paths(profile_id)
    repaired = 0
    removed = 0
    try:
        candidate = json.loads(paths["profile"].read_text(encoding="utf-8"))
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
        ensure_database(paths["db"])
    except Exception:
        repaired += 1
        ensure_database(paths["db"])
    result = compact_experience(
        paths["db"],
        int(config["experience_limit_per_game"]),
        len(profile["actions"]),
    )
    removed += result["removed"]
    memory_result = compact_state_values(
        paths["db"],
        int(config["state_memory_limit_per_game"]),
        len(profile["actions"]),
    )
    removed += memory_result["removed"]
    try:
        validate_model_file(paths["model"], profile, config)
    except Exception:
        backup_corrupt(paths["model"])
        repaired += 1
    return {
        "repaired": repaired,
        "removed": removed,
        "records": result["records"],
        "memory_records": memory_result["records"],
    }


def ensure_files(stop_event: threading.Event | None, download: bool) -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    repaired = 0
    downloaded = 0
    removed = 0
    records = 0
    memory_records = 0
    restart_required = False
    removed += cleanup_temporary_files()
    main_repaired, main_restart = repair_main_script()
    repaired += main_repaired
    restart_required = restart_required or main_restart
    config = load_config()
    index = load_index()
    profile_ids = set(index.get("profiles", {}))
    for directory in PROFILES_DIR.iterdir():
        if directory.is_dir() and valid_profile_id(directory.name):
            profile_ids.add(directory.name)
    if ensure_numpy(download=download, stop_event=stop_event):
        downloaded += 1
    np = import_numpy()
    runtime_self_check(np)
    prior_existed = GLOBAL_PRIOR_PATH.exists()
    if prior_existed and load_global_prior(np) is None:
        repaired += 1
    for profile_id in sorted(profile_ids):
        if stop_event is not None and stop_event.is_set():
            break
        result = repair_profile(profile_id, config)
        repaired += result["repaired"]
        removed += result["removed"]
        records += result["records"]
        memory_records += result["memory_records"]
    _, index_changed = sync_profile_index(index)
    repaired += index_changed
    if download and not (stop_event is not None and stop_event.is_set()):
        try:
            remote_changed, remote_restart = download_remote_files(config, stop_event)
            downloaded += remote_changed
            restart_required = restart_required or remote_restart
            if remote_restart and valid_script(LOCAL_SCRIPT_PATH):
                refresh_script_backup(LOCAL_SCRIPT_PATH)
        except RuntimeError:
            raise
        except Exception as error:
            log_text("远程文件更新失败: " + repr(error))
            return {
                "repaired": repaired,
                "downloaded": downloaded,
                "removed": removed,
                "records": records,
                "memory_records": memory_records,
                "restart_required": restart_required,
                "remote_error": str(error),
            }
    return {
        "repaired": repaired,
        "downloaded": downloaded,
        "removed": removed,
        "records": records,
        "memory_records": memory_records,
        "restart_required": restart_required,
    }


def record_human_session(target: int, stop_event: threading.Event) -> str:
    config = load_config()
    identity = profile_identity(target)
    profile, paths = load_or_create_profile(identity)
    ensure_action_metadata(profile)
    interval = max(0.04, min(0.25, float(config["sample_interval_seconds"])))
    max_actions = max(8, int(config["max_action_count"]))
    state_memory_limit = max(1000, int(config["state_memory_limit_per_game"]))
    state_memory = load_state_value_memory(paths["db"], max_actions, state_memory_limit)
    dirty_state_values: set[tuple[str, int]] = set()
    sampler = ScreenSampler(target)
    previous_frame = None
    previous_cursor = cursor_position()
    rows = []
    recorded = 0
    captured = 0
    idle_streak = 0
    new_actions = 0
    black_frames = 0
    last_action_index: int | None = None
    last_recorded_action: int | None = None
    last_recorded_digest = ""
    duplicate_streak = 0
    action_started = time.monotonic()
    try:
        while not stop_event.is_set():
            if esc_pressed() or not window_exists(target):
                break
            if foreground_window() != target:
                time.sleep(0.08)
                previous_frame = None
                previous_cursor = cursor_position()
                if last_action_index is not None:
                    record_action_duration(profile, last_action_index, time.monotonic() - action_started)
                    last_action_index = None
                action_started = time.monotonic()
                continue
            started = time.monotonic()
            action, previous_cursor = observe_human_action(target, previous_cursor)
            current = sampler.capture_gray()
            captured += 1
            black = max(current) - min(current) < 3
            if black:
                black_frames += 1
            feature = make_feature(current, previous_frame)
            previous_frame = current
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
                record_transition(profile, last_action_index, action_index)
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
            if not black:
                memory_key = (memory_state_key(current, feature), action_index)
                update_state_value_memory(state_memory, memory_key, 0.18 if idle else 0.88, 0.30)
                dirty_state_values.add(memory_key)
                if len(dirty_state_values) >= 256:
                    save_state_value_memory(paths["db"], state_memory, dirty_state_values)
            digest = frame_hash(current)
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
                rows.append((now_text(), "human", action_index, 1.0, FEATURE_DIM, compress_feature(feature)))
                recorded += 1
                last_recorded_action = action_index
                last_recorded_digest = digest
                profile["needs_training"] = True
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
            delay = interval - (time.monotonic() - started)
            if delay > 0:
                time.sleep(delay)
    finally:
        if last_action_index is not None:
            record_action_duration(profile, last_action_index, time.monotonic() - action_started)
        if rows:
            insert_samples(paths["db"], rows)
        save_state_value_memory(paths["db"], state_memory, dirty_state_values)
        sampler.close()
        profile["human_sessions"] = int(profile.get("human_sessions", 0)) + int(recorded > 0)
        save_profile(profile, paths)
        compact_experience(paths["db"], int(config["experience_limit_per_game"]), len(profile["actions"]))
        compact_state_values(paths["db"], state_memory_limit, len(profile["actions"]))
        wait_esc_release()
    warning = "；画面可能未被正确采集" if black_frames > max(20, captured // 2) else ""
    return f"人玩结束：{profile['name']}；记录 {recorded} 条；新增动作 {new_actions} 个{warning}"


def train_all_profiles(stop_event: threading.Event) -> str:
    ensure_numpy(download=False, stop_event=stop_event)
    np = import_numpy()
    config = load_config()
    index, _ = sync_profile_index(load_index())
    if not index.get("profiles"):
        return "没有可升级的游戏；请先使用“人”或“AI”模式积累经验"
    summaries = []
    total_profiles = 0
    total_samples = 0
    for profile_id in list(index["profiles"]):
        if stop_event.is_set():
            break
        paths = profile_paths(profile_id)
        try:
            candidate = json.loads(paths["profile"].read_text(encoding="utf-8"))
            profile = migrate_profile(candidate, profile_id)
            if profile is None:
                raise ValueError("档案损坏")
            if profile != candidate:
                atomic_write_json(paths["profile"], profile)
            pool = compact_experience(paths["db"], int(config["experience_limit_per_game"]), len(profile["actions"]))
            compact_state_values(
                paths["db"],
                int(config["state_memory_limit_per_game"]),
                len(profile["actions"]),
            )
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
                int(config["train_sample_limit_per_game"]),
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
                int(config["training_epochs"]),
                int(config["training_batch_size"]),
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
        except RuntimeError:
            raise
        except Exception:
            log_text(f"训练 {profile_id} 失败:\n" + traceback.format_exc())
            summaries.append(f"{profile_id}：失败")
    if stop_event.is_set():
        return "升级已取消"
    prior_updated = refresh_global_prior(np, index, config, stop_event)
    detail = "；".join(summaries[:4])
    if len(summaries) > 4:
        detail += f"；另有 {len(summaries) - 4} 个游戏"
    prior_text = "；已更新跨游戏通用先验" if prior_updated else ""
    return f"升级完成：{total_profiles} 个游戏，训练 {total_samples} 条{prior_text}。{detail}"


def run_ai_session(target: int, stop_event: threading.Event) -> str:
    ensure_numpy(download=False, stop_event=stop_event)
    np = import_numpy()
    config = load_config()
    identity = profile_identity(target)
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
    state_memory_limit = max(1000, int(config["state_memory_limit_per_game"]))
    persistent_state_values = load_state_value_memory(
        paths["db"],
        len(profile["actions"]),
        state_memory_limit,
    )
    dirty_state_values: set[tuple[str, int]] = set()
    total, human = count_samples(paths["db"])
    control_preferences = learned_control_preferences(profile, paths["db"])
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
    cold_start = int(model.get("training_rounds", 0)) <= 0 and not transferred_model
    if cold_start:
        mode_text = "通用探索"
    elif human < 8:
        mode_text = "跨游戏迁移"
    else:
        mode_text = "游戏模型"
    probe_actions = cold_start_probe_actions(profile, control_preferences)
    probe_limit = min(len(probe_actions), 18 if cold_start else (8 if human < 8 else 0))
    probe_cursor = 0
    sampler = ScreenSampler(target)
    previous_frame = None
    state_visits: dict[str, int] = {}
    state_action_visits: dict[tuple[str, int], int] = {}
    state_action_values: dict[tuple[str, int], tuple[float, int]] = {}
    recent_frame_hashes: list[str] = []
    recent_state_keys: list[str] = []
    recent_actions: list[int] = []
    pending_experiences: list[dict] = []
    rows = []
    steps = 0
    reward_sum = 0.0
    black_frames = 0
    black_streak = 0
    static_streak = 0
    passive_motion_ema = max(0.0, min(1.0, float(profile.get("passive_motion_ema", 0.0))))
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
    configured_hold = float(config["action_hold_seconds"])
    pause = max(0.0, min(0.5, float(config["step_pause_seconds"])))
    mouse_step = max(1, min(200, int(config["mouse_step_pixels"])))
    delayed_horizon = max(1, min(24, int(config["delayed_reward_horizon"])))
    delayed_discount = max(0.1, min(0.99, float(config["delayed_reward_discount"])))
    online_state_value_weight = max(0.0, min(1.0, float(config["online_state_value_weight"])))
    state_memory_weight = max(0.0, min(1.0, float(config["state_memory_weight"])))
    online_learning_rate = max(0.01, min(1.0, float(config["online_learning_rate"])))
    try:
        while not stop_event.is_set():
            if esc_pressed() or not window_exists(target):
                break
            if foreground_window() != target:
                release_all_inputs()
                flush_delayed_experience(profile, pending_experiences, rows)
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
                save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
                previous_frame = None
                black_streak = 0
                static_streak = 0
                recent_actions.clear()
                recent_frame_hashes.clear()
                recent_state_keys.clear()
                state_action_visits.clear()
                state_action_values.clear()
                smoothed_probabilities = None
                smoothed_values = None
                time.sleep(0.08)
                continue
            current = sampler.capture_gray()
            black = max(current) - min(current) < 3
            if black:
                black_frames += 1
                black_streak += 1
                release_all_inputs()
                flush_delayed_experience(profile, pending_experiences, rows)
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
                save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
                previous_frame = None
                time.sleep(0.08)
                if black_streak >= 120:
                    break
                continue
            black_streak = 0
            feature = make_feature(current, previous_frame)
            previous_frame = current
            current_state_key = state_key(current, feature)
            current_memory_state = memory_state_key(current, feature)
            probabilities, values = model_outputs(np, model, feature)
            if cold_start and len(probabilities) > 1:
                probabilities = probabilities * 0.25 + (0.75 / len(probabilities))
                probabilities /= max(1e-12, float(probabilities.sum()))
            scene_motion = feature_motion(feature)
            current_weight = 0.72 if scene_motion >= 0.025 else 0.48
            if smoothed_probabilities is None:
                smoothed_probabilities = probabilities.astype(np.float64, copy=True)
                smoothed_values = values.astype(np.float64, copy=True)
            else:
                smoothed_probabilities = current_weight * probabilities + (1.0 - current_weight) * smoothed_probabilities
                smoothed_probabilities /= max(1e-12, float(smoothed_probabilities.sum()))
                smoothed_values = current_weight * values + (1.0 - current_weight) * smoothed_values
            reward_prior = np.asarray(profile["action_reward_ema"], dtype=np.float64)
            reward_counts = np.asarray(profile["action_reward_counts"], dtype=np.float64)
            control_response = control_response_evidence(profile)
            policy_values = np.asarray(smoothed_values, dtype=np.float64).copy()
            if len(reward_prior) == len(policy_values):
                uncertainty_scale = 0.08 if cold_start else 0.13
                uncertainty_bonus = uncertainty_scale / np.sqrt(reward_counts + 1.0)
                if len(uncertainty_bonus):
                    uncertainty_bonus[0] = 0.0
                adaptive_bias = np.zeros(len(policy_values), dtype=np.float64)
                origins = profile.get("action_origins", [])
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
                    adaptive_bias[action_position] += 0.24 * float(control_response.get(action_kind(action), 0.0))
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
                    if action_position != 0:
                        adaptive_bias[action_position] += 0.035 / math.sqrt(int(online_count) + 1.0)
                        if memory_count <= 0:
                            adaptive_bias[action_position] += 0.018
                policy_values = np.clip(
                    policy_values + 0.30 * reward_prior + uncertainty_bonus + adaptive_bias,
                    -1.0,
                    1.0,
                )
            action_count = len(smoothed_probabilities)
            if action_count > 1:
                entropy = float(-(smoothed_probabilities * np.log(np.maximum(smoothed_probabilities, 1e-12))).sum())
                confidence = 1.0 - entropy / math.log(action_count)
            else:
                confidence = 1.0
            adaptive_exploration = max(
                0.0,
                min(0.75, exploration + (1.0 - confidence) * 0.14 - confidence * 0.025),
            )
            previous_action = recent_actions[-1] if recent_actions else None
            transition_prior = transition_distribution(np, profile, previous_action, len(profile["actions"]))
            probe_action_index: int | None = None
            probe_due = probe_cursor < probe_limit and (steps < 6 or static_streak >= 4 or steps % 4 == 0)
            if probe_due:
                while probe_cursor < probe_limit:
                    candidate_index = probe_actions[probe_cursor]
                    probe_cursor += 1
                    if not 0 <= candidate_index < len(profile["actions"]):
                        continue
                    if state_action_visits.get((current_state_key, candidate_index), 0) >= 2:
                        continue
                    probe_action_index = candidate_index
                    break
            if probe_action_index is None:
                action_index = choose_policy_action(
                    np,
                    smoothed_probabilities,
                    policy_values,
                    transition_prior,
                    adaptive_exploration,
                    recent_actions,
                    static_streak,
                )
            else:
                action_index = probe_action_index
            hold = learned_action_hold(profile, action_index, configured_hold)
            if not execute_action(target, profile["actions"][action_index], hold, mouse_step, stop_event):
                if stop_event.is_set() or esc_pressed():
                    break
                continue
            if pause and not sleep_cancelable(pause, stop_event, target):
                if stop_event.is_set() or esc_pressed():
                    break
                continue
            next_frame = sampler.capture_gray()
            next_black = max(next_frame) - min(next_frame) < 3
            useful_motion, changed_ratio, flicker = visual_change_metrics(current, next_frame)
            regional_activity, change_concentration, center_ratio, global_shift = regional_change_metrics(current, next_frame)
            digest = frame_hash(next_frame)
            next_feature = make_feature(next_frame, current)
            next_state_key = state_key(next_frame, next_feature)
            visit_count = state_visits.get(next_state_key, 0)
            looped = recent_hash_match(digest, recent_frame_hashes[-64:], 3)
            if useful_motion < 0.0045 and changed_ratio < 0.025:
                static_streak += 1
            else:
                static_streak = 0
            selected_kind = action_kind(profile["actions"][action_index])
            if selected_kind == "idle":
                passive_motion_ema = passive_motion_ema * 0.82 + useful_motion * 0.18
            else:
                passive_motion_ema = passive_motion_ema * 0.992 + min(scene_motion, useful_motion) * 0.008
            passive_reference = max(scene_motion * 0.60, passive_motion_ema * 0.85)
            passive_motion = min(useful_motion, passive_reference)
            causal_motion = max(0.0, useful_motion - passive_reference)
            motion_reward = min(0.52, causal_motion * 9.0)
            change_reward = min(0.15, changed_ratio * 0.30) if causal_motion >= 0.0015 else 0.0
            structured_reward = min(
                0.18,
                max(0.0, change_concentration - 0.28) * regional_activity * 7.0,
            )
            center_reward = min(0.08, max(0.0, center_ratio - 1.0) * causal_motion * 1.8)
            novel_state = visit_count == 0 and not looped
            novelty_reward = (0.20 / math.sqrt(visit_count + 1.0)) if useful_motion >= 0.0025 else 0.0
            progress_reward = 0.16 if novel_state and causal_motion >= 0.004 and changed_ratio >= 0.02 else 0.0
            loop_penalty = 0.30 if looped else 0.0
            static_penalty = min(0.70, static_streak * 0.047) if action_index != 0 else min(0.34, static_streak * 0.024)
            repetition_penalty = 0.0
            if len(recent_actions) >= 5 and len(set(recent_actions[-5:])) == 1 and recent_actions[-1] == action_index:
                repetition_penalty = min(0.38, 0.055 * (len(recent_actions[-8:]) - 4))
            passive_penalty = min(0.18, passive_motion * 2.2)
            flicker_penalty = min(0.38, flicker * 1.9)
            uniform_change_penalty = min(
                0.20,
                max(0.0, 0.30 - change_concentration) * causal_motion * 4.0 + global_shift * 0.30,
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
                    + novelty_reward
                    + progress_reward
                    - loop_penalty
                    - static_penalty
                    - repetition_penalty
                    - passive_penalty
                    - flicker_penalty
                    - uniform_change_penalty
                    - repeated_state_action_penalty
                    - black_penalty,
                ),
            )
            reward_sum += reward
            update_control_response(profile, action_index, reward)
            state_action_key = (current_state_key, action_index)
            update_online_state_value(state_action_values, state_action_key, reward)
            persistent_key = (current_memory_state, action_index)
            update_state_value_memory(persistent_state_values, persistent_key, reward, online_learning_rate)
            dirty_state_values.add(persistent_key)
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
            if len(state_action_visits) > 16384:
                state_action_visits.clear()
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
    finally:
        release_all_inputs()
        flush_delayed_experience(profile, pending_experiences, rows)
        if rows:
            insert_samples(paths["db"], rows)
        save_state_value_memory(paths["db"], persistent_state_values, dirty_state_values)
        sampler.close()
        if steps:
            mean_reward = max(-1.0, min(1.0, reward_sum / steps))
            old_session_reward = float(profile.get("ai_reward_ema", 0.0))
            completed_sessions = int(profile.get("ai_sessions", 0))
            session_alpha = 1.0 if completed_sessions <= 0 else 0.20
            profile["last_ai_mean_reward"] = mean_reward
            profile["ai_reward_ema"] = old_session_reward + session_alpha * (mean_reward - old_session_reward)
            profile["ai_sessions"] = completed_sessions + 1
            profile["passive_motion_ema"] = max(0.0, min(1.0, passive_motion_ema))
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
        self.exit_after_worker = True
        self.escape_was_down = esc_pressed() if os.name == "nt" else False

        tk.Label(self.root, text=f"AnyGameAI {APP_VERSION}", font=("Segoe UI", 24, "bold")).pack(pady=(22, 8))
        tk.Label(
            self.root,
            text="选择一项任务；切换到游戏窗口后，ESC 安全结束并退出",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 14))

        button_frame = tk.Frame(self.root)
        button_frame.pack()
        self.file_button = tk.Button(button_frame, text="文件", width=11, height=2, command=self.file_mode)
        self.human_button = tk.Button(button_frame, text="人", width=11, height=2, command=self.human_mode)
        self.upgrade_button = tk.Button(button_frame, text="升级", width=11, height=2, command=self.upgrade_mode)
        self.ai_button = tk.Button(button_frame, text="AI", width=11, height=2, command=self.ai_mode)
        for column, button in enumerate((self.file_button, self.human_button, self.upgrade_button, self.ai_button)):
            button.grid(row=0, column=column, padx=7)

        self.status = tk.StringVar(value="就绪；首次使用请先点击“文件”")
        tk.Label(self.root, textvariable=self.status, font=("Segoe UI", 10), wraplength=580).pack(pady=18)
        self.root.bind("<Escape>", self.on_escape)
        self.root.after(60, self.poll_worker)

    def on_escape(self, _event=None) -> None:
        self.escape_was_down = True
        if self.busy:
            self.close_requested = True
            self.stop_event.set()
            self.status.set("正在安全结束…")
        else:
            self.stop_and_close()

    def set_busy(self, value: bool) -> None:
        self.busy = value
        state = tk.DISABLED if value else tk.NORMAL
        for button in (self.file_button, self.human_button, self.upgrade_button, self.ai_button):
            button.config(state=state)

    def stop_and_close(self) -> None:
        if self.closing:
            return
        if self.busy:
            self.close_requested = True
            self.stop_event.set()
            self.status.set("正在安全结束…")
            return
        self.closing = True
        self.stop_event.set()
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
            try:
                result = worker()
            except Exception:
                error = traceback.format_exc()
                log_text(error)
            self.worker_messages.put((result, error, hide))

        threading.Thread(target=task, daemon=True).start()

    def poll_worker(self) -> None:
        if self.closing:
            return
        if os.name == "nt":
            escape_is_down = esc_pressed()
            if escape_is_down and not self.escape_was_down:
                self.escape_was_down = True
                if self.busy:
                    self.close_requested = True
                    if not self.stop_event.is_set():
                        self.stop_event.set()
                        self.status.set("正在安全结束…")
                else:
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

    def worker_done(self, result, error: str | None, hidden: bool) -> None:
        if os.name == "nt":
            release_all_inputs()
        if hidden and not self.close_requested:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        self.set_busy(False)
        if error and "操作已取消" not in error:
            self.status.set("失败；详情见桌面 AnyGameAI 文件夹中的日志")
            detail = error.strip().splitlines()[-1] if error.strip() else "未知错误"
            messagebox.showerror(APP_NAME, f"运行失败：{detail}\n\n详情已写入桌面 AnyGameAI 文件夹中的日志。")
        else:
            self.status.set(str(result) if result else "已结束")
        if self.exit_after_worker or self.close_requested:
            self.close_requested = False
            self.root.after(180, self.stop_and_close)

    def file_mode(self) -> None:
        def work():
            result = ensure_files(self.stop_event, download=True)
            if self.stop_event.is_set():
                return "文件检查已结束"
            parts = [
                f"修复 {result['repaired']} 项",
                f"下载 {result['downloaded']} 项",
                f"经验 {result['records']} 条",
                f"场景记忆 {result['memory_records']} 条",
                f"清理 {result['removed']} 条",
            ]
            if result.get("remote_error"):
                parts.append("远程更新失败，本地文件仍可用")
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
        self.run_worker("正在训练策略、动作价值、跨游戏通用先验并整理经验池；ESC 可取消", lambda: train_all_profiles(self.stop_event))

    def ai_mode(self) -> None:
        def work():
            target = wait_for_target_window(self.stop_event)
            if not target:
                wait_esc_release()
                return "未检测到游戏窗口，AI 模式已结束"
            return run_ai_session(target, self.stop_event)

        self.run_worker("请切换到游戏窗口；AI 将自动使用游戏模型、跨游戏迁移或通用探索；ESC 结束", work, hide=True)

    def run(self) -> None:
        self.root.mainloop()


def show_startup_error(text: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(APP_NAME, text)
    root.destroy()


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


def main() -> None:
    sys.excepthook = unhandled_exception
    if os.name != "nt":
        show_startup_error("此程序仅支持 Windows 11 x64。")
        return
    if sys.maxsize <= 2**32:
        show_startup_error("需要 64 位 Python。")
        return
    if sys.version_info[:2] != (3, 12):
        show_startup_error("需要 Python 3.12 x64。")
        return
    if sys.getwindowsversion().build < 22000:
        show_startup_error("需要 Windows 11 x64。")
        return
    bootstrap_to_desktop()
    hide_console()
    if not acquire_single_instance():
        show_startup_error("AnyGameAI 已经在运行。")
        return
    atexit.register(release_all_inputs)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    load_config()
    sync_profile_index(load_index())
    AnyGameAIApp().run()


if __name__ == "__main__":
    main()
