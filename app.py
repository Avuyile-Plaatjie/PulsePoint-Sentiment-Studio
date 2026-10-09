import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime
from pathlib import Path
import csv, io, json, re, html, zipfile, email, time, math

st.set_page_config(page_title="PulsePoint | Sentiment Studio", page_icon="◉", layout="wide", initial_sidebar_state="expanded")

# Compact, transparent lexicon baseline: no API key or model download is needed.
POSITIVE = {"amazing":2.5,"awesome":2.5,"excellent":2.8,"fantastic":2.8,"great":2,"good":1.5,"love":2.5,"loved":2.5,"best":2.8,"wonderful":2.5,"happy":2,"helpful":1.8,"fast":1.2,"easy":1.5,"smooth":1.7,"recommend":2,"reliable":1.5,"perfect":2.5,"beautiful":1.7,"friendly":1.5,"clear":1,"thank":1.1,"thanks":1.1,"impressive":2,"enjoy":1.8,"enjoyed":1.8,"delightful":2.2,"value":1,"intuitive":1.5,"responsive":1.5,"solved":1.5,"works":0.7,"improved":1.2,"quick":1.2,"comfortable":1.3,"worth":0.8,"positive":1.3,"outstanding":2.7,"brilliant":2.5,"perfectly":2,"convenient":1.2,"professional":1.4}
NEGATIVE = {"bad":-1.7,"terrible":-2.8,"awful":-2.8,"hate":-2.5,"hated":-2.5,"poor":-1.8,"slow":-1.4,"broken":-2.2,"disappointing":-2.2,"disappointed":-2,"worst":-2.8,"hard":-1,"difficult":-1.2,"confusing":-1.7,"bug":-1.5,"bugs":-1.5,"issue":-1,"issues":-1,"problem":-1.3,"problems":-1.3,"fail":-1.8,"failed":-1.8,"failure":-2,"expensive":-1.3,"waste":-2,"unhelpful":-1.8,"rude":-2,"unreliable":-1.8,"late":-0.8,"missing":-1,"error":-1.2,"errors":-1.4,"refund":-1,"returned":-0.8,"unclear":-1,"frustrating":-2,"frustrated":-1.8,"unfortunately":-0.7,"never":-0.8,"wrong":-1.4,"crash":-2,"crashes":-2,"crashed":-2,"overpriced":-1.8,"annoying":-1.6,"poorly":-1.8,"negative":-1.2,"unusable":-2.2,"unresponsive":-1.8,"messy":-1,"complaint":-1.2}
NEGATORS={"not","no","never","hardly","isn't","wasn't","don't","didn't","can't","cannot","won't","without"}
INTENSIFIERS={"very":1.35,"really":1.3,"extremely":1.6,"absolutely":1.5,"so":1.2,"quite":1.15,"super":1.35}

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--ink:#f2f6fb;--muted:#b4c1d0;--line:#2a3b50;--teal:#35c4bd;--mint:#163c42;--coral:#ff927f;--gold:#f3bd61;--panel:#142235;--panel2:#192a40}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:#e8eef6}
.stApp{background:#0b1421;color:#e8eef6}
header[data-testid="stHeader"]{background:rgba(11,20,33,.96)}
.block-container{padding-top:1.8rem;padding-bottom:3rem;max-width:1440px}
[data-testid="stSidebar"]{background:#0e1b2b;color:#e8eef6;border-right:1px solid #22344a}
[data-testid="stSidebar"] *{color:#e8eef6}
.hero{padding:.7rem 0 1rem}.eyebrow{font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#54d6cc;font-size:.75rem}
.hero h1{font-family:Manrope,sans-serif;font-size:2.5rem;letter-spacing:-.05em;margin:.38rem 0;color:#f4f7fb}.hero p{color:#bdc9d6;margin:0;font-size:1.02rem}
.metric{background:#142235;border:1px solid #2a3b50;border-radius:16px;padding:18px 20px;min-height:116px;box-shadow:0 8px 28px rgba(0,0,0,.14)}
.metric-label{font-size:.78rem;color:#bac6d3;font-weight:600}.metric-value{font:800 1.8rem Manrope,sans-serif;letter-spacing:-.04em;color:#f5f8fc;margin-top:7px}.metric-note{font-size:.77rem;color:#a9b7c7;margin-top:2px}
.section-title{font:700 1.06rem Manrope,sans-serif;margin:1.1rem 0 .15rem;color:#f0f5fa}.section-sub{font-size:.85rem;color:#b0bdcb;margin:0 0 .8rem}
.pill{display:inline-block;padding:5px 10px;border-radius:99px;font-size:.72rem;font-weight:700;background:#163c42;color:#75e0d8}
.note{background:#15283d;border:1px solid #2b4057;border-radius:12px;padding:12px 15px;color:#d4dee8;font-size:.85rem}
[data-testid="stTabs"]{border-bottom:1px solid #2a3b50}[data-testid="stTabs"] button{font-weight:650;color:#c4cfdb}[data-testid="stTabs"] button[aria-selected="true"]{color:#62d8d0}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input{background:#142235!important;color:#f2f6fb!important;border:1px solid #334961!important;border-radius:10px!important}
[data-testid="stTextArea"] textarea::placeholder,[data-testid="stTextInput"] input::placeholder{color:#9eafbf!important;opacity:1}
[data-testid="stSelectbox"],[data-testid="stMultiSelect"]{color:#eef3f8}
[data-baseweb="select"]>div{background:#142235!important;border-color:#3a5067!important;color:#f2f6fb!important}
[data-testid="stFileUploader"]{background:#122237;border:1px solid #314962;border-radius:15px;padding:10px}
[data-testid="stFileUploaderDropzone"]{background:#172a40!important;border:1px dashed #6b879d!important;border-radius:11px!important}
[data-testid="stFileUploaderDropzone"] *{color:#edf4fa!important;fill:#edf4fa!important}
[data-testid="stFileUploaderDropzone"] button{background:#087f8c!important;border:0!important;color:white!important;border-radius:9px!important;font-weight:700!important}
[data-testid="stFileUploaderDropzone"] button *{color:white!important}
[data-testid="stFileUploaderFile"]{background:#1a2c41!important;border:1px solid #40566c!important;border-radius:9px!important;color:#f3f6fa!important}
.stButton button,.stDownloadButton button{border-radius:10px;font-weight:650;background:#087f8c;color:white;border:1px solid #1a9da0}
.stButton button:hover,.stDownloadButton button:hover{background:#0997a0;color:white;border-color:#4bd2ca}
[data-testid="stDataFrame"]{border:1px solid #30445a;border-radius:12px;overflow:hidden}
[data-testid="stExpander"]{background:#132238;border:1px solid #2c4056;border-radius:12px}
[data-testid="stAlert"]{background:#182a40;color:#f0f5fa}
[data-testid="stCaptionContainer"]{color:#a9b8c8}
hr{border-color:#2a3b50!important}
footer{visibility:hidden}
</style>""", unsafe_allow_html=True)


def score_text(text, threshold=0.12):
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?|[!?]+", str(text).lower())
    score = 0.0; hits=[]; words=[t for t in tokens if re.fullmatch(r"[a-z]+(?:'[a-z]+)?",t)]
    for i,w in enumerate(words):
        val=POSITIVE.get(w,NEGATIVE.get(w,0))
        if not val: continue
        prior=words[max(0,i-3):i]
        if any(p in NEGATORS for p in prior): val *= -0.75
        for p in prior[-2:]:
            if p in INTENSIFIERS: val *= INTENSIFIERS[p]
        score += val
        hits.append((w,val))
    if "!" in str(text): score *= 1.08
    norm = score / max(1, len(words) ** 0.5)
    label = "Positive" if norm > threshold else "Negative" if norm < -threshold else "Neutral"
    return label, round(max(-1,min(1,norm/2.3)),3), [w for w,v in hits if v>0], [w for w,v in hits if v<0]


def json_text(obj):
    chunks=[]
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if isinstance(v,(str,int,float,bool)) and str(v).strip(): chunks.append(f"{k}: {v}")
                else: walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
        elif isinstance(x,(str,int,float)) and str(x).strip(): chunks.append(str(x))
    walk(obj); return "\n".join(chunks)


@st.cache_resource(show_spinner=False)
def get_ocr_engine():
    from rapidocr import RapidOCR
    return RapidOCR()


@st.cache_data(show_spinner=False)
def ocr_image(data):
    """Extract readable text from a screenshot using a locally running OCR engine."""
    from PIL import Image
    import numpy as np
    image=Image.open(io.BytesIO(data)).convert("RGB")
    # Bound OCR work for large phone screenshots while keeping text legible.
    image.thumbnail((2200,2200),Image.Resampling.LANCZOS)
    # RapidOCR expects an image array; convert the Pillow RGB buffer to OpenCV-style BGR.
    result=get_ocr_engine()(np.asarray(image)[:, :, ::-1].copy())
    if not result: return ""
    lines=getattr(result,"txts",None) or []
    return "\n".join(str(line).strip() for line in lines if str(line).strip())


def extract_file(name, data):
    ext=Path(name).suffix.lower()
    try:
        if ext in {".png",".jpg",".jpeg",".webp",".bmp",".tif",".tiff"}:
            started=time.perf_counter()
            extracted=ocr_image(data)
            elapsed=time.perf_counter()-started
            if extracted.strip(): return extracted, f"Screenshot text extracted with local OCR ({elapsed:.1f}s)"
            return "", f"Image scanned with local OCR ({elapsed:.1f}s); no readable text found"
        if ext in {".txt",".md",".log",".csv",".tsv",".json",".html",".htm",".xml",".yaml",".yml",".eml",".rst",".srt",".vtt"}:
            raw=data.decode("utf-8-sig",errors="replace")
            if ext==".json": return json_text(json.loads(raw)), "Text extracted from JSON fields"
            if ext in {".html",".htm",".xml"}: return html.unescape(re.sub(r"<[^>]+>"," ",raw)), "Markup text extracted"
            if ext==".eml":
                msg=email.message_from_string(raw); body=[]
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type()=="text/plain": body.append(part.get_payload(decode=True).decode(errors="replace"))
                else: body=[raw]
                return "\n".join(body), "Email body extracted"
            return raw, "Text content extracted"
        if ext==".pdf":
            from pypdf import PdfReader
            reader=PdfReader(io.BytesIO(data)); return "\n".join(p.extract_text() or "" for p in reader.pages), f"Text extracted from {len(reader.pages)} PDF pages"
        if ext==".docx":
            from docx import Document
            doc=Document(io.BytesIO(data)); return "\n".join(p.text for p in doc.paragraphs), "Word document paragraphs extracted"
        if ext==".pptx":
            from pptx import Presentation
            prs=Presentation(io.BytesIO(data)); chunks=[]
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape,"text"): chunks.append(shape.text)
            return "\n".join(chunks), f"Text extracted from {len(prs.slides)} slides"
        if ext in {".xlsx",".xls"}:
            book=pd.ExcelFile(io.BytesIO(data)); chunks=[]
            for sheet in book.sheet_names:
                frame=pd.read_excel(book,sheet_name=sheet).fillna("")
                chunks.extend(frame.astype(str).agg(" | ".join,axis=1).tolist())
            return "\n".join(chunks), f"Text extracted from {len(book.sheet_names)} spreadsheet sheets"
        if ext==".doc": return "", "Legacy .doc is attached; save as .docx or .txt to analyze its contents"
    except ImportError as e: return "", f"OCR reader unavailable ({e.name}); run python -m pip install -r requirements.txt and retry"
    except Exception as e: return "", f"Could not extract text ({type(e).__name__}: {e})"
    return "", f"Attachment accepted ({ext or 'unknown type'}); text extraction is not configured for this format"


def normalize_uploaded(name,data):
    raw, note=extract_file(name,data)
    ext=Path(name).suffix.lower()
    if ext in {".csv",".tsv"} and raw.strip():
        try:
            frame=pd.read_csv(io.BytesIO(data),sep="\t" if ext==".tsv" else None,engine="python")
            # One row is one observation. If there are multiple columns, use the selected/text-like column.
            return frame, note
        except Exception: pass
    if not raw.strip(): return pd.DataFrame(columns=["text","source"]), note
    # One sentence / paragraph / line per observation; retain long lines as complete records.
    bits=[re.sub(r"\s+"," ",x).strip() for x in re.split(r"\n+",raw) if x.strip()]
    if len(bits)==1 and len(bits[0])>550: bits=re.split(r"(?<=[.!?])\s+",bits[0])
    return pd.DataFrame({"text":bits,"source":name}), note


SUMMARY_STOPWORDS=set("a an and are as at be been being but by can could did do does for from had has have he her hers him his how i if in into is it its just may me might my no not of on or our ours she should so than that the their them then there these they this those through to too was we were what when where which who will with would you your yours about after again against all also any because before between both each few further here once only other over same some such very while your".split())


def summarize_content(text, limit=4):
    sentences=[re.sub(r"\s+"," ",part).strip(" \t-•") for part in re.split(r"(?<=[.!?])\s+|\n+",text) if len(part.strip())>18]
    words=re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}",text.lower())
    useful=[w for w in words if w not in SUMMARY_STOPWORDS]
    freq=Counter(useful)
    ranked=[]
    for pos,sentence in enumerate(sentences):
        ws=[w for w in re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}",sentence.lower()) if w not in SUMMARY_STOPWORDS]
        if not ws: continue
        score=sum(math.log1p(freq[w]) for w in ws)/math.sqrt(len(ws))
        ranked.append((score,pos,sentence))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    picked=[]; seen=set()
    for _,_,sentence in ranked:
        normalized=sentence.casefold()
        if normalized in seen: continue
        picked.append(sentence); seen.add(normalized)
        if len(picked)>=limit: break
    if not picked and sentences: picked=sentences[:min(limit,len(sentences))]
    bigrams=Counter((a,b) for a,b in zip(useful,useful[1:]) if a not in SUMMARY_STOPWORDS and b not in SUMMARY_STOPWORDS and a!=b)
    return picked,freq.most_common(8),bigrams.most_common(5)


def detailed_content_report(df):
    """Build a source-by-source, evidence-based explanation of extracted content."""
    if df.empty: return "No readable text was available to summarize."
    lines=["## Detailed content analysis", "", "This summary is based on text extracted from each attachment. Sentences and quoted evidence come directly from the source; key terms are frequency signals, not generated facts."]
    for source,group in df.groupby("source",sort=False,dropna=False):
        source=str(source or "Uploaded content")
        text="\n".join(group["text"].astype(str).tolist())
        summary,keywords,bigrams=summarize_content(text)
        counts=group["sentiment"].value_counts(); total=len(group)
        image=Path(source).suffix.lower() in {".png",".jpg",".jpeg",".webp",".bmp",".tif",".tiff"}
        lines += ["",f"### {source}","",f"**Content read:** {'Image text (OCR)' if image else 'Document or text'} · **{total} text segment(s)** · **Sentiment:** {int(counts.get('Positive',0))} positive, {int(counts.get('Neutral',0))} neutral, {int(counts.get('Negative',0))} negative.",""]
        lines.append("**Summary**")
        if summary: lines.extend([f"- {sentence[:500]}" for sentence in summary])
        else: lines.append("- Text was extracted, but there was not enough readable content to form a sentence summary.")
        if keywords:
            lines += ["", "**Most repeated content terms:** " + ", ".join(f"{w} ({n})" for w,n in keywords[:8]) + "."]
        if bigrams:
            lines += ["", "**Repeated phrase pairs:** " + ", ".join(f"{a} {b} ({n})" for (a,b),n in bigrams if n>1) + ("." if any(n>1 for _,n in bigrams) else "No phrase pairs repeated more than once.")]
        evidence=group.sort_values("score")
        if int(counts.get("Negative",0)):
            row=evidence.iloc[0]
            lines += ["",f"**Strongest negative evidence ({row.score:+.3f}):** “{str(row.text)[:300]}”"]
        if int(counts.get("Positive",0)):
            row=group.sort_values("score",ascending=False).iloc[0]
            lines += ["",f"**Strongest positive evidence ({row.score:+.3f}):** “{str(row.text)[:300]}”"]
        # Surface dates, amounts and percentages present in the extracted text.
        details=[]
        details += re.findall(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",text)
        details += re.findall(r"(?:[$€£]\s?\d[\d,]*(?:\.\d{1,2})?|\b\d+(?:\.\d+)?%)",text)
        details=list(dict.fromkeys(details))[:12]
        if details: lines += ["", "**Dates, amounts, or percentages found:** " + ", ".join(details) + "."]
        lines += ["",f"<details><summary>View all extracted text for {source}</summary>","",text[:12000],"", "</details>"]
        if image:
            lines += ["","> Image note: this analysis describes the text recognized in the image. It does not identify objects or visual scenes that contain no readable text."]
    return "\n".join(lines)


def render_report(df, source_names):
    counts=df["sentiment"].value_counts()
    n=len(df); pos=int(counts.get("Positive",0)); neg=int(counts.get("Negative",0)); neu=int(counts.get("Neutral",0))
    avg=float(df["score"].mean()) if n else 0
    def pct(x): return f"{x/n:.0%}" if n else "0%"
    pos_terms=Counter(w for arr in df["positive_terms"] for w in arr)
    neg_terms=Counter(w for arr in df["negative_terms"] for w in arr)
    top_pos=", ".join(f"{w} ({c})" for w,c in pos_terms.most_common(5)) or "No positive lexicon matches"
    top_neg=", ".join(f"{w} ({c})" for w,c in neg_terms.most_common(5)) or "No negative lexicon matches"
    lines=["# Feedback Analysis Report", "", f"**Generated:** {datetime.now().strftime('%d %B %Y, %H:%M')}  ", f"**Files:** {', '.join(source_names) if source_names else 'Manual text input'}  ", "**Analysis engine:** PulsePoint transparent lexicon baseline", "", f"PulsePoint analyzed **{n:,} text segments**. Mean normalized sentiment score: **{avg:+.3f}** (−1 is more negative; +1 is more positive). **{pos} positive ({pct(pos)})**, **{neu} neutral ({pct(neu)})**, and **{neg} negative ({pct(neg)})** segments.", "", detailed_content_report(df), "", "## Sentiment signals", "", f"- Positive share: **{pct(pos)}**; negative share: **{pct(neg)}**.", f"- Most frequent positive signals: {top_pos}.", f"- Most frequent negative signals: {top_neg}."]
    if neg:
        examples=df[df.sentiment=="Negative"].sort_values("score").head(3)
        lines += ["", "## Items to review", "", "Read these negative examples in their original context:"]
        lines += [f"- “{str(r.text)[:260]}” (score {r.score:+.3f})" for r in examples.itertuples()]
    lines += ["", "## Method and limitations", "", "Document and image summaries are extractive: they select and organize text found in the source. Image text comes from OCR. Visual objects or scenes without text are not identified. Sentiment uses a built-in English word lexicon with nearby negation and selected intensifier adjustments. This baseline does not understand sarcasm, domain context, multilingual text, or subtle mixed opinions. Review important results against the original file.", "", "---", "*PulsePoint Sentiment Studio · Feedback analysis*"]
    return "\n".join(lines)


with st.sidebar:
    st.markdown("<div style='font:800 1.12rem Manrope,sans-serif;letter-spacing:-.03em;margin:.1rem 0 1.6rem'>◉ &nbsp;PULSEPOINT <span style='color:#8fa5b3;font-weight:500;font-size:.68rem'>STUDIO</span></div>",unsafe_allow_html=True)
    st.markdown("### Analysis settings")
    threshold=st.slider("Neutral band",0.05,0.50,0.12,0.01,help="Higher values classify more borderline records as neutral.")
    st.caption("Scoring runs locally in this app. Uploaded data is not sent to an external API.")
    st.markdown("---")
    st.caption("PULSEPOINT · INSIGHT WITH CONTEXT")

st.markdown("<div class='hero'><div class='eyebrow'>CUSTOMER VOICE · SENTIMENT ANALYTICS</div><h1>Hear the feeling behind the feedback.</h1><p>Get source-by-source summaries, key evidence, and a clear picture of how people feel.</p></div>",unsafe_allow_html=True)
uploads=st.file_uploader("Add feedback files",accept_multiple_files=True,help="All file types are accepted. PNG/JPG images are read with OCR; text is extracted from TXT, CSV, TSV, JSON, HTML, PDF, DOCX, PPTX and XLSX.")
st.caption("Drop files here or browse. Documents are summarized from their text; pictures are read with OCR, so image summaries focus on visible words.")

if "manual_text" not in st.session_state: st.session_state.manual_text=""
manual=st.text_area("Or paste feedback here",key="manual_text",height=95,placeholder="Paste a review, survey answer, email excerpt or any text…")
frames=[]; notes=[]; source_names=[]
if uploads:
    for file in uploads:
        data=file.getvalue(); source_names.append(file.name)
        frame,note=normalize_uploaded(file.name,data); notes.append((file.name,note,len(data)))
        if not frame.empty:
            frame=frame.copy()
            if "text" not in frame.columns:
                candidates=[c for c in frame.columns if any(k in str(c).lower() for k in ("text","review","comment","feedback","message","response","content"))]
                chosen=candidates[0] if candidates else frame.select_dtypes(include="object").columns[0] if len(frame.select_dtypes(include="object").columns) else frame.columns[0]
                frame=frame.rename(columns={chosen:"text"})
            frame=frame[["text"]].copy(); frame["source"]=file.name; frames.append(frame)
if manual.strip():
    frames.append(pd.DataFrame({"text":[x.strip() for x in re.split(r"\n+",manual) if x.strip()],"source":"Pasted text"})); source_names.append("Pasted text")

if frames:
    rawdf=pd.concat(frames,ignore_index=True)
    rawdf["text"]=rawdf["text"].fillna("").astype(str).str.strip()
    rawdf=rawdf[rawdf.text!=""].reset_index(drop=True)
else: rawdf=pd.DataFrame(columns=["text","source"])
if not rawdf.empty:
    result=rawdf["text"].apply(lambda t:score_text(t,threshold))
    rawdf["sentiment"]=[x[0] for x in result]; rawdf["score"]=[x[1] for x in result]; rawdf["positive_terms"]=[x[2] for x in result]; rawdf["negative_terms"]=[x[3] for x in result]

if notes:
    with st.expander(f"Attachment handling · {len(notes)} file(s)",expanded=any(n.startswith("Attachment accepted") or n.startswith("Could not") or n.startswith("Optional") or "no readable text" in n.lower() for _,n,_ in notes)):
        for name,note,size in notes: st.write(f"**{name}** · {size:,} bytes — {note}")

if rawdf.empty:
    st.markdown("<div class='note'>Add a file or paste feedback above to start. The dashboard updates as soon as readable text is available.</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Designed for real-world feedback</div><div class='section-sub'>Flexible inputs · clear sentiment signals · shareable insights</div>",unsafe_allow_html=True)
    a,b,c=st.columns(3)
    for col,icon,title,desc in [(a,"↗","Spot the signal","See sentiment mix, average score and the language shaping the conversation."),(b,"⌕","Find what needs attention","Surface negative comments quickly and explore the terms behind them."),(c,"⇩","Share the story","Download a clean insights report and row-level results for your next review.")]:
        with col: st.markdown(f"<div class='metric'><div style='font-size:1.25rem;color:#087f8c'>{icon}</div><div class='section-title'>{title}</div><div class='section-sub' style='margin:4px 0 0'>{desc}</div></div>",unsafe_allow_html=True)
else:
    n=len(rawdf); c=rawdf.sentiment.value_counts(); pos=int(c.get("Positive",0)); neu=int(c.get("Neutral",0)); neg=int(c.get("Negative",0)); avg=rawdf.score.mean()
    st.markdown("<div class='section-title'>Your sentiment snapshot</div><div class='section-sub'>A high-level read across the loaded feedback.</div>",unsafe_allow_html=True)
    cols=st.columns(4)
    metrics=[("TEXT RECORDS",f"{n:,}",f"Across {len(set(rawdf.source))} source(s)"),("POSITIVE",f"{pos/n:.0%}",f"{pos:,} records"),("NEUTRAL",f"{neu/n:.0%}",f"{neu:,} records"),("NEGATIVE",f"{neg/n:.0%}",f"{neg:,} records")]
    for col,(label,val,note) in zip(cols,metrics):
        with col: st.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-note'>{note}</div></div>",unsafe_allow_html=True)
    left,right=st.columns([1,1.25],gap="large")
    with left:
        st.markdown("<div class='section-title'>Sentiment mix</div><div class='section-sub'>Share of feedback in each category</div>",unsafe_allow_html=True)
        order=["Positive","Neutral","Negative"]; donut=pd.DataFrame({"Sentiment":order,"Records":[pos,neu,neg]})
        fig=px.pie(donut,names="Sentiment",values="Records",hole=.70,color="Sentiment",color_discrete_map={"Positive":"#087f8c","Neutral":"#b9c8d3","Negative":"#ed765e"})
        fig.update_traces(textinfo="none",hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",marker_line_color="white",marker_line_width=3)
        fig.update_layout(showlegend=True,legend=dict(orientation="h",y=-.08,x=.1,font=dict(color="#d8e2ec")),margin=dict(l=4,r=4,t=5,b=20),height=270,paper_bgcolor="rgba(0,0,0,0)",annotations=[dict(text=f"{n:,}<br><span style='font-size:11px;color:#aab8c7'>records</span>",x=.5,y=.5,font=dict(size=24,color="#f2f6fb",family="Manrope"),showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown(f"<div class='note'>Average sentiment score &nbsp; <b>{avg:+.3f}</b> &nbsp; · &nbsp; −1 more negative &nbsp;to&nbsp; +1 more positive</div>",unsafe_allow_html=True)
    with right:
        st.markdown("<div class='section-title'>Sentiment landscape</div><div class='section-sub'>Distribution of normalized scores by record</div>",unsafe_allow_html=True)
        fig2=px.histogram(rawdf,x="score",color="sentiment",nbins=22,barmode="overlay",opacity=.82,color_discrete_map={"Positive":"#087f8c","Neutral":"#b9c8d3","Negative":"#ed765e"},category_orders={"sentiment":["Positive","Neutral","Negative"]})
        fig2.add_vline(x=0,line_color="#8292a1",line_dash="dot",line_width=1)
        fig2.update_layout(height=310,margin=dict(l=4,r=4,t=8,b=4),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#142235",xaxis_title="Sentiment score",yaxis_title="Records",legend_title="",font_color="#d4dee8",bargap=.07)
        fig2.update_xaxes(showgrid=False,zeroline=False,tickfont_color="#bcc9d6",title_font_color="#e6edf4"); fig2.update_yaxes(gridcolor="#304258",zeroline=False,tickfont_color="#bcc9d6",title_font_color="#e6edf4")
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
    st.markdown("<div class='section-title'>What people are saying</div><div class='section-sub'>The terms that most often carry sentiment in this dataset</div>",unsafe_allow_html=True)
    terms_l,terms_r=st.columns(2)
    pc=Counter(w for arr in rawdf.positive_terms for w in arr); nc=Counter(w for arr in rawdf.negative_terms for w in arr)
    with terms_l:
        st.markdown("<span class='pill'>POSITIVE SIGNALS</span>",unsafe_allow_html=True)
        st.write("　".join(f"**{w}** · {k}" for w,k in pc.most_common(8)) or "No positive lexicon matches found.")
    with terms_r:
        st.markdown("<span style='background:#fff0ed;color:#c45a45' class='pill'>AREAS TO REVIEW</span>",unsafe_allow_html=True)
        st.write("　".join(f"**{w}** · {k}" for w,k in nc.most_common(8)) or "No negative lexicon matches found.")
    tab1,tab2,tab3,tab4=st.tabs(["Detailed analysis","Feedback explorer","Insights report","Methodology"])
    with tab1:
        st.markdown("### What each file contains")
        st.markdown("A source-by-source summary, repeated topics, sentiment evidence, and extracted dates or amounts where found.")
        st.markdown(detailed_content_report(rawdf))
    with tab2:
        f1,f2=st.columns([1,2]);
        with f1: sentiment_filter=st.multiselect("Filter sentiment",["Positive","Neutral","Negative"],default=["Positive","Neutral","Negative"])
        with f2: query=st.text_input("Search feedback",placeholder="Search for a phrase or keyword…")
        view=rawdf[rawdf.sentiment.isin(sentiment_filter)]
        if query.strip(): view=view[view.text.str.contains(query,case=False,regex=False)]
        show=view[["source","sentiment","score","text"]].copy(); show.columns=["Source","Sentiment","Score","Feedback"]
        st.dataframe(show,use_container_width=True,hide_index=True,height=360)
        st.download_button("Download analyzed records · CSV",data=show.to_csv(index=False).encode("utf-8-sig"),file_name="pulsepoint_analyzed_feedback.csv",mime="text/csv")
    with tab3:
        report=render_report(rawdf,source_names)
        st.markdown(report)
        st.download_button("Download insights report · Markdown",data=report.encode("utf-8"),file_name="pulsepoint_insights_report.md",mime="text/markdown")
    with tab4:
        st.markdown("### A practical, transparent baseline")
        st.markdown("PulsePoint uses a compact built-in English word lexicon. Positive and negative word weights are summed, adjusted for nearby negation (for example, *not good*) and selected intensifiers (for example, *very good*), then normalized by text length. The default neutral band keeps weak or mixed signals from being overstated.")
        st.markdown("### Interpretation guardrails")
        st.markdown("This is an educational, rule-based project, not a trained language model. It is strongest on short, direct English statements. Sarcasm, slang, multilingual text, domain jargon, and nuanced context can lead to mistakes. Review examples before using the results to make decisions about people or services.")
        st.markdown("### File handling")
        st.markdown("All file types can be attached. Built-in readers cover common text and office formats. Screenshots and other common images are read with local OCR. The detailed summary organizes extracted text and evidence; it does not invent visual details. Audio, video, archives, and other binary formats need transcription or a format-specific reader before their contents can be analyzed.")

st.markdown("<div style='border-top:1px solid #2a3b50;margin-top:2rem;padding-top:12px;color:#a9b8c8;font-size:.74rem'>PULSEPOINT SENTIMENT STUDIO &nbsp;·&nbsp; BUILT FOR EXPLORATION, GROUNDED IN TRANSPARENCY</div>",unsafe_allow_html=True)

