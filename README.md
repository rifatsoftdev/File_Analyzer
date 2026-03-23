# File Analyzer Pro

**File Analyzer Pro** is a desktop application built with **Python + Tkinter** that scans a folder and generates a clear, structured file analysis report.

It is designed for fast local analysis and one-click export to **TXT** and **PDF**.

## Features

- Recursive folder analysis
- File and folder summary:
  - Total folders
  - Total files
  - Text files vs media files
  - Hidden files
  - Files without extension
  - Empty text files
- Line statistics:
  - Total lines in text files
  - File count per extension
  - Line count per extension
  - Average lines per extension
  - Longest text file detection
- Export report as:
  - `.txt`
  - `.pdf`
- Save dialogs default to the user's **Documents** folder
- Light/Dark mode toggle
- Branded header logo and app icon support

## Tech Stack

- Python 3
- Tkinter (GUI)
- `fpdf2` (PDF export)

## Project Structure

```text
File_Detals/
├── main.py
├── logo.png
├── logo.ico
└── setup.py
```

## Getting Started

### 1) Clone the repository

```bash
git clone <your-repo-url>
cd File_Detals
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install fpdf2
```

### 4) Run the app

```bash
python main.py
```

## Build a Standalone Executable (PyInstaller)

### Linux / macOS

```bash
pyinstaller --clean --noconfirm --windowed --onefile \
  --name FileAnalyzerPro \
  --icon logo.ico \
  --add-data="logo.png:." \
  --add-data="logo.ico:." \
  main.py
```

### Windows

```powershell
pyinstaller --clean --noconfirm --windowed --onefile `
  --name FileAnalyzerPro `
  --icon logo.ico `
  --add-data "logo.png;." `
  --add-data "logo.ico;." `
  main.py
```

Build output:

- Linux/macOS: `dist/FileAnalyzerPro`
- Windows: `dist\\FileAnalyzerPro.exe`

## Usage

1. Launch the app.
2. Click **Browse** and select a folder.
3. Click **Analyze Folder**.
4. Export with:
   - **Save as Text File**
   - **Save as PDF**

## Troubleshooting

- If PDF export fails on a target machine, install common Unicode fonts (for broader character coverage).
- If logo/icon does not appear in packaged builds, rebuild with `--clean` and ensure both `logo.png` and `logo.ico` are included using `--add-data`.
- Standalone binaries can be large because Python runtime and dependencies are bundled by design.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

## License

No license file is currently included. Add a `LICENSE` file before distributing publicly.
