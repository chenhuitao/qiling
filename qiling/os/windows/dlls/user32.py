#!/usr/bin/env python3
# 
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
# Built on top of Unicorn emulator (www.unicorn-engine.org) 

import struct
from qiling.os.windows.fncc import *
from qiling.os.fncc import *
from qiling.os.windows.utils import *
from qiling.os.windows.const import *
from qiling.const import *

# INT_PTR DialogBoxParamA(
#   HINSTANCE hInstance,
#   LPCSTR    lpTemplateName,
#   HWND      hWndParent,
#   DLGPROC   lpDialogFunc,
#   LPARAM    dwInitParam
# );
@winapi(cc=STDCALL, params={
    "hInstance": HANDLE,
    "lpTemplateName": POINTER,
    "hWndParent": HANDLE,
    "lpDialogFunc": POINTER,
    "dwInitParam": POINTER
})
def hook_DialogBoxParamA(self, address, params):
    ret = 0
    return ret


# UINT GetDlgItemTextA(
# 	HWND  hDlg,
# 	int   nIDDlgItem,
# 	LPSTR lpString,
# 	int   cchMax
# );
@winapi(cc=STDCALL, params={
    "hDlg": HANDLE,
    "nIDDlgItem": INT,
    "lpString": POINTER,
    "cchMax": INT
})
def hook_GetDlgItemTextA(self, address, params):
    ret = 0
    hDlg = params["hDlg"]
    nIDDlgItem = params["nIDDlgItem"]
    lpString = params["lpString"]
    cchMax = params["cchMax"]

    self.ql.stdout.write(b"Input DlgItemText :\n")
    string = self.ql.stdin.readline().strip()[:cchMax]
    ret = len(string)
    self.ql.mem.write(lpString, string)

    return ret


# int MessageBoxA(
#     HWND   hWnd,
#     LPCSTR lpText,
#     LPCSTR lpCaption,
#     UINT   uType
#     );
@winapi(cc=STDCALL, params={
    "hWnd": HANDLE,
    "lpText": STRING,
    "lpCaption": STRING,
    "uType": UINT
})
def hook_MessageBoxA(self, address, params):
    ret = 2
    return ret


# BOOL EndDialog(
#   HWND    hDlg,
#   INT_PTR nResult
# );
@winapi(cc=STDCALL, params={
    "hDlg": HANDLE,
    "nResult": POINTER
})
def hook_EndDialog(self, address, params):
    ret = 1
    return ret


# HWND GetDesktopWindow((
# );
@winapi(cc=STDCALL, params={})
def hook_GetDesktopWindow(self, address, params):
    pass


# BOOL OpenClipboard(
#  HWND hWndNewOwner
# );
@winapi(cc=STDCALL, params={
    "hWndNewOwner": HANDLE
})
def hook_OpenClipboard(self, address, params):
    return self.clipboard.open(params['hWndNewOwner'])


# BOOL CloseClipboard();
@winapi(cc=STDCALL, params={})
def hook_CloseClipboard(self, address, params):
    return self.clipboard.close()


# HANDLE SetClipboardData(
#  UINT   uFormat,
#  HANDLE hMem
# );
@winapi(cc=STDCALL, params={
    "uFormat": UINT,
    "hMem": STRING
})
def hook_SetClipboardData(self, address, params):
    try:
        data = bytes(params['hMem'], 'ascii', 'ignore')
    except UnicodeEncodeError:
        data = b""
    return self.clipboard.set_data(params['uFormat'], data)


# HANDLE GetClipboardData(
#  UINT uFormat
# );
@winapi(cc=STDCALL, params={
    "uFormat": UINT
})
def hook_GetClipboardData(self, address, params):
    data = self.clipboard.get_data(params['uFormat'])
    if data:
        addr = self.ql.heap.mem_alloc(len(data))
        self.ql.mem.write(addr, data)
        return addr
    else:
        self.ql.dprint(D_PROT, 'Failed to get clipboard data')
        return 0


# BOOL IsClipboardFormatAvailable(
#  UINT format
# );
@winapi(cc=STDCALL, params={
    "uFormat": UINT
})
def hook_IsClipboardFormatAvailable(self, address, params):
    rtn = self.clipboard.format_available(params['uFormat'])
    return rtn


# UINT MapVirtualKeyW(
#   UINT uCode,
#   UINT uMapType
# );
@winapi(cc=STDCALL, params={
    "uCode": UINT,
    "uMapType": UINT
})
def hook_MapVirtualKeyW(self, address, params):
    map_value = params["uMapType"]
    code_value = params["uCode"]
    map_dict = MAP_VK.get(map_value, None)
    if map_dict is not None:
        code = map_dict.get(code_value, None)
        if code is not None:
            return code
        else:
            self.ql.dprint(D_PROT, "Code value %x" % info)
            raise QlErrorNotImplemented("[!] API not implemented")
    else:
        self.ql.dprint(D_PROT, "Map value %x" % info)
        raise QlErrorNotImplemented("[!] API not implemented")


