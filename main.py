import os
import sys
import json
import time
import math
import uuid
import random
import hashlib
import threading
import traceback
import statistics
import sqlite3
import zlib
import base64
from pathlib import Path
from collections import deque,Counter,defaultdict
import tkinter as tk
from tkinter import ttk
import ctypes
from ctypes import wintypes
APP_NAME="UniversalGameAI"
FORMAT_VERSION=3
FEATURE_W=48
FEATURE_H=27
PIXELS=FEATURE_W*FEATURE_H
FEATURE_LEN=PIXELS*3
FEATURE_ALGORITHM_VERSION=3
ACTION_ALGORITHM_VERSION=4
DATABASE_SCHEMA_VERSION=1
MAX_SAMPLES=1500
MAX_PROTOTYPES=320
SUPPORTED_BUTTONS={"left","right","middle"}
SUPPORTED_KINDS={"no_op","click","double_click","long_press","drag","scroll_v","scroll_h","move","hover"}
class POINT(ctypes.Structure):
    _fields_=[("x",wintypes.LONG),("y",wintypes.LONG)]
class RECT(ctypes.Structure):
    _fields_=[("left",wintypes.LONG),("top",wintypes.LONG),("right",wintypes.LONG),("bottom",wintypes.LONG)]
class MSG(ctypes.Structure):
    _fields_=[("hwnd",wintypes.HWND),("message",wintypes.UINT),("wParam",wintypes.WPARAM),("lParam",wintypes.LPARAM),("time",wintypes.DWORD),("pt",POINT)]
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_=[("biSize",wintypes.DWORD),("biWidth",wintypes.LONG),("biHeight",wintypes.LONG),("biPlanes",wintypes.WORD),("biBitCount",wintypes.WORD),("biCompression",wintypes.DWORD),("biSizeImage",wintypes.DWORD),("biXPelsPerMeter",wintypes.LONG),("biYPelsPerMeter",wintypes.LONG),("biClrUsed",wintypes.DWORD),("biClrImportant",wintypes.DWORD)]
class BITMAPINFO(ctypes.Structure):
    _fields_=[("bmiHeader",BITMAPINFOHEADER),("bmiColors",wintypes.DWORD*3)]
ULONG_PTR=ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p)==8 else ctypes.c_ulong
class MOUSEINPUT(ctypes.Structure):
    _fields_=[("dx",wintypes.LONG),("dy",wintypes.LONG),("mouseData",wintypes.DWORD),("dwFlags",wintypes.DWORD),("time",wintypes.DWORD),("dwExtraInfo",ULONG_PTR)]
class INPUTUNION(ctypes.Union):
    _fields_=[("mi",MOUSEINPUT)]
class INPUT(ctypes.Structure):
    _anonymous_=("u",)
    _fields_=[("type",wintypes.DWORD),("u",INPUTUNION)]
class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_=[("pt",POINT),("mouseData",wintypes.DWORD),("flags",wintypes.DWORD),("time",wintypes.DWORD),("dwExtraInfo",ULONG_PTR)]
class TargetUnavailable(RuntimeError):
    pass
class CaptureUnavailable(RuntimeError):
    pass
def finite_number(value):
    try:
        return math.isfinite(float(value))
    except Exception:
        return False
