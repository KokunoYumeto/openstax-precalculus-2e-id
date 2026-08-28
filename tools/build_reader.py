#!/usr/bin/env python3
"""Build a centered, full-width, reflowed A4 reader from translated CNXML."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from xml.etree import ElementTree as ET

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, ByteStringObject
from reportlab.pdfgen import canvas


PACKET = Path(__file__).resolve().parents[1]
MODULES = (
    "m49386", "m49387", "m49389", "m49390", "m49392", "m49393",
    "m49395", "m49396", "m49397", "m49398", "m49399",
)
SOURCE_ORDERS = dict(zip(MODULES, range(38, 49)))
MATHML = "http://www.w3.org/1998/Math/MathML"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
HTML_OUT = PACKET / "preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.html"
PDF_OUT = PACKET / "preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.pdf"
TMP = PACKET / "tmp/pdfs"
RAW_PDF = TMP / "HP-A30-003_raw.pdf"
PROFILE = TMP / "edge-profile"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(tag: object) -> str:
    if tag is ET.Comment or not isinstance(tag, str):
        return "#comment"
    return tag.rsplit("}", 1)[-1]


def esc(value: str | None) -> str:
    return html.escape(value or "", quote=False)


def attrs(element: ET.Element) -> str:
    value = element.attrib.get("id")
    return f' id="{html.escape(value, quote=True)}"' if value else ""


def math_markup(element: ET.Element) -> str:
    def serialize(node: ET.Element) -> str:
        tag = local(node.tag)
        rendered_attrs = "".join(
            f' {local(key)}="{html.escape(value, quote=True)}"'
            for key, value in sorted(node.attrib.items())
        )
        namespace = ' xmlns="http://www.w3.org/1998/Math/MathML"' if tag == "math" else ""
        body = esc(node.text)
        for child in list(node):
            body += serialize(child) + esc(child.tail)
        return f"<{tag}{namespace}{rendered_attrs}>{body}</{tag}>"

    return serialize(element)


def inner(element: ET.Element, depth: int = 0) -> str:
    result = esc(element.text)
    for child in list(element):
        result += render(child, depth) + esc(child.tail)
    return result


def render_image(element: ET.Element, alt_override: str | None = None) -> str:
    filename = Path(element.attrib.get("src", "")).name
    alt = alt_override or element.attrib.get("alt") or filename
    return (
        f'<img src="../translated/media/{html.escape(filename, quote=True)}" '
        f'alt="{html.escape(alt, quote=True)}" loading="eager">'
    )


def render(element: ET.Element, depth: int = 0) -> str:
    name = local(element.tag)
    if name == "#comment":
        return ""
    if isinstance(element.tag, str) and element.tag.startswith("{" + MATHML + "}"):
        return math_markup(element)
    if name in {"content-id", "uuid"}:
        return ""
    if name == "title":
        level = min(max(depth + 1, 2), 5)
        return f"<h{level}{attrs(element)}>{inner(element, depth)}</h{level}>"
    if name == "metadata":
        return "".join(
            f'<aside class="learning"><h2>Tujuan Pembelajaran</h2>{inner(child, depth + 1)}</aside>'
            for child in list(element) if local(child.tag) == "abstract"
        )
    if name in {"abstract", "content", "tgroup", "tbody", "thead", "glossary", "meaning"}:
        return inner(element, depth)
    if name == "section":
        children = list(element)
        title = next((child for child in children if local(child.tag) == "title"), None)
        body = esc(element.text)
        for child in children:
            if child is title:
                body += esc(child.tail)
            else:
                body += render(child, depth + 1) + esc(child.tail)
        heading = render(title, depth + 1) if title is not None else ""
        return f'<section class="section depth-{depth}"{attrs(element)}>{heading}{body}</section>'
    if name == "para":
        return f"<p{attrs(element)}>{inner(element, depth)}</p>"
    if name == "emphasis":
        tag = "strong" if element.attrib.get("effect") == "bold" else "em"
        return f"<{tag}{attrs(element)}>{inner(element, depth)}</{tag}>"
    if name == "term":
        return f"<dfn{attrs(element)}>{inner(element, depth)}</dfn>"
    if name == "span":
        return f"<span{attrs(element)}>{inner(element, depth)}</span>"
    if name == "sup":
        return f"<sup>{inner(element, depth)}</sup>"
    if name == "newline":
        return "<br>"
    if name == "equation":
        return f'<div class="equation"{attrs(element)}>{inner(element, depth)}</div>'
    if name == "figure":
        return f"<figure{attrs(element)}>{inner(element, depth)}</figure>"
    if name == "media":
        body = esc(element.text)
        for child in list(element):
            if local(child.tag) == "image":
                body += render_image(child, element.attrib.get("alt"))
            else:
                body += render(child, depth)
            body += esc(child.tail)
        return f'<div class="media"{attrs(element)}>{body}</div>'
    if name == "image":
        return render_image(element)
    if name == "caption":
        return f"<figcaption>{inner(element, depth)}</figcaption>"
    if name == "note":
        return f'<aside class="note"{attrs(element)}>{inner(element, depth + 1)}</aside>'
    if name == "example":
        return f'<article class="example"{attrs(element)}>{inner(element, depth + 1)}</article>'
    if name == "exercise":
        return f'<article class="exercise"{attrs(element)}>{inner(element, depth + 1)}</article>'
    if name == "problem":
        return f'<div class="problem">{inner(element, depth)}</div>'
    if name == "solution":
        return f'<div class="solution"><div class="solution-label">Penyelesaian</div>{inner(element, depth)}</div>'
    if name == "commentary":
        return f'<div class="commentary">{inner(element, depth)}</div>'
    if name == "list":
        tag = "ol" if element.attrib.get("list-type") in {"enumerated", "ordered"} else "ul"
        return f"<{tag}{attrs(element)}>{inner(element, depth)}</{tag}>"
    if name == "item":
        return f"<li{attrs(element)}>{inner(element, depth)}</li>"
    if name == "table":
        summary = element.attrib.get("summary", "")
        summary_attr = f' aria-label="{html.escape(summary, quote=True)}"' if summary and summary != ".." else ""
        return f'<div class="table-wrap"><table{attrs(element)}{summary_attr}>{inner(element, depth)}</table></div>'
    if name == "row":
        return f"<tr>{inner(element, depth)}</tr>"
    if name == "entry":
        span = ""
        if element.attrib.get("namest") and element.attrib.get("nameend"):
            start = int(re.sub(r"\D", "", element.attrib["namest"]) or "1")
            end = int(re.sub(r"\D", "", element.attrib["nameend"]) or str(start))
            span = f' colspan="{max(1, end - start + 1)}"'
        return f"<td{span}>{inner(element, depth)}</td>"
    if name == "colspec":
        return ""
    if name == "definition":
        return f'<div class="definition"{attrs(element)}>{inner(element, depth + 1)}</div>'
    if name == "label":
        return f'<div class="label">{inner(element, depth)}</div>'
    if name == "link":
        target = element.attrib.get("url")
        if not target and element.attrib.get("target-id"):
            target = "#" + element.attrib["target-id"]
        if not target and element.attrib.get("document"):
            target = "#module-" + element.attrib["document"]
        label = inner(element, depth).strip() or "rujukan"
        return f'<a href="{html.escape(target or "#", quote=True)}">{label}</a>'
    return inner(element, depth)


def parse(path: Path) -> ET.Element:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.fromstring(path.read_bytes(), parser=parser)


def module_html(module: str) -> tuple[str, str]:
    root = parse(PACKET / f"translated/modules/{module}/index.cnxml")
    title_element = next(child for child in list(root) if local(child.tag) == "title")
    title = "".join(title_element.itertext()).strip()
    body = ""
    for child in list(root):
        if child is title_element:
            body += esc(child.tail)
        else:
            body += render(child, 1) + esc(child.tail)
    chapter = "Bab 6" if SOURCE_ORDERS[module] <= 41 else "Bab 7"
    markup = f"""
    <article class="module" id="module-{module}">
      <header class="module-header">
        <div class="eyebrow">{chapter} · Urutan sumber {SOURCE_ORDERS[module]} · {module}</div>
        <h1>{html.escape(title)}</h1>
      </header>{body}
    </article>"""
    return title, markup


CSS = r"""
@page { size: A4; margin: 17mm 15mm 19mm 15mm; }
* { box-sizing: border-box; }
html { color: #162033; background: #fff; }
body { margin: 0; width: 100%; font-family: "Aptos", "Segoe UI", Arial, sans-serif; font-size: 10.2pt; line-height: 1.46; text-rendering: optimizeLegibility; }
.cover { min-height: 245mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }
.cover .kicker, .eyebrow { color: #146a78; text-transform: uppercase; letter-spacing: .09em; font-weight: 700; font-size: 8.2pt; }
.cover h1 { font-size: 30pt; line-height: 1.08; margin: 5mm 0 4mm; color: #0c4050; }
.cover h2 { font-size: 16pt; font-weight: 500; color: #34505a; margin: 0 0 12mm; }
.cover .scope { max-width: 155mm; border-left: 4px solid #ef9f32; padding: 4mm 0 4mm 6mm; font-size: 11pt; }
.cover .meta { margin-top: 14mm; color: #53616a; font-size: 9.2pt; }
.toc { page-break-after: always; }
.toc h1 { color: #0c4050; font-size: 23pt; }
.toc ol { margin: 0; padding: 0; list-style: none; counter-reset: toc; }
.toc li { counter-increment: toc; display: grid; grid-template-columns: 10mm 1fr 22mm; gap: 2mm; border-bottom: 1px solid #dce5e8; padding: 2.7mm 0; }
.toc li::before { content: counter(toc, decimal-leading-zero); color: #146a78; font-weight: 700; }
.toc a { color: #162033; text-decoration: none; }
.toc .module-id { color: #6c7880; text-align: right; font-size: 8.5pt; }
.module { page-break-before: always; width: 100%; }
.module-header { border-bottom: 2px solid #146a78; margin-bottom: 7mm; padding-bottom: 4mm; }
.module-header h1 { font-size: 24pt; line-height: 1.12; color: #0c4050; margin: 2mm 0 0; }
h2 { color: #0c4050; font-size: 17pt; line-height: 1.2; margin: 8mm 0 3mm; break-after: avoid; }
h3 { color: #146a78; font-size: 13pt; line-height: 1.25; margin: 6mm 0 2.5mm; break-after: avoid; }
h4, h5 { color: #233f47; font-size: 11.2pt; margin: 5mm 0 2mm; break-after: avoid; }
p { margin: 0 0 3.3mm; text-align: justify; orphans: 3; widows: 3; }
a { color: #0d6678; text-decoration: none; }
dfn { font-style: normal; font-weight: 650; color: #0b5361; }
.learning, .note, .definition { background: #eef7f7; border-left: 3px solid #2393a3; padding: 3.5mm 4mm; margin: 4mm 0; break-inside: avoid-page; }
.learning h2 { font-size: 12.5pt; margin: 0 0 2mm; }
.example { border: 1px solid #cad8dc; border-radius: 2mm; padding: 3.8mm 4mm; margin: 5mm 0; }
.example > .label, .note > .label { color: #146a78; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; font-size: 8.5pt; margin-bottom: 1.5mm; }
.exercise { border-left: 2px solid #ef9f32; padding-left: 4mm; margin: 3.2mm 0; }
.problem { margin-bottom: 2mm; }
.solution { background: #f6f7f8; border: 1px solid #d9dde0; padding: 3mm 3.5mm; margin: 2.5mm 0 4mm; }
.solution-label { color: #4b5960; font-size: 8.2pt; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 1.5mm; }
.commentary { border-left: 2px solid #aeb9bf; padding-left: 3mm; color: #3b474d; }
ul, ol { margin: 1.5mm 0 3.5mm 6mm; padding-left: 5mm; }
li { margin: 1mm 0; }
.equation { display: block; text-align: center; margin: 3.5mm auto; break-inside: avoid; overflow: visible; }
math { font-family: "Cambria Math", "STIX Two Math", serif; font-size: 1.02em; }
.equation math { font-size: 1.08em; }
figure { margin: 5mm auto; text-align: center; break-inside: avoid-page; max-width: 100%; }
.media { width: 100%; text-align: center; }
img { display: block; width: auto; height: auto; max-width: 100%; max-height: 205mm; object-fit: contain; margin: 0 auto; }
figcaption { max-width: 165mm; margin: 2mm auto 0; color: #53616a; font-size: 8.5pt; line-height: 1.35; text-align: left; }
.table-wrap { width: 100%; margin: 4mm 0; overflow: visible; }
table { border-collapse: collapse; width: 100%; max-width: 100%; font-size: 8.4pt; line-height: 1.25; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
td, th { border: 0.35pt solid #91a1a8; padding: 1.3mm 1.5mm; vertical-align: top; text-align: center; }
.provenance { page-break-before: always; color: #3d4b52; }
.provenance h1 { color: #0c4050; }
.provenance code { font-family: "Cascadia Mono", Consolas, monospace; font-size: 8.5pt; word-break: break-all; }
"""


def build_html() -> None:
    entries: list[tuple[str, str]] = []
    modules: list[str] = []
    for module in MODULES:
        title, markup = module_html(module)
        entries.append((module, title))
        modules.append(markup)
    toc = "\n".join(
        f'<li><a href="#module-{module}">{html.escape(title)}</a><span class="module-id">{module}</span></li>'
        for module, title in entries
    )
    document = f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><title>Precalculus 2e - Bab 6-7 - Bahasa Indonesia</title><style>{CSS}</style></head>
<body>
<section class="cover">
  <div class="kicker">OpenStax Precalculus 2e · Edisi Bahasa Indonesia</div>
  <h1>Fungsi Periodik, Identitas, dan Persamaan Trigonometri</h1>
  <h2>Bab 6-7 · Paket pembantu HP-A30-003</h2>
  <div class="scope">Terjemahan lengkap dan berurutan untuk modul sumber 38-48. Struktur semantik, matematika, ID, rujukan silang, latihan, penyelesaian, dan aset sumber dipertahankan.</div>
  <div class="meta">Sumber dibekukan pada commit <code>789b54099106b071d1d32bfcee454fed72eb4768</code>. Bantuan penerjemahan dan pelokalan: OpenAI Codex gpt-5.6-sol, Ultra. Lisensi: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).</div>
</section>
<nav class="toc"><h1>Daftar Isi</h1><ol>{toc}</ol></nav>
{''.join(modules)}
<section class="provenance">
  <h1>Catatan Provenans</h1>
  <p>Karya terpilih: <em>OpenStax Precalculus 2e</em>. Otoritas sumber: repositori <code>openstax/osbooks-college-algebra-bundle</code>, branch <code>main</code>, commit <code>789b54099106b071d1d32bfcee454fed72eb4768</code>, tree <code>05b39123f698772482c0c33a43fa2d2d4ea562ae</code>.</p>
  <p><em>OpenStax Precalculus 2e</em> dan adaptasi terjemahan ini dilisensikan berdasarkan <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)</a>. Akses buku sumber secara gratis di <a href="https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions">https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions</a>. Semua kredit sumber, kontributor, dan aset yang hadir dalam materi dipertahankan; keterangan gambar dapat memuat ketentuan khusus komponennya sendiri.</p>
</section>
</body></html>"""
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(document, encoding="utf-8", newline="\n")


def wait_for_stable(path: Path, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    last = -1
    stable = 0
    while time.time() < deadline:
        if path.is_file():
            size = path.stat().st_size
            if size > 0 and size == last:
                stable += 1
                if stable >= 3:
                    return
            else:
                stable = 0
                last = size
        time.sleep(0.5)
    raise RuntimeError(f"PDF did not stabilize: {path}")


def print_raw_pdf() -> None:
    if not EDGE.is_file():
        raise RuntimeError(f"Edge executable unavailable: {EDGE}")
    TMP.mkdir(parents=True, exist_ok=True)
    if RAW_PDF.exists():
        RAW_PDF.unlink()
    if PROFILE.exists():
        shutil.rmtree(PROFILE)
    command = [
        str(EDGE), "--headless=new", "--disable-gpu", "--disable-extensions",
        "--run-all-compositor-stages-before-draw", "--no-pdf-header-footer",
        f"--user-data-dir={PROFILE}", f"--print-to-pdf={RAW_PDF}", HTML_OUT.resolve().as_uri(),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=300)
    if completed.returncode != 0:
        raise RuntimeError(f"Edge PDF build failed: {completed.stderr[-1000:]}")
    wait_for_stable(RAW_PDF)


def add_headers_and_page_numbers() -> dict[str, object]:
    source = PdfReader(str(RAW_PDF))
    writer = PdfWriter()
    for page_number, page in enumerate(source.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay_path = TMP / f"overlay-{page_number:04d}.pdf"
        overlay = canvas.Canvas(str(overlay_path), pagesize=(width, height), invariant=1, pageCompression=1)
        overlay.setFillColorRGB(0.28, 0.34, 0.37)
        overlay.setFont("Helvetica", 5.6)
        overlay.drawString(42, height - 23, "Access for free at https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions")
        overlay.drawRightString(width - 42, 20, str(page_number))
        overlay.save()
        page.merge_page(PdfReader(str(overlay_path)).pages[0], over=True)
        writer.add_page(page)
        overlay_path.unlink()
    writer.add_metadata({
        "/Title": "OpenStax Precalculus 2e - Bab 6-7 - Bahasa Indonesia",
        "/Subject": "HP-A30-003 reflowed helper reader",
        "/Author": "OpenStax source; Indonesian localization assistance by OpenAI Codex gpt-5.6-sol, Ultra",
        "/Creator": "HP-A30-003 deterministic reader workflow",
        "/Producer": "pypdf",
        "/CreationDate": "D:20260828000000Z",
        "/ModDate": "D:20260828000000Z",
    })
    fixed_id = hashlib.sha256(b"HP-A30-003 reader v1").digest()[:16]
    writer._ID = ArrayObject([ByteStringObject(fixed_id), ByteStringObject(fixed_id)])
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    with PDF_OUT.open("wb") as stream:
        writer.write(stream)
    reopened = PdfReader(str(PDF_OUT))
    if len(reopened.pages) != len(source.pages):
        raise RuntimeError("final reader page count differs from raw print")
    return {"pages": len(reopened.pages), "bytes": PDF_OUT.stat().st_size, "sha256": sha256(PDF_OUT)}


def main() -> None:
    build_html()
    print_raw_pdf()
    pdf_result = add_headers_and_page_numbers()
    result = {
        "schema_id": "hp-a30-003-reader-build-v1",
        "status": "PASS",
        "pages": pdf_result["pages"],
        "html": {"path": HTML_OUT.relative_to(PACKET).as_posix(), "bytes": HTML_OUT.stat().st_size, "sha256": sha256(HTML_OUT)},
        "pdf": {"path": PDF_OUT.relative_to(PACKET).as_posix(), "bytes": pdf_result["bytes"], "sha256": pdf_result["sha256"]},
        "renderer": str(EDGE),
        "layout": "A4 reflow, 15 mm side margins, centered responsive figures and tables, page header/footer",
    }
    receipt = PACKET / "qa/READER_BUILD.json"
    receipt.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    if RAW_PDF.exists():
        RAW_PDF.unlink()
    if PROFILE.exists():
        shutil.rmtree(PROFILE)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
