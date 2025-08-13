# Installation
## Requirements
- `uv`. Installation instructions [here](https://docs.astral.sh/uv/getting-started/installation/).
- `ollama`
- (for pdf chunking and embedding) `poppler`. It should be available in your PATH. See below for instructions.
- (for pdf chunking and embedding) `tesseract`. It should be available in your PATH. See below for instructions.

### Poppler installation
On Debian Linux:
`sudo apt install poppler-utils`

On Windows:
1. Go to https://github.com/oschwartz10612/poppler-windows
2. Download the latest build from the releases
3. Extract the folder in wherever you want in your system.
4. Find the `bin` directory and add that to your PATH. Start Menu -> Edit the system environment variables -> Environment Variables... -> copy the location of the `bin` directory and paste it into the PATH variable.
5. Test installation by running some of the Poppler executables in a Command Prompt, such as `pdfunite`.

### Tesseract installation
On Debian Linux:
`sudo apt install tesseract-ocr`

On Windows:
1. Go to https://github.com/UB-Mannheim/tesseract/wiki
2. Download the installer.
3. Follow the installer instructions.
4. Add the `c/Program Files/Tesseract OCR/` folder to your PATH, as you did with the poppler installation above.
5. Test installation by openning a Command Prompt and running `tesseract`.

## Talensinki installation steps
1. Get the [latest release](https://github.com/Txart/talensinki/releases/latest) from the link or from the Releases page.
2. Unzip the downloaded folder in the desired location. Navigate to the directory.
3. Open the command line and run `ollama serve`.
3. Open another command line prompt and run `uv run talensinki-gui`. This will also install all the required packages, which might be quite a few as a fresh install.

It should work now!

# Deprecated Installation: docker
## Through the docker container
`docker compose build`

# Run the docker container
`docker compose up`


# Run the app
Run the GUI:
`uv run talensinki-gui`

Run the TUI:
`uv run talensinki`


