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
import struct
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
APP_VERSION = "80.0"
SCRIPT_NAME = "AnyGameAI.py"
RELEASE_SOURCE_SHA256 = "33fe3fd1b4986a4ebb60aed059b796bb10d83a140e217550575913343f92b226"
REQUIRED_PYTHON_VERSION = (3, 12)
MIN_WINDOWS_11_BUILD = 22000
SUPPORTED_X64_MACHINES = frozenset({"amd64", "x86_64"})
APP_SCHEMA = 13
CONFIG_SCHEMA = 35
PROFILE_SCHEMA = 23
MODEL_SCHEMA = 20
DATABASE_SCHEMA = 14
FEATURE_WIDTH = 96
FEATURE_HEIGHT = 54
LOW_CAPTURE_WIDTH = FEATURE_WIDTH
LOW_CAPTURE_HEIGHT = FEATURE_HEIGHT
HIGH_CAPTURE_WIDTH = 160
HIGH_CAPTURE_HEIGHT = 90
COLOR_WIDTH = FEATURE_WIDTH
COLOR_HEIGHT = FEATURE_HEIGHT
COLOR_PIXELS = COLOR_WIDTH * COLOR_HEIGHT
LEGACY_FEATURE_WIDTH = 40
LEGACY_FEATURE_HEIGHT = 24
LEGACY_COLOR_WIDTH = LEGACY_FEATURE_WIDTH // 2
LEGACY_COLOR_HEIGHT = LEGACY_FEATURE_HEIGHT // 2
LEGACY_COLOR_PIXELS = LEGACY_COLOR_WIDTH * LEGACY_COLOR_HEIGHT
LEGACY_FEATURE_DIM = LEGACY_FEATURE_WIDTH * LEGACY_FEATURE_HEIGHT * 2
V27_FEATURE_DIM = LEGACY_FEATURE_WIDTH * LEGACY_FEATURE_HEIGHT * 3
V69_FEATURE_DIM = V27_FEATURE_DIM + LEGACY_COLOR_PIXELS * 2
COLOR_FEATURE_DIM = COLOR_PIXELS * 2
BASE_FEATURE_DIM = FEATURE_WIDTH * FEATURE_HEIGHT * 3 + COLOR_FEATURE_DIM
V74_FEATURE_DIM = BASE_FEATURE_DIM
SPATIAL_FULL_WIDTH = HIGH_CAPTURE_WIDTH
SPATIAL_FULL_HEIGHT = HIGH_CAPTURE_HEIGHT
SPATIAL_FULL_PIXELS = SPATIAL_FULL_WIDTH * SPATIAL_FULL_HEIGHT
SPATIAL_HUD_STRIP_HEIGHT = 12
SPATIAL_HUD_HEIGHT = SPATIAL_HUD_STRIP_HEIGHT * 2
SPATIAL_HUD_PIXELS = SPATIAL_FULL_WIDTH * SPATIAL_HUD_HEIGHT
SPATIAL_MOUSE_SIZE = 48
SPATIAL_MOUSE_PIXELS = SPATIAL_MOUSE_SIZE * SPATIAL_MOUSE_SIZE
SPATIAL_CONTEXT_DIM = SPATIAL_FULL_PIXELS + SPATIAL_HUD_PIXELS + SPATIAL_MOUSE_PIXELS
SPATIAL_FULL_POOL_ROWS = 6
SPATIAL_FULL_POOL_COLUMNS = 10
SPATIAL_HUD_POOL_ROWS = 4
SPATIAL_HUD_POOL_COLUMNS = 10
SPATIAL_MOUSE_POOL_ROWS = 8
SPATIAL_MOUSE_POOL_COLUMNS = 8
SPATIAL_BRANCH_FEATURE_DIM = 2 * (
    SPATIAL_FULL_POOL_ROWS * SPATIAL_FULL_POOL_COLUMNS
    + SPATIAL_HUD_POOL_ROWS * SPATIAL_HUD_POOL_COLUMNS
    + SPATIAL_MOUSE_POOL_ROWS * SPATIAL_MOUSE_POOL_COLUMNS
)
FEATURE_DIM = BASE_FEATURE_DIM + SPATIAL_CONTEXT_DIM
MODEL_PIXEL_CHANNELS = 6
Q_TWIN_COUNT = 2
WORLD_MODEL_MEMBERS = 3
REWARD_MODEL_MEMBERS = 3
REWARD_MODEL_OUTPUTS = 5
ACTION_EMBEDDING_SIZE = 48
DURATION_EMBEDDING_SIZE = 8
ACTION_CONTEXT_SCALAR_FEATURES = 11
MODEL_GLOBAL_FEATURES = ACTION_EMBEDDING_SIZE + DURATION_EMBEDDING_SIZE + ACTION_CONTEXT_SCALAR_FEATURES
V27_MODEL_INPUT_DIM = V27_FEATURE_DIM
MODEL_INPUT_DIM = FEATURE_DIM
LEGACY_MODEL_INPUT_DIM = LEGACY_FEATURE_DIM
MAX_COMPRESSED_FEATURE_BYTES = FEATURE_DIM * 2 + 256
DEFAULT_HIDDEN_SIZE = 512
TEACHER_HIDDEN_SIZE = 768
TARGET_NETWORK_SYNC_STEPS_DEFAULT = 128
TARGET_NETWORK_SOFT_UPDATE_DEFAULT = 0.12
TARGET_ENSEMBLE_WEIGHT_DEFAULT = 0.28
MODEL_UNCERTAINTY_WEIGHT_DEFAULT = 0.14
ONLINE_REPRESENTATION_SCALE_DEFAULT = 0.08
ONLINE_INPUT_ADAPTATION_SCALE_DEFAULT = 0.16
ONLINE_INPUT_ADAPTATION_FEATURES_DEFAULT = 96
OPTIMIZER_WARMUP_STEPS_DEFAULT = 512
OPTIMIZER_COSINE_STEPS_DEFAULT = 24000
OPTIMIZER_WEIGHT_DECAY_DEFAULT = 0.0001
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
INTEGRITY_SCHEMA = 5
RUNTIME_INTEGRITY_SCHEMA = 3
GLOBAL_PRIOR_SCHEMA = 15
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
MAX_MODEL_ARCHIVE_BYTES = 768 * 1024 * 1024
MAX_MODEL_EXPANDED_BYTES = 1536 * 1024 * 1024
MAX_MODEL_ARCHIVE_MEMBERS = 128
TRAINING_MEMMAP_THRESHOLD_BYTES = 320 * 1024 * 1024
GLOBAL_TRAINING_SAMPLE_LIMIT = 40_000
GLOBAL_TRAINING_MIN_PER_PROFILE = 16
POLICY_AVOIDANCE_WEIGHT = 0.30
CORRUPT_BACKUP_LIMIT = 3
UNIVERSAL_ACTION_SCHEMA = 13
UNIVERSAL_ACTION_LIMIT = 256
DELAYED_REWARD_HORIZON_DEFAULT = 12
DELAYED_REWARD_DISCOUNT_DEFAULT = 0.92
CONTROL_KINDS = ("idle", "keyboard", "pointer", "click", "wheel", "mixed")
TEMPORAL_FRAMES = 4
ACTION_HISTORY_LENGTH = 4
TRAIN_SEQUENCE_LENGTH = 96
TRAIN_BURN_IN_STEPS = 32
DURATION_HEAD_SIZE = 5
DURATION_SECONDS = (0.035, 0.070, 0.130, 0.230, 0.350)
KEY_HEAD_SIZE = 256
BUTTON_HEAD_SIZE = 5
MOUSE_HEAD_SIZE = 608
CRITIC_NAMES = ("task", "exploration", "safety")
TASK_CRITIC = 0
EXPLORATION_CRITIC = 1
SAFETY_CRITIC = 2
VALUE_HEAD_COUNT = len(CRITIC_NAMES)
SKILL_HEAD_SIZE = 128
SKILL_MIN_STEPS = 4
SKILL_MAX_STEPS = 32
SKILL_EXECUTION_LIMIT = 32
PROGRESS_RANK_MARGIN = 0.20
ONLINE_REPLAY_CAPACITY_DEFAULT = 1024
ONLINE_REPLAY_BATCH_DEFAULT = 32
ONLINE_REPLAY_INTERVAL_DEFAULT = 4
CNN_CHANNELS = 24
CNN_MID_CHANNELS = 48
CNN_OUTPUT_CHANNELS = 64
CNN_POOL_ROWS = 3
CNN_POOL_COLUMNS = 5
CNN_MID_POOL_ROWS = 2
CNN_MID_POOL_COLUMNS = 4
GRU_INPUT_SIZE = 128
WORLD_LATENT_SIZE = 96
WORLD_MODEL_BEAM_WIDTH = 12
WORLD_MODEL_BRANCH_FACTOR = 8
WORLD_MODEL_MIN_TRAINING_STEPS = 2048
WORLD_MODEL_FULL_CONFIDENCE_STEPS = 8192
VISUAL_INITIALIZATION_SEED = 0x0A70C0DE
N_STEP_HORIZON_DEFAULT = 12
VALIDATION_EPISODE_FRACTION = 0.16
TEMPORAL_STATE_MAGIC = b"AGT3"
LEGACY_TEMPORAL_STATE_MAGIC = b"AGT2"
QUANTIZED_VISION_MODEL_NAME = "vision_qlinear_v1.onnx"
ONNXRUNTIME_REQUIREMENT = "onnxruntime>=1.18,<2"
ONNXRUNTIME_DIRECTML_REQUIREMENT = "onnxruntime-directml>=1.18,<2"
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
STABLE_STATE_KEY_PATTERN = re.compile(r"v:[0-9a-f]{16}\Z")
MODEL_ARCHIVE_V16_REQUIRED_MEMBERS = frozenset({
    "schema.npy", "input_dim.npy", "hidden_size.npy", "output_size.npy",
    "temporal_frames.npy", "conv_w.npy", "conv_scale.npy", "conv_b.npy",
    "conv_master_w.npy", "conv2_depthwise_w.npy", "conv2_pointwise_w.npy",
    "conv2_b.npy", "conv3_depthwise_w.npy", "conv3_pointwise_w.npy",
    "conv3_b.npy", "frame_proj.npy", "frame_bias.npy",
    "wz.npy", "uz.npy", "bz.npy", "wr.npy", "ur.npy", "br.npy",
    "wh.npy", "uh.npy", "bh.npy",
    "policy_control_w.npy", "policy_control_b.npy", "policy_key_w.npy",
    "policy_key_b.npy", "policy_mouse_w.npy", "policy_mouse_b.npy",
    "policy_button_w.npy", "policy_button_b.npy",
    "policy_duration_w.npy", "policy_duration_b.npy",
    "policy_action_w.npy", "policy_action_b.npy",
    "q_control_w.npy", "q_control_b.npy", "q_key_w.npy", "q_key_b.npy",
    "q_mouse_w.npy", "q_mouse_b.npy", "q_button_w.npy", "q_button_b.npy",
    "q_duration_w.npy", "q_duration_b.npy",
    "q_action_w.npy", "q_action_b.npy", "value_w.npy", "value_b.npy",
    "progress_w.npy", "progress_b.npy",
    "policy_skill_w.npy", "policy_skill_b.npy",
    "skill_value_w.npy", "skill_value_b.npy",
    "policy_duration_kind_b.npy", "q_duration_kind_b.npy",
    "mouse_offset_w.npy", "mouse_offset_b.npy",
    "action_factors.npy", "action_key_multihot.npy", "action_button_multihot.npy",
    "trained_samples.npy", "training_rounds.npy",
    "online_updates.npy", "action_hash.npy", "action_signatures.npy",
})
MODEL_ARCHIVE_V18_REQUIRED_MEMBERS = MODEL_ARCHIVE_V16_REQUIRED_MEMBERS | frozenset({
    "critic_names.npy", "action_embedding.npy", "duration_embedding.npy",
    "q_twin_count.npy",
    "safety_w.npy", "safety_b.npy",
    "world_model_members.npy",
    "world_encoder_w.npy", "world_encoder_b.npy",
    "world_dynamics_w.npy", "world_dynamics_action_w.npy", "world_dynamics_b.npy",
    "world_reward_w.npy", "world_reward_action_w.npy", "world_reward_b.npy",
    "world_done_w.npy", "world_done_b.npy",
    "visual_pretraining_steps.npy", "world_training_steps.npy",
    "optimizer_step.npy", "optimizer_schedule_step.npy",
    "optimizer_keys.npy", "optimizer_offsets.npy",
    "optimizer_m.npy", "optimizer_v.npy",
})
MODEL_ARCHIVE_V19_REQUIRED_MEMBERS = MODEL_ARCHIVE_V18_REQUIRED_MEMBERS | frozenset({
    "world_dynamics_duration_w.npy", "world_reward_duration_w.npy",
})
MODEL_ARCHIVE_REQUIRED_MEMBERS = MODEL_ARCHIVE_V19_REQUIRED_MEMBERS | frozenset({
    "world_latent_to_hidden_w.npy", "world_latent_to_hidden_b.npy",
    "reward_model_w.npy", "reward_model_b.npy", "reward_model_training_steps.npy",
})
MODEL_ARCHIVE_ALLOWED_MEMBERS = MODEL_ARCHIVE_REQUIRED_MEMBERS | frozenset({
    "updated_at.npy", "runtime_tier.npy", "validation_score.npy",
})
GLOBAL_ARCHIVE_REQUIRED_MEMBERS = frozenset({
    "schema.npy", "policy_control_b.npy", "policy_key_b.npy",
    "policy_mouse_b.npy", "policy_button_b.npy", "policy_duration_b.npy",
    "q_control_b.npy", "q_key_b.npy", "q_mouse_b.npy", "q_button_b.npy",
    "q_duration_b.npy",
    "trained_samples.npy", "training_rounds.npy", "source_profile.npy",
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
    "build_temporal_state", "insert_transitions", "load_transition_graph",
    "factorized_action_outputs", "hardware_capability_tier",
    "ensure_accelerated_runtime", "quantized_vision_model_bytes",
    "recurrent_model_step", "recurrent_ensemble_outputs",
    "stable_visual_state_key", "contiguous_trajectory_records",
    "sequence_training_windows", "evaluate_model_records", "compose_reward",
    "recognize_hud_score", "pretrain_visual_encoder",
    "latent_world_model_plan_values", "train_world_model_transition",
})
REQUIRED_APP_METHODS = frozenset({
    "file_mode", "human_mode", "upgrade_mode", "ai_mode", "on_escape",
})
REQUIRED_NATIVE_APP_METHODS = frozenset({
    "file_mode", "human_mode", "upgrade_mode", "ai_mode", "on_escape",
    "stop_and_close", "run_worker", "poll_worker", "worker_done", "run",
})
REQUIRED_SCRIPT_CALLS = {
    "main": frozenset({"configure_runtime_environment", "bootstrap_to_desktop", "AnyGameAIApp", "NativeAnyGameAIApp"}),
    "ensure_files": frozenset({"repair_main_script", "ensure_numpy", "ensure_accelerated_runtime", "runtime_self_check", "repair_profile", "verify_main_script_integrity"}),
    "ensure_runtime_ready": frozenset({"ensure_core_ready", "ensure_numpy", "import_numpy", "runtime_self_check"}),
    "record_human_session": frozenset({"ensure_core_ready", "profile_identity", "observe_human_action", "build_temporal_state", "insert_transitions", "update_human_action_memory", "save_human_action_memory", "adaptive_runtime_settings", "compose_reward"}),
    "train_all_profiles": frozenset({"ensure_runtime_ready", "load_training_data", "train_model", "refresh_global_prior", "save_model"}),
    "run_ai_session": frozenset({"ensure_runtime_ready", "profile_identity", "execute_action", "temporal_policy_blend", "load_human_action_memory", "human_action_memory_biases", "soft_update_target_model", "recurrent_ensemble_outputs", "adaptive_exploration_rate", "adaptive_runtime_settings", "load_transition_graph", "load_state_value_memory", "infer_scene_context", "action_safety_penalty", "target_action_blocked", "choose_recovery_action", "insert_transitions", "save_model", "compose_reward", "latent_world_model_plan_values"}),
    "train_model": frozenset({"sequence_training_windows", "evaluate_model_records", "soft_update_target_model", "pretrain_visual_encoder", "train_world_model_transition"}),
    "classify_transition_reward": frozenset({"compose_reward", "recognize_hud_score"}),
    "load_training_data": frozenset({"decode_temporal_state", "compose_reward", "contiguous_trajectory_records"}),
    "online_model_update": frozenset({"temporal_critic_targets", "train_world_model_transition"}),
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
ONNX_SESSION_LOCK = threading.RLock()
ONNX_SESSION_CACHE: dict[str, object] = {}
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
    providers: tuple[str, ...] | list[str] | None = None,
) -> dict[str, int | float | str | bool]:
    memory = available_physical_memory_bytes() if available_memory_bytes is None else max(0, int(available_memory_bytes))
    processors = max(1, int(os.cpu_count() or 1) if cpu_count is None else int(cpu_count))
    gib = 1024 ** 3
    tier = hardware_capability_tier(memory, processors, providers)
    sample_interval = max(0.02, min(1.0, float(config.get("sample_interval_seconds", 0.070))))
    step_pause = max(0.0, min(2.0, float(config.get("step_pause_seconds", 0.025))))
    confirmation_delay = max(0.0, min(0.25, float(config.get("confirmation_delay_seconds", 0.035))))
    planning_horizon = max(2, min(12, int(config.get("planning_horizon", 6))))
    planning_refresh_steps = max(8, min(512, int(config.get("planning_refresh_steps", 48))))
    online_checkpoint_steps = max(32, min(10000, int(config.get("online_checkpoint_steps", 256))))
    translation_search_radius = max(1, min(4, int(config.get("translation_search_radius", 2))))
    if tier == "low_numpy":
        sample_interval = max(sample_interval, 0.095)
        step_pause = max(step_pause, 0.035)
        confirmation_delay = min(confirmation_delay, 0.025)
        planning_horizon = min(planning_horizon, 4)
        planning_refresh_steps = max(planning_refresh_steps, 80)
        online_checkpoint_steps = max(online_checkpoint_steps, 512)
        translation_search_radius = min(translation_search_radius, 2)
    elif tier == "high_directml":
        sample_interval = min(sample_interval, 0.050)
        step_pause = min(step_pause, 0.016)
        planning_horizon = max(8, planning_horizon)
        planning_refresh_steps = min(planning_refresh_steps, 28)
        online_checkpoint_steps = min(online_checkpoint_steps, 160)
        translation_search_radius = max(translation_search_radius, 3)
    else:
        sample_interval = min(sample_interval, 0.065)
        step_pause = min(step_pause, 0.023)
        planning_horizon = max(6, planning_horizon)
        planning_refresh_steps = min(planning_refresh_steps, 40)
        online_checkpoint_steps = min(online_checkpoint_steps, 224)
    if tier == "low_numpy":
        model_hidden_size, sequence_length, burn_in_steps = 256, 96, 32
        replay_capacity, replay_batch = 1024, 32
        latent_horizon = 0
    elif tier == "high_directml":
        model_hidden_size, sequence_length, burn_in_steps = 768, 256, 64
        replay_capacity, replay_batch = 8192, 128
        latent_horizon = max(8, min(12, planning_horizon))
    else:
        model_hidden_size, sequence_length, burn_in_steps = 512, 192, 64
        replay_capacity, replay_batch = 4096, 64
        latent_horizon = max(6, min(12, planning_horizon))
    return {
        "hardware_tier": tier,
        "hidden_size": model_hidden_size,
        "sequence_length": sequence_length,
        "burn_in_steps": burn_in_steps,
        "online_replay_capacity": replay_capacity,
        "online_replay_batch_size": replay_batch,
        "use_latent_world_model": latent_horizon > 0,
        "latent_planning_horizon": latent_horizon,
        "use_onnx": tier != "low_numpy",
        "sample_interval_seconds": max(0.02, min(1.0, sample_interval)),
        "step_pause_seconds": max(0.0, min(2.0, step_pause)),
        "confirmation_delay_seconds": max(0.0, min(0.25, confirmation_delay)),
        "planning_horizon": max(2, min(12, planning_horizon)),
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
QUANTIZED_VISION_MODEL_PATH = RUNTIME_DIR / QUANTIZED_VISION_MODEL_NAME

DEFAULT_CONFIG = {
    "schema": CONFIG_SCHEMA,
    "sample_interval_seconds": 0.070,
    "action_hold_seconds": 0.075,
    "step_pause_seconds": 0.025,
    "exploration": 0.07,
    "mouse_step_pixels": 24,
    "max_action_count": 256,
    "experience_limit_per_game": 90000,
    "train_sample_limit_per_game": 32000,
    "training_epochs": 16,
    "training_batch_size": 128,
    "learning_rate": 0.0008,
    "learning_rate_warmup_steps": OPTIMIZER_WARMUP_STEPS_DEFAULT,
    "learning_rate_cosine_steps": OPTIMIZER_COSINE_STEPS_DEFAULT,
    "weight_decay": OPTIMIZER_WEIGHT_DECAY_DEFAULT,
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
    "online_model_learning_rate": 0.00015,
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
    "planning_horizon": 8,
    "planning_discount": 0.85,
    "planning_weight": 0.28,
    "planning_disagreement_penalty": 0.45,
    "planning_refresh_steps": 48,
    "cross_game_control_weight": 0.35,
    "cross_game_scene_weight": 0.38,
    "cross_game_action_weight": 0.32,
    "scene_action_memory_weight": 0.30,
    "contextual_probe_weight": 0.55,
    "persistent_novelty_weight": 0.12,
    "successful_transition_threshold": 0.08,
    "adaptive_hold_strength": 0.35,
    "parameterized_action_strength": 0.65,
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
    "n_step_horizon": 16,
    "validation_episode_fraction": VALIDATION_EPISODE_FRACTION,
    "behavior_cloning_weight": 1.4,
    "iql_expectile": 0.80,
    "iql_temperature": 1.5,
    "task_reward_weight": 1.0,
    "exploration_reward_weight": 0.18,
    "safety_penalty_weight": 0.70,
    "minimum_human_transitions": 64,
    "candidate_min_improvement": 0.01,
    "minimum_validation_episodes": 8,
    "sequence_length": TRAIN_SEQUENCE_LENGTH,
    "burn_in_steps": TRAIN_BURN_IN_STEPS,
    "visual_change_reward_weight": 0.025,
    "score_signal_weight": 0.55,
    "death_signal_weight": 0.90,
    "menu_transition_penalty": 0.06,
    "jitter_penalty_weight": 0.28,
    "progress_margin": PROGRESS_RANK_MARGIN,
    "progress_pair_weight": 1.0,
    "progress_reward_scale": 1.0,
    "heuristic_task_aux_weight": 0.12,
    "world_uncertainty_penalty": 0.18,
    "skill_min_steps": SKILL_MIN_STEPS,
    "skill_max_steps": SKILL_MAX_STEPS,
    "skill_limit": SKILL_HEAD_SIZE,
    "skill_policy_weight": 0.35,
    "skill_start_probability": 0.30,
    "online_replay_capacity": ONLINE_REPLAY_CAPACITY_DEFAULT,
    "online_replay_batch_size": ONLINE_REPLAY_BATCH_DEFAULT,
    "online_replay_interval": ONLINE_REPLAY_INTERVAL_DEFAULT,
    "action_freeze_min_tests": 12,
    "action_freeze_effect_threshold": 0.006,
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
    "learning_rate_warmup_steps": (1, 1000000),
    "learning_rate_cosine_steps": (16, 10000000),
    "weight_decay": (0.0, 0.1),
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
    "planning_horizon": (1, 12),
    "planning_discount": (0.1, 0.95),
    "planning_weight": (0.0, 1.0),
    "planning_disagreement_penalty": (0.0, 2.0),
    "planning_refresh_steps": (8, 512),
    "cross_game_control_weight": (0.0, 1.0),
    "cross_game_scene_weight": (0.0, 1.0),
    "cross_game_action_weight": (0.0, 1.0),
    "scene_action_memory_weight": (0.0, 1.0),
    "contextual_probe_weight": (0.0, 1.0),
    "persistent_novelty_weight": (0.0, 1.0),
    "successful_transition_threshold": (-1.0, 1.0),
    "adaptive_hold_strength": (0.0, 1.0),
    "parameterized_action_strength": (0.0, 1.0),
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
    "n_step_horizon": (10, 20),
    "validation_episode_fraction": (0.05, 0.35),
    "behavior_cloning_weight": (0.1, 4.0),
    "iql_expectile": (0.5, 0.95),
    "iql_temperature": (0.25, 10.0),
    "task_reward_weight": (0.0, 2.0),
    "exploration_reward_weight": (0.0, 1.0),
    "safety_penalty_weight": (0.0, 2.0),
    "minimum_human_transitions": (8, 10000),
    "candidate_min_improvement": (0.0, 0.25),
    "minimum_validation_episodes": (1, 1000),
    "sequence_length": (32, 256),
    "burn_in_steps": (4, 64),
    "visual_change_reward_weight": (0.0, 0.10),
    "score_signal_weight": (0.0, 1.5),
    "death_signal_weight": (0.0, 2.0),
    "menu_transition_penalty": (0.0, 0.5),
    "jitter_penalty_weight": (0.0, 1.0),
    "progress_margin": (0.01, 1.0),
    "progress_pair_weight": (0.0, 4.0),
    "progress_reward_scale": (0.05, 4.0),
    "heuristic_task_aux_weight": (0.0, 0.5),
    "world_uncertainty_penalty": (0.0, 2.0),
    "skill_min_steps": (4, 16),
    "skill_max_steps": (8, 32),
    "skill_limit": (8, SKILL_HEAD_SIZE),
    "skill_policy_weight": (0.0, 2.0),
    "skill_start_probability": (0.0, 1.0),
    "online_replay_capacity": (128, 16384),
    "online_replay_batch_size": (8, 256),
    "online_replay_interval": (1, 64),
    "action_freeze_min_tests": (1, 10000),
    "action_freeze_effect_threshold": (0.0, 0.25),
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
            and schema in (1, 2, 3, 4, INTEGRITY_SCHEMA)
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
    if int(data["burn_in_steps"]) >= int(data["sequence_length"]):
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
                if source_schema < 32:
                    if abs(float(merged.get("candidate_min_improvement", 0.0)) - 0.002) < 1e-12:
                        merged["candidate_min_improvement"] = 0.01
                    if int(merged.get("sequence_length", 0)) == 64:
                        merged["sequence_length"] = TRAIN_SEQUENCE_LENGTH
                    if int(merged.get("burn_in_steps", 0)) == 16:
                        merged["burn_in_steps"] = TRAIN_BURN_IN_STEPS
                if source_schema < 33:
                    if int(merged.get("burn_in_steps", 0)) == 24:
                        merged["burn_in_steps"] = TRAIN_BURN_IN_STEPS
                    if int(merged.get("online_replay_capacity", 0)) == 512:
                        merged["online_replay_capacity"] = ONLINE_REPLAY_CAPACITY_DEFAULT
                    if int(merged.get("online_replay_batch_size", 0)) == 16:
                        merged["online_replay_batch_size"] = ONLINE_REPLAY_BATCH_DEFAULT
                    if int(merged.get("planning_horizon", 0)) == 6:
                        merged["planning_horizon"] = 8
                if source_schema < 34:
                    merged["planning_disagreement_penalty"] = DEFAULT_CONFIG["planning_disagreement_penalty"]
                    merged["parameterized_action_strength"] = DEFAULT_CONFIG["parameterized_action_strength"]
                if source_schema < 35:
                    merged["minimum_validation_episodes"] = DEFAULT_CONFIG["minimum_validation_episodes"]
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
        if isinstance(raw, dict) and raw.get("schema") in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, APP_SCHEMA) and isinstance(raw.get("profiles"), dict):
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
        data=read_json_file(RUNTIME_INTEGRITY_PATH,MAX_SMALL_JSON_BYTES)
        valid=(isinstance(data,dict) and data.get("schema")==RUNTIME_INTEGRITY_SCHEMA and data.get("distribution")=="numpy" and isinstance(data.get("version"),str) and supported_numpy_version(data["version"]) and isinstance(data.get("file_count"),int) and 8<=int(data["file_count"])<=MAX_DISTRIBUTION_RECORDS and isinstance(data.get("record_sha256"),str) and re.fullmatch(r"[0-9a-f]{64}",data["record_sha256"]) and isinstance(data.get("content_sha256"),str) and re.fullmatch(r"[0-9a-f]{64}",data["content_sha256"]) and isinstance(data.get("tree_file_count"),int) and int(data["file_count"])<=int(data["tree_file_count"])<=MAX_RUNTIME_TREE_FILES and isinstance(data.get("tree_size"),int) and 1<=int(data["tree_size"])<=MAX_RUNTIME_TREE_BYTES and isinstance(data.get("tree_sha256"),str) and re.fullmatch(r"[0-9a-f]{64}",data["tree_sha256"]))
        if valid:
            accelerator=str(data.get("accelerator",""));model_hash=str(data.get("vision_model_sha256",""))
            if accelerator and accelerator not in ("onnxruntime","directml"): return {}
            if model_hash and re.fullmatch(r"[0-9a-f]{64}",model_hash) is None: return {}
            return data
    except Exception: pass
    return {}



def save_runtime_integrity_state(snapshot: dict) -> None:
    data={"schema":RUNTIME_INTEGRITY_SCHEMA,"distribution":str(snapshot["distribution"]),"version":str(snapshot["version"]),"file_count":int(snapshot["file_count"]),"record_sha256":str(snapshot["record_sha256"]),"content_sha256":str(snapshot["content_sha256"]),"tree_file_count":int(snapshot["tree_file_count"]),"tree_size":int(snapshot["tree_size"]),"tree_sha256":str(snapshot["tree_sha256"]),"accelerator":str(snapshot.get("accelerator","")),"vision_model_sha256":str(snapshot.get("vision_model_sha256","")),"updated_at":now_text()}
    atomic_write_json(RUNTIME_INTEGRITY_PATH,data)



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

def _protobuf_varint(value: int) -> bytes:
    value=int(value)
    if value<0: value=(1<<64)+value
    out=bytearray()
    while value>0x7F:
        out.append((value&0x7F)|0x80);value>>=7
    out.append(value);return bytes(out)


def _protobuf_field_varint(number: int, value: int) -> bytes:
    return _protobuf_varint((int(number)<<3)|0)+_protobuf_varint(value)


def _protobuf_field_bytes(number: int, value: bytes) -> bytes:
    data=bytes(value);return _protobuf_varint((int(number)<<3)|2)+_protobuf_varint(len(data))+data


def _protobuf_field_text(number: int, value: str) -> bytes:
    return _protobuf_field_bytes(number,value.encode("utf-8"))


def _onnx_tensor(name: str, data_type: int, dims: tuple[int,...], raw_data: bytes) -> bytes:
    payload=bytearray()
    for dim in dims: payload.extend(_protobuf_field_varint(1,dim))
    payload.extend(_protobuf_field_varint(2,data_type));payload.extend(_protobuf_field_text(8,name));payload.extend(_protobuf_field_bytes(9,raw_data));return bytes(payload)


def _onnx_value_info(name: str, elem_type: int, dims: tuple[int,...]) -> bytes:
    shape=bytearray()
    for dim in dims:
        dimension=_protobuf_field_varint(1,dim);shape.extend(_protobuf_field_bytes(1,dimension))
    tensor_type=_protobuf_field_varint(1,elem_type)+_protobuf_field_bytes(2,bytes(shape))
    type_proto=_protobuf_field_bytes(1,tensor_type)
    return _protobuf_field_text(1,name)+_protobuf_field_bytes(2,type_proto)


def _onnx_node(op_type: str, inputs: tuple[str,...], outputs: tuple[str,...], name: str) -> bytes:
    payload=bytearray()
    for value in inputs: payload.extend(_protobuf_field_text(1,value))
    for value in outputs: payload.extend(_protobuf_field_text(2,value))
    payload.extend(_protobuf_field_text(3,name));payload.extend(_protobuf_field_text(4,op_type));return bytes(payload)



def quantized_vision_model_bytes(conv_w=None, conv_scale: float = 0.045, conv_b=None) -> bytes:
    if conv_w is None:
        conv_values = bytes(
            (((index * 7 + 3) % 15) - 7) & 0xFF
            for index in range(CNN_CHANNELS * MODEL_PIXEL_CHANNELS * 3 * 3)
        )
    else:
        raw = conv_w.astype("int8", copy=False).reshape(
            CNN_CHANNELS,
            MODEL_PIXEL_CHANNELS,
            3,
            3,
        )
        conv_values = raw.tobytes(order="C")
    scale = max(1e-8, float(conv_scale))
    if conv_b is None:
        bias_values = (0,) * CNN_CHANNELS
    else:
        bias_values = tuple(
            max(-(1 << 31), min((1 << 31) - 1, int(round(float(value) / (0.01 * scale)))))
            for value in conv_b
        )
    initializers = (
        _onnx_tensor("x_scale", 1, (), struct.pack("<f", 0.01)),
        _onnx_tensor("x_zero", 2, (), bytes([128])),
        _onnx_tensor("w", 3, (CNN_CHANNELS, MODEL_PIXEL_CHANNELS, 3, 3), conv_values),
        _onnx_tensor("w_scale", 1, (), struct.pack("<f", scale)),
        _onnx_tensor("w_zero", 3, (), bytes([0])),
        _onnx_tensor("y_scale", 1, (), struct.pack("<f", 0.02)),
        _onnx_tensor("y_zero", 2, (), bytes([0])),
        _onnx_tensor("bias", 6, (CNN_CHANNELS,), struct.pack("<" + "i" * CNN_CHANNELS, *bias_values)),
    )
    qconv = _onnx_node(
        "QLinearConv",
        ("input", "x_scale", "x_zero", "w", "w_scale", "w_zero", "y_scale", "y_zero", "bias"),
        ("conv_q",),
        "quantized_conv",
    )
    dequant = _onnx_node("DequantizeLinear", ("conv_q", "y_scale", "y_zero"), ("output",), "dequantize")
    graph = bytearray()
    graph.extend(_protobuf_field_bytes(1, qconv))
    graph.extend(_protobuf_field_bytes(1, dequant))
    graph.extend(_protobuf_field_text(2, "AnyGameAIQuantizedVision"))
    for tensor in initializers:
        graph.extend(_protobuf_field_bytes(5, tensor))
    graph.extend(
        _protobuf_field_bytes(
            11,
            _onnx_value_info(
                "input",
                2,
                (1, MODEL_PIXEL_CHANNELS, FEATURE_HEIGHT, FEATURE_WIDTH),
            ),
        )
    )
    graph.extend(_protobuf_field_bytes(12, _onnx_value_info("output", 1, (1, CNN_CHANNELS, FEATURE_HEIGHT - 2, FEATURE_WIDTH - 2))))
    opset = _protobuf_field_varint(2, 13)
    model = bytearray()
    model.extend(_protobuf_field_varint(1, 8))
    model.extend(_protobuf_field_text(2, APP_NAME))
    model.extend(_protobuf_field_text(3, APP_VERSION))
    model.extend(_protobuf_field_bytes(7, bytes(graph)))
    model.extend(_protobuf_field_bytes(8, opset))
    return bytes(model)


def ensure_quantized_vision_model() -> bool:
    expected=quantized_vision_model_bytes();changed=True
    if QUANTIZED_VISION_MODEL_PATH.is_file() and not QUANTIZED_VISION_MODEL_PATH.is_symlink():
        try: changed=QUANTIZED_VISION_MODEL_PATH.read_bytes()!=expected
        except OSError: changed=True
    if changed:
        QUANTIZED_VISION_MODEL_PATH.parent.mkdir(parents=True,exist_ok=True);temp=temporary_sibling_path(QUANTIZED_VISION_MODEL_PATH)
        try:
            with temp.open("xb") as file: file.write(expected);file.flush();os.fsync(file.fileno())
            os.replace(temp,QUANTIZED_VISION_MODEL_PATH)
        finally: temp.unlink(missing_ok=True)
    return changed


def clear_onnxruntime_modules() -> None:
    with ONNX_SESSION_LOCK: ONNX_SESSION_CACHE.clear()
    for name in list(sys.modules):
        if name=="onnxruntime" or name.startswith("onnxruntime."): sys.modules.pop(name,None)


def import_onnxruntime(local_only: bool = True):
    add_runtime_path();runtime_path=SITE_PACKAGES.resolve();module=sys.modules.get("onnxruntime")
    if module is not None and local_only:
        module_file=getattr(module,"__file__","");module_path=Path(module_file).resolve() if module_file else Path()
        if module_path!=runtime_path and runtime_path not in module_path.parents: clear_onnxruntime_modules();module=None
    if module is None: importlib.invalidate_caches();module=importlib.import_module("onnxruntime")
    module_path=Path(module.__file__).resolve()
    if local_only and module_path!=runtime_path and runtime_path not in module_path.parents: raise RuntimeError("未使用 AnyGameAI 本地 ONNX Runtime")
    return module



def accelerated_vision_session(model: dict | None = None):
    try:
        if model is None:
            payload = QUANTIZED_VISION_MODEL_PATH.read_bytes()
        else:
            payload = quantized_vision_model_bytes(
                model["conv_w"],
                float(model["conv_scale"][0]),
                model["conv_b"],
            )
        key = hashlib.sha256(payload).hexdigest()
    except Exception:
        return None
    with ONNX_SESSION_LOCK:
        cached = ONNX_SESSION_CACHE.get(key)
        if cached is not None:
            return cached
        try:
            ort = import_onnxruntime(True)
            providers = list(ort.get_available_providers())
            preferred = []
            if "DmlExecutionProvider" in providers:
                preferred.append("DmlExecutionProvider")
            if "CPUExecutionProvider" in providers:
                preferred.append("CPUExecutionProvider")
            session = ort.InferenceSession(payload, providers=preferred or providers)
            probe = import_numpy().zeros(
                (1, MODEL_PIXEL_CHANNELS, FEATURE_HEIGHT, FEATURE_WIDTH),
                dtype=import_numpy().uint8,
            )
            output = session.run(["output"], {"input": probe})[0]
            if tuple(output.shape) != (1, CNN_CHANNELS, FEATURE_HEIGHT - 2, FEATURE_WIDTH - 2):
                raise RuntimeError("量化视觉模型输出尺寸无效")
            ONNX_SESSION_CACHE[key] = session
            if len(ONNX_SESSION_CACHE) > 12:
                oldest = next(iter(ONNX_SESSION_CACHE))
                if oldest != key:
                    ONNX_SESSION_CACHE.pop(oldest, None)
            return session
        except Exception:
            return None


def local_onnx_probe_command(site_packages: Path, require_dml: bool) -> list[str]:
    code=("import sys;sys.path.insert(0,"+repr(str(site_packages))+ ");import onnxruntime as o;"
          "p=o.get_available_providers();assert 'CPUExecutionProvider' in p;"+("assert 'DmlExecutionProvider' in p;" if require_dml else "")+"print(o.__version__,p)")
    return [sys.executable,"-I","-c",code]


def ensure_accelerated_runtime(download: bool, stop_event: threading.Event | None = None) -> bool:
    tier=requested_hardware_tier()
    if tier=="low_numpy": return False
    require_dml=tier=="high_directml"
    requirement=ONNXRUNTIME_DIRECTML_REQUIREMENT if require_dml else ONNXRUNTIME_REQUIREMENT
    ensure_quantized_vision_model()
    code,output=run_process_cancelable(local_onnx_probe_command(SITE_PACKAGES,require_dml),stop_event,isolated_python_environment())
    state=load_runtime_integrity_state();expected_model_hash=sha256_file(QUANTIZED_VISION_MODEL_PATH)
    if code==0 and state and hmac.compare_digest(str(state.get("vision_model_sha256","")),expected_model_hash) and str(state.get("accelerator",""))==( "directml" if require_dml else "onnxruntime"):
        session=accelerated_vision_session()
        providers=tuple(session.get_providers()) if session is not None and hasattr(session,"get_providers") else ()
        if session is not None and (not require_dml or providers and providers[0]=="DmlExecutionProvider"):
            return False
    if not download:
        raise RuntimeError("中高配设备缺少或未校验量化 ONNX 运行组件，请先点击“文件”。")
    transaction_root=RUNTIME_DIR/f".update-onnx-{os.getpid()}-{time.time_ns()}";staged=transaction_root/"site-packages";rollback=transaction_root/"rollback-site-packages"
    transaction_root.mkdir(parents=True,exist_ok=True);shutil.copytree(SITE_PACKAGES,staged,dirs_exist_ok=True)
    environment=isolated_python_environment();environment.update({"TEMP":str(TEMP_DIR),"TMP":str(TEMP_DIR),"PIP_CACHE_DIR":str(TEMP_DIR/"pip-cache")})
    args=["--isolated","install","--upgrade","--disable-pip-version-check","--no-input","--no-cache-dir","--no-compile","--no-warn-script-location","--retries","3","--timeout","45","--only-binary=:all:","--target",str(staged),NUMPY_REQUIREMENT,requirement]
    commands=pip_install_commands(args);committed=False
    try:
        install_output=[];install_code=1
        for command in commands:
            install_code,part=run_process_cancelable(command,stop_event,environment);install_output.append(part)
            if install_code==0: break
        if install_code!=0:
            log_text("ONNX Runtime 安装失败:\n"+"\n".join(install_output)[-12000:]);raise RuntimeError("量化 ONNX 运行组件下载或安装失败。")
        probe_code,probe_output=run_process_cancelable(local_onnx_probe_command(staged,require_dml),stop_event,environment)
        if probe_code!=0: log_text("ONNX Runtime 自检失败:\n"+probe_output[-12000:]);raise RuntimeError("量化 ONNX 运行组件安装后自检失败。")
        verify_installed_distribution("numpy",stop_event,staged)
        clear_numpy_modules();clear_onnxruntime_modules();os.replace(SITE_PACKAGES,rollback);os.replace(staged,SITE_PACKAGES);committed=True
        try:
            importlib.invalidate_caches();import_numpy(True);ort=import_onnxruntime(True);providers=ort.get_available_providers()
            if require_dml and "DmlExecutionProvider" not in providers: raise RuntimeError("DirectML 提供程序缺失")
            snapshot=verify_installed_distribution("numpy",None,SITE_PACKAGES,collect_snapshot=True);snapshot["accelerator"]="directml" if require_dml else "onnxruntime";snapshot["vision_model_sha256"]=sha256_file(QUANTIZED_VISION_MODEL_PATH);save_runtime_integrity_state(snapshot)
            session=accelerated_vision_session()
            if session is None: raise RuntimeError("量化视觉模型无法加载")
            if require_dml and (
                not hasattr(session,"get_providers")
                or not session.get_providers()
                or session.get_providers()[0]!="DmlExecutionProvider"
            ):
                raise RuntimeError("量化视觉模型未实际使用 DirectML")
        except Exception as error:
            clear_numpy_modules();clear_onnxruntime_modules();shutil.rmtree(SITE_PACKAGES,ignore_errors=True);os.replace(rollback,SITE_PACKAGES);committed=False;raise RuntimeError("ONNX Runtime 替换后自检失败，已恢复原文件。") from error
        return True
    finally:
        if not committed and not SITE_PACKAGES.exists() and rollback.exists(): os.replace(rollback,SITE_PACKAGES)
        shutil.rmtree(transaction_root,ignore_errors=True)


def ensure_runtime_ready(stop_event: threading.Event | None = None):
    ensure_core_ready(stop_event);ensure_numpy(download=False,stop_event=stop_event);ensure_accelerated_runtime(download=False,stop_event=stop_event);np=import_numpy();runtime_self_check(np);return np




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
    def __init__(self, target_window: int, runtime_tier: str = "low_numpy"):
        self.window = target_window
        high_resolution = str(runtime_tier) == "high_directml"
        self.width = HIGH_CAPTURE_WIDTH if high_resolution else LOW_CAPTURE_WIDTH
        self.height = HIGH_CAPTURE_HEIGHT if high_resolution else LOW_CAPTURE_HEIGHT
        self.runtime_tier = "high_directml" if high_resolution else str(runtime_tier)
        self.last_spatial_context = bytes(SPATIAL_CONTEXT_DIM)
        self._candidate_spatial_context = self.last_spatial_context
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

    def _build_spatial_context(self, raw: bytes) -> bytes:
        if self.runtime_tier != "high_directml":
            return bytes(SPATIAL_CONTEXT_DIM)
        if self.width != SPATIAL_FULL_WIDTH or self.height != SPATIAL_FULL_HEIGHT:
            return bytes(SPATIAL_CONTEXT_DIM)
        full = bytearray(SPATIAL_FULL_PIXELS)
        for pixel in range(SPATIAL_FULL_PIXELS):
            source = pixel * 4
            b = raw[source]
            g = raw[source + 1]
            r = raw[source + 2]
            full[pixel] = (r * 77 + g * 150 + b * 29) >> 8
        strip = SPATIAL_HUD_STRIP_HEIGHT
        hud = bytes(full[:strip * SPATIAL_FULL_WIDTH]) + bytes(
            full[(SPATIAL_FULL_HEIGHT - strip) * SPATIAL_FULL_WIDTH:]
        )
        left, top, width, height = window_capture_rect(self.window)
        cursor_x, cursor_y = cursor_position()
        if width > 0 and height > 0 and left <= cursor_x < left + width and top <= cursor_y < top + height:
            center_x = max(0, min(SPATIAL_FULL_WIDTH - 1, int((cursor_x - left) * SPATIAL_FULL_WIDTH / width)))
            center_y = max(0, min(SPATIAL_FULL_HEIGHT - 1, int((cursor_y - top) * SPATIAL_FULL_HEIGHT / height)))
        else:
            center_x = SPATIAL_FULL_WIDTH // 2
            center_y = SPATIAL_FULL_HEIGHT // 2
        radius = SPATIAL_MOUSE_SIZE // 2
        mouse = bytearray(SPATIAL_MOUSE_PIXELS)
        for target_y in range(SPATIAL_MOUSE_SIZE):
            source_y = center_y - radius + target_y
            if not 0 <= source_y < SPATIAL_FULL_HEIGHT:
                continue
            for target_x in range(SPATIAL_MOUSE_SIZE):
                source_x = center_x - radius + target_x
                if 0 <= source_x < SPATIAL_FULL_WIDTH:
                    mouse[target_y * SPATIAL_MOUSE_SIZE + target_x] = full[
                        source_y * SPATIAL_FULL_WIDTH + source_x
                    ]
        context = bytes(full) + hud + bytes(mouse)
        if len(context) != SPATIAL_CONTEXT_DIM:
            raise RuntimeError("高精度空间分支尺寸无效")
        return context

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
        self._candidate_spatial_context = self._build_spatial_context(raw)
        gray = bytearray(FEATURE_WIDTH * FEATURE_HEIGHT)
        chroma_blue = bytearray(COLOR_PIXELS)
        chroma_red = bytearray(COLOR_PIXELS)
        for target_y in range(FEATURE_HEIGHT):
            source_y = min(self.height - 1, (target_y * self.height + self.height // 2) // FEATURE_HEIGHT)
            for target_x in range(FEATURE_WIDTH):
                source_x = min(self.width - 1, (target_x * self.width + self.width // 2) // FEATURE_WIDTH)
                source = (source_y * self.width + source_x) * 4
                target = target_y * FEATURE_WIDTH + target_x
                b = raw[source]
                g = raw[source + 1]
                r = raw[source + 2]
                gray[target] = (r * 77 + g * 150 + b * 29) >> 8
                chroma_blue[target] = b
                chroma_red[target] = r
        return bytes(gray), bytes(chroma_blue), bytes(chroma_red)

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
        color_presence = max(max(chroma_blue), max(chroma_red)) * 0.04
        visible_luminance = max(gray) * 0.05
        return max(float(gray_detail), float(color_detail), float(color_presence), float(visible_luminance))

    def capture_frame(self) -> tuple[bytes, bytes, bytes]:
        x, y, source_width, source_height = window_capture_rect(self.window)
        screen_frame = self._capture_from_dc(self.screen_dc, x, y, source_width, source_height)
        best_frame = screen_frame
        best_context = self._candidate_spatial_context
        best_detail = self._frame_detail(screen_frame)
        if best_detail >= 3:
            self.last_spatial_context = best_context
            return best_frame
        window_dc = user32.GetDC(self.window)
        if window_dc:
            try:
                window_frame = self._capture_from_dc(window_dc, 0, 0, source_width, source_height)
                window_context = self._candidate_spatial_context
                window_detail = self._frame_detail(window_frame)
                if window_detail > best_detail:
                    best_frame = window_frame
                    best_context = window_context
                    best_detail = window_detail
            except Exception:
                pass
            finally:
                user32.ReleaseDC(self.window, window_dc)
        if best_detail >= 3:
            self.last_spatial_context = best_context
            return best_frame
        try:
            printed = self._capture_print_window(source_width, source_height)
            printed_context = self._candidate_spatial_context
            if printed is not None and self._frame_detail(printed) > best_detail:
                self.last_spatial_context = printed_context
                return printed
        except Exception:
            pass
        self.last_spatial_context = best_context
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
    return max(chroma_blue) <= 2 and max(chroma_red) <= 2


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
    actions=profile.get("actions",[]);kind_counts:dict[str,int]={}
    try:
        ensure_database(database_path);connection=sqlite3.connect(database_path,timeout=20)
        try: rows=connection.execute("SELECT action,COUNT(*) FROM transitions WHERE source='human' GROUP BY action").fetchall()
        finally: connection.close()
        for action_id,count in rows:
            base_action,_=decode_action_id(int(action_id))
            if 0<=base_action<len(actions):
                kind=action_kind(actions[base_action]);kind_counts[kind]=kind_counts.get(kind,0)+max(0,int(count))
    except Exception: kind_counts={}
    active={kind:count for kind,count in kind_counts.items() if kind!="idle" and count>0}
    if active:
        maximum=max(active.values());preferences={kind:min(1.0,count/max(1,maximum)) for kind,count in active.items() if count>=max(2,sum(active.values())*0.02)}
        if kind_counts.get("idle",0)>0: preferences["idle"]=min(0.35,kind_counts["idle"]/max(1,sum(kind_counts.values())))
        return preferences
    origins=profile.get("action_origins",[]);fallback={action_kind(action) for index,action in enumerate(actions) if index<len(origins) and origins[index]=="human" and action_kind(action)!="idle"}
    return {kind:1.0 for kind in fallback}



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
    spatial_context: bytes | None = None,
) -> bytes:
    if len(current) != FEATURE_WIDTH * FEATURE_HEIGHT:
        raise ValueError("画面特征尺寸无效")
    if chroma_blue is None:
        chroma_blue = bytes(current)
    if chroma_red is None:
        chroma_red = bytes(current)
    if len(chroma_blue) != COLOR_PIXELS or len(chroma_red) != COLOR_PIXELS:
        raise ValueError("画面颜色特征尺寸无效")
    if spatial_context is None:
        spatial_context = bytes(SPATIAL_CONTEXT_DIM)
    if len(spatial_context) != SPATIAL_CONTEXT_DIM:
        raise ValueError("空间分支特征尺寸无效")
    if previous is None or len(previous) != len(current):
        difference = bytes(len(current))
        signed_change = bytes([128]) * len(current)
    else:
        difference = bytes(abs(a - b) for a, b in zip(current, previous))
        signed_change = bytes(
            max(0, min(255, (int(after) - int(before) + 256) // 2))
            for after, before in zip(current, previous)
        )
    return current + difference + signed_change + chroma_blue + chroma_red + bytes(spatial_context)


def feature_motion(feature: bytes) -> float:
    feature = normalize_feature_bytes(feature)
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    difference = feature[pixels:pixels * 2]
    return sum(difference) / max(1, len(difference)) / 255.0


def feature_chroma(feature: bytes) -> tuple[bytes, bytes]:
    normalized = normalize_feature_bytes(feature)
    start = FEATURE_WIDTH * FEATURE_HEIGHT * 3
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
    root = PROFILES_DIR / profile_id
    if root.exists() and path_is_unsafe_managed_entry(root):
        if not repair_unsafe:
            raise RuntimeError("游戏档案目录不能是链接、目录联接或硬链接")
        remove_unsafe_managed_entry(root)
    root.mkdir(parents=True, exist_ok=True)
    resolved_root = root.resolve()
    if PROFILES_DIR.resolve() not in resolved_root.parents:
        raise RuntimeError("游戏档案目录越界")
    paths = {
        "root": root,
        "profile": root / "profile.json",
        "db": root / "experience.sqlite3",
        "model": root / "teacher_model.npz",
        "best_model": root / "best_teacher_model.npz",
        "candidate_model": root / "candidate_teacher_model.npz",
        "target_model": root / "teacher_target_model.npz",
        "best_target_model": root / "best_teacher_target_model.npz",
        "candidate_target_model": root / "candidate_teacher_target_model.npz",
        "legacy_model": root / "model.npz",
        "legacy_best_model": root / "best_model.npz",
        "legacy_candidate_model": root / "candidate_model.npz",
        "legacy_target_model": root / "target_model.npz",
        "legacy_best_target_model": root / "best_target_model.npz",
        "legacy_candidate_target_model": root / "candidate_target_model.npz",
        "student_low": root / "student_low.npz",
        "student_mid": root / "student_mid.npz",
        "student_high": root / "student_high.npz",
        "student_low_target": root / "student_low_target.npz",
        "student_mid_target": root / "student_mid_target.npz",
        "student_high_target": root / "student_high_target.npz",
    }
    managed_files = (
        paths["profile"], paths["db"], paths["model"], paths["best_model"],
        paths["candidate_model"], paths["target_model"],
        paths["best_target_model"], paths["candidate_target_model"],
        paths["student_low"], paths["student_mid"], paths["student_high"],
        paths["student_low_target"], paths["student_mid_target"], paths["student_high_target"],
        paths["legacy_model"], paths["legacy_best_model"], paths["legacy_candidate_model"],
        paths["legacy_target_model"], paths["legacy_best_target_model"],
        paths["legacy_candidate_target_model"],
        Path(str(paths["db"]) + "-wal"), Path(str(paths["db"]) + "-shm"),
    )
    for path in managed_files:
        if path_is_unsafe_managed_entry(path):
            if not repair_unsafe:
                raise RuntimeError("游戏档案文件不能是链接、目录联接或硬链接")
            remove_unsafe_managed_entry(path)
        resolved = path.resolve(strict=False)
        if resolved == resolved_root or resolved_root not in resolved.parents:
            raise RuntimeError("游戏档案文件路径越界")
    legacy_pairs = (
        (paths["legacy_model"], paths["model"]),
        (paths["legacy_best_model"], paths["best_model"]),
        (paths["legacy_candidate_model"], paths["candidate_model"]),
        (paths["legacy_target_model"], paths["target_model"]),
        (paths["legacy_best_target_model"], paths["best_target_model"]),
        (paths["legacy_candidate_target_model"], paths["candidate_target_model"]),
    )
    for legacy_path, teacher_path in legacy_pairs:
        if not teacher_path.exists() and legacy_path.is_file() and not legacy_path.is_symlink():
            temp = temporary_sibling_path(teacher_path)
            try:
                shutil.copy2(legacy_path, temp)
                os.replace(temp, teacher_path)
            finally:
                temp.unlink(missing_ok=True)
    return paths


def runtime_student_tier(runtime_tier: str) -> str:
    if str(runtime_tier) == "low_numpy":
        return "low"
    if str(runtime_tier) == "high_directml":
        return "high"
    return "mid"


def runtime_student_paths(paths: dict[str, Path], runtime_tier: str) -> tuple[Path, Path]:
    tier = runtime_student_tier(runtime_tier)
    return paths[f"student_{tier}"], paths[f"student_{tier}_target"]


def runtime_student_hidden_size(runtime_tier: str) -> int:
    tier = runtime_student_tier(runtime_tier)
    return 256 if tier == "low" else 768 if tier == "high" else 512



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
        "skills": [],
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

    raw_skills = profile.get("skills")
    cleaned_skills = []
    seen_skills = set()
    if isinstance(raw_skills, list):
        for raw_skill in raw_skills[:SKILL_HEAD_SIZE * 2]:
            if not isinstance(raw_skill, dict):
                continue
            raw_actions = raw_skill.get("actions")
            raw_durations = raw_skill.get("durations")
            if not isinstance(raw_actions, list) or not SKILL_MIN_STEPS <= len(raw_actions) <= SKILL_MAX_STEPS:
                continue
            actions = []
            valid = True
            for value in raw_actions:
                try:
                    action_index = int(value)
                except (TypeError, ValueError):
                    valid = False
                    break
                if not 0 <= action_index < action_count:
                    valid = False
                    break
                actions.append(action_index)
            if not valid:
                continue
            durations = []
            if not isinstance(raw_durations, list):
                raw_durations = []
            for index in range(len(actions)):
                try:
                    duration_index = int(raw_durations[index])
                except (IndexError, TypeError, ValueError):
                    duration_index = DURATION_HEAD_SIZE // 2
                durations.append(max(0, min(DURATION_HEAD_SIZE - 1, duration_index)))
            signature = tuple(zip(actions, durations))
            if signature in seen_skills:
                continue
            seen_skills.add(signature)
            try:
                count = max(1, min(1_000_000_000, int(raw_skill.get("count", 1))))
                quality = float(raw_skill.get("quality", 0.0))
            except (TypeError, ValueError):
                count, quality = 1, 0.0
            if not math.isfinite(quality):
                quality = 0.0
            cleaned_skills.append({
                "actions": actions,
                "durations": durations,
                "count": count,
                "quality": max(-1.0, min(1.0, quality)),
            })
            if len(cleaned_skills) >= SKILL_HEAD_SIZE:
                break
    profile["skills"] = cleaned_skills


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
    if not isinstance(profile.get("skills"), list):
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


def windows_graphics_accelerator_available() -> bool:
    if os.name != "nt":
        return False
    try:
        class DISPLAY_DEVICEW(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("DeviceName", wintypes.WCHAR * 32),
                ("DeviceString", wintypes.WCHAR * 128),
                ("StateFlags", wintypes.DWORD),
                ("DeviceID", wintypes.WCHAR * 128),
                ("DeviceKey", wintypes.WCHAR * 128),
            ]

        index = 0
        while index < 32:
            device = DISPLAY_DEVICEW()
            device.cb = ctypes.sizeof(DISPLAY_DEVICEW)
            if not user32.EnumDisplayDevicesW(None, index, ctypes.byref(device), 0):
                break
            description = str(device.DeviceString).strip().lower()
            attached = bool(int(device.StateFlags) & 0x00000001)
            mirroring = bool(int(device.StateFlags) & 0x00000008)
            software = (
                "microsoft basic" in description
                or "remote display" in description
                or "indirect display" in description
            )
            if attached and not mirroring and not software and description:
                return True
            index += 1
    except Exception:
        return False
    return False


def requested_hardware_tier(
    available_memory_bytes: int | None = None,
    cpu_count: int | None = None,
    gpu_available: bool | None = None,
) -> str:
    memory = available_physical_memory_bytes() if available_memory_bytes is None else max(0, int(available_memory_bytes))
    processors = max(1, int(os.cpu_count() or 1) if cpu_count is None else int(cpu_count))
    gib = 1024 ** 3
    if processors <= 4 or (memory and memory < 4 * gib):
        return "low_numpy"
    has_gpu = (
        windows_graphics_accelerator_available()
        if gpu_available is None
        else bool(gpu_available)
    )
    if processors >= 12 and (not memory or memory >= 12 * gib) and has_gpu:
        return "high_directml"
    return "mid_onnx"


def installed_onnx_providers() -> tuple[str, ...]:
    try:
        return tuple(str(value) for value in import_onnxruntime(True).get_available_providers())
    except Exception:
        return ()


def hardware_capability_tier(
    available_memory_bytes: int | None = None,
    cpu_count: int | None = None,
    providers: tuple[str, ...] | list[str] | None = None,
) -> str:
    provider_hint = (
        None
        if providers is None
        else "DmlExecutionProvider" in tuple(providers)
    )
    requested = requested_hardware_tier(
        available_memory_bytes,
        cpu_count,
        provider_hint,
    )
    if requested != "high_directml":
        return requested
    available = installed_onnx_providers() if providers is None else tuple(providers)
    return "high_directml" if "DmlExecutionProvider" in available else "mid_onnx"


def duration_bin(seconds: float) -> int:
    value = max(0.0, min(2.0, float(seconds)))
    boundaries = (0.052, 0.095, 0.175, 0.290)
    return sum(value > boundary for boundary in boundaries)


def encode_action_id(base_action: int, duration_index: int) -> int:
    del duration_index
    return max(0, int(base_action))



def decode_action_id(action_id: int) -> tuple[int, int]:
    # Schema 15+ stores the base control only; duration lives in temporal state.
    return max(0, int(action_id)), DURATION_HEAD_SIZE // 2



def action_space_size(base_action_count: int) -> int:
    # Duration is predicted conditionally and is no longer multiplied into the
    # discrete action count. This keeps the learned action space sample-efficient.
    return max(1, int(base_action_count))



def action_factor_tuple(action: dict, duration_index: int = 2) -> tuple[int, int, int]:
    normalized = normalized_action(action)
    kind_index = CONTROL_KINDS.index(action_kind(normalized))
    mouse_bucket = 0
    if normalized["mouse_x"] >= 0 and normalized["mouse_y"] >= 0:
        mouse_bucket = 1 + int(normalized["mouse_y"]) * MOUSE_GRID_WIDTH + int(normalized["mouse_x"])
    elif normalized["mouse_dx"] or normalized["mouse_dy"]:
        dx = max(-2, min(2, int(normalized["mouse_dx"])))
        dy = max(-2, min(2, int(normalized["mouse_dy"])))
        mouse_bucket = 577 + (dy + 2) * 5 + (dx + 2)
    elif normalized["mouse_wheel"]:
        mouse_bucket = 602 + max(-2, min(2, int(normalized["mouse_wheel"]))) + 2
    return (
        kind_index,
        max(0, min(MOUSE_HEAD_SIZE - 1, mouse_bucket)),
        max(0, min(DURATION_HEAD_SIZE - 1, int(duration_index))),
    )


def action_factor_matrix(np, actions: list[dict]):
    rows = [action_factor_tuple(action, 0) for action in actions]
    return np.asarray(rows, dtype=np.int16)



def action_key_multihot_matrix(np, actions: list[dict]):
    rows = []
    for action in actions:
        normalized = normalized_action(action)
        keys = [int(value) for value in normalized["keys"] if 0 <= int(value) < KEY_HEAD_SIZE]
        row = np.zeros(KEY_HEAD_SIZE, dtype=np.float32)
        if keys:
            row[keys] = 1.0 / math.sqrt(len(keys))
        rows.append(row)
    return np.stack(rows, axis=0) if rows else np.zeros((0, KEY_HEAD_SIZE), dtype=np.float32)



def action_button_multihot_matrix(np, actions: list[dict]):
    button_index = {"left": 0, "right": 1, "middle": 2, "x1": 3, "x2": 4}
    rows = []
    for action in actions:
        normalized = normalized_action(action)
        buttons = [button_index[value] for value in normalized["buttons"] if value in button_index]
        row = np.zeros(BUTTON_HEAD_SIZE, dtype=np.float32)
        if buttons:
            row[buttons] = 1.0 / math.sqrt(len(buttons))
        rows.append(row)
    return np.stack(rows, axis=0) if rows else np.zeros((0, BUTTON_HEAD_SIZE), dtype=np.float32)



def conditional_duration_outputs(np, model: dict, hidden, control_kind: int):
    kind = max(0, min(len(CONTROL_KINDS) - 1, int(control_kind)))
    hidden_value = np.asarray(hidden, dtype=np.float32)
    logits = (
        hidden_value @ model["policy_duration_w"]
        + model["policy_duration_b"]
        + model["policy_duration_kind_b"][kind]
    )
    probabilities = _softmax_vector(np, logits).astype(np.float32)
    twin_values = (
        np.einsum("h,tvhd->tvd", hidden_value, model["q_duration_w"])
        + model["q_duration_b"]
        + model["q_duration_kind_b"][:, :, kind, :]
    ).astype(np.float32)
    q_values = np.minimum(twin_values[0], twin_values[1])
    return probabilities, q_values


def select_conditional_duration(
    np,
    model: dict,
    hidden,
    base_action: int,
    exploration: float = 0.0,
    critic_weights=None,
) -> int:
    if not 0 <= int(base_action) < len(model["action_factors"]):
        return DURATION_HEAD_SIZE // 2
    kind = int(model["action_factors"][int(base_action), 0])
    probabilities, q_values = conditional_duration_outputs(np, model, hidden, kind)
    score = np.log(np.maximum(probabilities, 1e-9)) + 0.35 * combined_critic_values(np, q_values, critic_weights)
    epsilon = max(0.0, min(0.35, float(exploration)))
    if epsilon > 0.0 and random.random() < epsilon:
        return random.randrange(DURATION_HEAD_SIZE)
    return int(np.argmax(score))


def predict_mouse_offset(np, model: dict, hidden) -> tuple[float, float]:
    value = np.tanh(np.asarray(hidden, dtype=np.float32) @ model["mouse_offset_w"] + model["mouse_offset_b"])
    return float(value[0]), float(value[1])


def refine_pointer_action(action: dict, offset: tuple[float, float]) -> dict:
    normalized = normalized_action(action)
    if normalized["mouse_x"] >= 0 and normalized["mouse_y"] >= 0:
        dx, dy = offset
        normalized["mouse_x"] = max(0, min(MOUSE_GRID_WIDTH - 1, int(round(normalized["mouse_x"] + dx * 0.49))))
        normalized["mouse_y"] = max(0, min(MOUSE_GRID_HEIGHT - 1, int(round(normalized["mouse_y"] + dy * 0.49))))
    elif normalized["mouse_dx"] or normalized["mouse_dy"]:
        dx, dy = offset
        normalized["mouse_dx"] = max(-2, min(2, int(round(normalized["mouse_dx"] + dx))))
        normalized["mouse_dy"] = max(-2, min(2, int(round(normalized["mouse_dy"] + dy))))
    return normalized




def predict_conditional_hold(
    np,
    model: dict,
    hidden,
    base_action: int,
    exploration: float = 0.0,
    critic_weights=None,
) -> float:
    """Return a continuous hold duration from policy, critics, and world dynamics."""
    if not 0 <= int(base_action) < len(model["action_factors"]):
        return float(DURATION_SECONDS[DURATION_HEAD_SIZE // 2])
    kind = int(model["action_factors"][int(base_action), 0])
    probabilities, q_values = conditional_duration_outputs(np, model, hidden, kind)
    combined = combined_critic_values(np, q_values, critic_weights)
    logits = np.log(np.maximum(probabilities, 1e-9)) + 0.25 * combined
    world_values = latent_world_model_duration_values(
        np,
        model,
        hidden,
        int(base_action),
        critic_weights,
    )
    if world_values.shape == (DURATION_HEAD_SIZE,) and np.isfinite(world_values).all():
        logits += 0.30 * world_values
    weights = _softmax_vector(np, logits)
    duration = float(np.dot(weights, np.asarray(DURATION_SECONDS, dtype=np.float64)))
    jitter = max(0.0, min(0.25, float(exploration)))
    if jitter > 0.0:
        duration *= 1.0 + random.uniform(-0.20, 0.20) * jitter
    return max(DURATION_SECONDS[0], min(DURATION_SECONDS[-1], duration))



def parameterized_action_from_heads(
    np,
    model: dict,
    hidden,
    base_action: dict,
    strength: float,
) -> dict:
    """Synthesize coordinates and safe key/button combinations from conditional heads."""
    action = normalized_action(base_action)
    effective = max(0.0, min(1.0, float(strength))) * learned_progress_confidence(model)
    if effective <= 0.02:
        return action
    hidden_value = np.asarray(hidden, dtype=np.float32)
    kind = action_kind(action)

    key_logits = hidden_value @ model["policy_key_w"] + model["policy_key_b"]
    key_probabilities = _sigmoid(np, key_logits)
    if kind in ("keyboard", "mixed"):
        selected = set(action["keys"])
        ranked = sorted(
            (int(key) for key in SAFE_KEY_VKS if 0 <= int(key) < KEY_HEAD_SIZE),
            key=lambda key: float(key_probabilities[key]),
            reverse=True,
        )
        target_count = max(1, min(4, len(selected) + int(round(2.0 * effective))))
        threshold = 0.60 + 0.12 * (1.0 - effective)
        for key in ranked:
            if len(selected) >= target_count:
                break
            if float(key_probabilities[key]) >= threshold:
                selected.add(key)
        action["keys"] = sorted(selected)

    button_logits = hidden_value @ model["policy_button_w"] + model["policy_button_b"]
    button_probabilities = _sigmoid(np, button_logits)
    button_names = ("left", "right", "middle", "x1", "x2")
    if kind in ("click", "mixed"):
        selected_buttons = set(action["buttons"])
        for index in np.argsort(button_probabilities)[::-1][:2]:
            if float(button_probabilities[int(index)]) >= 0.68 + 0.10 * (1.0 - effective):
                selected_buttons.add(button_names[int(index)])
        action["buttons"] = [name for name in button_names if name in selected_buttons]

    mouse_logits = hidden_value @ model["policy_mouse_w"] + model["policy_mouse_b"]
    offset_x, offset_y = predict_mouse_offset(np, model, hidden_value)
    if kind in ("click", "pointer", "mixed"):
        absolute_logits = np.asarray(mouse_logits[1:1 + MOUSE_GRID_WIDTH * MOUSE_GRID_HEIGHT], dtype=np.float64)
        top_count = min(12, len(absolute_logits))
        if top_count > 0:
            top_indices = np.argsort(absolute_logits)[-top_count:]
            top_weights = _softmax_vector(np, absolute_logits[top_indices])
            expected_x = float(sum(float(weight) * (int(index) % MOUSE_GRID_WIDTH) for weight, index in zip(top_weights, top_indices)))
            expected_y = float(sum(float(weight) * (int(index) // MOUSE_GRID_WIDTH) for weight, index in zip(top_weights, top_indices)))
            concentration = min(1.0, float(top_weights.max(initial=0.0)) * 4.0)
            blend = effective * concentration
            if action["mouse_x"] >= 0 and action["mouse_y"] >= 0:
                expected_x = (1.0 - blend) * action["mouse_x"] + blend * expected_x
                expected_y = (1.0 - blend) * action["mouse_y"] + blend * expected_y
                action["mouse_x"] = int(round(expected_x + offset_x * 0.75 * effective))
                action["mouse_y"] = int(round(expected_y + offset_y * 0.75 * effective))
            elif action["buttons"] and concentration >= 0.35:
                action["mouse_x"] = int(round(expected_x + offset_x * 0.75 * effective))
                action["mouse_y"] = int(round(expected_y + offset_y * 0.75 * effective))
                action["mouse_dx"] = 0
                action["mouse_dy"] = 0
        if action["mouse_x"] < 0 and (action["mouse_dx"] or action["mouse_dy"]):
            relative_logits = np.asarray(mouse_logits[577:602], dtype=np.float64)
            relative_weights = _softmax_vector(np, relative_logits)
            expected_dx = 0.0
            expected_dy = 0.0
            for index, weight in enumerate(relative_weights):
                expected_dx += float(weight) * ((index % 5) - 2)
                expected_dy += float(weight) * ((index // 5) - 2)
            action["mouse_dx"] = int(round((1.0 - effective) * action["mouse_dx"] + effective * expected_dx + offset_x * effective))
            action["mouse_dy"] = int(round((1.0 - effective) * action["mouse_dy"] + effective * expected_dy + offset_y * effective))
    return normalized_action(action)


def _pack_temporal_payload(frames: list[bytes], action_history: list[int], duration_history: list[float]) -> bytes:
    normalized_frames = [normalize_feature_bytes(frame) for frame in frames[-TEMPORAL_FRAMES:]]
    if not normalized_frames:
        normalized_frames = [bytes(FEATURE_DIM)]
    while len(normalized_frames) < TEMPORAL_FRAMES:
        normalized_frames.insert(0, normalized_frames[0])
    actions = [int(value) for value in action_history[-ACTION_HISTORY_LENGTH:]]
    durations = [max(0.0, min(2.0, float(value))) for value in duration_history[-ACTION_HISTORY_LENGTH:]]
    while len(actions) < ACTION_HISTORY_LENGTH:
        actions.insert(0, -1)
    while len(durations) < ACTION_HISTORY_LENGTH:
        durations.insert(0, 0.0)
    payload = bytearray(TEMPORAL_STATE_MAGIC)
    payload.extend(struct.pack("<BB", TEMPORAL_FRAMES, ACTION_HISTORY_LENGTH))
    for frame in normalized_frames:
        payload.extend(struct.pack("<I", len(frame)))
        payload.extend(frame)
    payload.extend(struct.pack("<" + "i" * ACTION_HISTORY_LENGTH, *actions))
    payload.extend(struct.pack("<" + "f" * ACTION_HISTORY_LENGTH, *durations))
    return bytes(payload)


def build_temporal_state(frames: list[bytes], action_history: list[int], duration_history: list[float]) -> bytes:
    return zlib.compress(_pack_temporal_payload(frames, action_history, duration_history), 6)


def decode_temporal_state(state: bytes) -> tuple[list[bytes], list[int], list[float]]:
    if not isinstance(state, (bytes, bytearray, memoryview)):
        raise ValueError("时序状态类型无效")
    raw = bytes(state)
    try:
        candidate = zlib.decompress(raw)
    except zlib.error:
        candidate = raw
    magic = (
        TEMPORAL_STATE_MAGIC
        if candidate.startswith(TEMPORAL_STATE_MAGIC)
        else LEGACY_TEMPORAL_STATE_MAGIC
        if candidate.startswith(LEGACY_TEMPORAL_STATE_MAGIC)
        else b""
    )
    if not magic:
        try:
            frame = normalize_feature_bytes(decompress_feature(raw, FEATURE_DIM))
        except Exception:
            frame = normalize_feature_bytes(candidate)
        return [frame] * TEMPORAL_FRAMES, [-1] * ACTION_HISTORY_LENGTH, [0.0] * ACTION_HISTORY_LENGTH
    offset = len(magic)
    if offset + 2 > len(candidate):
        raise ValueError("时序状态内容无效")
    frame_count, history_count = struct.unpack_from("<BB", candidate, offset)
    offset += 2
    if magic == TEMPORAL_STATE_MAGIC:
        # v71 wrote AGT3 with one frame/action. Keep those database rows valid
        # and normalize them to the v72 four-step state during database repair.
        valid_shape = (frame_count, history_count) in {
            (TEMPORAL_FRAMES, ACTION_HISTORY_LENGTH),
            (1, 1),
        }
    else:
        valid_shape = frame_count == 4 and history_count == 4
    if not valid_shape:
        raise ValueError("时序状态版本无效")
    frames = []
    for _ in range(frame_count):
        if offset + 4 > len(candidate):
            raise ValueError("时序状态内容无效")
        length = struct.unpack_from("<I", candidate, offset)[0]
        offset += 4
        if length not in (LEGACY_FEATURE_DIM, V27_FEATURE_DIM, V69_FEATURE_DIM, V74_FEATURE_DIM, FEATURE_DIM) or offset + length > len(candidate):
            raise ValueError("时序帧尺寸无效")
        frames.append(normalize_feature_bytes(candidate[offset:offset + length]))
        offset += length
    history_bytes = 4 * history_count
    if offset + history_bytes * 2 > len(candidate):
        raise ValueError("时序状态内容无效")
    actions = list(struct.unpack_from("<" + "i" * history_count, candidate, offset))
    offset += history_bytes
    durations = list(struct.unpack_from("<" + "f" * history_count, candidate, offset))
    offset += history_bytes
    if offset != len(candidate) or any(not math.isfinite(value) for value in durations):
        raise ValueError("时序状态内容无效")
    while len(frames) < TEMPORAL_FRAMES:
        frames.insert(0, frames[0])
    while len(actions) < ACTION_HISTORY_LENGTH:
        actions.insert(0, -1)
    while len(durations) < ACTION_HISTORY_LENGTH:
        durations.insert(0, 0.0)
    return frames[-TEMPORAL_FRAMES:], actions[-ACTION_HISTORY_LENGTH:], durations[-ACTION_HISTORY_LENGTH:]



def _temporal_frame_hash(state: bytes) -> str:
    frames, _, _ = decode_temporal_state(state)
    current = normalize_feature_bytes(frames[-1])
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    gray = current[:pixels]
    blue, red = feature_chroma(current)
    return frame_hash(gray, blue, red)


def _perceptual_hash_similarity(left: str, right: str) -> float:
    try:
        bits = max(1, 4 * max(len(left), len(right)))
        return max(0.0, min(1.0, 1.0 - frame_hash_distance(left, right) / bits))
    except Exception:
        return 0.0


def _temporal_progress_against_future(state: bytes, next_state: bytes | None, future_hashes: list[str]) -> float:
    if next_state is None or not future_hashes:
        return 0.0
    current_hash = _temporal_frame_hash(state)
    next_hash = _temporal_frame_hash(next_state)
    current_similarity = max(_perceptual_hash_similarity(current_hash, target) for target in future_hashes)
    next_similarity = max(_perceptual_hash_similarity(next_hash, target) for target in future_hashes)
    return max(-1.0, min(1.0, (next_similarity - current_similarity) * 4.0))


def stable_visual_state_key(np, model: dict, state: bytes) -> str:
    frames, _, _ = decode_temporal_state(state)
    channels = _frame_channels(np, frames[-1])
    embedding = _quantized_conv_features(np, model, channels).astype(np.float32, copy=False)
    if len(embedding) < 128 or not np.isfinite(embedding).all():
        raise ValueError("稳定视觉嵌入无效")
    boundaries = np.linspace(0, len(embedding), 129, dtype=np.int32)
    buckets = np.asarray(
        [
            float(embedding[int(boundaries[index]):int(boundaries[index + 1])].mean())
            for index in range(128)
        ],
        dtype=np.float32,
    )
    bits = 0
    for bit in range(64):
        if float(buckets[bit * 2]) >= float(buckets[bit * 2 + 1]):
            bits |= 1 << bit
    return f"v:{bits:016x}"


def temporal_state_key(state: bytes, np=None, model: dict | None = None) -> str:
    if np is not None and model is not None:
        try:
            return stable_visual_state_key(np, model, state)
        except Exception:
            pass
    frames, _, _ = decode_temporal_state(state)
    current = normalize_feature_bytes(frames[-1])
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    gray = current[:pixels]
    blue, red = feature_chroma(current)
    digest = int(frame_hash(gray, blue, red), 16)
    while digest >> 64:
        digest = (digest & ((1 << 64) - 1)) ^ (digest >> 64)
    return f"v:{digest & ((1 << 64) - 1):016x}"


def stable_state_distance(left: str, right: str) -> int:
    if STABLE_STATE_KEY_PATTERN.fullmatch(str(left)) is None or STABLE_STATE_KEY_PATTERN.fullmatch(str(right)) is None:
        return 65
    return (int(str(left)[2:], 16) ^ int(str(right)[2:], 16)).bit_count()


def transition_priority(source: str, reward: float, done: bool, novelty: float = 0.0) -> float:
    base = 2.0 if source == "human" else 1.0
    return max(0.05, min(20.0, base + abs(float(reward)) * 4.0 + (2.0 if done else 0.0) + max(0.0, novelty)))



def _append_signal_history(history: dict[str, list[float]] | None, key: str, value: float) -> list[float]:
    if history is None:
        return [float(value)]
    values = history.setdefault(key, [])
    values.append(float(value))
    del values[:-3]
    return values


def _confirmed_persistent_signal(values: list[float], high: float, low: float) -> float:
    if len(values) >= 2 and values[-1] >= high and values[-2] >= low:
        return min(1.0, (values[-1] + values[-2]) * 0.5)
    if len(values) >= 3 and sum(value >= low for value in values[-3:]) >= 2:
        return min(1.0, sum(values[-3:]) / 3.0)
    return 0.0


_OCR_DIGIT_TEMPLATES = {
    0: ("11111", "10001", "10011", "10101", "11001", "10001", "11111"),
    1: ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    2: ("11110", "00001", "00001", "11110", "10000", "10000", "11111"),
    3: ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    4: ("10010", "10010", "10010", "11111", "00010", "00010", "00010"),
    5: ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    6: ("01111", "10000", "10000", "11110", "10001", "10001", "01110"),
    7: ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    8: ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    9: ("01110", "10001", "10001", "01111", "00001", "00001", "11110"),
}


def recognize_hud_score(frame: bytes) -> tuple[int | None, float]:
    """Recognize compact numeric HUD text without an external OCR runtime."""
    if len(frame) != FEATURE_WIDTH * FEATURE_HEIGHT:
        return None, 0.0

    def recognize_band(top: int, bottom: int, bright_text: bool):
        height = max(0, bottom - top)
        if height < 5:
            return None
        values = [frame[y * FEATURE_WIDTH + x] for y in range(top, bottom) for x in range(FEATURE_WIDTH)]
        mean = sum(values) / max(1, len(values))
        low, high = min(values), max(values)
        if high - low < 28:
            return None
        threshold = mean + 0.32 * (high - mean) if bright_text else mean - 0.32 * (mean - low)
        binary = [
            [
                (frame[(top + y) * FEATURE_WIDTH + x] >= threshold)
                if bright_text
                else (frame[(top + y) * FEATURE_WIDTH + x] <= threshold)
                for x in range(FEATURE_WIDTH)
            ]
            for y in range(height)
        ]
        minimum_column_pixels = max(1, height // 9)
        active_columns = [
            sum(1 for y in range(height) if binary[y][x]) >= minimum_column_pixels
            for x in range(FEATURE_WIDTH)
        ]
        runs = []
        start = None
        for x, active in enumerate(active_columns + [False]):
            if active and start is None:
                start = x
            elif not active and start is not None:
                if 1 <= x - start <= max(14, height):
                    runs.append((start, x))
                start = None
        digits = []
        for left, right in runs:
            occupied_rows = [
                y for y in range(height)
                if any(binary[y][x] for x in range(left, right))
            ]
            if not occupied_rows:
                continue
            glyph_top, glyph_bottom = occupied_rows[0], occupied_rows[-1] + 1
            glyph_height = glyph_bottom - glyph_top
            glyph_width = right - left
            if glyph_height < 5 or glyph_width > glyph_height * 1.25:
                continue
            expected_width = max(glyph_width, int(round(glyph_height * 5.0 / 7.0)))
            padded_left = max(0, left - (expected_width - glyph_width) // 2)
            padded_right = min(FEATURE_WIDTH, padded_left + expected_width)
            padded_left = max(0, padded_right - expected_width)
            sampled = []
            for target_y in range(7):
                source_top = glyph_top + target_y * glyph_height // 7
                source_bottom = glyph_top + (target_y + 1) * glyph_height // 7
                row = []
                for target_x in range(5):
                    source_left = padded_left + target_x * (padded_right - padded_left) // 5
                    source_right = padded_left + (target_x + 1) * (padded_right - padded_left) // 5
                    area = max(1, (source_bottom - source_top) * (source_right - source_left))
                    ink = sum(
                        int(binary[y][x])
                        for y in range(source_top, max(source_top + 1, source_bottom))
                        for x in range(source_left, max(source_left + 1, source_right))
                    )
                    row.append(1 if ink / area >= 0.30 else 0)
                sampled.append(row)
            best_digit = None
            best_confidence = 0.0
            for digit, template_rows in _OCR_DIGIT_TEMPLATES.items():
                template = [[int(value) for value in row] for row in template_rows]
                matches = sum(sampled[y][x] == template[y][x] for y in range(7) for x in range(5)) / 35.0
                overlap = sum(sampled[y][x] and template[y][x] for y in range(7) for x in range(5))
                union = sum(sampled[y][x] or template[y][x] for y in range(7) for x in range(5))
                confidence = 0.58 * matches + 0.42 * overlap / max(1, union)
                if confidence > best_confidence:
                    best_digit, best_confidence = digit, confidence
            if best_digit is not None and best_confidence >= 0.64:
                digits.append((left, right, glyph_top, glyph_bottom, best_digit, best_confidence))
        if not digits:
            return None
        digits.sort()
        sequences = []
        current = []
        for item in digits:
            if current:
                previous = current[-1]
                overlap = max(0, min(previous[3], item[3]) - max(previous[2], item[2]))
                minimum_height = max(1, min(previous[3] - previous[2], item[3] - item[2]))
                gap = item[0] - previous[1]
                if overlap / minimum_height < 0.55 or gap > max(5, minimum_height // 2):
                    sequences.append(current)
                    current = []
            current.append(item)
        if current:
            sequences.append(current)
        candidates = []
        for sequence in sequences:
            confidence = sum(float(item[5]) for item in sequence) / len(sequence)
            if len(sequence) == 1 and confidence < 0.82:
                continue
            text = "".join(str(item[4]) for item in sequence[:12])
            candidates.append((confidence + min(0.12, 0.025 * len(sequence)), len(sequence), int(text)))
        return max(candidates, default=None)

    candidates = []
    bands = ((0, max(9, FEATURE_HEIGHT // 3)), (FEATURE_HEIGHT * 3 // 4, FEATURE_HEIGHT))
    for top, bottom in bands:
        for bright_text in (True, False):
            candidate = recognize_band(top, bottom, bright_text)
            if candidate is not None:
                candidates.append(candidate)
    if not candidates:
        return None, 0.0
    confidence, _, value = max(candidates)
    return int(value), max(0.0, min(1.0, float(confidence)))




_STATUS_LETTER_TEMPLATES = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
}
_STATUS_VICTORY_WORDS = ("WIN", "VICTORY", "CLEAR", "SUCCESS", "COMPLETE", "PASSED")
_STATUS_DEATH_WORDS = ("GAMEOVER", "DEFEAT", "DEAD", "FAILED", "TRYAGAIN")


def _status_word_similarity(left: str, right: str) -> float:
    left = "".join(character for character in str(left).upper() if character.isalpha())
    right = "".join(character for character in str(right).upper() if character.isalpha())
    if not left or not right:
        return 0.0
    if right in left:
        return 1.0
    best = 0.0
    width = len(right)
    for start in range(max(1, len(left) - width + 1)):
        candidate = left[start:start + width]
        matches = sum(a == b for a, b in zip(candidate, right))
        best = max(best, matches / max(len(candidate), width))
    return best


def _recognize_status_band(frame: bytes, top: int, bottom: int, bright_text: bool) -> tuple[str, float]:
    height = max(0, int(bottom) - int(top))
    if len(frame) != FEATURE_WIDTH * FEATURE_HEIGHT or height < 7:
        return "", 0.0
    values = [frame[y * FEATURE_WIDTH + x] for y in range(top, bottom) for x in range(FEATURE_WIDTH)]
    low, high = min(values), max(values)
    if high - low < 42:
        return "", 0.0
    mean = sum(values) / max(1, len(values))
    threshold = mean + 0.34 * (high - mean) if bright_text else mean - 0.34 * (mean - low)
    binary = [
        [
            frame[(top + y) * FEATURE_WIDTH + x] >= threshold
            if bright_text else frame[(top + y) * FEATURE_WIDTH + x] <= threshold
            for x in range(FEATURE_WIDTH)
        ]
        for y in range(height)
    ]
    minimum_column_pixels = max(2, height // 8)
    active_columns = [
        sum(1 for y in range(height) if binary[y][x]) >= minimum_column_pixels
        for x in range(FEATURE_WIDTH)
    ]
    runs = []
    start = None
    for x, active in enumerate(active_columns + [False]):
        if active and start is None:
            start = x
        elif not active and start is not None:
            if 1 <= x - start <= max(18, height + 4):
                runs.append((start, x))
            start = None
    glyphs = []
    for left, right in runs:
        occupied_rows = [y for y in range(height) if any(binary[y][x] for x in range(left, right))]
        if not occupied_rows:
            continue
        glyph_top, glyph_bottom = occupied_rows[0], occupied_rows[-1] + 1
        glyph_height = glyph_bottom - glyph_top
        glyph_width = right - left
        if glyph_height < 7 or glyph_width > glyph_height * 1.45:
            continue
        expected_width = max(glyph_width, int(round(glyph_height * 5.0 / 7.0)))
        padded_left = max(0, left - (expected_width - glyph_width) // 2)
        padded_right = min(FEATURE_WIDTH, padded_left + expected_width)
        padded_left = max(0, padded_right - expected_width)
        sampled = []
        for target_y in range(7):
            source_top = glyph_top + target_y * glyph_height // 7
            source_bottom = max(source_top + 1, glyph_top + (target_y + 1) * glyph_height // 7)
            row = []
            for target_x in range(5):
                source_left = padded_left + target_x * (padded_right - padded_left) // 5
                source_right = max(source_left + 1, padded_left + (target_x + 1) * (padded_right - padded_left) // 5)
                area = max(1, (source_bottom - source_top) * (source_right - source_left))
                ink = sum(
                    int(binary[y][x])
                    for y in range(source_top, min(height, source_bottom))
                    for x in range(source_left, min(FEATURE_WIDTH, source_right))
                )
                row.append(1 if ink / area >= 0.30 else 0)
            sampled.append(row)
        best_letter = ""
        best_confidence = 0.0
        for letter, template_rows in _STATUS_LETTER_TEMPLATES.items():
            template = [[int(value) for value in row] for row in template_rows]
            matches = sum(sampled[y][x] == template[y][x] for y in range(7) for x in range(5)) / 35.0
            overlap = sum(sampled[y][x] and template[y][x] for y in range(7) for x in range(5))
            union = sum(sampled[y][x] or template[y][x] for y in range(7) for x in range(5))
            confidence = 0.60 * matches + 0.40 * overlap / max(1, union)
            if confidence > best_confidence:
                best_letter, best_confidence = letter, confidence
        if best_letter and best_confidence >= 0.60:
            glyphs.append((left, right, glyph_top, glyph_bottom, best_letter, best_confidence))
    if len(glyphs) < 3:
        return "", 0.0
    glyphs.sort()
    text_parts = []
    confidences = []
    previous = None
    for glyph in glyphs:
        if previous is not None:
            gap = glyph[0] - previous[1]
            common_height = max(1, min(previous[3] - previous[2], glyph[3] - glyph[2]))
            if gap > max(4, common_height // 2):
                text_parts.append(" ")
        text_parts.append(glyph[4])
        confidences.append(float(glyph[5]))
        previous = glyph
    return "".join(text_parts), sum(confidences) / max(1, len(confidences))


def recognize_terminal_text(frame: bytes) -> tuple[float, float]:
    """Return conservative victory/death text confidences from common 5x7-like overlays."""
    bands = (
        (FEATURE_HEIGHT // 5, FEATURE_HEIGHT * 4 // 5),
        (FEATURE_HEIGHT // 3, FEATURE_HEIGHT * 2 // 3),
        (0, FEATURE_HEIGHT // 2),
    )
    victory = 0.0
    death = 0.0
    for top, bottom in bands:
        for bright_text in (True, False):
            text, glyph_confidence = _recognize_status_band(frame, top, bottom, bright_text)
            if not text:
                continue
            compact = text.replace(" ", "")
            victory_match = max((_status_word_similarity(compact, word) for word in _STATUS_VICTORY_WORDS), default=0.0)
            death_match = max((_status_word_similarity(compact, word) for word in _STATUS_DEATH_WORDS), default=0.0)
            victory = max(victory, glyph_confidence * max(0.0, (victory_match - 0.55) / 0.45))
            death = max(death, glyph_confidence * max(0.0, (death_match - 0.55) / 0.45))
    return max(0.0, min(1.0, victory)), max(0.0, min(1.0, death))


def recognize_hud_health(frame: bytes) -> tuple[float | None, float, float]:
    """Detect a persistent long HUD bar and return fill ratio, confidence, and horizontal anchor."""
    if len(frame) != FEATURE_WIDTH * FEATURE_HEIGHT:
        return None, 0.0, -1.0
    row_ranges = (
        range(0, max(5, FEATURE_HEIGHT // 4)),
        range(max(0, FEATURE_HEIGHT * 3 // 4), FEATURE_HEIGHT),
    )
    candidates = []
    for rows in row_ranges:
        previous_runs = []
        for y in rows:
            row = frame[y * FEATURE_WIDTH:(y + 1) * FEATURE_WIDTH]
            low, high = min(row), max(row)
            contrast = high - low
            if contrast < 36:
                previous_runs = []
                continue
            mean = sum(row) / FEATURE_WIDTH
            row_runs = []
            for bright in (True, False):
                threshold = mean + 0.38 * (high - mean) if bright else mean - 0.38 * (mean - low)
                active = [value >= threshold if bright else value <= threshold for value in row]
                start = None
                for x, value in enumerate(active + [False]):
                    if value and start is None:
                        start = x
                    elif not value and start is not None:
                        width = x - start
                        if width >= max(10, FEATURE_WIDTH // 8):
                            row_runs.append((start, x, width, contrast, bright))
                        start = None
            linked = []
            for run in row_runs:
                matches = [
                    item for item in previous_runs
                    if item[4] == run[4] and abs(item[0] - run[0]) <= 3 and abs(item[1] - run[1]) <= 4
                ]
                height = max((item[5] for item in matches), default=0) + 1
                linked.append((*run, height))
                if height >= 2:
                    width_ratio = run[2] / FEATURE_WIDTH
                    anchor_value = (run[0] + run[1]) * 0.5 / FEATURE_WIDTH
                    confidence = min(1.0, (height / 3.0) * (run[2] / 30.0) * (run[3] / 72.0))
                    candidates.append((confidence, width_ratio, anchor_value))
            previous_runs = linked
    if not candidates:
        return None, 0.0, -1.0
    confidence, ratio, anchor_value = max(candidates)
    return float(ratio), float(confidence), float(anchor_value)


def learned_progress_confidence(model: dict) -> float:
    """Return a conservative confidence for using learned progress as reward shaping."""
    try:
        samples = max(0, int(model.get("trained_samples", 0)))
        rounds = max(0, int(model.get("training_rounds", 0)))
        validation_score = float(model.get("validation_score", -0.20))
    except (TypeError, ValueError, OverflowError):
        return 0.0
    if not math.isfinite(validation_score):
        validation_score = -0.20
    sample_confidence = 1.0 - math.exp(-samples / 4096.0)
    round_confidence = 1.0 - math.exp(-rounds / 3.0)
    validation_confidence = max(0.0, min(1.0, (validation_score + 0.10) / 0.50))
    confidence = sample_confidence * (0.35 + 0.65 * round_confidence) * (
        0.35 + 0.65 * validation_confidence
    )
    return max(0.0, min(1.0, confidence))


def reward_model_signals(np, model: dict, hidden, next_hidden) -> dict[str, float]:
    current = np.asarray(hidden, dtype=np.float32)
    following = np.asarray(next_hidden if next_hidden is not None else hidden, dtype=np.float32)
    if current.shape != following.shape or current.shape != (int(model["hidden_size"]),):
        return {
            "progress": 0.0, "success_probability": 0.0,
            "failure_probability": 0.0, "reset_probability": 0.0,
            "confidence": 0.0,
        }
    transition = np.tanh(following - 0.35 * current).astype(np.float32, copy=False)
    logits = np.einsum("h,mho->mo", transition, model["reward_model_w"], optimize=True)
    logits += model["reward_model_b"]
    progress_members = np.tanh(logits[:, 0])
    probability_members = _sigmoid(np, logits[:, 1:4])
    confidence_members = _sigmoid(np, logits[:, 4])
    disagreement = float(progress_members.std()) + float(probability_members.std(axis=0).mean())
    agreement = math.exp(-3.0 * disagreement)
    steps = max(0, int(model.get("reward_model_training_steps", 0)))
    maturity = 1.0 - math.exp(-steps / 2048.0)
    confidence = float(confidence_members.mean()) * agreement * maturity
    return {
        "progress": float(np.clip(progress_members.mean(), -1.0, 1.0)),
        "success_probability": float(np.clip(probability_members[:, 0].mean(), 0.0, 1.0)),
        "failure_probability": float(np.clip(probability_members[:, 1].mean(), 0.0, 1.0)),
        "reset_probability": float(np.clip(probability_members[:, 2].mean(), 0.0, 1.0)),
        "confidence": float(max(0.0, min(1.0, confidence))),
    }


def train_reward_model_transition(
    np,
    model: dict,
    hidden,
    next_hidden,
    record: dict,
    sample_weight: float,
    gradients: dict[str, object],
) -> tuple[float, object]:
    current = np.asarray(hidden, dtype=np.float32)
    following = np.asarray(next_hidden if next_hidden is not None else hidden, dtype=np.float32)
    transition_pre = following - 0.35 * current
    transition = np.tanh(transition_pre).astype(np.float32, copy=False)
    task_target = max(-1.0, min(1.0, float(record.get("task_reward", 0.0))))
    safety = max(0.0, min(1.0, float(record.get("safety_penalty", 0.0))))
    done = bool(record.get("done", False))
    trajectory_class = str(record.get("trajectory_class", ""))
    source = str(record.get("source", ""))
    success_target = 1.0 if done and trajectory_class == "successful_ai" else 0.0
    if done and source == "human" and task_target > max(0.05, 0.50 * safety):
        success_target = max(success_target, 0.75)
    failure_target = 1.0 if done and trajectory_class == "failed_ai" else 0.0
    failure_target = max(failure_target, min(1.0, safety))
    reset_target = 1.0 if done and success_target < 0.50 and failure_target < 0.50 else 0.0
    weak_strength = max(
        abs(task_target), safety,
        success_target, failure_target,
        0.65 if reset_target > 0.0 else 0.0,
    )
    targets = np.asarray(
        [task_target, success_target, failure_target, reset_target, weak_strength],
        dtype=np.float32,
    )
    total_loss = 0.0
    hidden_gradient = np.zeros_like(current, dtype=np.float32)
    member_scale = 1.0 / REWARD_MODEL_MEMBERS
    base_weight = max(0.0, min(4.0, float(sample_weight)))
    for member in range(REWARD_MODEL_MEMBERS):
        bootstrap = base_weight * (0.90 + 0.05 * ((member + int(record.get("step", 0))) % 3))
        logits = transition @ model["reward_model_w"][member] + model["reward_model_b"][member]
        predictions = np.empty(REWARD_MODEL_OUTPUTS, dtype=np.float32)
        predictions[0] = math.tanh(float(logits[0]))
        predictions[1:] = _sigmoid(np, logits[1:])
        output_gradient = np.empty(REWARD_MODEL_OUTPUTS, dtype=np.float32)
        output_gradient[0] = (predictions[0] - targets[0]) * (1.0 - predictions[0] ** 2)
        output_gradient[1:] = predictions[1:] - targets[1:]
        output_gradient *= bootstrap * member_scale / REWARD_MODEL_OUTPUTS
        gradients["reward_model_w"][member] += np.outer(transition, output_gradient).astype(np.float32)
        gradients["reward_model_b"][member] += output_gradient
        transition_gradient = model["reward_model_w"][member] @ output_gradient
        hidden_gradient += -0.35 * transition_gradient * (1.0 - transition * transition)
        total_loss += 0.5 * bootstrap * float(np.mean((predictions - targets) ** 2)) * member_scale
    model["reward_model_training_steps"] = int(model.get("reward_model_training_steps", 0)) + 1
    return float(total_loss), hidden_gradient.astype(np.float32, copy=False)


def compose_reward(metrics: dict, config: dict) -> float:
    task = float(metrics.get("task_reward", 0.0))
    exploration = float(metrics.get("exploration_reward", 0.0))
    safety = float(metrics.get("safety_penalty", 0.0))
    if not math.isfinite(task):
        task = 0.0
    if not math.isfinite(exploration):
        exploration = 0.0
    if not math.isfinite(safety):
        safety = 0.0
    reward = (
        float(config["task_reward_weight"]) * task
        + float(config["exploration_reward_weight"]) * exploration
        - float(config["safety_penalty_weight"]) * safety
    )
    return max(-1.0, min(1.0, reward))


def classify_transition_reward(
    previous_frame: bytes,
    current_frame: bytes,
    previous_chroma_blue: bytes,
    previous_chroma_red: bytes,
    current_chroma_blue: bytes,
    current_chroma_red: bytes,
    recent_state_keys: list[str],
    config: dict,
    signal_history: dict[str, list[float]] | None = None,
    human_progress_reference: list[str] | None = None,
    learned_progress: float = 0.0,
    learned_reward_signals: dict[str, float] | None = None,
) -> tuple[float, dict[str, float]]:
    def configured(value: object, default: float, minimum: float = 0.0, maximum: float = 2.0) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError, OverflowError):
            numeric = default
        if not math.isfinite(numeric):
            numeric = default
        return max(minimum, min(maximum, numeric))

    motion, changed_ratio, flicker = visual_change_metrics(previous_frame, current_frame)
    color_motion, color_ratio = chroma_change_metrics(
        previous_chroma_blue, previous_chroma_red, current_chroma_blue, current_chroma_red
    )
    world_change, hud_change, side_change = scene_progress_metrics(previous_frame, current_frame)
    global_shift = uniform_brightness_change(previous_frame, current_frame)
    mean_before = sum(previous_frame) / max(1, len(previous_frame)) / 255.0
    mean_after = sum(current_frame) / max(1, len(current_frame)) / 255.0
    persistence = max(0.0, min(1.0, 1.0 - flicker * 1.8 - global_shift * 0.35))
    fade_score = max(0.0, min(1.0, (mean_before - mean_after) * 3.5 + global_shift * 0.45))
    darkness = max(0.0, 0.12 - mean_after) / 0.12

    # Generic HUD motion remains diagnostic only. Task reward is driven by
    # explicit score deltas, terminal text, and confirmed level transitions.
    raw_score = max(0.0, hud_change - world_change * 0.65 - global_shift * 0.20)
    raw_score *= max(0.0, min(1.0, persistence + color_ratio * 0.5))
    score_signal = min(1.0, raw_score * 8.0)
    previous_score, previous_score_confidence = recognize_hud_score(previous_frame)
    current_score, current_score_confidence = recognize_hud_score(current_frame)
    ocr_score_progress = 0.0
    reliable_score_progress = 0.0
    if (
        previous_score is not None
        and current_score is not None
        and min(previous_score_confidence, current_score_confidence) >= 0.72
    ):
        score_delta = int(current_score) - int(previous_score)
        score_scale = max(1.0, abs(float(previous_score)) * 0.02)
        ocr_score_progress = math.tanh(float(score_delta) / score_scale)
        reliable_score_progress = ocr_score_progress * min(previous_score_confidence, current_score_confidence)
        if score_delta > 0:
            score_signal = max(score_signal, min(previous_score_confidence, current_score_confidence))

    victory_text, death_text = recognize_terminal_text(current_frame)
    previous_health, previous_health_confidence, previous_health_anchor = recognize_hud_health(previous_frame)
    current_health, current_health_confidence, current_health_anchor = recognize_hud_health(current_frame)
    health_loss = 0.0
    health_gain = 0.0
    if (
        previous_health is not None
        and current_health is not None
        and min(previous_health_confidence, current_health_confidence) >= 0.52
        and abs(previous_health_anchor - current_health_anchor) <= 0.12
    ):
        relative_health_change = (float(current_health) - float(previous_health)) / max(0.08, float(previous_health))
        health_loss = max(0.0, min(1.0, -relative_health_change))
        health_gain = max(0.0, min(1.0, relative_health_change))

    death_signal = max(darkness, fade_score * 0.9, death_text)
    if mean_before > 0.20 and mean_after < 0.08:
        death_signal = max(death_signal, 0.85)
    menu_signal = min(
        1.0,
        max(0.0, global_shift - world_change * 1.8)
        * max(0.0, 1.0 - changed_ratio * 0.5)
        * 3.0,
    )
    current_key = frame_hash(current_frame, current_chroma_blue, current_chroma_red)
    returned = 1.0 if recent_hash_match(current_key, recent_state_keys[-8:], 5) else 0.0
    jitter_signal = min(
        1.0,
        flicker * 1.8
        + returned * max(0.0, changed_ratio - 0.01)
        + max(0.0, side_change - world_change) * 0.8,
    )
    meaningful_change = min(1.0, world_change * 4.0 + color_motion * 2.0 + motion * 1.5)
    translation_dx, translation_dy, translation_confidence = estimate_visual_translation(
        previous_frame,
        current_frame,
        int(config.get("translation_search_radius", 2)),
    )
    spatial_progress = min(
        1.0,
        translation_confidence
        * (abs(translation_dx) + abs(translation_dy))
        / max(1.0, float(config.get("translation_search_radius", 2))),
    )

    scene_cut_candidate = min(
        1.0,
        max(0.0, world_change - 0.10)
        * 4.0
        * max(0.0, 1.0 - min(1.0, hud_change * 3.0))
        * max(0.0, 1.0 - min(1.0, fade_score + darkness)),
    )
    prior_scene_cuts = list((signal_history or {}).get("scene_cut", []))
    confirmed_level_transition = (
        min(1.0, float(prior_scene_cuts[-1]))
        if prior_scene_cuts
        and float(prior_scene_cuts[-1]) >= 0.58
        and world_change <= 0.075
        and global_shift <= 0.18
        and death_signal < 0.50
        and menu_signal < 0.58
        else 0.0
    )

    score_history = _append_signal_history(signal_history, "score", max(0.0, reliable_score_progress))
    death_history = _append_signal_history(signal_history, "death", death_signal)
    menu_history = _append_signal_history(signal_history, "menu", menu_signal)
    victory_history = _append_signal_history(signal_history, "victory", victory_text)
    death_text_history = _append_signal_history(signal_history, "death_text", death_text)
    _append_signal_history(signal_history, "scene_cut", scene_cut_candidate)
    confirmed_score = _confirmed_persistent_signal(score_history, 0.55, 0.35)
    confirmed_victory = _confirmed_persistent_signal(victory_history, 0.62, 0.46)
    confirmed_death_text = _confirmed_persistent_signal(death_text_history, 0.62, 0.46)
    confirmed_death = (
        1.0
        if confirmed_death_text > 0.0
        or (len(death_history) >= 2 and death_history[-1] > 0.75 and death_history[-2] > 0.65)
        else 0.0
    )
    confirmed_menu = _confirmed_persistent_signal(menu_history, 0.62, 0.42)

    human_progress = 0.0
    references = human_progress_reference or []
    if references:
        previous_hash = frame_hash(previous_frame, previous_chroma_blue, previous_chroma_red)
        previous_similarity = max(_perceptual_hash_similarity(previous_hash, target) for target in references)
        current_similarity = max(_perceptual_hash_similarity(current_key, target) for target in references)
        human_progress = max(-1.0, min(1.0, (current_similarity - previous_similarity) * 4.0))

    controllable_novelty_reward = (
        meaningful_change
        * persistence
        * max(0.0, 1.0 - min(1.0, flicker * 2.0))
        * max(0.0, 1.0 - min(1.0, global_shift * 2.5))
        * (1.0 - returned)
    )
    cycle_penalty = min(1.0, max(returned, jitter_signal * 0.85, confirmed_menu * 0.75))
    learned_progress_value = max(-1.0, min(1.0, float(learned_progress)))
    death_penalty = max(0.0, min(1.0, max(confirmed_death, death_signal * 0.25)))

    score_weight = configured(config.get("score_signal_weight"), 0.55, 0.0, 1.5)
    visual_reward_weight = configured(config.get("visual_change_reward_weight"), 0.025, 0.0, 0.10)
    explicit_task_strength = max(
        abs(reliable_score_progress),
        confirmed_victory,
        confirmed_level_transition,
    )
    learned_task_weight = configured(
        config.get("heuristic_task_aux_weight"),
        0.12,
        0.0,
        0.5,
    )
    # Learned progress is signed: regress is penalized, but early negative
    # predictions are attenuated to reduce damage from an immature model.
    reward_signals = learned_reward_signals or {}
    fallback_confidence = 1.0 if learned_reward_signals is None and abs(learned_progress_value) > 0.0 else 0.0
    learned_confidence = max(
        0.0,
        min(1.0, float(reward_signals.get("confidence", fallback_confidence))),
    )
    learned_success = max(0.0, min(1.0, float(reward_signals.get("success_probability", 0.0))))
    learned_failure = max(0.0, min(1.0, float(reward_signals.get("failure_probability", 0.0))))
    if learned_confidence >= 0.55:
        signed_progress = (
            learned_progress_value
            if learned_progress_value >= 0.0
            else 0.50 * learned_progress_value
        )
        learned_outcome = 0.55 * learned_success - 0.55 * learned_failure
        learned_task_reward = (
            learned_task_weight
            * (signed_progress + learned_outcome)
            * learned_confidence
            * max(0.0, 1.0 - explicit_task_strength)
        )
    else:
        signed_progress = 0.0
        learned_task_reward = 0.0
    task_reward = (
        score_weight * reliable_score_progress
        + 1.00 * confirmed_victory
        + 0.65 * confirmed_level_transition
        + learned_task_reward
    )
    exploration_reward = (
        visual_reward_weight * controllable_novelty_reward
        + 0.02 * max(0.0, learned_progress_value)
        + 0.03 * max(0.0, human_progress)
    )
    safety_penalty = (
        0.68 * death_penalty
        + 0.18 * health_loss
        + 0.09 * cycle_penalty
        + 0.05 * jitter_signal
    )
    metrics = {
        "score": float(score_signal),
        "confirmed_score": float(confirmed_score),
        "ocr_score": float(current_score) if current_score is not None else -1.0,
        "ocr_score_confidence": float(current_score_confidence),
        "ocr_score_progress": float(ocr_score_progress),
        "reliable_score_progress": float(reliable_score_progress),
        "victory_text": float(victory_text),
        "confirmed_victory": float(confirmed_victory),
        "level_transition": float(confirmed_level_transition),
        "scene_cut": float(scene_cut_candidate),
        "health": float(current_health) if current_health is not None else -1.0,
        "health_confidence": float(current_health_confidence),
        "health_loss": float(health_loss),
        "health_gain": float(health_gain),
        "death": float(death_signal),
        "death_text": float(death_text),
        "death_penalty": float(death_penalty),
        "menu": float(menu_signal),
        "confirmed_death": float(confirmed_death),
        "confirmed_menu": float(confirmed_menu),
        "human_progress": float(human_progress),
        "learned_progress": float(learned_progress_value),
        "learned_progress_signed": float(signed_progress),
        "learned_reward_confidence": float(learned_confidence),
        "learned_success_probability": float(learned_success),
        "learned_failure_probability": float(learned_failure),
        "learned_task_reward": float(learned_task_reward),
        "controllable_novelty": float(controllable_novelty_reward),
        "task_reward": float(max(-1.0, min(1.0, task_reward))),
        "exploration_reward": float(max(0.0, min(1.0, exploration_reward))),
        "safety_penalty": float(max(0.0, min(2.0, safety_penalty))),
        "cycle": float(cycle_penalty),
        "jitter": float(jitter_signal),
        "visual": float(meaningful_change),
        "persistence": float(persistence),
        "flicker": float(flicker),
        "fade": float(fade_score),
        "global_shift": float(global_shift),
        "spatial_progress": float(spatial_progress),
        "translation_confidence": float(translation_confidence),
        "state_key": current_key,
    }
    return compose_reward(metrics, config), metrics

def load_human_progress_reference(path: Path, limit: int = 512) -> list[str]:
    if not path.exists():
        return []
    connection = sqlite3.connect(path, timeout=30)
    try:
        rows = connection.execute(
            "SELECT episode_id,step,state,reward,done FROM transitions "
            "WHERE source='human' ORDER BY rowid DESC LIMIT ?",
            (max(64, int(limit) * 8),),
        ).fetchall()
    except sqlite3.DatabaseError:
        return []
    finally:
        connection.close()
    episodes: dict[str, list[tuple[int, bytes, float, bool]]] = {}
    for episode_id, step, state, reward, done in rows:
        try:
            blob = bytes(state)
            decode_temporal_state(blob)
            episodes.setdefault(str(episode_id), []).append((int(step), blob, float(reward), bool(done)))
        except Exception:
            continue
    ranked = []
    for _, items in episodes.items():
        items.sort(key=lambda item: item[0])
        if len(items) < 8:
            continue
        tail = items[max(1, len(items) // 2):]
        terminal_failure = bool(items[-1][3] and items[-1][2] < -0.60)
        if terminal_failure:
            continue
        quality = len(items) + 8.0 * sum(max(0.0, item[2]) for item in items)
        ranked.append((quality, tail))
    ranked.sort(key=lambda item: item[0], reverse=True)
    references = []
    seen = set()
    for _, items in ranked:
        for _, state, _, _ in items:
            digest = _temporal_frame_hash(state)
            if digest not in seen:
                seen.add(digest)
                references.append(digest)
                if len(references) >= max(1, int(limit)):
                    return references
    return references


def insert_transitions(path: Path, rows: list[tuple]) -> None:
    if not rows:
        return
    normalized_rows = []
    for row in rows:
        if len(row) == 12:
            normalized_rows.append(tuple(row))
            continue
        if len(row) != 9:
            raise ValueError("轨迹记录字段数量无效")
        episode_id, step, source, state, action, reward, next_state, done, priority = row
        normalized_rows.append(
            (
                episode_id,
                step,
                source,
                state,
                action,
                reward,
                next_state,
                done,
                priority,
                reward,
                0.0,
                max(0.0, -float(reward)),
            )
        )
    ensure_database(path)
    connection = sqlite3.connect(path, timeout=30)
    try:
        connection.executemany(
            "INSERT OR REPLACE INTO transitions("
            "episode_id,step,source,state,action,reward,next_state,done,priority,"
            "task_reward,exploration_reward,safety_penalty"
            ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            normalized_rows,
        )
        connection.commit()
    finally:
        connection.close()


def mark_episode_terminal(path: Path, episode_id: str) -> None:
    if not episode_id or not path.exists():
        return
    connection=sqlite3.connect(path,timeout=30)
    try:
        connection.execute(
            "UPDATE transitions SET done=1 WHERE episode_id=? AND step=(SELECT MAX(step) FROM transitions WHERE episode_id=?)",
            (episode_id,episode_id),
        )
        connection.commit()
    finally:
        connection.close()



def load_transition_graph(
    path: Path,
    limit: int = 50000,
    np=None,
    model: dict | None = None,
) -> dict[tuple[str, int], dict[str, object]]:
    ensure_database(path)
    graph: dict[tuple[str, int], dict[str, object]] = {}
    effective_limit = max(1, int(limit))
    if model is not None:
        tier = str(model.get("runtime_tier", "low_numpy"))
        semantic_limit = 12000 if tier == "high_directml" else (6000 if tier == "mid_onnx" else 2500)
        effective_limit = min(effective_limit, semantic_limit)
    state_keys: set[str] = set()
    connection = sqlite3.connect(path, timeout=30)
    try:
        cursor = connection.execute(
            "SELECT state,action,reward,next_state,done FROM transitions WHERE next_state IS NOT NULL ORDER BY rowid DESC LIMIT ?",
            (effective_limit,),
        )
        for state, action, reward, next_state, done in cursor:
            try:
                state_key_value = temporal_state_key(bytes(state), np, model)
                next_key = temporal_state_key(bytes(next_state), np, model)
                state_keys.add(state_key_value)
                state_keys.add(next_key)
                key = (state_key_value, int(action))
                entry = graph.setdefault(key, {"count": 0, "reward": 0.0, "terminal": 0, "next": {}})
                entry["count"] = int(entry["count"]) + 1
                entry["reward"] = float(entry["reward"]) + float(reward)
                entry["terminal"] = int(entry["terminal"]) + int(bool(done))
                next_counts = entry["next"]
                next_counts[next_key] = int(next_counts.get(next_key, 0)) + 1
            except Exception:
                continue
    finally:
        connection.close()
    graph["__state_keys__"] = tuple(sorted(state_keys))
    graph["__neighbor_cache__"] = {}
    return graph


def ensure_database(path: Path) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    rebuilt = False
    try:
        connection = sqlite3.connect(path, timeout=30)
        try:
            result = connection.execute("PRAGMA quick_check").fetchone()
            if result and result[0] != "ok":
                raise sqlite3.DatabaseError(str(result[0]))
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute("PRAGMA foreign_keys=ON")
            database_version=int(connection.execute("PRAGMA user_version").fetchone()[0])
            if database_version not in (0,DATABASE_SCHEMA) and database_version>DATABASE_SCHEMA:
                raise sqlite3.DatabaseError("经验数据库版本过新")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transitions(
                    episode_id TEXT NOT NULL,
                    step INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    state BLOB NOT NULL,
                    action INTEGER NOT NULL,
                    reward REAL NOT NULL,
                    next_state BLOB,
                    done INTEGER NOT NULL,
                    priority REAL NOT NULL,
                    task_reward REAL NOT NULL DEFAULT 0,
                    exploration_reward REAL NOT NULL DEFAULT 0,
                    safety_penalty REAL NOT NULL DEFAULT 0,
                    PRIMARY KEY(episode_id, step)
                )
                """
            )
            columns = [row[1] for row in connection.execute("PRAGMA table_info(transitions)")]
            legacy_expected = [
                "episode_id", "step", "source", "state", "action", "reward",
                "next_state", "done", "priority",
            ]
            if columns == legacy_expected and database_version <= 12:
                connection.execute(
                    "ALTER TABLE transitions ADD COLUMN task_reward REAL NOT NULL DEFAULT 0"
                )
                connection.execute(
                    "ALTER TABLE transitions ADD COLUMN exploration_reward REAL NOT NULL DEFAULT 0"
                )
                connection.execute(
                    "ALTER TABLE transitions ADD COLUMN safety_penalty REAL NOT NULL DEFAULT 0"
                )
                connection.execute(
                    "UPDATE transitions SET task_reward=reward,"
                    "exploration_reward=0,safety_penalty=MAX(0,-reward)"
                )
                columns = [
                    row[1]
                    for row in connection.execute("PRAGMA table_info(transitions)")
                ]
            expected = legacy_expected + [
                "task_reward", "exploration_reward", "safety_penalty",
            ]
            if columns != expected:
                raise sqlite3.DatabaseError("轨迹数据库结构无效")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_transitions_source_priority ON transitions(source, priority DESC)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_transitions_episode ON transitions(episode_id, step)")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS state_values(
                    state TEXT NOT NULL, action INTEGER NOT NULL, value REAL NOT NULL,
                    visits INTEGER NOT NULL, updated_at TEXT NOT NULL,
                    PRIMARY KEY(state, action)
                ) WITHOUT ROWID"""
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_state_values_rank ON state_values(visits DESC, updated_at DESC)")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS human_state_actions(
                    state TEXT NOT NULL, action INTEGER NOT NULL, demonstrations INTEGER NOT NULL,
                    updated_at TEXT NOT NULL, PRIMARY KEY(state, action)
                ) WITHOUT ROWID"""
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_human_state_actions_rank ON human_state_actions(demonstrations DESC, updated_at DESC)")
            legacy = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='samples'").fetchone()
            if legacy:
                rows = connection.execute("SELECT id,source,action,reward,feature_dim,feature FROM samples ORDER BY id").fetchall()
                migrated = []
                episode_index = 0
                episode_id = "legacy-000000"
                episode_step = 0
                for index, row in enumerate(rows):
                    sample_id, source, action, reward, feature_dim, feature = row
                    try:
                        normalized = normalize_feature_bytes(decompress_feature(bytes(feature), int(feature_dim)))
                        state = build_temporal_state([normalized], [], [])
                    except Exception:
                        continue
                    next_state = None
                    done = 1
                    if index + 1 < len(rows) and rows[index + 1][1] == source and episode_step < 511:
                        try:
                            next_normalized = normalize_feature_bytes(decompress_feature(bytes(rows[index + 1][5]), int(rows[index + 1][4])))
                            next_state = build_temporal_state([next_normalized], [int(action)], [0.08])
                            done = 0
                        except Exception:
                            next_state = None
                    migrated.append((episode_id, episode_step, str(source), state, encode_action_id(int(action), 2), float(reward), next_state, done, transition_priority(str(source), float(reward), bool(done))))
                    episode_step += 1
                    if done:
                        episode_index += 1
                        episode_id = f"legacy-{episode_index:06d}"
                        episode_step = 0
                if migrated:
                    connection.executemany(
                        "INSERT OR IGNORE INTO transitions("
                        "episode_id,step,source,state,action,reward,next_state,done,priority"
                        ") VALUES(?,?,?,?,?,?,?,?,?)",
                        migrated,
                    )
                    connection.execute(
                        "UPDATE transitions SET task_reward=reward,"
                        "exploration_reward=0,safety_penalty=MAX(0,-reward) "
                        "WHERE episode_id LIKE 'legacy-%'"
                    )
                connection.execute("DROP TABLE samples")
            # Version 70/schema 13 encoded duration by multiplying the base
            # action id. Schema 14 stores duration in the temporal state only.
            # Convert every legacy id before publishing the new schema; derived
            # state/action caches are rebuilt because their keys used old ids.
            if database_version == 13:
                legacy_rows = connection.execute(
                    "SELECT episode_id,step,state,action,next_state FROM transitions"
                ).fetchall()
                converted_rows = []
                for episode_id, step, state, action, next_state in legacy_rows:
                    converted_rows.append((
                        max(0, int(action)) // DURATION_HEAD_SIZE,
                        _convert_legacy_temporal_action_schema(bytes(state)),
                        (
                            _convert_legacy_temporal_action_schema(bytes(next_state))
                            if next_state is not None else None
                        ),
                        str(episode_id),
                        int(step),
                    ))
                if converted_rows:
                    connection.executemany(
                        "UPDATE transitions SET action=?,state=?,next_state=? "
                        "WHERE episode_id=? AND step=?",
                        converted_rows,
                    )
                connection.execute("DELETE FROM state_values")
                connection.execute("DELETE FROM human_state_actions")
            connection.execute(f"PRAGMA user_version={DATABASE_SCHEMA}")
            connection.commit()
        finally:
            connection.close()
        return rebuilt
    except Exception:
        backup_corrupt(path)
        remove_sqlite_sidecars(path)
        connection = sqlite3.connect(path, timeout=30)
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute("CREATE TABLE transitions(episode_id TEXT NOT NULL,step INTEGER NOT NULL,source TEXT NOT NULL,state BLOB NOT NULL,action INTEGER NOT NULL,reward REAL NOT NULL,next_state BLOB,done INTEGER NOT NULL,priority REAL NOT NULL,task_reward REAL NOT NULL DEFAULT 0,exploration_reward REAL NOT NULL DEFAULT 0,safety_penalty REAL NOT NULL DEFAULT 0,PRIMARY KEY(episode_id,step))")
            connection.execute("CREATE INDEX idx_transitions_source_priority ON transitions(source, priority DESC)")
            connection.execute("CREATE INDEX idx_transitions_episode ON transitions(episode_id, step)")
            connection.execute("CREATE TABLE state_values(state TEXT NOT NULL,action INTEGER NOT NULL,value REAL NOT NULL,visits INTEGER NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(state,action)) WITHOUT ROWID")
            connection.execute("CREATE INDEX idx_state_values_rank ON state_values(visits DESC, updated_at DESC)")
            connection.execute("CREATE TABLE human_state_actions(state TEXT NOT NULL,action INTEGER NOT NULL,demonstrations INTEGER NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(state,action)) WITHOUT ROWID")
            connection.execute("CREATE INDEX idx_human_state_actions_rank ON human_state_actions(demonstrations DESC, updated_at DESC)")
            connection.execute(f"PRAGMA user_version={DATABASE_SCHEMA}")
            connection.commit()
        finally:
            connection.close()
        return True



def verify_experience_database(path: Path, action_count: int, scan_limit: int, stop_event: threading.Event | None) -> dict:
    ensure_database(path)
    checked = 0
    removed = 0
    migrated = 0
    invalid: list[tuple[str, int]] = []
    migration_rows: list[tuple[int, bytes, bytes | None, str, int]] = []
    connection = sqlite3.connect(path, timeout=60)
    install_sqlite_cancel_handler(connection, stop_event)
    try:
        if int(connection.execute("PRAGMA user_version").fetchone()[0]) != DATABASE_SCHEMA:
            raise sqlite3.DatabaseError("经验数据库 schema 无效")
        if [str(row[0]) for row in connection.execute("PRAGMA integrity_check").fetchall()] != ["ok"]:
            raise sqlite3.DatabaseError("经验数据库完整性失败")
        cursor = connection.execute(
            "SELECT episode_id,step,source,state,action,reward,next_state,done,priority,"
            "task_reward,exploration_reward,safety_penalty "
            "FROM transitions ORDER BY rowid DESC LIMIT ?",
            (max(1, int(scan_limit)),),
        )
        maximum_action = action_space_size(action_count)
        for (episode_id, step, source, state, action, reward, next_state, done, priority,
             task_reward, exploration_reward, safety_penalty) in cursor:
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("操作已取消")
            checked += 1
            try:
                if not isinstance(episode_id, str) or not episode_id or int(step) < 0 or source not in ("human", "ai"):
                    raise ValueError
                raw_action = int(action)
                normalized_action_id = raw_action
                if raw_action >= action_count and raw_action < action_count * DURATION_HEAD_SIZE:
                    normalized_action_id = raw_action // DURATION_HEAD_SIZE
                if not 0 <= normalized_action_id < maximum_action:
                    raise ValueError
                if not math.isfinite(float(reward)) or not -1.0001 <= float(reward) <= 1.0001:
                    raise ValueError
                if int(done) not in (0, 1) or not math.isfinite(float(priority)) or float(priority) <= 0:
                    raise ValueError
                if (
                    not math.isfinite(float(task_reward)) or not -1.0001 <= float(task_reward) <= 1.0001
                    or not math.isfinite(float(exploration_reward)) or not 0.0 <= float(exploration_reward) <= 1.0001
                    or not math.isfinite(float(safety_penalty)) or not 0.0 <= float(safety_penalty) <= 2.0001
                ):
                    raise ValueError
                state_blob = _normalize_temporal_action_schema(bytes(state), action_count)
                next_blob = _normalize_temporal_action_schema(bytes(next_state), action_count) if next_state is not None else None
                if not int(done) and next_blob is None:
                    raise ValueError
                if normalized_action_id != raw_action or state_blob != bytes(state) or (next_state is not None and next_blob != bytes(next_state)):
                    migration_rows.append((normalized_action_id, state_blob, next_blob, str(episode_id), int(step)))
                    if len(migration_rows) >= 128:
                        connection.executemany(
                            "UPDATE transitions SET action=?,state=?,next_state=? WHERE episode_id=? AND step=?",
                            migration_rows,
                        )
                        migrated += len(migration_rows)
                        migration_rows.clear()
            except Exception:
                invalid.append((str(episode_id), int(step)))
                if len(invalid) >= 256:
                    removed += len(invalid)
                    connection.executemany("DELETE FROM transitions WHERE episode_id=? AND step=?", invalid)
                    invalid.clear()
        if migration_rows:
            connection.executemany(
                "UPDATE transitions SET action=?,state=?,next_state=? WHERE episode_id=? AND step=?",
                migration_rows,
            )
            migrated += len(migration_rows)
        if invalid:
            removed += len(invalid)
            connection.executemany("DELETE FROM transitions WHERE episode_id=? AND step=?", invalid)
        # Old schema-14 online memories used duration-expanded action ids. They are
        # disposable caches, so remove only the out-of-range rows rather than the trajectories.
        connection.execute("DELETE FROM state_values WHERE action<0 OR action>=?", (action_count,))
        connection.execute("DELETE FROM human_state_actions WHERE action<0 OR action>=?", (action_count,))
        connection.commit()
        count = int(connection.execute("SELECT COUNT(*) FROM transitions").fetchone()[0])
        return {"checked": checked, "removed": removed, "migrated": migrated, "records": count}
    except sqlite3.DatabaseError as error:
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


def resize_feature_plane(
    plane: bytes,
    source_width: int,
    source_height: int,
    target_width: int = FEATURE_WIDTH,
    target_height: int = FEATURE_HEIGHT,
) -> bytes:
    if len(plane) != int(source_width) * int(source_height):
        raise ValueError("经验特征平面尺寸错误")
    if source_width == target_width and source_height == target_height:
        return bytes(plane)
    output = bytearray(target_width * target_height)
    for target_y in range(target_height):
        source_y = min(source_height - 1, (target_y * source_height + target_height // 2) // target_height)
        for target_x in range(target_width):
            source_x = min(source_width - 1, (target_x * source_width + target_width // 2) // target_width)
            output[target_y * target_width + target_x] = plane[source_y * source_width + source_x]
    return bytes(output)


def normalize_feature_bytes(feature: bytes) -> bytes:
    if len(feature) == FEATURE_DIM:
        return feature
    if len(feature) == V74_FEATURE_DIM:
        return bytes(feature) + bytes(SPATIAL_CONTEXT_DIM)
    legacy_pixels = LEGACY_FEATURE_WIDTH * LEGACY_FEATURE_HEIGHT
    if len(feature) == V69_FEATURE_DIM:
        gray = resize_feature_plane(feature[:legacy_pixels], LEGACY_FEATURE_WIDTH, LEGACY_FEATURE_HEIGHT)
        difference = resize_feature_plane(
            feature[legacy_pixels:legacy_pixels * 2],
            LEGACY_FEATURE_WIDTH,
            LEGACY_FEATURE_HEIGHT,
        )
        signed = resize_feature_plane(
            feature[legacy_pixels * 2:legacy_pixels * 3],
            LEGACY_FEATURE_WIDTH,
            LEGACY_FEATURE_HEIGHT,
        )
        color_start = legacy_pixels * 3
        legacy_blue = resize_feature_plane(
            feature[color_start:color_start + LEGACY_COLOR_PIXELS],
            LEGACY_COLOR_WIDTH,
            LEGACY_COLOR_HEIGHT,
        )
        legacy_red = resize_feature_plane(
            feature[color_start + LEGACY_COLOR_PIXELS:color_start + LEGACY_COLOR_PIXELS * 2],
            LEGACY_COLOR_WIDTH,
            LEGACY_COLOR_HEIGHT,
        )
        blue = bytes(
            max(0, min(255, int(y) + ((454 * (int(cb) - 128)) >> 8)))
            for y, cb in zip(gray, legacy_blue)
        )
        red = bytes(
            max(0, min(255, int(y) + ((359 * (int(cr) - 128)) >> 8)))
            for y, cr in zip(gray, legacy_red)
        )
        return gray + difference + signed + blue + red + bytes(SPATIAL_CONTEXT_DIM)
    if len(feature) == V27_FEATURE_DIM:
        gray = resize_feature_plane(feature[:legacy_pixels], LEGACY_FEATURE_WIDTH, LEGACY_FEATURE_HEIGHT)
        difference = resize_feature_plane(
            feature[legacy_pixels:legacy_pixels * 2],
            LEGACY_FEATURE_WIDTH,
            LEGACY_FEATURE_HEIGHT,
        )
        signed = resize_feature_plane(
            feature[legacy_pixels * 2:legacy_pixels * 3],
            LEGACY_FEATURE_WIDTH,
            LEGACY_FEATURE_HEIGHT,
        )
        return gray + difference + signed + gray + gray + bytes(SPATIAL_CONTEXT_DIM)
    if len(feature) == LEGACY_FEATURE_DIM:
        gray = resize_feature_plane(feature[:legacy_pixels], LEGACY_FEATURE_WIDTH, LEGACY_FEATURE_HEIGHT)
        difference = resize_feature_plane(
            feature[legacy_pixels:legacy_pixels * 2],
            LEGACY_FEATURE_WIDTH,
            LEGACY_FEATURE_HEIGHT,
        )
        signed = bytes([128]) * (FEATURE_WIDTH * FEATURE_HEIGHT)
        return gray + difference + signed + gray + gray + bytes(SPATIAL_CONTEXT_DIM)
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


def insert_samples(path: Path, rows: list) -> None:
    converted = []
    for index, row in enumerate(rows):
        if len(row) == 9:
            converted.append(tuple(row))
            continue
        if len(row) == 6:
            created_at, source, action, reward, feature_dim, feature = row
            frame = normalize_feature_bytes(decompress_feature(feature, feature_dim))
            state = build_temporal_state([frame], [], [])
            converted.append((f"compat-{created_at}-{index}", 0, source, state, encode_action_id(action, 2), reward, None, 1, transition_priority(source, reward, True)))
    insert_transitions(path, converted)



def count_samples(path: Path) -> tuple[int, int]:
    ensure_database(path);connection=sqlite3.connect(path,timeout=20)
    try:
        total=int(connection.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]);human=int(connection.execute("SELECT COUNT(*) FROM transitions WHERE source='human'").fetchone()[0]);return total,human
    finally: connection.close()



def compact_experience(path: Path, limit: int, action_count: int) -> dict:
    ensure_database(path)
    maximum = max(1000, int(limit))
    connection = sqlite3.connect(path, timeout=60)
    try:
        total = int(connection.execute("SELECT COUNT(*) FROM transitions").fetchone()[0])
        human = int(connection.execute("SELECT COUNT(*) FROM transitions WHERE source='human'").fetchone()[0])
        ai = total - human
        removed = 0
        if total > maximum:
            episode_rows = connection.execute(
                "SELECT episode_id,MAX(priority),MAX(rowid),COUNT(*) FROM transitions GROUP BY episode_id ORDER BY MAX(priority) DESC,MAX(rowid) DESC"
            ).fetchall()
            retained = []
            retained_count = 0
            human_episodes = [row for row in episode_rows if connection.execute("SELECT 1 FROM transitions WHERE episode_id=? AND source='human' LIMIT 1", (row[0],)).fetchone()]
            other_episodes = [row for row in episode_rows if row not in human_episodes]
            for row in human_episodes + other_episodes:
                if retained_count >= maximum and retained:
                    break
                retained.append(str(row[0])); retained_count += int(row[3])
            if retained:
                placeholders = ",".join("?" for _ in retained)
                before = connection.total_changes
                connection.execute(f"DELETE FROM transitions WHERE episode_id NOT IN ({placeholders})", retained)
                removed = connection.total_changes - before
        connection.commit()
        total = int(connection.execute("SELECT COUNT(*) FROM transitions").fetchone()[0])
        human = int(connection.execute("SELECT COUNT(*) FROM transitions WHERE source='human'").fetchone()[0])
        return {"records": total, "human": human, "ai": total - human, "removed": removed}
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



def transition_graph_state_neighbors(
    transition_graph: dict,
    state_key_value: str,
    maximum_distance: int = 10,
    limit: int = 6,
) -> tuple[str, ...]:
    if not transition_graph or STABLE_STATE_KEY_PATTERN.fullmatch(state_key_value) is None:
        return (state_key_value,)
    cache = transition_graph.get("__neighbor_cache__")
    if isinstance(cache, dict) and state_key_value in cache:
        return tuple(cache[state_key_value])
    candidates = []
    for candidate in transition_graph.get("__state_keys__", ()):
        distance = stable_state_distance(state_key_value, str(candidate))
        if distance <= max(0, int(maximum_distance)):
            candidates.append((distance, str(candidate)))
    candidates.sort(key=lambda item: (item[0], item[1]))
    result = tuple(value for _, value in candidates[:max(1, int(limit))])
    if not result:
        result = (state_key_value,)
    if isinstance(cache, dict):
        if len(cache) >= 4096:
            cache.pop(next(iter(cache)), None)
        cache[state_key_value] = result
    return result


def sequence_plan_values(
    np,
    profile: dict,
    action_count: int,
    horizon: int,
    discount: float,
    state: bytes | None = None,
    transition_graph: dict | None = None,
    model_values=None,
    model: dict | None = None,
):
    count = action_space_size(action_count)
    result = np.zeros(count, dtype=np.float64)
    if state is None or not transition_graph:
        return result
    state_key_value = temporal_state_key(state, np, model)
    state_neighbors = transition_graph_state_neighbors(
        transition_graph,
        state_key_value,
    )
    state_key_value = next(
        (
            candidate
            for candidate in state_neighbors
            if any(
                (candidate, action_id) in transition_graph
                for action_id in range(count)
            )
        ),
        state_neighbors[0],
    )
    horizon = max(1, min(8, int(horizon)))
    discount = max(0.1, min(0.98, float(discount)))
    base_values = np.zeros(count, dtype=np.float64) if model_values is None else np.asarray(model_values, dtype=np.float64)
    memo: dict[tuple[str, int], float] = {}

    def value(node_key: str, depth: int) -> float:
        cache_key = (node_key, depth)
        if cache_key in memo:
            return memo[cache_key]
        if depth <= 0:
            answer = 0.0
        else:
            candidates = []
            for action_id in range(count):
                entry = transition_graph.get((node_key, action_id))
                if not entry:
                    continue
                visits = max(1, int(entry["count"]))
                immediate = float(entry["reward"]) / visits
                terminal_rate = float(entry["terminal"]) / visits
                future = 0.0
                next_counts = entry["next"]
                next_total = sum(int(v) for v in next_counts.values())
                if depth > 1 and next_total > 0 and terminal_rate < 0.95:
                    future = sum(int(v) * value(k, depth - 1) for k, v in next_counts.items()) / next_total
                confidence = min(1.0, math.log1p(visits) / math.log(33.0))
                candidates.append(immediate + discount * (1.0 - terminal_rate) * confidence * future)
            answer = max(candidates) if candidates else 0.0
        memo[cache_key] = answer
        return answer

    for action_id in range(count):
        entry = transition_graph.get((state_key_value, action_id))
        if not entry:
            continue
        visits = max(1, int(entry["count"]))
        immediate = float(entry["reward"]) / visits
        terminal_rate = float(entry["terminal"]) / visits
        next_counts = entry["next"]
        next_total = sum(int(v) for v in next_counts.values())
        future = 0.0
        if horizon > 1 and next_total > 0:
            future = sum(int(v) * value(k, horizon - 1) for k, v in next_counts.items()) / next_total
        confidence = min(1.0, math.log1p(visits) / math.log(33.0))
        result[action_id] = confidence * (immediate + discount * (1.0 - terminal_rate) * future) + (1.0 - confidence) * float(base_values[action_id])
    return np.clip(result, -1.0, 1.0)



def _adaptive_spatial_pool(np, plane, height: int, width: int, rows: int, columns: int):
    if isinstance(plane, (bytes, bytearray, memoryview)):
        values = np.frombuffer(plane, dtype=np.uint8).astype(np.float32).reshape(height, width) / 255.0
    else:
        values = np.asarray(plane, dtype=np.float32).reshape(height, width)
        if values.size and float(np.max(values)) > 1.5:
            values = values / 255.0
    centered = np.clip((values - float(values.mean())) / max(0.08, float(values.std()) * 3.0), -1.0, 1.0)
    vertical = np.zeros_like(centered)
    horizontal = np.zeros_like(centered)
    vertical[1:] = np.abs(centered[1:] - centered[:-1])
    horizontal[:, 1:] = np.abs(centered[:, 1:] - centered[:, :-1])
    edges = np.clip(vertical + horizontal, 0.0, 1.0)
    pooled = []
    edge_pooled = []
    for row in range(rows):
        top, bottom = row * height // rows, (row + 1) * height // rows
        for column in range(columns):
            left, right = column * width // columns, (column + 1) * width // columns
            pooled.append(float(centered[top:bottom, left:right].mean()))
            edge_pooled.append(float(edges[top:bottom, left:right].mean()))
    return np.asarray(pooled + edge_pooled, dtype=np.float32)


def _spatial_branch_features(np, feature: bytes):
    normalized = normalize_feature_bytes(feature)
    context = normalized[BASE_FEATURE_DIM:]
    if len(context) != SPATIAL_CONTEXT_DIM:
        raise ValueError("空间分支内容无效")
    full_end = SPATIAL_FULL_PIXELS
    hud_end = full_end + SPATIAL_HUD_PIXELS
    full = _adaptive_spatial_pool(
        np,
        context[:full_end],
        SPATIAL_FULL_HEIGHT,
        SPATIAL_FULL_WIDTH,
        SPATIAL_FULL_POOL_ROWS,
        SPATIAL_FULL_POOL_COLUMNS,
    )
    hud = _adaptive_spatial_pool(
        np,
        context[full_end:hud_end],
        SPATIAL_HUD_HEIGHT,
        SPATIAL_FULL_WIDTH,
        SPATIAL_HUD_POOL_ROWS,
        SPATIAL_HUD_POOL_COLUMNS,
    )
    mouse = _adaptive_spatial_pool(
        np,
        context[hud_end:],
        SPATIAL_MOUSE_SIZE,
        SPATIAL_MOUSE_SIZE,
        SPATIAL_MOUSE_POOL_ROWS,
        SPATIAL_MOUSE_POOL_COLUMNS,
    )
    result = np.concatenate((full, hud, mouse)).astype(np.float32, copy=False)
    if result.shape != (SPATIAL_BRANCH_FEATURE_DIM,):
        raise RuntimeError("空间分支编码尺寸无效")
    return result


def _frame_channels(np, feature: bytes):
    feature = normalize_feature_bytes(feature)
    pixels = FEATURE_WIDTH * FEATURE_HEIGHT
    raw = np.frombuffer(feature[:BASE_FEATURE_DIM], dtype=np.uint8).astype(np.float32)
    image = raw[:pixels].reshape(FEATURE_HEIGHT, FEATURE_WIDTH) / 255.0
    difference = raw[pixels:pixels * 2].reshape(FEATURE_HEIGHT, FEATURE_WIDTH) / 255.0
    signed = np.clip((raw[pixels * 2:pixels * 3] - 128.0) / 127.0, -1.0, 1.0).reshape(FEATURE_HEIGHT, FEATURE_WIDTH)
    start = pixels * 3
    blue_rgb = raw[start:start + COLOR_PIXELS].reshape(COLOR_HEIGHT, COLOR_WIDTH)
    red_rgb = raw[start + COLOR_PIXELS:start + COLOR_FEATURE_DIM].reshape(COLOR_HEIGHT, COLOR_WIDTH)
    green_rgb = np.clip(
        (image * 255.0 * 256.0 - 77.0 * red_rgb - 29.0 * blue_rgb) / 150.0,
        0.0,
        255.0,
    )
    red = red_rgb / 127.5 - 1.0
    green = green_rgb / 127.5 - 1.0
    blue = blue_rgb / 127.5 - 1.0
    centered = np.clip((image - float(image.mean())) / max(0.08, float(image.std()) * 3.0), -1.0, 1.0)
    hud_mask = np.zeros_like(image, dtype=np.float32)
    hud_rows = max(2, FEATURE_HEIGHT // 6)
    hud_columns = max(2, FEATURE_WIDTH // 12)
    hud_mask[:hud_rows, :] = 1.0
    hud_mask[-max(2, FEATURE_HEIGHT // 8):, :] = 1.0
    hud_mask[:, :hud_columns] = np.maximum(hud_mask[:, :hud_columns], 0.55)
    hud_mask[:, -hud_columns:] = np.maximum(hud_mask[:, -hud_columns:], 0.55)
    hud_channel = centered * hud_mask
    base = np.stack(
        (
            red,
            green,
            blue,
            np.sqrt(np.maximum(0.0, difference)),
            signed,
            hud_channel,
        ),
        axis=0,
    ).astype(np.float32)
    return {
        "base": base,
        "spatial": _spatial_branch_features(np, feature),
    }


def _synchronize_quantized_conv_weights(np, model: dict) -> None:
    master = np.asarray(model["conv_master_w"], dtype=np.float32)
    maximum = float(np.max(np.abs(master), initial=0.0))
    scale = max(1e-6, maximum / 127.0)
    model["conv_scale"] = np.asarray([scale], dtype=np.float32)
    model["conv_w"] = np.clip(np.rint(master / scale), -127, 127).astype(np.int8)


def _pool_channel_features(np, convolved, rows: int, columns: int):
    pooled = []
    height, width = convolved.shape[1:]
    bounds = []
    for y in range(rows):
        top, bottom = y * height // rows, (y + 1) * height // rows
        for x in range(columns):
            left, right = x * width // columns, (x + 1) * width // columns
            pooled.extend(convolved[:, top:bottom, left:right].mean(axis=(1, 2)).tolist())
            bounds.append((top, bottom, left, right))
    return np.asarray(pooled, dtype=np.float32), bounds


def base_visual_encoder_output_dim() -> int:
    return (
        CNN_OUTPUT_CHANNELS * CNN_POOL_ROWS * CNN_POOL_COLUMNS
        + CNN_MID_CHANNELS * CNN_MID_POOL_ROWS * CNN_MID_POOL_COLUMNS
        + CNN_CHANNELS * 4
    )


def visual_encoder_output_dim() -> int:
    return base_visual_encoder_output_dim() + SPATIAL_BRANCH_FEATURE_DIM


def _depthwise_separable_block(np, source, depthwise_w, pointwise_w, bias, return_cache: bool = False):
    source = source.astype(np.float32, copy=False)
    windows = np.lib.stride_tricks.sliding_window_view(source, (3, 3), axis=(1, 2))[:, ::2, ::2, :, :]
    depthwise = np.einsum("cijmn,cmn->cij", windows, depthwise_w, optimize=True)
    projected_pre = np.einsum("cij,oc->oij", depthwise, pointwise_w, optimize=True)
    projected_pre += bias[:, None, None]
    output = np.maximum(0.0, projected_pre).astype(np.float32, copy=False)
    if not return_cache:
        return output
    return output, {
        "source_shape": source.shape,
        "windows": windows,
        "depthwise": depthwise,
        "projected_pre": projected_pre,
        "depthwise_w": depthwise_w,
        "pointwise_w": pointwise_w,
    }



def _visual_pyramid_features(np, model: dict, stem, return_cache: bool = False):
    if return_cache:
        middle, middle_cache = _depthwise_separable_block(
            np, stem, model["conv2_depthwise_w"], model["conv2_pointwise_w"], model["conv2_b"], True
        )
        final, final_cache = _depthwise_separable_block(
            np, middle, model["conv3_depthwise_w"], model["conv3_pointwise_w"], model["conv3_b"], True
        )
    else:
        middle = _depthwise_separable_block(
            np, stem, model["conv2_depthwise_w"], model["conv2_pointwise_w"], model["conv2_b"]
        )
        final = _depthwise_separable_block(
            np, middle, model["conv3_depthwise_w"], model["conv3_pointwise_w"], model["conv3_b"]
        )
        middle_cache = final_cache = None
    final_pool, final_bounds = _pool_channel_features(np, final, CNN_POOL_ROWS, CNN_POOL_COLUMNS)
    middle_pool, middle_bounds = _pool_channel_features(np, middle, CNN_MID_POOL_ROWS, CNN_MID_POOL_COLUMNS)
    height, width = stem.shape[1:]
    top_rows = max(1, height // 5)
    bottom_rows = max(1, height // 6)
    side_columns = max(1, width // 10)
    hud_pool = np.concatenate((
        stem[:, :top_rows, :].mean(axis=(1, 2)),
        stem[:, -bottom_rows:, :].mean(axis=(1, 2)),
        stem[:, :, :side_columns].mean(axis=(1, 2)),
        stem[:, :, -side_columns:].mean(axis=(1, 2)),
    )).astype(np.float32, copy=False)
    features = np.concatenate((final_pool, middle_pool, hud_pool)).astype(np.float32, copy=False)
    if not return_cache:
        return features
    return features, {
        "stem_shape": stem.shape,
        "middle_shape": middle.shape,
        "final_shape": final.shape,
        "middle_cache": middle_cache,
        "final_cache": final_cache,
        "final_bounds": final_bounds,
        "middle_bounds": middle_bounds,
        "hud_geometry": (top_rows, bottom_rows, side_columns),
    }



def _quantized_conv_features(np, model: dict, frame, return_cache: bool = False, training: bool = False):
    if isinstance(frame, dict):
        base_frame = np.asarray(frame["base"], dtype=np.float32)
        spatial = np.asarray(frame["spatial"], dtype=np.float32).reshape(SPATIAL_BRANCH_FEATURE_DIM)
    else:
        base_frame = np.asarray(frame, dtype=np.float32)
        spatial = np.zeros(SPATIAL_BRANCH_FEATURE_DIM, dtype=np.float32)
    # Training always uses the float master weights and a straight-through input
    # quantizer. Inference may use QLinearConv through ONNX Runtime.
    quantized = np.clip(np.rint(base_frame / 0.01) + 128.0, 0, 255).astype(np.uint8)
    dequantized = (quantized.astype(np.float32) - 128.0) * 0.01
    convolved = None
    if not training and not return_cache and str(model.get("runtime_tier", "low_numpy")) != "low_numpy":
        session = accelerated_vision_session(model)
        if session is not None:
            try:
                convolved = session.run(["output"], {"input": quantized[None, ...]})[0][0][:, ::2, ::2].astype(np.float32, copy=False)
            except Exception:
                convolved = None
    stem_cache = None
    if convolved is None:
        windows = np.lib.stride_tricks.sliding_window_view(dequantized, (3, 3), axis=(1, 2))[:, ::2, ::2, :, :]
        weights = (
            np.asarray(model["conv_master_w"], dtype=np.float32)
            if training or return_cache
            else model["conv_w"].astype(np.float32) * float(model["conv_scale"][0])
        )
        raw = np.einsum("cijmn,ocmn->oij", windows, weights, optimize=True)
        raw += model["conv_b"][:, None, None]
        if training or return_cache:
            convolved = np.maximum(0.0, raw).astype(np.float32, copy=False)
        else:
            convolved = np.clip(np.rint(np.maximum(0.0, raw) / 0.02), 0, 255).astype(np.float32) * 0.02
        if return_cache:
            stem_cache = {"windows": windows, "raw": raw, "shape": convolved.shape}
    if return_cache:
        pooled, pyramid_cache = _visual_pyramid_features(np, model, convolved, True)
        combined = np.concatenate((pooled, spatial)).astype(np.float32, copy=False)
        return combined, {"stem": stem_cache, "pyramid": pyramid_cache}
    pooled = _visual_pyramid_features(np, model, convolved)
    return np.concatenate((pooled, spatial)).astype(np.float32, copy=False)



def _sigmoid(np, value):
    value = np.clip(value, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-value))


def factorized_action_outputs(np, model: dict, feature: bytes):
    hidden = _model_hidden_state(np, model, feature)
    return factorized_action_outputs_from_hidden(np, model, hidden)

def feature_vector(np, feature: bytes):
    frames, actions, durations = decode_temporal_state(feature)
    return {
        "frames": [_frame_channels(np, frame) for frame in frames],
        "actions": np.asarray(actions, dtype=np.int32),
        "durations": np.asarray(durations, dtype=np.float32),
    }


def second_hidden_size(hidden_size: int) -> int:
    return max(8, min(2048, int(hidden_size)))




def initialize_model(np, input_dim: int, hidden_size: int, output_size: int) -> dict:
    hidden = second_hidden_size(hidden_size)
    action_dim = action_space_size(output_size)
    rng = np.random.default_rng()
    encoder_rng = np.random.default_rng(VISUAL_INITIALIZATION_SEED)
    conv_w = np.clip(
        np.rint(
            encoder_rng.standard_normal(
                (CNN_CHANNELS, MODEL_PIXEL_CHANNELS, 3, 3)
            ) * 2.8
        ),
        -7,
        7,
    ).astype(np.int8)
    sobel_x = np.asarray(((-1, 0, 1), (-2, 0, 2), (-1, 0, 1)), dtype=np.int8)
    sobel_y = sobel_x.T.copy()
    laplace = np.asarray(((0, 1, 0), (1, -4, 1), (0, 1, 0)), dtype=np.int8)
    for input_channel in range(3):
        conv_w[0, input_channel] = sobel_x
        conv_w[1, input_channel] = sobel_y
        conv_w[2, input_channel] = laplace
    conv_w[3].fill(0)
    conv_w[3, 0, 1, 1] = 4
    conv_w[3, 1, 1, 1] = -4
    conv_w[4].fill(0)
    conv_w[4, 2, 1, 1] = 4
    conv_w[4, 1, 1, 1] = -4
    conv_w[5].fill(0)
    conv_w[5, 3, 1, 1] = 5
    conv_scale = np.asarray([0.045], dtype=np.float32)
    visual_dim = visual_encoder_output_dim()
    context_dim = MODEL_GLOBAL_FEATURES
    conv2_depthwise = (
        encoder_rng.standard_normal((CNN_CHANNELS, 3, 3)).astype(np.float32) * 0.11
    )
    conv2_depthwise[:, 1, 1] += 0.34
    conv2_pointwise = (
        encoder_rng.standard_normal((CNN_MID_CHANNELS, CNN_CHANNELS)).astype(np.float32)
        * (2.0 / CNN_CHANNELS) ** 0.5
    )
    conv3_depthwise = (
        encoder_rng.standard_normal((CNN_MID_CHANNELS, 3, 3)).astype(np.float32) * 0.09
    )
    conv3_depthwise[:, 1, 1] += 0.30
    conv3_pointwise = (
        encoder_rng.standard_normal((CNN_OUTPUT_CHANNELS, CNN_MID_CHANNELS)).astype(np.float32)
        * (2.0 / CNN_MID_CHANNELS) ** 0.5
    )

    def weight(shape, scale):
        return rng.standard_normal(shape).astype(np.float32) * scale

    model = {
        "schema": MODEL_SCHEMA,
        "input_dim": int(input_dim),
        "hidden_size": hidden,
        "output_size": int(output_size),
        "temporal_frames": TEMPORAL_FRAMES,
        "conv_w": conv_w,
        "conv_scale": conv_scale,
        "conv_b": np.zeros(CNN_CHANNELS, dtype=np.float32),
        "conv_master_w": conv_w.astype(np.float32) * float(conv_scale[0]),
        "conv2_depthwise_w": conv2_depthwise,
        "conv2_pointwise_w": conv2_pointwise,
        "conv2_b": np.zeros(CNN_MID_CHANNELS, dtype=np.float32),
        "conv3_depthwise_w": conv3_depthwise,
        "conv3_pointwise_w": conv3_pointwise,
        "conv3_b": np.zeros(CNN_OUTPUT_CHANNELS, dtype=np.float32),
        "frame_proj": weight((visual_dim + context_dim, GRU_INPUT_SIZE), (2.0 / (visual_dim + context_dim)) ** 0.5),
        "frame_bias": np.zeros(GRU_INPUT_SIZE, dtype=np.float32),
        "action_embedding": weight((action_dim, ACTION_EMBEDDING_SIZE), 0.04),
        "duration_embedding": weight((DURATION_HEAD_SIZE, DURATION_EMBEDDING_SIZE), 0.04),
        "Wz": weight((GRU_INPUT_SIZE, hidden), 0.08),
        "Uz": weight((hidden, hidden), 0.05),
        "bz": np.zeros(hidden, dtype=np.float32),
        "Wr": weight((GRU_INPUT_SIZE, hidden), 0.08),
        "Ur": weight((hidden, hidden), 0.05),
        "br": np.zeros(hidden, dtype=np.float32),
        "Wh": weight((GRU_INPUT_SIZE, hidden), 0.08),
        "Uh": weight((hidden, hidden), 0.05),
        "bh": np.zeros(hidden, dtype=np.float32),
        "policy_control_w": weight((hidden, len(CONTROL_KINDS)), 0.04),
        "policy_control_b": np.zeros(len(CONTROL_KINDS), dtype=np.float32),
        "policy_key_w": weight((hidden, KEY_HEAD_SIZE), 0.03),
        "policy_key_b": np.zeros(KEY_HEAD_SIZE, dtype=np.float32),
        "policy_mouse_w": weight((hidden, MOUSE_HEAD_SIZE), 0.03),
        "policy_mouse_b": np.zeros(MOUSE_HEAD_SIZE, dtype=np.float32),
        "policy_button_w": weight((hidden, BUTTON_HEAD_SIZE), 0.03),
        "policy_button_b": np.zeros(BUTTON_HEAD_SIZE, dtype=np.float32),
        "policy_duration_w": weight((hidden, DURATION_HEAD_SIZE), 0.04),
        "policy_duration_b": np.zeros(DURATION_HEAD_SIZE, dtype=np.float32),
        "policy_duration_kind_b": np.zeros((len(CONTROL_KINDS), DURATION_HEAD_SIZE), dtype=np.float32),
        "policy_action_w": weight((hidden, action_dim), 0.02),
        "policy_action_b": np.zeros(action_dim, dtype=np.float32),
        "q_control_w": weight((Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, len(CONTROL_KINDS)), 0.025),
        "q_control_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, len(CONTROL_KINDS)), dtype=np.float32),
        "q_key_w": weight((Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, KEY_HEAD_SIZE), 0.02),
        "q_key_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, KEY_HEAD_SIZE), dtype=np.float32),
        "q_mouse_w": weight((Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, MOUSE_HEAD_SIZE), 0.02),
        "q_mouse_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, MOUSE_HEAD_SIZE), dtype=np.float32),
        "q_button_w": weight((Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, BUTTON_HEAD_SIZE), 0.02),
        "q_button_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, BUTTON_HEAD_SIZE), dtype=np.float32),
        "q_duration_w": weight((Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, DURATION_HEAD_SIZE), 0.025),
        "q_duration_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, DURATION_HEAD_SIZE), dtype=np.float32),
        "q_duration_kind_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, len(CONTROL_KINDS), DURATION_HEAD_SIZE), dtype=np.float32),
        "q_action_w": weight((Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, action_dim), 0.015),
        "q_action_b": np.zeros((Q_TWIN_COUNT, VALUE_HEAD_COUNT, action_dim), dtype=np.float32),
        "value_w": weight((hidden, 1), 0.02),
        "value_b": np.zeros(1, dtype=np.float32),
        "progress_w": weight((hidden, 1), 0.02),
        "progress_b": np.zeros(1, dtype=np.float32),
        "safety_w": weight((hidden, 1), 0.02),
        "safety_b": np.zeros(1, dtype=np.float32),
        "world_encoder_w": weight((WORLD_MODEL_MEMBERS, hidden, WORLD_LATENT_SIZE), (2.0 / hidden) ** 0.5),
        "world_encoder_b": np.zeros((WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE), dtype=np.float32),
        "world_dynamics_w": weight((WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE, WORLD_LATENT_SIZE), 0.045),
        "world_dynamics_action_w": weight((WORLD_MODEL_MEMBERS, ACTION_EMBEDDING_SIZE, WORLD_LATENT_SIZE), 0.045),
        "world_dynamics_duration_w": weight((WORLD_MODEL_MEMBERS, DURATION_EMBEDDING_SIZE, WORLD_LATENT_SIZE), 0.025),
        "world_dynamics_b": np.zeros((WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE), dtype=np.float32),
        "world_reward_w": weight((WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE, VALUE_HEAD_COUNT), 0.025),
        "world_reward_action_w": weight((WORLD_MODEL_MEMBERS, ACTION_EMBEDDING_SIZE, VALUE_HEAD_COUNT), 0.02),
        "world_reward_duration_w": weight((WORLD_MODEL_MEMBERS, DURATION_EMBEDDING_SIZE, VALUE_HEAD_COUNT), 0.015),
        "world_reward_b": np.zeros((WORLD_MODEL_MEMBERS, VALUE_HEAD_COUNT), dtype=np.float32),
        "world_done_w": weight((WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE, 1), 0.02),
        "world_done_b": np.zeros((WORLD_MODEL_MEMBERS, 1), dtype=np.float32),
        "world_latent_to_hidden_w": weight(
            (WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE, hidden),
            (2.0 / WORLD_LATENT_SIZE) ** 0.5,
        ),
        "world_latent_to_hidden_b": np.zeros((WORLD_MODEL_MEMBERS, hidden), dtype=np.float32),
        "reward_model_w": weight((REWARD_MODEL_MEMBERS, hidden, REWARD_MODEL_OUTPUTS), 0.02),
        "reward_model_b": np.zeros((REWARD_MODEL_MEMBERS, REWARD_MODEL_OUTPUTS), dtype=np.float32),
        "policy_skill_w": weight((hidden, SKILL_HEAD_SIZE), 0.02),
        "policy_skill_b": np.zeros(SKILL_HEAD_SIZE, dtype=np.float32),
        "skill_value_w": weight((hidden, SKILL_HEAD_SIZE), 0.015),
        "skill_value_b": np.zeros(SKILL_HEAD_SIZE, dtype=np.float32),
        "mouse_offset_w": np.zeros((hidden, 2), dtype=np.float32),
        "mouse_offset_b": np.zeros(2, dtype=np.float32),
        "action_factors": np.zeros((action_dim, 3), dtype=np.int16),
        "action_key_multihot": np.zeros((action_dim, KEY_HEAD_SIZE), dtype=np.float32),
        "action_button_multihot": np.zeros((action_dim, BUTTON_HEAD_SIZE), dtype=np.float32),
        "trained_samples": 0,
        "training_rounds": 0,
        "online_updates": 0,
        "action_hash": "",
        "action_signatures": [],
        "critic_names": list(CRITIC_NAMES),
        "q_twin_count": Q_TWIN_COUNT,
        "world_model_members": WORLD_MODEL_MEMBERS,
        "optimizer_step": 0,
        "optimizer_schedule_step": 0,
        "optimizer_keys": [],
        "optimizer_offsets": np.zeros(1, dtype=np.int64),
        "optimizer_m": np.zeros(0, dtype=np.float32),
        "optimizer_v": np.zeros(0, dtype=np.float32),
        "runtime_tier": "low_numpy",
        "validation_score": 0.0,
        "visual_pretraining_steps": 0,
        "world_training_steps": 0,
        "reward_model_training_steps": 0,
    }
    _synchronize_quantized_conv_weights(np, model)
    _reset_optimizer_state(np, model)
    return model




def _resize_exact_action_heads(np, model: dict, output_size: int, signatures: list[str]) -> bool:
    action_dim = action_space_size(output_size)
    hidden = int(model["hidden_size"])
    old_signatures = list(model.get("action_signatures", []))
    expected = {
        "policy_action_w": (hidden, action_dim),
        "policy_action_b": (action_dim,),
        "q_action_w": (Q_TWIN_COUNT, VALUE_HEAD_COUNT, hidden, action_dim),
        "q_action_b": (Q_TWIN_COUNT, VALUE_HEAD_COUNT, action_dim),
        "action_embedding": (action_dim, ACTION_EMBEDDING_SIZE),
    }
    if all(key in model and model[key].shape == shape for key, shape in expected.items()):
        return False
    seed = initialize_model(np, int(model["input_dim"]), hidden, output_size)
    replacements = {key: seed[key] for key in expected}
    old_index = {signature: index for index, signature in enumerate(old_signatures)}
    for new_action, signature in enumerate(signatures):
        previous_action = old_index.get(signature)
        if previous_action is None or previous_action >= model.get("policy_action_b", np.empty(0)).shape[-1]:
            continue
        replacements["policy_action_w"][:, new_action] = model["policy_action_w"][:, previous_action]
        replacements["policy_action_b"][new_action] = model["policy_action_b"][previous_action]
        replacements["q_action_w"][:, :, :, new_action] = model["q_action_w"][:, :, :, previous_action]
        replacements["q_action_b"][:, :, new_action] = model["q_action_b"][:, :, previous_action]
        if previous_action < model.get("action_embedding", np.empty((0, 0))).shape[0]:
            replacements["action_embedding"][new_action] = model["action_embedding"][previous_action]
    model.update(replacements)
    return True



def load_model(np, path: Path, input_dim: int, hidden_size: int, output_size: int, action_list: list[dict]) -> tuple[dict, bool]:
    signatures = [action_signature(action) for action in action_list]
    probe = initialize_model(np, input_dim, hidden_size, output_size)
    model = probe
    changed = False
    try:
        members = validate_npz_archive(path)
        if not MODEL_ARCHIVE_V16_REQUIRED_MEMBERS.issubset(members) or not members.issubset(MODEL_ARCHIVE_ALLOWED_MEMBERS):
            raise ValueError("模型成员无效")
        with np.load(path, allow_pickle=False) as data:
            archive_schema = int(data["schema"][0])
            if archive_schema not in (15, 16, 17, 18, 19, MODEL_SCHEMA):
                raise ValueError("模型版本不兼容")
            required_members = (
                MODEL_ARCHIVE_REQUIRED_MEMBERS
                if archive_schema == MODEL_SCHEMA
                else MODEL_ARCHIVE_V19_REQUIRED_MEMBERS
                if archive_schema >= 19
                else MODEL_ARCHIVE_V18_REQUIRED_MEMBERS
                if archive_schema >= 17
                else MODEL_ARCHIVE_V16_REQUIRED_MEMBERS
            )
            if not required_members.issubset(members):
                raise ValueError("模型版本成员不完整")
            archive_hidden = int(data["hidden_size"][0])
            archive_output = int(data["output_size"][0])
            archive_input = int(data["input_dim"][0])
            archive_signatures = [str(value) for value in data["action_signatures"].tolist()]
            model["trained_samples"] = int(data["trained_samples"][0])
            model["training_rounds"] = int(data["training_rounds"][0])
            model["online_updates"] = int(data["online_updates"][0])
            model["visual_pretraining_steps"] = int(data["visual_pretraining_steps"][0]) if "visual_pretraining_steps" in data else 0
            model["world_training_steps"] = int(data["world_training_steps"][0]) if "world_training_steps" in data else 0
            model["reward_model_training_steps"] = int(data["reward_model_training_steps"][0]) if "reward_model_training_steps" in data else 0
            model["runtime_tier"] = str(data["runtime_tier"][0]) if "runtime_tier" in data else "low_numpy"
            model["validation_score"] = float(data["validation_score"][0]) if "validation_score" in data else 0.0
            model["critic_names"] = (
                [str(value) for value in data["critic_names"].tolist()]
                if "critic_names" in data
                else list(CRITIC_NAMES)
            )
            if model["critic_names"] != list(CRITIC_NAMES):
                raise ValueError("模型 critic 定义无效")

            q_keys = {
                "q_control_w", "q_control_b", "q_key_w", "q_key_b",
                "q_mouse_w", "q_mouse_b", "q_button_w", "q_button_b",
                "q_duration_w", "q_duration_b", "q_duration_kind_b",
            }
            world_keys = {
                "world_encoder_w", "world_encoder_b", "world_dynamics_w",
                "world_dynamics_action_w", "world_dynamics_duration_w", "world_dynamics_b",
                "world_reward_w", "world_reward_action_w", "world_reward_duration_w",
                "world_reward_b", "world_done_w", "world_done_b",
                "world_latent_to_hidden_w", "world_latent_to_hidden_b",
                "reward_model_w", "reward_model_b",
            }
            skip_keys = {
                "policy_action_w", "policy_action_b", "q_action_w", "q_action_b",
                "action_embedding", "frame_proj",
                "optimizer_offsets", "optimizer_m", "optimizer_v",
            }

            def copy_overlap(destination, source):
                if source.ndim != destination.ndim:
                    return destination
                slices = tuple(
                    slice(0, min(source.shape[axis], destination.shape[axis]))
                    for axis in range(source.ndim)
                )
                destination[slices] = source[slices].astype(destination.dtype, copy=False)
                return destination

            def migrate_q_source(source, destination):
                source = np.asarray(source, dtype=np.float32)
                migrated = destination.copy()
                if source.ndim == destination.ndim:
                    return copy_overlap(migrated, source)
                if source.ndim == destination.ndim - 1 and source.shape[0] == VALUE_HEAD_COUNT:
                    for twin in range(Q_TWIN_COUNT):
                        slices = tuple(
                            slice(0, min(source.shape[axis], migrated.shape[axis + 1]))
                            for axis in range(source.ndim)
                        )
                        target_slices = (twin,) + slices
                        migrated[target_slices] = source[slices]
                    if migrated.ndim >= 3:
                        migrated[1] = 0.995 * migrated[0] + 0.005 * destination[1]
                    return migrated
                if source.ndim == destination.ndim - 2:
                    legacy_average = source.mean(axis=0)
                    for twin in range(Q_TWIN_COUNT):
                        target = migrated[twin, TASK_CRITIC]
                        if legacy_average.ndim == target.ndim:
                            slices = tuple(
                                slice(0, min(legacy_average.shape[axis], target.shape[axis]))
                                for axis in range(target.ndim)
                            )
                            target[slices] = legacy_average[slices]
                    return migrated
                return migrated

            for key, destination in list(model.items()):
                if (
                    key in skip_keys
                    or not isinstance(destination, np.ndarray)
                    or key not in data
                    or key in {"conv_w"}
                ):
                    continue
                source = data[key]
                if key in q_keys:
                    model[key] = migrate_q_source(source, destination)
                elif key in world_keys:
                    source_value = np.asarray(source, dtype=np.float32)
                    if source_value.ndim == destination.ndim - 1:
                        migrated = destination.copy()
                        for member in range(WORLD_MODEL_MEMBERS):
                            slices = tuple(
                                slice(0, min(source_value.shape[axis], migrated.shape[axis + 1]))
                                for axis in range(source_value.ndim)
                            )
                            migrated[(member,) + slices] = source_value[slices]
                        if migrated.ndim >= 3:
                            for member in range(1, WORLD_MODEL_MEMBERS):
                                migrated[member] = (
                                    0.995 * migrated[0] + 0.005 * destination[member]
                                )
                        model[key] = migrated
                    else:
                        model[key] = copy_overlap(destination.copy(), source_value)
                else:
                    dtype = np.int16 if key == "action_factors" else np.float32
                    model[key] = copy_overlap(
                        destination.copy(),
                        np.asarray(source, dtype=dtype),
                    )
            if "conv_w" in data:
                model["conv_w"] = copy_overlap(
                    model["conv_w"].copy(),
                    data["conv_w"].astype(np.int8, copy=False),
                )

            # Preserve the old base visual projection and move the old context
            # rows behind the newly added full-frame/HUD/mouse branches.
            old_projection = data["frame_proj"].astype(np.float32, copy=False)
            new_projection = model["frame_proj"].copy()
            column_overlap = min(old_projection.shape[1], new_projection.shape[1])
            old_base_visual = min(base_visual_encoder_output_dim(), old_projection.shape[0])
            new_projection[:old_base_visual, :column_overlap] = old_projection[
                :old_base_visual, :column_overlap
            ]
            old_context_rows = max(0, old_projection.shape[0] - old_base_visual)
            if old_context_rows >= MODEL_GLOBAL_FEATURES:
                context_count = min(MODEL_GLOBAL_FEATURES, old_context_rows)
                new_projection[
                    visual_encoder_output_dim():visual_encoder_output_dim() + context_count,
                    :column_overlap,
                ] = old_projection[
                    old_base_visual:old_base_visual + context_count,
                    :column_overlap,
                ]
            elif old_context_rows > 0:
                context_count = min(ACTION_CONTEXT_SCALAR_FEATURES, old_context_rows)
                destination_start = (
                    visual_encoder_output_dim()
                    + ACTION_EMBEDDING_SIZE
                    + DURATION_EMBEDDING_SIZE
                )
                new_projection[
                    destination_start:destination_start + context_count,
                    :column_overlap,
                ] = old_projection[
                    old_base_visual:old_base_visual + context_count,
                    :column_overlap,
                ]
            model["frame_proj"] = new_projection

            # Map exact action heads by stable action signature while allowing
            # hidden-size and action-space changes.
            old_index = {
                signature: index for index, signature in enumerate(archive_signatures)
            }
            hidden_overlap = min(archive_hidden, int(model["hidden_size"]))
            policy_action_w = data["policy_action_w"].astype(np.float32, copy=False)
            policy_action_b = data["policy_action_b"].astype(np.float32, copy=False)
            q_action_source = migrate_q_source(
                data["q_action_w"],
                np.zeros(
                    (
                        Q_TWIN_COUNT,
                        VALUE_HEAD_COUNT,
                        archive_hidden,
                        archive_output * DURATION_HEAD_SIZE,
                    ),
                    dtype=np.float32,
                ),
            )
            q_action_b_source = migrate_q_source(
                data["q_action_b"],
                np.zeros(
                    (
                        Q_TWIN_COUNT,
                        VALUE_HEAD_COUNT,
                        archive_output * DURATION_HEAD_SIZE,
                    ),
                    dtype=np.float32,
                ),
            )
            action_embedding_source = (
                data["action_embedding"].astype(np.float32, copy=False)
                if "action_embedding" in data
                else None
            )
            for new_action, signature in enumerate(signatures):
                old_action = old_index.get(signature)
                if old_action is None:
                    continue
                if old_action < policy_action_b.shape[-1]:
                    model["policy_action_w"][:hidden_overlap, new_action] = policy_action_w[
                        :hidden_overlap, old_action
                    ]
                    model["policy_action_b"][new_action] = policy_action_b[old_action]
                if old_action < q_action_b_source.shape[-1]:
                    model["q_action_w"][:, :, :hidden_overlap, new_action] = q_action_source[
                        :, :, :hidden_overlap, old_action
                    ]
                    model["q_action_b"][:, :, new_action] = q_action_b_source[
                        :, :, old_action
                    ]
                if (
                    action_embedding_source is not None
                    and old_action < action_embedding_source.shape[0]
                ):
                    model["action_embedding"][new_action] = action_embedding_source[old_action]

            if "duration_embedding" in data:
                model["duration_embedding"] = copy_overlap(
                    model["duration_embedding"].copy(),
                    data["duration_embedding"].astype(np.float32, copy=False),
                )
            if archive_schema == 15:
                model["mouse_offset_w"].fill(0.0)
                model["mouse_offset_b"].fill(0.0)
            if archive_schema < 19:
                # Schema 18 and earlier did not condition the world model on
                # the selected hold duration. Zero initialization preserves
                # the legacy transition/reward predictions exactly.
                model["world_dynamics_duration_w"].fill(0.0)
                model["world_reward_duration_w"].fill(0.0)
            if archive_schema < MODEL_SCHEMA:
                # New closed-loop projection and per-game reward model retain
                # their fresh initialization when migrating older archives.
                changed = True

            model["q_twin_count"] = Q_TWIN_COUNT
            model["world_model_members"] = WORLD_MODEL_MEMBERS
            model["action_hash"] = actions_hash(action_list)
            model["action_signatures"] = list(signatures)
            model["output_size"] = int(output_size)
            model["input_dim"] = int(input_dim)
            model["temporal_frames"] = TEMPORAL_FRAMES

            # Optimizer moments are accepted only from the new schema. Layout
            # validation below resets them automatically after any resize.
            if archive_schema == MODEL_SCHEMA and all(
                key in data
                for key in (
                    "optimizer_step", "optimizer_schedule_step", "optimizer_keys",
                    "optimizer_offsets", "optimizer_m", "optimizer_v",
                )
            ):
                model["optimizer_step"] = int(data["optimizer_step"][0])
                model["optimizer_schedule_step"] = int(data["optimizer_schedule_step"][0])
                model["optimizer_keys"] = [str(value) for value in data["optimizer_keys"].tolist()]
                model["optimizer_offsets"] = data["optimizer_offsets"].astype(np.int64, copy=True)
                model["optimizer_m"] = data["optimizer_m"].astype(np.float32, copy=True)
                model["optimizer_v"] = data["optimizer_v"].astype(np.float32, copy=True)
            else:
                changed = True

            if (
                archive_schema != MODEL_SCHEMA
                or archive_hidden != int(model["hidden_size"])
                or archive_output != int(output_size)
                or archive_input != int(input_dim)
                or int(data["temporal_frames"][0]) != TEMPORAL_FRAMES
            ):
                changed = True
    except Exception:
        if path.exists():
            backup_corrupt(path)
        model = initialize_model(np, input_dim, hidden_size, output_size)
        changed = True

    expected_factors = action_factor_matrix(np, action_list)
    if model["action_factors"].shape != expected_factors.shape or not np.array_equal(
        model["action_factors"], expected_factors
    ):
        model["action_factors"] = expected_factors
        changed = True
    expected_keys = action_key_multihot_matrix(np, action_list)
    if model["action_key_multihot"].shape != expected_keys.shape or not np.array_equal(
        model["action_key_multihot"], expected_keys
    ):
        model["action_key_multihot"] = expected_keys
        changed = True
    expected_buttons = action_button_multihot_matrix(np, action_list)
    if model["action_button_multihot"].shape != expected_buttons.shape or not np.array_equal(
        model["action_button_multihot"], expected_buttons
    ):
        model["action_button_multihot"] = expected_buttons
        changed = True
    current_hash = actions_hash(action_list)
    if model.get("action_hash") != current_hash or model.get("action_signatures") != signatures:
        model["action_hash"] = current_hash
        model["action_signatures"] = signatures
        changed = True
    model["output_size"] = int(output_size)
    model["schema"] = MODEL_SCHEMA
    previous_optimizer_step = int(model.get("optimizer_step", 0))
    _ensure_optimizer_state(np, model)
    if previous_optimizer_step > 0 and int(model.get("optimizer_step", 0)) == 0:
        changed = True
    previous_w = model["conv_w"].copy()
    previous_scale = float(model["conv_scale"][0])
    _synchronize_quantized_conv_weights(np, model)
    if (
        not np.array_equal(previous_w, model["conv_w"])
        or abs(previous_scale - float(model["conv_scale"][0])) > 1e-8
    ):
        changed = True
    return model, changed


def load_global_prior(np) -> dict | None:
    try:
        members=validate_npz_archive(GLOBAL_PRIOR_PATH)
        if not GLOBAL_ARCHIVE_REQUIRED_MEMBERS.issubset(members) or not members.issubset(GLOBAL_ARCHIVE_ALLOWED_MEMBERS): return None
        with np.load(GLOBAL_PRIOR_PATH,allow_pickle=False) as data:
            if int(data["schema"][0])!=GLOBAL_PRIOR_SCHEMA: return None
            result={key:data[key].astype(np.float32,copy=True) for key in ("policy_control_b","policy_key_b","policy_mouse_b","policy_button_b","policy_duration_b","q_control_b","q_key_b","q_mouse_b","q_button_b","q_duration_b")}
            result.update({"trained_samples":int(data["trained_samples"][0]),"training_rounds":int(data["training_rounds"][0]),"source_profile":str(data["source_profile"][0])})
            return result
    except Exception:
        return None


def apply_global_prior(np, model: dict, action_list: list[dict]) -> bool:
    prior=load_global_prior(np)
    if prior is None: return False
    for key in ("policy_control_b","policy_key_b","policy_mouse_b","policy_button_b","policy_duration_b"):
        if prior[key].shape==model[key].shape: model[key]=0.72*model[key]+0.28*prior[key]
    for key in ("q_control_b","q_key_b","q_mouse_b","q_button_b","q_duration_b"):
        if prior[key].shape==model[key].shape: model[key]=0.72*model[key]+0.28*prior[key]
    return True



def apply_global_action_heads(np, model: dict, action_list: list[dict], action_origins: list[str], prior: dict | None) -> bool:
    return apply_global_prior(np,model,action_list)




def verify_model_archive(np, path: Path, model: dict, signatures: list[str]) -> None:
    members = validate_npz_archive(path)
    if not MODEL_ARCHIVE_REQUIRED_MEMBERS.issubset(members) or not members.issubset(MODEL_ARCHIVE_ALLOWED_MEMBERS):
        raise RuntimeError("模型归档成员无效")
    with np.load(path, allow_pickle=False) as data:
        if int(data["schema"][0]) != MODEL_SCHEMA or int(data["output_size"][0]) != int(model["output_size"]):
            raise RuntimeError("模型归档元数据无效")
        if [str(v) for v in data["action_signatures"].tolist()] != signatures:
            raise RuntimeError("模型动作签名无效")
        if [str(v) for v in data["critic_names"].tolist()] != list(CRITIC_NAMES):
            raise RuntimeError("模型 critic 定义无效")
        if int(data["q_twin_count"][0]) != Q_TWIN_COUNT:
            raise RuntimeError("Twin Q 元数据无效")
        if int(data["world_model_members"][0]) != WORLD_MODEL_MEMBERS:
            raise RuntimeError("世界模型集成元数据无效")
        if [str(v) for v in data["optimizer_keys"].tolist()] != list(model.get("optimizer_keys", [])):
            raise RuntimeError("优化器参数布局无效")
        required_arrays = (
            "conv_w", "conv_master_w", "conv2_depthwise_w", "conv2_pointwise_w",
            "conv3_depthwise_w", "conv3_pointwise_w", "frame_proj", "frame_bias",
            "action_embedding", "duration_embedding",
            "Wz", "Uz", "Wr", "Ur", "Wh", "Uh", "policy_control_w",
            "policy_button_w", "policy_action_w", "policy_action_b",
            "q_control_w", "q_button_w", "q_action_w", "q_action_b", "value_w",
            "value_b", "progress_w", "progress_b", "safety_w", "safety_b",
            "world_encoder_w", "world_encoder_b", "world_dynamics_w",
            "world_dynamics_action_w", "world_dynamics_duration_w", "world_dynamics_b",
            "world_reward_w", "world_reward_action_w", "world_reward_duration_w",
            "world_reward_b", "world_done_w", "world_done_b",
            "world_latent_to_hidden_w", "world_latent_to_hidden_b",
            "reward_model_w", "reward_model_b",
            "policy_skill_w", "policy_skill_b",
            "skill_value_w", "skill_value_b", "policy_duration_kind_b", "q_duration_kind_b",
            "mouse_offset_w", "mouse_offset_b", "action_factors", "action_key_multihot",
            "action_button_multihot",
        )
        for key in required_arrays:
            if data[key].shape != model[key].shape or not np.isfinite(data[key]).all():
                raise RuntimeError(f"模型归档数组无效:{key}")
        for key in ("optimizer_offsets", "optimizer_m", "optimizer_v"):
            if data[key].shape != np.asarray(model[key]).shape or not np.isfinite(data[key]).all():
                raise RuntimeError(f"模型优化器数组无效:{key}")
        if int(data["optimizer_step"][0]) != int(model.get("optimizer_step", 0)):
            raise RuntimeError("模型优化器步数无效")
        if int(data["optimizer_schedule_step"][0]) != int(model.get("optimizer_schedule_step", 0)):
            raise RuntimeError("模型学习率计划步数无效")



def verify_global_prior_archive(np, path: Path, model: dict, signatures: list[str]) -> None:
    members=validate_npz_archive(path)
    if not GLOBAL_ARCHIVE_REQUIRED_MEMBERS.issubset(members) or not members.issubset(GLOBAL_ARCHIVE_ALLOWED_MEMBERS): raise RuntimeError("通用先验临时文件成员集合无效")
    with np.load(path,allow_pickle=False) as data:
        if int(data["schema"][0])!=GLOBAL_PRIOR_SCHEMA: raise RuntimeError("通用先验临时文件版本无效")
        for key in ("policy_control_b","policy_key_b","policy_mouse_b","policy_button_b","policy_duration_b","q_control_b","q_key_b","q_mouse_b","q_button_b","q_duration_b"):
            if key not in data or not np.isfinite(data[key]).all(): raise RuntimeError("通用先验临时文件参数无效")



def save_global_prior(np, model: dict, action_list: list[dict], source_profile: str) -> None:
    temp=temporary_sibling_path(GLOBAL_PRIOR_PATH); temp.unlink(missing_ok=True)
    values={"schema":np.asarray([GLOBAL_PRIOR_SCHEMA],dtype=np.int32),"trained_samples":np.asarray([model.get("trained_samples",0)],dtype=np.int64),"training_rounds":np.asarray([model.get("training_rounds",0)],dtype=np.int64),"source_profile":np.asarray([source_profile],dtype=np.str_),"updated_at":np.asarray([now_text()],dtype=np.str_)}
    for key in ("policy_control_b","policy_key_b","policy_mouse_b","policy_button_b","policy_duration_b","q_control_b","q_key_b","q_mouse_b","q_button_b","q_duration_b"): values[key]=model[key].astype(np.float32)
    try:
        with temp.open("wb") as file: np.savez_compressed(file,**values)
        os.replace(temp,GLOBAL_PRIOR_PATH)
    finally: temp.unlink(missing_ok=True)



def model_from_global_prior(np, prior: dict | None, action_list: list[dict], hidden_size: int) -> dict:
    model=initialize_model(np,MODEL_INPUT_DIM,hidden_size,len(action_list)); model["action_factors"]=action_factor_matrix(np,action_list); model["action_key_multihot"]=action_key_multihot_matrix(np,action_list); model["action_button_multihot"]=action_button_multihot_matrix(np,action_list); model["action_hash"]=actions_hash(action_list); model["action_signatures"]=[action_signature(a) for a in action_list]
    if prior is not None:
        for key in ("policy_control_b","policy_key_b","policy_mouse_b","policy_button_b","policy_duration_b","q_control_b","q_key_b","q_mouse_b","q_button_b","q_duration_b"):
            if key in prior and prior[key].shape==model[key].shape: model[key]=prior[key].copy()
        model["trained_samples"]=int(prior.get("trained_samples",0)); model["training_rounds"]=int(prior.get("training_rounds",0))
    return model



def refresh_global_prior(np, index: dict, config: dict, stop_event: threading.Event | None) -> bool:
    accum={}; weight_total=0.0; used=0
    for profile_id in sorted(index.get("profiles",{})):
        if stop_event is not None and stop_event.is_set(): raise RuntimeError("操作已取消")
        try:
            paths=profile_paths(profile_id); raw=read_json_file(paths["profile"],MAX_PROFILE_JSON_BYTES); profile=migrate_profile(raw,profile_id)
            if profile is None or not paths["model"].is_file(): continue
            model,_=load_model(np,paths["model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
            weight=max(1.0,math.sqrt(max(1,int(model.get("trained_samples",0)))))
            for key in ("policy_control_b","policy_key_b","policy_mouse_b","policy_button_b","policy_duration_b","q_control_b","q_key_b","q_mouse_b","q_button_b","q_duration_b"):
                accum[key]=accum.get(key,0.0)+model[key]*weight
            weight_total+=weight;used+=1
        except Exception:
            continue
    if used==0 or weight_total<=0: return False
    seed=initialize_model(np,MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,1)
    for key,value in accum.items(): seed[key]=(value/weight_total).astype(np.float32)
    seed["trained_samples"]=sum(int(index.get("profiles",{}).get(pid,{}).get("trained_samples",0)) for pid in index.get("profiles",{})); seed["training_rounds"]=used
    save_global_prior(np,seed,[],f"aggregate:{used}"); return True



def distill_teacher_model(
    np,
    teacher: dict,
    hidden_size: int,
    action_list: list[dict],
    records: list[dict] | None,
    runtime_tier: str,
    stop_event: threading.Event | None = None,
) -> dict:
    student = initialize_model(np, MODEL_INPUT_DIM, hidden_size, len(action_list))

    def copy_overlap(destination, source):
        if not isinstance(source, np.ndarray) or source.ndim != destination.ndim:
            return destination
        slices = tuple(slice(0, min(source.shape[i], destination.shape[i])) for i in range(source.ndim))
        destination[slices] = source[slices].astype(destination.dtype, copy=False)
        return destination

    for key, destination in list(student.items()):
        source = teacher.get(key)
        if isinstance(destination, np.ndarray) and isinstance(source, np.ndarray):
            student[key] = copy_overlap(destination.copy(), source)
    student["action_factors"] = action_factor_matrix(np, action_list)
    student["action_key_multihot"] = action_key_multihot_matrix(np, action_list)
    student["action_button_multihot"] = action_button_multihot_matrix(np, action_list)
    student["action_hash"] = actions_hash(action_list)
    student["action_signatures"] = [action_signature(action) for action in action_list]
    for key in (
        "trained_samples", "training_rounds", "online_updates", "visual_pretraining_steps",
        "world_training_steps", "reward_model_training_steps", "validation_score",
    ):
        student[key] = teacher.get(key, student.get(key, 0))
    student["runtime_tier"] = str(runtime_tier)

    calibration_records = list(records or [])[:512]
    if calibration_records and int(hidden_size) != int(teacher["hidden_size"]):
        learning_rate = 0.0008
        for epoch in range(2):
            for record in calibration_records:
                raise_if_cancelled(stop_event)
                teacher_hidden = _latest_temporal_hidden(np, teacher, record["state"])
                student_hidden = _latest_temporal_hidden(np, student, record["state"])
                teacher_probabilities, teacher_q, _ = factorized_action_outputs_from_hidden(
                    np, teacher, teacher_hidden
                )
                student_probabilities, student_q, _ = factorized_action_outputs_from_hidden(
                    np, student, student_hidden
                )
                policy_gradient = np.clip(
                    student_probabilities - teacher_probabilities, -0.20, 0.20
                ).astype(np.float32)
                student["policy_action_w"] -= learning_rate * np.outer(
                    student_hidden, policy_gradient
                ).astype(np.float32)
                student["policy_action_b"] -= learning_rate * policy_gradient
                action_id = max(0, min(len(action_list) - 1, int(record.get("action", 0))))
                q_gradient = np.clip(
                    student_q[:, action_id] - teacher_q[:, action_id], -1.0, 1.0
                ).astype(np.float32)
                student["q_action_w"][:, :, :, action_id] -= learning_rate * (
                    q_gradient[None, :, None] * student_hidden[None, None, :]
                )
                student["q_action_b"][:, :, action_id] -= learning_rate * q_gradient[None, :]
                teacher_value = float(teacher_hidden @ teacher["value_w"][:, 0] + teacher["value_b"][0])
                student_value = float(student_hidden @ student["value_w"][:, 0] + student["value_b"][0])
                value_error = max(-1.0, min(1.0, student_value - teacher_value))
                student["value_w"][:, 0] -= learning_rate * value_error * student_hidden
                student["value_b"][0] -= learning_rate * value_error
                for weight_key, bias_key, teacher_value_head, student_value_head in (
                    ("progress_w", "progress_b", predict_progress(np, teacher, teacher_hidden), predict_progress(np, student, student_hidden)),
                    ("safety_w", "safety_b", predict_safety_probability(np, teacher, teacher_hidden), predict_safety_probability(np, student, student_hidden)),
                ):
                    error = max(-1.0, min(1.0, student_value_head - teacher_value_head))
                    student[weight_key][:, 0] -= learning_rate * error * student_hidden
                    student[bias_key][0] -= learning_rate * error
    _synchronize_quantized_conv_weights(np, student)
    _reset_optimizer_state(np, student)
    return student


def save_runtime_students(
    np,
    paths: dict[str, Path],
    teacher: dict,
    teacher_target: dict,
    action_list: list[dict],
    records: list[dict],
    stop_event: threading.Event | None,
) -> None:
    specifications = (
        ("low", 256, "low_numpy"),
        ("mid", 512, "mid_onnx"),
        ("high", 768, "high_directml"),
    )
    for name, hidden_size, runtime_tier in specifications:
        student = distill_teacher_model(
            np, teacher, hidden_size, action_list, records, runtime_tier, stop_event
        )
        student_target = distill_teacher_model(
            np, teacher_target, hidden_size, action_list, records, runtime_tier, stop_event
        )
        save_model(np, paths[f"student_{name}"], student)
        save_model(np, paths[f"student_{name}_target"], student_target)


def save_model(np, path: Path, model: dict) -> None:
    signatures = [str(value) for value in model.get("action_signatures", [])]
    if len(signatures) != int(model.get("output_size", 0)) or len(set(signatures)) != len(signatures):
        raise RuntimeError("模型动作映射无效")
    _synchronize_quantized_conv_weights(np, model)
    _ensure_optimizer_state(np, model)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = temporary_sibling_path(path)
    temp.unlink(missing_ok=True)
    try:
        values = {
            "schema": np.asarray([MODEL_SCHEMA], dtype=np.int32),
            "input_dim": np.asarray([model["input_dim"]], dtype=np.int32),
            "hidden_size": np.asarray([model["hidden_size"]], dtype=np.int32),
            "output_size": np.asarray([model["output_size"]], dtype=np.int32),
            "temporal_frames": np.asarray([TEMPORAL_FRAMES], dtype=np.int32),
            "trained_samples": np.asarray([model.get("trained_samples", 0)], dtype=np.int64),
            "training_rounds": np.asarray([model.get("training_rounds", 0)], dtype=np.int64),
            "online_updates": np.asarray([model.get("online_updates", 0)], dtype=np.int64),
            "visual_pretraining_steps": np.asarray([model.get("visual_pretraining_steps", 0)], dtype=np.int64),
            "world_training_steps": np.asarray([model.get("world_training_steps", 0)], dtype=np.int64),
            "reward_model_training_steps": np.asarray([model.get("reward_model_training_steps", 0)], dtype=np.int64),
            "action_hash": np.asarray([model.get("action_hash", "")], dtype=np.str_),
            "action_signatures": np.asarray(signatures, dtype=np.str_),
            "critic_names": np.asarray(CRITIC_NAMES, dtype=np.str_),
            "q_twin_count": np.asarray([Q_TWIN_COUNT], dtype=np.int32),
            "world_model_members": np.asarray([WORLD_MODEL_MEMBERS], dtype=np.int32),
            "optimizer_step": np.asarray([model.get("optimizer_step", 0)], dtype=np.int64),
            "optimizer_schedule_step": np.asarray([model.get("optimizer_schedule_step", 0)], dtype=np.int64),
            "optimizer_keys": np.asarray(model.get("optimizer_keys", []), dtype=np.str_),
            "optimizer_offsets": np.asarray(model.get("optimizer_offsets", []), dtype=np.int64),
            "optimizer_m": np.asarray(model.get("optimizer_m", []), dtype=np.float32),
            "optimizer_v": np.asarray(model.get("optimizer_v", []), dtype=np.float32),
            "runtime_tier": np.asarray([model.get("runtime_tier", "low_numpy")], dtype=np.str_),
            "validation_score": np.asarray([model.get("validation_score", 0.0)], dtype=np.float32),
            "updated_at": np.asarray([now_text()], dtype=np.str_),
        }
        for key in (
            "conv_w", "conv_scale", "conv_b", "conv_master_w",
            "conv2_depthwise_w", "conv2_pointwise_w", "conv2_b",
            "conv3_depthwise_w", "conv3_pointwise_w", "conv3_b",
            "frame_proj", "frame_bias",
            "action_embedding", "duration_embedding",
            "Wz", "Uz", "bz", "Wr", "Ur", "br", "Wh", "Uh", "bh",
            "policy_control_w", "policy_control_b", "policy_key_w", "policy_key_b",
            "policy_mouse_w", "policy_mouse_b", "policy_button_w", "policy_button_b",
            "policy_duration_w", "policy_duration_b", "policy_duration_kind_b",
            "policy_action_w", "policy_action_b",
            "q_control_w", "q_control_b", "q_key_w", "q_key_b", "q_mouse_w", "q_mouse_b",
            "q_button_w", "q_button_b", "q_duration_w", "q_duration_b", "q_duration_kind_b",
            "q_action_w", "q_action_b", "value_w", "value_b", "progress_w", "progress_b",
            "safety_w", "safety_b",
            "world_encoder_w", "world_encoder_b", "world_dynamics_w",
            "world_dynamics_action_w", "world_dynamics_duration_w", "world_dynamics_b",
            "world_reward_w", "world_reward_action_w", "world_reward_duration_w",
            "world_reward_b", "world_done_w", "world_done_b",
            "world_latent_to_hidden_w", "world_latent_to_hidden_b",
            "reward_model_w", "reward_model_b",
            "policy_skill_w", "policy_skill_b", "skill_value_w", "skill_value_b",
            "mouse_offset_w", "mouse_offset_b", "action_factors",
            "action_key_multihot", "action_button_multihot",
        ):
            values[key] = model[key]
        with temp.open("wb") as file:
            np.savez_compressed(file, **values)
        verify_model_archive(np, temp, model, signatures)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)





def _model_hidden_state_from_vector(
    np,
    model: dict,
    vector: dict,
    return_cache: bool = False,
    initial_hidden=None,
):
    if initial_hidden is None:
        hidden = np.zeros(int(model["hidden_size"]), dtype=np.float32)
    else:
        hidden = np.asarray(initial_hidden, dtype=np.float32).reshape(-1).copy()
        if hidden.shape != (int(model["hidden_size"]),) or not np.isfinite(hidden).all():
            raise ValueError("循环隐藏状态尺寸无效")
    caches = []
    actions = vector["actions"]
    durations = vector["durations"]
    training = bool(return_cache)
    for index, frame in enumerate(vector["frames"]):
        if return_cache:
            visual, conv_cache = _quantized_conv_features(np, model, frame, return_cache=True, training=training)
        else:
            visual = _quantized_conv_features(np, model, frame)
            conv_cache = None
        action_value = int(actions[index])
        duration_value = float(durations[index])
        action_embedding = np.zeros(ACTION_EMBEDDING_SIZE, dtype=np.float32)
        kind_values = [0.0] * len(CONTROL_KINDS)
        has_action = 0.0
        key_density = 0.0
        button_density = 0.0
        mouse_value = 0.0
        if 0 <= action_value < len(model["action_factors"]):
            has_action = 1.0
            action_embedding = model["action_embedding"][action_value]
            factors = model["action_factors"][action_value]
            kind_index = int(factors[0])
            if 0 <= kind_index < len(kind_values):
                kind_values[kind_index] = 1.0
            mouse_bucket = int(factors[1])
            mouse_value = mouse_bucket / max(1, MOUSE_HEAD_SIZE - 1)
            key_density = min(
                1.0,
                float(np.count_nonzero(model["action_key_multihot"][action_value])) / 6.0,
            )
            button_density = min(
                1.0,
                float(np.count_nonzero(model["action_button_multihot"][action_value])) / 3.0,
            )
        duration_index = duration_bin(duration_value)
        duration_embedding = model["duration_embedding"][duration_index]
        context = np.concatenate(
            (
                action_embedding,
                duration_embedding,
                np.asarray(
                    [
                        has_action,
                        *kind_values,
                        key_density,
                        button_density,
                        mouse_value,
                        max(0.0, min(1.0, duration_value / 0.5)),
                    ],
                    dtype=np.float32,
                ),
            )
        )
        if len(context) != MODEL_GLOBAL_FEATURES:
            raise RuntimeError("结构化动作上下文尺寸无效")
        combined = np.concatenate((visual, context))
        projected_pre = combined @ model["frame_proj"] + model["frame_bias"]
        projected = np.tanh(projected_pre)
        previous_hidden = hidden
        update = _sigmoid(np, projected @ model["Wz"] + previous_hidden @ model["Uz"] + model["bz"])
        reset = _sigmoid(np, projected @ model["Wr"] + previous_hidden @ model["Ur"] + model["br"])
        candidate = np.tanh(projected @ model["Wh"] + (reset * previous_hidden) @ model["Uh"] + model["bh"])
        gru_hidden = (1.0 - update) * previous_hidden + update * candidate
        memory_width = max(8, min(int(model["hidden_size"]) // 4, int(model["hidden_size"]) // 2))
        source_slice = slice(0, memory_width)
        memory_slice = slice(int(model["hidden_size"]) - memory_width, int(model["hidden_size"]))
        thirds = np.array_split(np.arange(memory_width), 3)
        memory_decays = np.empty(memory_width, dtype=np.float32)
        for segment, decay in zip(thirds, (0.90, 0.97, 0.995)):
            memory_decays[segment] = decay
        slow_memory = (
            memory_decays * previous_hidden[memory_slice]
            + (1.0 - memory_decays) * gru_hidden[source_slice]
        )
        hidden = gru_hidden.copy()
        hidden[memory_slice] = 0.65 * gru_hidden[memory_slice] + 0.35 * slow_memory
        if return_cache:
            caches.append({
                "combined": combined,
                "projected": projected,
                "previous_hidden": previous_hidden,
                "update": update,
                "reset": reset,
                "candidate": candidate,
                "conv_cache": conv_cache,
                "action_value": action_value,
                "duration_index": duration_index,
                "memory_width": memory_width,
                "memory_decays": memory_decays,
            })
    hidden = hidden.astype(np.float32, copy=False)
    if return_cache:
        return hidden, caches
    return hidden




def _accumulate_gradient(gradients: dict[str, object], key: str, value) -> None:
    if key in gradients:
        gradients[key] += value.astype(gradients[key].dtype, copy=False)


def _backprop_convolution(np, model: dict, conv_cache: dict | None, visual_gradient, gradients: dict[str, object]) -> None:
    if conv_cache is None or "conv_master_w" not in gradients:
        return

    def pooled_gradient(flat_gradient, shape, bounds, rows, columns):
        channels, height, width = shape
        result = np.zeros(shape, dtype=np.float32)
        values = np.asarray(flat_gradient, dtype=np.float32).reshape(rows * columns, channels)
        for tile_index, (top, bottom, left, right) in enumerate(bounds):
            area = max(1, (bottom - top) * (right - left))
            result[:, top:bottom, left:right] += values[tile_index, :, None, None] / area
        return result

    def backprop_block(cache, output_gradient, depthwise_key, pointwise_key, bias_key):
        d_pre = np.asarray(output_gradient, dtype=np.float32) * (cache["projected_pre"] > 0.0)
        depthwise = cache["depthwise"]
        pointwise = cache["pointwise_w"]
        windows = cache["windows"]
        _accumulate_gradient(gradients, bias_key, d_pre.sum(axis=(1, 2)))
        _accumulate_gradient(gradients, pointwise_key, np.einsum("oij,cij->oc", d_pre, depthwise, optimize=True))
        d_depthwise = np.einsum("oc,oij->cij", pointwise, d_pre, optimize=True)
        _accumulate_gradient(gradients, depthwise_key, np.einsum("cij,cijmn->cmn", d_depthwise, windows, optimize=True))
        d_source = np.zeros(cache["source_shape"], dtype=np.float32)
        out_h, out_w = d_depthwise.shape[1:]
        weights = cache["depthwise_w"]
        for ky in range(3):
            for kx in range(3):
                d_source[:, ky:ky + out_h * 2:2, kx:kx + out_w * 2:2] += d_depthwise * weights[:, ky, kx][:, None, None]
        return d_source

    pyramid = conv_cache["pyramid"]
    final_size = CNN_OUTPUT_CHANNELS * CNN_POOL_ROWS * CNN_POOL_COLUMNS
    middle_size = CNN_MID_CHANNELS * CNN_MID_POOL_ROWS * CNN_MID_POOL_COLUMNS
    gradient = np.asarray(visual_gradient, dtype=np.float32)[:base_visual_encoder_output_dim()]
    final_gradient = pooled_gradient(
        gradient[:final_size], pyramid["final_shape"], pyramid["final_bounds"], CNN_POOL_ROWS, CNN_POOL_COLUMNS
    )
    middle_gradient = pooled_gradient(
        gradient[final_size:final_size + middle_size], pyramid["middle_shape"], pyramid["middle_bounds"],
        CNN_MID_POOL_ROWS, CNN_MID_POOL_COLUMNS
    )
    stem_gradient = np.zeros(pyramid["stem_shape"], dtype=np.float32)
    hud_gradient = gradient[final_size + middle_size:].reshape(4, CNN_CHANNELS)
    top_rows, bottom_rows, side_columns = pyramid["hud_geometry"]
    stem_gradient[:, :top_rows, :] += hud_gradient[0, :, None, None] / max(1, top_rows * pyramid["stem_shape"][2])
    stem_gradient[:, -bottom_rows:, :] += hud_gradient[1, :, None, None] / max(1, bottom_rows * pyramid["stem_shape"][2])
    stem_gradient[:, :, :side_columns] += hud_gradient[2, :, None, None] / max(1, side_columns * pyramid["stem_shape"][1])
    stem_gradient[:, :, -side_columns:] += hud_gradient[3, :, None, None] / max(1, side_columns * pyramid["stem_shape"][1])

    middle_gradient += backprop_block(
        pyramid["final_cache"], final_gradient,
        "conv3_depthwise_w", "conv3_pointwise_w", "conv3_b"
    )
    stem_gradient += backprop_block(
        pyramid["middle_cache"], middle_gradient,
        "conv2_depthwise_w", "conv2_pointwise_w", "conv2_b"
    )
    stem = conv_cache.get("stem")
    if stem is None:
        return
    raw_gradient = stem_gradient * (stem["raw"] > 0.0)
    _accumulate_gradient(
        gradients, "conv_master_w",
        np.einsum("oij,cijmn->ocmn", raw_gradient, stem["windows"], optimize=True)
    )
    _accumulate_gradient(gradients, "conv_b", raw_gradient.sum(axis=(1, 2)))



def _backprop_temporal_encoder(
    np,
    model: dict,
    caches: list[dict],
    hidden_gradient,
    learning_rate: float,
    gradients: dict[str, object] | None = None,
    return_initial_gradient: bool = False,
) -> dict[str, object]:
    local = gradients is None
    if local:
        gradients = {
            key: np.zeros_like(model[key], dtype=np.float32)
            for key in (
                *_CONV_PARAMETER_KEYS, "frame_proj", "frame_bias",
                "action_embedding", "duration_embedding",
                "Wz", "Uz", "bz", "Wr", "Ur", "br", "Wh", "Uh", "bh",
            )
        }
    dh = np.asarray(hidden_gradient, dtype=np.float32)
    visual_dim = visual_encoder_output_dim()
    for cache in reversed(caches):
        combined = cache["combined"]
        projected = cache["projected"]
        previous_hidden = cache["previous_hidden"]
        update = cache["update"]
        reset = cache["reset"]
        candidate = cache["candidate"]

        memory_width = int(cache.get("memory_width", 0))
        direct_previous = np.zeros_like(dh, dtype=np.float32)
        if memory_width > 0:
            memory_slice = slice(len(dh) - memory_width, len(dh))
            source_slice = slice(0, memory_width)
            decays = np.asarray(cache.get("memory_decays"), dtype=np.float32)
            output_gradient = dh
            gru_gradient = output_gradient.copy()
            tail_gradient = output_gradient[memory_slice].copy()
            gru_gradient[memory_slice] = 0.65 * tail_gradient
            gru_gradient[source_slice] += 0.35 * (1.0 - decays) * tail_gradient
            direct_previous[memory_slice] += 0.35 * decays * tail_gradient
            dh = gru_gradient

        d_previous = dh * (1.0 - update) + direct_previous
        d_update = dh * (candidate - previous_hidden)
        d_candidate = dh * update

        candidate_pre_gradient = d_candidate * (1.0 - candidate * candidate)
        _accumulate_gradient(gradients, "Wh", np.outer(projected, candidate_pre_gradient))
        _accumulate_gradient(gradients, "Uh", np.outer(reset * previous_hidden, candidate_pre_gradient))
        _accumulate_gradient(gradients, "bh", candidate_pre_gradient)
        d_projected = candidate_pre_gradient @ model["Wh"].T
        d_reset_previous = candidate_pre_gradient @ model["Uh"].T
        d_reset = d_reset_previous * previous_hidden
        d_previous += d_reset_previous * reset

        reset_pre_gradient = d_reset * reset * (1.0 - reset)
        _accumulate_gradient(gradients, "Wr", np.outer(projected, reset_pre_gradient))
        _accumulate_gradient(gradients, "Ur", np.outer(previous_hidden, reset_pre_gradient))
        _accumulate_gradient(gradients, "br", reset_pre_gradient)
        d_projected += reset_pre_gradient @ model["Wr"].T
        d_previous += reset_pre_gradient @ model["Ur"].T

        update_pre_gradient = d_update * update * (1.0 - update)
        _accumulate_gradient(gradients, "Wz", np.outer(projected, update_pre_gradient))
        _accumulate_gradient(gradients, "Uz", np.outer(previous_hidden, update_pre_gradient))
        _accumulate_gradient(gradients, "bz", update_pre_gradient)
        d_projected += update_pre_gradient @ model["Wz"].T
        d_previous += update_pre_gradient @ model["Uz"].T

        projected_pre_gradient = d_projected * (1.0 - projected * projected)
        _accumulate_gradient(gradients, "frame_proj", np.outer(combined, projected_pre_gradient))
        _accumulate_gradient(gradients, "frame_bias", projected_pre_gradient)
        combined_gradient = projected_pre_gradient @ model["frame_proj"].T
        _backprop_convolution(np, model, cache.get("conv_cache"), combined_gradient[:visual_dim], gradients)
        context_gradient = combined_gradient[visual_dim:]
        action_value = int(cache.get("action_value", -1))
        if "action_embedding" in gradients and 0 <= action_value < len(model["action_embedding"]):
            gradients["action_embedding"][action_value] += context_gradient[:ACTION_EMBEDDING_SIZE]
        duration_index = int(cache.get("duration_index", 0))
        if "duration_embedding" in gradients and 0 <= duration_index < DURATION_HEAD_SIZE:
            start = ACTION_EMBEDDING_SIZE
            gradients["duration_embedding"][duration_index] += context_gradient[
                start:start + DURATION_EMBEDDING_SIZE
            ]
        dh = d_previous
    if local:
        trainable = [gradient for gradient in gradients.values()]
        clip_gradients_by_global_norm(np, trainable, 8.0)
        step = max(0.0, min(0.02, float(learning_rate)))
        for key, gradient in gradients.items():
            model[key] -= step * gradient
        _synchronize_quantized_conv_weights(np, model)
    if return_initial_gradient:
        return gradients, dh.astype(np.float32, copy=False)
    return gradients


def _model_hidden_state(np, model: dict, feature: bytes):
    frames, actions, durations = decode_temporal_state(feature)
    return recurrent_model_step(
        np,
        model,
        frames[-1],
        np.zeros(int(model["hidden_size"]), dtype=np.float32),
        actions[-1],
        durations[-1],
    )


def recurrent_model_step(
    np,
    model: dict,
    feature: bytes,
    previous_hidden,
    previous_action: int = -1,
    previous_duration: float = 0.0,
    return_cache: bool = False,
):
    frame = normalize_feature_bytes(feature)
    vector = {
        "frames": [_frame_channels(np, frame)],
        "actions": np.asarray([int(previous_action)], dtype=np.int32),
        "durations": np.asarray([float(previous_duration)], dtype=np.float32),
    }
    return _model_hidden_state_from_vector(
        np,
        model,
        vector,
        return_cache=return_cache,
        initial_hidden=previous_hidden,
    )


def pretrain_visual_encoder(
    np,
    model: dict,
    records: list[dict],
    learning_rate: float,
    stop_event: threading.Event | None = None,
    maximum_steps: int = 64,
) -> dict[str, float]:
    """Temporal contrastive pretraining for the shared visual encoder."""
    parts = [part for part in _continuous_trajectory_parts(records) if len(part) >= 3]
    examples = []
    for part_index, part in enumerate(parts):
        for position in range(len(part) - 1):
            negative = None
            if len(parts) > 1:
                other = parts[(part_index + 1 + position) % len(parts)]
                negative = other[position % len(other)]
            elif len(part) >= 10:
                negative = part[(position + max(8, len(part) // 2)) % len(part)]
            if negative is not None:
                examples.append((part[position], part[position + 1], negative))
    if not examples:
        return {"steps": 0.0, "loss": 0.0}
    rng = np.random.default_rng(VISUAL_INITIALIZATION_SEED + int(model.get("visual_pretraining_steps", 0)))
    rng.shuffle(examples)
    limit = max(1, min(int(maximum_steps), len(examples)))
    step_size = max(1e-6, min(0.002, float(learning_rate) * 0.20))
    loss_total = 0.0
    trained = 0
    batch_gradients = {key: np.zeros_like(model[key], dtype=np.float32) for key in _CONV_PARAMETER_KEYS}
    batch_count = 0

    def encoded(record: dict):
        frames, _, _ = decode_temporal_state(record["state"])
        channels = _frame_channels(np, frames[-1])
        return _quantized_conv_features(np, model, channels, return_cache=True, training=True)

    def apply_batch() -> None:
        nonlocal batch_count
        if batch_count <= 0:
            return
        for gradient in batch_gradients.values():
            gradient /= batch_count
        clip_gradients_by_global_norm(np, list(batch_gradients.values()), 4.0)
        for key, gradient in batch_gradients.items():
            model[key] -= step_size * gradient
            gradient.fill(0.0)
        _synchronize_quantized_conv_weights(np, model)
        batch_count = 0

    for anchor_record, positive_record, negative_record in examples[:limit]:
        raise_if_cancelled(stop_event)
        anchor, anchor_cache = encoded(anchor_record)
        positive, positive_cache = encoded(positive_record)
        negative, negative_cache = encoded(negative_record)
        anchor_code = np.tanh(anchor)
        positive_code = np.tanh(positive)
        negative_code = np.tanh(negative)
        dimension = max(1, len(anchor_code))
        positive_delta = anchor_code - positive_code
        negative_delta = anchor_code - negative_code
        positive_loss = float(np.mean(positive_delta * positive_delta))
        negative_distance = float(np.mean(negative_delta * negative_delta))
        margin = 0.08
        hinge_active = negative_distance < margin
        loss_total += positive_loss + max(0.0, margin - negative_distance)
        anchor_gradient = 2.0 * positive_delta / dimension
        positive_gradient = -2.0 * positive_delta / dimension
        negative_gradient = np.zeros_like(negative_delta)
        if hinge_active:
            anchor_gradient -= 2.0 * negative_delta / dimension
            negative_gradient += 2.0 * negative_delta / dimension
        anchor_gradient *= 1.0 - anchor_code * anchor_code
        positive_gradient *= 1.0 - positive_code * positive_code
        negative_gradient *= 1.0 - negative_code * negative_code
        _backprop_convolution(np, model, anchor_cache, anchor_gradient, batch_gradients)
        _backprop_convolution(np, model, positive_cache, positive_gradient, batch_gradients)
        _backprop_convolution(np, model, negative_cache, negative_gradient, batch_gradients)
        batch_count += 1
        trained += 1
        if batch_count >= 4:
            apply_batch()
    apply_batch()
    model["visual_pretraining_steps"] = int(model.get("visual_pretraining_steps", 0)) + trained
    return {"steps": float(trained), "loss": float(loss_total / max(1, trained))}



def _model_head_outputs(np, model: dict, hidden):
    policy = (
        hidden @ model["policy_control_w"] + model["policy_control_b"],
        hidden @ model["policy_key_w"] + model["policy_key_b"],
        hidden @ model["policy_mouse_w"] + model["policy_mouse_b"],
        hidden @ model["policy_button_w"] + model["policy_button_b"],
        hidden @ model["policy_duration_w"] + model["policy_duration_b"],
    )
    q_twins = (
        np.einsum("h,tvhc->tvc", hidden, model["q_control_w"]) + model["q_control_b"],
        np.einsum("h,tvhk->tvk", hidden, model["q_key_w"]) + model["q_key_b"],
        np.einsum("h,tvhm->tvm", hidden, model["q_mouse_w"]) + model["q_mouse_b"],
        np.einsum("h,tvhb->tvb", hidden, model["q_button_w"]) + model["q_button_b"],
        np.einsum("h,tvhd->tvd", hidden, model["q_duration_w"]) + model["q_duration_b"],
    )
    q = tuple(np.minimum(values[0], values[1]) for values in q_twins)
    return policy, q


def critic_weight_vector(np, weights: dict | tuple[float, float, float] | None = None):
    if isinstance(weights, dict):
        values = (
            float(weights.get("task_reward_weight", 1.0)),
            float(weights.get("exploration_reward_weight", 0.18)),
            -float(weights.get("safety_penalty_weight", 0.70)),
        )
    elif weights is not None:
        values = tuple(float(value) for value in weights)
    else:
        values = (1.0, 0.18, -0.70)
    if len(values) != VALUE_HEAD_COUNT or not all(math.isfinite(value) for value in values):
        raise ValueError("critic 组合权重无效")
    return np.asarray(values, dtype=np.float32)


def combined_critic_values(np, q_values, weights: dict | tuple[float, float, float] | None = None):
    critics = np.asarray(q_values, dtype=np.float32)
    if critics.shape[0] != VALUE_HEAD_COUNT:
        raise ValueError("critic 输出尺寸无效")
    return np.tensordot(critic_weight_vector(np, weights), critics, axes=(0, 0)).astype(np.float32)


def critic_bootstrap_values(
    np,
    model: dict,
    hidden,
    weights=None,
    target_model: dict | None = None,
    target_hidden=None,
):
    probabilities, online_critics, _ = factorized_action_outputs_from_hidden(np, model, hidden)
    combined = combined_critic_values(np, online_critics, weights)
    action = int(np.argmax(combined + 0.05 * np.log(np.maximum(probabilities, 1e-9))))
    evaluator = target_model if target_model is not None else model
    evaluator_hidden = hidden if target_hidden is None else target_hidden
    _, target_critics, _ = factorized_action_outputs_from_hidden(np, evaluator, evaluator_hidden)
    return target_critics[:, action].astype(np.float32, copy=False)


def predict_safety_probability(np, model: dict, hidden) -> float:
    logit = np.asarray(hidden, dtype=np.float32) @ model["safety_w"] + model["safety_b"]
    return float(_sigmoid(np, logit)[0])


def world_model_latent(np, model: dict, hidden):
    hidden_value = np.asarray(hidden, dtype=np.float32).reshape(-1)
    return np.tanh(
        np.einsum("h,mhl->ml", hidden_value, model["world_encoder_w"])
        + model["world_encoder_b"]
    ).astype(np.float32)



def latent_world_model_step(
    np,
    model: dict,
    latent,
    action_id: int,
    duration_index: int = DURATION_HEAD_SIZE // 2,
):
    action = max(0, min(len(model["action_embedding"]) - 1, int(action_id)))
    duration = max(0, min(DURATION_HEAD_SIZE - 1, int(duration_index)))
    action_embedding = model["action_embedding"][action]
    duration_embedding = model["duration_embedding"][duration]
    latent_value = np.asarray(latent, dtype=np.float32).reshape(WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE)
    next_latents = np.tanh(
        np.einsum("ml,mlk->mk", latent_value, model["world_dynamics_w"])
        + np.einsum("a,mak->mk", action_embedding, model["world_dynamics_action_w"])
        + np.einsum("d,mdk->mk", duration_embedding, model["world_dynamics_duration_w"])
        + model["world_dynamics_b"]
    ).astype(np.float32)
    member_rewards = (
        np.einsum("ml,mlv->mv", next_latents, model["world_reward_w"])
        + np.einsum("a,mav->mv", action_embedding, model["world_reward_action_w"])
        + np.einsum("d,mdv->mv", duration_embedding, model["world_reward_duration_w"])
        + model["world_reward_b"]
    ).astype(np.float32)
    member_rewards[:, TASK_CRITIC] = np.clip(member_rewards[:, TASK_CRITIC], -1.0, 1.0)
    member_rewards[:, EXPLORATION_CRITIC] = np.clip(member_rewards[:, EXPLORATION_CRITIC], 0.0, 1.0)
    member_rewards[:, SAFETY_CRITIC] = np.clip(member_rewards[:, SAFETY_CRITIC], 0.0, 2.0)
    done_probabilities = _sigmoid(
        np,
        np.einsum("ml,mlq->mq", next_latents, model["world_done_w"])
        + model["world_done_b"],
    )[:, 0]
    return (
        next_latents,
        member_rewards.mean(axis=0).astype(np.float32),
        float(done_probabilities.mean()),
    )


def latent_world_model_duration_values(
    np,
    model: dict,
    hidden,
    action_id: int,
    critic_weights: dict | tuple[float, float, float] | None = None,
):
    result = np.zeros(DURATION_HEAD_SIZE, dtype=np.float64)
    world_steps = max(0, int(model.get("world_training_steps", 0)))
    minimum_steps = max(WORLD_MODEL_MIN_TRAINING_STEPS, len(model["action_factors"]) * 8)
    if world_steps < minimum_steps or not 0 <= int(action_id) < len(model["action_embedding"]):
        return result
    action = int(action_id)
    latent = world_model_latent(np, model, hidden)
    action_embedding = model["action_embedding"][action]
    duration_embeddings = model["duration_embedding"]
    next_latents = np.tanh(
        np.einsum("ml,mlk->mk", latent, model["world_dynamics_w"])[None, :, :]
        + np.einsum("a,mak->mk", action_embedding, model["world_dynamics_action_w"])[None, :, :]
        + np.einsum("da,mak->dmk", duration_embeddings, model["world_dynamics_duration_w"])
        + model["world_dynamics_b"][None, :, :]
    ).astype(np.float32)
    member_rewards = (
        np.einsum("dml,mlv->dmv", next_latents, model["world_reward_w"], optimize=True)
        + np.einsum("a,mav->mv", action_embedding, model["world_reward_action_w"])[None, :, :]
        + np.einsum("da,mav->dmv", duration_embeddings, model["world_reward_duration_w"], optimize=True)
        + model["world_reward_b"][None, :, :]
    )
    member_rewards[:, :, TASK_CRITIC] = np.clip(member_rewards[:, :, TASK_CRITIC], -1.0, 1.0)
    member_rewards[:, :, EXPLORATION_CRITIC] = np.clip(member_rewards[:, :, EXPLORATION_CRITIC], 0.0, 1.0)
    member_rewards[:, :, SAFETY_CRITIC] = np.clip(member_rewards[:, :, SAFETY_CRITIC], 0.0, 2.0)
    weights = critic_weight_vector(np, critic_weights)
    member_combined = np.einsum("dmv,v->dm", member_rewards, weights, optimize=True)
    uncertainty_weight = (
        max(0.0, min(2.0, float(critic_weights.get("world_uncertainty_penalty", 0.18))))
        if isinstance(critic_weights, dict)
        else 0.18
    )
    done_probabilities = _sigmoid(
        np,
        np.einsum("dml,mlq->dmq", next_latents, model["world_done_w"], optimize=True)
        + model["world_done_b"][None, :, :],
    )[:, :, 0].mean(axis=1)
    conservative = member_combined.mean(axis=1) - uncertainty_weight * member_combined.std(axis=1)
    full_steps = max(minimum_steps + 1, WORLD_MODEL_FULL_CONFIDENCE_STEPS, minimum_steps * 4)
    confidence = max(0.0, min(1.0, (world_steps - minimum_steps) / (full_steps - minimum_steps)))
    result = conservative * np.maximum(0.0, 1.0 - done_probabilities) * confidence
    return np.clip(result, -4.0, 4.0)




def latent_world_model_plan_values(
    np,
    model: dict,
    hidden,
    probabilities,
    base_values,
    horizon: int,
    discount: float,
    critic_weights: dict | tuple[float, float, float] | None = None,
    allowed_actions: list[int] | None = None,
):
    action_count = len(model["action_factors"])
    result = np.zeros(action_count, dtype=np.float64)
    world_steps = max(0, int(model.get("world_training_steps", 0)))
    minimum_steps = max(WORLD_MODEL_MIN_TRAINING_STEPS, action_count * 8)
    if world_steps < minimum_steps or horizon <= 0:
        return result
    full_confidence_steps = max(minimum_steps + 1, WORLD_MODEL_FULL_CONFIDENCE_STEPS, minimum_steps * 4)
    planning_confidence = max(
        0.0,
        min(1.0, (world_steps - minimum_steps) / (full_confidence_steps - minimum_steps)),
    )
    root_probabilities = np.asarray(probabilities, dtype=np.float64)
    root_values = np.asarray(base_values, dtype=np.float64)
    if (
        root_probabilities.shape != (action_count,)
        or root_values.shape != (action_count,)
        or not np.isfinite(root_probabilities).all()
        or not np.isfinite(root_values).all()
    ):
        return result
    allowed = [
        int(action)
        for action in (allowed_actions if allowed_actions is not None else range(action_count))
        if 0 <= int(action) < action_count
    ]
    if not allowed:
        return result
    gamma = max(0.1, min(0.98, float(discount)))
    horizon_value = max(1, min(12, int(horizon)))
    weights = critic_weight_vector(np, critic_weights)
    uncertainty_weight = (
        max(0.0, min(2.0, float(critic_weights.get("world_uncertainty_penalty", 0.18))))
        if isinstance(critic_weights, dict)
        else 0.18
    )

    def projected_hidden(latents):
        member_hidden = np.tanh(
            np.einsum(
                "ml,mlh->mh",
                np.asarray(latents, dtype=np.float32),
                model["world_latent_to_hidden_w"],
                optimize=True,
            )
            + model["world_latent_to_hidden_b"]
        )
        return member_hidden.mean(axis=0).astype(np.float32, copy=False)

    def candidate_actions(state_hidden, state_probabilities=None, state_values=None, limit=WORLD_MODEL_BRANCH_FACTOR):
        if state_probabilities is None or state_values is None:
            state_probabilities, state_q, _ = factorized_action_outputs_from_hidden(
                np, model, state_hidden
            )
            state_values = combined_critic_values(np, state_q, critic_weights)
        state_probabilities = np.asarray(state_probabilities, dtype=np.float64)
        state_values = np.asarray(state_values, dtype=np.float64)
        allowed_values = state_values[np.asarray(allowed, dtype=np.int64)]
        center = float(np.median(allowed_values))
        scale = max(0.25, float(np.std(allowed_values)))
        ranked = sorted(
            allowed,
            key=lambda action: (
                math.log(max(1e-9, float(state_probabilities[action])))
                + 0.65 * math.tanh((float(state_values[action]) - center) / scale)
            ),
            reverse=True,
        )
        return ranked[:min(len(ranked), max(1, int(limit)))]

    initial_latents = world_model_latent(np, model, hidden)
    root_candidates = candidate_actions(
        np.asarray(hidden, dtype=np.float32),
        root_probabilities,
        root_values,
        max(WORLD_MODEL_BEAM_WIDTH, WORLD_MODEL_BRANCH_FACTOR * 2),
    )
    beams = [(0.0, 1.0, -1, initial_latents)]
    best_by_initial = {action: -math.inf for action in root_candidates}
    completed_depth = 0
    for depth in range(horizon_value):
        expanded = []
        for beam_score, beam_survival, first_action, beam_latents in beams:
            state_hidden = np.asarray(hidden, dtype=np.float32) if depth == 0 else projected_hidden(beam_latents)
            actions = root_candidates if depth == 0 else candidate_actions(state_hidden)
            for action in actions:
                kind = int(model["action_factors"][action, 0])
                duration_probabilities, duration_q = conditional_duration_outputs(
                    np, model, state_hidden, kind
                )
                duration_scores = (
                    np.log(np.maximum(duration_probabilities, 1e-9))
                    + 0.25 * combined_critic_values(np, duration_q, critic_weights)
                    + 0.30 * latent_world_model_duration_values(
                        np, model, state_hidden, action, critic_weights
                    )
                )
                durations = [int(value) for value in np.argsort(duration_scores)[::-1][:2]]
                for duration in durations:
                    action_embedding = model["action_embedding"][action]
                    duration_embedding = model["duration_embedding"][duration]
                    next_latents = np.tanh(
                        np.einsum("ml,mlk->mk", beam_latents, model["world_dynamics_w"], optimize=True)
                        + np.einsum("a,mak->mk", action_embedding, model["world_dynamics_action_w"], optimize=True)
                        + np.einsum("d,mdk->mk", duration_embedding, model["world_dynamics_duration_w"], optimize=True)
                        + model["world_dynamics_b"]
                    ).astype(np.float32)
                    member_rewards = (
                        np.einsum("ml,mlv->mv", next_latents, model["world_reward_w"], optimize=True)
                        + np.einsum("a,mav->mv", action_embedding, model["world_reward_action_w"], optimize=True)
                        + np.einsum("d,mdv->mv", duration_embedding, model["world_reward_duration_w"], optimize=True)
                        + model["world_reward_b"]
                    )
                    member_rewards[:, TASK_CRITIC] = np.clip(member_rewards[:, TASK_CRITIC], -1.0, 1.0)
                    member_rewards[:, EXPLORATION_CRITIC] = np.clip(member_rewards[:, EXPLORATION_CRITIC], 0.0, 1.0)
                    member_rewards[:, SAFETY_CRITIC] = np.clip(member_rewards[:, SAFETY_CRITIC], 0.0, 2.0)
                    member_combined = member_rewards @ weights
                    conservative_reward = float(member_combined.mean() - uncertainty_weight * member_combined.std())
                    done_probability = float(
                        _sigmoid(
                            np,
                            np.einsum("ml,mlq->mq", next_latents, model["world_done_w"], optimize=True)
                            + model["world_done_b"],
                        )[:, 0].mean()
                    )
                    new_initial = action if first_action < 0 else first_action
                    new_score = beam_score + (gamma ** depth) * beam_survival * conservative_reward
                    new_survival = beam_survival * max(0.0, 1.0 - done_probability)
                    best_by_initial[new_initial] = max(best_by_initial.get(new_initial, -math.inf), new_score)
                    expanded.append((new_score, new_survival, new_initial, next_latents))
        if not expanded:
            break
        expanded.sort(key=lambda item: item[0], reverse=True)
        beams = expanded[:WORLD_MODEL_BEAM_WIDTH]
        completed_depth = depth + 1
        if max(item[1] for item in beams) < 0.02:
            break

    # Bootstrap the leaf values in the hidden space expected by the policy/value heads.
    for beam_score, beam_survival, first_action, beam_latents in beams:
        if first_action < 0:
            continue
        leaf_hidden = projected_hidden(beam_latents)
        terminal_value = float(leaf_hidden @ model["value_w"][:, 0] + model["value_b"][0])
        terminal_score = beam_score + (gamma ** max(1, completed_depth)) * beam_survival * terminal_value
        best_by_initial[first_action] = max(best_by_initial.get(first_action, -math.inf), terminal_score)
    for action, value in best_by_initial.items():
        if math.isfinite(value):
            result[action] = value
    return np.clip(result * planning_confidence, -4.0, 4.0)



def model_outputs(np, model: dict, feature: bytes):
    probabilities, q_values, _ = factorized_action_outputs(np, model, feature)
    return probabilities, np.clip(combined_critic_values(np, q_values), -4.0, 4.0)



def model_ensemble_outputs(np, model: dict, target_model: dict, feature: bytes, target_weight: float, critic_weights=None):
    online_prob, online_q, _ = factorized_action_outputs(np, model, feature)
    target_prob, target_q, _ = factorized_action_outputs(np, target_model, feature)
    weight = max(0.0, min(0.5, float(target_weight)))
    probabilities = online_prob * (1.0 - weight) + target_prob * weight
    probabilities /= max(1e-12, float(probabilities.sum()))
    online_values = combined_critic_values(np, online_q, critic_weights)
    target_values = combined_critic_values(np, target_q, critic_weights)
    values = online_values * (1.0 - weight) + target_values * weight
    disagreement = np.abs(online_values - target_values)
    uncertainty = disagreement * (0.5 + weight)
    return probabilities.astype(np.float32), np.clip(values, -4.0, 4.0), np.clip(uncertainty, 0.0, 4.0), np.clip(disagreement, 0.0, 4.0)


def recurrent_ensemble_outputs(
    np,
    model: dict,
    target_model: dict,
    online_hidden,
    target_hidden,
    target_weight: float,
    critic_weights=None,
):
    online_probability, online_q, _ = factorized_action_outputs_from_hidden(
        np,
        model,
        online_hidden,
    )
    target_probability, target_q, _ = factorized_action_outputs_from_hidden(
        np,
        target_model,
        target_hidden,
    )
    weight = max(0.0, min(0.5, float(target_weight)))
    probabilities = online_probability * (1.0 - weight) + target_probability * weight
    probabilities /= max(1e-12, float(probabilities.sum()))
    online_values = combined_critic_values(np, online_q, critic_weights)
    target_values = combined_critic_values(np, target_q, critic_weights)
    values = online_values * (1.0 - weight) + target_values * weight
    disagreement = np.abs(online_values - target_values)
    uncertainty = disagreement * (0.5 + weight)
    return (
        probabilities.astype(np.float32),
        np.clip(values, -4.0, 4.0),
        np.clip(uncertainty, 0.0, 4.0),
        np.clip(disagreement, 0.0, 4.0),
    )



def clone_target_model(np, model: dict) -> dict:
    clone = {}
    for key, value in model.items():
        clone[key] = value.copy() if isinstance(value, np.ndarray) else (list(value) if isinstance(value, list) else value)
    return clone



def soft_update_target_model(np, target: dict, source: dict, rate: float) -> None:
    tau = max(0.0, min(1.0, float(rate)))
    for key, source_value in source.items():
        if key.startswith("optimizer_"):
            continue
        target_value = target.get(key)
        if isinstance(source_value, np.ndarray) and isinstance(target_value, np.ndarray) and source_value.shape == target_value.shape:
            if np.issubdtype(source_value.dtype, np.floating):
                target_value *= 1.0 - tau; target_value += source_value * tau
            else:
                target[key] = source_value.copy()
        elif key in (
            "trained_samples", "training_rounds", "online_updates", "visual_pretraining_steps",
            "world_training_steps", "reward_model_training_steps", "action_hash", "action_signatures", "critic_names",
            "q_twin_count", "world_model_members", "runtime_tier", "validation_score",
        ):
            target[key] = list(source_value) if isinstance(source_value, list) else source_value



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



def temporal_difference_target(np, model: dict, reward: float, next_feature: bytes | None = None, discount: float = 0.0, terminal: bool = False, target_model: dict | None = None) -> float:
    immediate = max(-1.0, min(1.0, float(reward)))
    if terminal or next_feature is None:
        return immediate
    gamma = max(0.0, min(0.99, float(discount)))
    evaluator = target_model if target_model is not None else model
    next_hidden = _model_hidden_state(np, evaluator, next_feature)
    next_value = float(next_hidden @ evaluator["value_w"][:, 0] + evaluator["value_b"][0])
    return max(-3.0, min(3.0, immediate + gamma * next_value))


def _latest_temporal_hidden(np, model: dict, state: bytes, return_cache: bool = False):
    frames, actions, durations = decode_temporal_state(state)
    return recurrent_model_step(
        np,
        model,
        frames[-1],
        np.zeros(int(model["hidden_size"]), dtype=np.float32),
        actions[-1],
        durations[-1],
        return_cache=return_cache,
    )


def temporal_critic_targets(
    np,
    model: dict,
    rewards,
    next_feature: bytes | None = None,
    discount: float = 0.0,
    terminal: bool = False,
    target_model: dict | None = None,
    critic_weights=None,
):
    immediate = np.asarray(rewards, dtype=np.float32).reshape(-1)
    if immediate.size == 1:
        scalar = float(immediate[0])
        immediate = np.asarray((scalar, max(0.0, scalar), max(0.0, -scalar)), dtype=np.float32)
    if immediate.shape != (VALUE_HEAD_COUNT,) or not np.isfinite(immediate).all():
        raise ValueError("在线 critic 回报无效")
    immediate[TASK_CRITIC] = np.clip(immediate[TASK_CRITIC], -3.0, 3.0)
    immediate[EXPLORATION_CRITIC] = np.clip(immediate[EXPLORATION_CRITIC], 0.0, 3.0)
    immediate[SAFETY_CRITIC] = np.clip(immediate[SAFETY_CRITIC], 0.0, 4.0)
    if terminal or next_feature is None:
        return immediate
    evaluator = target_model if target_model is not None else model
    online_hidden = _latest_temporal_hidden(np, model, next_feature)
    target_hidden = _latest_temporal_hidden(np, evaluator, next_feature)
    result = immediate + max(0.0, min(0.99, float(discount))) * critic_bootstrap_values(
        np,
        model,
        online_hidden,
        critic_weights,
        evaluator,
        target_hidden,
    )
    result[TASK_CRITIC] = np.clip(result[TASK_CRITIC], -3.0, 3.0)
    result[EXPLORATION_CRITIC] = np.clip(result[EXPLORATION_CRITIC], 0.0, 3.0)
    result[SAFETY_CRITIC] = np.clip(result[SAFETY_CRITIC], 0.0, 4.0)
    return result.astype(np.float32)





def reconcile_online_world_plans(
    np,
    online_plan,
    world_plan,
    online_confidence: float,
    world_confidence: float,
    disagreement_penalty: float,
):
    """Combine separately-produced plans and lower scores where they disagree."""
    online = np.asarray(online_plan, dtype=np.float64)
    world = np.asarray(world_plan, dtype=np.float64)
    if online.shape != world.shape:
        raise ValueError("联合规划尺寸无效")
    online_scale = max(0.0, min(1.0, float(online_confidence)))
    world_scale = max(0.0, min(1.0, float(world_confidence)))
    total_scale = online_scale + world_scale
    if total_scale <= 1e-9:
        return np.zeros_like(online), np.zeros_like(online)
    combined = (online_scale * online + world_scale * world) / total_scale
    disagreement = np.abs(online - world)
    penalty = max(0.0, min(2.0, float(disagreement_penalty)))
    confidence_overlap = min(online_scale, world_scale)
    combined -= penalty * confidence_overlap * disagreement
    return np.clip(combined, -4.0, 4.0), disagreement



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
    critic_rewards=None,
    critic_weights=None,
    world_rewards=None,
    world_next_feature: bytes | None = None,
    world_terminal: bool | None = None,
    duration_index: int | None = None,
) -> bool:
    if not 0 <= int(action_index) < len(model["action_factors"]):
        return False
    lr = max(0.0, min(0.02, float(learning_rate)))
    if lr <= 0.0:
        return False
    hidden, caches = _latest_temporal_hidden(np, model, feature, return_cache=True)
    probabilities, q_values, _ = factorized_action_outputs_from_hidden(np, model, hidden)
    value = float(hidden @ model["value_w"][:, 0] + model["value_b"][0])
    reward_components = critic_rewards if critic_rewards is not None else (reward, max(0.0, reward), max(0.0, -reward))
    targets = temporal_critic_targets(
        np, model, reward_components, next_feature, discount, terminal, target_model, critic_weights
    )
    executed_duration = DURATION_HEAD_SIZE // 2
    if duration_index is not None:
        executed_duration = max(0, min(DURATION_HEAD_SIZE - 1, int(duration_index)))
    else:
        try:
            duration_state = world_next_feature or next_feature or feature
            _, _, duration_values = decode_temporal_state(duration_state)
            executed_duration = duration_bin(float(duration_values[-1]))
        except Exception:
            pass
    q_data = float(combined_critic_values(np, q_values[:, int(action_index), None], critic_weights)[0])
    gradients = _training_gradient_buffer(np, model)
    _, value_hidden_gradient = _train_value_head(
        np, model, hidden, q_data, value, 0.70, 1.0, gradients
    )
    _, q_hidden_gradient = _train_factor_q(
        np, model, hidden, int(action_index), targets, lr, 1.0,
        gradients=gradients, q_values=q_values, cql_weight=0.005,
        duration_index=executed_duration,
    )
    _, safety_hidden_gradient = _train_safety_head(
        np, model, hidden, max(0.0, min(1.0, float(targets[SAFETY_CRITIC]) / 4.0)), 1.0, gradients
    )
    world_done = bool(terminal) if world_terminal is None else bool(world_terminal)
    world_next = next_feature if world_next_feature is None else world_next_feature
    next_hidden = (
        _latest_temporal_hidden(np, model, world_next)
        if world_next is not None and not world_done
        else None
    )
    target_next_hidden = (
        _latest_temporal_hidden(np, target_model, world_next)
        if target_model is not None and world_next is not None and not world_done
        else None
    )
    _, world_hidden_gradient = train_world_model_transition(
        np,
        model,
        hidden,
        next_hidden,
        int(action_index),
        world_rewards if world_rewards is not None else reward_components,
        world_done,
        1.0,
        gradients,
        target_model=target_model,
        target_next_hidden=target_next_hidden,
        duration_index=executed_duration,
    )
    advantage = q_data - value
    policy_hidden_gradient = np.zeros_like(hidden)
    if advantage > -0.25:
        actor_weight = min(12.0, math.exp(min(3.0, advantage / 2.5)))
        _, policy_hidden_gradient = _train_factor_policy(
            np, model, hidden, model["action_factors"][int(action_index)], lr,
            0.15 * actor_weight, action_id=int(action_index), gradients=gradients,
            probabilities=probabilities, duration_index=executed_duration,
        )
    hidden_gradient = (
        value_hidden_gradient
        + q_hidden_gradient
        + policy_hidden_gradient
        + safety_hidden_gradient
        + world_hidden_gradient
    )
    _backprop_temporal_encoder(np, model, caches, hidden_gradient, lr * 0.25, gradients)
    visual_update = (
        int(model.get("trained_samples", 0)) >= 256
        and int(model.get("online_updates", 0)) % 32 == 0
        and float(targets[SAFETY_CRITIC]) < 0.75
    )
    if not visual_update:
        for key in _CONV_PARAMETER_KEYS:
            gradients[key].fill(0.0)
    clip_gradients_by_global_norm(np, list(gradients.values()), 3.5)
    _adam_apply(np, model, gradients, lr)
    _synchronize_quantized_conv_weights(np, model)
    model["online_updates"] = int(model.get("online_updates", 0)) + 1
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
    exploration: float,
    allowed_actions: list[int] | None = None,
    uncertainty=None,
    planning_values=None,
    uncertainty_weight: float = 0.22,
    planning_weight: float = 0.55,
) -> int:
    probabilities = np.asarray(probabilities, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    candidates = np.arange(len(probabilities), dtype=np.int64) if allowed_actions is None else np.asarray(allowed_actions, dtype=np.int64)
    candidates = candidates[(candidates >= 0) & (candidates < len(probabilities))]
    if len(candidates) == 0: return 0
    if random.random() < max(0.0, min(0.8, float(exploration))):
        # Exploratory actions should gather information, not merely resample
        # the current policy.  Blend policy support, uniform coverage, model
        # disagreement, and positive planning evidence.
        policy_weights = np.maximum(probabilities[candidates], 0.0)
        policy_total = float(policy_weights.sum())
        if policy_total > 1e-12:
            policy_weights /= policy_total
        else:
            policy_weights.fill(1.0 / len(candidates))
        weights = 0.55 * policy_weights + 0.20 / len(candidates)
        if uncertainty is not None:
            information = np.asarray(uncertainty, dtype=np.float64)[candidates]
            information = np.nan_to_num(information, nan=0.0, posinf=0.0, neginf=0.0)
            information = np.maximum(information, 0.0)
            information_total = float(information.sum())
            if information_total > 1e-12:
                weights += 0.20 * information / information_total
        if planning_values is not None:
            planned = np.asarray(planning_values, dtype=np.float64)[candidates]
            planned = np.nan_to_num(planned, nan=0.0, posinf=0.0, neginf=0.0)
            planned = np.maximum(planned - float(planned.min(initial=0.0)), 0.0)
            planned_total = float(planned.sum())
            if planned_total > 1e-12:
                weights += 0.05 * planned / planned_total
        weights = np.maximum(weights, 1e-12)
        weights /= float(weights.sum())
        return int(np.random.choice(candidates, p=weights))
    scores = np.log(np.maximum(probabilities[candidates], 1e-9)) + 0.85 * values[candidates]
    if planning_values is not None:
        scores += max(0.0, min(1.0, float(planning_weight))) * np.asarray(
            planning_values,
            dtype=np.float64,
        )[candidates]
    if uncertainty is not None:
        scores -= max(0.0, min(0.5, float(uncertainty_weight))) * np.asarray(
            uncertainty,
            dtype=np.float64,
        )[candidates]
    return int(candidates[int(np.argmax(scores))])



def reservoir_add(bucket: list, value, seen_count: int, capacity: int) -> None:
    if len(bucket) < capacity:
        bucket.append(value)
        return
    position = random.randrange(seen_count)
    if position < capacity:
        bucket[position] = value



def human_training_signal(reward: float) -> tuple[float, float, float]:
    quality = max(0.0, min(1.0, (float(reward) + 1.0) * 0.5))
    policy_multiplier = 0.55 + 0.45 * quality
    value_target = max(-1.0, min(1.0, float(reward)))
    value_weight = 0.65 + 0.35 * quality
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


def _continuous_trajectory_parts(records: list[dict]) -> list[list[dict]]:
    episodes: dict[tuple[str, str], list[dict]] = {}
    for record in records:
        episode_id = str(record["episode_id"])
        sequence_id = str(record.get("_sequence_id", episode_id))
        episodes.setdefault((episode_id, sequence_id), []).append(record)
    parts: list[list[dict]] = []
    for episode in episodes.values():
        episode.sort(key=lambda item: int(item["step"]))
        part: list[dict] = []
        for record in episode:
            if part and int(record["step"]) != int(part[-1]["step"]) + 1:
                parts.append(part)
                part = []
            part.append(record)
        if part:
            parts.append(part)
    return parts



def _success_rate_bucket(value: float) -> str:
    score = max(0.0, min(1.0, float(value)))
    if score >= 0.72:
        return "high"
    if score >= 0.42:
        return "medium"
    return "low"


def _novelty_bucket(value: float) -> str:
    score = max(0.0, min(1.0, float(value)))
    if score >= 0.68:
        return "high"
    if score >= 0.34:
        return "medium"
    return "low"


def _classify_failure_type(
    done: bool,
    task_total: float,
    safety_total: float,
    reward_mean: float,
    exploration_mean: float,
) -> str:
    if bool(done) and safety_total > max(0.35, abs(task_total) * 0.65):
        return "terminal_safety"
    if bool(done) and (task_total < -0.10 or reward_mean < -0.03):
        return "terminal_regression"
    if safety_total > max(0.50, abs(task_total)):
        return "unsafe"
    if reward_mean < -0.08 or task_total < -0.20:
        return "negative_reward"
    if exploration_mean < 0.012 and abs(task_total) < 0.08:
        return "stagnation"
    return "none"


def _bounded_episode_success_rate(
    task_total: float,
    exploration_total: float,
    safety_total: float,
    reward_mean: float,
    done: bool,
    failure_type: str,
    step_count: int,
) -> float:
    scale = max(1.0, math.sqrt(max(1, int(step_count))))
    score = (
        0.50
        + 0.32 * math.tanh(float(task_total) / scale * 2.0)
        + 0.10 * math.tanh(float(exploration_total) / scale)
        + 0.12 * math.tanh(float(reward_mean) * 3.0)
        - 0.38 * math.tanh(float(safety_total) / scale)
    )
    if bool(done) and failure_type == "none" and task_total > 0.0:
        score += 0.12
    elif failure_type != "none":
        score -= 0.12
    return max(0.0, min(1.0, score))


def _episode_novelty_score(records: list[dict]) -> float:
    if not records:
        return 0.0
    sample_limit = min(64, len(records))
    stride = max(1, len(records) // sample_limit)
    hashes: set[str] = set()
    sampled = 0
    for record in records[::stride][:sample_limit]:
        try:
            hashes.add(_temporal_frame_hash(record["state"]))
            sampled += 1
        except Exception:
            continue
    uniqueness = len(hashes) / max(1, sampled)
    exploration = sum(max(0.0, min(1.0, float(item.get("exploration_reward", 0.0)))) for item in records) / len(records)
    priority = sum(max(0.05, float(item.get("priority", 0.05))) for item in records) / len(records)
    return max(
        0.0,
        min(
            1.0,
            0.62 * uniqueness
            + 0.26 * min(1.0, exploration * 2.5)
            + 0.12 * min(1.0, math.log1p(priority) / math.log(6.0)),
        ),
    )


def _sampling_stratum(record: dict) -> str:
    source = "human" if record.get("source") == "human" else "ai"
    return "|".join(
        (
            source,
            _success_rate_bucket(float(record.get("episode_success_rate", 0.50))),
            str(record.get("failure_type", "none")),
            _novelty_bucket(float(record.get("novelty_score", 0.0))),
        )
    )


def _select_episode_ids_stratified(candidates: list[dict], row_limit: int, rng) -> list[str]:
    if not candidates:
        return []
    buckets: dict[str, deque] = {}
    for candidate in candidates:
        buckets.setdefault(str(candidate["stratum"]), deque()).append(candidate)
    for key, values in list(buckets.items()):
        ordered = sorted(
            values,
            key=lambda item: (
                float(item.get("priority", 0.0)),
                float(item.get("novelty", 0.0)),
                int(item.get("last_row", 0)),
            ),
            reverse=True,
        )
        buckets[key] = deque(ordered)
    strata = list(buckets)
    rng.shuffle(strata)
    selected: list[str] = []
    total = 0
    maximum = max(32, int(row_limit))
    while strata:
        progressed = False
        next_strata: list[str] = []
        for key in strata:
            values = buckets[key]
            if not values:
                continue
            candidate = values.popleft()
            selected.append(str(candidate["episode_id"]))
            total += max(1, int(candidate.get("count", 1)))
            progressed = True
            if values:
                next_strata.append(key)
            if total >= maximum and len(selected) >= min(4, len(candidates)):
                return selected
        if not progressed:
            break
        strata = next_strata
    return selected


def contiguous_trajectory_records(
    records: list[dict],
    limit: int,
    sequence_length: int,
    burn_in_steps: int,
    n_step_horizon: int,
    rng,
) -> list[dict]:
    maximum = max(1, int(limit))
    chunk_length = max(32, int(sequence_length) + int(burn_in_steps) + int(n_step_horizon))
    chunks: list[list[dict]] = []
    for part in _continuous_trajectory_parts(records):
        if len(part) <= chunk_length:
            chunks.append(part)
            continue
        stride = max(16, int(sequence_length) // 2)
        for start in range(0, len(part), stride):
            chunk = part[start:start + chunk_length]
            if len(chunk) >= 8:
                chunks.append(chunk)

    def chunk_priority(chunk: list[dict]) -> float:
        first = chunk[0]
        human_bonus = 2.5 if first.get("source") == "human" else 0.0
        success_bonus = 1.5 if first.get("trajectory_class") == "successful_ai" else 0.0
        failure_bonus = 0.9 if str(first.get("failure_type", "none")) != "none" else 0.0
        novelty_bonus = 1.8 * float(first.get("novelty_score", 0.0))
        priority = sum(max(0.05, float(item.get("priority", 0.05))) for item in chunk) / max(1, len(chunk))
        return human_bonus + success_bonus + failure_bonus + novelty_bonus + priority

    strata: dict[str, dict[str, deque]] = {}
    for chunk in chunks:
        stratum = _sampling_stratum(chunk[0])
        episode_id = str(chunk[0]["episode_id"])
        strata.setdefault(stratum, {}).setdefault(episode_id, deque()).append(chunk)
    for episode_map in strata.values():
        for episode_id, values in list(episode_map.items()):
            episode_map[episode_id] = deque(sorted(values, key=chunk_priority, reverse=True))

    stratum_order = list(strata)
    rng.shuffle(stratum_order)
    episode_orders: dict[str, list[str]] = {}
    episode_offsets: dict[str, int] = {}
    for stratum in stratum_order:
        order = list(strata[stratum])
        rng.shuffle(order)
        order.sort(
            key=lambda episode_id: chunk_priority(strata[stratum][episode_id][0]),
            reverse=True,
        )
        episode_orders[stratum] = order
        episode_offsets[stratum] = 0

    selected: list[dict] = []
    chunk_index = 0
    while len(selected) < maximum and stratum_order:
        progressed = False
        active_strata: list[str] = []
        for stratum in stratum_order:
            order = episode_orders[stratum]
            if not order:
                continue
            chosen_episode = None
            for _ in range(len(order)):
                offset = episode_offsets[stratum] % len(order)
                episode_offsets[stratum] += 1
                candidate_episode = order[offset]
                if strata[stratum][candidate_episode]:
                    chosen_episode = candidate_episode
                    break
            if chosen_episode is None:
                continue
            chunk = strata[stratum][chosen_episode].popleft()
            remaining = maximum - len(selected)
            chosen = chunk if len(chunk) <= remaining else chunk[:remaining] if remaining >= 8 else []
            if chosen:
                sequence_id = (
                    f"{chosen[0]['episode_id']}:{int(chosen[0]['step'])}:"
                    f"{int(chosen[-1]['step'])}:{chunk_index}"
                )
                selected.extend({**item, "_sequence_id": sequence_id} for item in chosen)
                chunk_index += 1
                progressed = True
            if any(strata[stratum][episode_id] for episode_id in order):
                active_strata.append(stratum)
            if len(selected) >= maximum:
                break
        if not progressed:
            break
        stratum_order = active_strata
    return selected




def load_training_data(
    np,
    db_path: Path,
    action_count: int,
    sample_limit: int,
    stop_event: threading.Event | None,
    n_step_horizon: int = N_STEP_HORIZON_DEFAULT,
    validation_fraction: float = VALIDATION_EPISODE_FRACTION,
    reward_config: dict | None = None,
):
    ensure_database(db_path)
    maximum_action = action_space_size(action_count)
    horizon = max(10, min(20, int(n_step_horizon)))
    validation_fraction = max(0.05, min(0.35, float(validation_fraction)))
    reward_config = reward_config or DEFAULT_CONFIG
    limit = max(32, int(sample_limit))
    rng = np.random.default_rng(0xA61)
    connection = sqlite3.connect(db_path, timeout=60)
    install_sqlite_cancel_handler(connection, stop_event)
    invalid = 0
    try:
        episode_rows = connection.execute(
            "SELECT episode_id,COUNT(*),SUM(priority),MAX(rowid),MIN(source),"
            "SUM(task_reward),SUM(exploration_reward),SUM(safety_penalty),AVG(reward),MAX(done) "
            "FROM transitions GROUP BY episode_id"
        ).fetchall()
        candidates: list[dict] = []
        for (
            episode_id,
            count,
            priority_sum,
            last_row,
            source,
            task_total,
            exploration_total,
            safety_total,
            reward_mean,
            done,
        ) in episode_rows:
            raise_if_cancelled(stop_event)
            count_value = max(1, int(count))
            task_value = float(task_total or 0.0)
            exploration_value = float(exploration_total or 0.0)
            safety_value = float(safety_total or 0.0)
            reward_value = float(reward_mean or 0.0)
            exploration_mean = exploration_value / count_value
            failure_type = _classify_failure_type(
                bool(done), task_value, safety_value, reward_value, exploration_mean
            )
            success_rate = _bounded_episode_success_rate(
                task_value,
                exploration_value,
                safety_value,
                reward_value,
                bool(done),
                failure_type,
                count_value,
            )
            average_priority = float(priority_sum or 0.0) / count_value
            novelty_proxy = max(
                0.0,
                min(
                    1.0,
                    0.58 * min(1.0, exploration_mean * 2.5)
                    + 0.42 * min(1.0, math.log1p(max(0.0, average_priority)) / math.log(6.0)),
                ),
            )
            source_group = "human" if str(source) == "human" else "ai"
            stratum = "|".join(
                (
                    source_group,
                    _success_rate_bucket(success_rate),
                    failure_type,
                    _novelty_bucket(novelty_proxy),
                )
            )
            candidates.append(
                {
                    "episode_id": str(episode_id),
                    "count": count_value,
                    "priority": float(priority_sum or 0.0),
                    "last_row": int(last_row or 0),
                    "novelty": novelty_proxy,
                    "stratum": stratum,
                }
            )
        selected = _select_episode_ids_stratified(
            candidates,
            max(limit * 3, limit + 128),
            rng,
        )
        if not selected:
            return None
        placeholders = ",".join("?" for _ in selected)
        rows = connection.execute(
            f"SELECT episode_id,step,source,state,action,reward,next_state,done,priority,"
            f"task_reward,exploration_reward,safety_penalty FROM transitions "
            f"WHERE episode_id IN ({placeholders}) ORDER BY episode_id,step",
            selected,
        ).fetchall()
    except sqlite3.DatabaseError as error:
        raise_if_sqlite_cancelled(error, stop_event)
        raise
    finally:
        connection.close()

    episodes: dict[str, list[dict]] = {}
    for (
        episode_id,
        step,
        source,
        state,
        action,
        reward,
        next_state,
        done,
        priority,
        task_reward,
        exploration_reward,
        safety_penalty,
    ) in rows:
        try:
            action_id = int(action)
            stored_reward = float(reward)
            done_value = bool(int(done))
            raw_task = float(task_reward)
            raw_exploration = float(exploration_reward)
            raw_safety = float(safety_penalty)
            if not all(math.isfinite(value) for value in (stored_reward, raw_task, raw_exploration, raw_safety)):
                raise ValueError
            task_value = max(-1.0, min(1.0, raw_task))
            exploration_value = max(0.0, min(1.0, raw_exploration))
            safety_value = max(0.0, min(2.0, raw_safety))
            reward_value = compose_reward(
                {
                    "task_reward": task_value,
                    "exploration_reward": exploration_value,
                    "safety_penalty": safety_value,
                },
                reward_config,
            )
            if action_id >= action_count and action_id < action_count * DURATION_HEAD_SIZE:
                action_id //= DURATION_HEAD_SIZE
            if source not in ("human", "ai") or not 0 <= action_id < maximum_action:
                raise ValueError
            state_blob = _normalize_temporal_action_schema(bytes(state), action_count)
            decode_temporal_state(state_blob)
            next_blob = _normalize_temporal_action_schema(bytes(next_state), action_count) if next_state is not None else None
            if next_blob is not None:
                decode_temporal_state(next_blob)
            if not done_value and next_blob is None:
                raise ValueError
            episodes.setdefault(str(episode_id), []).append(
                {
                    "episode_id": str(episode_id),
                    "step": int(step),
                    "source": str(source),
                    "state": state_blob,
                    "action": action_id,
                    "reward": max(-1.0, min(1.0, reward_value)),
                    "next_state": next_blob,
                    "done": done_value,
                    "priority": max(0.05, float(priority)),
                    "task_reward": task_value,
                    "exploration_reward": exploration_value,
                    "safety_penalty": safety_value,
                }
            )
        except Exception:
            invalid += 1

    for records in episodes.values():
        records.sort(key=lambda item: int(item["step"]))
        human_episode = bool(records and records[0]["source"] == "human")
        task_total = sum(float(record["task_reward"]) for record in records)
        exploration_total = sum(float(record["exploration_reward"]) for record in records)
        safety_total = sum(float(record["safety_penalty"]) for record in records)
        reward_mean = sum(float(record["reward"]) for record in records) / max(1, len(records))
        exploration_mean = exploration_total / max(1, len(records))
        terminal = bool(records and records[-1].get("done"))
        failure_type = _classify_failure_type(
            terminal, task_total, safety_total, reward_mean, exploration_mean
        )
        success_rate = _bounded_episode_success_rate(
            task_total,
            exploration_total,
            safety_total,
            reward_mean,
            terminal,
            failure_type,
            len(records),
        )
        novelty_score = _episode_novelty_score(records)
        trajectory_class = (
            "human"
            if human_episode
            else "successful_ai"
            if success_rate >= 0.65 and failure_type == "none"
            else "failed_ai"
            if failure_type != "none" and success_rate < 0.45
            else "ordinary_ai"
        )
        if human_episode:
            episode_quality = success_rate * (0.35 if failure_type != "none" else 1.0)
        elif trajectory_class == "successful_ai":
            episode_quality = max(0.70, success_rate)
        elif trajectory_class == "failed_ai":
            episode_quality = max(0.03, success_rate * 0.20)
        else:
            episode_quality = max(0.20, min(0.60, success_rate))
        for record in records:
            record["trajectory_class"] = trajectory_class
            record["episode_quality"] = float(episode_quality)
            record["episode_success_rate"] = float(success_rate)
            record["failure_type"] = failure_type
            record["novelty_score"] = float(novelty_score)
            record["novelty_bucket"] = _novelty_bucket(novelty_score)
            record["sampling_stratum"] = _sampling_stratum(record)

    train_records: list[dict] = []
    validation_records: list[dict] = []
    discount = 0.96
    for episode_id, records in episodes.items():
        validation_bucket = int.from_bytes(hashlib.sha256(episode_id.encode("utf-8")).digest()[:4], "little") / 2**32
        target = validation_records if validation_bucket < validation_fraction else train_records
        for index, record in enumerate(records):
            total = 0.0
            task_total = 0.0
            exploration_total = 0.0
            safety_total = 0.0
            multiplier = 1.0
            n_next = record["next_state"]
            n_done = record["done"]
            steps_used = 1
            for offset in range(horizon):
                position = index + offset
                if position >= len(records):
                    break
                item = records[position]
                if int(item["step"]) != int(record["step"]) + offset:
                    break
                total += multiplier * float(item["reward"])
                task_total += multiplier * float(item["task_reward"])
                exploration_total += multiplier * float(item["exploration_reward"])
                safety_total += multiplier * float(item["safety_penalty"])
                steps_used = offset + 1
                n_next = item["next_state"]
                n_done = bool(item["done"])
                if n_done:
                    break
                multiplier *= discount
            enriched = dict(record)
            enriched.update(
                {
                    "n_return": max(-3.0, min(3.0, total)),
                    "n_task_return": max(-3.0, min(3.0, task_total)),
                    "n_exploration_return": max(0.0, min(3.0, exploration_total)),
                    "n_safety_return": max(0.0, min(4.0, safety_total)),
                    "n_next_state": n_next,
                    "n_done": n_done,
                    "discount_power": 0.0 if n_done else discount**steps_used,
                    "n_steps": steps_used,
                }
            )
            target.append(enriched)
    if not validation_records and len(episodes) > 1:
        one_episode = next(iter(episodes))
        moved = [record for record in train_records if record["episode_id"] == one_episode]
        train_records = [record for record in train_records if record["episode_id"] != one_episode]
        validation_records.extend(moved)
    if not train_records and validation_records:
        one_episode = validation_records[0]["episode_id"]
        moved = [record for record in validation_records if record["episode_id"] == one_episode]
        validation_records = [record for record in validation_records if record["episode_id"] != one_episode]
        train_records.extend(moved)

    train_records = contiguous_trajectory_records(
        train_records,
        sample_limit,
        int(reward_config.get("sequence_length", TRAIN_SEQUENCE_LENGTH)),
        int(reward_config.get("burn_in_steps", TRAIN_BURN_IN_STEPS)),
        horizon,
        rng,
    )
    validation_limit = max(64, min(4096, sample_limit // 4))
    if len(validation_records) > validation_limit:
        validation_records = contiguous_trajectory_records(
            validation_records,
            validation_limit,
            int(reward_config.get("sequence_length", TRAIN_SEQUENCE_LENGTH)),
            int(reward_config.get("burn_in_steps", TRAIN_BURN_IN_STEPS)),
            horizon,
            rng,
        )
    strata = {
        str(record.get("sampling_stratum", ""))
        for record in train_records
        if record.get("sampling_stratum")
    }
    return {
        "train": train_records,
        "validation": validation_records,
        "invalid": invalid,
        "episodes": len(episodes),
        "horizon": horizon,
        "strata": len(strata),
    }




def predict_progress(np, model: dict, hidden) -> float:
    value = float(np.asarray(hidden, dtype=np.float32) @ model["progress_w"][:, 0] + model["progress_b"][0])
    return max(-4.0, min(4.0, value))


def _record_progress_stability(record: dict) -> float:
    try:
        frames, _, _ = decode_temporal_state(record["state"])
        motion = feature_motion(frames[-1])
    except Exception:
        motion = 1.0
    safety = max(0.0, min(2.0, float(record.get("safety_penalty", 0.0))))
    excessive_motion = max(0.0, min(1.0, (motion - 0.18) / 0.45))
    terminal_penalty = 0.35 if bool(record.get("done", False)) and safety > 0.25 else 0.0
    return max(0.10, min(1.0, 1.0 - 0.55 * excessive_motion - 0.30 * safety - terminal_penalty))


def _ordered_progress_positions(
    window: list[dict],
    earlier_position: int,
    later_position: int,
) -> tuple[int, int, float] | None:
    earlier = window[earlier_position]
    later = window[later_position]
    source = str(earlier.get("source", ""))
    trajectory_class = str(earlier.get("trajectory_class", ""))
    stability = 0.5 * (
        _record_progress_stability(earlier)
        + _record_progress_stability(later)
    )
    if source == "human":
        episode_quality = max(
            0.0,
            min(1.0, float(earlier.get("episode_quality", 0.50))),
        )
        return_difference = (
            float(later.get("n_task_return", 0.0))
            - float(earlier.get("n_task_return", 0.0))
        )
        later_safety = float(later.get("n_safety_return", later.get("safety_penalty", 0.0)))
        if (
            bool(later.get("done", False))
            and (episode_quality < 0.30 or later_safety > 0.50)
        ):
            return later_position, earlier_position, max(0.15, stability * 0.60)
        if abs(return_difference) > 0.08:
            if return_difference > 0.0:
                return earlier_position, later_position, max(0.18, stability * episode_quality)
            return later_position, earlier_position, max(0.18, stability * episode_quality)
        if episode_quality >= 0.65 and later_safety < 0.25:
            return earlier_position, later_position, max(0.20, stability * episode_quality)
        return None
    if trajectory_class == "successful_ai":
        return earlier_position, later_position, max(0.20, stability)
    if trajectory_class == "failed_ai" and (
        bool(later.get("done", False))
        or float(later.get("safety_penalty", 0.0)) > 0.35
    ):
        return later_position, earlier_position, max(0.20, stability)
    return_difference = (
        float(later.get("n_task_return", 0.0))
        - float(earlier.get("n_task_return", 0.0))
    )
    if abs(return_difference) <= 0.10:
        return None
    if return_difference > 0.0:
        return earlier_position, later_position, max(0.15, stability * 0.75)
    return later_position, earlier_position, max(0.15, stability * 0.75)


def _record_duration_index(record: dict) -> int:
    try:
        state_blob = record.get("next_state") or record.get("state")
        _, _, durations = decode_temporal_state(state_blob)
        return duration_bin(float(durations[-1]))
    except Exception:
        return DURATION_HEAD_SIZE // 2


def _convert_legacy_temporal_action_schema(state: bytes) -> bytes:
    frames, actions, durations = decode_temporal_state(state)
    normalized_actions = [max(0, int(value)) // DURATION_HEAD_SIZE for value in actions]
    return build_temporal_state(frames, normalized_actions, durations)


def _normalize_temporal_action_schema(state: bytes, action_count: int) -> bytes:
    frames, actions, durations = decode_temporal_state(state)
    changed = False
    normalized_actions = []
    for value in actions:
        action_id = int(value)
        if action_id >= int(action_count) and action_id < int(action_count) * DURATION_HEAD_SIZE:
            action_id //= DURATION_HEAD_SIZE
            changed = True
        normalized_actions.append(action_id)
    normalized_state = build_temporal_state(frames, normalized_actions, durations)
    return normalized_state if changed or normalized_state != state else state


def extract_human_skills(records: list[dict], config: dict) -> list[dict]:
    minimum = max(SKILL_MIN_STEPS, min(16, int(config.get("skill_min_steps", SKILL_MIN_STEPS))))
    maximum = max(minimum, min(SKILL_MAX_STEPS, int(config.get("skill_max_steps", SKILL_MAX_STEPS))))
    limit = max(8, min(SKILL_HEAD_SIZE, int(config.get("skill_limit", SKILL_HEAD_SIZE))))
    episodes = _continuous_trajectory_parts(
        [record for record in records if record.get("source") == "human"]
    )
    candidates: dict[tuple[tuple[int, int], ...], list[float]] = {}
    lengths = sorted({minimum, min(maximum, 8), min(maximum, 16), maximum})
    for episode in episodes.values():
        sequence = [(int(item["action"]), _record_duration_index(item), float(item.get("task_reward", 0.0))) for item in episode]
        for length in lengths:
            if length < minimum or len(sequence) < length:
                continue
            stride = max(1, length // 2)
            for start in range(0, len(sequence) - length + 1, stride):
                segment = sequence[start:start + length]
                signature = tuple((action, duration) for action, duration, _ in segment)
                quality = sum(reward for _, _, reward in segment) / length
                candidates.setdefault(signature, []).append(quality)
    ranked = []
    for signature, qualities in candidates.items():
        count = len(qualities)
        if count < 2 and len(signature) < 8:
            continue
        quality = sum(qualities) / max(1, count)
        diversity = len(set(action for action, _ in signature)) / max(1, len(signature))
        score = math.log1p(count) * math.sqrt(len(signature)) + 0.8 * quality + 0.25 * diversity
        ranked.append((score, signature, count, quality))
    ranked.sort(key=lambda item: item[0], reverse=True)
    result = []
    for _, signature, count, quality in ranked[:limit]:
        result.append({
            "actions": [action for action, _ in signature],
            "durations": [duration for _, duration in signature],
            "count": int(count),
            "quality": max(-1.0, min(1.0, float(quality))),
        })
    return result


def skill_label_for_position(window: list[dict], position: int, skills: list[dict]) -> int | None:
    best = None
    best_length = -1
    for skill_index, skill in enumerate(skills[:SKILL_HEAD_SIZE]):
        actions = skill.get("actions", [])
        if not SKILL_MIN_STEPS <= len(actions) <= SKILL_MAX_STEPS or position + len(actions) > len(window):
            continue
        if all(int(window[position + offset]["action"]) == int(action) for offset, action in enumerate(actions)):
            if len(actions) > best_length:
                best = skill_index
                best_length = len(actions)
    return best


def choose_skill(np, model: dict, hidden, skills: list[dict], start_probability: float, exploration: float) -> int | None:
    count = min(SKILL_HEAD_SIZE, len(skills))
    if count <= 0 or random.random() > max(0.0, min(1.0, float(start_probability))):
        return None
    logits = np.asarray(hidden, dtype=np.float32) @ model["policy_skill_w"][:, :count] + model["policy_skill_b"][:count]
    values = np.asarray(hidden, dtype=np.float32) @ model["skill_value_w"][:, :count] + model["skill_value_b"][:count]
    quality = np.asarray([float(skill.get("quality", 0.0)) for skill in skills[:count]], dtype=np.float32)
    score = logits + 0.35 * values + 0.20 * quality
    if random.random() < max(0.0, min(0.30, float(exploration))):
        return random.randrange(count)
    return int(np.argmax(score))


def _train_progress_pair(np, model: dict, earlier_hidden, later_hidden, margin: float, weight: float, gradients: dict[str, object]):
    earlier = predict_progress(np, model, earlier_hidden)
    later = predict_progress(np, model, later_hidden)
    violation = float(margin) - later + earlier
    if violation <= 0.0:
        return 0.0, np.zeros_like(earlier_hidden), np.zeros_like(later_hidden)
    scale = max(0.0, float(weight))
    gradients["progress_w"][:, 0] += scale * (earlier_hidden - later_hidden)
    gradients["progress_b"][0] += 0.0
    earlier_gradient = model["progress_w"][:, 0] * scale
    later_gradient = -model["progress_w"][:, 0] * scale
    return violation * scale, earlier_gradient.astype(np.float32), later_gradient.astype(np.float32)


def _train_skill_head(np, model: dict, hidden, skill_index: int, target_return: float, weight: float, gradients: dict[str, object]):
    count = SKILL_HEAD_SIZE
    logits = hidden @ model["policy_skill_w"] + model["policy_skill_b"]
    probabilities = _softmax_vector(np, logits).astype(np.float32)
    gradient = probabilities
    gradient[int(skill_index)] -= 1.0
    gradient *= max(0.0, float(weight))
    gradients["policy_skill_w"] += np.outer(hidden, gradient).astype(np.float32)
    gradients["policy_skill_b"] += gradient
    hidden_gradient = model["policy_skill_w"] @ gradient
    value = float(hidden @ model["skill_value_w"][:, int(skill_index)] + model["skill_value_b"][int(skill_index)])
    error = max(-3.0, min(3.0, value - float(target_return))) * max(0.0, float(weight))
    gradients["skill_value_w"][:, int(skill_index)] += hidden * error
    gradients["skill_value_b"][int(skill_index)] += error
    hidden_gradient += model["skill_value_w"][:, int(skill_index)] * error
    loss = -math.log(max(1e-9, float(probabilities[int(skill_index)]))) * max(0.0, float(weight)) + 0.5 * error * error
    return float(loss), hidden_gradient.astype(np.float32)


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


def _softmax_vector(np, logits):
    values=np.asarray(logits,dtype=np.float64); values-=float(values.max(initial=0.0)); exp=np.exp(np.clip(values,-60.0,30.0)); return exp/max(1e-12,float(exp.sum()))



_TEMPORAL_PARAMETER_KEYS = frozenset({
    "frame_proj", "frame_bias", "action_embedding", "duration_embedding",
    "Wz", "Uz", "bz", "Wr", "Ur", "br", "Wh", "Uh", "bh",
})
_CONV_PARAMETER_KEYS = frozenset({
    "conv_master_w", "conv_b", "conv2_depthwise_w", "conv2_pointwise_w", "conv2_b",
    "conv3_depthwise_w", "conv3_pointwise_w", "conv3_b",
})
_TRAINABLE_PARAMETER_KEYS = (
    *_CONV_PARAMETER_KEYS,
    "frame_proj", "frame_bias", "action_embedding", "duration_embedding",
    "Wz", "Uz", "bz", "Wr", "Ur", "br", "Wh", "Uh", "bh",
    "policy_control_w", "policy_control_b", "policy_key_w", "policy_key_b", "policy_mouse_w", "policy_mouse_b",
    "policy_button_w", "policy_button_b", "policy_duration_w", "policy_duration_b", "policy_duration_kind_b",
    "policy_action_w", "policy_action_b", "policy_skill_w", "policy_skill_b", "skill_value_w", "skill_value_b",
    "mouse_offset_w", "mouse_offset_b",
    "q_control_w", "q_control_b", "q_key_w", "q_key_b", "q_mouse_w", "q_mouse_b",
    "q_button_w", "q_button_b", "q_duration_w", "q_duration_b", "q_duration_kind_b",
    "q_action_w", "q_action_b", "value_w", "value_b", "progress_w", "progress_b",
    "safety_w", "safety_b",
    "world_encoder_w", "world_encoder_b", "world_dynamics_w",
    "world_dynamics_action_w", "world_dynamics_duration_w", "world_dynamics_b",
    "world_reward_w", "world_reward_action_w", "world_reward_duration_w",
    "world_reward_b", "world_done_w", "world_done_b",
    "world_latent_to_hidden_w", "world_latent_to_hidden_b",
    "reward_model_w", "reward_model_b",
)

def _training_gradient_buffer(np, model: dict) -> dict[str, object]:
    return {key: np.zeros_like(model[key], dtype=np.float32) for key in _TRAINABLE_PARAMETER_KEYS}


def _factor_bucket_gradient(np, factors, column: int, action_gradient, size: int):
    bucket_gradient = np.zeros(size, dtype=np.float32)
    np.add.at(bucket_gradient, factors[:, column], np.asarray(action_gradient, dtype=np.float32))
    return bucket_gradient


def _train_factor_policy(
    np,
    model: dict,
    hidden,
    factors,
    learning_rate: float,
    weight: float,
    action_id: int | None = None,
    gradients: dict[str, object] | None = None,
    probabilities=None,
    duration_index: int | None = None,
) -> tuple[float, object]:
    step = max(0.0, min(0.05, float(learning_rate)))
    if action_id is None:
        matches = np.flatnonzero(np.all(model["action_factors"][:, :2] == np.asarray(factors)[:2], axis=1))
        action_id = int(matches[0]) if len(matches) else 0
    if probabilities is None:
        probabilities, _, _ = factorized_action_outputs_from_hidden(np, model, hidden)
    scale_weight = max(0.0, min(100.0, float(weight)))
    action_gradient = np.asarray(probabilities, dtype=np.float32).copy()
    action_gradient[int(action_id)] -= 1.0
    action_gradient *= scale_weight
    loss = -math.log(max(1e-9, float(probabilities[int(action_id)]))) * scale_weight
    local = gradients is None
    if local:
        gradients = _training_gradient_buffer(np, model)
    factor_matrix = model["action_factors"].astype(np.int64, copy=False)
    hidden_gradient = model["policy_action_w"] @ action_gradient
    gradients["policy_action_w"] += np.outer(hidden, action_gradient).astype(np.float32)
    gradients["policy_action_b"] += action_gradient
    for w_key, b_key, column in (
        ("policy_control_w", "policy_control_b", 0),
        ("policy_mouse_w", "policy_mouse_b", 1),
    ):
        bucket_gradient = _factor_bucket_gradient(np, factor_matrix, column, action_gradient, model[b_key].shape[0])
        gradients[w_key] += np.outer(hidden, bucket_gradient).astype(np.float32)
        gradients[b_key] += bucket_gradient
        hidden_gradient += model[w_key] @ bucket_gradient
    key_gradient = action_gradient @ model["action_key_multihot"]
    button_gradient = action_gradient @ model["action_button_multihot"]
    gradients["policy_key_w"] += np.outer(hidden, key_gradient).astype(np.float32)
    gradients["policy_key_b"] += key_gradient
    gradients["policy_button_w"] += np.outer(hidden, button_gradient).astype(np.float32)
    gradients["policy_button_b"] += button_gradient
    hidden_gradient += model["policy_key_w"] @ key_gradient
    hidden_gradient += model["policy_button_w"] @ button_gradient

    if duration_index is not None:
        kind = int(factor_matrix[int(action_id), 0])
        duration_target = max(0, min(DURATION_HEAD_SIZE - 1, int(duration_index)))
        duration_probabilities, _ = conditional_duration_outputs(np, model, hidden, kind)
        duration_gradient = duration_probabilities.copy()
        duration_gradient[duration_target] -= 1.0
        duration_gradient *= scale_weight
        gradients["policy_duration_w"] += np.outer(hidden, duration_gradient).astype(np.float32)
        gradients["policy_duration_b"] += duration_gradient
        gradients["policy_duration_kind_b"][kind] += duration_gradient
        hidden_gradient += model["policy_duration_w"] @ duration_gradient
        loss += -math.log(max(1e-9, float(duration_probabilities[duration_target]))) * scale_weight

    mouse_bucket = int(factor_matrix[int(action_id), 1])
    mouse_target = None
    if 1 <= mouse_bucket <= MOUSE_GRID_WIDTH * MOUSE_GRID_HEIGHT:
        index = mouse_bucket - 1
        mouse_target = np.asarray(
            [
                2.0 * (index % MOUSE_GRID_WIDTH) / max(1, MOUSE_GRID_WIDTH - 1) - 1.0,
                2.0 * (index // MOUSE_GRID_WIDTH) / max(1, MOUSE_GRID_HEIGHT - 1) - 1.0,
            ],
            dtype=np.float32,
        )
    elif 577 <= mouse_bucket < 602:
        index = mouse_bucket - 577
        mouse_target = np.asarray([((index % 5) - 2) / 2.0, ((index // 5) - 2) / 2.0], dtype=np.float32)
    if mouse_target is not None:
        mouse_prediction = np.tanh(np.asarray(hidden, dtype=np.float32) @ model["mouse_offset_w"] + model["mouse_offset_b"])
        mouse_error = (mouse_prediction - mouse_target) * (1.0 - mouse_prediction * mouse_prediction)
        mouse_error *= 0.20 * scale_weight
        gradients["mouse_offset_w"] += np.outer(hidden, mouse_error).astype(np.float32)
        gradients["mouse_offset_b"] += mouse_error
        hidden_gradient += model["mouse_offset_w"] @ mouse_error
        loss += 0.10 * float(np.mean((mouse_prediction - mouse_target) ** 2)) * scale_weight
    if local:
        active = [gradient for gradient in gradients.values() if np.any(gradient)]
        if active:
            clip_gradients_by_global_norm(np, active, 6.0)
            for key, gradient in gradients.items():
                model[key] -= step * gradient
            _synchronize_quantized_conv_weights(np, model)
    return float(loss), hidden_gradient.astype(np.float32, copy=False)




def _logsumexp_vector(np, values) -> float:
    values = np.asarray(values, dtype=np.float64)
    maximum = float(values.max(initial=0.0))
    return maximum + math.log(max(1e-12, float(np.exp(np.clip(values - maximum, -60.0, 30.0)).sum())))


def _train_factor_q(
    np,
    model: dict,
    hidden,
    action_id: int,
    target: float,
    learning_rate: float,
    sample_weight: float,
    gradients: dict[str, object] | None = None,
    q_values=None,
    cql_weight: float = 0.02,
    duration_index: int | None = None,
) -> tuple[float, object]:
    step = max(0.0, min(0.02, float(learning_rate)))
    twin_q_values = factorized_twin_q_outputs_from_hidden(np, model, hidden)
    local = gradients is None
    if local:
        gradients = _training_gradient_buffer(np, model)
    factor_matrix = model["action_factors"].astype(np.int64, copy=False)
    hidden_gradient = np.zeros_like(hidden, dtype=np.float32)
    td_losses = []
    cql_losses = []
    targets = np.asarray(target, dtype=np.float32).reshape(-1)
    if targets.size == 1:
        targets = np.repeat(targets, VALUE_HEAD_COUNT)
    if targets.size != VALUE_HEAD_COUNT or not np.isfinite(targets).all():
        raise ValueError("critic 训练目标无效")
    ensemble_scale = 1.0 / (VALUE_HEAD_COUNT * Q_TWIN_COUNT)
    for twin in range(Q_TWIN_COUNT):
        for head in range(VALUE_HEAD_COUNT):
            values = np.asarray(twin_q_values[twin, head], dtype=np.float32)
            head_target = float(targets[head])
            error = float(values[int(action_id)] - head_target)
            clipped_error = max(-3.0, min(3.0, error))
            bootstrap_weight = 0.90 + 0.10 * float((int(action_id) + twin + head) % 2)
            action_gradient = np.zeros(len(values), dtype=np.float32)
            action_gradient[int(action_id)] = (
                clipped_error
                * max(0.0, float(sample_weight))
                * ensemble_scale
                * bootstrap_weight
            )
            conservative_gradient = _softmax_vector(np, values).astype(np.float32)
            conservative_gradient[int(action_id)] -= 1.0
            conservative_scale = 0.0 if head == SAFETY_CRITIC else max(0.0, float(cql_weight))
            conservative_gradient *= conservative_scale * ensemble_scale
            action_gradient += conservative_gradient
            td_losses.append(0.5 * clipped_error * clipped_error)
            cql_losses.append(_logsumexp_vector(np, values) - float(values[int(action_id)]))
            gradients["q_action_w"][twin, head] += np.outer(hidden, action_gradient).astype(np.float32)
            gradients["q_action_b"][twin, head] += action_gradient
            hidden_gradient += model["q_action_w"][twin, head] @ action_gradient
            for w_key, b_key, column in (
                ("q_control_w", "q_control_b", 0),
                ("q_mouse_w", "q_mouse_b", 1),
            ):
                bucket_gradient = _factor_bucket_gradient(
                    np,
                    factor_matrix,
                    column,
                    action_gradient / 4.0,
                    model[b_key].shape[-1],
                )
                gradients[w_key][twin, head] += np.outer(hidden, bucket_gradient).astype(np.float32)
                gradients[b_key][twin, head] += bucket_gradient
                hidden_gradient += model[w_key][twin, head] @ bucket_gradient
            key_gradient = (action_gradient / 4.0) @ model["action_key_multihot"]
            button_gradient = (action_gradient / 4.0) @ model["action_button_multihot"]
            gradients["q_key_w"][twin, head] += np.outer(hidden, key_gradient).astype(np.float32)
            gradients["q_key_b"][twin, head] += key_gradient
            gradients["q_button_w"][twin, head] += np.outer(hidden, button_gradient).astype(np.float32)
            gradients["q_button_b"][twin, head] += button_gradient
            hidden_gradient += model["q_key_w"][twin, head] @ key_gradient
            hidden_gradient += model["q_button_w"][twin, head] @ button_gradient

            if duration_index is not None:
                kind = int(factor_matrix[int(action_id), 0])
                duration_target = max(0, min(DURATION_HEAD_SIZE - 1, int(duration_index)))
                duration_values = (
                    hidden @ model["q_duration_w"][twin, head]
                    + model["q_duration_b"][twin, head]
                    + model["q_duration_kind_b"][twin, head, kind]
                )
                duration_error = max(
                    -3.0,
                    min(3.0, float(duration_values[duration_target]) - head_target),
                )
                duration_gradient = np.zeros(DURATION_HEAD_SIZE, dtype=np.float32)
                duration_gradient[duration_target] = (
                    duration_error
                    * max(0.0, float(sample_weight))
                    * ensemble_scale
                    * bootstrap_weight
                )
                gradients["q_duration_w"][twin, head] += np.outer(hidden, duration_gradient).astype(np.float32)
                gradients["q_duration_b"][twin, head] += duration_gradient
                gradients["q_duration_kind_b"][twin, head, kind] += duration_gradient
                hidden_gradient += model["q_duration_w"][twin, head] @ duration_gradient
                td_losses.append(0.5 * duration_error * duration_error)
    loss = float(
        sum(td_losses) / max(1, len(td_losses))
        + max(0.0, float(cql_weight)) * sum(cql_losses) / max(1, len(cql_losses))
    )
    if local:
        active = [gradient for gradient in gradients.values() if np.any(gradient)]
        if active:
            clip_gradients_by_global_norm(np, active, 6.0)
            for key, gradient in gradients.items():
                model[key] -= step * gradient
            _synchronize_quantized_conv_weights(np, model)
    return loss, hidden_gradient.astype(np.float32, copy=False)



def _train_value_head(
    np,
    model: dict,
    hidden,
    q_data: float,
    value: float,
    expectile: float,
    sample_weight: float,
    gradients: dict[str, object],
) -> tuple[float, object]:
    difference = float(q_data) - float(value)
    expectile_weight = float(expectile) if difference >= 0.0 else 1.0 - float(expectile)
    weight = expectile_weight * max(0.0, float(sample_weight))
    value_gradient = -2.0 * weight * difference
    gradients["value_w"][:, 0] += hidden * value_gradient
    gradients["value_b"][0] += value_gradient
    hidden_gradient = model["value_w"][:, 0] * value_gradient
    return float(weight * difference * difference), hidden_gradient.astype(np.float32, copy=False)


def _train_safety_head(
    np,
    model: dict,
    hidden,
    target: float,
    sample_weight: float,
    gradients: dict[str, object],
) -> tuple[float, object]:
    target_value = max(0.0, min(1.0, float(target)))
    weight = max(0.0, float(sample_weight))
    prediction = predict_safety_probability(np, model, hidden)
    logit_gradient = (prediction - target_value) * weight
    gradients["safety_w"][:, 0] += np.asarray(hidden, dtype=np.float32) * logit_gradient
    gradients["safety_b"][0] += logit_gradient
    hidden_gradient = model["safety_w"][:, 0] * logit_gradient
    loss = -weight * (
        target_value * math.log(max(1e-9, prediction))
        + (1.0 - target_value) * math.log(max(1e-9, 1.0 - prediction))
    )
    return float(loss), hidden_gradient.astype(np.float32, copy=False)



def train_world_model_transition(
    np,
    model: dict,
    hidden,
    next_hidden,
    action_id: int,
    reward_targets,
    done: bool,
    sample_weight: float,
    gradients: dict[str, object],
    target_model: dict | None = None,
    target_next_hidden=None,
    duration_index: int = DURATION_HEAD_SIZE // 2,
) -> tuple[float, object]:
    action = max(0, min(len(model["action_embedding"]) - 1, int(action_id)))
    duration = max(0, min(DURATION_HEAD_SIZE - 1, int(duration_index)))
    hidden_value = np.asarray(hidden, dtype=np.float32)
    weight = max(0.0, min(4.0, float(sample_weight)))
    action_embedding = model["action_embedding"][action]
    duration_embedding = model["duration_embedding"][duration]
    targets = np.asarray(reward_targets, dtype=np.float32).reshape(-1)
    if targets.shape != (VALUE_HEAD_COUNT,) or not np.isfinite(targets).all():
        raise ValueError("世界模型回报目标无效")
    targets[TASK_CRITIC] = np.clip(targets[TASK_CRITIC], -1.0, 1.0)
    targets[EXPLORATION_CRITIC] = np.clip(targets[EXPLORATION_CRITIC], 0.0, 1.0)
    targets[SAFETY_CRITIC] = np.clip(targets[SAFETY_CRITIC], 0.0, 2.0)
    latent_target_model = target_model if target_model is not None else model
    latent_target_hidden = target_next_hidden if target_next_hidden is not None else next_hidden
    target_latents = (
        world_model_latent(np, latent_target_model, latent_target_hidden)
        if not done and latent_target_hidden is not None
        else None
    )
    hidden_gradient = np.zeros_like(hidden_value, dtype=np.float32)
    action_gradient_total = np.zeros_like(action_embedding, dtype=np.float32)
    duration_gradient_total = np.zeros_like(duration_embedding, dtype=np.float32)
    total_loss = 0.0
    done_target = 1.0 if done else 0.0
    member_scale = 1.0 / WORLD_MODEL_MEMBERS
    for member in range(WORLD_MODEL_MEMBERS):
        bootstrap_weight = weight * (
            0.90
            + 0.05
            * ((action + duration + member + int(model.get("world_training_steps", 0))) % 3)
        )
        encoder_w = model["world_encoder_w"][member]
        latent_pre = hidden_value @ encoder_w + model["world_encoder_b"][member]
        latent = np.tanh(latent_pre)
        dynamics_pre = (
            latent @ model["world_dynamics_w"][member]
            + action_embedding @ model["world_dynamics_action_w"][member]
            + duration_embedding @ model["world_dynamics_duration_w"][member]
            + model["world_dynamics_b"][member]
        )
        predicted_latent = np.tanh(dynamics_pre)
        predicted_rewards = (
            predicted_latent @ model["world_reward_w"][member]
            + action_embedding @ model["world_reward_action_w"][member]
            + duration_embedding @ model["world_reward_duration_w"][member]
            + model["world_reward_b"][member]
        )
        reward_error = np.clip(predicted_rewards - targets, -3.0, 3.0)
        reward_gradient = reward_error * (bootstrap_weight * member_scale / VALUE_HEAD_COUNT)
        gradients["world_reward_w"][member] += np.outer(predicted_latent, reward_gradient).astype(np.float32)
        gradients["world_reward_action_w"][member] += np.outer(action_embedding, reward_gradient).astype(np.float32)
        gradients["world_reward_duration_w"][member] += np.outer(duration_embedding, reward_gradient).astype(np.float32)
        gradients["world_reward_b"][member] += reward_gradient
        predicted_gradient = model["world_reward_w"][member] @ reward_gradient
        action_gradient = model["world_reward_action_w"][member] @ reward_gradient
        duration_gradient = model["world_reward_duration_w"][member] @ reward_gradient

        done_probability = float(
            _sigmoid(
                np,
                predicted_latent @ model["world_done_w"][member]
                + model["world_done_b"][member],
            )[0]
        )
        done_gradient = (done_probability - done_target) * bootstrap_weight * 0.5 * member_scale
        gradients["world_done_w"][member, :, 0] += predicted_latent * done_gradient
        gradients["world_done_b"][member, 0] += done_gradient
        predicted_gradient += model["world_done_w"][member, :, 0] * done_gradient

        dynamics_loss = 0.0
        if target_latents is not None:
            dynamics_error = predicted_latent - target_latents[member]
            predicted_gradient += dynamics_error * (bootstrap_weight * member_scale / WORLD_LATENT_SIZE)
            dynamics_loss = 0.5 * bootstrap_weight * float(np.mean(dynamics_error * dynamics_error))
        projection_loss = 0.0
        if not done and next_hidden is not None:
            projected_pre = (
                predicted_latent @ model["world_latent_to_hidden_w"][member]
                + model["world_latent_to_hidden_b"][member]
            )
            projected_hidden = np.tanh(projected_pre)
            projection_error = projected_hidden - np.asarray(next_hidden, dtype=np.float32)
            projection_gradient = (
                projection_error
                * (1.0 - projected_hidden * projected_hidden)
                * (bootstrap_weight * member_scale / max(1, projected_hidden.size))
            )
            gradients["world_latent_to_hidden_w"][member] += np.outer(
                predicted_latent, projection_gradient
            ).astype(np.float32)
            gradients["world_latent_to_hidden_b"][member] += projection_gradient
            predicted_gradient += model["world_latent_to_hidden_w"][member] @ projection_gradient
            projection_loss = 0.5 * bootstrap_weight * float(np.mean(projection_error * projection_error))
        dynamics_gradient = predicted_gradient * (1.0 - predicted_latent * predicted_latent)
        gradients["world_dynamics_w"][member] += np.outer(latent, dynamics_gradient).astype(np.float32)
        gradients["world_dynamics_action_w"][member] += np.outer(action_embedding, dynamics_gradient).astype(np.float32)
        gradients["world_dynamics_duration_w"][member] += np.outer(duration_embedding, dynamics_gradient).astype(np.float32)
        gradients["world_dynamics_b"][member] += dynamics_gradient
        latent_gradient = model["world_dynamics_w"][member] @ dynamics_gradient
        action_gradient += model["world_dynamics_action_w"][member] @ dynamics_gradient
        duration_gradient += model["world_dynamics_duration_w"][member] @ dynamics_gradient
        encoder_gradient = latent_gradient * (1.0 - latent * latent)
        gradients["world_encoder_w"][member] += np.outer(hidden_value, encoder_gradient).astype(np.float32)
        gradients["world_encoder_b"][member] += encoder_gradient
        action_gradient_total += action_gradient
        duration_gradient_total += duration_gradient
        hidden_gradient += encoder_w @ encoder_gradient
        reward_loss = 0.5 * bootstrap_weight * float(np.mean(reward_error * reward_error))
        done_loss = -0.5 * bootstrap_weight * (
            done_target * math.log(max(1e-9, done_probability))
            + (1.0 - done_target) * math.log(max(1e-9, 1.0 - done_probability))
        )
        total_loss += (dynamics_loss + projection_loss + reward_loss + done_loss) * member_scale
    gradients["action_embedding"][action] += action_gradient_total
    gradients["duration_embedding"][duration] += duration_gradient_total
    model["world_training_steps"] = int(model.get("world_training_steps", 0)) + 1
    return float(total_loss), hidden_gradient.astype(np.float32, copy=False)



def _optimizer_layout(np, model: dict) -> tuple[list[str], object]:
    keys = [
        key
        for key in _TRAINABLE_PARAMETER_KEYS
        if key in model and isinstance(model[key], np.ndarray) and np.issubdtype(model[key].dtype, np.floating)
    ]
    offsets = [0]
    for key in keys:
        offsets.append(offsets[-1] + int(model[key].size))
    return keys, np.asarray(offsets, dtype=np.int64)


def _reset_optimizer_state(np, model: dict) -> None:
    keys, offsets = _optimizer_layout(np, model)
    total = int(offsets[-1]) if len(offsets) else 0
    model["optimizer_step"] = 0
    model["optimizer_schedule_step"] = 0
    model["optimizer_keys"] = list(keys)
    model["optimizer_offsets"] = offsets
    model["optimizer_m"] = np.zeros(total, dtype=np.float32)
    model["optimizer_v"] = np.zeros(total, dtype=np.float32)


def _ensure_optimizer_state(np, model: dict) -> None:
    keys, offsets = _optimizer_layout(np, model)
    total = int(offsets[-1]) if len(offsets) else 0
    stored_keys = [str(value) for value in model.get("optimizer_keys", [])]
    stored_offsets = np.asarray(model.get("optimizer_offsets", np.zeros(0)), dtype=np.int64).reshape(-1)
    moments = np.asarray(model.get("optimizer_m", np.zeros(0)), dtype=np.float32).reshape(-1)
    velocities = np.asarray(model.get("optimizer_v", np.zeros(0)), dtype=np.float32).reshape(-1)
    if (
        stored_keys != keys
        or stored_offsets.shape != offsets.shape
        or not np.array_equal(stored_offsets, offsets)
        or moments.shape != (total,)
        or velocities.shape != (total,)
        or not np.isfinite(moments).all()
        or not np.isfinite(velocities).all()
    ):
        _reset_optimizer_state(np, model)
        return
    model["optimizer_keys"] = stored_keys
    model["optimizer_offsets"] = stored_offsets.copy()
    model["optimizer_m"] = moments.copy()
    model["optimizer_v"] = velocities.copy()
    model["optimizer_step"] = max(0, int(model.get("optimizer_step", 0)))
    model["optimizer_schedule_step"] = max(0, int(model.get("optimizer_schedule_step", model["optimizer_step"])))


def _scheduled_learning_rate(
    base_learning_rate: float,
    schedule_step: int,
    warmup_steps: int,
    cosine_steps: int,
) -> float:
    base = max(1e-8, min(0.1, float(base_learning_rate)))
    step = max(1, int(schedule_step))
    warmup = max(1, int(warmup_steps))
    decay = max(16, int(cosine_steps))
    warmup_scale = min(1.0, step / warmup)
    progress = max(0.0, min(1.0, (step - warmup) / decay))
    cosine_scale = 0.10 + 0.90 * 0.5 * (1.0 + math.cos(math.pi * progress))
    return base * warmup_scale * cosine_scale


def _adam_apply(
    np,
    model: dict,
    gradients: dict[str, object],
    learning_rate: float,
    warmup_steps: int = OPTIMIZER_WARMUP_STEPS_DEFAULT,
    cosine_steps: int = OPTIMIZER_COSINE_STEPS_DEFAULT,
    weight_decay: float = OPTIMIZER_WEIGHT_DECAY_DEFAULT,
) -> float:
    _ensure_optimizer_state(np, model)
    model["optimizer_step"] = int(model.get("optimizer_step", 0)) + 1
    model["optimizer_schedule_step"] = int(model.get("optimizer_schedule_step", 0)) + 1
    step = int(model["optimizer_step"])
    schedule_step = int(model["optimizer_schedule_step"])
    effective_lr = _scheduled_learning_rate(
        learning_rate,
        schedule_step,
        warmup_steps,
        cosine_steps,
    )
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    decay = max(0.0, min(0.1, float(weight_decay)))
    key_index = {key: index for index, key in enumerate(model["optimizer_keys"])}
    offsets = model["optimizer_offsets"]
    flat_m = model["optimizer_m"]
    flat_v = model["optimizer_v"]
    for key, gradient in gradients.items():
        index = key_index.get(key)
        if index is None or not np.any(gradient):
            continue
        parameter = model[key]
        start = int(offsets[index])
        end = int(offsets[index + 1])
        moment = flat_m[start:end].reshape(parameter.shape)
        velocity = flat_v[start:end].reshape(parameter.shape)
        gradient_value = np.asarray(gradient, dtype=np.float32)
        moment *= beta1
        moment += (1.0 - beta1) * gradient_value
        velocity *= beta2
        velocity += (1.0 - beta2) * gradient_value * gradient_value
        corrected_m = moment / (1.0 - beta1 ** step)
        corrected_v = velocity / (1.0 - beta2 ** step)
        scale = 0.35 if key in _TEMPORAL_PARAMETER_KEYS else (0.12 if key in _CONV_PARAMETER_KEYS else 1.0)
        if decay > 0.0 and (
            key.endswith("_w")
            or key in {"action_embedding", "duration_embedding", "conv_master_w"}
        ):
            parameter *= max(0.0, 1.0 - effective_lr * scale * decay)
        parameter -= effective_lr * scale * corrected_m / (np.sqrt(corrected_v) + epsilon)
    return float(effective_lr)


def _batch_twin_q_outputs_from_hidden(np, model: dict, hidden_matrix):
    hidden_matrix = np.asarray(hidden_matrix, dtype=np.float32)
    factors = model["action_factors"].astype(np.int64, copy=False)
    key_matrix = model["action_key_multihot"].astype(np.float32, copy=False)
    button_matrix = model["action_button_multihot"].astype(np.float32, copy=False)
    q_control = np.einsum("bh,tvhc->btvc", hidden_matrix, model["q_control_w"]) + model["q_control_b"][None, :, :, :]
    q_key = np.einsum("bh,tvhk->btvk", hidden_matrix, model["q_key_w"]) + model["q_key_b"][None, :, :, :]
    q_mouse = np.einsum("bh,tvhm->btvm", hidden_matrix, model["q_mouse_w"]) + model["q_mouse_b"][None, :, :, :]
    q_button = np.einsum("bh,tvhu->btvu", hidden_matrix, model["q_button_w"]) + model["q_button_b"][None, :, :, :]
    factor_q = (
        q_control[:, :, :, factors[:, 0]]
        + q_mouse[:, :, :, factors[:, 1]]
        + np.einsum("btvk,ak->btva", q_key, key_matrix, optimize=True)
        + np.einsum("btvu,au->btva", q_button, button_matrix, optimize=True)
    ) / 4.0
    exact_q = np.einsum("bh,tvha->btva", hidden_matrix, model["q_action_w"]) + model["q_action_b"][None, :, :, :]
    return (factor_q + exact_q).astype(np.float32)


def _batch_model_outputs_from_hidden(np, model: dict, hidden_matrix):
    hidden_matrix = np.asarray(hidden_matrix, dtype=np.float32)
    factors = model["action_factors"].astype(np.int64, copy=False)
    policy_control = hidden_matrix @ model["policy_control_w"] + model["policy_control_b"]
    policy_key = hidden_matrix @ model["policy_key_w"] + model["policy_key_b"]
    policy_mouse = hidden_matrix @ model["policy_mouse_w"] + model["policy_mouse_b"]
    policy_button = hidden_matrix @ model["policy_button_w"] + model["policy_button_b"]
    key_matrix = model["action_key_multihot"].astype(np.float32, copy=False)
    button_matrix = model["action_button_multihot"].astype(np.float32, copy=False)
    logits = (
        policy_control[:, factors[:, 0]]
        + policy_mouse[:, factors[:, 1]]
        + policy_key @ key_matrix.T
        + policy_button @ button_matrix.T
        + hidden_matrix @ model["policy_action_w"]
        + model["policy_action_b"]
    ).astype(np.float64)
    logits -= logits.max(axis=1, keepdims=True)
    probabilities = np.exp(np.clip(logits, -60.0, 30.0))
    probabilities /= np.maximum(1e-12, probabilities.sum(axis=1, keepdims=True))
    twin_q_values = _batch_twin_q_outputs_from_hidden(np, model, hidden_matrix)
    q_values = np.minimum(twin_q_values[:, 0], twin_q_values[:, 1])
    values = hidden_matrix @ model["value_w"] + model["value_b"]
    return probabilities.astype(np.float32), q_values.astype(np.float32), values[:, 0].astype(np.float32)




def factorized_twin_q_outputs_from_hidden(np, model: dict, hidden):
    hidden_value = np.asarray(hidden, dtype=np.float32)[None, :]
    return _batch_twin_q_outputs_from_hidden(np, model, hidden_value)[0]


def factorized_action_outputs_from_hidden(np, model: dict, hidden):
    probabilities, q_values, _ = _batch_model_outputs_from_hidden(
        np,
        model,
        np.asarray(hidden, dtype=np.float32)[None, :],
    )
    return probabilities[0], q_values[0], np.asarray(hidden, dtype=np.float32)



def sequence_training_windows(
    records: list[dict],
    sequence_length: int,
    burn_in_steps: int,
) -> list[tuple[list[dict], int]]:
    length = max(32, min(256, int(sequence_length)))
    burn = max(0, min(min(64, length - 1), int(burn_in_steps)))
    episodes: dict[tuple[str, str], list[dict]] = {}
    for record in records:
        episode_id = str(record["episode_id"])
        sequence_id = str(record.get("_sequence_id", episode_id))
        episodes.setdefault((episode_id, sequence_id), []).append(record)
    windows: list[tuple[list[dict], int]] = []
    for episode_records in episodes.values():
        for continuous_part in _continuous_trajectory_parts(episode_records):
            for start in range(0, len(continuous_part), length):
                context_start = max(0, start - burn)
                train_end = min(len(continuous_part), start + length)
                lookahead = max(
                    (int(item.get("n_steps", 1)) for item in continuous_part[start:train_end]),
                    default=1,
                )
                end = min(len(continuous_part), train_end + lookahead)
                window = continuous_part[context_start:end]
                if window:
                    windows.append((window, start - context_start))
    return windows



def evaluate_model_records(np, model: dict, items: list[dict]) -> dict[str, float]:
    if not items:
        return {
            "accuracy": 0.0, "human_log_likelihood": 0.0,
            "progress_accuracy": 0.0, "return_ranking_accuracy": 0.0,
            "q_mae": 0.0, "q_calibration_error": 1.0,
            "value_mae": 0.0, "safety_error": 1.0, "score": -0.20,
            "episode_count": 0.0, "success_episode_rate": 0.0,
            "average_survival_steps": 0.0, "actual_cumulative_score": 0.0,
            "episode_test_score": 0.0,
        }
    human_total = 0
    human_correct = 0
    human_log_probabilities = []
    q_errors = []
    value_errors = []
    safety_errors = []
    progress_pairs = 0
    progress_correct = 0
    return_pairs = 0
    return_correct = 0
    current_sequence = None
    previous_step = None
    hidden = None
    episode_outputs = []
    episode_tests = []

    def finish_episode():
        nonlocal progress_pairs, progress_correct, return_pairs, return_correct, episode_outputs
        if len(episode_outputs) >= 2:
            for left in range(0, len(episode_outputs) - 4, max(1, len(episode_outputs) // 12)):
                right = min(len(episode_outputs) - 1, left + max(4, len(episode_outputs) // 4))
                a, b = episode_outputs[left], episode_outputs[right]
                task_difference = b["task_return"] - a["task_return"]
                if a["source"] == "human" and b["source"] == "human":
                    progress_pairs += 1
                    progress_correct += int(b["progress"] > a["progress"])
                elif abs(task_difference) > 0.10:
                    progress_pairs += 1
                    progress_correct += int(
                        (b["progress"] > a["progress"]) == (task_difference > 0.0)
                    )
                if abs(b["return"] - a["return"]) > 0.05:
                    return_pairs += 1
                    return_correct += int((b["value"] > a["value"]) == (b["return"] > a["return"]))
        if episode_outputs:
            task_total = sum(float(item["task_reward"]) for item in episode_outputs)
            safety_total = sum(float(item["safety_penalty"]) for item in episode_outputs)
            trajectory_class = str(episode_outputs[-1].get("trajectory_class", ""))
            source = str(episode_outputs[-1].get("source", ""))
            actual_success = trajectory_class == "successful_ai" or (
                source == "human" and task_total > max(0.05, safety_total * 0.50)
            )
            episode_tests.append({
                "success": float(actual_success),
                "survival": float(len(episode_outputs)),
                "score": float(task_total),
            })
        episode_outputs = []

    for record in sorted(
        items,
        key=lambda item: (
            str(item["episode_id"]),
            str(item.get("_sequence_id", item["episode_id"])),
            int(item["step"]),
        ),
    ):
        episode_id = str(record["episode_id"])
        sequence_key = (episode_id, str(record.get("_sequence_id", episode_id)))
        current_step = int(record["step"])
        if sequence_key != current_sequence or (
            previous_step is not None and current_step != previous_step + 1
        ):
            finish_episode()
            current_sequence = sequence_key
            hidden = np.zeros(int(model["hidden_size"]), dtype=np.float32)
        frames, actions, durations = decode_temporal_state(record["state"])
        hidden = recurrent_model_step(np, model, frames[-1], hidden, actions[-1], durations[-1])
        probabilities, q_values, _ = factorized_action_outputs_from_hidden(np, model, hidden)
        action_id = int(record["action"])
        probability = max(1e-9, float(probabilities[action_id]))
        greedy_match = int(int(np.argmax(probabilities)) == action_id)
        if record["source"] == "human":
            human_total += 1
            human_correct += greedy_match
            human_log_probabilities.append(math.log(probability))
        critic_prediction = q_values[:, action_id]
        critic_target = np.asarray(
            [
                float(record.get("n_task_return", record.get("task_reward", 0.0))),
                float(record.get("n_exploration_return", record.get("exploration_reward", 0.0))),
                float(record.get("n_safety_return", record.get("safety_penalty", 0.0))),
            ],
            dtype=np.float32,
        )
        q_data = float(combined_critic_values(np, critic_prediction[:, None])[0])
        value = float(hidden @ model["value_w"][:, 0] + model["value_b"][0])
        target_return = float(record.get("n_return", record.get("reward", 0.0)))
        value_errors.append(abs(q_data - value))
        q_errors.append(float(np.mean(np.abs(critic_prediction - critic_target))))
        safe_target = max(0.0, min(1.0, float(record.get("n_safety_return", 0.0)) / 4.0))
        safe_prediction = predict_safety_probability(np, model, hidden)
        safety_errors.append(abs(safe_prediction - safe_target))
        episode_outputs.append({
            "source": str(record["source"]),
            "trajectory_class": str(record.get("trajectory_class", "")),
            "progress": predict_progress(np, model, hidden),
            "task_return": float(record.get("n_task_return", record.get("task_reward", 0.0))),
            "return": target_return,
            "value": q_data,
            "action_probability": probability,
            "greedy_match": float(greedy_match),
            "task_reward": float(record.get("task_reward", 0.0)),
            "safety_penalty": float(record.get("safety_penalty", 0.0)),
        })
        previous_step = current_step
    finish_episode()
    accuracy = human_correct / max(1, human_total)
    mean_log = sum(human_log_probabilities) / max(1, len(human_log_probabilities))
    random_log = math.log(max(2, len(model["action_factors"])))
    normalized_log_likelihood = (
        max(0.0, min(1.0, 1.0 + mean_log / random_log))
        if human_log_probabilities else 0.0
    )
    progress_accuracy = progress_correct / max(1, progress_pairs)
    return_ranking_accuracy = return_correct / max(1, return_pairs)
    q_mae = sum(q_errors) / max(1, len(q_errors))
    q_calibration_error = max(0.0, min(1.0, q_mae / 3.0))
    value_mae = sum(value_errors) / max(1, len(value_errors))
    safety_error = sum(safety_errors) / max(1, len(safety_errors))
    episode_count = len(episode_tests)
    success_episode_rate = (
        sum(item["success"] for item in episode_tests) / episode_count
        if episode_count else 0.0
    )
    average_survival_steps = (
        sum(item["survival"] for item in episode_tests) / episode_count
        if episode_count else 0.0
    )
    actual_cumulative_score = (
        sum(item["score"] for item in episode_tests) / episode_count
        if episode_count else 0.0
    )
    episode_test_score = (
        0.50 * success_episode_rate
        + 0.25 * math.tanh(average_survival_steps / 96.0)
        + 0.25 * math.tanh(actual_cumulative_score / 3.0)
    ) if episode_tests else 0.0
    score = (
        0.55 * episode_test_score
        + 0.15 * return_ranking_accuracy
        + 0.10 * progress_accuracy
        + 0.10 * normalized_log_likelihood
        + 0.05 * accuracy
        - 0.025 * q_calibration_error
        - 0.025 * safety_error
    )
    return {
        "accuracy": float(accuracy),
        "human_log_likelihood": float(normalized_log_likelihood),
        "progress_accuracy": float(progress_accuracy),
        "return_ranking_accuracy": float(return_ranking_accuracy),
        "q_mae": float(q_mae),
        "q_calibration_error": float(q_calibration_error),
        "value_mae": float(value_mae),
        "safety_error": float(safety_error),
        "score": float(score),
        "episode_count": float(episode_count),
        "success_episode_rate": float(success_episode_rate),
        "average_survival_steps": float(average_survival_steps),
        "actual_cumulative_score": float(actual_cumulative_score),
        "episode_test_score": float(episode_test_score),
    }

def train_model(
    np,
    model: dict,
    dataset: dict,
    target_model: dict,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    stop_event: threading.Event | None,
    config: dict | None = None,
) -> dict:
    if not dataset or not dataset.get("train"):
        return {"samples": 0, "accuracy": 0.0, "value_mae": 0.0, "validation_accuracy": 0.0, "validation_value_mae": 0.0}
    config = config or DEFAULT_CONFIG
    records = list(dataset["train"])
    validation = list(dataset.get("validation", []))
    skills = list(dataset.get("skills", []))[:SKILL_HEAD_SIZE]
    human_records = [record for record in records if record["source"] == "human"]
    ai_records = [record for record in records if record["source"] == "ai"]
    successful_ai = [record for record in ai_records if record.get("trajectory_class") == "successful_ai"]
    failed_ai = [record for record in ai_records if record.get("trajectory_class") == "failed_ai"]
    epochs = max(1, min(40, int(epochs)))
    batch_size = max(8, min(8192, int(batch_size)))
    lr = max(1e-6, min(0.02, float(learning_rate)))
    bc_weight = max(0.1, min(4.0, float(config.get("behavior_cloning_weight", 1.4))))
    expectile = max(0.5, min(0.95, float(config.get("iql_expectile", 0.80))))
    temperature = max(0.25, min(10.0, float(config.get("iql_temperature", 1.5))))
    progress_margin = max(0.01, min(1.0, float(config.get("progress_margin", PROGRESS_RANK_MARGIN))))
    progress_weight = max(0.0, min(4.0, float(config.get("progress_pair_weight", 1.0))))
    skill_weight = max(0.0, min(2.0, float(config.get("skill_policy_weight", 0.35))))
    sequence_length = max(32, min(256, int(config.get("sequence_length", TRAIN_SEQUENCE_LENGTH))))
    burn_in = max(4, min(min(64, sequence_length - 1), int(config.get("burn_in_steps", TRAIN_BURN_IN_STEPS))))
    cql_weight = 0.02
    warmup_steps = max(1, int(config.get("learning_rate_warmup_steps", OPTIMIZER_WARMUP_STEPS_DEFAULT)))
    cosine_steps = max(16, int(config.get("learning_rate_cosine_steps", OPTIMIZER_COSINE_STEPS_DEFAULT)))
    weight_decay = max(0.0, min(0.1, float(config.get("weight_decay", OPTIMIZER_WEIGHT_DECAY_DEFAULT))))
    progress_reward_scale = max(0.05, min(4.0, float(config.get("progress_reward_scale", 1.0))))
    heuristic_task_aux_weight = max(0.0, min(0.5, float(config.get("heuristic_task_aux_weight", 0.12))))
    rng = np.random.default_rng(
        VISUAL_INITIALIZATION_SEED
        + int(model.get("training_rounds", 0)) * 1009
        + len(records)
    )
    _ensure_optimizer_state(np, model)
    last_effective_lr = 0.0
    policy_loss_total = q_loss_total = value_loss_total = progress_loss_total = skill_loss_total = 0.0
    safety_loss_total = world_loss_total = 0.0
    updates = 0
    windows_per_batch = max(1, batch_size // sequence_length)

    runtime_tier = str(model.get("runtime_tier", "low_numpy"))
    if runtime_tier == "low_numpy":
        pretrain_limit = min(96, max(32, len(records) // 256))
    elif runtime_tier == "high_directml":
        pretrain_limit = min(384, max(96, len(records) // 96))
    else:
        pretrain_limit = min(192, max(64, len(records) // 160))
    visual_pretraining = pretrain_visual_encoder(
        np,
        model,
        records,
        lr,
        stop_event,
        pretrain_limit,
    )

    def forward_window(window: list[dict], encoder_model: dict, with_cache: bool):
        hidden = np.zeros(int(encoder_model["hidden_size"]), dtype=np.float32)
        encoded = []
        previous_step: int | None = None
        for record in window:
            current_step = int(record["step"])
            if previous_step is not None and current_step != previous_step + 1:
                hidden.fill(0.0)
            frames, actions, durations = decode_temporal_state(record["state"])
            current_frame = frames[-1]
            previous_action = actions[-1]
            previous_duration = durations[-1]
            if with_cache:
                hidden, caches = recurrent_model_step(
                    np, encoder_model, current_frame, hidden,
                    previous_action, previous_duration, return_cache=True,
                )
            else:
                hidden = recurrent_model_step(
                    np, encoder_model, current_frame, hidden,
                    previous_action, previous_duration, return_cache=False,
                )
                caches = None
            encoded.append((hidden.copy(), caches))
            previous_step = current_step
        return encoded

    def backpropagate_window(gradients, encoded, hidden_gradients, first_train: int, train_end: int):
        carry = np.zeros(int(model["hidden_size"]), dtype=np.float32)
        for position in range(train_end - 1, first_train - 1, -1):
            _, carry = _backprop_temporal_encoder(
                np, model, encoded[position][1], hidden_gradients[position] + carry,
                lr * 0.35, gradients, return_initial_gradient=True,
            )

    def apply_gradients(gradients, divisor: int):
        nonlocal last_effective_lr
        if divisor <= 0:
            return
        for gradient in gradients.values():
            gradient /= divisor
        active = [gradient for gradient in gradients.values() if np.any(gradient)]
        if active:
            clip_gradients_by_global_norm(np, active, 8.0)
            last_effective_lr = _adam_apply(
                np,
                model,
                gradients,
                lr,
                warmup_steps,
                cosine_steps,
                weight_decay,
            )
            _synchronize_quantized_conv_weights(np, model)

    bc_epochs = max(1, epochs // 3) if human_records else 0
    bc_windows = sequence_training_windows(human_records, sequence_length, burn_in)
    for _ in range(bc_epochs):
        rng.shuffle(bc_windows)
        for group_start in range(0, len(bc_windows), windows_per_batch):
            raise_if_cancelled(stop_event)
            gradients = _training_gradient_buffer(np, model)
            trained = 0
            for window, first_train in bc_windows[group_start:group_start + windows_per_batch]:
                train_end = min(len(window), first_train + sequence_length)
                if train_end <= first_train:
                    continue
                encoded = forward_window(window, model, True)
                hidden_matrix = np.stack([item[0] for item in encoded[first_train:train_end]], axis=0)
                probabilities, _, _ = _batch_model_outputs_from_hidden(np, model, hidden_matrix)
                hidden_gradients = [np.zeros(int(model["hidden_size"]), dtype=np.float32) for _ in window]
                for local_index, record in enumerate(window[first_train:train_end]):
                    position = first_train + local_index
                    action_id = int(record["action"])
                    quality, _, _ = human_training_signal(
                        float(record.get("n_task_return", record["task_reward"]))
                    )
                    episode_quality = max(
                        0.0,
                        min(1.0, float(record.get("episode_quality", 0.50))),
                    )
                    quality *= 0.15 + 0.85 * episode_quality
                    duration_index = _record_duration_index(record)
                    loss, hidden_gradient = _train_factor_policy(
                        np, model, encoded[position][0], model["action_factors"][action_id], lr,
                        bc_weight * quality, action_id=action_id, gradients=gradients,
                        probabilities=probabilities[local_index], duration_index=duration_index,
                    )
                    hidden_gradients[position] += hidden_gradient
                    policy_loss_total += loss
                    label = skill_label_for_position(window, position, skills) if skills else None
                    if label is not None:
                        skill_loss, skill_gradient = _train_skill_head(
                            np, model, encoded[position][0], label,
                            float(record.get("n_task_return", record.get("task_reward", 0.0))),
                            skill_weight * quality, gradients,
                        )
                        hidden_gradients[position] += skill_gradient
                        skill_loss_total += skill_loss
                    trained += 1
                    updates += 1
                if train_end - first_train >= 5:
                    ordered = _ordered_progress_positions(
                        window,
                        first_train,
                        train_end - 1,
                    )
                    if ordered is not None:
                        low_position, high_position, pair_quality = ordered
                        progress_loss, low_gradient, high_gradient = _train_progress_pair(
                            np,
                            model,
                            encoded[low_position][0],
                            encoded[high_position][0],
                            progress_margin,
                            progress_weight * pair_quality,
                            gradients,
                        )
                        hidden_gradients[low_position] += low_gradient
                        hidden_gradients[high_position] += high_gradient
                        progress_loss_total += progress_loss
                backpropagate_window(gradients, encoded, hidden_gradients, first_train, train_end)
            apply_gradients(gradients, trained)

    iql_epochs = max(1, epochs - bc_epochs)
    all_windows = sequence_training_windows(records, sequence_length, burn_in)
    for epoch in range(iql_epochs):
        rng.shuffle(all_windows)
        for group_start in range(0, len(all_windows), windows_per_batch):
            raise_if_cancelled(stop_event)
            gradients = _training_gradient_buffer(np, model)
            trained = 0
            for window, first_train in all_windows[group_start:group_start + windows_per_batch]:
                train_end = min(len(window), first_train + sequence_length)
                if train_end <= first_train:
                    continue
                encoded = forward_window(window, model, True)
                target_encoded = forward_window(window, target_model, False)
                train_items = window[first_train:train_end]
                hidden_matrix = np.stack([item[0] for item in encoded[first_train:train_end]], axis=0)
                probabilities, q_values, values = _batch_model_outputs_from_hidden(np, model, hidden_matrix)
                hidden_gradients = [np.zeros(int(model["hidden_size"]), dtype=np.float32) for _ in window]
                step_to_position = {
                    int(item["step"]): index
                    for index, item in enumerate(window)
                }
                for local_index, record in enumerate(train_items):
                    position = first_train + local_index
                    hidden = hidden_matrix[local_index]
                    action_id = int(record["action"])
                    duration_index = _record_duration_index(record)
                    observed_critics = q_values[local_index, :, action_id]
                    q_data = float(combined_critic_values(np, observed_critics[:, None], config)[0])
                    value = float(values[local_index])
                    _, _, value_weight = (
                        human_training_signal(
                            float(record.get("n_task_return", record["task_reward"]))
                        )
                        if record["source"] == "human"
                        else (1.0, 0.0, 1.0)
                    )
                    value_loss, value_hidden_gradient = _train_value_head(
                        np, model, hidden, q_data, value, expectile, value_weight, gradients,
                    )
                    future_step = int(record["step"]) + int(record.get("n_steps", 1))
                    future_position = step_to_position.get(future_step)
                    has_future = (
                        not bool(record["n_done"])
                        and future_position is not None
                        and 0 <= future_position < len(target_encoded)
                    )
                    stored_task_auxiliary = float(
                        record.get("n_task_return", record.get("task_reward", 0.0))
                    )
                    progress_target = 0.0
                    if future_position is not None and 0 <= future_position < len(encoded):
                        progress_target = (
                            predict_progress(np, model, encoded[future_position][0])
                            - predict_progress(np, model, hidden)
                        )
                    task_return_anchor = (
                        (1.0 - heuristic_task_aux_weight) * stored_task_auxiliary
                        + 0.35 * progress_reward_scale * progress_target
                    )
                    critic_targets = np.asarray(
                        [
                            task_return_anchor,
                            float(record.get("n_exploration_return", record.get("exploration_reward", 0.0))),
                            float(record.get("n_safety_return", record.get("safety_penalty", 0.0))),
                        ],
                        dtype=np.float32,
                    )
                    if has_future:
                        online_future_hidden = encoded[future_position][0]
                        target_future_hidden = target_encoded[future_position][0]
                        critic_targets += float(record["discount_power"]) * critic_bootstrap_values(
                            np,
                            model,
                            online_future_hidden,
                            config,
                            target_model,
                            target_future_hidden,
                        )
                    critic_targets[TASK_CRITIC] = np.clip(critic_targets[TASK_CRITIC], -3.0, 3.0)
                    critic_targets[EXPLORATION_CRITIC] = np.clip(critic_targets[EXPLORATION_CRITIC], 0.0, 3.0)
                    critic_targets[SAFETY_CRITIC] = np.clip(critic_targets[SAFETY_CRITIC], 0.0, 4.0)
                    priority_weight = min(3.0, max(0.2, float(record["priority"]) / 3.0))
                    q_loss, q_hidden_gradient = _train_factor_q(
                        np, model, hidden, action_id, critic_targets, lr, priority_weight,
                        gradients=gradients, q_values=q_values[local_index], cql_weight=cql_weight,
                        duration_index=duration_index,
                    )
                    safety_target = max(
                        0.0,
                        min(1.0, float(record.get("n_safety_return", 0.0)) / 4.0),
                    )
                    safety_loss, safety_hidden_gradient = _train_safety_head(
                        np, model, hidden, safety_target, priority_weight, gradients,
                    )
                    next_step_position = step_to_position.get(int(record["step"]) + 1)
                    world_next_hidden = (
                        encoded[next_step_position][0]
                        if next_step_position is not None and not bool(record["done"])
                        else None
                    )
                    world_target_next_hidden = (
                        target_encoded[next_step_position][0]
                        if next_step_position is not None and not bool(record["done"])
                        else None
                    )
                    one_step_progress = (
                        predict_progress(np, model, world_next_hidden)
                        - predict_progress(np, model, hidden)
                        if world_next_hidden is not None
                        else 0.0
                    )
                    external_task_target = float(record.get("task_reward", 0.0))
                    world_task_target = float(np.clip(
                        external_task_target + 0.10 * one_step_progress,
                        -1.0,
                        1.0,
                    ))
                    world_loss, world_hidden_gradient = train_world_model_transition(
                        np,
                        model,
                        hidden,
                        world_next_hidden,
                        action_id,
                        (
                            world_task_target,
                            float(record.get("exploration_reward", 0.0)),
                            float(record.get("safety_penalty", 0.0)),
                        ),
                        bool(record["done"]),
                        priority_weight,
                        gradients,
                        target_model=target_model,
                        target_next_hidden=world_target_next_hidden,
                        duration_index=duration_index,
                    )
                    reward_model_loss, reward_model_hidden_gradient = train_reward_model_transition(
                        np,
                        model,
                        hidden,
                        world_next_hidden,
                        record,
                        priority_weight,
                        gradients,
                    )
                    world_hidden_gradient += reward_model_hidden_gradient
                    world_loss += reward_model_loss
                    advantage = q_data - value
                    actor_weight = min(
                        20.0,
                        math.exp(max(-5.0, min(3.0, advantage / temperature))),
                    )
                    if record["source"] == "human":
                        trajectory_scale = 0.20 + 0.80 * max(
                            0.0,
                            min(1.0, float(record.get("episode_quality", 0.50))),
                        )
                    elif record.get("trajectory_class") == "successful_ai":
                        trajectory_scale = 0.45
                    elif record.get("trajectory_class") == "failed_ai":
                        trajectory_scale = 0.04
                    else:
                        trajectory_scale = 0.08
                    safe_scale = max(0.05, 1.0 - 0.55 * float(record["safety_penalty"]))
                    policy_weight = bc_weight * actor_weight * trajectory_scale * safe_scale * min(2.0, max(0.5, float(record["priority"]) / 2.0))
                    policy_loss, policy_hidden_gradient = _train_factor_policy(
                        np, model, hidden, model["action_factors"][action_id], lr, policy_weight,
                        action_id=action_id, gradients=gradients, probabilities=probabilities[local_index],
                        duration_index=duration_index,
                    )
                    hidden_gradients[position] += (
                        policy_hidden_gradient
                        + q_hidden_gradient
                        + value_hidden_gradient
                        + safety_hidden_gradient
                        + world_hidden_gradient
                    )
                    policy_loss_total += policy_loss
                    q_loss_total += q_loss
                    value_loss_total += value_loss
                    safety_loss_total += safety_loss
                    world_loss_total += world_loss
                    trained += 1
                    updates += 1
                if train_end - first_train >= 5:
                    ordered = _ordered_progress_positions(
                        window,
                        first_train,
                        train_end - 1,
                    )
                    if ordered is not None:
                        low_position, high_position, pair_quality = ordered
                        progress_loss, low_gradient, high_gradient = _train_progress_pair(
                            np,
                            model,
                            encoded[low_position][0],
                            encoded[high_position][0],
                            progress_margin,
                            progress_weight * pair_quality,
                            gradients,
                        )
                        hidden_gradients[low_position] += low_gradient
                        hidden_gradients[high_position] += high_gradient
                        progress_loss_total += progress_loss
                backpropagate_window(gradients, encoded, hidden_gradients, first_train, train_end)
            apply_gradients(gradients, trained)
        soft_update_target_model(np, target_model, model, 0.18 if epoch == iql_epochs - 1 else 0.05)

    # Cross-trajectory ranking anchors the progress scale: successful endings
    # must rank above failed endings, independently of OCR or screen darkness.
    episode_endings: dict[str, dict] = {}
    for record in sorted(records, key=lambda item: (str(item["episode_id"]), int(item["step"]))):
        episode_endings[str(record["episode_id"])] = record
    successful_endings = [
        record
        for record in episode_endings.values()
        if record.get("trajectory_class") == "successful_ai"
    ]
    failed_endings = [
        record
        for record in episode_endings.values()
        if record.get("trajectory_class") == "failed_ai"
    ]
    if not successful_endings:
        successful_endings = [
            record
            for record in episode_endings.values()
            if record.get("trajectory_class") == "human"
            and float(record.get("episode_quality", 0.50)) >= 0.65
        ]
    cross_pair_limit = min(64, len(successful_endings) * len(failed_endings))
    if cross_pair_limit > 0:
        cross_gradients = _training_gradient_buffer(np, model)
        cross_pairs = 0
        for pair_index in range(cross_pair_limit):
            raise_if_cancelled(stop_event)
            high_record = successful_endings[pair_index % len(successful_endings)]
            low_record = failed_endings[(pair_index * 7) % len(failed_endings)]
            low_hidden, low_caches = _latest_temporal_hidden(
                np,
                model,
                low_record["state"],
                return_cache=True,
            )
            high_hidden, high_caches = _latest_temporal_hidden(
                np,
                model,
                high_record["state"],
                return_cache=True,
            )
            pair_quality = min(
                _record_progress_stability(low_record),
                _record_progress_stability(high_record),
            )
            pair_loss, low_gradient, high_gradient = _train_progress_pair(
                np,
                model,
                low_hidden,
                high_hidden,
                progress_margin,
                progress_weight * max(0.35, pair_quality),
                cross_gradients,
            )
            _backprop_temporal_encoder(
                np,
                model,
                low_caches,
                low_gradient,
                lr * 0.25,
                cross_gradients,
            )
            _backprop_temporal_encoder(
                np,
                model,
                high_caches,
                high_gradient,
                lr * 0.25,
                cross_gradients,
            )
            progress_loss_total += pair_loss
            cross_pairs += 1
            if cross_pairs % 16 == 0:
                apply_gradients(cross_gradients, 32)
                cross_gradients = _training_gradient_buffer(np, model)
        if cross_pairs % 16:
            apply_gradients(cross_gradients, 2 * (cross_pairs % 16))

    train_metrics = evaluate_model_records(np, model, records[:min(2048, len(records))])
    validation_metrics = evaluate_model_records(np, model, validation)
    model["trained_samples"] = int(model.get("trained_samples", 0)) + len(records)
    model["training_rounds"] = int(model.get("training_rounds", 0)) + 1
    model["validation_score"] = float(validation_metrics["score"])
    return {
        "samples": len(records),
        "accuracy": train_metrics["accuracy"],
        "value_mae": train_metrics["q_mae"],
        "validation_accuracy": validation_metrics["accuracy"],
        "validation_value_mae": validation_metrics["q_mae"],
        "validation_score": validation_metrics["score"],
        "validation_human_log_likelihood": validation_metrics["human_log_likelihood"],
        "validation_progress_accuracy": validation_metrics["progress_accuracy"],
        "validation_return_ranking_accuracy": validation_metrics["return_ranking_accuracy"],
        "validation_safety_error": validation_metrics["safety_error"],
        "validation_q_calibration_error": validation_metrics["q_calibration_error"],
        "validation_episode_count": validation_metrics["episode_count"],
        "validation_success_episode_rate": validation_metrics["success_episode_rate"],
        "validation_average_survival_steps": validation_metrics["average_survival_steps"],
        "validation_actual_cumulative_score": validation_metrics["actual_cumulative_score"],
        "validation_episode_test_score": validation_metrics["episode_test_score"],
        "policy_loss": policy_loss_total / max(1, updates),
        "q_loss": q_loss_total / max(1, updates),
        "safety_loss": safety_loss_total / max(1, updates),
        "world_model_loss": world_loss_total / max(1, updates),
        "visual_pretraining_loss": float(visual_pretraining["loss"]),
        "visual_pretraining_steps": int(visual_pretraining["steps"]),
        "iql_value_loss": value_loss_total / max(1, updates),
        "progress_loss": progress_loss_total / max(1, len(bc_windows) * max(1, bc_epochs)),
        "skill_loss": skill_loss_total / max(1, updates),
        "iql_value_mae": train_metrics["value_mae"],
        "validation_iql_value_mae": validation_metrics["value_mae"],
        "episodes": int(dataset.get("episodes", 0)),
        "human_samples": len(human_records),
        "successful_ai_samples": len(successful_ai),
        "ai_samples": len(ai_records),
        "skills": len(skills),
        "bc_epochs": bc_epochs,
        "iql_epochs": iql_epochs,
        "failed_ai_samples": len(failed_ai),
        "optimizer_step": int(model.get("optimizer_step", 0)),
        "effective_learning_rate": float(last_effective_lr),
    }





def runtime_self_check(np) -> None:
    if np is None or not supported_numpy_version(getattr(np, "__version__", "0")):
        raise RuntimeError("NumPy 运行组件版本无效")
    current = bytes((index * 17 + 31) % 256 for index in range(FEATURE_WIDTH * FEATURE_HEIGHT))
    previous = bytes((index * 13 + 19) % 256 for index in range(FEATURE_WIDTH * FEATURE_HEIGHT))
    blue = bytes((128 + (index % 9) - 4) % 256 for index in range(COLOR_PIXELS))
    red = bytes((128 + (index % 7) - 3) % 256 for index in range(COLOR_PIXELS))
    feature = make_feature(current, previous, blue, red)
    state = build_temporal_state([feature], [3], [0.23])
    frames, actions, durations = decode_temporal_state(state)
    if len(frames) != TEMPORAL_FRAMES or actions[-1] != 3 or abs(durations[-1] - 0.23) > 1e-5:
        raise RuntimeError("单帧轨迹状态自检失败")
    sequence_probe = [
        {
            "episode_id": "sequence-probe",
            "step": probe_step,
            "source": "human",
            "trajectory_class": "human",
            "priority": 1.0,
            "n_steps": 1,
        }
        for probe_step in (100, 101, 104, 105)
    ]
    contiguous_probe = contiguous_trajectory_records(
        sequence_probe, 16, 96, 32, 12, np.random.default_rng(7)
    )
    for probe_window, _ in sequence_training_windows(contiguous_probe, 96, 32):
        if any(
            int(probe_window[index]["step"]) != int(probe_window[index - 1]["step"]) + 1
            for index in range(1, len(probe_window))
        ):
            raise RuntimeError("连续轨迹采样自检失败")
    ocr_frame = bytearray(FEATURE_WIDTH * FEATURE_HEIGHT)
    ocr_x = 4
    for character in "42":
        template = _OCR_DIGIT_TEMPLATES[int(character)]
        for template_y, row in enumerate(template):
            for template_x, cell in enumerate(row):
                if cell == "1":
                    for offset_y in range(2):
                        for offset_x in range(2):
                            ocr_frame[
                                (2 + template_y * 2 + offset_y) * FEATURE_WIDTH
                                + ocr_x + template_x * 2 + offset_x
                            ] = 255
        ocr_x += 12
    recognized_score, recognized_confidence = recognize_hud_score(bytes(ocr_frame))
    if recognized_score != 42 or recognized_confidence < 0.72:
        raise RuntimeError("HUD OCR 分数识别自检失败")
    actions_list = universal_actions()[:8]
    legacy_payload = bytearray(TEMPORAL_STATE_MAGIC)
    legacy_payload.extend(struct.pack("<BB", 1, 1))
    legacy_payload.extend(struct.pack("<I", len(feature)))
    legacy_payload.extend(feature)
    legacy_payload.extend(struct.pack("<i", 3))
    legacy_payload.extend(struct.pack("<f", 0.23))
    legacy_state = zlib.compress(bytes(legacy_payload), 6)
    legacy_frames, legacy_actions, legacy_durations = decode_temporal_state(legacy_state)
    migrated_state = _normalize_temporal_action_schema(legacy_state, len(actions_list))
    if (
        len(legacy_frames) != TEMPORAL_FRAMES
        or legacy_actions[-1] != 3
        or abs(legacy_durations[-1] - 0.23) > 1e-5
        or migrated_state == legacy_state
    ):
        raise RuntimeError("旧 AGT3 单帧经验迁移自检失败")
    model = initialize_model(np, MODEL_INPUT_DIM, 64, len(actions_list))
    model["action_factors"] = action_factor_matrix(np, actions_list)
    model["action_key_multihot"] = action_key_multihot_matrix(np, actions_list)
    model["action_button_multihot"] = action_button_multihot_matrix(np, actions_list)
    model["action_signatures"] = [action_signature(action) for action in actions_list]
    model["action_hash"] = actions_hash(actions_list)
    probabilities, q_values, hidden = factorized_action_outputs(np, model, state)
    expected = action_space_size(len(actions_list))
    if (
        probabilities.shape != (expected,)
        or q_values.shape != (VALUE_HEAD_COUNT, expected)
        or hidden.shape != (model["hidden_size"],)
        or model["policy_action_w"].shape != (model["hidden_size"], expected)
        or model["q_action_w"].shape != (Q_TWIN_COUNT, VALUE_HEAD_COUNT, model["hidden_size"], expected)
        or model["action_embedding"].shape != (expected, ACTION_EMBEDDING_SIZE)
        or model["duration_embedding"].shape != (DURATION_HEAD_SIZE, DURATION_EMBEDDING_SIZE)
        or model["safety_w"].shape != (model["hidden_size"], 1)
        or model["world_encoder_w"].shape != (WORLD_MODEL_MEMBERS, model["hidden_size"], WORLD_LATENT_SIZE)
        or model["world_latent_to_hidden_w"].shape != (WORLD_MODEL_MEMBERS, WORLD_LATENT_SIZE, model["hidden_size"])
        or model["reward_model_w"].shape != (REWARD_MODEL_MEMBERS, model["hidden_size"], REWARD_MODEL_OUTPUTS)
        or model["value_w"].shape != (model["hidden_size"], 1)
        or not np.isfinite(probabilities).all()
        or abs(float(probabilities.sum()) - 1.0) > 1e-4
    ):
        raise RuntimeError("CNN+GRU+精确动作残差+IQL 模型自检失败")
    spatial_probe = bytes(BASE_FEATURE_DIM) + bytes(
        (index * 17 + index // max(1, SPATIAL_FULL_WIDTH)) & 0xFF
        for index in range(SPATIAL_CONTEXT_DIM)
    )
    spatial_features = _spatial_branch_features(np, spatial_probe)
    if (
        spatial_features.shape != (SPATIAL_BRANCH_FEATURE_DIM,)
        or not np.isfinite(spatial_features).all()
        or not np.any(np.abs(spatial_features) > 1e-5)
    ):
        raise RuntimeError("全画面/HUD/鼠标局部空间分支自检失败")
    twin_outputs = _batch_twin_q_outputs_from_hidden(
        np, model, np.zeros((1, model["hidden_size"]), dtype=np.float32)
    )
    _, conservative_outputs, _ = _batch_model_outputs_from_hidden(
        np, model, np.zeros((1, model["hidden_size"]), dtype=np.float32)
    )
    if (
        twin_outputs.shape != (1, Q_TWIN_COUNT, VALUE_HEAD_COUNT, expected)
        or not np.allclose(conservative_outputs, twin_outputs.min(axis=1), atol=1e-6)
    ):
        raise RuntimeError("Twin Q 保守目标自检失败")
    optimizer_probe = initialize_model(np, MODEL_INPUT_DIM, 8, 1)
    optimizer_gradients = _training_gradient_buffer(np, optimizer_probe)
    optimizer_gradients["progress_w"].fill(0.01)
    effective_learning_rate = _adam_apply(
        np, optimizer_probe, optimizer_gradients, 0.001, 8, 32, 0.0001
    )
    if (
        int(optimizer_probe.get("optimizer_step", 0)) != 1
        or not 0.0 < effective_learning_rate < 0.001
        or not np.any(optimizer_probe["optimizer_m"])
        or not np.any(optimizer_probe["optimizer_v"])
    ):
        raise RuntimeError("持久 AdamW 与预热/余弦计划自检失败")
    hidden_cached, caches = recurrent_model_step(
        np,
        model,
        frames[-1],
        np.zeros(model["hidden_size"], dtype=np.float32),
        actions[-1],
        durations[-1],
        return_cache=True,
    )
    gradients = _training_gradient_buffer(np, model)
    _, policy_hidden = _train_factor_policy(
        np, model, hidden_cached, model["action_factors"][0], 0.001, 1.0,
        action_id=0, gradients=gradients,
    )
    _backprop_temporal_encoder(np, model, caches, policy_hidden, 0.00025, gradients)
    if (
        not np.any(np.abs(gradients["frame_proj"]) > 0.0)
        or not np.any(np.abs(gradients["Wz"]) > 0.0)
        or not np.any(np.abs(gradients["conv_master_w"]) > 0.0)
        or not np.any(np.abs(gradients["conv2_pointwise_w"]) > 0.0)
        or not np.any(np.abs(gradients["conv3_pointwise_w"]) > 0.0)
        or not np.any(np.abs(gradients["action_embedding"]) > 0.0)
        or not np.any(np.abs(gradients["duration_embedding"]) > 0.0)
    ):
        raise RuntimeError("三层视觉网络与GRU反向传播自检失败")
    recurrent_first = recurrent_model_step(
        np,
        model,
        feature,
        np.zeros(model["hidden_size"], dtype=np.float32),
        0,
        0.07,
    )
    recurrent_second = recurrent_model_step(
        np,
        model,
        feature,
        recurrent_first,
        1,
        0.13,
    )
    if recurrent_first.shape != recurrent_second.shape or np.allclose(
        recurrent_second,
        recurrent_first,
    ):
        raise RuntimeError("整局循环记忆自检失败")
    critic_probe = np.stack(
        (
            np.ones(expected, dtype=np.float32),
            np.full(expected, 0.5, dtype=np.float32),
            np.full(expected, 0.25, dtype=np.float32),
        )
    )
    combined_probe = combined_critic_values(np, critic_probe, DEFAULT_CONFIG)
    if not np.allclose(
        combined_probe,
        1.0
        + float(DEFAULT_CONFIG["exploration_reward_weight"]) * 0.5
        - float(DEFAULT_CONFIG["safety_penalty_weight"]) * 0.25,
    ):
        raise RuntimeError("任务/探索/安全 critic 组合自检失败")
    auxiliary_gradients = _training_gradient_buffer(np, model)
    safety_loss, _ = _train_safety_head(
        np, model, recurrent_first, 0.75, 1.0, auxiliary_gradients
    )
    world_loss, _ = train_world_model_transition(
        np,
        model,
        recurrent_first,
        recurrent_second,
        0,
        (0.25, 0.10, 0.20),
        False,
        1.0,
        auxiliary_gradients,
    )
    if (
        not math.isfinite(safety_loss)
        or not math.isfinite(world_loss)
        or not np.any(auxiliary_gradients["safety_w"])
        or not np.any(auxiliary_gradients["world_dynamics_w"])
        or not np.any(auxiliary_gradients["world_dynamics_duration_w"])
        or not np.any(auxiliary_gradients["world_reward_w"])
        or not np.any(auxiliary_gradients["world_reward_duration_w"])
        or not np.any(auxiliary_gradients["duration_embedding"])
    ):
        raise RuntimeError("独立安全头与动作时长潜在世界模型训练自检失败")
    target = clone_target_model(np, model)
    before = float(target["q_control_b"][0, 0, 0])
    model["q_control_b"][0, 0, 0] += 0.8
    soft_update_target_model(np, target, model, 0.25)
    if abs(float(target["q_control_b"][0, 0, 0]) - (before + 0.2)) > 1e-5:
        raise RuntimeError("目标网络软更新自检失败")
    previous_updates = int(model.get("online_updates", 0))
    stable_before_update = stable_visual_state_key(np, model, state)
    online_model_update(
        np, model, state, 0, 0.4, 0.002, state, 0.9, False, target,
        duration_index=duration_bin(0.13),
    )
    if int(model.get("online_updates", 0)) != previous_updates + 1:
        raise RuntimeError("IQL 在线更新自检失败")
    if stable_visual_state_key(np, model, state) != stable_before_update:
        raise RuntimeError("冻结视觉状态键稳定性自检失败")
    graph_key = temporal_state_key(state, np, model)
    graph = {(graph_key, 0): {"count": 3, "reward": 1.2, "terminal": 0, "next": {graph_key: 3}}}
    plan = sequence_plan_values(np, {}, len(actions_list), 3, 0.8, state, graph, np.zeros(expected), model)
    if plan.shape != (expected,) or float(plan[0]) <= 0.0:
        raise RuntimeError("语义状态转移规划自检失败")
    model["world_training_steps"] = max(16, int(model.get("world_training_steps", 0)))
    latent_plan = latent_world_model_plan_values(
        np,
        model,
        recurrent_second,
        np.full(expected, 1.0 / expected, dtype=np.float32),
        np.zeros(expected, dtype=np.float32),
        6,
        0.85,
        DEFAULT_CONFIG,
        list(range(expected)),
    )
    if latent_plan.shape != (expected,) or not np.isfinite(latent_plan).all():
        raise RuntimeError("六步潜在世界模型规划自检失败")
    if hardware_capability_tier(2 * 1024 ** 3, 4, ()) != "low_numpy" or hardware_capability_tier(16 * 1024 ** 3, 16, ("DmlExecutionProvider",)) != "high_directml":
        raise RuntimeError("硬件分级自检失败")
    if second_hidden_size(768) != 768 or second_hidden_size(2048) != 2048:
        raise RuntimeError("隐藏层配置规模自检失败")
    low_runtime = adaptive_runtime_settings(DEFAULT_CONFIG, 2 * 1024 ** 3, 4)
    middle_runtime = adaptive_runtime_settings(DEFAULT_CONFIG, 12 * 1024 ** 3, 12)
    high_runtime = adaptive_runtime_settings(
        DEFAULT_CONFIG, 24 * 1024 ** 3, 16, ("DmlExecutionProvider",)
    )
    if (
        (low_runtime["hidden_size"], low_runtime["sequence_length"], low_runtime["burn_in_steps"]) != (256, 96, 32)
        or (middle_runtime["hidden_size"], middle_runtime["sequence_length"], middle_runtime["burn_in_steps"]) != (512, 192, 64)
        or (high_runtime["hidden_size"], high_runtime["sequence_length"], high_runtime["burn_in_steps"]) != (768, 256, 64)
    ):
        raise RuntimeError("分层训练规模自检失败")
    structured_keys = action_key_multihot_matrix(
        np,
        [{"keys": [0x57, 0x10]}, {"keys": [0x41, 0x10]}],
    )
    if structured_keys.shape != (2, KEY_HEAD_SIZE) or np.array_equal(
        structured_keys[0],
        structured_keys[1],
    ):
        raise RuntimeError("结构化按键 multi-hot 自检失败")
    death_config = dict(DEFAULT_CONFIG)
    for key in (
        "score_signal_weight",
        "world_progress_weight",
        "spatial_progress_weight",
        "transition_novelty_weight",
        "persistent_novelty_weight",
        "color_progress_weight",
        "visual_change_reward_weight",
        "menu_transition_penalty",
        "cycle_penalty_weight",
        "jitter_penalty_weight",
        "fade_penalty_weight",
    ):
        death_config[key] = 0.0
    death_config["task_reward_weight"] = 0.0
    death_config["exploration_reward_weight"] = 0.0
    death_config["safety_penalty_weight"] = 1.0
    death_config["death_signal_weight"] = 1.0
    bright = bytes([180]) * (FEATURE_WIDTH * FEATURE_HEIGHT)
    dark = bytes(FEATURE_WIDTH * FEATURE_HEIGHT)
    bright_color = bytes([180]) * COLOR_PIXELS
    dark_color = bytes(COLOR_PIXELS)
    death_history = {"score": [], "death": [], "menu": []}
    classify_transition_reward(
        bright,
        dark,
        bright_color,
        bright_color,
        dark_color,
        dark_color,
        [],
        death_config,
        death_history,
    )
    weighted_death, _ = classify_transition_reward(
        bright,
        dark,
        bright_color,
        bright_color,
        dark_color,
        dark_color,
        [],
        death_config,
        death_history,
    )
    progress_config = dict(death_config)
    progress_config["task_reward_weight"] = 0.0
    progress_config["exploration_reward_weight"] = 1.0
    progress_config["safety_penalty_weight"] = 0.0
    positive_progress, _ = classify_transition_reward(
        bright, bright, bright_color, bright_color, bright_color, bright_color,
        [], progress_config, {"score": [], "death": [], "menu": []}, None, 0.8,
    )
    negative_progress, _ = classify_transition_reward(
        bright, bright, bright_color, bright_color, bright_color, bright_color,
        [], progress_config, {"score": [], "death": [], "menu": []}, None, -0.8,
    )
    if not weighted_death < 0.0 or not positive_progress > negative_progress:
        raise RuntimeError("统一奖励组合自检失败")



def validate_model_file(path: Path, profile: dict, config: dict) -> bool:
    np=import_numpy(); model,changed=load_model(np,path,MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
    if changed: save_model(np,path,model)
    return changed



def repair_profile(profile_id: str, config: dict, stop_event: threading.Event | None) -> dict:
    paths=profile_paths(profile_id,repair_unsafe=True); repaired=0;removed=0
    try:
        candidate=read_json_file(paths["profile"],MAX_PROFILE_JSON_BYTES); profile=migrate_profile(candidate,profile_id)
    except Exception: profile=None
    if profile is None:
        backup_corrupt(paths["profile"]); identity={"id":profile_id,"name":profile_id,"title":"","window_class":"","executable":""}; profile=default_profile(identity); save_profile(profile,paths); repaired+=1
    else:
        ensure_action_metadata(profile)
        if profile!=candidate: save_profile(profile,paths);repaired+=1
    result=verify_experience_database(paths["db"],len(profile["actions"]),int(config["database_integrity_scan_limit"]),stop_event)
    removed+=int(result.get("removed",0))
    np=import_numpy(); model,changed=load_model(np,paths["model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
    if changed or not paths["model"].is_file(): save_model(np,paths["model"],model);repaired+=1
    best,best_changed=load_model(np,paths["best_model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
    if best_changed or not paths["best_model"].is_file():
        if int(best.get("training_rounds",0))<=0: best=clone_target_model(np,model)
        save_model(np,paths["best_model"],best);repaired+=1
    target,changed_target=load_model(np,paths["target_model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
    if changed_target or not paths["target_model"].is_file():
        if int(target.get("trained_samples",0))==0: target=clone_target_model(np,model)
        save_model(np,paths["target_model"],target);repaired+=1
    best_target,best_target_changed=load_model(np,paths["best_target_model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
    if best_target_changed or not paths["best_target_model"].is_file():
        if int(best_target.get("trained_samples",0))==0: best_target=clone_target_model(np,target)
        save_model(np,paths["best_target_model"],best_target);repaired+=1
    if paths["candidate_model"].exists():
        candidate,candidate_changed=load_model(np,paths["candidate_model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
        if candidate_changed:
            save_model(np,paths["candidate_model"],best);repaired+=1
    if paths["candidate_target_model"].exists():
        candidate_target,candidate_target_changed=load_model(np,paths["candidate_target_model"],MODEL_INPUT_DIM,TEACHER_HIDDEN_SIZE,len(profile["actions"]),profile["actions"])
        if candidate_target_changed:
            save_model(np,paths["candidate_target_model"],best_target);repaired+=1
    for tier_name, hidden_size, runtime_tier in (("low",256,"low_numpy"),("mid",512,"mid_onnx"),("high",768,"high_directml")):
        student_path=paths[f"student_{tier_name}"]; student_target_path=paths[f"student_{tier_name}_target"]
        student,student_changed=load_model(np,student_path,MODEL_INPUT_DIM,hidden_size,len(profile["actions"]),profile["actions"])
        student_target,student_target_changed=load_model(np,student_target_path,MODEL_INPUT_DIM,hidden_size,len(profile["actions"]),profile["actions"])
        if student_changed or not student_path.is_file():
            student=distill_teacher_model(np,best,hidden_size,profile["actions"],[],runtime_tier,stop_event)
            save_model(np,student_path,student);repaired+=1
        if student_target_changed or not student_target_path.is_file():
            student_target=distill_teacher_model(np,best_target,hidden_size,profile["actions"],[],runtime_tier,stop_event)
            save_model(np,student_target_path,student_target);repaired+=1
    memory_result=compact_state_values(paths["db"],int(config["state_memory_limit_per_game"]),len(profile["actions"]),stop_event)
    human_result=compact_human_action_memory(paths["db"],HUMAN_ACTION_MEMORY_LIMIT,len(profile["actions"]),stop_event)
    removed+=int(memory_result.get("removed",0))+int(human_result.get("removed",0))
    return {"repaired":repaired,"removed":removed,"records":int(result.get("records",0)),"memory_records":int(memory_result.get("records",0)),"human_memory_records":int(human_result.get("records",0))}



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
    if ensure_accelerated_runtime(download=True, stop_event=stop_event):
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
    del idle
    return 0.0




def human_observed_effect_reward(idle: bool, observed_effect: float) -> float:
    del idle
    return max(-0.04, min(0.08, 0.08 * float(observed_effect)))



def record_human_session(target: int, stop_event: threading.Event) -> str:
    config,_=ensure_core_ready(stop_event);identity=profile_identity(target);profile,paths=load_or_create_profile(identity);ensure_action_metadata(profile)
    runtime=adaptive_runtime_settings(config);interval=max(0.04,min(0.25,float(runtime["sample_interval_seconds"])));reacquire=max(0.0,min(15.0,float(config["target_reacquire_seconds"])))
    max_actions=max(8,int(config["max_action_count"]));sampler=ScreenSampler(target,str(runtime["hardware_tier"]));wheel_monitor=MouseWheelMonitor();wheel_monitor.start()
    human_memory=load_human_action_memory(paths["db"],len(profile["actions"]),HUMAN_ACTION_MEMORY_LIMIT);dirty_human:set[tuple[str,int]]=set()
    episode_id=f"human-{time.time_ns():x}-{os.getpid():x}";step=0;rows=[];pending=None;recorded=0;captured=0;black_frames=0;new_actions=0
    frame_history=[];action_history=[];duration_history=[];recent_state_keys=[];signal_history={"score":[],"death":[],"menu":[]};human_progress_reference=load_human_progress_reference(paths["db"]);previous_cursor=cursor_position();last_observation_time=time.monotonic()
    previous_raw=None;previous_blue=None;previous_red=None;previous_model_frame=None
    try:
        while not stop_event.is_set():
            if esc_pressed(): break
            replacement=foreground_replacement_window(target,identity)
            if not window_exists(target): replacement=replacement or wait_for_replacement_window(target,identity,stop_event,reacquire)
            if replacement:
                if pending is not None:
                    pending=list(pending);pending[7]=1;rows.append(tuple(pending));pending=None
                sampler.close();target=replacement;sampler=ScreenSampler(target,str(runtime["hardware_tier"]));wheel_monitor.clear();previous_cursor=cursor_position();frame_history.clear();action_history.clear();duration_history.clear();signal_history={"score":[],"death":[],"menu":[]};previous_raw=previous_blue=previous_red=previous_model_frame=None;last_observation_time=time.monotonic()
                episode_id=f"human-{time.time_ns():x}-{os.getpid():x}";step=0;continue
            if not window_exists(target): break
            if foreground_window()!=target:
                wheel_monitor.clear();time.sleep(0.08);previous_raw=previous_blue=previous_red=previous_model_frame=None;frame_history.clear();last_observation_time=time.monotonic();continue
            pre,pre_blue,pre_red=sampler.capture_frame();captured+=1
            if frame_capture_failed(pre,pre_blue,pre_red):
                black_frames+=1;time.sleep(interval);continue
            pre_model=cursor_aware_frame(target,pre);pre_feature=make_feature(pre_model,previous_model_frame,pre_blue,pre_red,sampler.last_spatial_context)
            if not frame_history: frame_history=[pre_feature]*TEMPORAL_FRAMES
            else: frame_history=(frame_history+[pre_feature])[-TEMPORAL_FRAMES:]
            state=build_temporal_state(frame_history,action_history,duration_history)
            action,previous_cursor=observe_human_action(target,previous_cursor,wheel_monitor.consume())
            now=time.monotonic()
            observed_duration=max(0.01,min(2.0,now-last_observation_time))
            last_observation_time=now
            base_action,added=register_action(profile,action,max_actions,origin="human")
            if added:
                new_actions+=1;ensure_action_metadata(profile);profile["needs_training"]=True
            composite_action=encode_action_id(base_action,duration_bin(observed_duration))
            if not sleep_cancelable(interval,stop_event,target): break
            post,post_blue,post_red=sampler.capture_frame();captured+=1
            black=frame_capture_failed(post,post_blue,post_red)
            if black:
                black_frames+=1
                next_state=None;done=1;metrics={"visual":0.0,"confirmed_death":0.0,"persistent_event":0.0,"human_progress":0.0,"controllable_novelty":0.0,"task_reward":0.0,"exploration_reward":0.0,"safety_penalty":0.20,"state_key":"black"};reward=compose_reward(metrics,config)
            else:
                post_model=cursor_aware_frame(target,post);post_feature=make_feature(post_model,pre_model,post_blue,post_red,sampler.last_spatial_context)
                next_frames=(frame_history+[post_feature])[-TEMPORAL_FRAMES:]
                next_actions=(action_history+[composite_action])[-ACTION_HISTORY_LENGTH:]
                next_durations=(duration_history+[observed_duration])[-ACTION_HISTORY_LENGTH:]
                next_state=build_temporal_state(next_frames,next_actions,next_durations)
                _,metrics=classify_transition_reward(pre,post,pre_blue,pre_red,post_blue,post_red,recent_state_keys,config,signal_history,human_progress_reference)
                idle=not(action["keys"] or action["buttons"] or action["mouse_dx"] or action["mouse_dy"] or action["mouse_wheel"])
                observed_effect=float(metrics.get("persistent_event",0.0))+float(metrics.get("human_progress",0.0))
                demonstration_effect=human_observed_effect_reward(idle,observed_effect)
                metrics["task_reward"]=max(-1.0,min(1.0,float(metrics.get("task_reward",0.0))+demonstration_effect))
                reward=compose_reward(metrics,config)
                done=1 if metrics.get("confirmed_death",0.0)>0.5 or metrics.get("confirmed_victory",0.0)>0.5 else 0
            priority=transition_priority("human",reward,bool(done),float(metrics.get("visual",0.0)))
            transition=(episode_id,step,"human",state,composite_action,reward,next_state,done,priority,float(metrics.get("task_reward",reward)),float(metrics.get("exploration_reward",0.0)),float(metrics.get("safety_penalty",max(0.0,-reward))))
            if pending is not None: rows.append(pending)
            pending=transition;recorded+=1
            memory_key=memory_state_key(pre,pre_feature);update_human_action_memory(human_memory,(memory_key,base_action));dirty_human.add((memory_key,base_action))
            update_action_reward(profile,base_action,reward);update_action_effect(profile,base_action,float(metrics.get("visual",0.0)));record_action_duration(profile,base_action,observed_duration)
            if len(rows)>=96: insert_transitions(paths["db"],rows);rows.clear()
            if len(dirty_human)>=256: save_human_action_memory(paths["db"],human_memory,dirty_human)
            if black or done:
                if pending is not None:
                    pending=list(pending);pending[7]=1;rows.append(tuple(pending));pending=None
                episode_id=f"human-{time.time_ns():x}-{os.getpid():x}";step=0;frame_history.clear();action_history.clear();duration_history.clear();recent_state_keys.clear();signal_history={"score":[],"death":[],"menu":[]};previous_model_frame=None
            else:
                step+=1;frame_history=next_frames;action_history=next_actions;duration_history=next_durations;recent_state_keys.append(str(metrics.get("state_key","")));recent_state_keys=recent_state_keys[-16:]
                previous_model_frame=post_model;previous_raw=post;previous_blue=post_blue;previous_red=post_red
    finally:
        wheel_monitor.stop();sampler.close()
        if pending is not None:
            pending=list(pending);pending[7]=1;rows.append(tuple(pending))
        if rows: insert_transitions(paths["db"],rows)
        save_human_action_memory(paths["db"],human_memory,dirty_human)
        if recorded:
            profile["human_sessions"]=int(profile.get("human_sessions",0))+1;profile["needs_training"]=True;save_profile(profile,paths)
        compact_experience(paths["db"],int(config["experience_limit_per_game"]),len(profile["actions"]));wait_esc_release()
    warning="；画面采集可能失败" if black_frames>max(8,captured//2) else ""
    return f"人类示范结束：{profile['name']}；保存 {recorded} 条完整转移；新增动作 {new_actions}{warning}"



def train_all_profiles(stop_event: threading.Event) -> str:
    np=ensure_runtime_ready(stop_event); config=load_config(); index,_=sync_profile_index(); summaries=[];total_profiles=0;total_samples=0;total_removed=0
    settings=adaptive_training_settings(config)
    runtime_training=adaptive_runtime_settings(config)
    training_config=dict(config)
    training_config["sequence_length"]=int(runtime_training["sequence_length"])
    training_config["burn_in_steps"]=int(runtime_training["burn_in_steps"])
    training_hidden_size=TEACHER_HIDDEN_SIZE
    for profile_id in sorted(index.get("profiles",{})):
        if stop_event.is_set(): return "升级已取消"
        try:
            paths=profile_paths(profile_id); profile=migrate_profile(read_json_file(paths["profile"],MAX_PROFILE_JSON_BYTES),profile_id)
            if profile is None: continue
            pool=compact_experience(paths["db"],int(config["experience_limit_per_game"]),len(profile["actions"])); total_removed+=int(pool.get("removed",0))
            if pool["human"]<4 and pool["records"]<24: summaries.append(f"{profile['name']}：经验不足");continue
            active_path=paths["best_model"] if paths["best_model"].is_file() else paths["model"]
            active_target_path=paths["best_target_model"] if paths["best_target_model"].is_file() else paths["target_model"]
            incumbent,_=load_model(np,active_path,MODEL_INPUT_DIM,training_hidden_size,len(profile["actions"]),profile["actions"])
            incumbent_target,target_changed=load_model(np,active_target_path,MODEL_INPUT_DIM,training_hidden_size,len(profile["actions"]),profile["actions"])
            tier=str(adaptive_runtime_settings(config)["hardware_tier"]);incumbent["runtime_tier"]=tier;incumbent_target["runtime_tier"]=tier
            if target_changed and int(incumbent_target.get("trained_samples",0))==0: incumbent_target=clone_target_model(np,incumbent)
            dataset=load_training_data(np,paths["db"],len(profile["actions"]),int(settings["sample_limit"]),stop_event,int(config["n_step_horizon"]),float(config["validation_episode_fraction"]),config)
            if not dataset or not dataset.get("train"): summaries.append(f"{profile['name']}：无有效轨迹");continue
            skills=extract_human_skills(list(dataset.get("train",[])),training_config)
            profile["skills"]=skills
            dataset["skills"]=skills
            validation_records=list(dataset.get("validation",[]))
            baseline=evaluate_model_records(np,incumbent,validation_records)
            if paths["candidate_model"].is_file():
                candidate,_=load_model(np,paths["candidate_model"],MODEL_INPUT_DIM,training_hidden_size,len(profile["actions"]),profile["actions"])
            else:
                candidate=clone_target_model(np,incumbent)
            if paths["candidate_target_model"].is_file():
                candidate_target,_=load_model(np,paths["candidate_target_model"],MODEL_INPUT_DIM,training_hidden_size,len(profile["actions"]),profile["actions"])
            else:
                candidate_target=clone_target_model(np,incumbent_target)
            candidate["runtime_tier"]=tier;candidate_target["runtime_tier"]=tier
            apply_global_prior(np,candidate,profile["actions"])
            metrics=train_model(np,candidate,dataset,candidate_target,int(settings["epochs"]),int(settings["batch_size"]),float(config["learning_rate"]),stop_event,training_config)
            candidate["action_hash"]=actions_hash(profile["actions"]);candidate["action_signatures"]=[action_signature(a) for a in profile["actions"]]
            candidate_target["action_hash"]=candidate["action_hash"];candidate_target["action_signatures"]=list(candidate["action_signatures"])
            save_model(np,paths["candidate_model"],candidate);save_model(np,paths["candidate_target_model"],candidate_target)
            baseline_score=float(baseline.get("score",-1e9));candidate_score=float(metrics.get("validation_score",-1e9))
            baseline_safety=float(baseline.get("safety_error",1.0))
            candidate_safety=float(metrics.get("validation_safety_error",1.0))
            baseline_q_error=float(baseline.get("q_calibration_error",1.0))
            candidate_q_error=float(metrics.get("validation_q_calibration_error",1.0))
            first_model=int(incumbent.get("training_rounds",0))<=0
            safety_guard=candidate_safety<=baseline_safety+0.03
            calibration_guard=candidate_q_error<=baseline_q_error+0.05
            baseline_success=float(baseline.get("success_episode_rate",0.0))
            candidate_success=float(metrics.get("validation_success_episode_rate",0.0))
            baseline_actual_score=float(baseline.get("actual_cumulative_score",0.0))
            candidate_actual_score=float(metrics.get("validation_actual_cumulative_score",0.0))
            baseline_episode_test=float(baseline.get("episode_test_score",0.0))
            candidate_episode_test=float(metrics.get("validation_episode_test_score",0.0))
            episode_count=int(metrics.get("validation_episode_count",0))
            minimum_validation_episodes=max(1,int(config.get("minimum_validation_episodes",8)))
            enough_validation=episode_count>=minimum_validation_episodes
            outcome_improved=(
                candidate_episode_test>=baseline_episode_test+0.01
                or candidate_success>=baseline_success+0.02
                or candidate_actual_score>=baseline_actual_score+0.05
            )
            accepted=first_model or (
                enough_validation
                and outcome_improved
                and safety_guard
                and calibration_guard
                and candidate_score>=baseline_score-0.01
            )
            if accepted:
                save_model(np,paths["best_model"],candidate);save_model(np,paths["model"],candidate)
                save_model(np,paths["best_target_model"],candidate_target);save_model(np,paths["target_model"],candidate_target)
                save_runtime_students(
                    np, paths, candidate, candidate_target, profile["actions"],
                    list(dataset.get("train", [])), stop_event,
                )
                profile["trained_samples"]=int(profile.get("trained_samples",0))+metrics["samples"];profile["training_rounds"]=int(profile.get("training_rounds",0))+1;profile["needs_training"]=False;save_profile(profile,paths)
                total_profiles+=1;total_samples+=metrics["samples"]
                decision=f"已晋升（{baseline_score:.3f}→{candidate_score:.3f}）"
            else:
                save_model(np,paths["candidate_model"],incumbent);save_model(np,paths["candidate_target_model"],incumbent_target)
                profile["needs_training"]=True;save_profile(profile,paths)
                decision=f"未晋升并自动回滚（{baseline_score:.3f}→{candidate_score:.3f}）"
            summaries.append(f"{profile['name']}：{metrics['samples']}条/{metrics['episodes']}回合，技能{metrics['skills']}个，成功回合{metrics['validation_success_episode_rate']:.0%}，生存{metrics['validation_average_survival_steps']:.1f}步，实际累计分{metrics['validation_actual_cumulative_score']:.2f}，{decision}")
            if dataset.get("invalid"): log_text(f"{profile_id} 训练时忽略损坏轨迹 {dataset['invalid']} 条")
        except RuntimeError as error:
            if str(error)=="操作已取消": raise
            log_text(f"训练 {profile_id} 失败:\n"+traceback.format_exc());summaries.append(f"{profile_id}：失败")
        except Exception:
            log_text(f"训练 {profile_id} 失败:\n"+traceback.format_exc());summaries.append(f"{profile_id}：失败")
    prior_updated=refresh_global_prior(np,index,config,stop_event)
    detail="；".join(summaries[:4])+(f"；另有 {len(summaries)-4} 个游戏" if len(summaries)>4 else "")
    return f"升级完成：{total_profiles} 个候选模型通过验证，训练 {total_samples} 条完整转移；清理 {total_removed} 条；best_teacher_model 可自动回滚"+("；已更新跨游戏因子先验" if prior_updated else "")+"。"+detail





def _stratified_replay_samples(population: list[dict], count: int) -> list[dict]:
    maximum = max(0, min(len(population), int(count)))
    if maximum <= 0:
        return []
    strata: dict[str, dict[str, list[dict]]] = {}
    for index, sample in enumerate(population):
        episode_id = str(sample.get("episode_id", f"unknown-{index}"))
        key = "|".join(
            (
                _success_rate_bucket(float(sample.get("success_rate", 0.50))),
                str(sample.get("failure_type", "none")),
                _novelty_bucket(float(sample.get("novelty_score", 0.0))),
            )
        )
        strata.setdefault(key, {}).setdefault(episode_id, []).append(sample)
    stratum_order = list(strata)
    random.shuffle(stratum_order)
    episode_orders: dict[str, list[str]] = {}
    episode_offsets: dict[str, int] = {}
    for key in stratum_order:
        order = list(strata[key])
        random.shuffle(order)
        episode_orders[key] = order
        episode_offsets[key] = 0
    selected: list[dict] = []
    selected_ids: set[int] = set()
    while len(selected) < maximum and stratum_order:
        progressed = False
        active: list[str] = []
        for key in stratum_order:
            order = episode_orders[key]
            if not order:
                continue
            chosen_episode = None
            for _ in range(len(order)):
                position = episode_offsets[key] % len(order)
                episode_offsets[key] += 1
                candidate = order[position]
                if strata[key][candidate]:
                    chosen_episode = candidate
                    break
            if chosen_episode is None:
                continue
            bucket = strata[key][chosen_episode]
            sample = bucket.pop(random.randrange(len(bucket)))
            selected.append(sample)
            selected_ids.add(id(sample))
            progressed = True
            if any(strata[key][episode_id] for episode_id in order):
                active.append(key)
            if len(selected) >= maximum:
                break
        if not progressed:
            break
        stratum_order = active
    if len(selected) < maximum:
        remaining = [sample for sample in population if id(sample) not in selected_ids]
        random.shuffle(remaining)
        selected.extend(remaining[: maximum - len(selected)])
    return selected


def _flush_online_n_step(
    np,
    queue_items: deque,
    model: dict,
    target_model: dict,
    learning_rate: float,
    horizon: int,
    discount: float,
    replay_buffer: deque | None = None,
    batch_size: int = ONLINE_REPLAY_BATCH_DEFAULT,
    update_interval: int = ONLINE_REPLAY_INTERVAL_DEFAULT,
    force: bool = False,
    critic_weights=None,
) -> int:
    if replay_buffer is None:
        replay_buffer = deque(maxlen=ONLINE_REPLAY_CAPACITY_DEFAULT)
    prepared = 0
    while queue_items and (force or len(queue_items) >= horizon or queue_items[0]["done"]):
        first = queue_items[0]
        total = 0.0
        task_total = 0.0
        exploration_total = 0.0
        safety_total = 0.0
        factor = 1.0
        next_state = first["next_state"]
        terminal = first["done"]
        used = 0
        reliability_total = 0.0
        success_total = 0.0
        novelty_total = 0.0
        failure_types: list[str] = []
        for item in list(queue_items)[:horizon]:
            total += factor * float(item["reward"])
            task_total += factor * float(item.get("task_reward", item["reward"]))
            exploration_total += factor * float(item.get("exploration_reward", max(0.0, item["reward"])))
            safety_total += factor * float(item.get("safety_penalty", max(0.0, -item["reward"])))
            reliability_total += float(item.get("reliability", 1.0))
            success_total += float(item.get("success_rate", 0.50))
            novelty_total += float(item.get("novelty_score", 0.0))
            failure_value = str(item.get("failure_type", "none"))
            if failure_value != "none":
                failure_types.append(failure_value)
            used += 1
            next_state = item["next_state"]
            terminal = bool(item["done"])
            if terminal:
                break
            factor *= discount
        replay_buffer.append(
            {
                "episode_id": str(first.get("episode_id", "unknown")),
                "state": first["state"],
                "action": int(first["action"]),
                "duration_index": max(
                    0,
                    min(DURATION_HEAD_SIZE - 1, int(first.get("duration_index", DURATION_HEAD_SIZE // 2))),
                ),
                "reward": max(-3.0, min(3.0, total)),
                "critic_rewards": (
                    max(-3.0, min(3.0, task_total)),
                    max(0.0, min(3.0, exploration_total)),
                    max(0.0, min(4.0, safety_total)),
                ),
                "world_rewards": (
                    max(-1.0, min(1.0, float(first.get("task_reward", first["reward"])))),
                    max(0.0, min(1.0, float(first.get("exploration_reward", 0.0)))),
                    max(0.0, min(2.0, float(first.get("safety_penalty", max(0.0, -first["reward"]))))),
                ),
                "world_next_state": first["next_state"],
                "world_terminal": bool(first["done"]),
                "next_state": next_state,
                "discount": 0.0 if terminal else discount**used,
                "terminal": terminal,
                "reliability": max(0.05, min(1.0, reliability_total / max(1, used))),
                "success_rate": max(0.0, min(1.0, success_total / max(1, used))),
                "failure_type": failure_types[0] if failure_types else "none",
                "novelty_score": max(0.0, min(1.0, novelty_total / max(1, used))),
            }
        )
        prepared += 1
        queue_items.popleft()
        if not force and len(queue_items) < horizon:
            break
    model["_online_replay_ticks"] = int(model.get("_online_replay_ticks", 0)) + int(prepared > 0)
    interval = max(1, min(64, int(update_interval)))
    requested_batch = max(8, min(256, int(batch_size)))
    should_update = force or (
        prepared > 0
        and len(replay_buffer) >= requested_batch
        and int(model["_online_replay_ticks"]) % interval == 0
    )
    if not should_update or not replay_buffer:
        return 0
    population = list(replay_buffer)
    count = min(len(population), requested_batch)
    samples = _stratified_replay_samples(population, count)
    updated = 0
    for sample in samples:
        effective_lr = float(learning_rate) * float(sample["reliability"]) / math.sqrt(max(1, count))
        if online_model_update(
            np,
            model,
            sample["state"],
            sample["action"],
            sample["reward"],
            effective_lr,
            sample["next_state"],
            sample["discount"],
            sample["terminal"],
            target_model,
            sample["critic_rewards"],
            critic_weights,
            sample["world_rewards"],
            sample["world_next_state"],
            sample["world_terminal"],
            duration_index=sample["duration_index"],
        ):
            updated += 1
    return updated




def run_ai_session(target: int, stop_event: threading.Event) -> str:
    np = ensure_runtime_ready(stop_event)
    config = load_config()
    runtime = adaptive_runtime_settings(config)
    model_hidden_size = int(runtime["hidden_size"])
    identity = profile_identity(target)
    profile, paths = load_or_create_profile(identity)
    ensure_action_metadata(profile)
    prior = load_global_prior(np)
    runtime_tier = str(runtime["hardware_tier"])
    active_path, active_target_path = runtime_student_paths(paths, runtime_tier)
    if active_path.is_file():
        model, changed = load_model(
            np, active_path, MODEL_INPUT_DIM, model_hidden_size,
            len(profile["actions"]), profile["actions"],
        )
    else:
        teacher_path = paths["best_model"] if paths["best_model"].is_file() else paths["model"]
        if teacher_path.is_file():
            teacher, _ = load_model(
                np, teacher_path, MODEL_INPUT_DIM, TEACHER_HIDDEN_SIZE,
                len(profile["actions"]), profile["actions"],
            )
            model = distill_teacher_model(
                np, teacher, model_hidden_size, profile["actions"], [], runtime_tier, stop_event
            )
        else:
            model = model_from_global_prior(np, prior, profile["actions"], model_hidden_size)
        changed = True
    if active_target_path.is_file():
        target_model, target_changed = load_model(
            np, active_target_path, MODEL_INPUT_DIM, model_hidden_size,
            len(profile["actions"]), profile["actions"],
        )
    else:
        target_model = clone_target_model(np, model)
        target_changed = True
    model["runtime_tier"] = runtime_tier
    target_model["runtime_tier"] = runtime_tier
    if changed or not active_path.is_file():
        save_model(np, active_path, model)
    if target_changed or not active_target_path.is_file():
        save_model(np, active_target_path, target_model)

    action_count = len(profile["actions"])
    skills = list(profile.get("skills", []))[:SKILL_HEAD_SIZE]
    human_memory = load_human_action_memory(
        paths["db"],
        action_count,
        HUMAN_ACTION_MEMORY_LIMIT,
    )
    human_index = build_human_action_memory_index(human_memory)
    state_memory = load_state_value_memory(
        paths["db"],
        action_count,
        int(config["state_memory_limit_per_game"]),
    )
    state_index = build_state_memory_index(state_memory)
    state_visit_totals = build_state_visit_totals(state_memory)
    dirty_state_values: set[tuple[str, int]] = set()
    state_action_visits: dict[tuple[str, int], int] = {
        key: int(value[1]) for key, value in state_memory.items()
    }
    graph = load_transition_graph(paths["db"], 50000, np, model)
    human_progress_reference = load_human_progress_reference(paths["db"])
    total_samples, human_samples = count_samples(paths["db"])
    minimum_human = max(8, int(config["minimum_human_transitions"]))
    online_ready = (
        human_samples >= minimum_human
        and int(model.get("training_rounds", 0)) > 0
    )
    if not online_ready:
        return (
            f"AI未启动：{profile['name']} 目前有 {human_samples} 条人类转移；"
            f"请先用“人”记录至少 {minimum_human} 条，再点“升级”完成行为克隆和离线 IQL。"
        )
    local_control = learned_control_preferences(profile, paths["db"])
    cross_control = load_cross_game_control_prior(profile["id"])
    control_preferences = blend_control_preferences(
        local_control,
        cross_control,
        human_samples,
        float(config["cross_game_control_weight"]),
    )
    cross_scene_control = load_cross_game_scene_control_prior(profile["id"])
    cross_scene_actions = load_cross_game_scene_action_prior(profile["id"])
    probe_template = cold_start_probe_actions(profile, control_preferences)

    sampler = ScreenSampler(target, runtime_tier)
    reacquire = max(0.0, min(15.0, float(config["target_reacquire_seconds"])))
    pause = max(0.0, min(0.5, float(runtime["step_pause_seconds"])))
    confirmation_delay = max(
        0.0,
        min(0.25, float(runtime["confirmation_delay_seconds"])),
    )
    capture_timeout = max(
        10.0,
        min(300.0, float(config["capture_failure_timeout_seconds"])),
    )
    mouse_step = max(1, min(200, int(config["mouse_step_pixels"])))
    horizon = max(1, min(24, int(config["delayed_reward_horizon"])))
    discount = max(0.1, min(0.99, float(config["delayed_reward_discount"])))
    online_lr = (
        max(0.0, min(0.02, float(config["online_model_learning_rate"])))
        if online_ready
        else 0.0
    )
    online_td_discount = max(0.0, min(0.95, float(config["online_td_discount"])))
    target_sync = max(16, min(4096, int(config["target_network_sync_steps"])))
    target_tau = max(0.01, min(1.0, float(config["target_network_soft_update"])))
    checkpoint = max(32, min(10000, int(runtime["online_checkpoint_steps"])))
    planning_refresh = max(8, min(512, int(runtime["planning_refresh_steps"])))
    base_exploration = max(0.0, min(0.65, float(config["exploration"])))
    base_exploration = min(
        base_exploration,
        max(0.0, min(1.0, float(config["zero_shot_exploration"]))),
    )
    if not online_ready:
        base_exploration = 0.0

    episode_id = f"ai-{time.time_ns():x}-{os.getpid():x}"
    step = 0
    rows: list[tuple] = []
    online_queue = deque()
    online_replay = deque(maxlen=max(128, min(16384, int(runtime["online_replay_capacity"]))))
    active_skill = deque()
    active_skill_index = None
    frame_history: list[bytes] = []
    action_history: list[int] = []
    duration_history: list[float] = []
    recent_state_keys: list[str] = []
    signal_history = {"score": [], "death": [], "menu": []}
    recent_actions: list[int] = []
    failure_until: dict[int, int] = {}
    steps = 0
    reward_sum = 0.0
    black_frames = 0
    recent_reward = 0.0
    reward_observations = 0
    episode_task_total = 0.0
    episode_exploration_total = 0.0
    episode_safety_total = 0.0
    episode_reward_total = 0.0
    episode_novelty_total = 0.0
    episode_steps = 0
    static_streak = 0
    smoothed_prob = None
    smoothed_values = None
    model_changed = False
    previous_model_frame = None
    previous_raw = None
    last_good_capture = time.monotonic()
    last_action_id = -1
    last_duration = 0.0
    model_hidden = np.zeros(int(model["hidden_size"]), dtype=np.float32)
    target_hidden = np.zeros(int(target_model["hidden_size"]), dtype=np.float32)

    def reset_episode_state() -> None:
        nonlocal step, frame_history, action_history, duration_history
        nonlocal recent_state_keys, signal_history, recent_actions, static_streak
        nonlocal previous_model_frame, previous_raw, smoothed_prob, smoothed_values
        nonlocal last_action_id, last_duration, model_hidden, target_hidden
        nonlocal active_skill, active_skill_index
        nonlocal episode_task_total, episode_exploration_total, episode_safety_total
        nonlocal episode_reward_total, episode_novelty_total, episode_steps
        step = 0
        frame_history = []
        action_history = []
        duration_history = []
        recent_state_keys = []
        signal_history = {"score": [], "death": [], "menu": []}
        recent_actions = []
        static_streak = 0
        previous_model_frame = None
        previous_raw = None
        smoothed_prob = None
        smoothed_values = None
        last_action_id = -1
        last_duration = 0.0
        episode_task_total = 0.0
        episode_exploration_total = 0.0
        episode_safety_total = 0.0
        episode_reward_total = 0.0
        episode_novelty_total = 0.0
        episode_steps = 0
        model_hidden = np.zeros(int(model["hidden_size"]), dtype=np.float32)
        target_hidden = np.zeros(int(target_model["hidden_size"]), dtype=np.float32)
        active_skill.clear()
        active_skill_index = None

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
                    reacquire,
                )
            if replacement:
                _flush_online_n_step(
                    np,
                    online_queue,
                    model,
                    target_model,
                    online_lr,
                    horizon,
                    online_td_discount,
                    online_replay,
                    int(runtime["online_replay_batch_size"]),
                    int(config["online_replay_interval"]),
                    True,
                    config,
                )
                if rows:
                    last = list(rows[-1])
                    last[7] = 1
                    rows[-1] = tuple(last)
                    insert_transitions(paths["db"], rows)
                    rows.clear()
                else:
                    mark_episode_terminal(paths["db"], episode_id)
                sampler.close()
                target = replacement
                sampler = ScreenSampler(target, runtime_tier)
                episode_id = f"ai-{time.time_ns():x}-{os.getpid():x}"
                reset_episode_state()
                continue
            if not window_exists(target):
                break
            if foreground_window() != target:
                release_all_inputs()
                time.sleep(0.08)
                previous_model_frame = None
                previous_raw = None
                continue

            current_raw, current_blue, current_red = sampler.capture_frame()
            if frame_capture_failed(current_raw, current_blue, current_red):
                black_frames += 1
                if time.monotonic() - last_good_capture >= capture_timeout:
                    raise RuntimeError("持续无法采集游戏画面，已安全停止")
                time.sleep(0.08)
                continue
            last_good_capture = time.monotonic()
            current_model = cursor_aware_frame(target, current_raw)
            current_feature = make_feature(
                current_model,
                previous_model_frame,
                current_blue,
                current_red,
                sampler.last_spatial_context,
            )
            if not frame_history:
                frame_history = [current_feature] * TEMPORAL_FRAMES
            else:
                frame_history = (frame_history + [current_feature])[-TEMPORAL_FRAMES:]
            state = build_temporal_state(
                frame_history,
                action_history,
                duration_history,
            )
            model_hidden = recurrent_model_step(
                np,
                model,
                current_feature,
                model_hidden,
                last_action_id,
                last_duration,
            )
            target_hidden = recurrent_model_step(
                np,
                target_model,
                current_feature,
                target_hidden,
                last_action_id,
                last_duration,
            )
            probabilities, values, uncertainty, disagreement = recurrent_ensemble_outputs(
                np,
                model,
                target_model,
                model_hidden,
                target_hidden,
                float(config["target_ensemble_weight"]),
                config,
            )
            state_safety_risk = predict_safety_probability(np, model, model_hidden)
            scene_motion = feature_motion(current_feature)
            static_streak = static_streak + 1 if scene_motion < 0.008 else 0
            scene_context, scene_biases = infer_scene_context(
                current_raw,
                previous_raw,
                static_streak,
            )
            probabilities, values, policy_drift = temporal_policy_blend(
                np,
                probabilities,
                values,
                smoothed_prob,
                smoothed_values,
                scene_motion,
                static_streak,
            )
            smoothed_prob = probabilities.copy()
            smoothed_values = values.copy()

            memory_key = memory_state_key(current_raw, current_feature)
            human_bias = human_action_memory_biases(
                human_memory,
                human_index,
                memory_key,
                action_count,
            )
            approximate_values = approximate_state_action_values(
                state_index,
                memory_key,
                action_count,
            )
            scene_control = blended_scene_control_evidence(
                profile,
                scene_context,
                cross_scene_control,
                float(config["cross_game_scene_weight"]),
            )
            scene_action_values = scene_action_response_evidence(
                profile,
                scene_context,
            )
            cross_action_values = cross_game_scene_action_values(
                cross_scene_actions,
                scene_context,
                profile["actions"],
            )
            visual_targets = visual_action_target_biases(
                current_raw,
                previous_raw,
                profile["actions"],
            )
            reward_guidance, effect_guidance, risk_guidance, uncertainty_bonus = (
                empirical_action_guidance(
                    np,
                    profile["action_reward_ema"],
                    profile["action_reward_counts"],
                    profile["action_effect_ema"],
                    profile["action_effect_counts"],
                    profile["action_risk_ema"],
                    profile["action_risk_counts"],
                    not online_ready,
                )
            )
            executable_name = Path(str(profile.get("executable", ""))).stem.lower()
            blocked_action_ids: set[int] = set()
            origins = profile.get("action_origins", [])
            for base_index, action in enumerate(profile["actions"]):
                origin = origins[base_index] if base_index < len(origins) else "generic"
                kind = action_kind(action)
                exact_value, exact_visits = state_memory.get(
                    (memory_key, base_index),
                    (0.0, 0),
                )
                exact_confidence = min(
                    1.0,
                    math.log1p(max(0, int(exact_visits))) / math.log(33.0),
                )
                approximate_value, approximate_confidence = approximate_values.get(
                    base_index,
                    (0.0, 0.0),
                )
                policy_bias = action_policy_bias(
                    action,
                    origin,
                    not online_ready,
                    static_streak,
                    scene_motion,
                    steps,
                    control_preferences,
                )
                safety = action_safety_penalty(
                    action,
                    origin,
                    executable_name,
                    static_streak,
                )
                diversity_penalty = (
                    recent_actions[-8:].count(base_index)
                    / 8.0
                    * float(config["action_diversity_weight"])
                )
                adjustment = (
                    float(config["state_memory_weight"])
                    * float(exact_value)
                    * exact_confidence
                    + float(config["approximate_state_memory_weight"])
                    * float(approximate_value)
                    * float(approximate_confidence)
                    + float(config["online_state_value_weight"])
                    * float(human_bias[base_index])
                    + float(config["action_effect_weight"])
                    * float(effect_guidance[base_index])
                    + float(config["world_progress_weight"])
                    * float(reward_guidance[base_index])
                    - float(config["action_risk_weight"])
                    * float(risk_guidance[base_index])
                    + float(config["scene_strategy_weight"])
                    * (
                        float(scene_biases.get(kind, 0.0))
                        + float(scene_control.get(kind, 0.0))
                    )
                    + float(config["scene_action_memory_weight"])
                    * float(scene_action_values[base_index])
                    + float(config["cross_game_action_weight"])
                    * float(cross_action_values[base_index])
                    + 0.18 * float(visual_targets[base_index])
                    + policy_bias
                    + float(uncertainty_bonus[base_index])
                    - float(config["safety_penalty_weight"]) * safety
                    - diversity_penalty
                )
                values[base_index] += adjustment
                ineffective = (
                    int(profile["action_effect_counts"][base_index]) >= int(config["action_freeze_min_tests"])
                    and float(profile["action_effect_ema"][base_index]) < float(config["action_freeze_effect_threshold"])
                    and static_streak < int(config["stuck_recovery_threshold"])
                )
                if (
                    target_action_blocked(action, origin, executable_name)
                    or failure_until.get(base_index, -1) > steps
                    or ineffective
                ):
                    blocked_action_ids.add(base_index)

            if recent_actions:
                sequence_prior = transition_distribution(
                    np,
                    profile,
                    recent_actions[-1],
                    action_count,
                    recent_actions[-2] if len(recent_actions) > 1 else None,
                    float(config["sequence_prior_weight"]),
                )
                expanded_prior = sequence_prior
                sequence_blend = max(
                    0.0,
                    min(0.85, float(config["sequence_prior_weight"])),
                )
                probabilities = (
                    probabilities * (1.0 - sequence_blend)
                    + expanded_prior * sequence_blend
                )
                probabilities /= max(1e-12, float(probabilities.sum()))

            allowed_actions = [
                action_id
                for action_id in range(len(probabilities))
                if action_id not in blocked_action_ids
            ]
            graph_planning = sequence_plan_values(
                np,
                profile,
                action_count,
                int(runtime["planning_horizon"]),
                float(config["planning_discount"]),
                state,
                graph,
                values,
                model,
            )
            stable_key = temporal_state_key(state, np, model)
            neighbor_keys = transition_graph_state_neighbors(graph, stable_key)
            familiar_entries = sum(
                1
                for neighbor in neighbor_keys
                for action_id in range(len(probabilities))
                if (neighbor, action_id) in graph
            )
            familiarity = min(1.0, familiar_entries / 8.0)
            online_planning = graph_planning
            plan_disagreement = np.zeros_like(online_planning, dtype=np.float64)
            if bool(runtime["use_latent_world_model"]):
                world_planning = latent_world_model_plan_values(
                    np,
                    model,
                    model_hidden,
                    probabilities,
                    values,
                    int(runtime["latent_planning_horizon"]),
                    float(config["planning_discount"]),
                    config,
                    allowed_actions,
                )
                world_steps = max(0, int(model.get("world_training_steps", 0)))
                world_confidence = min(1.0, world_steps / max(1.0, float(WORLD_MODEL_FULL_CONFIDENCE_STEPS)))
                planning, plan_disagreement = reconcile_online_world_plans(
                    np,
                    online_planning,
                    world_planning,
                    familiarity,
                    world_confidence,
                    float(config["planning_disagreement_penalty"]),
                )
            else:
                planning = online_planning
            confidence = calibrated_policy_confidence(
                np,
                probabilities,
                values,
            )
            exploration = adaptive_exploration_rate(
                base_exploration,
                confidence,
                familiarity,
                policy_drift,
                recent_reward,
                reward_observations,
            )
            exploration *= max(0.15, 1.0 - 0.70 * state_safety_risk)
            recovery_base = None
            if static_streak >= int(config["stuck_recovery_threshold"]):
                recovery_base = choose_recovery_action(
                    profile,
                    memory_key,
                    state_action_visits,
                    recent_actions,
                    static_streak,
                    steps,
                    control_preferences,
                    control_response_evidence(profile),
                    scene_control,
                )
            contextual_probe = None
            if (
                online_ready
                and recovery_base is None
                and static_streak >= max(3, int(config["stuck_recovery_threshold"]) // 2)
            ):
                contextual_probe = choose_contextual_probe_action(
                    profile,
                    list(probe_template),
                    set(blocked_action_ids),
                    state_action_visits,
                    memory_key,
                    scene_biases,
                    float(config["contextual_probe_weight"]),
                    steps,
                )
            selected_base = recovery_base if recovery_base is not None else contextual_probe
            selected_skill_duration = None
            if active_skill and (static_streak >= int(config["stuck_recovery_threshold"]) or recent_reward < -0.18):
                active_skill.clear()
                active_skill_index = None
            if selected_base is None and active_skill:
                candidate_base, candidate_duration = active_skill.popleft()
                if candidate_base in allowed_actions:
                    selected_base = candidate_base
                    selected_skill_duration = candidate_duration
                else:
                    active_skill.clear()
                    active_skill_index = None
            if selected_base is None and not active_skill:
                skill_index = choose_skill(
                    np, model, model_hidden, skills,
                    float(config["skill_start_probability"]), exploration,
                )
                if skill_index is not None:
                    skill = skills[skill_index]
                    active_skill = deque(zip(skill["actions"][:SKILL_EXECUTION_LIMIT], skill["durations"][:SKILL_EXECUTION_LIMIT]))
                    active_skill_index = skill_index
                    if active_skill:
                        candidate_base, candidate_duration = active_skill.popleft()
                        if candidate_base in allowed_actions:
                            selected_base = candidate_base
                            selected_skill_duration = candidate_duration
                        else:
                            active_skill.clear()
                            active_skill_index = None
            if selected_base is not None and 0 <= selected_base < action_count and selected_base not in blocked_action_ids:
                action_id = int(selected_base)
            else:
                action_id = choose_policy_action(
                    np, probabilities, values, exploration,
                    allowed_actions=allowed_actions,
                    uncertainty=uncertainty + disagreement + plan_disagreement,
                    planning_values=planning,
                    uncertainty_weight=float(config["model_uncertainty_weight"]),
                    planning_weight=float(config["planning_weight"]),
                )
            base_action = int(action_id)
            if not 0 <= base_action < action_count:
                action_id = 0
                base_action = 0
            if selected_skill_duration is not None:
                duration_index = max(0, min(DURATION_HEAD_SIZE - 1, int(selected_skill_duration)))
                configured_hold = float(DURATION_SECONDS[duration_index])
            else:
                configured_hold = predict_conditional_hold(
                    np,
                    model,
                    model_hidden,
                    base_action,
                    exploration * 0.35,
                    config,
                )
                duration_index = duration_bin(configured_hold)
            hold = adaptive_action_hold(
                profile,
                base_action,
                configured_hold,
                scene_motion,
                static_streak,
                float(config["adaptive_hold_strength"]),
            )
            duration_index = duration_bin(hold)
            action_id = encode_action_id(base_action, duration_index)

            pre_raw = current_raw
            pre_blue = current_blue
            pre_red = current_red
            pre_model = current_model
            if not execute_action(
                target,
                parameterized_action_from_heads(
                    np,
                    model,
                    model_hidden,
                    profile["actions"][base_action],
                    float(config["parameterized_action_strength"]),
                ),
                hold,
                mouse_step,
                stop_event,
            ):
                break
            if pause and not sleep_cancelable(pause, stop_event, target):
                break
            next_raw, next_blue, next_red = sampler.capture_frame()
            black = frame_capture_failed(next_raw, next_blue, next_red)
            if not black and confirmation_delay > 0.0:
                immediate = (next_raw, next_blue, next_red)
                if sleep_cancelable(confirmation_delay, stop_event, target):
                    settled = sampler.capture_frame()
                    if not frame_capture_failed(*settled):
                        next_raw, next_blue, next_red = settled
                    else:
                        next_raw, next_blue, next_red = immediate
            if black:
                black_frames += 1
                next_state = None
                next_feature = None
                next_model = None
                next_memory_key = ""
                done = 1
                metrics = {
                    "visual": 0.0,
                    "death": 1.0,
                    "confirmed_death": 0.0,
                    "persistence": 0.0,
                    "flicker": 1.0,
                    "fade": 1.0,
                    "global_shift": 1.0,
                    "task_reward": 0.0,
                    "exploration_reward": 0.0,
                    "safety_penalty": 1.0,
                    "state_key": "black",
                }
                reward = compose_reward(metrics, config)
            else:
                next_model = cursor_aware_frame(target, next_raw)
                next_feature = make_feature(
                    next_model,
                    pre_model,
                    next_blue,
                    next_red,
                    sampler.last_spatial_context,
                )
                next_frames = (frame_history + [next_feature])[-TEMPORAL_FRAMES:]
                next_actions = (action_history + [action_id])[-ACTION_HISTORY_LENGTH:]
                next_durations = (duration_history + [hold])[-ACTION_HISTORY_LENGTH:]
                next_state = build_temporal_state(
                    next_frames,
                    next_actions,
                    next_durations,
                )
                next_hidden_preview = recurrent_model_step(
                    np, model, next_feature, model_hidden, action_id, hold
                )
                target_next_hidden_preview = recurrent_model_step(
                    np,
                    target_model,
                    next_feature,
                    target_hidden,
                    action_id,
                    hold,
                )
                online_progress_delta = (
                    predict_progress(np, model, next_hidden_preview)
                    - predict_progress(np, model, model_hidden)
                )
                target_progress_delta = (
                    predict_progress(np, target_model, target_next_hidden_preview)
                    - predict_progress(np, target_model, target_hidden)
                )
                progress_agreement = math.exp(
                    -3.5 * abs(online_progress_delta - target_progress_delta)
                )
                progress_confidence = min(
                    learned_progress_confidence(model),
                    learned_progress_confidence(target_model),
                )
                progress_head_delta = max(
                    -1.0,
                    min(
                        1.0,
                        (
                            0.35 * online_progress_delta
                            + 0.65 * target_progress_delta
                        )
                        * progress_agreement
                        * progress_confidence,
                    ),
                )
                online_reward_signals = reward_model_signals(
                    np, model, model_hidden, next_hidden_preview
                )
                target_reward_signals = reward_model_signals(
                    np, target_model, target_hidden, target_next_hidden_preview
                )
                reward_progress_agreement = math.exp(
                    -3.5 * abs(
                        online_reward_signals["progress"]
                        - target_reward_signals["progress"]
                    )
                )
                learned_reward_confidence = min(
                    online_reward_signals["confidence"],
                    target_reward_signals["confidence"],
                ) * reward_progress_agreement
                learned_progress_delta = (
                    0.30 * progress_head_delta
                    + 0.70 * (
                        0.35 * online_reward_signals["progress"]
                        + 0.65 * target_reward_signals["progress"]
                    ) * learned_reward_confidence
                )
                learned_reward_signals = {
                    "progress": float(learned_progress_delta),
                    "success_probability": float(
                        0.35 * online_reward_signals["success_probability"]
                        + 0.65 * target_reward_signals["success_probability"]
                    ),
                    "failure_probability": float(
                        0.35 * online_reward_signals["failure_probability"]
                        + 0.65 * target_reward_signals["failure_probability"]
                    ),
                    "reset_probability": float(
                        0.35 * online_reward_signals["reset_probability"]
                        + 0.65 * target_reward_signals["reset_probability"]
                    ),
                    "confidence": float(learned_reward_confidence),
                }
                reward, metrics = classify_transition_reward(
                    pre_raw,
                    next_raw,
                    pre_blue,
                    pre_red,
                    next_blue,
                    next_red,
                    recent_state_keys,
                    config,
                    signal_history,
                    human_progress_reference,
                    learned_progress_delta,
                    learned_reward_signals,
                )
                next_memory_key = memory_state_key(next_raw, next_feature)
                meaningful = (
                    float(metrics.get("visual", 0.0))
                    >= float(config["successful_transition_threshold"])
                )
                frontier_bonus = persistent_frontier_reward(
                    state_visit_totals,
                    next_memory_key,
                    float(metrics.get("visual", 0.0)),
                    meaningful,
                    float(config["persistent_frontier_reward_weight"]),
                )
                action_safety = action_safety_penalty(
                    profile["actions"][base_action],
                    origins[base_action] if base_action < len(origins) else "generic",
                    executable_name,
                    static_streak,
                )
                metrics["exploration_reward"] = max(
                    0.0,
                    min(
                        1.0,
                        float(metrics.get("exploration_reward", 0.0))
                        + frontier_bonus,
                    ),
                )
                metrics["safety_penalty"] = max(
                    0.0,
                    min(
                        2.0,
                        float(metrics.get("safety_penalty", 0.0))
                        + float(config["action_risk_weight"]) * action_safety,
                    ),
                )
                reward = compose_reward(metrics, config)
                done = 1 if float(metrics.get("confirmed_death", 0.0)) > 0.5 or float(metrics.get("confirmed_victory", 0.0)) > 0.5 else 0
                if done or float(metrics.get("cycle", 0.0)) > 0.65 or reward < -0.45:
                    active_skill.clear()
                    active_skill_index = None

            priority = transition_priority(
                "ai",
                reward,
                bool(done),
                float(metrics.get("visual", 0.0)),
            )
            rows.append(
                (
                    episode_id,
                    step,
                    "ai",
                    state,
                    action_id,
                    reward,
                    next_state,
                    done,
                    priority,
                    float(metrics.get("task_reward", reward)),
                    float(metrics.get("exploration_reward", 0.0)),
                    float(metrics.get("safety_penalty", max(0.0, -reward))),
                )
            )
            reliability = online_update_reliability(
                float(metrics.get("persistence", 0.0)),
                float(metrics.get("flicker", 1.0)),
                float(metrics.get("fade", 1.0)),
                float(metrics.get("global_shift", 1.0)),
                black,
            )
            task_signal = float(metrics.get("task_reward", reward))
            exploration_signal = float(metrics.get("exploration_reward", 0.0))
            safety_signal = float(metrics.get("safety_penalty", max(0.0, -reward)))
            novelty_signal = max(
                0.0,
                min(
                    1.0,
                    max(
                        float(metrics.get("controllable_novelty", 0.0)),
                        float(metrics.get("visual", 0.0)),
                        exploration_signal,
                    ),
                ),
            )
            episode_task_total += task_signal
            episode_exploration_total += exploration_signal
            episode_safety_total += safety_signal
            episode_reward_total += reward
            episode_novelty_total += novelty_signal
            episode_steps += 1
            episode_reward_mean = episode_reward_total / max(1, episode_steps)
            failure_type = _classify_failure_type(
                bool(done),
                episode_task_total,
                episode_safety_total,
                episode_reward_mean,
                episode_exploration_total / max(1, episode_steps),
            )
            if float(metrics.get("confirmed_death", 0.0)) > 0.5:
                failure_type = "terminal_death"
            elif float(metrics.get("cycle", 0.0)) > 0.65:
                failure_type = "cycle"
            success_rate = _bounded_episode_success_rate(
                episode_task_total,
                episode_exploration_total,
                episode_safety_total,
                episode_reward_mean,
                bool(done),
                failure_type,
                episode_steps,
            )
            if float(metrics.get("confirmed_victory", 0.0)) > 0.5:
                success_rate = max(success_rate, 0.95)
            online_queue.append(
                {
                    "episode_id": episode_id,
                    "state": state,
                    "action": action_id,
                    "duration_index": duration_index,
                    "reward": reward,
                    "task_reward": task_signal,
                    "exploration_reward": exploration_signal,
                    "safety_penalty": safety_signal,
                    "next_state": next_state,
                    "done": bool(done),
                    "reliability": reliability,
                    "success_rate": success_rate,
                    "failure_type": failure_type,
                    "novelty_score": episode_novelty_total / max(1, episode_steps),
                }
            )
            updates = _flush_online_n_step(
                np,
                online_queue,
                model,
                target_model,
                online_lr,
                horizon,
                online_td_discount,
                online_replay,
                int(runtime["online_replay_batch_size"]),
                int(config["online_replay_interval"]),
                False,
                config,
            )
            model_changed = model_changed or updates > 0
            if (
                updates > 0
                and int(model.get("online_updates", 0))
                and int(model.get("online_updates", 0)) % target_sync == 0
            ):
                soft_update_target_model(np, target_model, model, target_tau)

            memory_update_reward = compose_reward(metrics, config)
            state_memory_key = (memory_key, base_action)
            update_state_value_memory(
                state_memory,
                state_memory_key,
                memory_update_reward,
                float(config["online_learning_rate"]),
            )
            value_record, visit_record = state_memory[state_memory_key]
            update_state_memory_index(
                state_index,
                state_memory_key,
                value_record,
                visit_record,
            )
            state_action_visits[state_memory_key] = visit_record
            state_visit_totals[memory_key] = state_visit_totals.get(memory_key, 0) + 1
            dirty_state_values.add(state_memory_key)
            update_action_reward(profile, base_action, reward)
            update_action_effect(
                profile,
                base_action,
                float(metrics.get("visual", 0.0)),
            )
            update_action_risk(
                profile,
                base_action,
                float(metrics.get("safety_penalty", max(0.0, -reward))),
            )
            update_control_response(profile, base_action, reward)
            update_scene_control_response(
                profile,
                scene_context,
                base_action,
                reward,
            )
            update_scene_action_response(
                profile,
                scene_context,
                base_action,
                reward,
            )
            record_action_duration(profile, base_action, hold)
            if recent_actions:
                record_transition(
                    profile,
                    recent_actions[-1],
                    base_action,
                    recent_actions[-2] if len(recent_actions) > 1 else None,
                    2 if reward >= float(config["successful_transition_threshold"]) else 1,
                )
            if reward <= -float(config["successful_transition_threshold"]):
                failure_until[base_action] = (
                    steps + int(config["failure_cooldown_steps"])
                )

            recent_actions.append(base_action)
            recent_actions = recent_actions[-32:]
            steps += 1
            reward_sum += reward
            reward_observations += 1
            recent_reward += 0.18 * (reward - recent_reward)
            if len(rows) >= 96:
                insert_transitions(paths["db"], rows)
                rows.clear()
            if len(dirty_state_values) >= 256:
                save_state_value_memory(
                    paths["db"],
                    state_memory,
                    dirty_state_values,
                )
            if steps % planning_refresh == 0:
                if rows:
                    insert_transitions(paths["db"], rows)
                    rows.clear()
                graph = load_transition_graph(paths["db"], 50000, np, model)
            if model_changed and steps % checkpoint == 0:
                model["action_hash"] = actions_hash(profile["actions"])
                model["action_signatures"] = [
                    action_signature(action) for action in profile["actions"]
                ]
                target_model["action_hash"] = model["action_hash"]
                target_model["action_signatures"] = list(
                    model["action_signatures"]
                )
                save_model(np, active_path, model)
                save_model(np, active_target_path, target_model)
                model_changed = False

            if black or done:
                _flush_online_n_step(
                    np,
                    online_queue,
                    model,
                    target_model,
                    online_lr,
                    horizon,
                    online_td_discount,
                    online_replay,
                    int(runtime["online_replay_batch_size"]),
                    int(config["online_replay_interval"]),
                    True,
                    config,
                )
                if rows:
                    insert_transitions(paths["db"], rows)
                    rows.clear()
                episode_id = f"ai-{time.time_ns():x}-{os.getpid():x}"
                reset_episode_state()
            else:
                step += 1
                frame_history = next_frames
                action_history = next_actions
                duration_history = next_durations
                recent_state_keys.append(str(metrics.get("state_key", "")))
                recent_state_keys = recent_state_keys[-16:]
                previous_model_frame = next_model
                previous_raw = next_raw
                last_action_id = action_id
                last_duration = hold
    finally:
        release_all_inputs()
        _flush_online_n_step(
            np,
            online_queue,
            model,
            target_model,
            online_lr,
            horizon,
            online_td_discount,
            online_replay,
            int(runtime["online_replay_batch_size"]),
            int(config["online_replay_interval"]),
            True,
            config,
        )
        if rows:
            last = list(rows[-1])
            last[7] = 1
            rows[-1] = tuple(last)
            insert_transitions(paths["db"], rows)
        else:
            mark_episode_terminal(paths["db"], episode_id)
        save_state_value_memory(
            paths["db"],
            state_memory,
            dirty_state_values,
        )
        sampler.close()
        if online_ready and (
            model_changed or int(model.get("online_updates", 0)) > 0
        ):
            model["action_hash"] = actions_hash(profile["actions"])
            model["action_signatures"] = [
                action_signature(action) for action in profile["actions"]
            ]
            target_model["action_hash"] = model["action_hash"]
            target_model["action_signatures"] = list(model["action_signatures"])
            save_model(np, active_path, model)
            save_model(np, active_target_path, target_model)
        if steps:
            mean = max(-1.0, min(1.0, reward_sum / steps))
            sessions = int(profile.get("ai_sessions", 0))
            profile["last_ai_mean_reward"] = mean
            profile["ai_reward_ema"] = (
                mean
                if sessions == 0
                else float(profile.get("ai_reward_ema", 0.0))
                + 0.20 * (mean - float(profile.get("ai_reward_ema", 0.0)))
            )
            profile["ai_sessions"] = sessions + 1
            profile["needs_training"] = True
            save_profile(profile, paths)
        compact_state_values(
            paths["db"],
            int(config["state_memory_limit_per_game"]),
            action_count,
        )
        compact_experience(
            paths["db"],
            int(config["experience_limit_per_game"]),
            action_count,
        )
        wait_esc_release()
    mode = {
        "low_numpy": "低配 CPU/NumPy",
        "mid_onnx": "中配量化 ONNX",
        "high_directml": "高配 DirectML",
    }.get(runtime_tier, runtime_tier)
    warning = (
        "；画面可能未正确采集"
        if black_frames > max(20, steps // 2)
        else ""
    )
    mean_text = f"；平均任务反馈 {reward_sum / steps:.2f}" if steps else ""
    stage = (
        "人类BC→离线IQL已就绪，在线候选仅待升级验证"
        if online_ready
        else f"模仿保护模式（需至少 {minimum_human} 条人类转移并完成升级）"
    )
    return (
        f"AI结束：{profile['name']}；{mode}；执行 {steps} 步；{stage}"
        f"{mean_text}{warning}"
    )



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
