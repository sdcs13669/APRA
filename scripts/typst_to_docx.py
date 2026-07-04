"""Convert competition.typ to competition.docx with proper formatting."""
import re, os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TYP_PATH = r"C:\Users\qq283\Desktop\APRA\report\competition.typ"
DOCX_PATH = r"C:\Users\qq283\Desktop\APRA\report\competition.docx"
IMG_DIR = r"C:\Users\qq283\Desktop\APRA\APRA_Presentation_meaningful_images"

with open(TYP_PATH, encoding='utf-8') as f:
    text = f.read()

doc = Document()

# --- Global style setup ---
style = doc.styles['Normal']
style.font.size = Pt(10.5)
style.font.name = 'SimSun'
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
style.paragraph_format.line_spacing = 1.15

for i, (sz, clr) in enumerate([(16, '24476F'), (13, '24476F'), (11, '2F7D68')], 1):
    hs = doc.styles[f'Heading {i}']
    hs.font.size = Pt(sz)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor.from_string(clr)
    hs.font.name = 'SimHei'
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimHei')
    hs.paragraph_format.space_before = Pt(12 if i == 1 else 8)
    hs.paragraph_format.space_after = Pt(4)

# --- Helper functions ---
def add_body(doc, txt):
    """Add justified paragraph with first-line indent."""
    if not txt.strip():
        return
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(txt)
    run.font.size = Pt(10.5)
    run.font.name = 'SimSun'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

