from __future__ import annotations

import atexit
import ctypes
import hashlib
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
APP_VERSION = "7.0"
SCRIPT_NAME = "AnyGameAI.py"
APP_SCHEMA = 3
CONFIG_SCHEMA = 3
PROFILE_SCHEMA = 3
MODEL_SCHEMA = 2
FEATURE_WIDTH = 40
FEATURE_HEIGHT = 24
FEATURE_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 2
MAX_COMPRESSED_FEATURE_BYTES = FEATURE_DIM * 2 + 256
DEFAULT_HIDDEN_SIZE = 64
TARGET_WAIT_SECONDS = 15.0
MOUSE_GRID_WIDTH = 32
MOUSE_GRID_HEIGHT = 18
INTEGRITY_SCHEMA = 1
NUMPY_REQUIREMENT = "numpy>=1.26,<3"
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_REMOTE_FILE_BYTES = 512 * 1024 * 1024
MAX_SCRIPT_BYTES = 8 * 1024 * 1024
WINDOWS_RESERVED_NAMES = {"con", "prn", "aux", "nul", *(f"com{index}" for index in range(1, 10)), *(f"lpt{index}" for index in range(1, 10))}
WINDOWS_INVALID_NAME_PATTERN = re.compile(r'[<>:"|?*\x00-\x1f]')
VERSION_PATTERN = re.compile(r'^APP_VERSION\s*=\s*["\'](\d+(?:\.\d+)*)["\']', re.MULTILINE)


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
PROFILES_DIR = APP_DIR / "profiles"

DEFAULT_CONFIG = {
    "schema": CONFIG_SCHEMA,
    "sample_interval_seconds": 0.085,
    "action_hold_seconds": 0.075,
    "step_pause_seconds": 0.025,
    "exploration": 0.08,
    "mouse_step_pixels": 24,
    "max_action_count": 128,
    "experience_limit_per_game": 60000,
    "train_sample_limit_per_game": 18000,
    "training_epochs": 8,
    "training_batch_size": 128,
    "learning_rate": 0.0015,
    "hidden_size": DEFAULT_HIDDEN_SIZE,
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
        if validate_config(raw):
            merged = deep_copy_json(DEFAULT_CONFIG)
            merged.update(raw)
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
        if isinstance(raw, dict) and raw.get("schema") == APP_SCHEMA and isinstance(raw.get("profiles"), dict):
            profiles = {
                profile_id: metadata
                for profile_id, metadata in raw["profiles"].items()
                if valid_profile_id(profile_id) and isinstance(metadata, dict)
            }
            return {"schema": APP_SCHEMA, "profiles": profiles}
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


def local_numpy_probe_command() -> list[str]:
    code = (
        "import pathlib,sys;"
        f"root=pathlib.Path({str(SITE_PACKAGES)!r}).resolve();"
        "sys.path.insert(0,str(root));"
        "import numpy as n;"
        "path=pathlib.Path(n.__file__).resolve();"
        "assert path==root or root in path.parents;"
        "assert float(n.arange(16,dtype=n.float32).reshape(4,4).mean())==7.5"
    )
    return [sys.executable, "-c", code]


def run_process_cancelable(command: list[str], stop_event: threading.Event | None) -> tuple[int, str]:
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
        probe_code, _ = run_process_cancelable(local_numpy_probe_command(), stop_event)
        if probe_code == 0:
            return False
    else:
        try:
            import_numpy(local_only=True)
            return False
        except Exception as first_error:
            raise RuntimeError("缺少或损坏的本地 NumPy 运行组件，请先点击“文件”。") from first_error
    if stop_event is not None and stop_event.is_set():
        raise RuntimeError("操作已取消")
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    clear_numpy_modules()
    try:
        shutil.rmtree(SITE_PACKAGES)
    except FileNotFoundError:
        pass
    SITE_PACKAGES.mkdir(parents=True, exist_ok=True)
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
        "--only-binary=:all:",
        "--target",
        str(SITE_PACKAGES),
        NUMPY_REQUIREMENT,
    ]
    code, output = run_process_cancelable(command, stop_event)
    if stop_event is not None and stop_event.is_set():
        raise RuntimeError("操作已取消")
    if code != 0:
        ensure_code, ensure_output = run_process_cancelable([sys.executable, "-m", "ensurepip", "--upgrade"], stop_event)
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        if ensure_code == 0:
            code, output = run_process_cancelable(command, stop_event)
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
        else:
            output += "\n" + ensure_output
    if code != 0:
        log_text("运行组件安装失败:\n" + output[-12000:])
        raise RuntimeError("运行组件下载或安装失败，详情已写入日志。")
    probe_code, probe_output = run_process_cancelable(local_numpy_probe_command(), stop_event)
    if probe_code != 0:
        log_text("运行组件自检失败:\n" + probe_output[-12000:])
        raise RuntimeError("运行组件安装后自检失败，详情已写入日志。")
    importlib.invalidate_caches()
    import_numpy(local_only=True)
    return True


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
    protected = {"config.json", "profiles.json", "anygameai.log", "integrity.json"}
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