# UINT RegisterWindowMessageA(
#   LPCSTR lpString
# );
@winapi(cc=STDCALL, params={
    "lpString": STRING
})
def hook_RegisterWindowMessageA(self, address, params):
    # maybe some samples really use this and we need to have a real implementation
    return 0xD10C


# UINT RegisterWindowMessageW(
#   LPCWSTR lpString
# );
@winapi(cc=STDCALL, params={
    "lpString": WSTRING
})
def hook_RegisterWindowMessageW(self, address, params):
    # maybe some samples really use this and we need to have a real implementation
    return 0xD10C


# HWND GetActiveWindow();
@winapi(cc=STDCALL, params={
})
def hook_GetActiveWindow(self, address, params):
    # maybe some samples really use this and we need to have a real implementation
    return 0xD10C


# HWND GetLastActivePopup(
#   HWND hWnd
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER
})
def hook_GetLastActivePopup(self, address, params):
    hwnd = params["hWnd"]
    return hwnd


# BOOL GetPhysicalCursorPos(
#   LPPOINT lpPoint
# );
@winapi(cc=STDCALL, params={
    "lpPoint": POINTER
})
def hook_GetPhysicalCursorPos(self, address, params):
    return 1


# int GetSystemMetrics(
#   int nIndex
# );
@winapi(cc=STDCALL, params={
    "nIndex": INT
})
def hook_GetSystemMetrics(self, address, params):
    info = params["nIndex"]
    if info == SM_CXICON or info == SM_CYICON:
        # Size of icon
        return 32
    elif info == SM_CXVSCROLL:
        return 4
    elif info == SM_CYHSCROLL:
        return 300
    else:
        self.ql.dprint(D_PROT, "Info value %x" % info)
        raise QlErrorNotImplemented("[!] API not implemented")


# HDC GetDC(
#   HWND hWnd
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER
})
def hook_GetDC(self, address, params):
    handler = params["hWnd"]
    # Maybe we should really emulate the handling of screens and windows. Is going to be a pain
    return 0xD10C


# int GetDeviceCaps(
#   HDC hdc,
#   int index
# );
@winapi(cc=STDCALL, params={
    "hdc": POINTER,
    "index": INT
})
def hook_GetDeviceCaps(self, address, params):
    # Maybe we should really emulate the handling of screens and windows. Is going to be a pain
    return 1


# int ReleaseDC(
#   HWND hWnd,
#   HDC  hDC
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER,
    "hdc": POINTER
})
def hook_ReleaseDC(self, address, params):
    return 1


# DWORD GetSysColor(
#   int nIndex
# );
@winapi(cc=STDCALL, params={
    "nIndex": INT
})
def hook_GetSysColor(self, address, params):
    info = params["nIndex"]
    return 0


# HBRUSH GetSysColorBrush(
#   int nIndex
# );
@winapi(cc=STDCALL, params={
    "nIndex": INT
})
def hook_GetSysColorBrush(self, address, params):
    info = params["nIndex"]
    return 0xd10c


# HCURSOR LoadCursorA(
#   HINSTANCE hInstance,
#   LPCSTR    lpCursorName
# );
@winapi(cc=STDCALL, params={
    "hInstance": POINTER,
    "lpCursorName": INT
})
def hook_LoadCursorA(self, address, params):
    return 0xd10c


# UINT GetOEMCP();
@winapi(cc=STDCALL, params={
})
def hook_GetOEMCP(self, address, params):
    return OEM_US


# int LoadStringA(
#   HINSTANCE hInstance,
#   UINT      uID,
#   LPSTR     lpBuffer,
#   int       cchBufferMax
# );
@winapi(cc=STDCALL, params={
    "hInstance": POINTER,
    "uID": UINT,
    "lpBuffer": POINTER,
    "cchBufferMax": INT
})
def hook_LoadStringA(self, address, params):
    dst = params["lpBuffer"]
    max_len = params["cchBufferMax"]
    string = "AAAABBBBCCCCDDDD" + "\x00"
    if max_len == 0:
        if len(string) >= max_len:
            string[max_len] = "\x00"
            string = string[:max_len]
        self.ql.mem.write(dst, string.encode("utf-16le"))
    # should not count the \x00 byte
    return len(string) - 1


# BOOL MessageBeep(
#   UINT uType
# );
@winapi(cc=STDCALL, params={
    "uType": UINT
})
def hook_MessageBeep(self, address, params):
    return 1


