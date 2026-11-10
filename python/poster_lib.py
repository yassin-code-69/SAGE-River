"""Helpers to build an editable scientific poster with python-pptx (native text boxes, shapes, charts)."""
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

NAVY = RGBColor(0x14, 0x28, 0x4B)
TEAL = RGBColor(0x1A, 0x9E, 0x9E)
CYAN_LIGHT = RGBColor(0xE6, 0xF6, 0xF6)
ORANGE = RGBColor(0xE8, 0x59, 0x0C)
GREY = RGBColor(0x5F, 0x6B, 0x7A)
LIGHT = RGBColor(0xF4, 0xF6, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x22, 0x22, 0x22)
FONT = "Calibri"


def new_poster(w_in=48, h_in=36):
    p = Presentation()
    p.slide_width = Inches(w_in)
    p.slide_height = Inches(h_in)
    s = p.slides.add_slide(p.slide_layouts[6])
    return p, s


def rect(slide, x, y, w, h, fill=WHITE, line=None, shape=MSO_SHAPE.RECTANGLE, line_w=1.5):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    if sh.has_text_frame:
        sh.text_frame.text = ""
    return sh


def text(slide, x, y, w, h, paras, size=24, color=DARK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         font=FONT, line_spacing=1.08, space_after=6):
    """paras: str or list of str / (str, dict) / list-of-runs [(text, dict), ...]. dict keys: size,bold,color,italic,bullet."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    if isinstance(paras, str):
        paras = [paras]
    first = True
    for para in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        runs = para if isinstance(para, list) else [para if isinstance(para, tuple) else (para, {})]
        for rt, st in runs:
            r = p.add_run()
            r.text = rt
            f = r.font
            f.name = st.get("font", font)
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.italic = st.get("italic", False)
            f.color.rgb = st.get("color", color)
    return tb


def bullets(slide, x, y, w, h, items, size=22, color=DARK, bullet="•", **kw):
    paras = []
    for it in items:
        if isinstance(it, list):
            paras.append([(bullet + " ", {"color": TEAL, "bold": True, "size": size})] + it)
        else:
            paras.append([(bullet + " ", {"color": TEAL, "bold": True, "size": size}), (it, {"size": size, "color": color})])
    return text(slide, x, y, w, h, paras, size=size, color=color, **kw)


def section(slide, x, y, w, h, number, title, title_size=34):
    """White card with a navy header strip; returns content origin (x, y, w)."""
    rect(slide, x, y, w, h, fill=WHITE, line=RGBColor(0xD5, 0xDB, 0xE3), line_w=1.25)
    rect(slide, x, y, w, 0.82, fill=NAVY)
    rect(slide, x, y, 0.22, 0.82, fill=TEAL)
    text(slide, x + 0.4, y + 0.06, w - 0.6, 0.72, [[(f"{number}  ", {"color": RGBColor(0x7F, 0xD8, 0xD8), "bold": True}),
                                                    (title.upper(), {"color": WHITE, "bold": True})]],
         size=title_size, anchor=MSO_ANCHOR.MIDDLE)
    return x + 0.35, y + 1.0, w - 0.7


def picture(slide, path, x, y, w=None, h=None):
    from pathlib import Path
    if not Path(path).exists():  # never invent a figure: show an explicit placeholder instead
        hh = h if h is not None else (w or 4) * 0.5
        ww = w if w is not None else hh * 2
        rect(slide, x, y, ww, hh, fill=LIGHT, line=GREY)
        text(slide, x, y + hh / 2 - 0.4, ww, 0.8, [[(f"Figure pending: {Path(path).name}", {"italic": True, "color": GREY})]],
             size=20, align=PP_ALIGN.CENTER)
        return None
    kw = {}
    if w is not None:
        kw["width"] = Inches(w)
    if h is not None:
        kw["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


def fit_picture(slide, path, x, y, max_w, max_h, align="center"):
    """Insert an image scaled to fit inside (max_w, max_h) inches, preserving aspect. Returns (w, h) used."""
    from pathlib import Path
    from PIL import Image
    if not Path(path).exists():
        picture(slide, path, x, y, w=max_w, h=max_h)
        return max_w, max_h
    with Image.open(path) as im:
        iw, ih = im.size
    ar = iw / ih
    w, h = (max_w, max_w / ar) if max_w / ar <= max_h else (max_h * ar, max_h)
    dx = (max_w - w) / 2 if align == "center" else 0
    picture(slide, path, x + dx, y, w=w, h=h)
    return w, h


def caption(slide, x, y, w, txt, size=17):
    return text(slide, x, y, w, 0.6, [[(txt, {"italic": True, "color": GREY, "size": size})]], size=size)


def callout(slide, x, y, w, h, title, body, fill=CYAN_LIGHT, title_color=NAVY, size=22):
    rect(slide, x, y, w, h, fill=fill, line=TEAL, line_w=2)
    text(slide, x + 0.2, y + 0.12, w - 0.4, h - 0.2, [[(title, {"bold": True, "color": title_color, "size": size + 2})]] +
         [[(b, {"size": size})] for b in body], size=size)


def line_chart(slide, x, y, w, h, categories, series, title=None, y_title=None, y_max=None, number_format='0.00',
               colors=None, font_size=16):
    cd = CategoryChartData()
    cd.categories = categories
    for name, vals in series:
        cd.add_series(name, [None if v is None else float(v) for v in vals])
    gf = slide.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.BOTTOM
    ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(font_size - 2)
    ch.font.size = Pt(font_size)
    ch.font.name = FONT
    if title:
        ch.has_title = True
        ch.chart_title.text_frame.text = title
        ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(font_size + 2)
        ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
        ch.chart_title.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)
    va.tick_labels.number_format = number_format
    va.tick_labels.number_format_is_linked = False
    if y_max is not None:
        va.maximum_scale = y_max
        va.minimum_scale = 0
    if y_title:
        va.has_title = True
        va.axis_title.text_frame.text = y_title
        va.axis_title.text_frame.paragraphs[0].runs[0].font.size = Pt(font_size - 1)
    ca = ch.category_axis
    ca.has_title = True
    ca.axis_title.text_frame.text = "post-monsoon scenes used (k)"
    ca.axis_title.text_frame.paragraphs[0].runs[0].font.size = Pt(font_size - 1)
    if colors:
        for s, c in zip(ch.series, colors):
            s.format.line.color.rgb = c
            s.format.line.width = Pt(3)
            s.marker.style = XL_MARKER_STYLE.CIRCLE
            s.marker.size = 9
            s.marker.format.fill.solid()
            s.marker.format.fill.fore_color.rgb = c
            s.marker.format.line.color.rgb = c
            s.smooth = False
    return gf


def table(slide, x, y, w, h, rows, col_w=None, font_size=16, header_fill=NAVY):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(h))
    t = gt.table
    if col_w:
        for i, cw in enumerate(col_w):
            t.columns[i].width = Inches(cw)
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.text = str(v)
            para = c.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            run = para.runs[0]
            run.font.size = Pt(font_size)
            run.font.name = FONT
            run.font.bold = i == 0
            run.font.color.rgb = WHITE if i == 0 else DARK
            c.fill.solid()
            c.fill.fore_color.rgb = header_fill if i == 0 else (LIGHT if i % 2 else WHITE)
            c.margin_left = c.margin_right = Inches(0.05)
            c.margin_top = c.margin_bottom = Inches(0.02)
    return gt