def profile_identity(window: int) -> dict:
    title = window_text(window)
    class_name = window_class(window)
    executable = process_path(window)
    executable_name = Path(executable).stem.lower() if executable else ""
    host_executables = {
        "chrome", "msedge", "firefox", "brave", "opera", "vivaldi",
        "retroarch", "pcsx2", "rpcs3", "dolphin", "dolphin-emu", "mame",
        "cemu", "yuzu", "ryujinx", "xenia", "ppssppwindows64",
    }
    game_title = stable_game_title(title)
    use_title = executable_name in host_executables or not executable
    base = game_title if use_title and game_title else (Path(executable).stem if executable else (class_name or "game"))
    identity_parts = [executable.lower(), class_name.lower()]
    if use_title:
        identity_parts.append(game_title.lower())
    identity = "|".join(identity_parts).encode("utf-8", errors="replace")
    digest = hashlib.sha256(identity).hexdigest()[:12]
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._-") or "game"
    profile_id = f"{safe[:48]}-{digest}"
    return {
        "id": profile_id,
        "name": base or title or "Game",
        "title": title,
        "window_class": class_name,
        "executable": executable,
    }


class ScreenSampler:
    def __init__(self, target_window: int):
        self.window = target_window
        self.width = FEATURE_WIDTH
        self.height = FEATURE_HEIGHT
        self.screen_dc = user32.GetDC(0)
        self.memory_dc = gdi32.CreateCompatibleDC(self.screen_dc)
        self.bitmap = gdi32.CreateCompatibleBitmap(self.screen_dc, self.width, self.height)
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

    def capture_gray(self) -> bytes:
        x, y, source_width, source_height = window_capture_rect(self.window)
        ok = gdi32.StretchBlt(
            self.memory_dc,
            0,
            0,
            self.width,
            self.height,
            self.screen_dc,
            x,
            y,
            source_width,
            source_height,
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
        target = 0
        for source in range(0, len(raw), 4):
            b = raw[source]
            g = raw[source + 1]
            r = raw[source + 2]
            gray[target] = (r * 77 + g * 150 + b * 29) >> 8
            target += 1
        return bytes(gray)

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
        "mouse_x": mouse_x,
        "mouse_y": mouse_y,
    }


def action_signature(action: dict) -> str:
    return json.dumps(normalized_action(action), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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
            "mouse_x": mouse_x,
            "mouse_y": mouse_y,
        }
    )
    return action, current


def execute_action(target: int, action: dict, hold_seconds: float, mouse_step: int) -> None:
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
    send_inputs(down)
    if down:
        time.sleep(max(0.01, min(0.35, float(hold_seconds))))
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
    return hashlib.blake2s(gray, digest_size=8).hexdigest()


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
    return {
        "schema": PROFILE_SCHEMA,
        "id": identity["id"],
        "name": identity.get("name", identity["id"]),
        "title": identity.get("title", ""),
        "window_class": identity.get("window_class", ""),
        "executable": identity.get("executable", ""),
        "created_at": now_text(),
        "updated_at": now_text(),
        "actions": [normalized_action({})],
        "trained_samples": 0,
        "training_rounds": 0,
        "needs_training": True,
    }


def migrate_profile(data: object, profile_id: str) -> dict | None:
    if not isinstance(data, dict) or data.get("id") != profile_id:
        return None
    if data.get("schema") not in (2, PROFILE_SCHEMA):
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
        return migrated
    except Exception:
        return None