def canonical_bytes(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def add_checksum(data):
    result=dict(data)
    result.pop("checksum",None)
    result["checksum"]=hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result
def verify_checksum(data):
    if not isinstance(data,dict) or not isinstance(data.get("checksum"),str):
        return False
    expected=data.get("checksum")
    item=dict(data)
    item.pop("checksum",None)
    return hashlib.sha256(canonical_bytes(item)).hexdigest()==expected
def quantile(values,q):
    if not values:
        return 0.0
    ordered=sorted(float(x) for x in values)
    if len(ordered)==1:
        return ordered[0]
    pos=(len(ordered)-1)*q
    low=int(math.floor(pos))
    high=int(math.ceil(pos))
    if low==high:
        return ordered[low]
    part=pos-low
    return ordered[low]*(1.0-part)+ordered[high]*part
def path_length(path):
    total=0.0
    for a,b in zip(path,path[1:]):
        total+=math.hypot(float(b[0])-float(a[0]),float(b[1])-float(a[1]))
    return total
def direction_changes(path):
    if len(path)<3:
        return 0
    changes=0
    previous=None
    for a,b in zip(path,path[1:]):
        dx=float(b[0])-float(a[0])
        dy=float(b[1])-float(a[1])
        if abs(dx)+abs(dy)<0.002:
            continue
        angle=math.atan2(dy,dx)
        if previous is not None:
            delta=abs((angle-previous+math.pi)%(2*math.pi)-math.pi)
            if delta>math.radians(35):
                changes+=1
        previous=angle
    return changes
def resample_path(path,count=16):
    clean=[]
    for point in path or []:
        if isinstance(point,(list,tuple)) and len(point)>=2 and finite_number(point[0]) and finite_number(point[1]):
            clean.append([max(0.0,min(1.0,float(point[0]))),max(0.0,min(1.0,float(point[1])))])
    if not clean:
        return []
    if len(clean)==1:
        return [[round(clean[0][0],5),round(clean[0][1],5)] for _ in range(count)]
    distances=[0.0]
    for a,b in zip(clean,clean[1:]):
        distances.append(distances[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
    total=distances[-1]
    if total<1e-9:
        return [[round(clean[0][0],5),round(clean[0][1],5)] for _ in range(count)]
    result=[]
    segment=0
    for index in range(count):
        target=total*index/(count-1)
        while segment+1<len(distances) and distances[segment+1]<target:
            segment+=1
        if segment+1>=len(clean):
            point=clean[-1]
        else:
            span=max(1e-9,distances[segment+1]-distances[segment])
            ratio=(target-distances[segment])/span
            point=[clean[segment][0]+(clean[segment+1][0]-clean[segment][0])*ratio,clean[segment][1]+(clean[segment+1][1]-clean[segment][1])*ratio]
        result.append([round(point[0],5),round(point[1],5)])
    return result
def normalize_action(action):
    if not isinstance(action,dict):
        return None
    kind=str(action.get("kind",""))
    if kind not in SUPPORTED_KINDS:
        return None
    result={"kind":kind}
    if kind=="no_op":
        result["duration"]=round(max(0.05,min(3.0,float(action.get("duration",0.35)))),3)
        return result
    if kind in {"scroll_v","scroll_h"}:
        delta=int(action.get("delta",0))
        if delta==0:
            return None
        result["delta"]=max(-960,min(960,delta))
        point=resample_path(action.get("path") or [[0.5,0.5]],16)
        if not point:
            return None
        result["path"]=point
        result["duration"]=round(max(0.03,min(1.0,float(action.get("duration",0.08)))),3)
        return result
    path=resample_path(action.get("path"),16)
    if not path:
        return None
    result["path"]=path
    result["duration"]=round(max(0.03,min(3.0,float(action.get("duration",0.1)))),3)
    if kind in {"click","double_click","long_press","drag"}:
        button=str(action.get("button","left"))
        if button not in SUPPORTED_BUTTONS:
            return None
        result["button"]=button
    return result
def action_family_key(action):
    item=normalize_action(action)
    if not item:
        return ""
    kind=item["kind"]
    if kind in {"click","double_click","long_press","drag"}:
        return kind+"|"+item.get("button","left")
    if kind in {"scroll_v","scroll_h"}:
        return kind+"|"+str(1 if item["delta"]>0 else -1)
    return kind
def _main_direction(path):
    if not path or len(path)<2:
        return 0.0
    dx=float(path[-1][0])-float(path[0][0])
    dy=float(path[-1][1])-float(path[0][1])
    return math.atan2(dy,dx) if abs(dx)+abs(dy)>1e-9 else 0.0
def _path_rms(a,b):
    first=resample_path(a,16)
    second=resample_path(b,16)
    if not first or not second:
        return float("inf")
    return math.sqrt(sum((x[0]-y[0])**2+(x[1]-y[1])**2 for x,y in zip(first,second))/len(first))
def action_geometry_distance(first,second):
    a=normalize_action(first)
    b=normalize_action(second)
    if not a or not b or action_family_key(a)!=action_family_key(b):
        return float("inf")
    kind=a["kind"]
    duration_gap=abs(float(a.get("duration",0.1))-float(b.get("duration",0.1)))/3.0
    if kind=="no_op":
        return duration_gap
    if kind in {"scroll_v","scroll_h"}:
        pa=a["path"][-1]
        pb=b["path"][-1]
        point_gap=math.hypot(pa[0]-pb[0],pa[1]-pb[1])
        tier_a=min(8,max(1,round(abs(a["delta"])/120)))
        tier_b=min(8,max(1,round(abs(b["delta"])/120)))
        return 0.55*point_gap+0.35*abs(tier_a-tier_b)/7.0+0.10*duration_gap
    pa=a["path"]
    pb=b["path"]
    end_gap=math.hypot(pa[-1][0]-pb[-1][0],pa[-1][1]-pb[-1][1])
    if kind in {"click","double_click","long_press","hover"}:
        return 0.92*end_gap+0.08*duration_gap
    start_gap=math.hypot(pa[0][0]-pb[0][0],pa[0][1]-pb[0][1])
    path_gap=_path_rms(pa,pb)
    length_gap=abs(path_length(pa)-path_length(pb))
    angle_gap=abs((_main_direction(pa)-_main_direction(pb)+math.pi)%(2*math.pi)-math.pi)/math.pi
    if kind=="drag":
        return 0.24*start_gap+0.30*end_gap+0.25*path_gap+0.11*length_gap+0.07*angle_gap+0.03*duration_gap
    if kind=="move":
        return 0.18*start_gap+0.28*end_gap+0.32*path_gap+0.12*length_gap+0.08*angle_gap+0.02*duration_gap
    return end_gap
def action_cluster_limit(action):
    kind=normalize_action(action)["kind"]
    return {"no_op":0.22,"click":0.075,"double_click":0.085,"long_press":0.09,"hover":0.085,"drag":0.16,"move":0.18,"scroll_v":0.16,"scroll_h":0.16}.get(kind,0.1)
def action_signature(action):
    item=normalize_action(action)
    if not item:
        return ""
    kind=item["kind"]
    family=action_family_key(item)
    if kind=="no_op":
        return family
    if kind in {"scroll_v","scroll_h"}:
        point=item["path"][-1]
        tier=min(8,max(1,round(abs(item["delta"])/120)))
        return "|".join([family,str(tier),str(int(round(point[0]*12))),str(int(round(point[1]*8)))])
    path=item["path"]
    end=path[-1]
    if kind in {"click","double_click","long_press","hover"}:
        return "|".join([family,str(int(round(end[0]*20))),str(int(round(end[1]*12)))])
    start=path[0]
    direction=int(round(((_main_direction(path)+math.pi)/(2*math.pi))*8))%8
    return "|".join([family,str(int(round(start[0]*12))),str(int(round(start[1]*8))),str(int(round(end[0]*12))),str(int(round(end[1]*8))),str(direction)])
def feature_valid(feature):
    if isinstance(feature,(bytes,bytearray)):
        return len(feature)==FEATURE_LEN
    return isinstance(feature,(list,tuple)) and len(feature)==FEATURE_LEN and all(finite_number(value) for value in feature)
def feature_bytes(feature):
    if not feature_valid(feature):
        raise RuntimeError("特征尺寸无效")
    if isinstance(feature,bytes):
        return feature
    return bytes(int(max(0,min(255,round(float(value))))) for value in feature)
def gray_valid(gray):
    return isinstance(gray,(bytes,bytearray,list,tuple)) and len(gray)==PIXELS
def gray_bytes(gray):
    if not gray_valid(gray):
        return None
    if isinstance(gray,bytes):
        return gray
    return bytes(int(max(0,min(255,round(float(value))))) for value in gray)
def coarse_feature(feature):
    source=feature_bytes(feature)
    result=[]
    for channel in range(3):
        offset=channel*PIXELS
        for oy in range(9):
            y=min(FEATURE_H-1,int((oy+0.5)*FEATURE_H/9))
            for ox in range(12):
                x=min(FEATURE_W-1,int((ox+0.5)*FEATURE_W/12))
                result.append(source[offset+y*FEATURE_W+x])
    return bytes(result)
def coarse_distance(a,b):
    if not isinstance(a,(bytes,bytearray)) or not isinstance(b,(bytes,bytearray)) or len(a)!=len(b) or not a:
        return float("inf")
    return sum((int(x)-int(y))**2 for x,y in zip(a,b))/len(a)
def feature_distance(a,b):
    if not feature_valid(a) or not feature_valid(b):
        return float("inf")
    base=0.0
    edge=0.0
    diff=0.0
    for index in range(PIXELS):
        delta=float(a[index])-float(b[index])
        base+=delta*delta
    for index in range(PIXELS,PIXELS*2):
        delta=float(a[index])-float(b[index])
        edge+=delta*delta
    for index in range(PIXELS*2,PIXELS*3):
        delta=float(a[index])-float(b[index])
        diff+=delta*delta
    return 0.55*base/PIXELS+0.30*edge/PIXELS+0.15*diff/PIXELS
def visual_distance(a,b):
    if not feature_valid(a) or not feature_valid(b):
        return float("inf")
    total=0.0
    for index in range(PIXELS*2):
        delta=float(a[index])-float(b[index])
        total+=delta*delta
    return total/(PIXELS*2)
class WinBridge:
    def __init__(self):
        if os.name!="nt":
            raise RuntimeError("本程序仅支持Windows 11")
        version=sys.getwindowsversion()
        if int(version.major)!=10 or int(version.build)<22000:
            raise RuntimeError("本程序仅支持Windows 11（系统内部版本22000或更高）")
        self.user32=ctypes.WinDLL("user32",use_last_error=True)
        self.gdi32=ctypes.WinDLL("gdi32",use_last_error=True)
        self.kernel32=ctypes.WinDLL("kernel32",use_last_error=True)
        self._bind()
        try:
            self.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except Exception:
            try:
                self.user32.SetProcessDPIAware()
            except Exception:
                pass
        self.previous_frames={}
        self.frame_lock=threading.RLock()
        self.held=set()
        self.input_lock=threading.RLock()
    def _bind(self):
        self.WNDENUMPROC=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
        self.HOOKPROC=ctypes.WINFUNCTYPE(wintypes.LPARAM,ctypes.c_int,wintypes.WPARAM,wintypes.LPARAM)
        self.user32.EnumWindows.argtypes=[self.WNDENUMPROC,wintypes.LPARAM]
        self.user32.EnumWindows.restype=wintypes.BOOL
        self.user32.IsWindow.argtypes=[wintypes.HWND]
        self.user32.IsWindow.restype=wintypes.BOOL
        self.user32.IsWindowVisible.argtypes=[wintypes.HWND]
        self.user32.IsWindowVisible.restype=wintypes.BOOL
        self.user32.IsIconic.argtypes=[wintypes.HWND]
        self.user32.IsIconic.restype=wintypes.BOOL
        self.user32.GetForegroundWindow.argtypes=[]
        self.user32.GetForegroundWindow.restype=wintypes.HWND
        self.user32.GetWindowTextLengthW.argtypes=[wintypes.HWND]
        self.user32.GetWindowTextLengthW.restype=ctypes.c_int
        self.user32.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
        self.user32.GetWindowTextW.restype=ctypes.c_int
        self.user32.GetClassNameW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
        self.user32.GetClassNameW.restype=ctypes.c_int
        self.user32.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        self.user32.GetWindowThreadProcessId.restype=wintypes.DWORD
        self.user32.GetClientRect.argtypes=[wintypes.HWND,ctypes.POINTER(RECT)]
        self.user32.GetClientRect.restype=wintypes.BOOL
        self.user32.ClientToScreen.argtypes=[wintypes.HWND,ctypes.POINTER(POINT)]
        self.user32.ClientToScreen.restype=wintypes.BOOL
        self.user32.GetWindowRect.argtypes=[wintypes.HWND,ctypes.POINTER(RECT)]
        self.user32.GetWindowRect.restype=wintypes.BOOL
        self.user32.GetCursorPos.argtypes=[ctypes.POINTER(POINT)]
        self.user32.GetCursorPos.restype=wintypes.BOOL
        self.user32.GetAsyncKeyState.argtypes=[ctypes.c_int]
        self.user32.GetAsyncKeyState.restype=wintypes.SHORT
        self.user32.SetForegroundWindow.argtypes=[wintypes.HWND]
        self.user32.SetForegroundWindow.restype=wintypes.BOOL
        self.user32.SendInput.argtypes=[wintypes.UINT,ctypes.POINTER(INPUT),ctypes.c_int]
        self.user32.SendInput.restype=wintypes.UINT
        self.user32.GetSystemMetrics.argtypes=[ctypes.c_int]
        self.user32.GetSystemMetrics.restype=ctypes.c_int
        self.user32.GetDC.argtypes=[wintypes.HWND]
        self.user32.GetDC.restype=wintypes.HDC
        self.user32.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC]
        self.user32.ReleaseDC.restype=ctypes.c_int
        self.user32.PrintWindow.argtypes=[wintypes.HWND,wintypes.HDC,wintypes.UINT]
        self.user32.PrintWindow.restype=wintypes.BOOL
        self.user32.SetWindowsHookExW.argtypes=[ctypes.c_int,self.HOOKPROC,wintypes.HINSTANCE,wintypes.DWORD]
        self.user32.SetWindowsHookExW.restype=wintypes.HHOOK
        self.user32.CallNextHookEx.argtypes=[wintypes.HHOOK,ctypes.c_int,wintypes.WPARAM,wintypes.LPARAM]
        self.user32.CallNextHookEx.restype=wintypes.LPARAM
        self.user32.UnhookWindowsHookEx.argtypes=[wintypes.HHOOK]
        self.user32.UnhookWindowsHookEx.restype=wintypes.BOOL
        self.user32.GetMessageW.argtypes=[ctypes.POINTER(MSG),wintypes.HWND,wintypes.UINT,wintypes.UINT]
        self.user32.GetMessageW.restype=wintypes.BOOL
        self.user32.TranslateMessage.argtypes=[ctypes.POINTER(MSG)]
        self.user32.TranslateMessage.restype=wintypes.BOOL
        self.user32.DispatchMessageW.argtypes=[ctypes.POINTER(MSG)]
        self.user32.DispatchMessageW.restype=wintypes.LPARAM
        self.user32.PostThreadMessageW.argtypes=[wintypes.DWORD,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
        self.user32.PostThreadMessageW.restype=wintypes.BOOL
        self.kernel32.GetCurrentThreadId.argtypes=[]
        self.kernel32.GetCurrentThreadId.restype=wintypes.DWORD
        self.kernel32.GetModuleHandleW.argtypes=[wintypes.LPCWSTR]
        self.kernel32.GetModuleHandleW.restype=wintypes.HMODULE
        self.gdi32.CreateCompatibleDC.argtypes=[wintypes.HDC]
        self.gdi32.CreateCompatibleDC.restype=wintypes.HDC
        self.gdi32.DeleteDC.argtypes=[wintypes.HDC]
        self.gdi32.DeleteDC.restype=wintypes.BOOL
        self.gdi32.CreateDIBSection.argtypes=[wintypes.HDC,ctypes.POINTER(BITMAPINFO),wintypes.UINT,ctypes.POINTER(ctypes.c_void_p),wintypes.HANDLE,wintypes.DWORD]
        self.gdi32.CreateDIBSection.restype=wintypes.HBITMAP
        self.gdi32.SelectObject.argtypes=[wintypes.HDC,wintypes.HGDIOBJ]
        self.gdi32.SelectObject.restype=wintypes.HGDIOBJ
        self.gdi32.DeleteObject.argtypes=[wintypes.HGDIOBJ]
        self.gdi32.DeleteObject.restype=wintypes.BOOL
        self.gdi32.SetStretchBltMode.argtypes=[wintypes.HDC,ctypes.c_int]
        self.gdi32.SetStretchBltMode.restype=ctypes.c_int
        self.gdi32.StretchBlt.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.DWORD]
        self.gdi32.StretchBlt.restype=wintypes.BOOL
    def valid(self,hwnd):
        return bool(hwnd and self.user32.IsWindow(wintypes.HWND(hwnd)))
    def class_name(self,hwnd):
        buffer=ctypes.create_unicode_buffer(512)
        if not self.user32.GetClassNameW(wintypes.HWND(hwnd),buffer,512):
            raise ctypes.WinError(ctypes.get_last_error())
        return buffer.value
    def pid(self,hwnd):
        value=wintypes.DWORD()
        if not self.user32.GetWindowThreadProcessId(wintypes.HWND(hwnd),ctypes.byref(value)):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(value.value)
    def enum_windows(self):
        result=[]
        own_pid=os.getpid()
        def callback(hwnd,lparam):
            if not self.user32.IsWindowVisible(hwnd):
                return True
            length=self.user32.GetWindowTextLengthW(hwnd)
            if length<=0:
                return True
            title_buffer=ctypes.create_unicode_buffer(length+1)
            self.user32.GetWindowTextW(hwnd,title_buffer,length+1)
            title=title_buffer.value.strip()
            if not title:
                return True
            pid=self.pid(hwnd)
            if pid==own_pid:
                return True
            result.append({"hwnd":int(hwnd),"title":title,"class":self.class_name(hwnd),"pid":pid,"minimized":bool(self.user32.IsIconic(hwnd))})
            return True
        cb=self.WNDENUMPROC(callback)
        if not self.user32.EnumWindows(cb,0):
            raise ctypes.WinError(ctypes.get_last_error())
        result.sort(key=lambda item:(item["minimized"],item["title"].casefold()))
        return result
    def client_rect(self,hwnd):
        if not self.valid(hwnd):
            raise TargetUnavailable("目标窗口已关闭或句柄无效")
        if self.user32.IsIconic(wintypes.HWND(hwnd)):
            raise TargetUnavailable("目标窗口已最小化")
        rect=RECT()
        if not self.user32.GetClientRect(wintypes.HWND(hwnd),ctypes.byref(rect)):
            raise ctypes.WinError(ctypes.get_last_error())
        first=POINT(rect.left,rect.top)
        second=POINT(rect.right,rect.bottom)
        if not self.user32.ClientToScreen(wintypes.HWND(hwnd),ctypes.byref(first)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not self.user32.ClientToScreen(wintypes.HWND(hwnd),ctypes.byref(second)):
            raise ctypes.WinError(ctypes.get_last_error())
        width=int(second.x-first.x)
        height=int(second.y-first.y)
        if width<2 or height<2:
            raise TargetUnavailable("目标窗口客户区尺寸无效")
        return int(first.x),int(first.y),width,height
    def foreground_hwnd(self):
        return int(self.user32.GetForegroundWindow() or 0)
    def request_foreground(self,hwnd):
        if not self.valid(hwnd):
            return False
        result=bool(self.user32.SetForegroundWindow(wintypes.HWND(hwnd)))
        return result and self.foreground_hwnd()==int(hwnd)
    def validate_target(self,target,require_foreground=True):
        if not isinstance(target,dict):
            raise TargetUnavailable("目标窗口身份信息无效")
        hwnd=int(target.get("hwnd",0))
        if not self.valid(hwnd):
            raise TargetUnavailable("目标窗口已关闭或句柄无效")
        current_pid=self.pid(hwnd)
        if current_pid!=int(target.get("pid",-1)):
            raise TargetUnavailable("目标窗口PID已变化，窗口句柄可能被复用")
        current_class=self.class_name(hwnd)
        if current_class!=str(target.get("class","")):
            raise TargetUnavailable("目标窗口类名已变化，窗口身份不确定")
        if self.user32.IsIconic(wintypes.HWND(hwnd)):
            raise TargetUnavailable("目标窗口已最小化")
        if require_foreground and self.foreground_hwnd()!=hwnd:
            raise TargetUnavailable("目标窗口失去焦点，等待恢复")
        rect=self.client_rect(hwnd)
        return rect
    def cursor(self):
        point=POINT()
        if not self.user32.GetCursorPos(ctypes.byref(point)):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(point.x),int(point.y)
    def key_down(self,vk):
        return bool(self.user32.GetAsyncKeyState(vk)&0x8000)
    def _make_dib(self,reference_dc,width,height):
        memory=self.gdi32.CreateCompatibleDC(reference_dc)
        if not memory:
            raise ctypes.WinError(ctypes.get_last_error())
        info=BITMAPINFO()
        info.bmiHeader.biSize=ctypes.sizeof(BITMAPINFOHEADER)
        info.bmiHeader.biWidth=width
        info.bmiHeader.biHeight=-height
        info.bmiHeader.biPlanes=1
        info.bmiHeader.biBitCount=32
        info.bmiHeader.biCompression=0
        bits=ctypes.c_void_p()
        bitmap=self.gdi32.CreateDIBSection(reference_dc,ctypes.byref(info),0,ctypes.byref(bits),None,0)
        if not bitmap:
            self.gdi32.DeleteDC(memory)
            raise ctypes.WinError(ctypes.get_last_error())
        old=self.gdi32.SelectObject(memory,bitmap)
        return memory,bitmap,old,bits
    def _gray_from_raw(self,raw,width,height,out_w=FEATURE_W,out_h=FEATURE_H):
        result=[]
        for oy in range(out_h):
            sy=min(height-1,int((oy+0.5)*height/out_h))
            row=sy*width*4
            for ox in range(out_w):
                sx=min(width-1,int((ox+0.5)*width/out_w))
                index=row+sx*4
                b=raw[index]
                g=raw[index+1]
                r=raw[index+2]
                result.append((r*77+g*150+b*29)>>8)
        return result
    def _capture_print(self,hwnd,width,height):
        reference=self.user32.GetDC(wintypes.HWND(0))
        if not reference:
            raise ctypes.WinError(ctypes.get_last_error())
        memory=bitmap=old=bits=None
        try:
            memory,bitmap,old,bits=self._make_dib(reference,width,height)
            ctypes.memset(bits,0,width*height*4)
            if not self.user32.PrintWindow(wintypes.HWND(hwnd),memory,3):
                raise CaptureUnavailable("PrintWindow采集失败")
            raw=ctypes.string_at(bits.value,width*height*4)
            return self._gray_from_raw(raw,width,height)
        finally:
            if memory and old:
                self.gdi32.SelectObject(memory,old)
            if bitmap:
                self.gdi32.DeleteObject(bitmap)
            if memory:
                self.gdi32.DeleteDC(memory)
            self.user32.ReleaseDC(wintypes.HWND(0),reference)
    def _capture_dc(self,source_hwnd,sx,sy,width,height):
        source=self.user32.GetDC(wintypes.HWND(source_hwnd))
        if not source:
            raise ctypes.WinError(ctypes.get_last_error())
        memory=bitmap=old=bits=None
        try:
            memory,bitmap,old,bits=self._make_dib(source,FEATURE_W,FEATURE_H)
            self.gdi32.SetStretchBltMode(memory,4)
            if not self.gdi32.StretchBlt(memory,0,0,FEATURE_W,FEATURE_H,source,sx,sy,width,height,0x00CC0020):
                raise CaptureUnavailable("窗口DC采集失败")
            raw=ctypes.string_at(bits.value,FEATURE_W*FEATURE_H*4)
            return self._gray_from_raw(raw,FEATURE_W,FEATURE_H)
        finally:
            if memory and old:
                self.gdi32.SelectObject(memory,old)
            if bitmap:
                self.gdi32.DeleteObject(bitmap)
            if memory:
                self.gdi32.DeleteDC(memory)
            self.user32.ReleaseDC(wintypes.HWND(source_hwnd),source)
    def _quality(self,gray):
        mean=sum(gray)/len(gray)
        variance=sum((value-mean)*(value-mean) for value in gray)/len(gray)
        std=math.sqrt(variance)
        spread=max(gray)-min(gray)
        black=max(gray)<10 or mean<2.5
        solid=std<0.9 or spread<3
        return {"mean":mean,"std":std,"spread":spread,"black":black,"solid":solid,"valid":not black and not solid}
    def _normalized_gray(self,gray):
        mean=sum(gray)/len(gray)
        variance=sum((value-mean)*(value-mean) for value in gray)/len(gray)
        std=max(8.0,math.sqrt(variance))
        return bytes(int(max(0,min(255,round(128+(value-mean)*48/std)))) for value in gray)
    def feature_from_gray(self,gray,previous_gray=None):
        normalized=self._normalized_gray(gray)
        edges=[]
        for y in range(FEATURE_H):
            for x in range(FEATURE_W):
                index=y*FEATURE_W+x
                right=normalized[index+1] if x+1<FEATURE_W else normalized[index]
                down=normalized[index+FEATURE_W] if y+1<FEATURE_H else normalized[index]
                edges.append(min(255,abs(right-normalized[index])+abs(down-normalized[index])))
        previous=self._normalized_gray(previous_gray) if gray_valid(previous_gray) else None
        difference=bytes(PIXELS) if previous is None else bytes(abs(a-b) for a,b in zip(normalized,previous))
        return normalized+bytes(edges)+difference
    def _features(self,gray,key):
        now=time.time()
        with self.frame_lock:
            history=self.previous_frames.setdefault(int(key),deque(maxlen=12))
            previous=None
            for stamp,item in reversed(history):
                if stamp<=now-0.1:
                    previous=item
                    break
            history.append((now,gray_bytes(gray)))
        return self.feature_from_gray(gray,previous)
    def reset_frame_history(self,hwnd=None):
        with self.frame_lock:
            if hwnd is None:
                self.previous_frames.clear()
            else:
                self.previous_frames.pop(int(hwnd),None)
    def capture_gray(self,target,require_foreground_for_desktop=True):
        rect=self.validate_target(target,False)
        hwnd=int(target["hwnd"])
        x,y,width,height=rect
        attempts=[]
        candidates=[]
        for name,callback in [("PrintWindow",lambda:self._capture_print(hwnd,width,height)),("窗口DC",lambda:self._capture_dc(hwnd,0,0,width,height))]:
            try:
                gray=callback()
                quality=self._quality(gray)
                candidates.append((quality["std"],name,gray,quality))
                if quality["valid"]:
                    return {"gray":gray_bytes(gray),"method":name,"quality":quality}
                attempts.append(name+"返回黑屏或纯色帧")
            except Exception as error:
                attempts.append(name+"失败："+str(error))
        if not require_foreground_for_desktop or self.foreground_hwnd()==hwnd:
            try:
                gray=self._capture_dc(0,x,y,width,height)
                quality=self._quality(gray)
                candidates.append((quality["std"],"桌面裁剪",gray,quality))
                if quality["valid"]:
                    return {"gray":gray_bytes(gray),"method":"桌面裁剪","quality":quality}
                attempts.append("桌面裁剪返回黑屏或纯色帧")
            except Exception as error:
                attempts.append("桌面裁剪失败："+str(error))
        else:
            attempts.append("桌面裁剪被禁止：目标窗口不在前台")
        if candidates:
            best=max(candidates,key=lambda item:item[0])
            raise CaptureUnavailable("检测到无效画面（黑屏或纯色帧），已尝试三级采集："+"；".join(attempts)+"；最佳方式="+best[1])
        raise CaptureUnavailable("无法采集目标窗口："+"；".join(attempts))
    def capture(self,target,require_foreground_for_desktop=True):
        item=self.capture_gray(target,require_foreground_for_desktop)
        item["f"]=self._features(item["gray"],int(target["hwnd"]))
        item["motion_valid"]=True
        return item
    def _send(self,flags,data=0,dx=0,dy=0):
        item=INPUT()
        item.type=0
        item.mi=MOUSEINPUT(int(dx),int(dy),ctypes.c_ulong(int(data)&0xffffffff).value,int(flags),0,0)
        if self.user32.SendInput(1,ctypes.byref(item),ctypes.sizeof(INPUT))!=1:
            raise ctypes.WinError(ctypes.get_last_error())
    def move_cursor(self,x,y):
        left=self.user32.GetSystemMetrics(76)
        top=self.user32.GetSystemMetrics(77)
        width=self.user32.GetSystemMetrics(78)
        height=self.user32.GetSystemMetrics(79)
        nx=round((int(x)-left)*65535/max(1,width-1))
        ny=round((int(y)-top)*65535/max(1,height-1))
        self._send(0x0001|0x8000|0x4000,0,nx,ny)
    def button(self,button,down):
        flags={"left":(0x0002,0x0004),"right":(0x0008,0x0010),"middle":(0x0020,0x0040)}
        if button not in flags:
            raise RuntimeError("不支持的鼠标按钮")
        with self.input_lock:
            self._send(flags[button][0 if down else 1])
            if down:
                self.held.add(button)
            else:
                self.held.discard(button)
    def wheel(self,delta,horizontal=False):
        self._send(0x01000 if horizontal else 0x0800,int(delta))
    def release_all_buttons(self):
        with self.input_lock:
            for button in list(self.held):
                try:
                    flags={"left":0x0004,"right":0x0010,"middle":0x0040}
                    self._send(flags[button])
                except Exception:
                    pass
                self.held.discard(button)
            for flag in (0x0004,0x0010,0x0040):
                try:
                    self._send(flag)
                except Exception:
                    pass
class MouseMonitor:
    def __init__(self,bridge):
        self.bridge=bridge
        self.events=deque(maxlen=6000)
        self.lock=threading.Lock()
        self.thread=None
        self.thread_id=0
        self.hook=None
        self.callback=None
        self.ready=threading.Event()
        self.error=None
        self.last_move=0.0
    def start(self):
        self.thread=threading.Thread(target=self._run,daemon=True)
        self.thread.start()
        self.ready.wait(2.0)
        if self.error:
            raise RuntimeError(self.error)
        if not self.hook:
            raise RuntimeError("无法安装鼠标监听器")
    def _append(self,event):
        with self.lock:
            self.events.append(event)
    def _run(self):
        try:
            self.thread_id=int(self.bridge.kernel32.GetCurrentThreadId())
            messages={0x0200:"move",0x0201:"left_down",0x0202:"left_up",0x0204:"right_down",0x0205:"right_up",0x0207:"middle_down",0x0208:"middle_up",0x020A:"wheel",0x020E:"hwheel"}
            def callback(code,wparam,lparam):
                if code>=0 and int(wparam) in messages:
                    data=ctypes.cast(lparam,ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                    now=time.time()
                    kind=messages[int(wparam)]
                    if kind!="move" or now-self.last_move>=0.018:
                        if kind=="move":
                            self.last_move=now
                        event={"type":kind,"x":int(data.pt.x),"y":int(data.pt.y),"time":now}
                        if kind in {"wheel","hwheel"}:
                            raw=(int(data.mouseData)>>16)&0xffff
                            event["delta"]=raw-0x10000 if raw&0x8000 else raw
                        self._append(event)
                return self.bridge.user32.CallNextHookEx(self.hook,code,wparam,lparam)
            self.callback=self.bridge.HOOKPROC(callback)
            module=self.bridge.kernel32.GetModuleHandleW(None)
            self.hook=self.bridge.user32.SetWindowsHookExW(14,self.callback,module,0)
            if not self.hook:
                raise ctypes.WinError(ctypes.get_last_error())
            self.ready.set()
            message=MSG()
            while self.bridge.user32.GetMessageW(ctypes.byref(message),None,0,0)>0:
                self.bridge.user32.TranslateMessage(ctypes.byref(message))
                self.bridge.user32.DispatchMessageW(ctypes.byref(message))
        except Exception:
            self.error=traceback.format_exc()
            self.ready.set()
        finally:
            if self.hook:
                try:
                    self.bridge.user32.UnhookWindowsHookEx(self.hook)
                except Exception:
                    pass
                self.hook=None
    def drain(self):
        with self.lock:
            result=list(self.events)
            self.events.clear()
        return result
    def stop(self):
        if self.thread_id:
            try:
                self.bridge.user32.PostThreadMessageW(self.thread_id,0x0012,0,0)
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(1.0)
class FrameBuffer:
    def __init__(self,bridge,target,hz=20.0,seconds=2.0,motion_interval=0.1):
        self.bridge=bridge
        self.target=dict(target)
        self.interval=1.0/max(5.0,float(hz))
        self.motion_interval=max(0.05,min(0.25,float(motion_interval)))
        self.frames=deque(maxlen=max(12,int(float(hz)*float(seconds))+4))
        self.lock=threading.RLock()
        self.stop_event=threading.Event()
        self.ready=threading.Event()
        self.thread=None
        self.last_error=""
    def start(self):
        self.bridge.reset_frame_history(self.target.get("hwnd"))
        self.stop_event.clear()
        self.thread=threading.Thread(target=self._run,daemon=True)
        self.thread.start()
        return self
    def _run(self):
        next_time=time.time()
        while not self.stop_event.is_set():
            try:
                captured=self.bridge.capture_gray(self.target,True)
                stamp=time.time()
                gray=captured["gray"]
                with self.lock:
                    previous=None
                    for frame in reversed(self.frames):
                        if frame["time"]<=stamp-self.motion_interval:
                            previous=frame["gray"]
                            break
                feature=self.bridge.feature_from_gray(gray,previous)
                frame={"time":stamp,"f":feature,"coarse":coarse_feature(feature),"gray":gray,"method":captured["method"],"quality":captured["quality"],"motion_valid":previous is not None}
                with self.lock:
                    self.frames.append(frame)
                self.last_error=""
                self.ready.set()
            except Exception as error:
                self.last_error=str(error)
            next_time=max(next_time+self.interval,time.time())
            self.stop_event.wait(max(0.001,next_time-time.time()))
    def latest(self,before=None,max_age=0.6):
        now=time.time()
        with self.lock:
            candidates=list(self.frames)
        if before is not None:
            candidates=[frame for frame in candidates if frame["time"]<=float(before)]
        if not candidates:
            return None
        frame=candidates[-1]
        reference=float(before) if before is not None else now
        if reference-frame["time"]>max_age:
            return None
        return dict(frame)
    def latest_after(self,stamp,max_wait_age=0.8):
        with self.lock:
            for frame in reversed(self.frames):
                if frame["time"]>float(stamp):
                    return dict(frame)
        if time.time()-float(stamp)>max_wait_age:
            return None
        return None
    def snapshot(self,seconds=1.5):
        cutoff=time.time()-max(0.1,float(seconds))
        with self.lock:
            return [dict(frame) for frame in self.frames if frame["time"]>=cutoff]
    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(1.5)
class DataStore:
    def __init__(self):
        local=os.environ.get("LOCALAPPDATA")
        self.base=(Path(local) if local else Path.home()/"AppData"/"Local")/APP_NAME
        self.base.mkdir(parents=True,exist_ok=True)
        self.db_path=self.base/"universal_game_ai.db"
        self.lock=threading.RLock()
        self.model_cache={}
        self.db=sqlite3.connect(str(self.db_path),timeout=20.0,check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        with self.db:
            self.db.execute("PRAGMA foreign_keys=ON")
            self.db.execute("PRAGMA journal_mode=DELETE")
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("PRAGMA temp_store=MEMORY")
        self._initialize_schema()
        self._migrate_legacy()
    def _initialize_schema(self):
        with self.lock,self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS config_backups(id INTEGER PRIMARY KEY AUTOINCREMENT,created REAL NOT NULL,payload TEXT NOT NULL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS games(id TEXT PRIMARY KEY,name TEXT NOT NULL COLLATE NOCASE UNIQUE,created REAL NOT NULL,needs_review INTEGER NOT NULL DEFAULT 0,last_review REAL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS samples(id INTEGER PRIMARY KEY AUTOINCREMENT,game_id TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,created REAL NOT NULL,kind TEXT NOT NULL,action_signature TEXT NOT NULL,feature BLOB NOT NULL,coarse BLOB NOT NULL,action TEXT NOT NULL,source TEXT NOT NULL,context TEXT NOT NULL,thumbnail BLOB,weight REAL NOT NULL DEFAULT 1.0,fingerprint TEXT NOT NULL,UNIQUE(game_id,fingerprint))")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_samples_game_kind_created ON samples(game_id,kind,created)")
            self.db.execute("CREATE TABLE IF NOT EXISTS models(game_id TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,slot TEXT NOT NULL,saved REAL NOT NULL,created REAL NOT NULL,prototype_count INTEGER NOT NULL,validation TEXT NOT NULL,payload BLOB NOT NULL,checksum TEXT NOT NULL,PRIMARY KEY(game_id,slot))")
            self.db.execute("CREATE TABLE IF NOT EXISTS model_backups(id INTEGER PRIMARY KEY AUTOINCREMENT,game_id TEXT NOT NULL,created REAL NOT NULL,prototype_count INTEGER NOT NULL,validation TEXT NOT NULL,payload BLOB NOT NULL,checksum TEXT NOT NULL)")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_model_backups_game_created ON model_backups(game_id,created DESC)")
            self.db.execute("CREATE TABLE IF NOT EXISTS rejections(id INTEGER PRIMARY KEY AUTOINCREMENT,game_id TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,created REAL NOT NULL,feature BLOB NOT NULL,coarse BLOB NOT NULL,thumbnail BLOB,candidates TEXT NOT NULL,source TEXT NOT NULL)")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_rejections_game_created ON rejections(game_id,created DESC)")
            self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)",(str(DATABASE_SCHEMA_VERSION),))
    def _legacy_read_json(self,path,default=None):
        try:
            with path.open("r",encoding="utf-8") as stream:
                return json.load(stream)
        except Exception:
            return default
    def _migrate_legacy(self):
        with self.lock:
            row=self.db.execute("SELECT value FROM meta WHERE key='legacy_migrated'").fetchone()
            if row:
                return
        config_path=self.base/"config.json"
        backup_path=config_path.with_suffix(".json.bak")
        legacy_dirs=[self.base/name for name in ("samples","models","backups","temp")]
        legacy_present=config_path.exists() or backup_path.exists() or any(folder.exists() and any(folder.iterdir()) for folder in legacy_dirs)
        if not legacy_present:
            with self.lock,self.db:
                self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('legacy_migrated',?)",("1",))
            return
        config=self._legacy_read_json(config_path,None)
        if not isinstance(config,dict):
            config=self._legacy_read_json(backup_path,None)
        if not isinstance(config,dict) or not isinstance(config.get("games"),list):
            raise RuntimeError("旧配置损坏，且config.json.bak无法通过schema恢复；旧文件已保留")
        migration_safe=True
        game_ids=set()
        with self.lock,self.db:
            for game in config.get("games",[]):
                if isinstance(game,dict) and game.get("id") and str(game.get("name","")).strip():
                    gid=str(game["id"])
                    game_ids.add(gid)
                    self.db.execute("INSERT OR IGNORE INTO games(id,name,created,needs_review,last_review) VALUES(?,?,?,?,?)",(gid,str(game["name"]).strip(),float(game.get("created",time.time())),1 if game.get("needs_review") else 0,game.get("last_review")))
                else:
                    migration_safe=False
            selected=config.get("selected_game")
            if selected in game_ids:
                self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('selected_game',?)",(str(selected),))
            elif game_ids:
                self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('selected_game',?)",(sorted(game_ids)[0],))
        samples_dir=self.base/"samples"
        if samples_dir.exists():
            for path in samples_dir.glob("*.jsonl"):
                gid=path.stem
                if gid not in game_ids:
                    migration_safe=False
                    continue
                try:
                    with path.open("r",encoding="utf-8") as stream:
                        for line in stream:
                            try:
                                item=json.loads(line)
                                action=normalize_action(item.get("a"))
                                feature=item.get("f")
                                if not action or not feature_valid(feature):
                                    migration_safe=False
                                    continue
                                self._insert_sample(gid,feature,action,str(item.get("source","legacy")),item.get("context") if isinstance(item.get("context"),dict) else {},item.get("thumbnail"),float(item.get("weight",1.0)),False,False,float(item.get("created",time.time())))
                            except Exception:
                                migration_safe=False
                except Exception:
                    migration_safe=False
        models_dir=self.base/"models"
        if models_dir.exists():
            for path in models_dir.glob("*.json"):
                if path.name.endswith(".partial.json"):
                    continue
                item=self._legacy_read_json(path,None)
                gid=path.stem
                if gid.endswith(".partial"):
                    continue
                try:
                    if not isinstance(item,dict) or item.get("game_id")!=gid or item.get("complete") is not True:
                        migration_safe=False
                        continue
                    self.save_model(gid,item,True)
                except Exception:
                    migration_safe=False
        if not migration_safe:
            raise RuntimeError("旧数据迁移未能通过完整schema校验；数据库事务数据已保留，旧JSON/JSONL文件也未删除，请修复旧数据后重试")
        with self.lock,self.db:
            self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('legacy_migrated',?)",("1",))
        for path in (config_path,backup_path):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        for folder in legacy_dirs:
            if folder.exists():
                for child in list(folder.iterdir()):
                    try:
                        child.unlink()
                    except Exception:
                        pass
                try:
                    folder.rmdir()
                except Exception:
                    pass
    def _config_snapshot(self):
        games=[dict(row) for row in self.db.execute("SELECT id,name,created,needs_review,last_review FROM games ORDER BY created,id")]
        row=self.db.execute("SELECT value FROM meta WHERE key='selected_game'").fetchone()
        return {"format_version":FORMAT_VERSION,"games":games,"selected_game":row[0] if row else None}
    def games(self):
        with self.lock:
            rows=self.db.execute("SELECT id,name,created,needs_review,last_review FROM games ORDER BY created,id").fetchall()
        return [{"id":row["id"],"name":row["name"],"created":row["created"],"needs_review":bool(row["needs_review"]),"last_review":row["last_review"]} for row in rows]
    def selected_game(self):
        with self.lock:
            row=self.db.execute("SELECT value FROM meta WHERE key='selected_game'").fetchone()
        if not row:
            return None
        return next((game for game in self.games() if game["id"]==row[0]),None)
    def replace_games(self,games,selected):
        cleaned=[]
        names=set()
        for item in games:
            if not isinstance(item,dict) or not item.get("id") or not str(item.get("name","")).strip():
                continue
            name=str(item["name"]).strip()
            if name.casefold() in names:
                raise RuntimeError("游戏名称重复")
            names.add(name.casefold())
            cleaned.append({"id":str(item["id"]),"name":name,"created":float(item.get("created",time.time())),"needs_review":1 if item.get("needs_review") else 0,"last_review":item.get("last_review")})
        if selected not in {item["id"] for item in cleaned}:
            raise RuntimeError("所选游戏不存在")
        with self.lock,self.db:
            self.db.execute("INSERT INTO config_backups(created,payload) VALUES(?,?)",(time.time(),json.dumps(self._config_snapshot(),ensure_ascii=False,separators=(",",":"))))
            self.db.execute("DELETE FROM config_backups WHERE id NOT IN (SELECT id FROM config_backups ORDER BY id DESC LIMIT 5)")
            keep={item["id"] for item in cleaned}
            existing={row[0] for row in self.db.execute("SELECT id FROM games")}
            for gid in existing-keep:
                self.db.execute("DELETE FROM games WHERE id=?",(gid,))
                self.model_cache.pop(gid,None)
            for item in cleaned:
                self.db.execute("INSERT INTO games(id,name,created,needs_review,last_review) VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,created=excluded.created,needs_review=excluded.needs_review,last_review=excluded.last_review",(item["id"],item["name"],item["created"],item["needs_review"],item["last_review"]))
            self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('selected_game',?)",(selected,))
    def update_game(self,gid,**changes):
        allowed={"name","created","needs_review","last_review"}
        fields=[]
        values=[]
        for key,value in changes.items():
            if key in allowed:
                fields.append(key+"=?")
                values.append(1 if key=="needs_review" and value else 0 if key=="needs_review" else value)
        if not fields:
            return
        values.append(gid)
        with self.lock,self.db:
            self.db.execute("UPDATE games SET "+",".join(fields)+" WHERE id=?",values)
    def _sample_fingerprint(self,feature,action,source):
        data={"c":base64.b64encode(coarse_feature(feature)).decode("ascii"),"a":normalize_action(action),"source":str(source)}
        return hashlib.sha256(canonical_bytes(data)).hexdigest()
    def _insert_sample(self,gid,feature,action,source,context,thumbnail,weight,enforce_quota,mark_review,created=None):
        clean=normalize_action(action)
        if not clean or not feature_valid(feature):
            raise RuntimeError("拒绝保存无效样本")
        fbytes=feature_bytes(feature)
        cbytes=coarse_feature(fbytes)
        fingerprint=self._sample_fingerprint(fbytes,clean,source)
        kind=clean["kind"]
        with self.lock,self.db:
            if not self.db.execute("SELECT 1 FROM games WHERE id=?",(gid,)).fetchone():
                raise RuntimeError("游戏不存在")
            if enforce_quota and kind=="no_op":
                row=self.db.execute("SELECT SUM(CASE WHEN kind='no_op' THEN 1 ELSE 0 END) AS noops,SUM(CASE WHEN kind!='no_op' THEN 1 ELSE 0 END) AS actions FROM samples WHERE game_id=?",(gid,)).fetchone()
                noops=int(row["noops"] or 0)
                actions=int(row["actions"] or 0)
                allowed=max(1,actions//3)
                if noops>=allowed:
                    return False
            try:
                cursor=self.db.execute("INSERT INTO samples(game_id,created,kind,action_signature,feature,coarse,action,source,context,thumbnail,weight,fingerprint) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(gid,float(created or time.time()),kind,action_signature(clean),sqlite3.Binary(zlib.compress(fbytes,6)),sqlite3.Binary(cbytes),json.dumps(clean,ensure_ascii=False,separators=(",",":")),str(source),json.dumps(context if isinstance(context,dict) else {},ensure_ascii=False,separators=(",",":")),sqlite3.Binary(zlib.compress(gray_bytes(thumbnail),6)) if gray_valid(thumbnail) else None,float(max(0.1,min(10.0,weight))),fingerprint))
            except sqlite3.IntegrityError:
                return False
            if mark_review:
                self.db.execute("UPDATE games SET needs_review=1 WHERE id=?",(gid,))
            count=int(self.db.execute("SELECT COUNT(*) FROM samples WHERE game_id=?",(gid,)).fetchone()[0])
        if count>MAX_SAMPLES:
            self.compact_samples(gid,MAX_SAMPLES)
        return cursor.rowcount>0
    def append_sample(self,gid,feature,action,source,context=None,thumbnail=None,weight=1.0):
        return self._insert_sample(gid,feature,action,source,context or {},thumbnail,weight,True,True)
    def append_rejection(self,gid,feature,candidates,source="teach_reject",thumbnail=None):
        if not feature_valid(feature):
            raise RuntimeError("拒绝记录的特征无效")
        candidate_data=[]
        for item in candidates or []:
            action=normalize_action(item.get("a") if isinstance(item,dict) else item)
            if action:
                candidate_data.append({"action_signature":str(item.get("action_signature",action_signature(action))) if isinstance(item,dict) else action_signature(action),"a":action})
        with self.lock,self.db:
            self.db.execute("INSERT INTO rejections(game_id,created,feature,coarse,thumbnail,candidates,source) VALUES(?,?,?,?,?,?,?)",(gid,time.time(),sqlite3.Binary(zlib.compress(feature_bytes(feature),6)),sqlite3.Binary(coarse_feature(feature)),sqlite3.Binary(zlib.compress(gray_bytes(thumbnail),6)) if gray_valid(thumbnail) else None,json.dumps(candidate_data,ensure_ascii=False,separators=(",",":")),str(source)))
            self.db.execute("UPDATE games SET needs_review=1 WHERE id=?",(gid,))
    def load_samples(self,gid,limit=MAX_SAMPLES):
        with self.lock:
            rows=self.db.execute("SELECT created,feature,action,source,context,thumbnail,weight,fingerprint FROM samples WHERE game_id=? ORDER BY created DESC,id DESC LIMIT ?",(gid,int(limit))).fetchall()
        result=[]
        for row in reversed(rows):
            try:
                feature=zlib.decompress(row["feature"])
                action=normalize_action(json.loads(row["action"]))
                if not feature_valid(feature) or not action:
                    continue
                thumbnail=zlib.decompress(row["thumbnail"]) if row["thumbnail"] is not None else None
                result.append({"format_version":FORMAT_VERSION,"feature_width":FEATURE_W,"feature_height":FEATURE_H,"feature_algorithm_version":FEATURE_ALGORITHM_VERSION,"action_algorithm_version":ACTION_ALGORITHM_VERSION,"created":row["created"],"game_id":gid,"f":feature,"a":action,"source":row["source"],"context":json.loads(row["context"]),"thumbnail":thumbnail,"weight":row["weight"],"checksum":row["fingerprint"]})
            except Exception:
                continue
        return result,{"valid":len(result),"invalid":0,"total":len(result)}
    def load_rejections(self,gid,limit=500):
        with self.lock:
            rows=self.db.execute("SELECT created,feature,thumbnail,candidates,source FROM rejections WHERE game_id=? ORDER BY created DESC,id DESC LIMIT ?",(gid,int(limit))).fetchall()
        result=[]
        for row in rows:
            try:
                feature=zlib.decompress(row["feature"])
                candidates=json.loads(row["candidates"])
                thumbnail=zlib.decompress(row["thumbnail"]) if row["thumbnail"] is not None else None
                if feature_valid(feature) and isinstance(candidates,list):
                    result.append({"created":row["created"],"f":feature,"thumbnail":thumbnail,"candidates":candidates,"source":row["source"]})
            except Exception:
                pass
        return result
    def sample_stats(self,gid):
        with self.lock:
            row=self.db.execute("SELECT COUNT(*) AS total,COALESCE(SUM(length(feature)+length(coarse)+length(action)+length(context)+COALESCE(length(thumbnail),0)),0) AS bytes FROM samples WHERE game_id=?",(gid,)).fetchone()
        return {"valid":int(row["total"] or 0),"invalid":0,"total":int(row["total"] or 0),"bytes":int(row["bytes"] or 0)}
    def _select_diverse(self,rows,count):
        if count<=0:
            return []
        if len(rows)<=count:
            return list(rows)
        ordered=sorted(rows,key=lambda row:(float(row["weight"]),float(row["created"])),reverse=True)
        selected=[ordered.pop(0)]
        while ordered and len(selected)<count:
            candidates=ordered if len(ordered)<=180 else ordered[:180]
            best=max(candidates,key=lambda row:(min(coarse_distance(row["coarse"],chosen["coarse"]) for chosen in selected),float(row["weight"]),float(row["created"])))
            selected.append(best)
            ordered.remove(best)
        return selected
    def compact_samples(self,gid,keep=MAX_SAMPLES):
        keep=max(1,int(keep))
        with self.lock:
            rows=self.db.execute("SELECT id,kind,coarse,weight,created FROM samples WHERE game_id=?",(gid,)).fetchall()
        if len(rows)<=keep:
            return {"kept":len(rows),"removed":0,"invalid":0}
        groups=defaultdict(list)
        for row in rows:
            groups[row["kind"]].append(row)
        targets={kind:0 for kind in groups}
        if "no_op" in groups:
            targets["no_op"]=min(len(groups["no_op"]),int(keep*0.25))
        non_noop=[kind for kind in groups if kind!="no_op"]
        minimum=max(4,min(30,keep//max(1,len(non_noop)*4)))
        for kind in non_noop:
            targets[kind]=min(len(groups[kind]),minimum)
        while sum(targets.values())>keep:
            kind=max((key for key in targets if targets[key]>1),key=lambda key:targets[key],default=None)
            if kind is None:
                break
            targets[kind]-=1
        while sum(targets.values())<keep:
            candidates=[kind for kind in groups if targets[kind]<len(groups[kind]) and not (kind=="no_op" and targets[kind]>=int(keep*0.25))]
            if not candidates:
                break
            kind=max(candidates,key=lambda key:(len(groups[key])-targets[key])/(targets[key]+1))
            targets[kind]+=1
        chosen=[]
        for kind,items in groups.items():
            chosen.extend(self._select_diverse(items,targets.get(kind,0)))
        keep_ids={int(row["id"]) for row in chosen}
        with self.lock,self.db:
            placeholders=",".join("?" for _ in keep_ids)
            if keep_ids:
                self.db.execute("DELETE FROM samples WHERE game_id=? AND id NOT IN ("+placeholders+")",[gid]+list(keep_ids))
            else:
                self.db.execute("DELETE FROM samples WHERE game_id=?",(gid,))
        return {"kept":len(keep_ids),"removed":len(rows)-len(keep_ids),"invalid":0}
    def clear_game_data(self,gid):
        with self.lock,self.db:
            self.db.execute("DELETE FROM samples WHERE game_id=?",(gid,))
            self.db.execute("DELETE FROM models WHERE game_id=?",(gid,))
            self.db.execute("DELETE FROM model_backups WHERE game_id=?",(gid,))
            self.db.execute("DELETE FROM rejections WHERE game_id=?",(gid,))
            self.db.execute("UPDATE games SET needs_review=0,last_review=NULL WHERE id=?",(gid,))
        self.model_cache.pop(gid,None)
    def _pack_model(self,model):
        item=dict(model)
        packed=[]
        for proto in item.get("prototypes",[]):
            entry=dict(proto)
            entry["f_blob"]=base64.b64encode(zlib.compress(feature_bytes(entry.pop("f")),6)).decode("ascii")
            coarse=entry.pop("coarse",None)
            entry["coarse_blob"]=base64.b64encode(bytes(coarse) if isinstance(coarse,(bytes,bytearray)) else coarse_feature(zlib.decompress(base64.b64decode(entry["f_blob"])))).decode("ascii")
            packed.append(entry)
        item["prototypes"]=packed
        return zlib.compress(canonical_bytes(item),9)
    def _unpack_model(self,payload):
        item=json.loads(zlib.decompress(payload).decode("utf-8"))
        unpacked=[]
        for proto in item.get("prototypes",[]):
            entry=dict(proto)
            entry["f"]=zlib.decompress(base64.b64decode(entry.pop("f_blob")))
            entry["coarse"]=base64.b64decode(entry.pop("coarse_blob"))
            unpacked.append(entry)
        item["prototypes"]=unpacked
        return item
    def _model_valid(self,item,gid,complete=True):
        if not isinstance(item,dict) or item.get("format_version")!=FORMAT_VERSION or item.get("feature_width")!=FEATURE_W or item.get("feature_height")!=FEATURE_H or item.get("feature_algorithm_version")!=FEATURE_ALGORITHM_VERSION or item.get("action_algorithm_version")!=ACTION_ALGORITHM_VERSION or item.get("game_id")!=gid or bool(item.get("complete"))!=bool(complete):
            return False
        prototypes=item.get("prototypes")
        if not isinstance(prototypes,list) or not prototypes:
            return False
        for proto in prototypes:
            if not isinstance(proto,dict) or not str(proto.get("id","")) or not feature_valid(proto.get("f")) or not isinstance(proto.get("coarse"),(bytes,bytearray)) or len(proto.get("coarse"))!=324 or not normalize_action(proto.get("a")) or not str(proto.get("action_signature","")) or not finite_number(proto.get("threshold")) or float(proto.get("threshold"))<=0 or int(proto.get("support",0))<=0:
                return False
            conflict=proto.get("nearest_conflicting_distance")
            if conflict is not None and (not finite_number(conflict) or float(conflict)<=0):
                return False
            rejected=proto.get("nearest_rejected_distance")
            if rejected is not None and (not finite_number(rejected) or float(rejected)<0):
                return False
            if not finite_number(proto.get("minimum_second_candidate_gap",0)):
                return False
        validation=item.get("validation")
        return isinstance(validation,dict)
    def save_model(self,gid,model,complete=True):
        item=dict(model)
        item.update({"format_version":FORMAT_VERSION,"feature_width":FEATURE_W,"feature_height":FEATURE_H,"feature_algorithm_version":FEATURE_ALGORITHM_VERSION,"action_algorithm_version":ACTION_ALGORITHM_VERSION,"game_id":gid,"complete":bool(complete),"saved":time.time()})
        for proto in item.get("prototypes",[]):
            if "coarse" not in proto and feature_valid(proto.get("f")):
                proto["coarse"]=coarse_feature(proto["f"])
        if not self._model_valid(item,gid,complete):
            raise RuntimeError("模型完整schema校验失败")
        payload=self._pack_model(item)
        checksum=hashlib.sha256(payload).hexdigest()
        slot="complete" if complete else "partial"
        validation=json.dumps(item.get("validation",{}),ensure_ascii=False,separators=(",",":"))
        with self.lock,self.db:
            if complete:
                old=self.db.execute("SELECT saved,prototype_count,validation,payload,checksum FROM models WHERE game_id=? AND slot='complete'",(gid,)).fetchone()
                if old:
                    self.db.execute("INSERT INTO model_backups(game_id,created,prototype_count,validation,payload,checksum) VALUES(?,?,?,?,?,?)",(gid,old["saved"],old["prototype_count"],old["validation"],old["payload"],old["checksum"]))
                    self.db.execute("DELETE FROM model_backups WHERE game_id=? AND id NOT IN (SELECT id FROM model_backups WHERE game_id=? ORDER BY id DESC LIMIT 5)",(gid,gid))
            self.db.execute("INSERT INTO models(game_id,slot,saved,created,prototype_count,validation,payload,checksum) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(game_id,slot) DO UPDATE SET saved=excluded.saved,created=excluded.created,prototype_count=excluded.prototype_count,validation=excluded.validation,payload=excluded.payload,checksum=excluded.checksum",(gid,slot,item["saved"],float(item.get("created",time.time())),len(item["prototypes"]),validation,sqlite3.Binary(payload),checksum))
            if complete:
                self.db.execute("DELETE FROM models WHERE game_id=? AND slot='partial'",(gid,))
                self.db.execute("UPDATE games SET needs_review=0,last_review=? WHERE id=?",(float(item.get("created",time.time())),gid))
        if complete:
            self.model_cache[gid]=item
    def _row_model(self,row,gid,complete):
        if not row or hashlib.sha256(row["payload"]).hexdigest()!=row["checksum"]:
            return None
        try:
            item=self._unpack_model(row["payload"])
        except Exception:
            return None
        return item if self._model_valid(item,gid,complete) else None
    def load_model(self,gid):
        cached=self.model_cache.get(gid)
        if cached is not None and self._model_valid(cached,gid,True):
            return cached
        with self.lock:
            row=self.db.execute("SELECT payload,checksum FROM models WHERE game_id=? AND slot='complete'",(gid,)).fetchone()
        item=self._row_model(row,gid,True)
        if item:
            self.model_cache[gid]=item
            return item
        with self.lock:
            backups=self.db.execute("SELECT id,created,prototype_count,validation,payload,checksum FROM model_backups WHERE game_id=? ORDER BY id DESC",(gid,)).fetchall()
        for backup in backups:
            recovered=self._row_model(backup,gid,True)
            if recovered:
                with self.lock,self.db:
                    self.db.execute("INSERT OR REPLACE INTO models(game_id,slot,saved,created,prototype_count,validation,payload,checksum) VALUES(?,?,?,?,?,?,?,?)",(gid,"complete",float(recovered.get("saved",backup["created"])),float(recovered.get("created",backup["created"])),len(recovered["prototypes"]),json.dumps(recovered.get("validation",{}),ensure_ascii=False,separators=(",",":")),backup["payload"],backup["checksum"]))
                self.model_cache[gid]=recovered
                return recovered
        if row:
            raise RuntimeError("模型版本、游戏ID、特征尺寸、算法版本或原型schema校验失败，且无法从数据库备份恢复")
        return None
    def model_metadata(self,gid):
        with self.lock:
            row=self.db.execute("SELECT slot,saved,created,prototype_count,validation FROM models WHERE game_id=? ORDER BY saved DESC LIMIT 1",(gid,)).fetchone()
        if not row:
            return None
        try:
            validation=json.loads(row["validation"])
        except Exception:
            validation={"status":"invalid"}
        return {"slot":row["slot"],"saved":row["saved"],"created":row["created"],"prototype_count":row["prototype_count"],"validation":validation}
    def restore_model_backup(self,gid):
        with self.lock:
            backups=self.db.execute("SELECT id,created,prototype_count,validation,payload,checksum FROM model_backups WHERE game_id=? ORDER BY id DESC",(gid,)).fetchall()
        for backup in backups:
            item=self._row_model(backup,gid,True)
            if item:
                with self.lock,self.db:
                    self.db.execute("INSERT OR REPLACE INTO models(game_id,slot,saved,created,prototype_count,validation,payload,checksum) VALUES(?,?,?,?,?,?,?,?)",(gid,"complete",float(item.get("saved",backup["created"])),float(item.get("created",backup["created"])),len(item["prototypes"]),json.dumps(item.get("validation",{}),ensure_ascii=False,separators=(",",":")),backup["payload"],backup["checksum"]))
                self.model_cache[gid]=item
                return True
        raise RuntimeError("没有通过完整版本、游戏ID、特征尺寸、算法版本和原型schema校验的模型备份")
    def close(self):
        with self.lock:
            try:
                self.db.close()
            except Exception:
                pass
class App:
    def __init__(self,root):
        self.root=root
        self.api=WinBridge()
        self.store=DataStore()
        self.selected_game=self.store.selected_game()
        self.selected_window=None
        self.mode=None
        self.stop_event=None
        self.mode_thread=None
        self.controls=[]
        self.stop_button=None
        self.ask_window=None
        self.ask_buffer=None
        self.ask_after_ids=set()
        self.ask_escape_armed=False
        self.error_recent={}
        self.error_windows=[]
        self.status=tk.StringVar(value="就绪")
        self.game_text=tk.StringVar(value="未选择")
        self.window_text=tk.StringVar(value="未选择")
        self.window_detail=tk.StringVar(value="PID：-  类名：-  客户区：-")
        self.sample_text=tk.StringVar(value="样本：有效0  废弃0  数据0 KB")
        self.model_text=tk.StringVar(value="模型：无  需要复习：否")
        self.confidence_text=tk.StringVar(value="训练置信度：-")
        self.progress_value=tk.DoubleVar(value=0.0)
        self.root.report_callback_exception=self.tk_exception
        self._build()
        self._refresh_all()
        self.root.protocol("WM_DELETE_WINDOW",self.close)
        self.root.after(1200,self.periodic_refresh)
    def _build(self):
        self.root.title("通用游戏AI")
        self.root.geometry("760x620")
        self.root.minsize(680,560)
        self.root.option_add("*Font",("Microsoft YaHei UI",10))
        outer=ttk.Frame(self.root,padding=18)
        outer.pack(fill="both",expand=True)
        ttk.Label(outer,text="通用游戏AI控制面板",font=("Microsoft YaHei UI",18,"bold")).pack(anchor="w",pady=(0,12))
        info=ttk.LabelFrame(outer,text="当前状态",padding=12)
        info.pack(fill="x",pady=(0,12))
        labels=[("当前游戏：",self.game_text),("目标窗口：",self.window_text),("窗口身份：",self.window_detail),("数据统计：",self.sample_text),("模型状态：",self.model_text),("识别状态：",self.confidence_text)]
        for row,(name,value) in enumerate(labels):
            ttk.Label(info,text=name).grid(row=row,column=0,sticky="nw",pady=2)
            ttk.Label(info,textvariable=value,wraplength=590).grid(row=row,column=1,sticky="nw",pady=2)
        info.columnconfigure(1,weight=1)
        grid=ttk.Frame(outer)
        grid.pack(fill="both",expand=True)
        specs=[("游戏",self.open_game_dialog),("选择窗口",self.open_window_dialog),("学习",self.start_learning),("复习",self.start_review),("训练",self.start_training),("请教",self.start_ask),("停止",self.request_stop),("数据清理",self.open_data_dialog)]
        for index,(text,command) in enumerate(specs):
            button=ttk.Button(grid,text=text,command=command)
            button.grid(row=index//2,column=index%2,sticky="nsew",padx=7,pady=7,ipady=11)
            if text=="停止":
                self.stop_button=button
                button.configure(state="disabled")
            else:
                self.controls.append(button)
        for column in range(2):
            grid.columnconfigure(column,weight=1)
        for row in range(4):
            grid.rowconfigure(row,weight=1)
        ttk.Progressbar(outer,variable=self.progress_value,maximum=100).pack(fill="x",pady=(12,8))
        bottom=ttk.Frame(outer)
        bottom.pack(fill="x")
        ttk.Label(bottom,text="状态：").pack(side="left")
        ttk.Label(bottom,textvariable=self.status,wraplength=540).pack(side="left",fill="x",expand=True)
        ttk.Label(bottom,text="ESC或“停止”结束").pack(side="right")
    def tk_exception(self,exc_type,exc_value,exc_traceback):
        self.show_error("".join(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def ui(self,callback):
        try:
            self.root.after(0,callback)
        except Exception:
            pass
    def set_status(self,text):
        self.ui(lambda:self.status.set(str(text)))
    def set_confidence(self,text):
        self.ui(lambda:self.confidence_text.set(str(text)))
    def set_progress(self,value):
        self.ui(lambda:self.progress_value.set(max(0.0,min(100.0,float(value)))))
    def show_error(self,text):
        if threading.current_thread() is not threading.main_thread():
            self.ui(lambda:self.show_error(text))
            return
        message=str(text).strip() or "未知错误"
        digest=hashlib.sha256(message.encode("utf-8","replace")).hexdigest()
        now=time.time()
        self.error_recent={key:value for key,value in self.error_recent.items() if now-value<6.0}
        if digest in self.error_recent:
            return
        self.error_recent[digest]=now
        win=tk.Toplevel(self.root)
        self.error_windows.append(win)
        win.title("报错信息")
        win.geometry("700x390")
        win.minsize(500,300)
        win.transient(self.root)
        frame=ttk.Frame(win,padding=14)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="报错信息",font=("Microsoft YaHei UI",14,"bold")).pack(anchor="w",pady=(0,8))
        body=ttk.Frame(frame)
        body.pack(fill="both",expand=True)
        widget=tk.Text(body,wrap="word",font=("Microsoft YaHei UI",10),relief="solid",borderwidth=1)
        scroll=ttk.Scrollbar(body,orient="vertical",command=widget.yview)
        widget.configure(yscrollcommand=scroll.set)
        widget.pack(side="left",fill="both",expand=True)
        scroll.pack(side="right",fill="y")
        widget.insert("1.0",message)
        widget.configure(state="disabled")
        def close_error():
            try:
                self.error_windows.remove(win)
            except ValueError:
                pass
            win.destroy()
        ttk.Button(frame,text="确认",command=close_error).pack(pady=(12,0),ipadx=24)
        win.bind("<Return>",lambda event:close_error())
        win.protocol("WM_DELETE_WINDOW",close_error)
        win.wait_visibility()
        win.focus_force()
    def prompt_text(self,title,label,initial=""):
        result={"value":None}
        win=tk.Toplevel(self.root)
        win.title(title)
        win.geometry("440x190")
        win.resizable(False,False)
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=18)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text=label).pack(anchor="w")
        value=tk.StringVar(value=initial)
        entry=ttk.Entry(frame,textvariable=value)
        entry.pack(fill="x",pady=12)
        error=tk.StringVar()
        ttk.Label(frame,textvariable=error).pack(anchor="w")
        buttons=ttk.Frame(frame)
        buttons.pack(side="bottom")
        def confirm():
            text=value.get().strip()
            if not text:
                error.set("名称不能为空")
                return
            if len(text)>80:
                error.set("名称不能超过80个字符")
                return
            result["value"]=text
            win.destroy()
        ttk.Button(buttons,text="确认",command=confirm).pack(side="left",padx=6)
        ttk.Button(buttons,text="取消",command=win.destroy).pack(side="left",padx=6)
        entry.bind("<Return>",lambda event:confirm())
        entry.bind("<Escape>",lambda event:win.destroy())
        entry.focus_set()
        win.wait_window()
        return result["value"]
    def confirm_dialog(self,title,text):
        result={"value":False}
        win=tk.Toplevel(self.root)
        win.title(title)
        win.geometry("500x210")
        win.resizable(False,False)
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=20)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text=text,wraplength=450,justify="left").pack(fill="x",expand=True)
        buttons=ttk.Frame(frame)
        buttons.pack(side="bottom")
        def confirm():
            result["value"]=True
            win.destroy()
        ttk.Button(buttons,text="确认",command=confirm).pack(side="left",padx=6)
        ttk.Button(buttons,text="取消",command=win.destroy).pack(side="left",padx=6)
        win.wait_window()
        return result["value"]
    def _refresh_all(self):
        self.game_text.set(self.selected_game["name"] if self.selected_game else "未选择")
        if self.selected_window:
            self.window_text.set(self.selected_window.get("title","未命名窗口"))
            try:
                rect=self.api.validate_target(self.selected_window,False)
                self.window_detail.set("PID："+str(self.selected_window["pid"])+"  类名："+self.selected_window["class"]+"  客户区："+str(rect[2])+"×"+str(rect[3]))
            except Exception as error:
                self.window_detail.set("PID："+str(self.selected_window.get("pid","-"))+"  类名："+str(self.selected_window.get("class","-"))+"  "+str(error))
        else:
            self.window_text.set("未选择")
            self.window_detail.set("PID：-  类名：-  客户区：-")
        self.refresh_data_stats()
    def refresh_data_stats(self):
        if not self.selected_game:
            self.sample_text.set("样本：有效0  废弃0  数据0 KB")
            self.model_text.set("模型：无  需要复习：否")
            return
        gid=self.selected_game["id"]
        try:
            stats=self.store.sample_stats(gid)
            self.sample_text.set("样本：有效"+str(stats["valid"])+"  废弃"+str(stats["invalid"])+"  数据"+str(round(stats["bytes"]/1024,1))+" KB")
            metadata=self.store.model_metadata(gid)
            needs=bool(next((game.get("needs_review") for game in self.store.games() if game["id"]==gid),False))
            if metadata:
                created=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(metadata.get("created",0)))
                validation=metadata.get("validation",{})
                holdout=int(validation.get("holdout",0) or 0)
                accepted=int(validation.get("accepted",0) or 0)
                coverage=float(validation.get("coverage",0.0) or 0.0)
                reject_rate=float(validation.get("reject_rate",1.0) or 0.0)
                overall=float(validation.get("overall_accuracy",0.0) or 0.0)
                accepted_error=validation.get("accepted_error_rate")
                status=str(validation.get("status","insufficient"))
                if accepted_error is None:
                    error_text="接受样本错误率无法计算（验证不足）"
                else:
                    error_text="接受样本错误率"+str(round(float(accepted_error)*100,2))+"%（"+("通过" if status=="passed" else "未通过")+"）"
                detail="留出"+str(holdout)+" 接受"+str(accepted)+" 覆盖"+str(round(coverage*100,1))+"% 总体正确"+str(round(overall*100,1))+"% 拒识"+str(round(reject_rate*100,1))+"%"
                model_kind="完整模型" if metadata.get("slot")=="complete" else "未验收临时模型（旧完整模型如存在则保留）"
                self.model_text.set(model_kind+"："+str(metadata.get("prototype_count",0))+"个原型  最近复习："+created+"  "+error_text+"  "+detail+"  需要复习："+("是" if needs else "否"))
            else:
                self.model_text.set("模型：无  需要复习："+("是" if needs else "否"))
        except Exception as error:
            self.sample_text.set("数据统计失败")
            self.model_text.set(str(error))
    def periodic_refresh(self):
        try:
            if not self.mode:
                self._refresh_all()
        finally:
            try:
                self.root.after(1200,self.periodic_refresh)
            except Exception:
                pass
    def open_game_dialog(self):
        if self.mode:
            self.show_error("请先停止当前模式")
            return
        games=[dict(item) for item in self.store.games()]
        selected_id=self.selected_game["id"] if self.selected_game else None
        win=tk.Toplevel(self.root)
        win.title("游戏")
        win.geometry("540x450")
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=16)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="选择、新建、编辑或删除游戏名称",font=("Microsoft YaHei UI",13,"bold")).pack(anchor="w",pady=(0,10))
        list_frame=ttk.Frame(frame)
        list_frame.pack(fill="both",expand=True)
        box=tk.Listbox(list_frame,exportselection=False,font=("Microsoft YaHei UI",11))
        scroll=ttk.Scrollbar(list_frame,orient="vertical",command=box.yview)
        box.configure(yscrollcommand=scroll.set)
        box.pack(side="left",fill="both",expand=True)
        scroll.pack(side="right",fill="y")
        def refresh(target=None):
            box.delete(0,"end")
            for game in games:
                suffix="  [需要复习]" if game.get("needs_review") else ""
                box.insert("end",game["name"]+suffix)
            wanted=target or selected_id
            for index,game in enumerate(games):
                if game["id"]==wanted:
                    box.selection_set(index)
                    box.see(index)
                    break
        def current_index():
            selection=box.curselection()
            return selection[0] if selection else None
        def add_game():
            name=self.prompt_text("新建游戏","输入游戏名称")
            if name is None:
                return
            if any(item["name"].casefold()==name.casefold() for item in games):
                self.show_error("游戏名称已存在")
                return
            game={"id":uuid.uuid4().hex,"name":name,"created":time.time(),"needs_review":False,"last_review":None}
            games.append(game)
            refresh(game["id"])
        def edit_game():
            index=current_index()
            if index is None:
                self.show_error("请先选择一个游戏")
                return
            name=self.prompt_text("编辑游戏","修改游戏名称",games[index]["name"])
            if name is None:
                return
            if any(position!=index and item["name"].casefold()==name.casefold() for position,item in enumerate(games)):
                self.show_error("游戏名称已存在")
                return
            games[index]["name"]=name
            refresh(games[index]["id"])
        def delete_game():
            index=current_index()
            if index is None:
                self.show_error("请先选择一个游戏")
                return
            if not self.confirm_dialog("删除游戏","确认删除“"+games[index]["name"]+"”及其学习数据、模型和备份吗？"):
                return
            games.pop(index)
            refresh(games[min(index,len(games)-1)]["id"] if games else None)
        def confirm():
            selection=box.curselection()
            if not selection:
                self.show_error("请先选择一个游戏；如果列表为空，请先新建游戏")
                return
            chosen=games[selection[0]]
            self.store.replace_games(games,chosen["id"])
            self.selected_game=dict(chosen)
            self._refresh_all()
            self.status.set("已选择游戏："+chosen["name"])
            win.destroy()
        tools=ttk.Frame(frame)
        tools.pack(fill="x",pady=10)
        ttk.Button(tools,text="新建",command=add_game).pack(side="left",padx=(0,6))
        ttk.Button(tools,text="编辑",command=edit_game).pack(side="left",padx=6)
        ttk.Button(tools,text="删除",command=delete_game).pack(side="left",padx=6)
        actions=ttk.Frame(frame)
        actions.pack(fill="x")
        ttk.Button(actions,text="确认",command=confirm).pack(side="right",padx=(6,0))
        ttk.Button(actions,text="取消",command=win.destroy).pack(side="right")
        box.bind("<Double-Button-1>",lambda event:confirm())
        refresh()
        win.wait_visibility()
        box.focus_set()
    def open_window_dialog(self):
        if self.mode:
            self.show_error("请先停止当前模式")
            return
        win=tk.Toplevel(self.root)
        win.title("选择窗口")
        win.geometry("800x520")
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=16)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="选择雷电模拟器窗口或其他窗口",font=("Microsoft YaHei UI",13,"bold")).pack(anchor="w",pady=(0,10))
        list_frame=ttk.Frame(frame)
        list_frame.pack(fill="both",expand=True)
        box=tk.Listbox(list_frame,exportselection=False,font=("Microsoft YaHei UI",10))
        scroll=ttk.Scrollbar(list_frame,orient="vertical",command=box.yview)
        box.configure(yscrollcommand=scroll.set)
        box.pack(side="left",fill="both",expand=True)
        scroll.pack(side="right",fill="y")
        windows=[]
        def refresh():
            nonlocal windows
            windows=self.api.enum_windows()
            box.delete(0,"end")
            selected_index=None
            for index,item in enumerate(windows):
                prefix="[最小化] " if item["minimized"] else ""
                box.insert("end",prefix+item["title"]+"  [PID "+str(item["pid"])+"]  ["+item["class"]+"]")
                if self.selected_window and item["hwnd"]==self.selected_window["hwnd"] and item["pid"]==self.selected_window["pid"] and item["class"]==self.selected_window["class"]:
                    selected_index=index
            if selected_index is not None:
                box.selection_set(selected_index)
                box.see(selected_index)
        def confirm():
            selection=box.curselection()
            if not selection:
                self.show_error("请先选择一个窗口")
                return
            item=dict(windows[selection[0]])
            self.api.validate_target(item,False)
            self.selected_window=item
            self.api.reset_frame_history(item["hwnd"])
            self._refresh_all()
            self.status.set("已选择窗口："+item["title"])
            win.destroy()
        tools=ttk.Frame(frame)
        tools.pack(fill="x",pady=(10,0))
        ttk.Button(tools,text="刷新",command=refresh).pack(side="left")
        ttk.Button(tools,text="确认",command=confirm).pack(side="right",padx=(6,0))
        ttk.Button(tools,text="取消",command=win.destroy).pack(side="right")
        box.bind("<Double-Button-1>",lambda event:confirm())
        refresh()
        win.wait_visibility()
        box.focus_set()
    def require_game(self):
        if not self.selected_game:
            raise RuntimeError("请先点击“游戏”按钮选择或新建游戏")
        return self.selected_game
    def require_window(self,foreground=False):
        if not self.selected_window:
            raise RuntimeError("请先点击“选择窗口”按钮选择目标窗口")
        self.api.validate_target(self.selected_window,foreground)
        return self.selected_window
    def set_controls(self,running):
        for button in self.controls:
            button.configure(state="disabled" if running else "normal")
        if self.stop_button:
            self.stop_button.configure(state="normal" if running else "disabled")
    def start_worker(self,name,target,needs_window=False):
        if self.mode:
            self.show_error("当前正在“"+self.mode+"”，请先停止")
            return
        try:
            self.require_game()
            if needs_window:
                self.require_window(False)
        except Exception as error:
            self.show_error(str(error))
            return
        self.mode=name
        self.stop_event=threading.Event()
        self.set_controls(True)
        self.progress_value.set(0)
        self.status.set(name+"已开始，按ESC或点击“停止”结束")
        self.mode_thread=threading.Thread(target=self.worker_entry,args=(name,target),daemon=True)
        self.mode_thread.start()
    def worker_entry(self,name,target):
        error=None
        final_text=name+"已结束"
        try:
            final_text=target()
        except Exception:
            error=traceback.format_exc()
        finally:
            self.api.release_all_buttons()
        def finish():
            self.mode=None
            self.stop_event=None
            self.mode_thread=None
            self.set_controls(False)
            self.progress_value.set(0)
            self.status.set(final_text)
            self._refresh_all()
            if error:
                self.show_error(error)
        self.ui(finish)
    def request_stop(self):
        self.api.release_all_buttons()
        if self.ask_window is not None:
            self.close_ask()
            return
        if self.stop_event:
            self.stop_event.set()
            self.status.set("正在停止，已释放全部鼠标键")
    def wait_escape_release(self):
        while self.api.key_down(0x1B) and self.stop_event and not self.stop_event.is_set():
            time.sleep(0.04)
    def should_stop(self):
        if not self.stop_event or self.stop_event.is_set():
            return True
        if self.api.key_down(0x1B):
            self.stop_event.set()
            self.api.release_all_buttons()
            return True
        return False
    def inside(self,x,y,rect):
        rx,ry,rw,rh=rect
        return rx<=x<rx+rw and ry<=y<ry+rh
    def normalize_point(self,x,y,rect):
        rx,ry,rw,rh=rect
        return [max(0.0,min(1.0,(x-rx)/max(1,rw-1))),max(0.0,min(1.0,(y-ry)/max(1,rh-1)))]
    def point_to_screen(self,point,rect):
        x,y,width,height=rect
        return x+round(max(0.0,min(1.0,float(point[0])))*max(1,width-1)),y+round(max(0.0,min(1.0,float(point[1])))*max(1,height-1))
    def sample_context(self,last_signature,last_time,last_changed,motion_valid=True):
        return {"previous_action":last_signature or "","seconds_since_previous":round(max(0.0,min(60.0,time.time()-last_time)) if last_time else 60.0,3),"previous_action_changed_frame":bool(last_changed),"motion_channel_valid":bool(motion_valid)}
    def start_learning(self):
        self.start_worker("学习",self.learning_worker,True)
    def learning_worker(self):
        game=self.require_game()
        target=self.require_window(False)
        hwnd=target["hwnd"]
        focused=self.api.request_foreground(hwnd)
        if not focused:
            self.set_status("无法自动切换到目标窗口，学习将等待目标窗口成为前台")
        self.wait_escape_release()
        frame_buffer=FrameBuffer(self.api,target,20.0,2.0,0.1).start()
        monitor=MouseMonitor(self.api)
        monitor.start()
        active={}
        pending_click={}
        learned=0
        discarded=0
        duplicates=0
        invalid_frames=0
        last_action_signature=""
        last_action_time=0.0
        last_action_feature=None
        last_action_changed=True
        last_negative=0.0
        last_motion_time=0.0
        motion=None
        last_cursor=None
        hover_start=0.0
        hover_point=None
        last_update=0.0
        def capture_safe(stamp=None):
            nonlocal invalid_frames
            frame=frame_buffer.latest(stamp,0.75)
            if frame is None:
                invalid_frames+=1
            return frame
        def save(frame,action,source,weight=1.0):
            nonlocal learned,duplicates,last_action_signature,last_action_time,last_action_feature,last_action_changed
            if frame is None:
                return False
            context=self.sample_context(last_action_signature,last_action_time,last_action_changed,frame.get("motion_valid",False))
            saved=self.store.append_sample(game["id"],frame["f"],action,source,context,frame.get("gray"),weight)
            if saved:
                learned+=1
                last_action_signature=action_signature(action)
                last_action_time=time.time()
                last_action_changed=True if last_action_feature is None else visual_distance(last_action_feature,frame["f"])>75
                last_action_feature=frame["f"]
            else:
                duplicates+=1
            return saved
        def save_click(button,item):
            save(item["frame"],{"kind":"click","button":button,"path":[item["point"]],"duration":item["duration"]},"learn")
        def flush_pending(now,force=False):
            for button,item in list(pending_click.items()):
                if force or now-item["time"]>0.42:
                    save_click(button,item)
                    pending_click.pop(button,None)
        try:
            while not self.should_stop():
                now=time.time()
                try:
                    rect=self.api.validate_target(target,True)
                    focused=True
                except TargetUnavailable:
                    focused=False
                    active.clear()
                    if motion is not None:
                        motion["outside"]=True
                    motion=None
                    last_cursor=None
                    hover_point=None
                    hover_start=0.0
                    self.api.release_all_buttons()
                    self.set_status("目标窗口失去焦点，等待恢复；已释放全部鼠标键")
                events=monitor.drain()
                if not focused:
                    flush_pending(now)
                    time.sleep(0.05)
                    continue
                for event in events:
                    etype=event["type"]
                    x=event["x"]
                    y=event["y"]
                    event_time=event["time"]
                    inside=self.inside(x,y,rect)
                    if etype.endswith("_down"):
                        button=etype.split("_")[0]
                        if button in SUPPORTED_BUTTONS and inside:
                            frame=capture_safe(event_time)
                            if frame is not None:
                                point=self.normalize_point(x,y,rect)
                                active[button]={"frame":frame,"path":[point],"start":event_time,"outside":False,"last":point}
                        if motion is not None:
                            motion["outside"]=True
                        motion=None
                        last_cursor=None
                        hover_point=None
                        hover_start=0.0
                    elif etype=="move":
                        last_motion_time=event_time
                        if active:
                            for item in active.values():
                                if not inside:
                                    item["outside"]=True
                                else:
                                    point=self.normalize_point(x,y,rect)
                                    if abs(point[0]-item["last"][0])+abs(point[1]-item["last"][1])>=0.004:
                                        item["path"].append(point)
                                        item["last"]=point
                            if not inside:
                                last_cursor=None
                                hover_point=None
                                hover_start=0.0
                        else:
                            if not inside:
                                last_cursor=None
                                hover_point=None
                                hover_start=0.0
                                if motion is not None:
                                    motion["outside"]=True
                                continue
                            point=self.normalize_point(x,y,rect)
                            if motion is not None and motion.get("outside"):
                                discarded+=1
                                motion=None
                            if last_cursor is None:
                                last_cursor=point
                                hover_point=point
                                hover_start=event_time
                                continue
                            distance=math.hypot(point[0]-last_cursor[0],point[1]-last_cursor[1])
                            if motion is None and distance>=0.012:
                                frame=capture_safe(event_time)
                                if frame is not None:
                                    motion={"frame":frame,"path":[last_cursor,point],"start":event_time,"last":point,"outside":False}
                            elif motion is not None and math.hypot(point[0]-motion["last"][0],point[1]-motion["last"][1])>=0.006:
                                motion["path"].append(point)
                                motion["last"]=point
                            last_cursor=point
                            hover_point=point
                            hover_start=event_time
                    elif etype.endswith("_up"):
                        button=etype.split("_")[0]
                        if button in active:
                            item=active.pop(button)
                            if not inside:
                                item["outside"]=True
                            if item["outside"]:
                                discarded+=1
                                last_cursor=None
                                hover_point=None
                                hover_start=0.0
                                continue
                            point=self.normalize_point(x,y,rect)
                            item["path"].append(point)
                            duration=max(0.03,min(3.0,event_time-item["start"]))
                            length=path_length(item["path"])
                            if length>0.045:
                                save(item["frame"],{"kind":"drag","button":button,"path":item["path"],"duration":duration},"learn",1.4)
                            elif duration>=0.48:
                                save(item["frame"],{"kind":"long_press","button":button,"path":[point],"duration":duration},"learn",1.2)
                            else:
                                previous=pending_click.get(button)
                                if previous:
                                    click_gap=item["start"]-previous["time"]
                                    close=math.hypot(point[0]-previous["point"][0],point[1]-previous["point"][1])<=0.035
                                    if click_gap<=0.42 and close:
                                        pending_click.pop(button,None)
                                        save(previous["frame"],{"kind":"double_click","button":button,"path":[previous["point"]],"duration":max(0.06,event_time-previous["time"])},"learn",1.3)
                                        continue
                                    save_click(button,previous)
                                    pending_click.pop(button,None)
                                pending_click[button]={"frame":item["frame"],"point":point,"duration":duration,"time":event_time}
                    elif etype in {"wheel","hwheel"} and inside and not active:
                        frame=capture_safe(event_time)
                        if frame is not None:
                            save(frame,{"kind":"scroll_h" if etype=="hwheel" else "scroll_v","delta":event.get("delta",0),"path":[self.normalize_point(x,y,rect)],"duration":0.08},"learn",1.2)
                flush_pending(now)
                try:
                    polled_x,polled_y=self.api.cursor()
                    polled_inside=self.inside(polled_x,polled_y,rect)
                except Exception:
                    polled_inside=False
                if not polled_inside:
                    last_cursor=None
                    hover_point=None
                    hover_start=0.0
                    if motion is not None:
                        motion["outside"]=True
                    for item in active.values():
                        item["outside"]=True
                if motion is not None and now-last_motion_time>0.22:
                    if not motion["outside"] and path_length(motion["path"])>0.06:
                        save(motion["frame"],{"kind":"move","path":motion["path"],"duration":max(0.05,min(2.0,now-motion["start"]))},"learn")
                    elif motion["outside"]:
                        discarded+=1
                    motion=None
                    last_cursor=None
                if not active and hover_point is not None and now-hover_start>0.85 and now-last_action_time>0.7:
                    try:
                        current_x,current_y=self.api.cursor()
                        current_inside=self.inside(current_x,current_y,rect)
                    except Exception:
                        current_inside=False
                    if current_inside:
                        current_point=self.normalize_point(current_x,current_y,rect)
                        if math.hypot(current_point[0]-hover_point[0],current_point[1]-hover_point[1])<=0.02:
                            frame=capture_safe(now)
                            if frame is not None:
                                save(frame,{"kind":"hover","path":[current_point],"duration":0.85},"learn")
                            hover_start=now+1.5
                        else:
                            hover_point=current_point
                            hover_start=now
                    else:
                        last_cursor=None
                        hover_point=None
                        hover_start=0.0
                        if motion is not None:
                            motion["outside"]=True
                if not active and not pending_click and now-last_negative>0.9 and now-last_motion_time>0.35:
                    frame=capture_safe(now)
                    if frame is not None:
                        save(frame,{"kind":"no_op","duration":0.45},"negative",0.6)
                    last_negative=now
                if now-last_update>0.45:
                    self.set_status("学习中：有效"+str(learned)+"  重复或配额抑制"+str(duplicates)+"  越界废弃"+str(discarded)+"  无效画面"+str(invalid_frames)+"；事件使用发生前最近帧，仅保存全程位于客户区内的动作")
                    last_update=now
                time.sleep(0.012)
        finally:
            flush_pending(time.time(),True)
            monitor.stop()
            frame_buffer.stop()
            self.api.release_all_buttons()
        return "学习已结束：有效"+str(learned)+"，重复或配额抑制"+str(duplicates)+"，废弃"+str(discarded)+"，无效画面"+str(invalid_frames)
    def _prototype_medoid(self,members):
        if len(members)==1:
            return members[0]
        candidates=members if len(members)<=28 else [members[round(index*(len(members)-1)/27)] for index in range(28)]
        comparisons=members if len(members)<=72 else [members[round(index*(len(members)-1)/71)] for index in range(72)]
        best=candidates[0]
        best_total=float("inf")
        for candidate in candidates:
            total=0.0
            for other in comparisons:
                total+=feature_distance(candidate["f"],other["f"])
            if total<best_total:
                best_total=total
                best=candidate
        return best
    def _action_medoid(self,members):
        if len(members)==1:
            return members[0]
        candidates=members if len(members)<=36 else [members[round(index*(len(members)-1)/35)] for index in range(36)]
        comparisons=members if len(members)<=96 else [members[round(index*(len(members)-1)/95)] for index in range(96)]
        return min(candidates,key=lambda candidate:sum(action_geometry_distance(candidate["a"],other["a"])*float(other.get("weight",1.0)) for other in comparisons))
    def _cluster_action_samples(self,samples):
        families=defaultdict(list)
        for sample in samples:
            family=action_family_key(sample["a"])
            if family:
                families[family].append(sample)
        clusters=[]
        for family,items in sorted(families.items()):
            local=[]
            for item in sorted(items,key=lambda value:str(value.get("checksum",""))):
                if not local:
                    local.append({"family":family,"members":[item],"medoid":item})
                    continue
                distances=[action_geometry_distance(item["a"],cluster["medoid"]["a"]) for cluster in local]
                best_index=min(range(len(distances)),key=lambda index:distances[index])
                limit=action_cluster_limit(item["a"])
                if distances[best_index]<=limit:
                    cluster=local[best_index]
                    cluster["members"].append(item)
                    if len(cluster["members"])<=48 or len(cluster["members"])%8==0:
                        cluster["medoid"]=self._action_medoid(cluster["members"])
                else:
                    local.append({"family":family,"members":[item],"medoid":item})
            changed=True
            while changed and len(local)>1:
                changed=False
                for first in range(len(local)):
                    if changed:
                        break
                    for second in range(first+1,len(local)):
                        limit=min(action_cluster_limit(local[first]["medoid"]["a"]),action_cluster_limit(local[second]["medoid"]["a"]))*0.82
                        if action_geometry_distance(local[first]["medoid"]["a"],local[second]["medoid"]["a"])<=limit:
                            local[first]["members"].extend(local[second]["members"])
                            local[first]["medoid"]=self._action_medoid(local[first]["members"])
                            local.pop(second)
                            changed=True
                            break
            for index,cluster in enumerate(local):
                medoid_action=normalize_action(cluster["medoid"]["a"])
                token=hashlib.sha256(canonical_bytes({"family":family,"action":medoid_action,"index":index})).hexdigest()[:20]
                cluster["id"]="action|"+family+"|"+token
                cluster["a"]=medoid_action
                for member in cluster["members"]:
                    member["_action_cluster"]=cluster["id"]
                    member["_cluster_action"]=medoid_action
                    member["_action_support"]=len(cluster["members"])
                clusters.append(cluster)
        return clusters
    def _cluster_action_group(self,signature,action,action_support,items,progress_callback):
        clusters=[]
        max_clusters=max(1,min(28,int(math.sqrt(len(items)))+3))
        threshold=520.0
        for index,item in enumerate(items):
            if self.should_stop():
                break
            if not clusters:
                clusters.append([item])
            else:
                medoids=[cluster[0] for cluster in clusters]
                distances=[feature_distance(item["f"],medoid["f"]) for medoid in medoids]
                best_index=min(range(len(distances)),key=lambda position:distances[position])
                if distances[best_index]>threshold and len(clusters)<max_clusters:
                    clusters.append([item])
                else:
                    clusters[best_index].append(item)
            if index%15==0:
                progress_callback(index,len(items),len(clusters))
        result=[]
        for cluster in clusters:
            medoid=self._prototype_medoid(cluster)
            distances=[feature_distance(item["f"],medoid["f"]) for item in cluster]
            mean=statistics.fmean(distances) if distances else 0.0
            std=statistics.pstdev(distances) if len(distances)>1 else 0.0
            limit95=quantile(distances,0.95)
            limit99=quantile(distances,0.99)
            threshold_value=max(20.0,min(1800.0,max(limit99,mean+2.58*std)+max(12.0,std*0.35)))
            previous=Counter(str(item.get("context",{}).get("previous_action","")) for item in cluster)
            prev=previous.most_common(1)[0][0] if previous else ""
            result.append({"id":uuid.uuid4().hex,"f":feature_bytes(medoid["f"]),"coarse":coarse_feature(medoid["f"]),"a":normalize_action(action),"action_signature":signature,"support":len(cluster),"action_support":int(action_support),"mean_distance":round(mean,6),"std_distance":round(std,6),"limit95":round(limit95,6),"limit99":round(limit99,6),"intra_threshold":round(threshold_value,6),"threshold":round(threshold_value,6),"previous_action":prev,"created_from_sample_checksum":medoid.get("checksum","")})
        return result
    def rank_action_candidates(self,feature,prototypes,last_action_signature="",full_limit=16):
        if not feature_valid(feature):
            return []
        query_coarse=coarse_feature(feature)
        coarse_rank=[]
        best_per_action={}
        for proto in prototypes:
            pc=proto.get("coarse")
            if not isinstance(pc,(bytes,bytearray)) or len(pc)!=324:
                pc=coarse_feature(proto["f"])
                proto["coarse"]=pc
            distance=coarse_distance(query_coarse,pc)
            coarse_rank.append((distance,proto))
            signature=str(proto.get("action_signature",""))
            if signature and (signature not in best_per_action or distance<best_per_action[signature][0]):
                best_per_action[signature]=(distance,proto)
        coarse_rank.sort(key=lambda item:item[0])
        selected=[]
        selected_ids=set()
        for distance,proto in coarse_rank[:max(8,int(full_limit))]:
            if proto["id"] not in selected_ids:
                selected.append(proto)
                selected_ids.add(proto["id"])
        for distance,proto in sorted(best_per_action.values(),key=lambda item:item[0])[:12]:
            if proto["id"] not in selected_ids:
                selected.append(proto)
                selected_ids.add(proto["id"])
        grouped=defaultdict(list)
        for proto in selected:
            raw=feature_distance(feature,proto["f"])
            expected=str(proto.get("previous_action",""))
            penalty=0.0
            if expected and last_action_signature and expected!=last_action_signature:
                penalty=min(120.0,raw*0.08+18.0)
            grouped[str(proto["action_signature"])].append((raw+penalty,raw,proto))
        result=[]
        for signature,items in grouped.items():
            items.sort(key=lambda item:item[0])
            best_score,best_distance,best_proto=items[0]
            vote_score=best_score
            if len(items)>1:
                vote_score=0.88*best_score+0.12*items[1][0]
            result.append({"action_signature":signature,"score":vote_score,"best_score":best_score,"distance":best_distance,"proto":best_proto,"a":normalize_action(best_proto["a"]),"support":max(int(item[2].get("action_support",item[2].get("support",0))) for item in items),"prototype_votes":len(items)})
        result.sort(key=lambda item:item["score"])
        return result
    def evaluate_action_candidates(self,ranked):
        if not ranked:
            return {"accepted":False,"confidence":0.0,"reason":"没有候选"}
        best=ranked[0]
        second=ranked[1] if len(ranked)>1 else None
        proto=best["proto"]
        strict_multiplier,min_support,margin_ratio=self.action_strictness(best["a"])
        threshold=float(proto["threshold"])/strict_multiplier
        second_score=second["score"] if second else float("inf")
        margin=second_score-best["score"]
        required_gap=max(float(proto.get("minimum_second_candidate_gap",16.0)),best["score"]*0.12)
        margin_ok=math.isinf(second_score) or best["score"]<second_score*margin_ratio and margin>required_gap
        support=int(best.get("support",0))
        rejected_distance=proto.get("nearest_rejected_distance")
        rejection_ok=rejected_distance is None or best["distance"]<float(rejected_distance)*0.65
        accepted=best["distance"]<threshold and margin_ok and support>=min_support and rejection_ok
        confidence=max(0.0,min(1.0,1.0-best["distance"]/max(1.0,threshold)))
        return {"accepted":accepted,"best":best,"second":second,"threshold":threshold,"margin":margin,"required_gap":required_gap,"support":support,"min_support":min_support,"confidence":confidence,"margin_ok":margin_ok,"rejection_ok":rejection_ok,"nearest_rejected_distance":rejected_distance}
    def start_review(self):
        self.start_worker("复习",self.review_worker,False)
    def review_worker(self):
        game=self.require_game()
        samples,stats=self.store.load_samples(game["id"])
        valid=[]
        for sample in samples:
            action=normalize_action(sample.get("a"))
            if feature_valid(sample.get("f")) and action:
                item=dict(sample)
                item["a"]=action
                valid.append(item)
        if not valid:
            raise RuntimeError("没有可复习的有效学习数据，请先进行学习")
        self.wait_escape_release()
        action_clusters=self._cluster_action_samples(valid)
        max_holdout=sum(max(0,len(cluster["members"])-1) for cluster in action_clusters)
        target_holdout=min(max_holdout,max(1,max(20,round(len(valid)*0.22))))
        candidates=[]
        for cluster in action_clusters:
            ordered=sorted(cluster["members"],key=lambda item:str(item.get("checksum","")))
            candidates.extend(ordered[1:])
        candidates.sort(key=lambda item:hashlib.sha256(str(item.get("checksum","")).encode("utf-8")).hexdigest())
        holdout_ids={id(item) for item in candidates[:target_holdout]}
        train=[item for item in valid if id(item) not in holdout_ids]
        holdout=[item for item in valid if id(item) in holdout_ids]
        if not train:
            train=valid
            holdout=[]
        groups=defaultdict(list)
        cluster_map={cluster["id"]:cluster for cluster in action_clusters}
        for sample in train:
            groups[sample["_action_cluster"]].append(sample)
        ordered=sorted(groups.items(),key=lambda item:(normalize_action(cluster_map[item[0]]["a"])["kind"]=="no_op",-len(item[1])))
        prototypes=[]
        processed=0
        total=len(train)
        stopped=False
        for signature,items in ordered:
            if self.should_stop():
                stopped=True
                break
            cluster=cluster_map[signature]
            def progress(local,total_local,count):
                overall=processed+local
                self.set_progress(82*overall/max(1,total))
                self.set_status("复习中：动作先按种类和按钮分组，再按几何距离聚类；"+str(overall)+"/"+str(total)+"，原型"+str(len(prototypes)+count)+"个")
            group_prototypes=self._cluster_action_group(signature,cluster["a"],len(items),items,progress)
            prototypes.extend(group_prototypes)
            processed+=len(items)
            if len(prototypes)>MAX_PROTOTYPES:
                prototypes=sorted(prototypes,key=lambda item:(item.get("action_support",0),item["support"]),reverse=True)[:MAX_PROTOTYPES]
        for index,proto in enumerate(prototypes):
            conflicting=[other for other in prototypes if other["id"]!=proto["id"] and other["action_signature"]!=proto["action_signature"]]
            nearest=float("inf")
            if conflicting:
                rough=sorted((coarse_distance(proto["coarse"],other["coarse"]),other) for other in conflicting)[:16]
                nearest=min(feature_distance(proto["f"],other["f"]) for rough_distance,other in rough)
            proto["nearest_conflicting_distance"]=None if math.isinf(nearest) else round(nearest,6)
            intra=float(proto.get("intra_threshold",proto["threshold"]))
            proto["threshold"]=round(intra if math.isinf(nearest) else max(8.0,min(intra,nearest*0.62)),6)
            proto["minimum_second_candidate_gap"]=round(max(12.0,float(proto["threshold"])*0.12,0.0 if math.isinf(nearest) else nearest*0.08),6)
            if index%12==0:
                self.set_progress(82+6*(index+1)/max(1,len(prototypes)))
                self.set_status("复习中：使用异类动作距离收紧原型阈值 "+str(index+1)+"/"+str(len(prototypes)))
        rejections=self.store.load_rejections(game["id"],500)
        rejection_constraints=0
        for index,proto in enumerate(prototypes):
            matching=[]
            for rejection in rejections:
                candidate_actions=[normalize_action(item.get("a")) for item in rejection.get("candidates",[]) if isinstance(item,dict)]
                if any(action and action_family_key(action)==action_family_key(proto["a"]) and action_geometry_distance(action,proto["a"])<=action_cluster_limit(proto["a"])*1.25 for action in candidate_actions):
                    matching.append((coarse_distance(proto["coarse"],coarse_feature(rejection["f"])),rejection))
            if matching:
                nearest_rejected=min(feature_distance(proto["f"],rejection["f"]) for rough,rejection in sorted(matching,key=lambda item:item[0])[:8])
                proto["nearest_rejected_distance"]=round(nearest_rejected,6)
                proto["threshold"]=round(max(0.001,min(float(proto["threshold"]),nearest_rejected*0.78)),6)
                rejection_constraints+=1
            else:
                proto["nearest_rejected_distance"]=None
            if index%12==0 and rejections:
                self.set_progress(88+1.5*(index+1)/max(1,len(prototypes)))
                self.set_status("复习中：应用实时请教的拒绝记录 "+str(index+1)+"/"+str(len(prototypes)))
        if stopped:
            if prototypes:
                partial={"created":time.time(),"samples":len(valid),"training_samples":len(train),"invalid_samples":stats["invalid"],"rejection_constraints":rejection_constraints,"prototypes":prototypes,"validation":{"status":"stopped","holdout":0,"accepted":0,"coverage":0.0,"accepted_error_rate":None,"overall_accuracy":0.0,"reject_rate":1.0},"stopped":True}
                self.store.save_model(game["id"],partial,False)
            return "复习已中断：旧完整模型未被覆盖，部分结果仅保存为临时模型"
        self.set_progress(88)
        errors=0
        accepted=0
        correct=0
        for index,sample in enumerate(holdout):
            ranked=self.rank_action_candidates(sample["f"],prototypes,"",16)
            decision=self.evaluate_action_candidates(ranked)
            if decision.get("accepted"):
                accepted+=1
                if decision["best"]["action_signature"]==sample["_action_cluster"]:
                    correct+=1
                else:
                    errors+=1
            if index%5==0:
                self.set_progress(88+10*(index+1)/max(1,len(holdout)))
                self.set_status("复习中：按动作级候选对留出样本验证 "+str(index+1)+"/"+str(len(holdout)))
        holdout_count=len(holdout)
        coverage=accepted/holdout_count if holdout_count else 0.0
        accepted_error_rate=errors/accepted if accepted else None
        overall_accuracy=correct/holdout_count if holdout_count else 0.0
        reject_rate=1.0-coverage if holdout_count else 1.0
        if holdout_count<20 or accepted==0 or coverage<0.55:
            validation_status="insufficient"
        elif accepted_error_rate is not None and accepted_error_rate>0.12 or overall_accuracy<0.45:
            validation_status="failed"
        else:
            validation_status="passed"
        validation={"status":validation_status,"minimum_holdout":20,"minimum_coverage":0.55,"maximum_accepted_error_rate":0.12,"minimum_overall_accuracy":0.45,"holdout":holdout_count,"accepted":accepted,"errors":errors,"correct":correct,"coverage":coverage,"accepted_error_rate":accepted_error_rate,"overall_accuracy":overall_accuracy,"reject_rate":reject_rate}
        model={"created":time.time(),"samples":len(valid),"training_samples":len(train),"invalid_samples":stats["invalid"],"action_clusters":len(action_clusters),"rejection_constraints":rejection_constraints,"prototypes":prototypes,"validation":validation,"stopped":False}
        if not prototypes:
            raise RuntimeError("复习未生成可用原型")
        if validation_status=="passed":
            self.store.save_model(game["id"],model,True)
            self.set_progress(100)
            return "复习完成并通过验收："+str(len(prototypes))+"个真实样本原型，留出"+str(holdout_count)+"，覆盖率"+str(round(coverage*100,2))+"%，接受样本错误率"+str(round((accepted_error_rate or 0.0)*100,2))+"%，总体正确率"+str(round(overall_accuracy*100,2))+"%"
        self.store.save_model(game["id"],model,False)
        self.set_progress(100)
        error_text="无可计算值" if accepted_error_rate is None else str(round(accepted_error_rate*100,2))+"%"
        validation_label="验证不足" if validation_status=="insufficient" else "验证未通过"
        return "复习完成但"+validation_label+"，旧完整模型未被覆盖：留出"+str(holdout_count)+"，接受"+str(accepted)+"，覆盖率"+str(round(coverage*100,2))+"%，接受样本错误率"+error_text+"，总体正确率"+str(round(overall_accuracy*100,2))+"%，拒识率"+str(round(reject_rate*100,2))+"%"
    def action_text(self,action):
        item=normalize_action(action) or {"kind":"no_op","duration":0.3}
        kind=item["kind"]
        names={"left":"左键","right":"右键","middle":"中键"}
        if kind=="no_op":
            return "不操作，等待"+str(item.get("duration",0.3))+"秒"
        if kind in {"scroll_v","scroll_h"}:
            direction="向上" if item["delta"]>0 else "向下"
            if kind=="scroll_h":
                direction="向右" if item["delta"]>0 else "向左"
            return ("水平滚轮" if kind=="scroll_h" else "垂直滚轮")+direction
        point=item["path"][-1]
        position="("+str(int(round(point[0]*100)))+"%, "+str(int(round(point[1]*100)))+"%)"
        if kind=="move":
            return "无按键移动到"+position
        if kind=="hover":
            return "悬停于"+position
        label={"click":"单击","double_click":"双击","long_press":"长按","drag":"拖动"}.get(kind,kind)
        return names.get(item.get("button"),"左键")+label+" "+position
    def action_cooldown(self,action):
        kind=normalize_action(action)["kind"]
        return {"click":0.8,"double_click":1.5,"long_press":2.0,"drag":1.2,"scroll_v":0.8,"scroll_h":1.0,"move":0.45,"hover":1.0,"no_op":0.25}.get(kind,1.0)
    def action_strictness(self,action):
        kind=normalize_action(action)["kind"]
        button=normalize_action(action).get("button")
        if kind in {"double_click","long_press","drag"} or button in {"right","middle"}:
            return 1.35,4,0.78
        if kind in {"scroll_v","scroll_h"}:
            return 1.2,3,0.80
        if kind in {"move","hover"}:
            return 1.0,2,0.84
        if kind=="no_op":
            return 1.0,1,0.88
        return 1.0,2,0.84
    def execute_action(self,target,action):
        item=normalize_action(action)
        if not item:
            raise RuntimeError("模型包含无效动作")
        kind=item["kind"]
        if kind=="no_op":
            end=time.time()+item.get("duration",0.35)
            while time.time()<end and not self.should_stop():
                self.api.validate_target(target,True)
                time.sleep(0.02)
            return
        path=item.get("path") or [[0.5,0.5]]*16
        def move_to(point):
            rect=self.api.validate_target(target,True)
            x,y=self.point_to_screen(point,rect)
            if not self.inside(x,y,rect):
                raise TargetUnavailable("动作坐标超出客户区")
            self.api.move_cursor(x,y)
            self.api.validate_target(target,True)
        move_to(path[0])
        if self.should_stop():
            return
        if kind=="move":
            for point in path[1:]:
                if self.should_stop():
                    return
                move_to(point)
                time.sleep(max(0.004,item["duration"]/max(1,len(path)-1)))
            return
        if kind=="hover":
            end=time.time()+item["duration"]
            while time.time()<end and not self.should_stop():
                self.api.validate_target(target,True)
                time.sleep(0.02)
            return
        if kind in {"scroll_v","scroll_h"}:
            self.api.validate_target(target,True)
            self.api.wheel(item["delta"],kind=="scroll_h")
            self.api.validate_target(target,True)
            return
        button=item["button"]
        if kind=="double_click":
            for iteration in range(2):
                self.api.validate_target(target,True)
                self.api.button(button,True)
                time.sleep(0.045)
                self.api.validate_target(target,True)
                self.api.button(button,False)
                if iteration==0:
                    time.sleep(0.09)
            return
        self.api.validate_target(target,True)
        self.api.button(button,True)
        try:
            if kind=="drag":
                step_time=item["duration"]/max(1,len(path)-1)
                for point in path[1:]:
                    if self.should_stop():
                        break
                    move_to(point)
                    end=time.time()+step_time
                    while time.time()<end and not self.should_stop():
                        self.api.validate_target(target,True)
                        time.sleep(min(0.012,max(0.002,end-time.time())))
            else:
                hold=item["duration"] if kind=="long_press" else min(0.13,item["duration"])
                end=time.time()+hold
                while time.time()<end and not self.should_stop():
                    self.api.validate_target(target,True)
                    time.sleep(0.01)
        finally:
            try:
                self.api.button(button,False)
            except Exception:
                self.api.release_all_buttons()
    def start_training(self):
        try:
            game=self.require_game()
            self.require_window(False)
            model=self.store.load_model(game["id"])
            if not model or not model.get("prototypes"):
                raise RuntimeError("没有可用完整模型，请先学习并完成复习")
            if str(model.get("validation",{}).get("status",""))!="passed":
                raise RuntimeError("完整模型未通过留出数量、覆盖率、错误率和总体正确率验收，请重新复习")
            current=next((item for item in self.store.games() if item["id"]==game["id"]),{})
            if current.get("needs_review"):
                raise RuntimeError("模型需要复习：请先点击“复习”完成离线优化")
        except Exception as error:
            self.show_error(str(error))
            return
        self.start_worker("训练",self.training_worker,True)
    def training_worker(self):
        game=self.require_game()
        target=self.require_window(False)
        model=self.store.load_model(game["id"])
        prototypes=[proto for proto in model.get("prototypes",[]) if feature_valid(proto.get("f")) and normalize_action(proto.get("a")) and finite_number(proto.get("threshold")) and str(proto.get("action_signature",""))]
        if not prototypes:
            raise RuntimeError("模型中没有可用原型")
        focused=self.api.request_foreground(target["hwnd"])
        if not focused:
            self.set_status("无法自动切换到目标窗口，训练将等待目标窗口成为前台")
        self.wait_escape_release()
        frame_buffer=FrameBuffer(self.api,target,20.0,2.0,0.1).start()
        actions=0
        candidate_id=None
        candidate_count=0
        candidate_frame_stamp=0.0
        last_action_signature=""
        last_action_time=0.0
        last_action_feature=None
        last_executed_signature=None
        state_unlocked=True
        no_change_count=0
        frozen_count=0
        previous_feature=None
        previous_frame_stamp=0.0
        coordinate_hits=deque()
        paused_reason=""
        pause_until=0.0
        paused_coordinate_key=None
        try:
            while not self.should_stop():
                try:
                    self.api.validate_target(target,True)
                except TargetUnavailable as error:
                    self.api.release_all_buttons()
                    candidate_id=None
                    candidate_count=0
                    self.set_confidence("训练置信度：0%")
                    self.set_status("目标窗口失去焦点，等待恢复；已释放全部鼠标键；"+str(error))
                    time.sleep(0.08)
                    continue
                captured=frame_buffer.latest(None,0.7)
                if captured is None:
                    self.api.release_all_buttons()
                    self.set_status("等待固定间隔画面缓冲；"+(frame_buffer.last_error or "尚无有效帧"))
                    time.sleep(0.08)
                    continue
                feature=captured["f"]
                frame_change=float("inf")
                if captured["time"]!=previous_frame_stamp:
                    if previous_feature is not None:
                        frame_change=visual_distance(previous_feature,feature)
                        frozen_count=frozen_count+1 if frame_change<2.0 else 0
                    previous_feature=feature
                    previous_frame_stamp=captured["time"]
                if frozen_count>=24 and not paused_reason.startswith("同一坐标"):
                    paused_reason="画面长时间冻结，训练已自动暂停"
                if paused_reason.startswith("画面长时间冻结") and frame_change>25:
                    paused_reason=""
                    frozen_count=0
                significant_change=last_action_feature is not None and visual_distance(last_action_feature,feature)>90
                if significant_change:
                    state_unlocked=True
                    no_change_count=0
                    if paused_reason.startswith("等待画面变化") or paused_reason.startswith("画面长时间冻结") or paused_reason.startswith("同一坐标"):
                        paused_reason=""
                        pause_until=0.0
                        candidate_id=None
                        candidate_count=0
                        if paused_coordinate_key is not None:
                            coordinate_hits=deque((stamp,key) for stamp,key in coordinate_hits if key!=paused_coordinate_key)
                        paused_coordinate_key=None
                now=time.time()
                if paused_reason.startswith("同一坐标") and pause_until and now>=pause_until:
                    coordinate_hits=deque((stamp,key) for stamp,key in coordinate_hits if key!=paused_coordinate_key)
                    paused_reason=""
                    pause_until=0.0
                    paused_coordinate_key=None
                    candidate_id=None
                    candidate_count=0
                if paused_reason:
                    self.api.release_all_buttons()
                    self.set_confidence("训练置信度：0%")
                    suffix="；冷却剩余"+str(round(max(0.0,pause_until-now),1))+"秒或等待明显画面变化" if paused_reason.startswith("同一坐标") else "；等待明显状态变化或停止"
                    self.set_status(paused_reason+suffix)
                    time.sleep(0.1)
                    continue
                ranked=self.rank_action_candidates(feature,prototypes,last_action_signature,16)
                decision=self.evaluate_action_candidates(ranked)
                if not decision.get("accepted"):
                    candidate_id=None
                    candidate_count=0
                    confidence=float(decision.get("confidence",0.0))
                    if ranked:
                        best=ranked[0]
                        threshold=float(decision.get("threshold",0.0))
                        self.set_confidence("训练置信度："+str(round(confidence*100,1))+"%  未达到动作阈值/不同动作差距/支持数要求")
                        self.set_status("训练中：识别不确定，执行no_op；最佳动作距离"+str(round(best["distance"],1))+"，阈值"+str(round(threshold,1))+"，动作支持"+str(decision.get("support",0))+"，差距"+str(round(float(decision.get("margin",0.0)),1))+"/"+str(round(float(decision.get("required_gap",0.0)),1)))
                    else:
                        self.set_confidence("训练置信度：0%")
                        self.set_status("训练中：没有合法动作级候选")
                    time.sleep(0.14)
                    continue
                best=decision["best"]
                action_id=best["action_signature"]
                if candidate_id==action_id:
                    if captured["time"]==candidate_frame_stamp:
                        time.sleep(0.025)
                        continue
                    candidate_count+=1
                else:
                    candidate_id=action_id
                    candidate_count=1
                candidate_frame_stamp=captured["time"]
                self.set_confidence("训练置信度："+str(round(decision["confidence"]*100,1))+"%  动作级连续确认"+str(candidate_count)+"/2  支持"+str(decision["support"])+"  原型投票"+str(best.get("prototype_votes",1)))
                if candidate_count<2:
                    time.sleep(0.07)
                    continue
                action=normalize_action(best["a"])
                signature=best["action_signature"]
                if action["kind"]=="no_op":
                    self.set_status("训练中：模型决定不操作，等待画面变化")
                    self.execute_action(target,action)
                    candidate_count=0
                    continue
                if last_executed_signature==signature and not state_unlocked:
                    self.set_status("等待画面变化：同一状态和同一动作只允许执行一次")
                    time.sleep(0.1)
                    continue
                cooldown=self.action_cooldown(action)
                if time.time()-last_action_time<cooldown:
                    self.set_status("动作冷却中："+self.action_text(action))
                    time.sleep(0.07)
                    continue
                point=(action.get("path") or [[0.5,0.5]])[-1]
                coordinate_key=(action.get("button","none"),round(point[0],2),round(point[1],2),action["kind"])
                now=time.time()
                while coordinate_hits and now-coordinate_hits[0][0]>12.0:
                    coordinate_hits.popleft()
                same_hits=sum(1 for stamp,key in coordinate_hits if key==coordinate_key)
                if same_hits>=3:
                    paused_reason="同一坐标连续动作达到上限，训练进入安全冷却"
                    pause_until=now+3.0
                    paused_coordinate_key=coordinate_key
                    self.api.release_all_buttons()
                    continue
                before=feature
                before_stamp=captured["time"]
                self.set_status("训练中："+self.action_text(action)+"；动作距离"+str(round(best["distance"],1))+"/阈值"+str(round(decision["threshold"],1))+"；不同动作差距"+str(round(decision["margin"],1))+"；采集="+captured["method"])
                try:
                    self.execute_action(target,action)
                except TargetUnavailable:
                    self.api.release_all_buttons()
                    self.set_status("目标窗口失去焦点，等待恢复；已释放全部鼠标键")
                    candidate_id=None
                    candidate_count=0
                    continue
                actions+=1
                coordinate_hits.append((now,coordinate_key))
                last_action_signature=signature
                last_action_time=time.time()
                last_action_feature=before
                last_executed_signature=signature
                state_unlocked=False
                candidate_count=0
                end=time.time()+0.24
                while time.time()<end and not self.should_stop():
                    try:
                        self.api.validate_target(target,True)
                    except TargetUnavailable:
                        self.api.release_all_buttons()
                        break
                    time.sleep(0.02)
                if self.should_stop():
                    break
                after=None
                wait_end=time.time()+0.45
                while time.time()<wait_end and not self.should_stop():
                    after=frame_buffer.latest_after(before_stamp)
                    if after is not None:
                        break
                    time.sleep(0.025)
                change=visual_distance(before,after["f"]) if after is not None else 0.0
                if change<70:
                    no_change_count+=1
                    self.set_status("等待画面变化：动作后变化不足，连续"+str(no_change_count)+"次")
                    if no_change_count>=3:
                        paused_reason="等待画面变化：连续多次无变化，训练已自动暂停"
                else:
                    no_change_count=0
                    state_unlocked=True
                time.sleep(0.07)
        finally:
            frame_buffer.stop()
            self.api.release_all_buttons()
        return "训练已结束，AI执行"+str(actions)+"个鼠标动作"
    def basic_actions(self):
        result=[]
        for y in (0.18,0.35,0.5,0.68,0.84):
            for x in (0.16,0.32,0.5,0.68,0.84):
                result.append(normalize_action({"kind":"click","button":"left","path":[[x,y]],"duration":0.08}))
        result.extend([normalize_action({"kind":"double_click","button":"left","path":[[0.5,0.5]],"duration":0.16}),normalize_action({"kind":"drag","button":"left","path":[[0.25,0.5],[0.75,0.5]],"duration":0.45}),normalize_action({"kind":"drag","button":"left","path":[[0.5,0.75],[0.5,0.25]],"duration":0.45}),normalize_action({"kind":"no_op","duration":0.4}),normalize_action({"kind":"scroll_v","delta":120,"path":[[0.5,0.5]],"duration":0.08}),normalize_action({"kind":"scroll_v","delta":-120,"path":[[0.5,0.5]],"duration":0.08})])
        return result
    def start_ask(self):
        if self.mode:
            self.show_error("当前正在“"+self.mode+"”，请先停止")
            return
        try:
            game=self.require_game()
            target=self.require_window(False)
            samples,stats=self.store.load_samples(game["id"])
            try:
                model=self.store.load_model(game["id"])
            except Exception:
                model=None
            prototypes=[]
            if model:
                prototypes=[item for item in model.get("prototypes",[]) if feature_valid(item.get("f")) and normalize_action(item.get("a"))]
            historical=[]
            for item in samples:
                action=normalize_action(item.get("a"))
                if feature_valid(item.get("f")) and action:
                    historical.append({"id":str(item.get("checksum",uuid.uuid4().hex)),"f":item["f"],"coarse":coarse_feature(item["f"]),"a":action,"action_signature":str(item.get("_action_cluster",action_signature(action))),"source":"sample"})
            focused=self.api.request_foreground(target["hwnd"])
            if not focused:
                self.status.set("请教将等待目标窗口成为前台")
            self.ask_buffer=FrameBuffer(self.api,target,20.0,2.0,0.1).start()
        except Exception as error:
            if self.ask_buffer is not None:
                self.ask_buffer.stop()
                self.ask_buffer=None
            self.show_error(str(error))
            return
        self.mode="请教"
        self.set_controls(True)
        self.status.set("请教已开始：从当前窗口实时画面选择最不确定状态；ESC或“停止”结束")
        win=tk.Toplevel(self.root)
        self.ask_window=win
        win.title("请教")
        win.geometry("760x760")
        win.minsize(680,680)
        win.transient(self.root)
        frame=ttk.Frame(win,padding=16)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="请选择当前实时画面中AI应该执行的鼠标动作",font=("Microsoft YaHei UI",14,"bold")).pack(anchor="w")
        ttk.Label(frame,text="画面来自所选窗口的实时客户区；优先选择模型最不确定或两个动作最接近的近期状态，选项会随机排列。",wraplength=700).pack(anchor="w",pady=(4,10))
        canvas=tk.Canvas(frame,width=672,height=378,bg="black",highlightthickness=1,highlightbackground="#777777")
        canvas.pack(fill="x",expand=False)
        choice_frame=ttk.Frame(frame)
        choice_frame.pack(fill="both",expand=True,pady=(10,0))
        answer_buttons=[]
        count={"saved":0,"duplicates":0,"skipped":0,"rejected":0}
        state={"frame":None,"choices":[],"image":None,"locked":False,"candidates":[]}
        actions=[item["a"] for item in prototypes]+[item["a"] for item in historical]+self.basic_actions()
        unique=[]
        seen=set()
        for action in actions:
            signature=action_signature(action)
            if signature and signature not in seen:
                seen.add(signature)
                unique.append(action)
        def schedule(delay,callback):
            holder={"id":None}
            def wrapped():
                self.ask_after_ids.discard(holder["id"])
                callback()
            holder["id"]=win.after(delay,wrapped)
            self.ask_after_ids.add(holder["id"])
        def set_locked(value):
            state["locked"]=bool(value)
            for button in answer_buttons:
                button.configure(state="disabled" if value else "normal")
            skip_button.configure(state="disabled" if value else "normal")
            reject_button.configure(state="disabled" if value else "normal")
            custom_button.configure(state="disabled" if value else "normal")
        def render(gray):
            image=tk.PhotoImage(width=FEATURE_W,height=FEATURE_H)
            rows=[]
            source=gray_bytes(gray) or bytes(PIXELS)
            for y in range(FEATURE_H):
                row=[]
                for x in range(FEATURE_W):
                    value=source[y*FEATURE_W+x]
                    row.append("#%02x%02x%02x"%(value,value,value))
                rows.append("{"+" ".join(row)+"}")
            image.put(" ".join(rows))
            scaled=image.zoom(14,14)
            state["image"]=(image,scaled)
            canvas.delete("all")
            canvas.create_image(336,189,image=scaled)
        def select_question_frame():
            frames=self.ask_buffer.snapshot(1.6) if self.ask_buffer is not None else []
            if not frames:
                return None,[]
            if not prototypes:
                return frames[-1],[]
            best_frame=frames[-1]
            best_ranked=self.rank_action_candidates(best_frame["f"],prototypes,"",16)
            best_uncertainty=float("inf")
            for candidate_frame in frames[-24:]:
                ranked=self.rank_action_candidates(candidate_frame["f"],prototypes,"",16)
                if not ranked:
                    continue
                if len(ranked)>1:
                    uncertainty=(ranked[1]["score"]-ranked[0]["score"])/max(1.0,ranked[0]["score"])
                else:
                    uncertainty=10.0
                decision=self.evaluate_action_candidates(ranked)
                if not decision.get("accepted"):
                    uncertainty-=0.2
                if uncertainty<best_uncertainty:
                    best_uncertainty=uncertainty
                    best_frame=candidate_frame
                    best_ranked=ranked
            return best_frame,best_ranked
        def make_choices(question_frame,ranked):
            choices=[]
            signatures=set()
            candidates=[]
            for item in ranked[:3]:
                action=normalize_action(item["a"])
                signature=action_signature(action)
                candidates.append({"action_signature":item["action_signature"],"a":action})
                if signature and signature not in signatures:
                    signatures.add(signature)
                    choices.append(action)
                if len(choices)>=2:
                    break
            if not ranked and historical:
                query=coarse_feature(question_frame["f"])
                rough=sorted((coarse_distance(query,item["coarse"]),item) for item in historical)[:16]
                exact=sorted((feature_distance(question_frame["f"],item["f"]),item) for rough_distance,item in rough)
                for distance,item in exact:
                    action=item["a"]
                    signature=action_signature(action)
                    candidates.append({"action_signature":item["action_signature"],"a":action})
                    if signature and signature not in signatures:
                        signatures.add(signature)
                        choices.append(action)
                    if len(choices)>=2:
                        break
            distractors=list(unique)
            random.shuffle(distractors)
            for action in distractors:
                signature=action_signature(action)
                if signature and signature not in signatures:
                    signatures.add(signature)
                    choices.append(action)
                if len(choices)>=4:
                    break
            random.shuffle(choices)
            final_choices=choices[:4]
            candidates=[{"action_signature":action_signature(action),"a":action} for action in final_choices]
            return final_choices,candidates
        def new_question():
            if self.ask_window is None:
                return
            set_locked(True)
            try:
                self.api.validate_target(target,True)
            except Exception as error:
                self.status.set("请教等待目标窗口恢复前台："+str(error))
                schedule(180,new_question)
                return
            question_frame,ranked=select_question_frame()
            if question_frame is None:
                self.status.set("请教等待实时画面缓冲；"+(self.ask_buffer.last_error if self.ask_buffer is not None else ""))
                schedule(150,new_question)
                return
            choices,candidates=make_choices(question_frame,ranked)
            state["frame"]=question_frame
            state["choices"]=choices
            state["candidates"]=candidates
            render(question_frame["gray"])
            for index,button in enumerate(answer_buttons):
                if index<len(choices):
                    button.configure(text=chr(65+index)+". "+self.action_text(choices[index]),command=lambda position=index:choose(position),state="normal")
                else:
                    button.configure(text=chr(65+index)+". 无可用答案",state="disabled")
            set_locked(False)
        def finish_answer():
            self.status.set("请教中：已保存"+str(count["saved"])+"，重复未保存"+str(count["duplicates"])+"，跳过"+str(count["skipped"])+"，拒绝记录"+str(count["rejected"])+"；模型需要复习")
            schedule(140,new_question)
        def choose(index):
            if self.ask_window is None or state["locked"] or index>=len(state["choices"]):
                return
            set_locked(True)
            question_frame=state["frame"]
            action=state["choices"][index]
            saved=self.store.append_sample(game["id"],question_frame["f"],action,"teach_live",{"previous_action":"","seconds_since_previous":60.0,"previous_action_changed_frame":True,"motion_channel_valid":question_frame.get("motion_valid",False)},question_frame.get("gray"),3.0)
            if saved:
                count["saved"]+=1
            else:
                count["duplicates"]+=1
            finish_answer()
        def skip():
            if state["locked"]:
                return
            set_locked(True)
            count["skipped"]+=1
            finish_answer()
        def reject():
            if state["locked"]:
                return
            set_locked(True)
            question_frame=state["frame"]
            self.store.append_rejection(game["id"],question_frame["f"],state["candidates"],"teach_live_reject",question_frame.get("gray"))
            count["rejected"]+=1
            finish_answer()
        def custom():
            if state["locked"]:
                return
            set_locked(True)
            dialog=tk.Toplevel(win)
            dialog.title("自定义点击/拖动")
            dialog.geometry("720x500")
            dialog.transient(win)
            dialog.grab_set()
            ttk.Label(dialog,text="在实时画面上按下并释放左键：短距离为点击，移动为拖动；取消不会保存。",wraplength=680).pack(pady=10)
            custom_canvas=tk.Canvas(dialog,width=672,height=378,bg="black",highlightthickness=1,highlightbackground="#777777")
            custom_canvas.pack()
            custom_canvas.create_image(336,189,image=state["image"][1])
            drag={"start":None,"start_time":0.0,"line":None}
            def press(event):
                drag["start"]=(event.x,event.y)
                drag["start_time"]=time.time()
            def motion_event(event):
                if drag["start"]:
                    if drag["line"]:
                        custom_canvas.delete(drag["line"])
                    drag["line"]=custom_canvas.create_line(drag["start"][0],drag["start"][1],event.x,event.y,width=3,arrow="last")
            def release(event):
                if not drag["start"]:
                    return
                sx,sy=drag["start"]
                ex=max(0,min(671,event.x))
                ey=max(0,min(377,event.y))
                start=[sx/671,sy/377]
                end=[ex/671,ey/377]
                duration=max(0.03,min(3.0,time.time()-drag["start_time"]))
                kind="drag" if math.hypot(end[0]-start[0],end[1]-start[1])>0.035 else "click"
                action={"kind":kind,"button":"left","path":[start,end] if kind=="drag" else [end],"duration":duration}
                question_frame=state["frame"]
                saved=self.store.append_sample(game["id"],question_frame["f"],action,"teach_live_custom",{"previous_action":"","seconds_since_previous":60.0,"previous_action_changed_frame":True,"motion_channel_valid":question_frame.get("motion_valid",False)},question_frame.get("gray"),3.5)
                if saved:
                    count["saved"]+=1
                else:
                    count["duplicates"]+=1
                dialog.destroy()
                finish_answer()
            def cancel():
                dialog.destroy()
                set_locked(False)
            custom_canvas.bind("<ButtonPress-1>",press)
            custom_canvas.bind("<B1-Motion>",motion_event)
            custom_canvas.bind("<ButtonRelease-1>",release)
            ttk.Button(dialog,text="取消",command=cancel).pack(pady=10)
            dialog.protocol("WM_DELETE_WINDOW",cancel)
        for index in range(4):
            button=ttk.Button(choice_frame,text=chr(65+index),command=lambda position=index:choose(position))
            button.pack(fill="x",pady=3,ipady=6)
            answer_buttons.append(button)
        tools=ttk.Frame(frame)
        tools.pack(fill="x",pady=(8,0))
        skip_button=ttk.Button(tools,text="跳过此题",command=skip)
        skip_button.pack(side="left",padx=(0,6))
        reject_button=ttk.Button(tools,text="都不正确",command=reject)
        reject_button.pack(side="left",padx=6)
        custom_button=ttk.Button(tools,text="自定义点击/拖动",command=custom)
        custom_button.pack(side="left",padx=6)
        ttk.Button(tools,text="结束请教",command=self.close_ask).pack(side="right")
        win.protocol("WM_DELETE_WINDOW",self.close_ask)
        self.ask_escape_armed=not self.api.key_down(0x1B)
        def poll_escape():
            if self.ask_window is None:
                return
            down=self.api.key_down(0x1B)
            if not down:
                self.ask_escape_armed=True
            elif self.ask_escape_armed:
                self.close_ask()
                return
            schedule(45,poll_escape)
        schedule(120,new_question)
        poll_escape()
        win.wait_visibility()
        win.focus_force()
    def close_ask(self):
        if self.ask_window is None:
            return
        win=self.ask_window
        self.ask_window=None
        for after_id in list(self.ask_after_ids):
            try:
                win.after_cancel(after_id)
            except Exception:
                pass
        self.ask_after_ids.clear()
        if self.ask_buffer is not None:
            self.ask_buffer.stop()
            self.ask_buffer=None
        try:
            win.destroy()
        except Exception:
            pass
        self.mode=None
        self.set_controls(False)
        self.status.set("请教已结束；实时答案和拒绝记录已写入数据库，模型需要复习")
        self._refresh_all()
    def open_data_dialog(self):
        if self.mode:
            self.show_error("请先停止当前模式")
            return
        try:
            game=self.require_game()
        except Exception as error:
            self.show_error(str(error))
            return
        win=tk.Toplevel(self.root)
        win.title("数据清理")
        win.geometry("560x300")
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=18)
        frame.pack(fill="both",expand=True)
        text=tk.StringVar()
        ttk.Label(frame,text="当前游戏数据维护",font=("Microsoft YaHei UI",13,"bold")).pack(anchor="w",pady=(0,10))
        ttk.Label(frame,textvariable=text,wraplength=510).pack(anchor="w",fill="x")
        def refresh():
            stats=self.store.sample_stats(game["id"])
            model=self.store.load_model(game["id"])
            text.set("游戏："+game["name"]+"\n有效样本："+str(stats["valid"])+"\n异常行："+str(stats["invalid"])+"\n数据大小："+str(round(stats["bytes"]/1024,1))+" KB\n模型原型："+str(len(model.get("prototypes",[])) if model else 0))
        def compact():
            result=self.store.compact_samples(game["id"])
            self.status.set("数据整理完成：保留"+str(result["kept"])+"，移除"+str(result["removed"]))
            refresh()
            self._refresh_all()
        def restore():
            self.store.restore_model_backup(game["id"])
            self.status.set("已从数据库中的完整校验备份恢复模型")
            refresh()
            self._refresh_all()
        def clear():
            if not self.confirm_dialog("清空数据","确认清空当前游戏的全部样本、模型和备份吗？此操作不可撤销。"):
                return
            self.store.clear_game_data(game["id"])
            self.status.set("已清空当前游戏数据")
            win.destroy()
            self._refresh_all()
        buttons=ttk.Frame(frame)
        buttons.pack(side="bottom",fill="x",pady=(14,0))
        ttk.Button(buttons,text="压缩重复样本",command=compact).pack(side="left",padx=(0,6))
        ttk.Button(buttons,text="恢复模型备份",command=restore).pack(side="left",padx=6)
        ttk.Button(buttons,text="清空全部数据",command=clear).pack(side="left",padx=6)
        ttk.Button(buttons,text="关闭",command=win.destroy).pack(side="right")
        refresh()
    def close(self):
        self.api.release_all_buttons()
        if self.stop_event:
            self.stop_event.set()
        if self.ask_window is not None:
            self.close_ask()
        if self.mode_thread and self.mode_thread.is_alive() and self.mode_thread is not threading.current_thread():
            self.mode_thread.join(2.0)
        try:
            self.store.close()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
