import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

SUPPORTED_SUFFIXES = {".txt", ".json", ".csv"}
ENC_MARKER_PATTERN = re.compile(r"ENC\[[^\]]+\]")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d{1,3}[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\w)")
SENSITIVE_ASSIGNMENT_PATTERN = re.compile(r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)\b\s*[:=]")


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def outgoing_dir() -> Path:
    return root_dir() / "outgoing"


def logs_dir() -> Path:
    return root_dir() / "logs"


def pid_file() -> Path:
    return root_dir() / "agent.pid"


def clawmatry_config_path() -> Path:
    return root_dir() / "clawmatry.config.json"


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle == 0:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def watcher_status() -> tuple[str, str]:
    if not pid_file().exists():
        return "Stopped", "No pid file"
    raw = pid_file().read_text(encoding="utf-8").strip()
    if not raw.isdigit():
        return "Stopped", "Invalid pid file"
    pid = int(raw)
    if _is_pid_running(pid):
        return "Running", f"PID {pid}"
    return "Stopped", f"Stale PID {pid}"


def tail_lines(path: Path, max_lines: int = 20) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-max_lines:]


def count_possible_plain_sensitive(text: str) -> int:
    plain_text = ENC_MARKER_PATTERN.sub("", text)
    count = 0
    count += len(EMAIL_PATTERN.findall(plain_text))
    count += len(PHONE_PATTERN.findall(plain_text))
    count += len(SENSITIVE_ASSIGNMENT_PATTERN.findall(plain_text))
    return count


def file_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base = outgoing_dir()
    if not base.exists():
        return rows

    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        enc_count = len(ENC_MARKER_PATTERN.findall(content))
        plain_sensitive = count_possible_plain_sensitive(content)
        rows.append(
            {
                "File": str(path.relative_to(base)),
                "Type": path.suffix.lower(),
                "Encrypted Markers": enc_count,
                "Possible Plain Sensitive": plain_sensitive,
                "Size (KB)": round(path.stat().st_size / 1024, 2),
                "Updated": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return rows


def config_status() -> dict[str, str]:
    cfg_path = clawmatry_config_path()
    if not cfg_path.exists():
        return {
            "Config": "Missing",
            "Upload URL": "Not set",
            "Token": "Not set",
        }
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "Config": "Invalid JSON",
            "Upload URL": "Unknown",
            "Token": "Unknown",
        }
    return {
        "Config": "Loaded",
        "Upload URL": "Set" if cfg.get("upload_url") else "Not set",
        "Token": "Set" if cfg.get("upload_token") else "Not set",
    }


def read_preview(relative_file: str, max_chars: int = 5000) -> str:
    target = outgoing_dir() / relative_file
    if not target.exists():
        return "File not found."
    text = target.read_text(encoding="utf-8", errors="ignore")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... (truncated)"
    return text


def render() -> None:
    st.set_page_config(page_title="Sensitive File Protection Dashboard", layout="wide")
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');
          html, body, [class*="css"] {font-family: 'Space Grotesk', sans-serif;}
          .hero {
            background: linear-gradient(120deg, #001219 0%, #005f73 48%, #94d2bd 100%);
            padding: 1rem 1.2rem;
            border-radius: 14px;
            color: #f0f8ff;
            margin-bottom: 0.8rem;
          }
          .hint {
            background: #f4f7f8;
            border-left: 4px solid #0a9396;
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            color: #1d3557;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero"><h2 style="margin:0;">Sensitive File Protection Dashboard</h2>'
        '<div style="margin-top:0.3rem;">Drop files in <b>outgoing</b>. Sensitive values are encrypted in-place.</div></div>',
        unsafe_allow_html=True,
    )

    status, status_detail = watcher_status()
    rows = file_rows()
    cfg = config_status()

    total_files = len(rows)
    total_markers = sum(int(r["Encrypted Markers"]) for r in rows)
    files_with_encryption = sum(1 for r in rows if int(r["Encrypted Markers"]) > 0)
    files_with_plain_sensitive = sum(1 for r in rows if int(r["Possible Plain Sensitive"]) > 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Watcher", status, status_detail)
    c2.metric("Files In Outgoing", total_files)
    c3.metric("Files With ENC", files_with_encryption)
    c4.metric("Possible Plain Sensitive", files_with_plain_sensitive)

    c5, c6 = st.columns(2)
    c5.metric("Total ENC Markers", total_markers)
    c6.metric("Clawmatry Config", cfg["Config"], f"URL: {cfg['Upload URL']} | Token: {cfg['Token']}")

    st.markdown(
        '<div class="hint">Presentation tip: show "Possible Plain Sensitive" as 0 after watcher runs, '
        'and "Files With ENC" increasing.</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Outgoing Files")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No supported files found yet in outgoing folder.")

    st.subheader("File Preview")
    if rows:
        options = [str(r["File"]) for r in rows]
        selected = st.selectbox("Choose a file", options=options, index=0)
        st.code(read_preview(selected), language="text")
    else:
        st.code("Drop a .txt/.json/.csv file into outgoing to preview it here.", language="text")

    st.subheader("Watcher Logs")
    out_lines = tail_lines(logs_dir() / "agent.out.log", max_lines=15)
    err_lines = tail_lines(logs_dir() / "agent.err.log", max_lines=15)

    lc1, lc2 = st.columns(2)
    with lc1:
        st.caption("Output log (latest 15)")
        st.code("\n".join(out_lines) if out_lines else "No output logs yet.", language="text")
    with lc2:
        st.caption("Error log (latest 15)")
        st.code("\n".join(err_lines) if err_lines else "No error logs.", language="text")

    st.button("Refresh Dashboard")


if __name__ == "__main__":
    render()