def load_or_create_profile(identity: dict) -> tuple[dict, dict[str, Path]]:
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
            connection.commit()
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
            "DELETE FROM samples WHERE feature_dim<>? OR action<0 OR action>=? OR length(feature)>?",
            (FEATURE_DIM, action_count, MAX_COMPRESSED_FEATURE_BYTES),
        )
        human_count = int(connection.execute("SELECT COUNT(*) FROM samples WHERE source='human'").fetchone()[0])
        ai_count = int(connection.execute("SELECT COUNT(*) FROM samples WHERE source='ai'").fetchone()[0])
        ai_reserve = min(ai_count, max(0, int(limit * 0.15)))
        human_keep = min(human_count, max(0, limit - ai_reserve))
        ai_keep = min(ai_count, max(0, limit - human_keep))

        def trim_source(source: str, keep: int) -> None:
            if keep <= 0:
                connection.execute("DELETE FROM samples WHERE source=?", (source,))
                return
            if source == "ai":
                connection.execute(
                    "DELETE FROM samples WHERE source='ai' AND id NOT IN "
                    "(SELECT id FROM samples WHERE source='ai' ORDER BY reward DESC, id DESC LIMIT ?)",
                    (keep,),
                )
                return
            cutoff = connection.execute(
                "SELECT id FROM samples WHERE source=? ORDER BY id DESC LIMIT 1 OFFSET ?",
                (source, keep - 1),
            ).fetchone()
            if cutoff:
                connection.execute("DELETE FROM samples WHERE source=? AND id<?", (source, int(cutoff[0])))

        if human_count > human_keep:
            trim_source("human", human_keep)
        if ai_count > ai_keep:
            trim_source("ai", ai_keep)
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
        if action["mouse_x"] >= 0 and candidate["mouse_x"] >= 0:
            distance = abs(action["mouse_x"] - candidate["mouse_x"]) + abs(action["mouse_y"] - candidate["mouse_y"])
            score += max(-4.0, 4.0 - distance * 0.35)
        elif action["mouse_x"] != candidate["mouse_x"]:
            score -= 2.0
        if score > best_score:
            best_score = score
            best_index = index
    return best_index


def register_action(profile: dict, candidate: dict, max_actions: int) -> tuple[int, bool]:
    candidate = normalized_action(candidate)
    signature = action_signature(candidate)
    for index, action in enumerate(profile["actions"]):
        if action_signature(action) == signature:
            return index, False
    if len(profile["actions"]) < max_actions:
        profile["actions"].append(candidate)
        return len(profile["actions"]) - 1, True
    return nearest_action_index(profile["actions"], candidate), False


