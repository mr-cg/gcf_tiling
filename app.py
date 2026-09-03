
import math
import random
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="GCF Tiling Explorer",
    page_icon="🟦",
    layout="wide",
)

# ---------- Helpers ----------

def random_rectangle():
    """Generate a rectangle that usually has a non-trivial GCF."""
    g = random.randint(2, 8)
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    while a == b:
        b = random.randint(2, 5)

    width = g * a
    height = g * b

    # Keep dimensions classroom-friendly.
    if width > 30 or height > 30:
        return random_rectangle()
    return width, height


def make_candidates(width, height, n=7):
    """Create a shuffled set of square side lengths that always includes the GCF."""
    g = math.gcd(width, height)
    max_side = min(width, height)

    pool = list(range(1, max_side + 1))

    # Favor a useful mix around the true GCF.
    preferred = {
        1,
        g,
        max(1, g - 1),
        min(max_side, g + 1),
        max(1, g // 2),
        min(max_side, g * 2),
    }

    candidates = [x for x in preferred if 1 <= x <= max_side]

    remaining = [x for x in pool if x not in candidates]
    random.shuffle(remaining)

    while len(candidates) < min(n, len(pool)) and remaining:
        candidates.append(remaining.pop())

    # If there are too many from preferred, keep GCF and sample the rest.
    if len(candidates) > n:
        others = [x for x in candidates if x != g]
        random.shuffle(others)
        candidates = [g] + others[: n - 1]

    candidates = sorted(set(candidates))

    # Backfill if deduplication reduced the count.
    remaining = [x for x in pool if x not in candidates]
    random.shuffle(remaining)
    while len(candidates) < min(n, len(pool)) and remaining:
        candidates.append(remaining.pop())

    random.shuffle(candidates)
    return candidates


def factor_label(n):
    return f"{n} × {n}"


def tiling_svg(width, height, tile=None):
    """
    Draw the rectangle.
    - No tile: empty rectangle.
    - Valid tile: complete tiling.
    - Invalid tile: place as many whole tiles as possible and paint uncovered area red.
    """
    max_px_w = 760
    max_px_h = 430

    scale = min(max_px_w / width, max_px_h / height)
    scale = min(scale, 34)

    rect_w = width * scale
    rect_h = height * scale
    margin = 38
    svg_w = rect_w + margin * 2
    svg_h = rect_h + margin * 2 + 34

    x0 = margin
    y0 = margin

    valid = tile is not None and width % tile == 0 and height % tile == 0

    parts = [
        f'<svg viewBox="0 0 {svg_w:.1f} {svg_h:.1f}" width="100%" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Rectangle {width} by {height}">',
        '<style>'
        '.label{font:600 15px system-ui,sans-serif;fill:#334155}'
        '.small{font:500 12px system-ui,sans-serif;fill:#475569}'
        '</style>',
        f'<rect x="{x0}" y="{y0}" width="{rect_w}" height="{rect_h}" '
        'rx="3" fill="#f8fafc" stroke="#334155" stroke-width="2.4"/>',
    ]

    if tile is not None:
        tile_px = tile * scale
        cols = width // tile
        rows = height // tile
        covered_w = cols * tile_px
        covered_h = rows * tile_px

        # Draw whole tiles.
        for r in range(rows):
            for c in range(cols):
                x = x0 + c * tile_px
                y = y0 + r * tile_px
                parts.append(
                    f'<rect x="{x:.2f}" y="{y:.2f}" width="{tile_px:.2f}" '
                    f'height="{tile_px:.2f}" fill="#dbeafe" '
                    'stroke="#64748b" stroke-width="1"/>'
                )

        if not valid:
            # Uncovered right strip.
            if covered_w < rect_w:
                parts.append(
                    f'<rect x="{x0 + covered_w:.2f}" y="{y0:.2f}" '
                    f'width="{rect_w - covered_w:.2f}" height="{covered_h:.2f}" '
                    'fill="#fecaca" stroke="#dc2626" stroke-width="1.4"/>'
                )
            # Uncovered bottom strip, including bottom-right corner.
            if covered_h < rect_h:
                parts.append(
                    f'<rect x="{x0:.2f}" y="{y0 + covered_h:.2f}" '
                    f'width="{rect_w:.2f}" height="{rect_h - covered_h:.2f}" '
                    'fill="#fecaca" stroke="#dc2626" stroke-width="1.4"/>'
                )

    # Dimension labels.
    parts.extend([
        f'<text class="label" x="{x0 + rect_w/2:.2f}" y="{y0 - 12}" text-anchor="middle">'
        f'{width} units</text>',
        f'<text class="label" x="{x0 - 12}" y="{y0 + rect_h/2:.2f}" '
        f'text-anchor="middle" transform="rotate(-90 {x0 - 12} {y0 + rect_h/2:.2f})">'
        f'{height} units</text>',
    ])

    if tile is not None:
        if valid:
            count = (width // tile) * (height // tile)
            footer = f"{count} square tiles of side {tile}"
        else:
            cols = width // tile
            rows = height // tile
            count = cols * rows
            footer = f"{count} whole tiles fit, but red area remains"
        parts.append(
            f'<text class="small" x="{x0 + rect_w/2:.2f}" y="{y0 + rect_h + 28:.2f}" '
            f'text-anchor="middle">{footer}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def square_preview_svg(side, max_side, selected=False):
    size = 78
    square_px = max(28, 68 * side / max_side)
    x = (size - square_px) / 2
    y = (size - square_px) / 2
    stroke = "#2563eb" if selected else "#64748b"
    fill = "#dbeafe" if selected else "#f1f5f9"

    return f"""
    <svg viewBox="0 0 {size} {size}" width="78" height="78"
         xmlns="http://www.w3.org/2000/svg" aria-label="Square side {side}">
      <rect x="{x:.1f}" y="{y:.1f}" width="{square_px:.1f}" height="{square_px:.1f}"
            rx="3" fill="{fill}" stroke="{stroke}" stroke-width="2"/>
      <text x="39" y="43" text-anchor="middle"
            font-family="system-ui,sans-serif" font-size="14" font-weight="700"
            fill="#334155">{side}</text>
    </svg>
    """


# ---------- Session state ----------

if "width" not in st.session_state or "height" not in st.session_state:
    w, h = random_rectangle()
    st.session_state.width = w
    st.session_state.height = h

if "candidates" not in st.session_state:
    st.session_state.candidates = make_candidates(
        st.session_state.width, st.session_state.height
    )

if "selected" not in st.session_state:
    st.session_state.selected = None

if "dims_signature" not in st.session_state:
    st.session_state.dims_signature = (
        st.session_state.width,
        st.session_state.height,
    )


# ---------- Header ----------

st.title("GCF as Tiling")
st.write(
    "Choose the **largest square** that can tile the rectangle perfectly, "
    "with no gaps and no overlaps."
)

controls, info = st.columns([2, 1])

with controls:
    c1, c2, c3 = st.columns([1, 1, 1.2])

    with c1:
        width = st.number_input(
            "Rectangle width",
            min_value=2,
            max_value=40,
            step=1,
            key="width",
        )

    with c2:
        height = st.number_input(
            "Rectangle height",
            min_value=2,
            max_value=40,
            step=1,
            key="height",
        )

    with c3:
        st.write("")
        st.write("")
        if st.button("🎲 New random rectangle", use_container_width=True):
            w, h = random_rectangle()
            st.session_state.width = w
            st.session_state.height = h
            st.session_state.candidates = make_candidates(w, h)
            st.session_state.selected = None
            st.session_state.dims_signature = (w, h)
            st.rerun()

# Regenerate candidates if dimensions changed manually.
signature = (int(width), int(height))
if signature != st.session_state.dims_signature:
    st.session_state.candidates = make_candidates(int(width), int(height))
    st.session_state.selected = None
    st.session_state.dims_signature = signature
    st.rerun()

gcf = math.gcd(int(width), int(height))

with info:
    st.metric("Rectangle", f"{int(width)} × {int(height)}")
    st.caption("Your goal: find the greatest common factor using square tiles.")


# ---------- Main rectangle ----------

st.subheader("1. Test a square")

selected = st.session_state.selected

svg = tiling_svg(int(width), int(height), selected)
components.html(
    f"""
    <div style="display:flex;justify-content:center;align-items:center;
                width:100%;padding:4px 0 10px 0;">
        {svg}
    </div>
    """,
    height=500,
    scrolling=False,
)

# ---------- Feedback ----------

if selected is not None:
    is_factor = (int(width) % selected == 0) and (int(height) % selected == 0)

    if is_factor:
        tile_count = (int(width) // selected) * (int(height) // selected)

        if selected == gcf:
            st.success(
                f"✅ Correct! A {selected} × {selected} square tiles the rectangle "
                f"perfectly, and it is the **largest** possible square. "
                f"You need **{tile_count} tiles**."
            )
        else:
            st.info(
                f"👍 A {selected} × {selected} square **does** tile the rectangle "
                f"perfectly. You need **{tile_count} tiles**. "
                f"But it is not the largest possible square — try a larger factor."
            )
    else:
        cols = int(width) // selected
        rows = int(height) // selected
        whole_tiles = cols * rows

        covered_area = whole_tiles * selected * selected
        total_area = int(width) * int(height)
        uncovered_area = total_area - covered_area

        st.error(
            f"❌ A {selected} × {selected} square does not tile the rectangle perfectly. "
            f"{whole_tiles} whole tiles fit, but **{uncovered_area} square units** "
            f"remain uncovered (shown in red)."
        )


# ---------- Candidate squares ----------

st.subheader("2. Choose a square")
st.caption(
    "A smaller common factor may work, but the winning square must be the largest one."
)

candidates = st.session_state.candidates
max_candidate = max(candidates)

# Responsive-ish rows of at most 7 columns.
cols = st.columns(len(candidates))

for i, side in enumerate(candidates):
    with cols[i]:
        preview = square_preview_svg(
            side,
            max_candidate,
            selected=(selected == side),
        )
        components.html(
            f'<div style="display:flex;justify-content:center">{preview}</div>',
            height=84,
            scrolling=False,
        )

        if st.button(
            f"{side} × {side}",
            key=f"candidate_{side}",
            use_container_width=True,
            type="primary" if selected == side else "secondary",
        ):
            st.session_state.selected = side
            st.rerun()


# ---------- Optional hint / reset ----------

st.divider()
h1, h2 = st.columns([1, 1])

with h1:
    if st.button("↩️ Clear my choice", use_container_width=True):
        st.session_state.selected = None
        st.rerun()

with h2:
    with st.popover("💡 Hint"):
        common_factors = [
            n
            for n in range(1, min(int(width), int(height)) + 1)
            if int(width) % n == 0 and int(height) % n == 0
        ]
        st.write(
            "A square tiles the rectangle perfectly only when its side length "
            "is a factor of **both** rectangle dimensions."
        )
        if st.checkbox("Show the common factors"):
            st.write(", ".join(map(str, common_factors)))
        if st.checkbox("Reveal the GCF"):
            st.write(f"**GCF = {gcf}**")
