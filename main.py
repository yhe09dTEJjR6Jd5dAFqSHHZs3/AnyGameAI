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
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import ctypes
from ctypes import wintypes
class POINT(ctypes.Structure):
    _fields_=[("x",wintypes.LONG),("y",wintypes.LONG)]
class RECT(ctypes.Structure):
    _fields_=[("left",wintypes.LONG),("top",wintypes.LONG),("right",wintypes.LONG),("bottom",wintypes.LONG)]
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_=[("biSize",wintypes.DWORD),("biWidth",wintypes.LONG),("biHeight",wintypes.LONG),("biPlanes",wintypes.WORD),("biBitCount",wintypes.WORD),("biCompression",wintypes.DWORD),("biSizeImage",wintypes.DWORD),("biXPelsPerMeter",wintypes.LONG),("biYPelsPerMeter",wintypes.LONG),("biClrUsed",wintypes.DWORD),("biClrImportant",wintypes.DWORD)]
class BITMAPINFO(ctypes.Structure):
    _fields_=[("bmiHeader",BITMAPINFOHEADER),("bmiColors",wintypes.DWORD*3)]
class WinBridge:
    def __init__(self):
        if os.name!="nt":
            raise RuntimeError("本程序只能在Windows 11上运行")
        self.user32=ctypes.WinDLL("user32",use_last_error=True)
        self.gdi32=ctypes.WinDLL("gdi32",use_last_error=True)
        self.kernel32=ctypes.WinDLL("kernel32",use_last_error=True)
        try:
            self.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except Exception:
            try:
                self.user32.SetProcessDPIAware()
            except Exception:
                pass
        self._bind()
    def _bind(self):
        self.WNDENUMPROC=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
        self.user32.EnumWindows.argtypes=[self.WNDENUMPROC,wintypes.LPARAM]
        self.user32.EnumWindows.restype=wintypes.BOOL
        self.user32.IsWindow.argtypes=[wintypes.HWND]
        self.user32.IsWindow.restype=wintypes.BOOL
        self.user32.IsWindowVisible.argtypes=[wintypes.HWND]
        self.user32.IsWindowVisible.restype=wintypes.BOOL
        self.user32.IsIconic.argtypes=[wintypes.HWND]
        self.user32.IsIconic.restype=wintypes.BOOL
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
        self.user32.GetCursorPos.argtypes=[ctypes.POINTER(POINT)]
        self.user32.GetCursorPos.restype=wintypes.BOOL
        self.user32.GetAsyncKeyState.argtypes=[ctypes.c_int]
        self.user32.GetAsyncKeyState.restype=wintypes.SHORT
        self.user32.SetCursorPos.argtypes=[ctypes.c_int,ctypes.c_int]
        self.user32.SetCursorPos.restype=wintypes.BOOL
        self.user32.mouse_event.argtypes=[wintypes.DWORD,wintypes.DWORD,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p]
        self.user32.SetForegroundWindow.argtypes=[wintypes.HWND]
        self.user32.SetForegroundWindow.restype=wintypes.BOOL
        self.user32.GetDC.argtypes=[wintypes.HWND]
        self.user32.GetDC.restype=wintypes.HDC
        self.user32.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC]
        self.user32.ReleaseDC.restype=ctypes.c_int
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
    def enum_windows(self):
        result=[]
        own_pid=os.getpid()
        callback_type=self.WNDENUMPROC
        def callback(hwnd,lparam):
            if not self.user32.IsWindowVisible(hwnd):
                return True
            length=self.user32.GetWindowTextLengthW(hwnd)
            if length<=0:
                return True
            title_buf=ctypes.create_unicode_buffer(length+1)
            self.user32.GetWindowTextW(hwnd,title_buf,length+1)
            title=title_buf.value.strip()
            if not title:
                return True
            pid=wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
            if pid.value==own_pid:
                return True
            class_buf=ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd,class_buf,256)
            result.append({"hwnd":int(hwnd),"title":title,"class":class_buf.value,"pid":int(pid.value),"minimized":bool(self.user32.IsIconic(hwnd))})
            return True
        cb=callback_type(callback)
        if not self.user32.EnumWindows(cb,0):
            raise ctypes.WinError(ctypes.get_last_error())
        result.sort(key=lambda x:(x["minimized"],x["title"].lower()))
        return result
    def client_rect(self,hwnd):
        if not self.valid(hwnd):
            raise RuntimeError("已选择的窗口不存在，请重新选择窗口")
        if self.user32.IsIconic(wintypes.HWND(hwnd)):
            raise RuntimeError("已选择的窗口处于最小化状态，请先还原窗口")
        rect=RECT()
        if not self.user32.GetClientRect(wintypes.HWND(hwnd),ctypes.byref(rect)):
            raise ctypes.WinError(ctypes.get_last_error())
        p1=POINT(rect.left,rect.top)
        p2=POINT(rect.right,rect.bottom)
        if not self.user32.ClientToScreen(wintypes.HWND(hwnd),ctypes.byref(p1)) or not self.user32.ClientToScreen(wintypes.HWND(hwnd),ctypes.byref(p2)):
            raise ctypes.WinError(ctypes.get_last_error())
        width=p2.x-p1.x
        height=p2.y-p1.y
        if width<2 or height<2:
            raise RuntimeError("所选窗口的客户区尺寸无效")
        return int(p1.x),int(p1.y),int(width),int(height)
    def foreground(self,hwnd):
        if self.valid(hwnd):
            self.user32.SetForegroundWindow(wintypes.HWND(hwnd))
    def cursor(self):
        p=POINT()
        if not self.user32.GetCursorPos(ctypes.byref(p)):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(p.x),int(p.y)
    def key_down(self,vk):
        return bool(self.user32.GetAsyncKeyState(vk)&0x8000)
    def capture(self,hwnd,out_w=16,out_h=9):
        x,y,w,h=self.client_rect(hwnd)
        src=self.user32.GetDC(wintypes.HWND(0))
        if not src:
            raise ctypes.WinError(ctypes.get_last_error())
        mem=self.gdi32.CreateCompatibleDC(src)
        if not mem:
            self.user32.ReleaseDC(wintypes.HWND(0),src)
            raise ctypes.WinError(ctypes.get_last_error())
        bmi=BITMAPINFO()
        bmi.bmiHeader.biSize=ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth=out_w
        bmi.bmiHeader.biHeight=-out_h
        bmi.bmiHeader.biPlanes=1
        bmi.bmiHeader.biBitCount=32
        bmi.bmiHeader.biCompression=0
        bits=ctypes.c_void_p()
        bitmap=self.gdi32.CreateDIBSection(src,ctypes.byref(bmi),0,ctypes.byref(bits),None,0)
        if not bitmap:
            self.gdi32.DeleteDC(mem)
            self.user32.ReleaseDC(wintypes.HWND(0),src)
            raise ctypes.WinError(ctypes.get_last_error())
        old=self.gdi32.SelectObject(mem,bitmap)
        try:
            self.gdi32.SetStretchBltMode(mem,4)
            ok=self.gdi32.StretchBlt(mem,0,0,out_w,out_h,src,x,y,w,h,0x00CC0020)
            if not ok:
                raise ctypes.WinError(ctypes.get_last_error())
            raw=ctypes.string_at(bits.value,out_w*out_h*4)
            feature=[]
            for i in range(0,len(raw),4):
                b=raw[i]
                g=raw[i+1]
                r=raw[i+2]
                feature.append((r*77+g*150+b*29)>>8)
            return feature
        finally:
            self.gdi32.SelectObject(mem,old)
            self.gdi32.DeleteObject(bitmap)
            self.gdi32.DeleteDC(mem)
            self.user32.ReleaseDC(wintypes.HWND(0),src)
    def set_cursor(self,x,y):
        if not self.user32.SetCursorPos(int(x),int(y)):
            raise ctypes.WinError(ctypes.get_last_error())
    def button_event(self,button,down):
        flags={"left":(0x0002,0x0004),"right":(0x0008,0x0010),"middle":(0x0020,0x0040)}
        if button not in flags:
            return
        self.user32.mouse_event(flags[button][0 if down else 1],0,0,0,None)
