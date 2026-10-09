# PulsePoint Sentiment Studio

A professional customer feedback dashboard with a **dark, high-contrast interface**, sentiment charts, a searchable feedback explorer, and detailed source-by-source analysis. It accepts any file type. Common text/document formats are extracted directly, and PNG/JPG screenshots are read with local OCR.

## Install and run on Windows

1. Download and extract `PulsePoint_Sentiment_Studio_Professional.zip` into a new folder.
2. In File Explorer, open that folder, click the address bar, type `powershell`, and press Enter. This opens PowerShell in the correct project folder. Run `dir` and confirm `app.py` and `requirements.txt` are listed.
3. Create an isolated Python environment:
   ```powershell
   python -m venv .venv
   ```
4. Install the project packages:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
5. Start PulsePoint:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```
6. Open the local address shown in the terminal, usually `http://localhost:8501`.

Do not run `python -m` by itself: `-m` must be followed by a module name. Do not run `pip install` by itself: provide `-r requirements.txt` to install this project's dependencies.

For macOS/Linux, create and activate `.venv`, install with `python -m pip install -r requirements.txt`, and start with `python -m streamlit run app.py`.

## Add a picture or document

Use the large **Add feedback files** box at the top of the dashboard. Click **Browse files** or drag files into the box. No file extension filter is applied. PNG, JPG, JPEG, WEBP, BMP, and TIFF images are scanned for text locally. Extracted text appears in the detailed analysis and feedback explorer. OCR runs once per image and is cached while the app is running.

Supported text extraction also includes TXT, MD, CSV, TSV, JSON, HTML, XML, YAML, EML, PDF, DOCX, PPTX, and XLSX. Audio, video, archives, and other binary formats can be attached and listed, but need transcription or a format-specific reader to analyze their contents.

## Read the detailed analysis

Open **Detailed analysis** after uploading a file. For each source it shows a short extractive summary, recurring terms and phrases, sentiment counts, strongest positive and negative evidence, dates or amounts found, and the exact extracted text in an expandable section. This is grounded in source text; it does not invent missing details. For an image, OCR summarizes the visible text. It does not identify objects or describe a scene that contains no readable text.

Use **Feedback explorer** to search and filter individual records. **Insights report** provides a downloadable Markdown report. You can also export analyzed rows to CSV. The sidebar's neutral-band slider changes classification sensitivity.

## Sentiment method and limits

The sentiment baseline uses an included English word lexicon. It adjusts for nearby negation and selected intensifiers, then normalizes by text length. It is deterministic and does not call an external API. It is strongest on short, direct English feedback; sarcasm, mixed opinions, slang, multilingual text, and specialist terms may be misclassified. Use results as directional signals and review original comments.

## Project contents

- `app.py` — dashboard, OCR, text extraction, detailed analysis, scoring, visualizations, and exports
- `.streamlit/config.toml` — dark application theme
- `requirements.txt` — Python packages, including OCR runtime
- `sample_feedback.csv` — fictional sample data
- `Insights_Report.md` — written sample analysis
- `SUBMISSION_GUIDE.md` — presentation checklist
- `LICENSE.txt` — license
