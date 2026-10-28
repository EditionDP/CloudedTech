"""Local CloudEdTech branded image composition.

This module creates corporate graphic templates, not AI-generated images.
No publication or external API calls occur here.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO

NAVY = "#080A27"
ORANGE = "#FF7400"
WHITE = "#FFFFFF"

SIZES = {
    "linkedin": (1200, 627),
    "x": (1200, 675),
    "discord": (1200, 675),
}


def _font(size: int, bold: bool = False):
    windows = Path("C:/Windows/Fonts")
    candidates = (
        ["arialbd.ttf", "segoeuib.ttf"]
        if bold else
        ["arial.ttf", "segoeui.ttf"]
    )
    for name in candidates:
        path = windows / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()



def _brand_icon():
    """Render the official CloudEdTech SVG with resvg."""
    import resvg_py

    asset = (
        Path(__file__).resolve().parents[3]
        / "frontend/public/brand/cloudedtech-icon.svg"
    )

    if not asset.is_file():
        raise FileNotFoundError("Official brand icon not found")

    png_data = resvg_py.svg_to_bytes(
        svg_string=asset.read_text(encoding="utf-8"),
        width=112,
        height=80,
    )

    return Image.open(BytesIO(png_data)).convert("RGBA")


def generar_pieza_corporativa(
    plataforma: str,
    titulo: str,
    mensaje: str,
    destino: str | Path,
) -> Path:
    """Generate a branded PNG locally without publishing it."""

    if plataforma not in SIZES:
        raise ValueError("Unsupported platform")

    if not titulo.strip() or not mensaje.strip():
        raise ValueError("Title and message are required")

    width, height = SIZES[plataforma]
    image = Image.new("RGB", (width, height), NAVY)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (65, 65, width - 65, height - 65),
        radius=35,
        fill="#11153B",
        outline="#303759",
        width=2,
    )

    draw.rounded_rectangle(
        (100, 105, 250, 117),
        radius=6,
        fill=ORANGE,
    )

    icon = _brand_icon()
    if icon is not None:
        image.paste(icon, (width - 230, 115), icon)

    draw.text(
        (100, 145),
        "CloudEdTech",
        font=_font(45, bold=True),
        fill=WHITE,
    )

    if titulo.strip().casefold() != "cloudedtech":
        draw.text(
            (100, 218),
            titulo.strip()[:65],
            font=_font(39, bold=True),
            fill=ORANGE,
        )

    # Mixed text/emoji layout. Preserve the original message characters.
    import unicodedata

    emoji_path = Path("C:/Windows/Fonts/seguiemj.ttf")

    if not emoji_path.is_file():
        raise RuntimeError("Segoe UI Emoji font is unavailable")

    has_subtitle = titulo.strip().casefold() != "cloudedtech"
    body_top = 290 if has_subtitle else 225
    body_bottom = height - 145
    available_width = width - 230
    available_height = body_bottom - body_top

    def is_emoji_character(character):
        code = ord(character)
        return (
            0x1F000 <= code <= 0x1FAFF
            or 0x2600 <= code <= 0x27BF
            or code in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139)
        )

    def emoji_clusters(value):
        """Keep variation selectors, modifiers and ZWJ sequences together."""
        clusters = []
        current = ""

        for character in value:
            code = ord(character)
            continuation = (
                code in (0x200D, 0xFE0E, 0xFE0F, 0x20E3)
                or 0x1F3FB <= code <= 0x1F3FF
                or unicodedata.combining(character) != 0
                or current.endswith("\u200d")
            )

            if current and continuation:
                current += character
            else:
                if current:
                    clusters.append(current)
                current = character

        if current:
            clusters.append(current)

        return clusters

    def cluster_is_emoji(cluster):
        return any(is_emoji_character(char) for char in cluster)

    def measure_cluster(cluster, text_font, emoji_font):
        font = emoji_font if cluster_is_emoji(cluster) else text_font
        return draw.textlength(cluster, font=font)

    def measure_text(value, text_font, emoji_font):
        return sum(
            measure_cluster(cluster, text_font, emoji_font)
            for cluster in emoji_clusters(value)
        )

    def wrap_paragraph(paragraph, text_font, emoji_font):
        """Wrap at word boundaries while preserving every character."""
        import re

        result = []
        current = ""

        # Keep whitespace attached to the following word.
        tokens = re.findall(r"\s*\S+|\s+", paragraph)

        for token in tokens:
            candidate = current + token

            if measure_text(candidate, text_font, emoji_font) <= available_width:
                current = candidate
                continue

            if current:
                result.append(current.rstrip())
                current = token.lstrip()

            if measure_text(current, text_font, emoji_font) <= available_width:
                continue

            # Split an exceptionally long token by emoji-safe clusters.
            remainder = current
            current = ""

            for cluster in emoji_clusters(remainder):
                candidate = current + cluster

                if measure_text(candidate, text_font, emoji_font) <= available_width:
                    current = candidate
                    continue

                if current:
                    result.append(current)
                    current = ""

                if measure_cluster(cluster, text_font, emoji_font) > available_width:
                    raise ValueError(
                        "A text or emoji cluster cannot fit in the image"
                    )

                current = cluster

        if current:
            result.append(current.rstrip())

        # Avoid leaving a closing emoji and punctuation alone on a line.
        # Move the preceding word only when the combined line fits.
        if len(result) >= 2:
            last_line = result[-1].strip()
            last_clusters = emoji_clusters(last_line)

            emoji_only = (
                bool(last_clusters)
                and any(cluster_is_emoji(c) for c in last_clusters)
                and all(
                    cluster_is_emoji(c)
                    or c.isspace()
                    or unicodedata.category(c[0]).startswith("P")
                    for c in last_clusters
                )
            )

            if emoji_only:
                previous = result[-2].rstrip()
                words = previous.rsplit(None, 1)

                if len(words) == 2:
                    moved_word = words[1]
                    combined = moved_word + " " + last_line

                    if measure_text(
                        combined, text_font, emoji_font
                    ) <= available_width:
                        result[-2] = words[0]
                        result[-1] = combined

        return result

    def draw_mixed_text(x, y, value, text_font, emoji_font):
        cursor = float(x)

        for cluster in emoji_clusters(value):
            if cluster_is_emoji(cluster):
                draw.text(
                    (round(cursor), y),
                    cluster,
                    font=emoji_font,
                    embedded_color=True,
                    fill=WHITE,
                )
            else:
                draw.text(
                    (round(cursor), y),
                    cluster,
                    font=text_font,
                    fill=WHITE,
                )

            cursor += measure_cluster(cluster, text_font, emoji_font)

    paragraphs = mensaje.strip().splitlines()
    layout = None

    for font_size in (34, 32, 30, 28, 26, 24):
        text_font = _font(font_size)
        emoji_font = ImageFont.truetype(str(emoji_path), font_size)
        line_height = int(font_size * 1.45)
        paragraph_gap = max(8, font_size // 2)
        candidate_lines = []

        for paragraph_index, paragraph in enumerate(paragraphs):
            if paragraph_index:
                candidate_lines.append((None, paragraph_gap))

            if paragraph.strip():
                for line in wrap_paragraph(paragraph, text_font, emoji_font):
                    candidate_lines.append((line, line_height))

        required_height = sum(space for _, space in candidate_lines)

        if required_height <= available_height:
            layout = (text_font, emoji_font, candidate_lines)
            break

    if layout is None:
        raise ValueError(
            "El mensaje es demasiado largo para una sola imagen corporativa. "
            "Acorta el texto o prepara una pieza adicional."
        )

    body_font, body_emoji_font, body_lines = layout
    y = body_top

    for line, space in body_lines:
        if line is not None:
            draw_mixed_text(
                100,
                y,
                line,
                body_font,
                body_emoji_font,
            )
        y += space

    draw.text(
        (100, height - 115),
        "Comunidad | Innovacion | Inteligencia Artificial",
        font=_font(22),
        fill="#C7CCE5",
    )

    path = Path(destino)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)
    return path