def install_global_hooks(app_holder):
    def sys_hook(exc_type,exc_value,exc_traceback):
        text="".join(traceback.format_exception(exc_type,exc_value,exc_traceback))
        app=app_holder.get("app")
        if app:
            app.show_error(text)
        else:
            try:
                sys.stderr.write(text)
            except Exception:
                pass
    def thread_hook(args):
        sys_hook(args.exc_type,args.exc_value,args.exc_traceback)
    sys.excepthook=sys_hook
    if hasattr(threading,"excepthook"):
        threading.excepthook=thread_hook
def startup_error(root,text):
    root.withdraw()
    win=tk.Toplevel(root)
    win.title("报错信息")
    win.geometry("700x390")
    frame=ttk.Frame(win,padding=14)
    frame.pack(fill="both",expand=True)
    widget=tk.Text(frame,wrap="word",font=("Microsoft YaHei UI",10))
    widget.pack(fill="both",expand=True)
    widget.insert("1.0",text)
    widget.configure(state="disabled")
    ttk.Button(frame,text="确认",command=root.destroy).pack(pady=(10,0))
    win.protocol("WM_DELETE_WINDOW",root.destroy)
def main():
    holder={"app":None}
    install_global_hooks(holder)
    root=tk.Tk()
    try:
        holder["app"]=App(root)
    except Exception:
        startup_error(root,traceback.format_exc())
    root.mainloop()
if __name__=="__main__":
    main()
