# Viewer

A small, portable Windows image viewer built with Python and PySide6.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

Choose a folder with the folder button, paste a path into the header, or select a
saved favorite. Hold **Shift** and use the mouse wheel over a gallery to resize
the grid tiles.

## Build a portable executable

```powershell
./build.ps1
```

To change the generated file name, edit `build.env` before building:

```text
APP_NAME=Wiever
APP_VERSION=1.0.0
```

With these values, the distributable application is written to
`dist/Wiever-1.0.0.exe`.
