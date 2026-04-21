#!/usr/bin/env python3
"""Generate Arabic PDFs for Chapter 2 and Chapter 3 of Distributed Systems."""

import os
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts
FONT_DIR = '/home/runner/work/TESTC/TESTC'
pdfmetrics.registerFont(TTFont('Amiri', os.path.join(FONT_DIR, 'Amiri-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Amiri-Bold', os.path.join(FONT_DIR, 'Amiri-Bold.ttf')))

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 2 * cm

# ─── Arabic helper ────────────────────────────────────────────────────────────

def ar(text):
    """Reshape + bidi-reorder Arabic text for correct PDF rendering."""
    return get_display(arabic_reshaper.reshape(text))


def draw_rtl_text(c, text, x, y, font, size, color=colors.black, max_width=None):
    """Draw a single line of RTL text. Returns actual width drawn."""
    c.setFont(font, size)
    c.setFillColor(color)
    rendered = ar(text)
    if max_width:
        # Truncate if too wide
        while c.stringWidth(rendered, font, size) > max_width and len(rendered) > 3:
            rendered = rendered[1:]
    tw = c.stringWidth(rendered, font, size)
    c.drawString(x - tw, y, rendered)
    return tw


def wrap_rtl(c, text, font, size, max_width):
    """Wrap Arabic text into lines not exceeding max_width. Returns list of display strings."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        test_display = ar(test)
        if c.stringWidth(test_display, font, size) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return [ar(l) for l in lines] if lines else [ar(text)]


def draw_wrapped_rtl(c, text, right_x, y, font, size, max_width, line_height, color=colors.black):
    """Draw wrapped RTL text, returns the y position after the last line."""
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap_rtl(c, text, font, size, max_width)
    for line in lines:
        tw = c.stringWidth(line, font, size)
        c.drawString(right_x - tw, y, line)
        y -= line_height
    return y

# ─── Layout helpers ──────────────────────────────────────────────────────────

HEADER_BG = colors.HexColor('#1a3a5c')
ACCENT     = colors.HexColor('#c8a84b')
LIGHT_BG   = colors.HexColor('#f5f5f0')
DIVIDER    = colors.HexColor('#d0d0c0')

RIGHT_X = PAGE_WIDTH - MARGIN


def draw_header(c, chapter_ar, chapter_num_ar, page_num, total_pages=None):
    """Draw page header with chapter info."""
    c.setFillColor(HEADER_BG)
    c.rect(0, PAGE_HEIGHT - 1.8*cm, PAGE_WIDTH, 1.8*cm, fill=1, stroke=0)
    # Chapter label
    c.setFont('Amiri-Bold', 11)
    c.setFillColor(ACCENT)
    label = ar(chapter_ar)
    tw = c.stringWidth(label, 'Amiri-Bold', 11)
    c.drawString(RIGHT_X - tw, PAGE_HEIGHT - 1.2*cm, label)
    # Page number
    c.setFont('Amiri', 9)
    c.setFillColor(colors.white)
    pg = f"{page_num}"
    c.drawString(MARGIN, PAGE_HEIGHT - 1.2*cm, pg)


def draw_footer(c):
    """Draw decorative footer bar."""
    c.setFillColor(HEADER_BG)
    c.rect(0, 0, PAGE_WIDTH, 0.6*cm, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, 0.6*cm, PAGE_WIDTH, 0.08*cm, fill=1, stroke=0)


def draw_title_page(c, title_ar, subtitle_ar, chapter_label_ar):
    """Draw a full title page."""
    # Background
    c.setFillColor(HEADER_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    # Gold accent bar
    c.setFillColor(ACCENT)
    c.rect(0, PAGE_HEIGHT * 0.42, PAGE_WIDTH, 0.15*cm, fill=1, stroke=0)
    c.rect(0, PAGE_HEIGHT * 0.38, PAGE_WIDTH, 0.08*cm, fill=1, stroke=0)

    # Main title
    c.setFont('Amiri-Bold', 36)
    c.setFillColor(colors.white)
    t = ar(title_ar)
    tw = c.stringWidth(t, 'Amiri-Bold', 36)
    c.drawString((PAGE_WIDTH - tw) / 2, PAGE_HEIGHT * 0.60, t)

    # Subtitle
    c.setFont('Amiri', 22)
    c.setFillColor(ACCENT)
    s = ar(subtitle_ar)
    sw = c.stringWidth(s, 'Amiri', 22)
    c.drawString((PAGE_WIDTH - sw) / 2, PAGE_HEIGHT * 0.50, s)

    # Chapter label
    c.setFont('Amiri', 16)
    c.setFillColor(colors.white)
    ch = ar(chapter_label_ar)
    cw = c.stringWidth(ch, 'Amiri', 16)
    c.drawString((PAGE_WIDTH - cw) / 2, PAGE_HEIGHT * 0.35, ch)

    # Bottom note
    c.setFont('Amiri', 10)
    c.setFillColor(DIVIDER)
    note = ar("الأنظمة الموزعة – الطبعة الرابعة")
    nw = c.stringWidth(note, 'Amiri', 10)
    c.drawString((PAGE_WIDTH - nw) / 2, 1.5*cm, note)
    c.showPage()


def draw_slide_page(c, slide_num, title_ar, bullets, chapter_ar, page_num):
    """Draw one slide's content on a PDF page."""
    draw_footer(c)
    draw_header(c, chapter_ar, '', page_num)

    content_top    = PAGE_HEIGHT - 2.2*cm
    content_bottom = 1.0*cm
    content_height = content_top - content_bottom

    # Slide number badge
    badge_y = content_top - 0.3*cm
    c.setFillColor(ACCENT)
    c.roundRect(MARGIN, badge_y - 0.55*cm, 1.4*cm, 0.65*cm, 0.2*cm, fill=1, stroke=0)
    c.setFont('Amiri-Bold', 12)
    c.setFillColor(HEADER_BG)
    num_s = str(slide_num)
    nw = c.stringWidth(num_s, 'Amiri-Bold', 12)
    c.drawString(MARGIN + (1.4*cm - nw)/2, badge_y - 0.35*cm, num_s)

    # Title
    title_y = badge_y - 0.15*cm
    c.setFont('Amiri-Bold', 18)
    c.setFillColor(HEADER_BG)
    title_r = ar(title_ar)
    tw = c.stringWidth(title_r, 'Amiri-Bold', 18)
    # Ensure it fits
    max_tw = RIGHT_X - MARGIN - 2.0*cm
    while tw > max_tw and len(title_r) > 4:
        title_r = title_r[1:]
        tw = c.stringWidth(title_r, 'Amiri-Bold', 18)
    c.drawString(RIGHT_X - tw, title_y, title_r)

    # Divider
    div_y = title_y - 0.45*cm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line(MARGIN, div_y, RIGHT_X, div_y)

    # Bullets
    y = div_y - 0.5*cm
    max_w = RIGHT_X - MARGIN - 0.8*cm
    line_h_normal = 0.55*cm
    line_h_sub    = 0.50*cm

    for bullet in bullets:
        if y < content_bottom + 0.5*cm:
            c.showPage()
            page_num += 1
            draw_footer(c)
            draw_header(c, chapter_ar, '', page_num)
            y = content_top - 0.3*cm

        level = bullet.get('level', 0)
        text  = bullet['text']
        is_section = bullet.get('section', False)

        if is_section:
            # Section heading
            y -= 0.2*cm
            c.setFillColor(LIGHT_BG)
            c.rect(MARGIN, y - 0.45*cm, RIGHT_X - MARGIN, 0.6*cm, fill=1, stroke=0)
            c.setFont('Amiri-Bold', 13)
            c.setFillColor(HEADER_BG)
            s = ar(text)
            sw = c.stringWidth(s, 'Amiri-Bold', 13)
            c.drawString(RIGHT_X - sw - 0.2*cm, y - 0.28*cm, s)
            y -= 0.75*cm
        else:
            indent = MARGIN + level * 0.5*cm
            right  = RIGHT_X - level * 0.3*cm
            avail  = right - indent - 0.6*cm

            font      = 'Amiri-Bold' if level == 0 else 'Amiri'
            font_size = 12 if level == 0 else 11
            lh        = line_h_normal if level == 0 else line_h_sub

            # Bullet marker
            if level == 0:
                c.setFillColor(ACCENT)
                c.circle(right - 0.2*cm, y - 0.12*cm, 0.07*cm, fill=1, stroke=0)
            else:
                c.setFillColor(HEADER_BG)
                c.rect(right - 0.3*cm, y - 0.10*cm, 0.15*cm, 0.15*cm, fill=1, stroke=0)

            lines = wrap_rtl(c, text, font, font_size, avail)
            for line in lines:
                if y < content_bottom + 0.5*cm:
                    c.showPage()
                    page_num += 1
                    draw_footer(c)
                    draw_header(c, chapter_ar, '', page_num)
                    y = content_top - 0.3*cm
                c.setFont(font, font_size)
                c.setFillColor(colors.black)
                lw = c.stringWidth(line, font, font_size)
                c.drawString(right - lw - 0.4*cm, y, line)
                y -= lh
            y -= 0.1*cm

    c.showPage()
    return page_num + 1

# ─── Chapter 2 data ──────────────────────────────────────────────────────────

CHAPTER2_TITLE   = "الأنظمة الموزعة"
CHAPTER2_SUB     = "الفصل الثاني: المعماريات"
CHAPTER2_LABEL   = "Chapter 02: Architectures"

CHAPTER2_SLIDES = [
    {
        'title': 'الأنظمة الموزعة – الفصل الثاني: المعماريات',
        'bullets': [
            {'level': 0, 'text': 'Distributed Systems'},
            {'level': 0, 'text': 'الفصل الثاني: المعماريات (Architectures)'},
        ]
    },
    {
        'title': 'أنماط المعمارية (Architectural Styles)',
        'bullets': [
            {'text': 'المعماريات', 'section': True},
            {'level': 0, 'text': 'الفكرة الأساسية'},
            {'level': 1, 'text': 'يُعرَّف النمط المعماري من خلال:'},
            {'level': 1, 'text': 'مكوّنات (Components) قابلة للاستبدال ذات واجهات محددة بوضوح'},
            {'level': 1, 'text': 'طريقة ربط هذه المكوّنات ببعضها البعض'},
            {'level': 1, 'text': 'البيانات المتبادلة بين المكوّنات'},
            {'level': 1, 'text': 'كيفية تشكيل هذه المكوّنات والروابط (Connectors) معاً في نظام متكامل'},
            {'level': 0, 'text': 'الرابط (Connector)'},
            {'level': 1, 'text': 'آلية تتوسّط عمليات الاتصال أو التنسيق أو التعاون بين المكوّنات'},
            {'level': 1, 'text': 'أمثلة: استدعاء الإجراءات عن بُعد (RPC)، تبادل الرسائل، أو البث المتدفق (Streaming)'},
        ]
    },
    {
        'title': 'المعمارية الطبقية (Layered Architecture)',
        'bullets': [
            {'text': 'المعماريات', 'section': True},
            {'level': 0, 'text': 'أنماط المعمارية – المعمارية الطبقية'},
            {'level': 1, 'text': 'تنظيمات طبقية مختلفة (أ)، (ب)، (ج)'},
            {'level': 1, 'text': 'تُقسَّم المكوّنات إلى طبقات منظّمة بشكل هرمي'},
            {'level': 1, 'text': 'كل طبقة تقدّم خدمات للطبقة الأعلى منها وتستهلك خدمات الطبقة الأدنى'},
            {'level': 1, 'text': 'يسهل تبديل أي طبقة دون التأثير على بقية المنظومة'},
        ]
    },
    {
        'title': 'سلاسل الكتل (Blockchains)',
        'bullets': [
            {'text': 'المعماريات – المعماريات الهجينة', 'section': True},
            {'level': 0, 'text': 'مبدأ عمل نظام Blockchain'},
            {'level': 0, 'text': 'ملاحظات:'},
            {'level': 1, 'text': 'تُنظَّم الكتل في سلسلة لا يمكن تزويرها وتعمل بنظام الإلحاق فقط (Append-only)'},
            {'level': 1, 'text': 'كل كتلة في السلسلة غير قابلة للتغيير (Immutable) ⇒ يستوجب ذلك نسخاً احتياطياً هائلاً'},
            {'level': 1, 'text': 'التحدي الحقيقي يكمن في تحديد مَن يُسمح له بإلحاق كتلة جديدة بالسلسلة'},
            {'level': 0, 'text': 'معماريات Blockchain'},
        ]
    },
    {
        'title': 'إلحاق كتلة: التوافق الموزّع – الحل المركزي',
        'bullets': [
            {'text': 'المعماريات – المعماريات الهجينة', 'section': True},
            {'level': 0, 'text': 'الحل المركزي (Centralized Solution)'},
            {'level': 0, 'text': 'ملاحظة:'},
            {'level': 1, 'text': 'تتولى جهة واحدة تحديد المدقِّق (Validator) المخوَّل له إلحاق كتلة'},
            {'level': 1, 'text': 'هذا لا يتوافق مع الأهداف التصميمية لأنظمة Blockchain القائمة على اللامركزية'},
        ]
    },
    {
        'title': 'إلحاق كتلة: التوافق الموزّع – الحل الموزّع (المصرَّح به)',
        'bullets': [
            {'text': 'المعماريات – المعماريات الهجينة', 'section': True},
            {'level': 0, 'text': 'الحل الموزّع المصرَّح به (Distributed / Permissioned)'},
            {'level': 0, 'text': 'ملاحظة:'},
            {'level': 1, 'text': 'مجموعة صغيرة نسبياً من الخوادم المختارة تتوافق معاً على المدقِّق المؤهَّل'},
            {'level': 1, 'text': 'لا يُشترط الثقة بأيٍّ من هذه الخوادم، ما دام ثلثاها تقريباً يعملان وفق المواصفات'},
            {'level': 1, 'text': 'في الواقع العملي، لا يمكن استيعاب سوى عشرات الخوادم القليلة'},
        ]
    },
    {
        'title': 'إلحاق كتلة: التوافق الموزّع – الحل اللامركزي (غير المقيَّد)',
        'bullets': [
            {'text': 'المعماريات – المعماريات الهجينة', 'section': True},
            {'level': 0, 'text': 'الحل اللامركزي غير المقيَّد (Decentralized / Permissionless)'},
            {'level': 0, 'text': 'ملاحظة:'},
            {'level': 1, 'text': 'يشارك جميع الأطراف في انتخاب القائد (Leader Election)'},
            {'level': 1, 'text': 'القائد المنتخَب وحده هو المخوَّل بإلحاق كتلة من المعاملات الموثَّقة'},
            {'level': 1, 'text': 'انتخاب قائد لامركزي على نطاق واسع بشكل عادل وآمن وموثوق أمر بالغ التعقيد'},
        ]
    },
]

# ─── Chapter 3 data ──────────────────────────────────────────────────────────

CHAPTER3_TITLE = "الأنظمة الموزعة"
CHAPTER3_SUB   = "الفصل الثالث: العمليات"
CHAPTER3_LABEL = "Chapter 03: Processes"

CHAPTER3_SLIDES = [
    {
        'title': 'الأنظمة الموزعة – الفصل الثالث: العمليات',
        'bullets': [
            {'level': 0, 'text': 'Distributed Systems'},
            {'level': 1, 'text': '(الطبعة الرابعة، الإصدار 01)'},
            {'level': 0, 'text': 'الفصل الثالث: العمليات (Processes)'},
        ]
    },
    {
        'title': 'مقدمة إلى الخيوط (Threads)',
        'bullets': [
            {'text': 'العمليات – الخيوط', 'section': True},
            {'level': 0, 'text': 'الفكرة الأساسية'},
            {'level': 1, 'text': 'نبني معالجات افتراضية برمجياً فوق المعالجات المادية:'},
            {'level': 0, 'text': 'المعالج (Processor)'},
            {'level': 1, 'text': 'يوفّر مجموعة من التعليمات مع القدرة على تنفيذها تلقائياً بصورة متسلسلة'},
            {'level': 0, 'text': 'الخيط (Thread)'},
            {'level': 1, 'text': 'معالج برمجي صغير يُنفَّذ في سياقه تسلسلٌ من التعليمات'},
            {'level': 1, 'text': 'حفظ سياق الخيط يعني إيقاف التنفيذ الحالي وتخزين كافة البيانات اللازمة لاستئنافه لاحقاً'},
            {'level': 0, 'text': 'العملية (Process)'},
            {'level': 1, 'text': 'معالج برمجي يُنفَّذ في سياقه خيطٌ واحد أو أكثر'},
            {'level': 1, 'text': 'تنفيذ خيط يعني تنفيذ تسلسل من التعليمات في سياق ذلك الخيط'},
        ]
    },
    {
        'title': 'تبديل السياق (Context Switching)',
        'bullets': [
            {'text': 'العمليات – الخيوط', 'section': True},
            {'level': 0, 'text': 'السياقات (Contexts)'},
            {'level': 0, 'text': 'سياق المعالج (Processor Context)'},
            {'level': 1, 'text': 'المجموعة الدنيا من القيم المخزَّنة في سجلات المعالج اللازمة لتنفيذ تسلسل من التعليمات'},
            {'level': 1, 'text': 'أمثلة: مؤشر المكدّس، سجلات العنونة، عدّاد البرنامج (Program Counter)'},
            {'level': 0, 'text': 'سياق الخيط (Thread Context)'},
            {'level': 1, 'text': 'المجموعة الدنيا من القيم المخزَّنة في السجلات والذاكرة اللازمة لتنفيذ تسلسل التعليمات'},
            {'level': 1, 'text': 'يشمل سياق المعالج والحالة الراهنة (State)'},
            {'level': 0, 'text': 'سياق العملية (Process Context)'},
            {'level': 1, 'text': 'يشمل سياق الخيط إضافةً إلى قيم سجلات وحدة إدارة الذاكرة (MMU)'},
        ]
    },
    {
        'title': 'تبديل السياق – ملاحظات',
        'bullets': [
            {'text': 'العمليات – الخيوط', 'section': True},
            {'level': 0, 'text': 'ملاحظات'},
            {'level': 1, 'text': 'تشترك الخيوط في نفس فضاء العناوين، لذا يمكن إجراء تبديل سياقها دون تدخّل نظام التشغيل'},
            {'level': 1, 'text': 'تبديل سياق العملية أكثر تكلفةً لأنه يستلزم تدخّل نظام التشغيل (الانتقال إلى النواة)'},
            {'level': 1, 'text': 'إنشاء الخيوط وإتلافها أرخص بكثير من إنشاء العمليات وإتلافها'},
        ]
    },
    {
        'title': 'لماذا نستخدم الخيوط؟',
        'bullets': [
            {'text': 'العمليات – الخيوط', 'section': True},
            {'level': 0, 'text': 'أسباب مبسَّطة'},
            {'level': 0, 'text': 'تجنّب الحجب غير الضروري'},
            {'level': 1, 'text': 'العملية ذات الخيط الواحد تتوقف عند تنفيذ عمليات I/O'},
            {'level': 1, 'text': 'في العملية متعددة الخيوط، يتمكن نظام التشغيل من تحويل المعالج إلى خيط آخر'},
            {'level': 0, 'text': 'استثمار التوازي'},
            {'level': 1, 'text': 'يمكن جدولة خيوط العملية للتنفيذ المتوازي على معالجات متعددة أو معالج متعدد الأنوية (Multicore)'},
            {'level': 0, 'text': 'تجنّب تبديل العمليات'},
            {'level': 1, 'text': 'هيكلة التطبيقات الكبيرة عبر خيوط متعددة بدلاً من مجموعة من العمليات المنفصلة'},
        ]
    },
]


# ─── PDF builder ─────────────────────────────────────────────────────────────

def build_pdf(filename, title_ar, subtitle_ar, chapter_label, slides):
    out = os.path.join(FONT_DIR, filename)
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle(title_ar)
    c.setAuthor("الأنظمة الموزعة")

    draw_title_page(c, title_ar, subtitle_ar, chapter_label)

    page_num = 2
    for i, slide in enumerate(slides, 1):
        page_num = draw_slide_page(
            c,
            slide_num=i,
            title_ar=slide['title'],
            bullets=slide['bullets'],
            chapter_ar=subtitle_ar,
            page_num=page_num,
        )

    c.save()
    print(f"Created: {out}  ({os.path.getsize(out):,} bytes)")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    build_pdf(
        'الأنظمة_الموزعة_الفصل_الثاني.pdf',
        CHAPTER2_TITLE, CHAPTER2_SUB, CHAPTER2_LABEL,
        CHAPTER2_SLIDES,
    )
    build_pdf(
        'الأنظمة_الموزعة_الفصل_الثالث.pdf',
        CHAPTER3_TITLE, CHAPTER3_SUB, CHAPTER3_LABEL,
        CHAPTER3_SLIDES,
    )
    print("Done!")