def actions_hash(actions: list[dict]) -> str:
    text = json.dumps(actions, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def initialize_model(np, input_dim: int, hidden_size: int, output_size: int) -> dict:
    scale1 = (2.0 / input_dim) ** 0.5
    scale2 = (2.0 / hidden_size) ** 0.5
    return {
        "schema": MODEL_SCHEMA,
        "input_dim": input_dim,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "W1": (np.random.standard_normal((input_dim, hidden_size)).astype(np.float32) * scale1),
        "b1": np.zeros(hidden_size, dtype=np.float32),
        "W2": (np.random.standard_normal((hidden_size, output_size)).astype(np.float32) * scale2),
        "b2": np.zeros(output_size, dtype=np.float32),
        "trained_samples": 0,
        "training_rounds": 0,
        "action_hash": "",
    }


def load_model(np, path: Path, input_dim: int, hidden_size: int, output_size: int, action_list: list[dict]) -> tuple[dict, bool]:
    changed = False
    model = None
    try:
        with np.load(path, allow_pickle=False) as data:
            schema = int(data["schema"][0])
            if schema != MODEL_SCHEMA:
                raise ValueError("模型版本不兼容")
            loaded = {
                "schema": schema,
                "input_dim": int(data["input_dim"][0]),
                "hidden_size": int(data["hidden_size"][0]),
                "output_size": int(data["output_size"][0]),
                "W1": data["W1"].astype(np.float32, copy=True),
                "b1": data["b1"].astype(np.float32, copy=True),
                "W2": data["W2"].astype(np.float32, copy=True),
                "b2": data["b2"].astype(np.float32, copy=True),
                "trained_samples": int(data["trained_samples"][0]),
                "training_rounds": int(data["training_rounds"][0]),
                "action_hash": str(data["action_hash"][0]),
            }
            if loaded["input_dim"] != input_dim or loaded["hidden_size"] != hidden_size:
                raise ValueError("模型结构变化")
            if loaded["W1"].shape != (input_dim, hidden_size) or loaded["b1"].shape != (hidden_size,):
                raise ValueError("模型参数尺寸错误")
            if loaded["W2"].shape[0] != hidden_size or loaded["b2"].shape != (loaded["output_size"],):
                raise ValueError("模型输出尺寸错误")
            for value in (loaded["W1"], loaded["b1"], loaded["W2"], loaded["b2"]):
                if not np.isfinite(value).all():
                    raise ValueError("模型包含无效数值")
            model = loaded
    except FileNotFoundError:
        pass
    except Exception:
        backup_corrupt(path)
    if model is None:
        model = initialize_model(np, input_dim, hidden_size, output_size)
        changed = True
    if model["output_size"] < output_size:
        old_size = model["output_size"]
        expanded_w2 = np.random.standard_normal((hidden_size, output_size)).astype(np.float32) * ((2.0 / hidden_size) ** 0.5)
        expanded_b2 = np.zeros(output_size, dtype=np.float32)
        expanded_w2[:, :old_size] = model["W2"]
        expanded_b2[:old_size] = model["b2"]
        model["W2"] = expanded_w2
        model["b2"] = expanded_b2
        model["output_size"] = output_size
        changed = True
    elif model["output_size"] > output_size:
        model["W2"] = model["W2"][:, :output_size].copy()
        model["b2"] = model["b2"][:output_size].copy()
        model["output_size"] = output_size
        changed = True
    current_hash = actions_hash(action_list)
    if model.get("action_hash") != current_hash:
        model["action_hash"] = current_hash
        changed = True
    return model, changed


def save_model(np, path: Path, model: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("wb") as file:
        np.savez_compressed(
            file,
            schema=np.array([MODEL_SCHEMA], dtype=np.int32),
            input_dim=np.array([model["input_dim"]], dtype=np.int32),
            hidden_size=np.array([model["hidden_size"]], dtype=np.int32),
            output_size=np.array([model["output_size"]], dtype=np.int32),
            W1=model["W1"].astype(np.float32),
            b1=model["b1"].astype(np.float32),
            W2=model["W2"].astype(np.float32),
            b2=model["b2"].astype(np.float32),
            trained_samples=np.array([model.get("trained_samples", 0)], dtype=np.int64),
            training_rounds=np.array([model.get("training_rounds", 0)], dtype=np.int64),
            action_hash=np.array([model.get("action_hash", "")]),
            updated_at=np.array([now_text()]),
        )
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, path)


def model_probabilities(np, model: dict, feature: bytes):
    x = np.frombuffer(feature, dtype=np.uint8).astype(np.float32) / 255.0
    x[: FEATURE_WIDTH * FEATURE_HEIGHT] -= 0.5
    hidden = np.maximum(0.0, x @ model["W1"] + model["b1"])
    logits = hidden @ model["W2"] + model["b2"]
    logits -= float(logits.max())
    probabilities = np.exp(logits)
    probabilities /= max(1e-8, float(probabilities.sum()))
    return probabilities


def choose_policy_action(np, probabilities, exploration: float, recent_actions: list[int], static_streak: int) -> int:
    action_count = len(probabilities)
    if action_count <= 1:
        return 0
    adjusted = probabilities.astype(np.float64, copy=True)
    repeated = len(recent_actions) >= 4 and len(set(recent_actions[-4:])) == 1
    if repeated:
        adjusted[recent_actions[-1]] *= 0.25
    if static_streak >= 5:
        for action_index in set(recent_actions[-min(6, len(recent_actions)):]):
            adjusted[action_index] *= 0.45
        adjusted[0] *= 0.2
    adjusted = np.maximum(adjusted, 1e-12)
    dynamic_exploration = min(0.6, exploration + min(0.42, static_streak * 0.045))
    if random.random() < dynamic_exploration:
        weights = np.sqrt(adjusted)
        weights /= weights.sum()
        return int(np.random.choice(action_count, p=weights))
    return int(np.argmax(adjusted))


def reservoir_add(bucket: list, value, seen_count: int, capacity: int) -> None:
    if len(bucket) < capacity:
        bucket.append(value)
        return
    position = random.randrange(seen_count)
    if position < capacity:
        bucket[position] = value


def load_training_data(np, db_path: Path, action_count: int, sample_limit: int, stop_event: threading.Event | None):
    ensure_database(db_path)
    per_action = max(120, sample_limit // max(1, action_count))
    human_capacity = max(180, int(per_action * 0.82))
    ai_capacity = max(40, per_action - human_capacity)
    buckets: dict[tuple[str, int], list] = {}
    seen: dict[tuple[str, int], int] = {}
    invalid = 0
    connection = sqlite3.connect(db_path, timeout=30)
    try:
        cursor = connection.execute(
            "SELECT source, action, reward, feature_dim, feature FROM samples ORDER BY id"
        )
        for source, action, reward, feature_dim, blob in cursor:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            action = int(action)
            if int(feature_dim) != FEATURE_DIM or not (0 <= action < action_count) or source not in ("human", "ai"):
                invalid += 1
                continue
            try:
                feature = decompress_feature(blob, FEATURE_DIM)
            except Exception:
                invalid += 1
                continue
            key = (source, action)
            seen[key] = seen.get(key, 0) + 1
            capacity = human_capacity if source == "human" else ai_capacity
            reservoir_add(buckets.setdefault(key, []), (feature, action, float(reward), source), seen[key], capacity)
    finally:
        connection.close()
    samples = [item for bucket in buckets.values() for item in bucket]
    if len(samples) > sample_limit:
        random.shuffle(samples)
        samples = samples[:sample_limit]
    random.shuffle(samples)
    if not samples:
        return None, None, None, invalid
    x = np.empty((len(samples), FEATURE_DIM), dtype=np.float32)
    y = np.empty(len(samples), dtype=np.int64)
    weights = np.empty(len(samples), dtype=np.float32)
    counts = {}
    for _, action, _, _ in samples:
        counts[action] = counts.get(action, 0) + 1
    mean_count = sum(counts.values()) / max(1, len(counts))
    for index, (feature, action, reward, source) in enumerate(samples):
        row = np.frombuffer(feature, dtype=np.uint8).astype(np.float32) / 255.0
        row[: FEATURE_WIDTH * FEATURE_HEIGHT] -= 0.5
        x[index] = row
        y[index] = action
        class_weight = min(3.0, max(0.55, (mean_count / max(1, counts[action])) ** 0.5))
        if source == "human":
            source_weight = 1.0
        else:
            source_weight = min(0.45, max(0.01, 0.02 + max(0.0, reward) * 0.32))
        weights[index] = class_weight * source_weight
    return x, y, weights, invalid


def train_model(np, model: dict, x, y, sample_weights, epochs: int, batch_size: int, learning_rate: float, stop_event: threading.Event | None) -> dict:
    sample_count = len(x)
    if sample_count < 8:
        raise RuntimeError("示范经验太少，请先在人模式中多玩一会儿。")
    order = np.arange(sample_count)
    np.random.shuffle(order)
    split = max(1, int(sample_count * 0.1)) if sample_count >= 40 else 0
    if split:
        validation_indices = order[-split:].copy()
        train_indices = order[:-split].copy()
    else:
        validation_indices = np.array([], dtype=np.int64)
        train_indices = order.copy()
    parameters = [model["W1"], model["b1"], model["W2"], model["b2"]]
    moments = [np.zeros_like(value) for value in parameters]
    variances = [np.zeros_like(value) for value in parameters]
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    step = 0
    last_loss = 0.0
    for _ in range(max(1, epochs)):
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("操作已取消")
        np.random.shuffle(train_indices)
        for start in range(0, len(train_indices), max(8, batch_size)):
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            indices = train_indices[start:start + max(8, batch_size)]
            batch_x = x[indices]
            batch_y = y[indices]
            batch_weights = sample_weights[indices]
            z1 = batch_x @ model["W1"] + model["b1"]
            hidden = np.maximum(0.0, z1)
            logits = hidden @ model["W2"] + model["b2"]
            logits -= logits.max(axis=1, keepdims=True)
            probabilities = np.exp(logits)
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            chosen = probabilities[np.arange(len(indices)), batch_y]
            weight_total = max(1e-6, float(batch_weights.sum()))
            last_loss = float((-np.log(chosen + 1e-8) * batch_weights).sum() / weight_total)
            gradient_logits = probabilities
            gradient_logits[np.arange(len(indices)), batch_y] -= 1.0
            gradient_logits *= (batch_weights / weight_total)[:, None]
            gradient_w2 = hidden.T @ gradient_logits + 1e-5 * model["W2"]
            gradient_b2 = gradient_logits.sum(axis=0)
            gradient_hidden = gradient_logits @ model["W2"].T
            gradient_hidden[z1 <= 0] = 0
            gradient_w1 = batch_x.T @ gradient_hidden + 1e-5 * model["W1"]
            gradient_b1 = gradient_hidden.sum(axis=0)
            gradients = [gradient_w1, gradient_b1, gradient_w2, gradient_b2]
            step += 1
            for index, (parameter, gradient) in enumerate(zip(parameters, gradients)):
                np.clip(gradient, -3.0, 3.0, out=gradient)
                moments[index] = beta1 * moments[index] + (1.0 - beta1) * gradient
                variances[index] = beta2 * variances[index] + (1.0 - beta2) * (gradient * gradient)
                corrected_m = moments[index] / (1.0 - beta1 ** step)
                corrected_v = variances[index] / (1.0 - beta2 ** step)
                parameter -= learning_rate * corrected_m / (np.sqrt(corrected_v) + epsilon)
    if len(validation_indices):
        validation_x = x[validation_indices]
        validation_y = y[validation_indices]
        hidden = np.maximum(0.0, validation_x @ model["W1"] + model["b1"])
        predictions = np.argmax(hidden @ model["W2"] + model["b2"], axis=1)
        accuracy = float((predictions == validation_y).mean())
    else:
        hidden = np.maximum(0.0, x @ model["W1"] + model["b1"])
        predictions = np.argmax(hidden @ model["W2"] + model["b2"], axis=1)
        accuracy = float((predictions == y).mean())
    model["trained_samples"] = int(model.get("trained_samples", 0)) + sample_count
    model["training_rounds"] = int(model.get("training_rounds", 0)) + 1
    return {"samples": sample_count, "loss": last_loss, "accuracy": accuracy}


def validate_model_file(path: Path, profile: dict, config: dict) -> bool:
    if not path.exists():
        return True
    np = import_numpy()
    model, changed = load_model(
        np,
        path,
        FEATURE_DIM,
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
    try:
        validate_model_file(paths["model"], profile, config)
    except Exception:
        backup_corrupt(paths["model"])
        repaired += 1
    return {"repaired": repaired, "removed": removed, "records": result["records"]}


def ensure_files(stop_event: threading.Event | None, download: bool) -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    repaired = 0
    downloaded = 0
    removed = 0
    records = 0
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
    for profile_id in sorted(profile_ids):
        if stop_event is not None and stop_event.is_set():
            break
        result = repair_profile(profile_id, config)
        repaired += result["repaired"]
        removed += result["removed"]
        records += result["records"]
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
                "restart_required": restart_required,
                "remote_error": str(error),
            }
    return {
        "repaired": repaired,
        "downloaded": downloaded,
        "removed": removed,
        "records": records,
        "restart_required": restart_required,
    }


def record_human_session(target: int, stop_event: threading.Event) -> str:
    config = load_config()
    identity = profile_identity(target)
    profile, paths = load_or_create_profile(identity)
    interval = max(0.04, min(0.25, float(config["sample_interval_seconds"])))
    max_actions = max(8, int(config["max_action_count"]))
    sampler = ScreenSampler(target)
    previous_frame = None
    previous_cursor = cursor_position()
    rows = []
    recorded = 0
    captured = 0
    idle_streak = 0
    new_actions = 0
    black_frames = 0
    try:
        while not stop_event.is_set():
            if esc_pressed() or not window_exists(target):
                break
            if foreground_window() != target:
                time.sleep(0.08)
                previous_frame = None
                previous_cursor = cursor_position()
                continue
            started = time.monotonic()
            action, previous_cursor = observe_human_action(target, previous_cursor)
            current = sampler.capture_gray()
            captured += 1
            if max(current) - min(current) < 3:
                black_frames += 1
            feature = make_feature(current, previous_frame)
            previous_frame = current
            action_index, added = register_action(profile, action, max_actions)
            if added:
                new_actions += 1
                profile["needs_training"] = True
                save_profile(profile, paths)
            idle = not action["keys"] and not action["buttons"] and not action["mouse_dx"] and not action["mouse_dy"]
            if idle and feature_motion(feature) < 0.004:
                idle_streak += 1
            else:
                idle_streak = 0
            keep_sample = idle_streak <= 2 or idle_streak % 6 == 0
            if keep_sample:
                rows.append((now_text(), "human", action_index, 1.0, FEATURE_DIM, compress_feature(feature)))
                recorded += 1
                profile["needs_training"] = True
                if len(rows) >= 100:
                    insert_samples(paths["db"], rows)
                    rows.clear()
            delay = interval - (time.monotonic() - started)
            if delay > 0:
                time.sleep(delay)
    finally:
        if rows:
            insert_samples(paths["db"], rows)
        sampler.close()
        save_profile(profile, paths)
        compact_experience(paths["db"], int(config["experience_limit_per_game"]), len(profile["actions"]))
        wait_esc_release()
    warning = "；画面可能未被正确采集" if black_frames > max(20, captured // 2) else ""
    return f"人玩结束：{profile['name']}；记录 {recorded} 条；新增动作 {new_actions} 个{warning}"


def train_all_profiles(stop_event: threading.Event) -> str:
    ensure_numpy(download=False, stop_event=stop_event)
    np = import_numpy()
    config = load_config()
    index, _ = sync_profile_index(load_index())
    if not index.get("profiles"):
        return "没有可升级的游戏；请先使用“人”模式示范"
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
            pool = compact_experience(
                paths["db"],
                int(config["experience_limit_per_game"]),
                len(profile["actions"]),
            )
            if pool["human"] < 8:
                summaries.append(f"{profile['name']}：示范不足")
                continue
            model, _ = load_model(
                np,
                paths["model"],
                FEATURE_DIM,
                int(config["hidden_size"]),
                len(profile["actions"]),
                profile["actions"],
            )
            x, y, weights, invalid = load_training_data(
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
                weights,
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
            summaries.append(f"{profile['name']}：{metrics['samples']}条，准确率{metrics['accuracy']:.0%}")
            if invalid:
                log_text(f"{profile_id} 训练时忽略损坏经验 {invalid} 条")
        except RuntimeError:
            raise
        except Exception:
            log_text(f"训练 {profile_id} 失败:\n" + traceback.format_exc())
            summaries.append(f"{profile_id}：失败")
    if stop_event.is_set():
        return "升级已取消"
    detail = "；".join(summaries[:4])
    if len(summaries) > 4:
        detail += f"；另有 {len(summaries) - 4} 个游戏"
    return f"升级完成：{total_profiles} 个游戏，训练 {total_samples} 条。{detail}"


def run_ai_session(target: int, stop_event: threading.Event) -> str:
    ensure_numpy(download=False, stop_event=stop_event)
    np = import_numpy()
    config = load_config()
    identity = profile_identity(target)
    profile, paths = load_or_create_profile(identity)
    total, human = count_samples(paths["db"])
    if human < 8 or not paths["model"].exists() or bool(profile.get("needs_training", False)):
        return f"{profile['name']} 尚未完成训练或动作已变化；请先用“人”示范，再点“升级”"
    model, changed = load_model(
        np,
        paths["model"],
        FEATURE_DIM,
        int(config["hidden_size"]),
        len(profile["actions"]),
        profile["actions"],
    )
    if int(model.get("training_rounds", 0)) <= 0:
        return f"{profile['name']} 尚未完成训练；请先点“升级”"
    if changed:
        save_model(np, paths["model"], model)
    sampler = ScreenSampler(target)
    previous_frame = None
    seen_frames: set[str] = set()
    recent_actions: list[int] = []
    rows = []
    steps = 0
    black_frames = 0
    static_streak = 0
    exploration = max(0.0, min(0.35, float(config["exploration"])))
    hold = float(config["action_hold_seconds"])
    pause = max(0.0, min(0.5, float(config["step_pause_seconds"])))
    mouse_step = max(1, min(200, int(config["mouse_step_pixels"])))
    try:
        while not stop_event.is_set():
            if esc_pressed() or not window_exists(target):
                break
            if foreground_window() != target:
                release_all_inputs()
                previous_frame = None
                static_streak = 0
                recent_actions.clear()
                time.sleep(0.08)
                continue
            current = sampler.capture_gray()
            if max(current) - min(current) < 3:
                black_frames += 1
            feature = make_feature(current, previous_frame)
            previous_frame = current
            probabilities = model_probabilities(np, model, feature)
            action_index = choose_policy_action(np, probabilities, exploration, recent_actions, static_streak)
            execute_action(target, profile["actions"][action_index], hold, mouse_step)
            if pause:
                time.sleep(pause)
            next_frame = sampler.capture_gray()
            next_feature = make_feature(next_frame, current)
            motion = feature_motion(next_feature)
            digest = frame_hash(next_frame)
            novelty = 0.12 if digest not in seen_frames else 0.0
            if motion < 0.006:
                static_streak += 1
            else:
                static_streak = 0
            static_penalty = min(0.35, static_streak * 0.025) if action_index != 0 else 0.0
            reward = min(1.0, motion * 5.0) + novelty - static_penalty
            rows.append((now_text(), "ai", action_index, float(reward), FEATURE_DIM, compress_feature(feature)))
            if len(rows) >= 100:
                insert_samples(paths["db"], rows)
                rows.clear()
            seen_frames.add(digest)
            if len(seen_frames) > 4096:
                seen_frames.clear()
            recent_actions.append(action_index)
            if len(recent_actions) > 12:
                recent_actions.pop(0)
            steps += 1
    finally:
        release_all_inputs()
        if rows:
            insert_samples(paths["db"], rows)
        sampler.close()
        compact_experience(paths["db"], int(config["experience_limit_per_game"]), len(profile["actions"]))
        wait_esc_release()
    warning = "；画面可能未被正确采集" if black_frames > max(20, steps // 2) else ""
    return f"AI结束：{profile['name']}；执行 {steps} 步；经验池原有 {total} 条{warning}"


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
        self.escape_was_down = esc_pressed() if os.name == "nt" else False

        tk.Label(self.root, text=f"AnyGameAI {APP_VERSION}", font=("Segoe UI", 24, "bold")).pack(pady=(22, 8))
        tk.Label(
            self.root,
            text="选择模式后切换到游戏窗口；ESC 结束当前模式",
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
            self.stop_event.set()
            self.status.set("正在结束…")
        else:
            self.stop_and_close()

    def set_busy(self, value: bool) -> None:
        self.busy = value
        state = tk.DISABLED if value else tk.NORMAL
        for button in (self.file_button, self.human_button, self.upgrade_button, self.ai_button):
            button.config(state=state)

    def stop_and_close(self) -> None:
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
                    if not self.stop_event.is_set():
                        self.stop_event.set()
                        self.status.set("正在结束…")
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
        self.root.after(60, self.poll_worker)

    def worker_done(self, result, error: str | None, hidden: bool) -> None:
        if os.name == "nt":
            release_all_inputs()
        if hidden:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        self.set_busy(False)
        if self.close_requested:
            self.close_requested = False
            self.stop_and_close()
            return
        if error:
            if "操作已取消" in error:
                self.status.set("已结束")
                return
            self.status.set("失败；详情见桌面 AnyGameAI 文件夹中的日志")
            detail = error.strip().splitlines()[-1] if error.strip() else "未知错误"
            messagebox.showerror(
                APP_NAME,
                f"运行失败：{detail}\n\n详情已写入桌面 AnyGameAI 文件夹中的日志。",
            )
            return
        self.status.set(str(result) if result else "已结束")

    def file_mode(self) -> None:
        def work():
            result = ensure_files(self.stop_event, download=True)
            if self.stop_event.is_set():
                return "文件检查已结束"
            parts = [
                f"修复 {result['repaired']} 项",
                f"下载 {result['downloaded']} 项",
                f"经验 {result['records']} 条",
                f"清理 {result['removed']} 条",
            ]
            if result.get("remote_error"):
                parts.append("远程更新失败，本地文件仍可用")
            if result.get("restart_required"):
                parts.append("主程序已更新，请按 ESC 退出后重新运行")
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
        self.run_worker("正在训练视觉模型并整理所有游戏的经验池；ESC 可取消", lambda: train_all_profiles(self.stop_event))

    def ai_mode(self) -> None:
        def work():
            target = wait_for_target_window(self.stop_event)
            if not target:
                wait_esc_release()
                return "未检测到游戏窗口，AI 模式已结束"
            return run_ai_session(target, self.stop_event)

        self.run_worker("请切换到已示范并升级过的游戏窗口；AI 正在运行；ESC 结束", work, hide=True)

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