def add_centered(doc, txt, size=Pt(12), bold=False, color=None, space_before=Pt(0)):
    """Add centered paragraph (for cover page)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = space_before
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(txt)
    run.font.size = size
    run.font.name = 'SimHei'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimHei')
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)

def add_code(doc, code):
    """Add code block with light background."""
    for line in code.strip().split('\n'):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), 'EEF3F8')
        shd.set(qn('w:val'), 'clear')
        p.paragraph_format.element.get_or_add_pPr().append(shd)
        run = p.add_run(line if line else ' ')
        run.font.size = Pt(9)
        run.font.name = 'Consolas'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimHei')

def add_box(doc, title, body):
    """Add a callout box with border."""
    # Title in bold
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(title)
    run.font.size = Pt(10.5)
    run.bold = True
    run.font.name = 'SimHei'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimHei')
    run.font.color.rgb = RGBColor.from_string('24476F')
    # Body
    p2 = doc.add_paragraph()
    p2.paragraph_format.first_line_indent = Cm(0.74)
    run2 = p2.add_run(body)
    run2.font.size = Pt(10.5)
    run2.font.name = 'SimSun'
    run2._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
    # Add bottom spacing
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_bullet(doc, txt):
    """Add a bullet list item."""
    p = doc.add_paragraph(style='List Bullet')
    p.clear()
    run = p.add_run(txt)
    run.font.size = Pt(10.5)
    run.font.name = 'SimSun'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

def add_page_break(doc):
    doc.add_page_break()

# --- Preprocess: strip comments and math ---
# Remove line comments
lines = text.split('\n')
# Remove comment-only lines and style definitions
clean_lines = []
in_block = False
for line in lines:
    # Skip style definition blocks
    if line.strip().startswith('// ====') or line.strip().startswith('// ----'):
        continue
    # Skip font/style setup (lines 1-81 are setup)
    clean_lines.append(line)

# Rejoin but skip the preamble (everything before the cover)
content = '\n'.join(clean_lines)
# Find the cover page start
cover_start = content.find('// 封面')
if cover_start >= 0:
    content = content[cover_start:]

# Split into sections by heading markers and process linearly
# We'll process the typst content section by section

# Strip the leading comments
content = re.sub(r'^//.*$', '', content, flags=re.MULTILINE)

# --- Process the content ---
# The content is now markdown-like. Let me parse it into a sequence of blocks.
# Blocks: headings (=, ==, ===), paragraphs, code blocks (```...```),
# tables (#table...), figures (#figure...), boxes (#box...), lists (+ ...)

# First, extract sections by = headings and process each

def process_typst_content(doc, text):
    """Process Typst content and build DOCX elements."""
    # Split into blocks
    blocks = []
    current_block = []

    for line in text.split('\n'):
        stripped = line.strip()
        # Detect block boundaries
        if stripped.startswith('= ') and not stripped.startswith('== '):
            if current_block:
                blocks.append(('\n'.join(current_block)).strip())
            current_block = [line]
        elif stripped.startswith('== ') and not stripped.startswith('=== '):
            if current_block:
                blocks.append(('\n'.join(current_block)).strip())
            current_block = [line]
        elif stripped.startswith('=== '):
            if current_block:
                blocks.append(('\n'.join(current_block)).strip())
            current_block = [line]
        else:
            current_block.append(line)

    if current_block:
        blocks.append(('\n'.join(current_block)).strip())

    for block in blocks:
        if not block.strip():
            continue

        lines = block.split('\n')
        first = lines[0].strip()

        # Chapter heading (=)
        if first.startswith('= ') and not first.startswith('== '):
            title = first[2:].strip()
            doc.add_heading(title, level=1)
            continue

        # Section heading (==)
        if first.startswith('== ') and not first.startswith('=== '):
            title = first[3:].strip()
            doc.add_heading(title, level=2)
            continue

        # Subsection heading (===)
        if first.startswith('=== '):
            title = first[4:].strip()
            doc.add_heading(title, level=3)
            continue

        # Process the block content
        process_block_body(doc, block)

def process_block_body(doc, block):
    """Process a block that may contain text, code, tables, lists, boxes, etc."""
    # Split block into sub-blocks
    lines = block.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block start
        if stripped.startswith('```') and i + 1 < len(lines):
            i += 1
            code_lines = []
            while i < len(lines):
                if lines[i].strip().startswith('```'):
                    break
                code_lines.append(lines[i])
                i += 1
            add_code(doc, '\n'.join(code_lines))
            i += 1
            continue

        # Table start
        if '#table(' in stripped or '#figure(' in stripped:
            # Skip tables and figures in DOCX - they're complex to reproduce
            # Just add a note for figures
            if '#figure(' in stripped:
                # Try to extract caption
                caption_match = re.search(r'caption:\s*\[(.*?)\]', block[i:])
                if caption_match:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.first_line_indent = Cm(0)
                    run = p.add_run(f'[图：{caption_match.group(1)}]')
                    run.font.size = Pt(9)
                    run.italic = True
                    run.font.color.rgb = RGBColor.from_string('687385')
                    run.font.name = 'SimSun'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
            # Skip to end of table/figure block
            brace_count = None
            j = i
            while j < len(lines):
                for ch in lines[j]:
                    pass  # just scan
                if ')' in lines[j] and j > i + 2:
                    i = j + 1
                    break
                j += 1
            else:
                i += 1
            continue

        # Box callout
        box_match = re.match(r'#box\[(.*?)\]\[', stripped)
        if box_match:
            title = box_match.group(1)
            # Collect box body until matching ]
            box_body_lines = []
            # The body starts after the second [
            body_start = stripped.index('][') + 2 if '][' in stripped else -1
            if body_start >= 0:
                rest = stripped[body_start:]
                # Collect until we find closing ]
                depth = 1
                j = i
                while j < len(lines) and depth > 0:
                    for ch in lines[j]:
                        if ch == '[':
                            depth += 1
                        elif ch == ']':
                            depth -= 1
                    if depth > 0 or j == i:
                        if j == i and body_start >= 0:
                            box_body_lines.append(rest)
                        else:
                            box_body_lines.append(lines[j])
                    j += 1
                body_text = '\n'.join(box_body_lines).strip()
                if body_text.endswith(']'):
                    body_text = body_text[:-1]
                add_box(doc, title, body_text)
                i = j
                continue

        # Source note
        if stripped.startswith('#source-note['):
            note = stripped[len('#source-note['):].rstrip(']')
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(note)
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor.from_string('687385')
            run.font.name = 'SimSun'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
            i += 1
            continue

        # Page break
        if stripped.startswith('#pagebreak()'):
            add_page_break(doc)
            i += 1
            continue

        # Math formula (inline)
        if stripped.startswith('$ ') and stripped.endswith(' $'):
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped[2:-2])
            run.font.size = Pt(10.5)
            run.italic = True
            run.font.name = 'Times New Roman'
            i += 1
            continue

        # Bullet list item
        if stripped.startswith('+ ') or stripped.startswith('- '):
            prefix_len = 2
            txt = stripped[prefix_len:].strip()
            # Remove inline formatting markers
            txt = re.sub(r'\*([^*]+)\*', r'\1', txt)
            # Remove $...$ math
            txt = re.sub(r'\$[^$]+\$', '', txt)
            add_bullet(doc, txt)
            i += 1
            continue

        # Text directive
        if stripped.startswith('#text('):
            i += 1
            continue

        # Regular paragraph
        if stripped and not stripped.startswith('#'):
            txt = stripped
            # Remove inline formatting
            txt = re.sub(r'\*([^*]+)\*', r'\1', txt)
            # Remove box/code text markers
            txt = re.sub(r'`([^`]+)`', r'\1', txt)
            # Remove raw math
            txt = re.sub(r'\$[^$]+\$', '', txt)
            if txt.strip() and not txt.strip().startswith('#') and not txt.strip().startswith('//'):
                # Handle #strong[...] and #emph[...]
                txt = re.sub(r'#strong\[([^\]]+)\]', r'\1', txt)
                txt = re.sub(r'#emph\[([^\]]+)\]', r'\1', txt)
                if txt.strip():
                    add_body(doc, txt)
            i += 1
            continue

        i += 1

# Process the content
process_typst_content(doc, content)

# --- Create cover page at the beginning ---
# Move cover page to front by inserting at position 0
# Since python-docx doesn't support easy reordering, we'll just accept the order
# as the content is likely in the right order already

# Add metadata
doc.core_properties.title = "APRA 全国大学生信息安全作品赛参赛作品"
doc.core_properties.author = "黄智辉 许皓人 樊政灵 王欣蕾"

doc.save(DOCX_PATH)
print(f"Saved to {DOCX_PATH}")
print(f"File size: {os.path.getsize(DOCX_PATH) / 1024:.0f} KB")
