"""Folder permissions on a shared Windows PC (DEC-024, SEC-005).

- create_private_folder() creates a new folder that only the current user, SYSTEM and Administrators
  can open.
- check_shared_folders() reads the access lists of the AgentDesk folder and the data folder and logs one
  warning for each folder that other Windows accounts on this PC can change.

AgentDesk only reads permissions: it never changes the permissions of an existing folder. Accounts are
compared by their well-known security identifiers (SIDs) only; no account name is read or stored
(DEC-009). Everything uses the Python standard library (ctypes), and no program is run.
"""

import ctypes
import functools
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

README_SECTION = '"Keep AgentDesk private on a shared PC" in README.md'

# Groups that include every other account on the PC, by well-known SID.
BROAD_SIDS = {
    "S-1-1-0": "Everyone",
    "S-1-5-11": "Authenticated Users",
    "S-1-5-32-545": "Users",
}

# Access rights that let someone create, change or delete files in a folder, or change its permissions.
WRITE_ACCESS = (
    0x00000002  # FILE_WRITE_DATA (create files)
    | 0x00000004  # FILE_APPEND_DATA (create subfolders)
    | 0x00000010  # FILE_WRITE_EA
    | 0x00000040  # FILE_DELETE_CHILD
    | 0x00000100  # FILE_WRITE_ATTRIBUTES
    | 0x00010000  # DELETE
    | 0x00040000  # WRITE_DAC (change permissions)
    | 0x00080000  # WRITE_OWNER
    | 0x10000000  # GENERIC_ALL
    | 0x40000000  # GENERIC_WRITE
)

_SE_FILE_OBJECT = 1
_DACL_SECURITY_INFORMATION = 0x4
_SE_DACL_PROTECTED = 0x1000
_ACCESS_ALLOWED_ACE_TYPE = 0
_ACCESS_DENIED_ACE_TYPE = 1
_INHERIT_ONLY_ACE = 0x08


class _ACL(ctypes.Structure):
    _fields_ = [
        ("AclRevision", ctypes.c_ubyte),
        ("Sbz1", ctypes.c_ubyte),
        ("AclSize", ctypes.c_ushort),
        ("AceCount", ctypes.c_ushort),
        ("Sbz2", ctypes.c_ushort),
    ]


class _ACE(ctypes.Structure):
    """ACCESS_ALLOWED_ACE and ACCESS_DENIED_ACE share this layout; the SID starts at SidStart."""

    _fields_ = [
        ("AceType", ctypes.c_ubyte),
        ("AceFlags", ctypes.c_ubyte),
        ("AceSize", ctypes.c_ushort),
        ("Mask", ctypes.c_uint32),
        ("SidStart", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class AccessEntry:
    sid: str  # for example "S-1-5-11"
    allowed: bool  # True for an allow entry, False for a deny entry
    mask: int  # the access rights
    inherit_only: bool  # applies only to the files and folders inside, not to the folder itself


@dataclass(frozen=True)
class FolderAccess:
    protected: bool  # the folder does not inherit permissions from its parent folder
    entries: list[AccessEntry] | None  # None: no access list at all, which gives everyone full access


def create_private_folder(path: Path) -> bool:
    """Create the folder if it does not exist yet, so that only the current user, SYSTEM and
    Administrators can open it. Missing parent folders are created normally. Returns True if the
    folder was created.

    os.mkdir with mode 0o700 gives this protected access list on Windows with Python 3.13 or newer;
    with Python 3.12 the folder inherits its parent's permissions, and the startup check warns.
    Raises OSError if the folder cannot be created, for example because a file is in the way.
    """
    path = Path(path)
    if path.is_dir():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkdir(path, 0o700)
    except FileExistsError:
        if path.is_dir():  # created by another process meanwhile
            return False
        raise
    return True


@functools.cache
def _windows_api():
    """The four Windows security functions used here, with their argument types."""
    from ctypes import wintypes

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    void_pp = ctypes.POINTER(ctypes.c_void_p)

    get_info = advapi32.GetNamedSecurityInfoW
    get_info.argtypes = [wintypes.LPCWSTR, ctypes.c_int, wintypes.DWORD, void_pp, void_pp, void_pp, void_pp, void_pp]
    get_info.restype = wintypes.DWORD
    get_control = advapi32.GetSecurityDescriptorControl
    get_control.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.WORD), ctypes.POINTER(wintypes.DWORD)]
    get_control.restype = wintypes.BOOL
    get_ace = advapi32.GetAce
    get_ace.argtypes = [ctypes.c_void_p, wintypes.DWORD, void_pp]
    get_ace.restype = wintypes.BOOL
    sid_to_text = advapi32.ConvertSidToStringSidW
    sid_to_text.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
    sid_to_text.restype = wintypes.BOOL
    local_free = kernel32.LocalFree
    local_free.argtypes = [ctypes.c_void_p]
    local_free.restype = ctypes.c_void_p
    return get_info, get_control, get_ace, sid_to_text, local_free


