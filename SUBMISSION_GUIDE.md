# Submission Guide — PulsePoint Sentiment Studio

## Included

The ZIP contains the runnable dashboard, dark high-contrast theme, screenshot OCR, document text extraction, detailed source analysis, sample data, setup guide, and sample insights report.

## Suggested demonstration

1. Launch the dashboard using the PowerShell commands in `README.md`.
2. Upload `sample_feedback.csv` using **Add feedback files**.
3. Review the sentiment snapshot and score distribution.
4. Open **Detailed analysis** to show the source summary, repeated terms, example evidence, and full extracted text.
5. Upload a PNG/JPG containing readable feedback or a document such as PDF/DOCX. Show how the extracted content is organized and summarized.
6. Open **Insights report** and download the generated Markdown report.
7. Explain that summaries are extractive and grounded in source text. Image analysis reads visible text; it does not identify non-text objects or scenes.

## Project description

> PulsePoint Sentiment Studio is a local-first dashboard that accepts arbitrary attachments, extracts text from common documents and screenshots, and analyzes customer feedback with an explainable rule-based sentiment baseline. It provides a high-contrast interface, detailed source-by-source summaries with supporting evidence, interactive visualizations, a searchable feedback explorer, CSV exports, and a downloadable insights report.

## File support

The uploader accepts files of any extension. PNG/JPG and other common image formats are processed by local OCR. Common text and office formats have direct readers. Other binary formats remain attachable and are listed, but need transcription or a format-specific reader before their content can be analyzed.
