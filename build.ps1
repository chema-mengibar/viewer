$ErrorActionPreference = "Stop"

$Config = @{
    APP_NAME = "Wiever"
    APP_VERSION = "1.0.0"
}

if (Test-Path "build.env") {
    Get-Content "build.env" | ForEach-Object {
        $Line = $_.Trim()
        if (-not $Line -or $Line.StartsWith("#")) {
            return
        }

        $Parts = $Line.Split("=", 2)
        if ($Parts.Count -eq 2) {
            $Config[$Parts[0].Trim()] = $Parts[1].Trim()
        }
    }
}

$DistName = "$($Config.APP_NAME)-$($Config.APP_VERSION)"
$IconData = "$(Resolve-Path "assets");assets"
$VenvPython = Join-Path ".venv" "Scripts\python.exe"

if (Get-Command "uv" -ErrorAction SilentlyContinue) {
    uv sync --extra build
    uv run pyinstaller --noconfirm --clean --onefile --windowed --name $DistName --specpath build --add-data $IconData main.py
} else {
    if (-not (Test-Path $VenvPython)) {
        python -m venv .venv
    }

    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r requirements-build.txt
    & $VenvPython -m PyInstaller --noconfirm --clean --onefile --windowed --name $DistName --specpath build --add-data $IconData main.py
}

if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}
