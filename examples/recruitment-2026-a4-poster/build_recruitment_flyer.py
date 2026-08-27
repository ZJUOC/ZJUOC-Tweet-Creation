#!/usr/bin/env python3
"""Build the 2026 recruitment flyer as a 300 dpi PNG and print-ready PDF."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
BACKGROUND = ROOT / "assets/generated-ocean-robot-bg.png"
SKILL_ROOT = REPO_ROOT / "plugins/ocean-robot-wechat/skills/ocean-robot-wechat"
LOGO = SKILL_ROOT / "assets/association-logo.jpg"
QUESTIONNAIRE_QR = ROOT / "assets/recruitment-questionnaire-qr.png"
QQ_GROUP_QR_SOURCE = ROOT / "assets/qq-group-qr-source.jpg"
PHOTO_ROOT = REPO_ROOT / "examples/recruitment-2026-lively/assets/original"
CUTOUT_ROOT = SKILL_ROOT / "assets/library/cutout-watercolor"
PNG_OUTPUT = ROOT / "zju-ocean-robot-association-recruitment-2026-a4.png"
PDF_OUTPUT = ROOT / "zju-ocean-robot-association-recruitment-2026-a4.pdf"

WIDTH, HEIGHT = 2480, 3508
FONT_CANDIDATES = {
    "cjk": [
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
        ("C:/Windows/Fonts/msyh.ttc", 0),
    ],
    "bold": [
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 1),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),
        ("C:/Windows/Fonts/msyhbd.ttc", 0),
    ],
    "latin": [
        ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
        ("C:/Windows/Fonts/arial.ttf", 0),
    ],
}

INK = "#2E4148"
MUTED = "#53666C"
TURQUOISE = "#39A6A2"
CORAL = "#F06F43"
SAND = "#E9B85D"
PAPER = "#FAFCF8"


def load_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    for path, index in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=index)
    raise FileNotFoundError(
        f"No usable {kind} font found. Install Noto Sans CJK or update FONT_CANDIDATES."
    )


def font(size: int, *, bold: bool = False, latin: bool = False) -> ImageFont.FreeTypeFont:
    return load_font("latin" if latin else ("bold" if bold else "cjk"), size)


def art_font(size: int) -> ImageFont.FreeTypeFont:
    return load_font("bold", size)


def art_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    size: int,
    fill: str,
    shadow: str,
    stroke_width: int = 13,
) -> None:
    """Draw heavy poster lettering with a bright outline and offset color layer."""
    x, y = xy
    text_font = art_font(size)
    draw.text(
        (x + 18, y + 22),
        text,
        font=text_font,
        fill=shadow,
        stroke_width=stroke_width + 3,
        stroke_fill=shadow,
    )
    draw.text(
        (x, y),
        text,
        font=text_font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=PAPER,
    )


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def tracked_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    tracking: int,
) -> None:
    x, y = xy
    for character in text:
        draw.text((x, y), character, font=text_font, fill=fill)
        x += round(draw.textlength(character, font=text_font)) + tracking


def place_logo(page: Image.Image) -> None:
    logo_size = 310
    source = Image.open(LOGO).convert("RGB").resize(
        (logo_size, logo_size), Image.Resampling.LANCZOS
    )
    mask = Image.new("L", (logo_size, logo_size), 0)
    ImageDraw.Draw(mask).ellipse((3, 3, logo_size - 3, logo_size - 3), fill=255)

    shadow = Image.new("RGBA", page.size, (0, 0, 0, 0))
    shadow_mask = mask.filter(ImageFilter.GaussianBlur(18))
    shadow.paste((46, 65, 72, 42), (151, 143), shadow_mask)
    page.alpha_composite(shadow)

    backing = Image.new("RGBA", (logo_size + 24, logo_size + 24), (255, 255, 255, 0))
    ImageDraw.Draw(backing).ellipse(
        (0, 0, backing.width - 1, backing.height - 1), fill="#FFFFFF", outline=CORAL, width=9
    )
    page.alpha_composite(backing, (139, 131))
    page.paste(source, (151, 143), mask)


def place_photo(
    page: Image.Image,
    source_path: Path,
    xy: tuple[int, int],
    size: tuple[int, int],
    angle: float,
    accent: str,
) -> None:
    """Place a real article photo as a slightly rotated paper clipping."""
    photo_w, photo_h = size
    photo = cover(Image.open(source_path).convert("RGB"), size)
    card = Image.new("RGBA", (photo_w + 48, photo_h + 82), "#FFFFFF")
    card.paste(photo, (24, 24))
    card_draw = ImageDraw.Draw(card)
    card_draw.rectangle((24, photo_h + 42, photo_w + 24, photo_h + 57), fill=accent)
    card_draw.rectangle(
        (photo_w // 2 - 76, 3, photo_w // 2 + 124, 31),
        fill=(242, 214, 162, 205),
    )
    rotated = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    shadow = Image.new("RGBA", rotated.size, (46, 65, 72, 0))
    shadow.putalpha(rotated.getchannel("A").filter(ImageFilter.GaussianBlur(20)).point(lambda p: p // 4))
    page.alpha_composite(shadow, (xy[0] + 18, xy[1] + 22))
    page.alpha_composite(rotated, xy)


def place_cutout(
    page: Image.Image,
    source_path: Path,
    xy: tuple[int, int],
    max_size: int,
    angle: float,
) -> None:
    source = Image.open(source_path).convert("RGBA")
    scale = min(max_size / source.width, max_size / source.height)
    source = source.resize(
        (round(source.width * scale), round(source.height * scale)),
        Image.Resampling.LANCZOS,
    )
    source = source.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    shadow = Image.new("RGBA", source.size, (46, 65, 72, 0))
    shadow.putalpha(source.getchannel("A").filter(ImageFilter.GaussianBlur(12)).point(lambda p: p // 5))
    page.alpha_composite(shadow, (xy[0] + 10, xy[1] + 12))
    page.alpha_composite(source, xy)


def centered_text_x(
    draw: ImageDraw.ImageDraw,
    text: str,
    text_font: ImageFont.FreeTypeFont,
    center_x: int,
) -> int:
    box = draw.textbbox((0, 0), text, font=text_font)
    return round(center_x - (box[2] - box[0]) / 2)


def place_qr_tile(
    page: Image.Image,
    draw: ImageDraw.ImageDraw,
    qr: Image.Image,
    xy: tuple[int, int],
    accent: str,
    label: str,
    detail: str,
) -> None:
    """Place one supplied QR with a generous quiet frame and a clear label."""
    x, y = xy
    tile_size = 330
    draw.rounded_rectangle(
        (x, y, x + tile_size + 38, y + tile_size + 38),
        radius=34,
        fill="#FFFFFF",
        outline=accent,
        width=10,
    )
    qr = qr.convert("RGB").resize((tile_size, tile_size), Image.Resampling.NEAREST)
    page.paste(qr, (x + 19, y + 19))
    label_font = art_font(43)
    detail_font = font(29, bold=True)
    center_x = x + (tile_size + 38) // 2
    draw.text(
        (centered_text_x(draw, label, label_font, center_x), y + tile_size + 58),
        label,
        font=label_font,
        fill=INK,
    )
    draw.text(
        (centered_text_x(draw, detail, detail_font, center_x), y + tile_size + 116),
        detail,
        font=detail_font,
        fill=MUTED,
    )


def build_png() -> None:
    base = cover(Image.open(BACKGROUND).convert("RGB"), (WIDTH, HEIGHT))
    base = ImageEnhance.Contrast(base).enhance(0.97).convert("RGBA")

    # A translucent paper wash keeps the generated artwork lively while preserving
    # a crisp reading zone for deterministic typography.
    wash_color = Image.new("RGBA", (WIDTH, HEIGHT), (250, 252, 248, 255))
    wash_mask = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(wash_mask).rectangle((20, 20, 1490, 2700), fill=222)
    wash_mask = wash_mask.filter(ImageFilter.GaussianBlur(120))
    base.paste(wash_color, (0, 0), wash_mask)

    # Real moments from the source WeChat article form an irregular editorial
    # collage: training, competition, field testing, and the shared lab.
    place_photo(base, PHOTO_ROOT / "original-24.jpg", (1630, 435), (650, 365), 4.0, CORAL)
    place_photo(base, PHOTO_ROOT / "original-33.jpg", (1505, 850), (680, 390), -4.5, TURQUOISE)
    place_photo(base, PHOTO_ROOT / "original-16.jpg", (1815, 1265), (540, 405), 4.5, SAND)
    place_photo(base, PHOTO_ROOT / "original-54.jpg", (1390, 1450), (540, 345), -3.0, CORAL)

    place_logo(base)
    draw = ImageDraw.Draw(base)

    draw.text((520, 160), "浙江大学学生海洋机器人协会", font=art_font(66), fill=INK)
    tracked_text(
        draw,
        (522, 258),
        "ZJU OCEAN ROBOT ASSOCIATION",
        font(27, latin=True),
        MUTED,
        5,
    )
    draw.rounded_rectangle((520, 304, 990, 318), radius=7, fill=CORAL)
    draw.rounded_rectangle((1005, 304, 1162, 318), radius=7, fill=SAND)

    tracked_text(
        draw,
        (168, 590),
        "2026 RECRUITMENT  /  OPEN TO ALL ZJU STUDENTS",
        font(29, latin=True),
        TURQUOISE,
        4,
    )
    art_text(draw, (145, 660), "2026 纳新", 194, INK, TURQUOISE, 12)
    art_text(draw, (145, 905), "向海出发", 204, CORAL, SAND, 14)
    draw.arc((680, 1070, 1275, 1170), 195, 345, fill=CORAL, width=15)
    draw.arc((735, 1090, 1300, 1175), 195, 345, fill=TURQUOISE, width=9)
    draw.text(
        (160, 1185),
        "不限年级 · 不限专业 · 不要求基础",
        font=art_font(60),
        fill=MUTED,
    )

    items = [
        ("01", "从零内训", "算法、电控与结构全覆盖"),
        ("02", "项目实践", "设计、联调、下水、比赛复盘"),
        ("03", "面向全校", "带着兴趣来，把想法真正做出来"),
    ]
    y = 1390
    for number, title, description in items:
        draw.rounded_rectangle((160, y + 8, 262, y + 110), radius=25, fill=CORAL)
        number_box = draw.textbbox((0, 0), number, font=font(36, bold=True, latin=True))
        number_w = number_box[2] - number_box[0]
        draw.text(
            (211 - number_w / 2, y + 36),
            number,
            font=font(36, bold=True, latin=True),
            fill="#FFFFFF",
        )
        draw.text((305, y - 6), title, font=art_font(74), fill=INK)
        draw.text((305, y + 91), description, font=font(43, bold=True), fill=MUTED)
        draw.line((305, y + 163, 1215, y + 163), fill=(83, 102, 108, 82), width=3)
        y += 255

    # Registered watercolor cutouts act as light punctuation beside the three
    # recruitment promises; they keep the page lively without covering copy.
    place_cutout(base, CUTOUT_ROOT / "thruster-wrench.png", (1110, 1375), 210, -8)
    place_cutout(base, CUTOUT_ROOT / "sonar-fish.png", (1115, 1620), 220, 7)
    place_cutout(base, CUTOUT_ROOT / "rov-bubble.png", (1120, 1860), 205, -5)

    questionnaire_qr = Image.open(QUESTIONNAIRE_QR).convert("RGB")
    # The QQ screenshot is user-supplied. Crop only the square code area and keep
    # the surrounding dark quiet zone intact; never regenerate or stylize it.
    # Dense colored QR extent in the supplied 1284x2283 screenshot is
    # x=238..1044, y=871..1677. Add an even 33px quiet margin so all three
    # positioning rings remain complete and the code is optically centered.
    qq_group_qr = Image.open(QQ_GROUP_QR_SOURCE).convert("RGB").crop(
        (205, 838, 1077, 1710)
    )
    draw.rounded_rectangle((120, 2074, 824, 2160), radius=42, fill=CORAL)
    draw.text((220, 2091), "扫码报名 · 加入群聊", font=art_font(43), fill="#FFFFFF")
    place_qr_tile(
        base,
        draw,
        questionnaire_qr,
        (104, 2190),
        CORAL,
        "纳新问卷",
        "填写报名信息",
    )
    place_qr_tile(
        base,
        draw,
        qq_group_qr,
        (520, 2190),
        TURQUOISE,
        "QQ 纳新群",
        "群号 1057559620",
    )
    draw.text((920, 2192), "先填写问卷", font=art_font(68), fill=INK)
    draw.text((920, 2287), "再加入群聊", font=art_font(68), fill=CORAL)
    draw.text((922, 2402), "获取内训、项目与比赛通知", font=font(35, bold=True), fill=MUTED)
    draw.text((922, 2468), "关注公众号 ZJUORA", font=font(35, bold=True), fill=MUTED)

    # Replace the former dark badge with large open lettering. The paper outline
    # keeps it legible across the coral ribbon without introducing a black box.
    art_text(draw, (145, 2845), "把奇思妙想", 84, INK, CORAL, 8)
    art_text(draw, (145, 2950), "做成真正下水的机器人", 78, INK, TURQUOISE, 8)
    tracked_text(
        draw,
        (162, 3070),
        "LEARN  ·  BUILD  ·  DIVE",
        font(36, latin=True),
        INK,
        5,
    )
    draw.line((154, 3133, 725, 3133), fill=CORAL, width=12)
    draw.line((744, 3133, 970, 3133), fill=TURQUOISE, width=12)

    rgb = base.convert("RGB")
    rgb.save(PNG_OUTPUT, format="PNG", dpi=(300, 300), optimize=True)


def build_pdf() -> None:
    page_width, page_height = A4
    pdf = canvas.Canvas(str(PDF_OUTPUT), pagesize=A4, pageCompression=1)
    pdf.setTitle("浙江大学学生海洋机器人协会 2026 纳新宣传单 - 艺术字双二维码版")
    pdf.setAuthor("浙江大学学生海洋机器人协会")
    pdf.setSubject("2026 海洋机器人协会纳新宣传单")
    pdf.drawImage(
        str(PNG_OUTPUT),
        0,
        0,
        width=page_width,
        height=page_height,
        preserveAspectRatio=False,
        mask="auto",
    )
    pdf.showPage()
    pdf.save()


if __name__ == "__main__":
    PNG_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    build_png()
    build_pdf()
    print(PNG_OUTPUT)
    print(PDF_OUTPUT)
