# Viewer

A small, portable Windows image viewer built with Python and PySide6.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

Choose a folder with the folder button, paste a path into the header, or select a
saved favorite. Hold **Shift** and use the mouse wheel over a gallery to resize
the grid tiles.

## Build a portable executable

```powershell
.\build.ps1
```

The build script creates `.venv` automatically, installs the runtime and build
dependencies into it, and writes a single-file Windows executable into `dist`.
The generated `.exe` is meant to run on another Windows PC without installing
Python or the packages from `requirements.txt`.

To change the generated file name, edit `build.env` before building:

```text
APP_NAME=Wiever
APP_VERSION=1.0.0
```

With these values, the distributable application is written to
`dist/Wiever-1.0.0.exe`.