def _check(succeeded) -> None:
    if not succeeded:
        raise ctypes.WinError(ctypes.get_last_error())


def read_folder_access(path: Path) -> FolderAccess:
    """Read a folder's access list through the Windows security API. Raises OSError on failure."""
    if sys.platform != "win32":
        raise OSError("folder permissions can only be read on Windows")
    from ctypes import wintypes

    get_info, get_control, get_ace, sid_to_text, local_free = _windows_api()
    dacl = ctypes.c_void_p()
    descriptor = ctypes.c_void_p()
    error = get_info(
        str(path), _SE_FILE_OBJECT, _DACL_SECURITY_INFORMATION,
        None, None, ctypes.byref(dacl), None, ctypes.byref(descriptor),
    )
    if error:
        raise ctypes.WinError(error)
    try:
        control = wintypes.WORD()
        revision = wintypes.DWORD()
        _check(get_control(descriptor, ctypes.byref(control), ctypes.byref(revision)))
        protected = bool(control.value & _SE_DACL_PROTECTED)
        if not dacl.value:
            return FolderAccess(protected=protected, entries=None)

        entries = []
        for index in range(_ACL.from_address(dacl.value).AceCount):
            ace_address = ctypes.c_void_p()
            _check(get_ace(dacl, index, ctypes.byref(ace_address)))
            ace = _ACE.from_address(ace_address.value)
            if ace.AceType not in (_ACCESS_ALLOWED_ACE_TYPE, _ACCESS_DENIED_ACE_TYPE):
                continue  # other entry types (audit, object, callback) have another layout
            text = wintypes.LPWSTR()
            _check(sid_to_text(ctypes.c_void_p(ace_address.value + _ACE.SidStart.offset), ctypes.byref(text)))
            try:
                sid = text.value
            finally:
                local_free(ctypes.cast(text, ctypes.c_void_p))
            entries.append(AccessEntry(
                sid=sid,
                allowed=ace.AceType == _ACCESS_ALLOWED_ACE_TYPE,
                mask=ace.Mask,
                inherit_only=bool(ace.AceFlags & _INHERIT_ONLY_ACE),
            ))
        return FolderAccess(protected=protected, entries=entries)
    finally:
        local_free(descriptor)


def broad_write_sids(path: Path) -> list[str]:
    """The SIDs among Everyone, Authenticated Users and Users that an allow entry gives write-type
    access to the folder or to the files inside it."""
    access = read_folder_access(path)
    if access.entries is None:
        return ["S-1-1-0"]
    found = []
    for entry in access.entries:
        if entry.allowed and entry.sid in BROAD_SIDS and entry.mask & WRITE_ACCESS and entry.sid not in found:
            found.append(entry.sid)
    return found


def check_shared_folders(folders: list[tuple[str, Path]]) -> list[Path]:
    """Log one WARNING for each folder that other Windows accounts on this PC can change. Read-only.

    folders: (label, path) pairs, for example ("AgentDesk folder", REPO_ROOT). Returns the folders
    warned about. If the permissions cannot be read, one INFO line says so and the check stops:
    it never stops AgentDesk from starting.
    """
    if sys.platform != "win32":
        return []
    warned = []
    for label, path in folders:
        try:
            sids = broad_write_sids(path)
        except Exception as exc:  # best effort only: a failing check must never stop startup
            logger.info("The folder permissions could not be checked (%s: %s); AgentDesk continues.", label, exc)
            return warned
        if sids:
            groups = ", ".join(BROAD_SIDS[sid] for sid in sids)
            logger.warning(
                "Other Windows accounts on this PC can change files in the %s %s (write access for: %s). "
                "If other people use this PC, see %s. AgentDesk never changes folder permissions itself.",
                label, path, groups, README_SECTION,
            )
            warned.append(path)
    return warned
