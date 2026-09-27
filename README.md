# Viewer

## Description

A small, portable Windows image viewer built with Python and PySide6.

Choose a folder with the folder button, paste a path into the header, or select a
saved favorite. Hold **Shift** and use the mouse wheel over a gallery to resize
the grid tiles.

## Installation

Install dependencies and run the application with `uv`:

```powershell
uv run python main.py
```

Alternatively, use Python's built-in virtual environment support:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

## Distribution

Build a portable Windows executable:

```powershell
.\build.ps1
```

The build script uses `uv` when it is available. If `uv` is not installed, it
falls back to creating `.venv` with Python. It installs the runtime and build
dependencies into the isolated environment and writes a single-file Windows
executable into `dist`.

To change the generated file name, edit `build.env` before building:

```text
APP_NAME=Wiever
APP_VERSION=1.0.0
```

With these values, the distributable application is written to
`dist/Wiever-1.0.0.exe`.
