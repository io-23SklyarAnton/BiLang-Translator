**Real-Time Subtitle Translator**

A lightweight, real-time screen translation overlay.

**Windows**

For Windows users, a standalone executable is available.

1. Download the latest `.exe` from the **Releases** page.
2. Double-click to run. No installation or external dependencies are required.

**macOS**

Due to Gatekeeper security restrictions and system library dependencies, it is recommended to run the application from the source code.

1. Install Tesseract and language packages via Homebrew:

```bash
brew install tesseract tesseract-lang

```

2. Clone this repository and navigate to the project folder.
3. Install the required Python dependencies:

```bash
pip install -r requirements.txt

```

4. Run the application:

```bash
python main.py

```

**Linux**

Linux users should run the application directly from the source.

1. Install Tesseract and language packages (Debian/Ubuntu example):

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-all

```

2. Clone this repository and navigate to the project folder.
3. Install the required Python dependencies:

```bash
pip install -r requirements.txt

```

4. Run the application:

```bash
python main.py

```

**How to Use**

* **Select Area:** Click the scissors icon and drag to select the region of the screen containing the text.
* **Select Languages:** Use the dropdown menus to set the source text language and the target translation language.
* **Move and Resize:** Drag the control bar to move the window. Drag the bottom-right corner to resize it.
* **Exit:** Click the 'X' button to close the application.
