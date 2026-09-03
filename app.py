
import math
import random

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="GCF Tiling Explorer",
    page_icon="🟦",
    layout="wide",
)


# ============================================================
# Puzzle helpers
# ============================================================

def random_rectangle():
    """Generate a classroom-friendly rectangle, usually with a non-trivial GCF."""
    while True:
        g = random.randint(2, 8)
        a = random.randint(2, 5)
        b = random.randint(2, 5)

        if a == b:
            continue

        width = g * a
        height = g * b

        if width <= 30 and height <= 30:
            return width, height


def make_candidates(width, height, n=7):
    """Return tile choices that always include the true GCF."""
    g = math.gcd(width, height)
    max_side = min(width, height)

    preferred = [
        g,
        1,
        max(1, g - 1),
        min(max_side, g + 1),
        max(1, g // 2),
        min(max_side, g * 2),
    ]

    candidates = []
    for value in preferred:
        if 1 <= value <= max_side and value not in candidates:
            candidates.append(value)

    remaining = [
        value for value in range(1, max_side + 1)
        if value not in candidates
    ]
    random.shuffle(remaining)

    while len(candidates) < min(n, max_side) and remaining:
        candidates.append(remaining.pop())

    # If preferred values exceeded n, always preserve the GCF.
    if len(candidates) > n:
        others = [x for x in candidates if x != g]
        random.shuffle(others)
        candidates = [g] + others[:n - 1]

    random.shuffle(candidates)
    return candidates


# ============================================================
# Session-state callbacks
# IMPORTANT: callbacks may safely change widget state because
# they execute before Streamlit redraws the widgets.
# ============================================================

def dimensions_changed():
    width = int(st.session_state.rect_width)
    height = int(st.session_state.rect_height)

    st.session_state.candidates = make_candidates(width, height)
    st.session_state.selected = None


def new_random_rectangle():
    width, height = random_rectangle()

    st.session_state.rect_width = width
    st.session_state.rect_height = height
    st.session_state.candidates = make_candidates(width, height)
    st.session_state.selected = None


def choose_square(side):
    st.session_state.selected = int(side)


def clear_choice():
    st.session_state.selected = None


# ============================================================
# SVG drawing
# ============================================================

def tiling_svg(width, height, tile=None):
    """
    Draw the rectangle without browser stretching.

    Returns:
        svg_html, iframe_height
    """

    # Maximum size of the RECTANGLE itself.
    # It will never be stretched beyond these dimensions.
    MAX_RECT_WIDTH = 620
    MAX_RECT_HEIGHT = 300

    # Also stop tiny rectangles from becoming enormous.
    MAX_PIXELS_PER_UNIT = 36

    scale = min(
        MAX_RECT_WIDTH / width,
        MAX_RECT_HEIGHT / height,
        MAX_PIXELS_PER_UNIT,
    )

    rect_w = width * scale
    rect_h = height * scale

    left_margin = 58
    right_margin = 24
    top_margin = 54
    bottom_margin = 54

    svg_w = rect_w + left_margin + right_margin
    svg_h = rect_h + top_margin + bottom_margin

    x0 = left_margin
    y0 = top_margin

    valid = (
        tile is not None
        and width % tile == 0
        and height % tile == 0
    )

    parts = [
        (
            f'<svg '
            f'width="{svg_w:.0f}" '
            f'height="{svg_h:.0f}" '
            f'viewBox="0 0 {svg_w:.1f} {svg_h:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'style="display:block; max-width:100%; height:auto; margin:0 auto;" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'role="img" '
            f'aria-label="Rectangle {width} by {height}">'
        ),
        """
        <style>
            .dimension {
                font: 600 17px system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
                fill: #334155;
            }
            .footer {
                font: 500 13px system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
                fill: #475569;
            }
        </style>
        """,
        (
            f'<rect x="{x0:.2f}" y="{y0:.2f}" '
            f'width="{rect_w:.2f}" height="{rect_h:.2f}" '
            f'rx="3" '
            f'fill="#f8fafc" '
            f'stroke="#334155" stroke-width="2.6"/>'
        ),
    ]

    if tile is not None:
        tile_px = tile * scale
        cols = width // tile
        rows = height // tile

        covered_w = cols * tile_px
        covered_h = rows * tile_px

        # Draw every complete tile that fits.
        for row in range(rows):
            for col in range(cols):
                x = x0 + col * tile_px
                y = y0 + row * tile_px

                parts.append(
                    f'<rect '
                    f'x="{x:.2f}" y="{y:.2f}" '
                    f'width="{tile_px:.2f}" height="{tile_px:.2f}" '
                    f'fill="#dbeafe" '
                    f'stroke="#64748b" stroke-width="1.1"/>'
                )

        if not valid:
            # Right-hand remainder above the bottom strip.
            if covered_w < rect_w and covered_h > 0:
                parts.append(
                    f'<rect '
                    f'x="{x0 + covered_w:.2f}" y="{y0:.2f}" '
                    f'width="{rect_w - covered_w:.2f}" '
                    f'height="{covered_h:.2f}" '
                    f'fill="#fecaca" '
                    f'stroke="#dc2626" stroke-width="1.2"/>'
                )

            # Bottom remainder across the full width.
            if covered_h < rect_h:
                parts.append(
                    f'<rect '
                    f'x="{x0:.2f}" y="{y0 + covered_h:.2f}" '
                    f'width="{rect_w:.2f}" '
                    f'height="{rect_h - covered_h:.2f}" '
                    f'fill="#fecaca" '
                    f'stroke="#dc2626" stroke-width="1.2"/>'
                )

    # Width label.
    parts.append(
        f'<text class="dimension" '
        f'x="{x0 + rect_w / 2:.2f}" y="{y0 - 18:.2f}" '
        f'text-anchor="middle">{width} units</text>'
    )

    # Height label.
    height_label_x = x0 - 30
    height_label_y = y0 + rect_h / 2

    parts.append(
        f'<text class="dimension" '
        f'x="{height_label_x:.2f}" y="{height_label_y:.2f}" '
        f'text-anchor="middle" '
        f'transform="rotate(-90 {height_label_x:.2f} {height_label_y:.2f})">'
        f'{height} units</text>'
    )

    # Footer.
    if tile is not None:
        if valid:
            tile_count = (width // tile) * (height // tile)
            footer = f"{tile_count} square tiles of side {tile}"
        else:
            whole_tiles = (width // tile) * (height // tile)
            footer = f"{whole_tiles} whole tiles fit; the red area is left over"

        parts.append(
            f'<text class="footer" '
            f'x="{x0 + rect_w / 2:.2f}" '
            f'y="{y0 + rect_h + 31:.2f}" '
            f'text-anchor="middle">{footer}</text>'
        )

    parts.append("</svg>")

    # A few pixels of breathing room around the intrinsic SVG.
    iframe_height = int(math.ceil(svg_h + 8))

    return "".join(parts), iframe_height


def square_preview_svg(side, max_side, selected=False):
    """Small tile icon for each answer choice."""
    canvas = 76
    square_px = max(24, 62 * side / max_side)

    x = (canvas - square_px) / 2
    y = (canvas - square_px) / 2

    stroke = "#2563eb" if selected else "#64748b"
    fill = "#dbeafe" if selected else "#f1f5f9"

    return f"""
    <svg viewBox="0 0 {canvas} {canvas}"
         width="{canvas}" height="{canvas}"
         preserveAspectRatio="xMidYMid meet"
         xmlns="http://www.w3.org/2000/svg"
         role="img"
         aria-label="Square with side {side}">
        <rect
            x="{x:.1f}" y="{y:.1f}"
            width="{square_px:.1f}" height="{square_px:.1f}"
            rx="3"
            fill="{fill}"
            stroke="{stroke}"
            stroke-width="2"
        />
        <text
            x="{canvas/2}"
            y="{canvas/2 + 5}"
            text-anchor="middle"
            font-family="system-ui, sans-serif"
            font-size="14"
            font-weight="700"
            fill="#334155"
        >{side}</text>
    </svg>
    """


# ============================================================
# Initial state
# ============================================================

if "rect_width" not in st.session_state or "rect_height" not in st.session_state:
    initial_w, initial_h = random_rectangle()
    st.session_state.rect_width = initial_w
    st.session_state.rect_height = initial_h

if "selected" not in st.session_state:
    st.session_state.selected = None

if "candidates" not in st.session_state:
    st.session_state.candidates = make_candidates(
        int(st.session_state.rect_width),
        int(st.session_state.rect_height),
    )


# ============================================================
# Page
# ============================================================

st.title("GCF as Tiling")

st.write(
    "Choose the **largest square** that can tile the rectangle perfectly, "
    "with no gaps and no overlaps."
)

controls, info = st.columns([2.2, 1])

with controls:
    c1, c2, c3 = st.columns([1, 1, 1.25])

    with c1:
        st.number_input(
            "Rectangle width",
            min_value=2,
            max_value=40,
            step=1,
            key="rect_width",
            on_change=dimensions_changed,
        )

    with c2:
        st.number_input(
            "Rectangle height",
            min_value=2,
            max_value=40,
            step=1,
            key="rect_height",
            on_change=dimensions_changed,
        )

    with c3:
        st.write("")
        st.write("")
        st.button(
            "🎲 New random rectangle",
            use_container_width=True,
            on_click=new_random_rectangle,
        )


width = int(st.session_state.rect_width)
height = int(st.session_state.rect_height)
gcf = math.gcd(width, height)
selected = st.session_state.selected


with info:
    st.metric("Rectangle", f"{width} × {height}")
    st.caption(
        "Your goal: find the greatest common factor using square tiles."
    )


# ============================================================
# Main visual
# ============================================================

st.subheader("1. Test a square")

svg, svg_height = tiling_svg(width, height, selected)

components.html(
    f"""
    <div style="
        width:100%;
        display:flex;
        justify-content:center;
        align-items:center;
        box-sizing:border-box;
        padding:2px 8px;
        overflow:hidden;
    ">
        {svg}
    </div>
    """,
    height=svg_height,
    scrolling=False,
)


# ============================================================
# Feedback
# ============================================================

if selected is not None:
    is_factor = (
        width % selected == 0
        and height % selected == 0
    )

    if is_factor:
        tile_count = (width // selected) * (height // selected)

        if selected == gcf:
            st.success(
                f"✅ Correct! A {selected} × {selected} square tiles the rectangle "
                f"perfectly, and it is the **largest** possible square. "
                f"You need **{tile_count} tiles**."
            )
        else:
            st.info(
                f"👍 A {selected} × {selected} square tiles the rectangle perfectly. "
                f"You need **{tile_count} tiles**. "
                f"But a larger square also works — keep looking for the GCF."
            )

    else:
        cols = width // selected
        rows = height // selected

        whole_tiles = cols * rows
        covered_area = whole_tiles * selected * selected
        total_area = width * height
        uncovered_area = total_area - covered_area

        st.error(
            f"❌ A {selected} × {selected} square does **not** tile the rectangle "
            f"perfectly. {whole_tiles} whole tiles fit, but "
            f"**{uncovered_area} square units** remain uncovered in red."
        )


# ============================================================
# Choices
# ============================================================

st.subheader("2. Choose a square")

st.caption(
    "A smaller common factor may work, but the winning square must be the largest one."
)

candidates = st.session_state.candidates
max_candidate = max(candidates)

choice_columns = st.columns(len(candidates))

for column, side in zip(choice_columns, candidates):
    with column:
        preview = square_preview_svg(
            side,
            max_candidate,
            selected=(selected == side),
        )

        components.html(
            f"""
            <div style="
                width:100%;
                display:flex;
                justify-content:center;
                align-items:center;
            ">
                {preview}
            </div>
            """,
            height=80,
            scrolling=False,
        )

        st.button(
            f"{side} × {side}",
            key=f"candidate_{side}",
            use_container_width=True,
            type="primary" if selected == side else "secondary",
            on_click=choose_square,
            args=(side,),
        )


# ============================================================
# Hint / reset
# ============================================================

st.divider()

reset_col, hint_col = st.columns(2)

with reset_col:
    st.button(
        "↩️ Clear my choice",
        use_container_width=True,
        on_click=clear_choice,
    )

with hint_col:
    with st.popover("💡 Hint", use_container_width=True):
        common_factors = [
            n
            for n in range(1, min(width, height) + 1)
            if width % n == 0 and height % n == 0
        ]

        st.write(
            "A square tiles the rectangle perfectly only when its side length "
            "is a factor of **both** rectangle dimensions."
        )

        if st.checkbox("Show the common factors"):
            st.write(", ".join(map(str, common_factors)))

        if st.checkbox("Reveal the GCF"):
            st.write(f"**GCF = {gcf}**")