class DataStore:
    def __init__(self):
        self.base=Path(sys.argv[0]).resolve().parent/".universal_game_ai"
        self.base.mkdir(parents=True,exist_ok=True)
        (self.base/"samples").mkdir(exist_ok=True)
        (self.base/"models").mkdir(exist_ok=True)
        self.config_path=self.base/"config.json"
        self.lock=threading.RLock()
        self.config=self._load_json(self.config_path,{"games":[],"selected_game":None})
        if not isinstance(self.config,dict):
            self.config={"games":[],"selected_game":None}
        if not isinstance(self.config.get("games"),list):
            self.config["games"]=[]
    def _load_json(self,path,default):
        try:
            with path.open("r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    def _write_json(self,path,data):
        temp=path.with_suffix(path.suffix+".tmp")
        with temp.open("w",encoding="utf-8",newline="\n") as f:
            json.dump(data,f,ensure_ascii=False,separators=(",",":"))
        os.replace(temp,path)
    def save_config(self):
        with self.lock:
            self._write_json(self.config_path,self.config)
    def games(self):
        with self.lock:
            return [dict(x) for x in self.config.get("games",[]) if isinstance(x,dict) and x.get("id") and x.get("name")]
    def replace_games(self,games,selected):
        with self.lock:
            old_ids={x.get("id") for x in self.config.get("games",[]) if isinstance(x,dict)}
            new_ids={x.get("id") for x in games}
            removed=old_ids-new_ids
            self.config["games"]=[dict(x) for x in games]
            self.config["selected_game"]=selected
            self.save_config()
            for gid in removed:
                for path in (self.sample_path(gid),self.model_path(gid)):
                    try:
                        path.unlink()
                    except FileNotFoundError:
                        pass
    def selected_game(self):
        gid=self.config.get("selected_game")
        for game in self.games():
            if game["id"]==gid:
                return game
        return None
    def sample_path(self,gid):
        return self.base/"samples"/(gid+".jsonl")
    def model_path(self,gid):
        return self.base/"models"/(gid+".json")
    def append_sample(self,gid,sample):
        line=json.dumps(sample,ensure_ascii=False,separators=(",",":"))
        with self.lock:
            with self.sample_path(gid).open("a",encoding="utf-8",newline="\n") as f:
                f.write(line+"\n")
    def load_samples(self,gid):
        result=[]
        path=self.sample_path(gid)
        if not path.exists():
            return result
        with self.lock:
            with path.open("r",encoding="utf-8") as f:
                for line in f:
                    try:
                        item=json.loads(line)
                        if isinstance(item,dict) and isinstance(item.get("f"),list) and isinstance(item.get("a"),dict):
                            result.append(item)
                    except Exception:
                        pass
        return result
    def save_model(self,gid,model):
        with self.lock:
            self._write_json(self.model_path(gid),model)
    def load_model(self,gid):
        model=self._load_json(self.model_path(gid),None)
        if isinstance(model,dict) and isinstance(model.get("prototypes"),list):
            return model
        return None
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
        self.buttons=[]
        self.status=tk.StringVar(value="就绪")
        self.game_text=tk.StringVar()
        self.window_text=tk.StringVar()
        self.ask_window=None
        self.ask_escape_armed=False
        self._build()
        self._refresh_labels()
        self.root.protocol("WM_DELETE_WINDOW",self.close)
    def _build(self):
        self.root.title("通用游戏AI")
        self.root.geometry("640x390")
        self.root.minsize(560,350)
        self.root.option_add("*Font",("Microsoft YaHei UI",11))
        outer=ttk.Frame(self.root,padding=20)
        outer.pack(fill="both",expand=True)
        title=ttk.Label(outer,text="通用游戏AI控制面板",font=("Microsoft YaHei UI",18,"bold"))
        title.pack(anchor="w",pady=(0,16))
        info=ttk.Frame(outer)
        info.pack(fill="x",pady=(0,16))
        ttk.Label(info,text="当前游戏：").grid(row=0,column=0,sticky="w",pady=3)
        ttk.Label(info,textvariable=self.game_text).grid(row=0,column=1,sticky="w",pady=3)
        ttk.Label(info,text="目标窗口：").grid(row=1,column=0,sticky="w",pady=3)
        ttk.Label(info,textvariable=self.window_text).grid(row=1,column=1,sticky="w",pady=3)
        info.columnconfigure(1,weight=1)
        grid=ttk.Frame(outer)
        grid.pack(fill="both",expand=True)
        specs=[("游戏",self.open_game_dialog),("选择窗口",self.open_window_dialog),("学习",self.start_learning),("复习",self.start_review),("训练",self.start_training),("请教",self.start_ask)]
        for i,(text,command) in enumerate(specs):
            button=ttk.Button(grid,text=text,command=command)
            button.grid(row=i//2,column=i%2,sticky="nsew",padx=7,pady=7,ipady=13)
            self.buttons.append(button)
        grid.columnconfigure(0,weight=1)
        grid.columnconfigure(1,weight=1)
        for row in range(3):
            grid.rowconfigure(row,weight=1)
        bottom=ttk.Frame(outer)
        bottom.pack(fill="x",pady=(14,0))
        ttk.Label(bottom,text="状态：").pack(side="left")
        ttk.Label(bottom,textvariable=self.status).pack(side="left",fill="x",expand=True)
        ttk.Label(bottom,text="运行模式中按ESC结束").pack(side="right")
    def _refresh_labels(self):
        self.game_text.set(self.selected_game["name"] if self.selected_game else "未选择")
        self.window_text.set(self.selected_window["title"] if self.selected_window else "未选择")
    def ui(self,func):
        try:
            self.root.after(0,func)
        except Exception:
            pass
    def set_status(self,text):
        self.ui(lambda:self.status.set(text))
    def show_error(self,text):
        if threading.current_thread() is not threading.main_thread():
            self.ui(lambda:self.show_error(text))
            return
        win=tk.Toplevel(self.root)
        win.title("报错信息")
        win.geometry("660x360")
        win.minsize(460,260)
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=14)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="报错信息",font=("Microsoft YaHei UI",14,"bold")).pack(anchor="w",pady=(0,8))
        body=ttk.Frame(frame)
        body.pack(fill="both",expand=True)
        text_widget=tk.Text(body,wrap="word",font=("Microsoft YaHei UI",10),relief="solid",borderwidth=1)
        scroll=ttk.Scrollbar(body,orient="vertical",command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        text_widget.pack(side="left",fill="both",expand=True)
        scroll.pack(side="right",fill="y")
        text_widget.insert("1.0",str(text))
        text_widget.configure(state="disabled")
        ttk.Button(frame,text="确认",command=win.destroy).pack(pady=(12,0),ipadx=22)
        win.bind("<Return>",lambda e:win.destroy())
        win.protocol("WM_DELETE_WINDOW",win.destroy)
        win.wait_visibility()
        win.focus_force()
    def prompt_text(self,title,label,initial=""):
        result={"value":None}
        win=tk.Toplevel(self.root)
        win.title(title)
        win.geometry("430x180")
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
        entry.bind("<Return>",lambda e:confirm())
        entry.bind("<Escape>",lambda e:win.destroy())
        entry.focus_set()
        win.wait_window()
        return result["value"]
    def confirm_dialog(self,title,text):
        result={"value":False}
        win=tk.Toplevel(self.root)
        win.title(title)
        win.geometry("460x190")
        win.resizable(False,False)
        win.transient(self.root)
        win.grab_set()
        frame=ttk.Frame(win,padding=20)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text=text,wraplength=410,justify="left").pack(fill="x",expand=True)
        buttons=ttk.Frame(frame)
        buttons.pack(side="bottom")
        def yes():
            result["value"]=True
            win.destroy()
        ttk.Button(buttons,text="确认",command=yes).pack(side="left",padx=6)
        ttk.Button(buttons,text="取消",command=win.destroy).pack(side="left",padx=6)
        win.wait_window()
        return result["value"]
    def open_game_dialog(self):
        if self.mode:
            self.show_error("请先按ESC结束当前模式")
            return
        original=self.store.games()
        games=[dict(x) for x in original]
        selected_id=self.selected_game["id"] if self.selected_game else None
        win=tk.Toplevel(self.root)
        win.title("游戏")
        win.geometry("520x430")
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
        def refresh(select=None):
            box.delete(0,"end")
            for game in games:
                box.insert("end",game["name"])
            target=select or selected_id
            for i,game in enumerate(games):
                if game["id"]==target:
                    box.selection_set(i)
                    box.see(i)
                    break
        def current_index():
            selection=box.curselection()
            return selection[0] if selection else None
        def add_game():
            name=self.prompt_text("新建游戏","输入游戏名称")
            if name is None:
                return
            if any(x["name"].casefold()==name.casefold() for x in games):
                self.show_error("游戏名称已存在")
                return
            game={"id":uuid.uuid4().hex,"name":name,"created":time.time()}
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
            if any(i!=index and x["name"].casefold()==name.casefold() for i,x in enumerate(games)):
                self.show_error("游戏名称已存在")
                return
            games[index]["name"]=name
            refresh(games[index]["id"])
        def delete_game():
            index=current_index()
            if index is None:
                self.show_error("请先选择一个游戏")
                return
            if not self.confirm_dialog("删除游戏","确认删除“"+games[index]["name"]+"”及其学习数据和模型吗？"):
                return
            del games[index]
            refresh(games[min(index,len(games)-1)]["id"] if games else None)
        def confirm():
            selection=box.curselection()
            if not selection:
                self.show_error("请先选择一个游戏；如果列表为空，请先新建游戏")
                return
            chosen=games[selection[0]]
            self.store.replace_games(games,chosen["id"])
            self.selected_game=dict(chosen)
            self._refresh_labels()
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
        box.bind("<Double-Button-1>",lambda e:confirm())
        refresh()
        win.wait_visibility()
        box.focus_set()
    def open_window_dialog(self):
        if self.mode:
            self.show_error("请先按ESC结束当前模式")
            return
        win=tk.Toplevel(self.root)
        win.title("选择窗口")
        win.geometry("760x500")
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
            try:
                windows=self.api.enum_windows()
                box.delete(0,"end")
                selected_index=None
                for i,item in enumerate(windows):
                    prefix="[最小化] " if item["minimized"] else ""
                    box.insert("end",prefix+item["title"]+"    ["+item["class"]+"]")
                    if self.selected_window and item["hwnd"]==self.selected_window["hwnd"]:
                        selected_index=i
                if selected_index is not None:
                    box.selection_set(selected_index)
                    box.see(selected_index)
            except Exception as e:
                self.show_error(str(e))
        def confirm():
            selection=box.curselection()
            if not selection:
                self.show_error("请先选择一个窗口")
                return
            item=windows[selection[0]]
            try:
                self.api.client_rect(item["hwnd"])
            except Exception as e:
                self.show_error(str(e))
                return
            self.selected_window=dict(item)
            self._refresh_labels()
            self.status.set("已选择窗口："+item["title"])
            win.destroy()
        tools=ttk.Frame(frame)
        tools.pack(fill="x",pady=(10,0))
        ttk.Button(tools,text="刷新",command=refresh).pack(side="left")
        ttk.Button(tools,text="确认",command=confirm).pack(side="right",padx=(6,0))
        ttk.Button(tools,text="取消",command=win.destroy).pack(side="right")
        box.bind("<Double-Button-1>",lambda e:confirm())
        refresh()
        win.wait_visibility()
        box.focus_set()
    def require_game(self):
        if not self.selected_game:
            raise RuntimeError("请先点击“游戏”按钮选择或新建游戏")
        return self.selected_game
    def require_window(self):
        if not self.selected_window:
            raise RuntimeError("请先点击“选择窗口”按钮选择目标窗口")
        if not self.api.valid(self.selected_window["hwnd"]):
            self.selected_window=None
            self.ui(self._refresh_labels)
            raise RuntimeError("已选择的窗口不存在，请重新选择窗口")
        self.api.client_rect(self.selected_window["hwnd"])
        return self.selected_window
    def set_controls(self,enabled):
        state="normal" if enabled else "disabled"
        for button in self.buttons:
            button.configure(state=state)
    def start_worker(self,name,target):
        if self.mode:
            self.show_error("当前正在“"+self.mode+"”，请先按ESC结束")
            return
        try:
            self.require_game()
            if name in ("学习","训练"):
                self.require_window()
        except Exception as e:
            self.show_error(str(e))
            return
        self.mode=name
        self.stop_event=threading.Event()
        self.set_controls(False)
        self.status.set(name+"已开始，按ESC结束")
        self.mode_thread=threading.Thread(target=self.worker_entry,args=(name,target),daemon=True)
        self.mode_thread.start()
    def worker_entry(self,name,target):
        error=None
        final_text=name+"已结束"
        try:
            final_text=target()
        except Exception:
            error=traceback.format_exc()
        def finish():
            self.mode=None
            self.stop_event=None
            self.mode_thread=None
            self.set_controls(True)
            self.status.set(final_text)
            if error:
                self.show_error(error)
        self.ui(finish)
    def wait_escape_release(self):
        while self.api.key_down(0x1B) and self.stop_event and not self.stop_event.is_set():
            time.sleep(0.04)
    def should_stop(self):
        if not self.stop_event or self.stop_event.is_set():
            return True
        if self.api.key_down(0x1B):
            self.stop_event.set()
            return True
        return False
    def normalize_point(self,x,y,rect):
        rx,ry,rw,rh=rect
        nx=(x-rx)/max(1,rw-1)
        ny=(y-ry)/max(1,rh-1)
        return [max(0.0,min(1.0,nx)),max(0.0,min(1.0,ny))]
    def inside(self,x,y,rect):
        rx,ry,rw,rh=rect
        return rx<=x<rx+rw and ry<=y<ry+rh
    def start_learning(self):
        self.start_worker("学习",self.learning_worker)
    def learning_worker(self):
        game=self.require_game()
        window=self.require_window()
        hwnd=window["hwnd"]
        self.api.foreground(hwnd)
        self.wait_escape_release()
        buttons={"left":0x01,"right":0x02,"middle":0x04}
        previous={name:self.api.key_down(vk) for name,vk in buttons.items()}
        active={}
        learned=0
        last_update=0.0
        while not self.should_stop():
            rect=self.api.client_rect(hwnd)
            cx,cy=self.api.cursor()
            now=time.time()
            for name,vk in buttons.items():
                down=self.api.key_down(vk)
                if down and not previous[name] and self.inside(cx,cy,rect):
                    feature=self.api.capture(hwnd)
                    point=self.normalize_point(cx,cy,rect)
                    active[name]={"feature":feature,"path":[point],"start":now,"last_time":now,"last_point":point}
                if down and name in active:
                    point=self.normalize_point(cx,cy,rect)
                    last=active[name]["last_point"]
                    distance=abs(point[0]-last[0])+abs(point[1]-last[1])
                    if now-active[name]["last_time"]>=0.045 and distance>=0.006:
                        active[name]["path"].append(point)
                        active[name]["last_time"]=now
                        active[name]["last_point"]=point
                if not down and previous[name] and name in active:
                    item=active.pop(name)
                    point=self.normalize_point(cx,cy,rect)
                    if not item["path"] or abs(point[0]-item["path"][-1][0])+abs(point[1]-item["path"][-1][1])>0.002:
                        item["path"].append(point)
                    path=item["path"]
                    if len(path)>80:
                        step=(len(path)-1)/79
                        path=[path[round(i*step)] for i in range(80)]
                    action={"kind":"gesture","button":name,"path":[[round(p[0],5),round(p[1],5)] for p in path],"duration":round(max(0.03,min(3.0,now-item["start"])),3)}
                    sample={"t":time.time(),"f":item["feature"],"a":action,"source":"learn"}
                    self.store.append_sample(game["id"],sample)
                    learned+=1
                previous[name]=down
            if now-last_update>0.5:
                self.set_status("学习中：已记录"+str(learned)+"个鼠标动作，按ESC结束")
                last_update=now
            time.sleep(0.012)
        return "学习已结束，本次记录"+str(learned)+"个鼠标动作"
    def feature_distance(self,a,b):
        if len(a)!=len(b) or not a:
            return float("inf")
        total=0.0
        for x,y in zip(a,b):
            d=float(x)-float(y)
            total+=d*d
        return total/len(a)
    def action_signature(self,action):
        button=action.get("button","left")
        path=action.get("path") or [[0.5,0.5]]
        first=path[0]
        last=path[-1]
        drag=1 if abs(first[0]-last[0])+abs(first[1]-last[1])>0.06 else 0
        values=[button,str(drag),str(int(max(0,min(7,float(first[0])*8)))),str(int(max(0,min(5,float(first[1])*6)))),str(int(max(0,min(7,float(last[0])*8)))),str(int(max(0,min(5,float(last[1])*6))))]
        return "|".join(values)
    def start_review(self):
        self.start_worker("复习",self.review_worker)
    def review_worker(self):
        game=self.require_game()
        samples=self.store.load_samples(game["id"])
        samples=[x for x in samples if len(x.get("f",[]))==144 and isinstance(x.get("a"),dict)]
        if not samples:
            raise RuntimeError("没有可复习的学习数据，请先进行学习")
        self.wait_escape_release()
        prototypes=[]
        max_prototypes=min(256,max(24,int(math.sqrt(len(samples))*8)))
        threshold=1150.0
        stopped=False
        for index,sample in enumerate(samples):
            if self.should_stop():
                stopped=True
                break
            feature=[float(v) for v in sample["f"]]
            action=sample["a"]
            signature=self.action_signature(action)
            if not prototypes:
                prototypes.append({"f":feature,"n":1,"votes":{signature:[1,action]}})
            else:
                best_index=0
                best_distance=self.feature_distance(feature,prototypes[0]["f"])
                for i in range(1,len(prototypes)):
                    distance=self.feature_distance(feature,prototypes[i]["f"])
                    if distance<best_distance:
                        best_distance=distance
                        best_index=i
                if best_distance>threshold and len(prototypes)<max_prototypes:
                    prototypes.append({"f":feature,"n":1,"votes":{signature:[1,action]}})
                else:
                    proto=prototypes[best_index]
                    new_n=proto["n"]+1
                    weight=1.0/new_n
                    proto["f"]=[old+(new-old)*weight for old,new in zip(proto["f"],feature)]
                    proto["n"]=new_n
                    if signature in proto["votes"]:
                        proto["votes"][signature][0]+=1
                    else:
                        proto["votes"][signature]=[1,action]
            if index%10==0:
                self.set_status("复习中："+str(index+1)+"/"+str(len(samples))+"，原型"+str(len(prototypes))+"个，按ESC结束")
        optimized=[]
        for proto in prototypes:
            best=max(proto["votes"].values(),key=lambda x:x[0])
            optimized.append({"f":[int(round(max(0,min(255,v)))) for v in proto["f"]],"a":best[1],"n":proto["n"],"support":best[0]})
        if not optimized:
            return "复习已取消，未生成模型"
        model={"version":1,"created":time.time(),"samples":len(samples),"stopped":stopped,"prototypes":optimized}
        self.store.save_model(game["id"],model)
        return ("复习已提前结束并保存部分模型：" if stopped else "复习完成：")+str(len(optimized))+"个行为原型"
    def point_to_screen(self,point,rect):
        x,y,w,h=rect
        px=x+round(max(0.0,min(1.0,float(point[0])))*max(1,w-1))
        py=y+round(max(0.0,min(1.0,float(point[1])))*max(1,h-1))
        return px,py
    def execute_action(self,hwnd,action):
        rect=self.api.client_rect(hwnd)
        path=action.get("path") or [[0.5,0.5]]
        clean=[]
        for point in path:
            if isinstance(point,list) and len(point)>=2:
                clean.append([float(point[0]),float(point[1])])
        if not clean:
            clean=[[0.5,0.5]]
        button=action.get("button","left")
        duration=max(0.03,min(1.8,float(action.get("duration",0.12))))
        self.api.set_cursor(*self.point_to_screen(clean[0],rect))
        if self.should_stop():
            return
        self.api.button_event(button,True)
        try:
            if len(clean)==1:
                end=time.time()+min(0.15,duration)
                while time.time()<end:
                    if self.should_stop():
                        break
                    time.sleep(0.01)
            else:
                step_duration=duration/max(1,len(clean)-1)
                for point in clean[1:]:
                    if self.should_stop():
                        break
                    self.api.set_cursor(*self.point_to_screen(point,rect))
                    end=time.time()+step_duration
                    while time.time()<end:
                        if self.should_stop():
                            break
                        time.sleep(min(0.012,max(0.001,end-time.time())))
        finally:
            self.api.button_event(button,False)
    def action_text(self,action):
        names={"left":"左键","right":"右键","middle":"中键"}
        button=names.get(action.get("button"),"左键")
        path=action.get("path") or [[0.5,0.5]]
        start=path[0]
        end=path[-1]
        sx=int(round(float(start[0])*100))
        sy=int(round(float(start[1])*100))
        ex=int(round(float(end[0])*100))
        ey=int(round(float(end[1])*100))
        if abs(float(start[0])-float(end[0]))+abs(float(start[1])-float(end[1]))>0.06:
            return button+"拖动：("+str(sx)+"%, "+str(sy)+"%) → ("+str(ex)+"%, "+str(ey)+"%)"
        return button+"点击：("+str(ex)+"%, "+str(ey)+"%)"
    def start_training(self):
        try:
            game=self.require_game()
            model=self.store.load_model(game["id"])
            if not model or not model.get("prototypes"):
                raise RuntimeError("没有可用模型，请先学习并复习")
        except Exception as e:
            self.show_error(str(e))
            return
        self.start_worker("训练",self.training_worker)
    def training_worker(self):
        game=self.require_game()
        window=self.require_window()
        model=self.store.load_model(game["id"])
        prototypes=model.get("prototypes",[]) if model else []
        if not prototypes:
            raise RuntimeError("没有可用模型，请先学习并复习")
        hwnd=window["hwnd"]
        self.api.foreground(hwnd)
        self.wait_escape_release()
        actions=0
        while not self.should_stop():
            feature=self.api.capture(hwnd)
            best=None
            best_distance=float("inf")
            for proto in prototypes:
                distance=self.feature_distance(feature,proto.get("f",[]))
                if distance<best_distance:
                    best_distance=distance
                    best=proto
            if best is None:
                time.sleep(0.2)
                continue
            if best_distance>9000:
                self.set_status("训练中：当前画面与学习数据差异较大，等待识别，按ESC结束")
                end=time.time()+0.25
                while time.time()<end and not self.should_stop():
                    time.sleep(0.03)
                continue
            self.set_status("训练中："+self.action_text(best["a"])+"，匹配差异"+str(int(best_distance))+"，按ESC结束")
            before=feature
            self.execute_action(hwnd,best["a"])
            actions+=1
            if self.should_stop():
                break
            end=time.time()+0.22
            while time.time()<end and not self.should_stop():
                time.sleep(0.02)
            if self.should_stop():
                break
            after=self.api.capture(hwnd)
            change=self.feature_distance(before,after)
            wait=0.55 if change<90 else 0.12
            end=time.time()+wait
            while time.time()<end and not self.should_stop():
                time.sleep(0.025)
        return "训练已结束，AI执行"+str(actions)+"个鼠标动作"
    def basic_actions(self):
        points=[[0.25,0.5],[0.5,0.5],[0.75,0.5],[0.5,0.82],[0.5,0.18],[0.2,0.82],[0.8,0.82],[0.2,0.2],[0.8,0.2]]
        return [{"kind":"gesture","button":"left","path":[p],"duration":0.08} for p in points]
    def start_ask(self):
        if self.mode:
            self.show_error("当前正在“"+self.mode+"”，请先按ESC结束")
            return
        try:
            game=self.require_game()
            samples=self.store.load_samples(game["id"])
            model=self.store.load_model(game["id"])
            pool=[]
            if model:
                pool.extend(model.get("prototypes",[]))
            if not pool:
                pool=[{"f":x["f"],"a":x["a"],"n":1,"support":1} for x in samples if len(x.get("f",[]))==144]
            if not pool:
                raise RuntimeError("没有可请教的画面，请先进行学习")
        except Exception as e:
            self.show_error(str(e))
            return
        self.mode="请教"
        self.set_controls(False)
        self.status.set("请教已开始，选择答案；按ESC结束")
        win=tk.Toplevel(self.root)
        self.ask_window=win
        win.title("请教")
        win.geometry("720x650")
        win.minsize(620,560)
        win.transient(self.root)
        frame=ttk.Frame(win,padding=16)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="请选择此画面中AI应该执行的鼠标动作",font=("Microsoft YaHei UI",14,"bold")).pack(anchor="w")
        ttk.Label(frame,text="灰度缩略图表示学习到的客户区画面；每次选择都会成为新的请教数据。").pack(anchor="w",pady=(4,10))
        canvas=tk.Canvas(frame,width=576,height=324,bg="black",highlightthickness=1,highlightbackground="#777777")
        canvas.pack(fill="both",expand=False)
        choice_frame=ttk.Frame(frame)
        choice_frame.pack(fill="both",expand=True,pady=(12,0))
        answer_buttons=[]
        count={"value":0}
        state={"feature":None,"choices":None,"image":None}
        combined_actions=[]
        for item in pool:
            action=item.get("a")
            if isinstance(action,dict):
                combined_actions.append(action)
        combined_actions.extend(self.basic_actions())
        unique_actions=[]
        signatures=set()
        for action in combined_actions:
            signature=self.action_signature(action)
            if signature not in signatures:
                signatures.add(signature)
                unique_actions.append(action)
        def close_ask():
            if self.ask_window is None:
                return
            self.ask_window=None
            try:
                win.destroy()
            except Exception:
                pass
            self.mode=None
            self.set_controls(True)
            self.status.set("请教已结束，共记录"+str(count["value"])+"个答案")
        def render(feature):
            small=tk.PhotoImage(width=16,height=9)
            rows=[]
            for y in range(9):
                row=[]
                for x in range(16):
                    v=int(max(0,min(255,feature[y*16+x])))
                    row.append("#%02x%02x%02x"%(v,v,v))
                rows.append("{"+" ".join(row)+"}")
            small.put(" ".join(rows))
            scaled=small.zoom(36,36)
            state["image"]=(small,scaled)
            canvas.delete("all")
            canvas.create_image(288,162,image=scaled)
        def new_question():
            if self.ask_window is None:
                return
            seed=random.choice(pool)
            feature=list(seed.get("f",[]))
            if len(feature)!=144:
                new_question()
                return
            ranked=[]
            for item in pool:
                if len(item.get("f",[]))==144 and isinstance(item.get("a"),dict):
                    ranked.append((self.feature_distance(feature,item["f"]),item["a"]))
            ranked.sort(key=lambda x:x[0])
            choices=[]
            seen=set()
            for distance,action in ranked:
                signature=self.action_signature(action)
                if signature not in seen:
                    seen.add(signature)
                    choices.append(action)
                if len(choices)>=4:
                    break
            shuffled=list(unique_actions)
            random.shuffle(shuffled)
            for action in shuffled:
                signature=self.action_signature(action)
                if signature not in seen:
                    seen.add(signature)
                    choices.append(action)
                if len(choices)>=4:
                    break
            while len(choices)<4:
                choices.append(random.choice(self.basic_actions()))
            random.shuffle(choices)
            state["feature"]=feature
            state["choices"]=choices
            render(feature)
            for i,button in enumerate(answer_buttons):
                button.configure(text=chr(65+i)+". "+self.action_text(choices[i]),command=lambda index=i:choose(index))
        def choose(index):
            if self.ask_window is None or state["feature"] is None:
                return
            action=state["choices"][index]
            sample={"t":time.time(),"f":list(state["feature"]),"a":action,"source":"teach"}
            self.store.append_sample(game["id"],sample)
            current=self.store.load_model(game["id"])
            if current and isinstance(current.get("prototypes"),list):
                current["prototypes"].append({"f":list(state["feature"]),"a":action,"n":3,"support":3})
                if len(current["prototypes"])>320:
                    current["prototypes"]=current["prototypes"][-320:]
                current["created"]=time.time()
                self.store.save_model(game["id"],current)
            count["value"]+=1
            self.status.set("请教中：已记录"+str(count["value"])+"个答案，按ESC结束")
            win.after(120,new_question)
        for i in range(4):
            button=ttk.Button(choice_frame,text=chr(65+i),command=lambda index=i:choose(index))
            button.pack(fill="x",pady=4,ipady=8)
            answer_buttons.append(button)
        ttk.Label(frame,text="按ESC结束请教").pack(anchor="e",pady=(8,0))
        win.protocol("WM_DELETE_WINDOW",close_ask)
        self.ask_escape_armed=not self.api.key_down(0x1B)
        def poll_escape():
            if self.ask_window is None:
                return
            down=self.api.key_down(0x1B)
            if not down:
                self.ask_escape_armed=True
            elif self.ask_escape_armed:
                close_ask()
                return
            win.after(45,poll_escape)
        new_question()
        poll_escape()
        win.wait_visibility()
        win.focus_force()
    def close(self):
        if self.stop_event:
            self.stop_event.set()
        if self.ask_window is not None:
            try:
                self.ask_window.destroy()
            except Exception:
                pass
            self.ask_window=None
        self.root.destroy()
def main():
    root=tk.Tk()
    try:
        App(root)
    except Exception:
        error=traceback.format_exc()
        root.withdraw()
        win=tk.Toplevel(root)
        win.title("报错信息")
        win.geometry("680x380")
        frame=ttk.Frame(win,padding=14)
        frame.pack(fill="both",expand=True)
        text=tk.Text(frame,wrap="word",font=("Microsoft YaHei UI",10))
        text.pack(fill="both",expand=True)
        text.insert("1.0",error)
        text.configure(state="disabled")
        ttk.Button(frame,text="确认",command=root.destroy).pack(pady=(10,0))
    root.mainloop()
if __name__=="__main__":
    main()