# HHOOK SetWindowsHookExA(
#   int       idHook,
#   HOOKPROC  lpfn,
#   HINSTANCE hmod,
#   DWORD     dwThreadId
# );
@winapi(cc=STDCALL, params={
    "idHook": INT,
    "lpfn": POINTER,
    "hmod": POINTER,
    "dwThreadId": DWORD
})
def hook_SetWindowsHookExA(self, address, params):
    # Should hook a procedure to a dll
    hook = params["lpfn"]
    return hook


# BOOL UnhookWindowsHookEx(
#   HHOOK hhk
# );
@winapi(cc=STDCALL, params={
    "hhk": POINTER,
})
def hook_UnhookWindowsHookEx(self, address, params):
    return 1


# BOOL ShowWindow(
#   HWND hWnd,
#   int  nCmdShow
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER,
    "nCmdShow": INT
})
def hook_ShowWindow(self, address, params):
    # return value depends on sample goal (evasion on just display error)
    return 0x1


# HICON LoadIconA(
#   HINSTANCE hInstance,
#   LPCSTR    lpIconName
# );
@winapi(cc=STDCALL, params={
    "hInstance": POINTER,
    "lpIconName": INT
})
def hook_LoadIconA(self, address, params):
    # we should create an handle for this?
    return 0xD10C


# BOOL IsWindow(
#   HWND hWnd
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER
})
def hook_IsWindow(self, address, params):
    # return value depends on sample  goal (evasion on just display error)
    return 0x1


# LRESULT SendMessageA(
#   HWND   hWnd,
#   UINT   Msg,
#   WPARAM wParam,
#   LPARAM lParam
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER,
    "Msg": UINT,
    "wParam": UINT,
    "lParam": UINT
})
def hook_SendMessageA(self, address, params):
    # TODO don't know how to get right return value
    return 0xD10C


# LRESULT LRESULT DefWindowProcA(
#   HWND   hWnd,
#   UINT   Msg,
#   WPARAM wParam,
#   LPARAM lParam
# );
@winapi(cc=STDCALL, params={
    "hWnd": POINTER,
    "Msg": UINT,
    "wParam": UINT,
    "lParam": UINT
})
def hook_DefWindowProcA(self, address, params):
    # TODO don't know how to get right return value
    return 0xD10C


# LPWSTR CharNextW(
#   LPCWSTR lpsz
# );
@winapi(cc=STDCALL, params={
    "lpsz": POINTER
})
def hook_CharNextW(self, address, params):
    # Return next char if is different from \x00
    point = params["lpsz"]
    string = read_wstring(self.ql, point)
    self.ql.dprint(D_PROT, string)
    if len(string) == 0:
        return point
    else:
        return point + 1


# LPWSTR CharPrevW(
#   LPCWSTR lpszStart,
#   LPCWSTR lpszCurrent
# );
@winapi(cc=STDCALL, params={
    "lpszStart": POINTER,
    "lpszCurrent": POINTER
})
def hook_CharPrevW(self, address, params):
    # Return next char if is different from \x00
    current = params["lpszCurrent"]
    start = params["lpszStart"]
    if start == current:
        return start
    return current - 1


# int WINAPIV wsprintfW(
#   LPWSTR  ,
#   LPCWSTR ,
#   ...
# );
@winapi(cc=CDECL, param_num=3)
def hook_wsprintfW(self, address, params):
    dst, p_format, p_args = get_function_param(self, 3)
    format_string = read_wstring(self.ql, p_format)
    size, string = printf(self, address, format_string, p_args, "wsprintfW", wstring=True)

    count = format_string.count('%')
    if self.ql.archtype== QL_X8664:
        # We must pop the stack correctly
        raise QlErrorNotImplemented("[!] API not implemented")

    self.ql.mem.write(dst, (string + "\x00").encode("utf-16le"))
    return size

# int WINAPIV sprintf(
#   LPWSTR  ,
#   LPCWSTR ,
#   ...
# );
@winapi(cc=CDECL, param_num=3)
def hook_sprintf(self, address, params):
    dst, p_format, p_args = get_function_param(self, 3)
    format_string = read_wstring(self.ql, p_format)
    size, string = printf(self, address, format_string, p_args, "sprintf", wstring=True)

    count = format_string.count('%')
    if self.ql.archtype== QL_X8664:
        # We must pop the stack correctly
        raise QlErrorNotImplemented("[!] API not implemented")

    self.ql.mem.write(dst, (string + "\x00").encode("utf-16le"))
    return size


# HWND GetForegroundWindow();
@winapi(cc=STDCALL, params={
})
def hook_GetForegroundWindow(self, address, params):
    return 0xF02E620D  # Value so we can recognize inside dumps
