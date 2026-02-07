"""DearPyGui test app for nitro-image library."""

import io
import sys
import array
from pathlib import Path

import dearpygui.dearpygui as dpg
from PIL import Image as PILImage

# Add src to path so we can import nitro_img without installing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nitro_img import Image, BatchImage  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DISPLAY_W, DISPLAY_H = 480, 360
TEX_W, TEX_H = DISPLAY_W, DISPLAY_H
ANCHORS = [
    "center", "top-left", "top-right", "bottom-left",
    "bottom-right", "top", "bottom", "left", "right",
]
POSITIONS = ANCHORS + ["tiled"]

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
state = {
    "source_path": None,
    "source_bytes": None,
    "original_pil": None,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def pil_to_dpg(pil_img):
    """Convert PIL Image to flat RGBA float array sized for display."""
    img = pil_img.copy()
    img.thumbnail((TEX_W, TEX_H))
    canvas = PILImage.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    x = (TEX_W - img.width) // 2
    y = (TEX_H - img.height) // 2
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    canvas.paste(img, (x, y))
    raw = canvas.tobytes()
    buf = array.array("f", [0.0] * (TEX_W * TEX_H * 4))
    for i in range(len(raw)):
        buf[i] = raw[i] / 255.0
    return buf


def blank_texture():
    return array.array("f", [0.1, 0.1, 0.1, 1.0] * (TEX_W * TEX_H))


def update_original(pil_img):
    dpg.set_value("tex_original", pil_to_dpg(pil_img))
    w, h = pil_img.size
    fmt = pil_img.format or "?"
    dpg.set_value("lbl_orig_info", f"{w}x{h}  {fmt}  {pil_img.mode}")


def update_processed(pil_img, size_bytes=None):
    dpg.set_value("tex_processed", pil_to_dpg(pil_img))
    w, h = pil_img.size
    info = f"{w}x{h}"
    if size_bytes is not None:
        info += f"  {size_bytes // 1024}KB"
    dpg.set_value("lbl_proc_info", info)


def status(msg):
    dpg.set_value("lbl_status", str(msg))


def fresh_image():
    """Return a fresh Image from stored source bytes."""
    if state["source_bytes"] is None:
        status("No image loaded")
        return None
    return Image.from_bytes(state["source_bytes"])


def apply_and_show(img):
    """Execute pipeline on Image instance and update processed preview."""
    try:
        data = img.png().to_bytes()
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status("Done")
    except Exception as e:
        status(f"Error: {e}")


def make_sample_image():
    """Generate a colorful 800x600 sample image."""
    img = PILImage.new("RGB", (800, 600))
    pixels = img.load()
    for y in range(600):
        for x in range(800):
            pixels[x, y] = (
                int(255 * x / 800),
                int(255 * y / 600),
                int(255 * (1 - x / 800)),
            )
    return img


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

def cb_load_file(sender, app_data):
    selections = app_data.get("selections", {})
    if not selections:
        return
    path = list(selections.values())[0]
    try:
        state["source_path"] = path
        state["source_bytes"] = Path(path).read_bytes()
        pil = PILImage.open(io.BytesIO(state["source_bytes"]))
        state["original_pil"] = pil.copy()
        update_original(pil)
        update_processed(pil, len(state["source_bytes"]))
        status(f"Loaded: {Path(path).name}")
    except Exception as e:
        status(f"Load error: {e}")


def cb_load_sample(sender, app_data):
    pil = make_sample_image()
    buf = io.BytesIO()
    pil.save(buf, "PNG")
    state["source_bytes"] = buf.getvalue()
    state["source_path"] = None
    state["original_pil"] = pil.copy()
    update_original(pil)
    update_processed(pil, len(state["source_bytes"]))
    status("Loaded sample image (800x600)")


def cb_reset(sender, app_data):
    if state["original_pil"]:
        update_processed(state["original_pil"])
    status("Reset to original")


# -- Resize callbacks --

def cb_resize(sender, app_data):
    img = fresh_image()
    if not img:
        return
    w = int(dpg.get_value("inp_resize_w"))
    h = int(dpg.get_value("inp_resize_h"))
    up = dpg.get_value("chk_upscale")
    if w > 0:
        img = img.resize(width=w, height=h if h > 0 else None, allow_upscale=up)
    apply_and_show(img)


def cb_thumbnail(sender, app_data):
    img = fresh_image()
    if not img:
        return
    w = int(dpg.get_value("inp_thumb_w"))
    h = int(dpg.get_value("inp_thumb_h"))
    img = img.thumbnail(w, h)
    apply_and_show(img)


def cb_cover(sender, app_data):
    img = fresh_image()
    if not img:
        return
    w = int(dpg.get_value("inp_cover_w"))
    h = int(dpg.get_value("inp_cover_h"))
    img = img.cover(w, h)
    apply_and_show(img)


def cb_contain(sender, app_data):
    img = fresh_image()
    if not img:
        return
    w = int(dpg.get_value("inp_contain_w"))
    h = int(dpg.get_value("inp_contain_h"))
    bg = dpg.get_value("inp_contain_bg")
    img = img.contain(w, h, bg=bg)
    apply_and_show(img)


# -- Crop & Transform callbacks --

def cb_crop(sender, app_data):
    img = fresh_image()
    if not img:
        return
    w = int(dpg.get_value("inp_crop_w"))
    h = int(dpg.get_value("inp_crop_h"))
    anchor = dpg.get_value("combo_anchor")
    img = img.crop(w, h, anchor=anchor)
    apply_and_show(img)


def cb_rotate(sender, app_data):
    img = fresh_image()
    if not img:
        return
    deg = dpg.get_value("slider_rotate")
    expand = dpg.get_value("chk_expand")
    img = img.rotate(deg, expand=expand)
    apply_and_show(img)


def cb_flip(sender, app_data):
    img = fresh_image()
    if img:
        apply_and_show(img.flip())


def cb_mirror(sender, app_data):
    img = fresh_image()
    if img:
        apply_and_show(img.mirror())


def cb_grayscale(sender, app_data):
    img = fresh_image()
    if img:
        apply_and_show(img.grayscale())


# -- Adjust callbacks --

def cb_adjust(sender, app_data):
    img = fresh_image()
    if not img:
        return
    b = dpg.get_value("slider_brightness")
    c = dpg.get_value("slider_contrast")
    s = dpg.get_value("slider_saturation")
    sh = dpg.get_value("slider_sharpen")
    bl = dpg.get_value("slider_blur")
    if b != 1.0:
        img = img.brightness(b)
    if c != 1.0:
        img = img.contrast(c)
    if s != 1.0:
        img = img.saturation(s)
    if sh != 1.0:
        img = img.sharpen(sh)
    if bl > 0.0:
        img = img.blur(bl)
    apply_and_show(img)


# -- Effects callbacks --

def cb_sepia(sender, app_data):
    img = fresh_image()
    if img:
        apply_and_show(img.sepia())


def cb_rounded(sender, app_data):
    img = fresh_image()
    if not img:
        return
    r = int(dpg.get_value("slider_rounded"))
    apply_and_show(img.rounded_corners(r))


# -- Overlay callbacks --

def cb_watermark_file(sender, app_data):
    selections = app_data.get("selections", {})
    if selections:
        path = list(selections.values())[0]
        dpg.set_value("inp_wm_path", path)


def cb_watermark(sender, app_data):
    img = fresh_image()
    if not img:
        return
    wm_path = dpg.get_value("inp_wm_path")
    if not wm_path or not Path(wm_path).exists():
        status("Select a watermark image first")
        return
    pos = dpg.get_value("combo_wm_pos")
    opacity = dpg.get_value("slider_wm_opacity")
    margin = int(dpg.get_value("inp_wm_margin"))
    img = img.watermark(wm_path, position=pos, opacity=opacity, margin=margin)
    apply_and_show(img)


def cb_text_overlay(sender, app_data):
    img = fresh_image()
    if not img:
        return
    text = dpg.get_value("inp_text")
    pos = dpg.get_value("combo_text_pos")
    size = int(dpg.get_value("slider_text_size"))
    c = dpg.get_value("picker_text_color")
    color = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
    opacity = dpg.get_value("slider_text_opacity")
    margin = int(dpg.get_value("inp_text_margin"))
    img = img.text_overlay(
        text, position=pos, font_size=size,
        color=color, opacity=opacity, margin=margin,
    )
    apply_and_show(img)


# -- Format & Output callbacks --

def cb_save_file(sender, app_data):
    selections = app_data.get("file_path_name", "")
    if not selections:
        return
    img = fresh_image()
    if not img:
        return
    fmt_name = dpg.get_value("radio_format")
    q = int(dpg.get_value("slider_quality"))
    if fmt_name == "JPEG":
        img = img.jpeg(quality=q)
    elif fmt_name == "PNG":
        img = img.png()
    elif fmt_name == "WebP":
        img = img.webp(quality=q)
    elif fmt_name == "GIF":
        img = img.gif()
    elif fmt_name == "Auto":
        img = img.auto_format()
    try:
        path = img.save(selections)
        status(f"Saved: {path} ({path.stat().st_size // 1024}KB)")
    except Exception as e:
        status(f"Save error: {e}")


def cb_to_bytes(sender, app_data):
    img = fresh_image()
    if not img:
        return
    fmt_name = dpg.get_value("radio_format")
    q = int(dpg.get_value("slider_quality"))
    if fmt_name == "JPEG":
        img = img.jpeg(quality=q)
    elif fmt_name == "PNG":
        img = img.png()
    elif fmt_name == "WebP":
        img = img.webp(quality=q)
    elif fmt_name == "GIF":
        img = img.gif()
    else:
        img = img.auto_format()
    try:
        data = img.to_bytes()
        status(f"to_bytes(): {len(data)} bytes ({len(data) // 1024}KB)")
    except Exception as e:
        status(f"Error: {e}")


def cb_to_base64(sender, app_data):
    img = fresh_image()
    if not img:
        return
    img = img.png()
    try:
        b64 = img.to_base64()
        status(f"to_base64(): {len(b64)} chars")
    except Exception as e:
        status(f"Error: {e}")


def cb_to_data_uri(sender, app_data):
    img = fresh_image()
    if not img:
        return
    img = img.png()
    try:
        uri = img.to_data_uri()
        status(f"to_data_uri(): {len(uri)} chars (data:image/png;base64,...)")
    except Exception as e:
        status(f"Error: {e}")


def cb_to_response(sender, app_data):
    img = fresh_image()
    if not img:
        return
    img = img.png()
    try:
        resp = img.to_response()
        status(
            f"to_response(): content_type={resp['content_type']}, "
            f"content_length={resp['content_length']}"
        )
    except Exception as e:
        status(f"Error: {e}")


# -- Placeholder callbacks --

def cb_metadata(sender, app_data):
    img = fresh_image()
    if not img:
        return
    meta = img.get_metadata()
    lines = [f"{k}: {v}" for k, v in meta.items() if k != "exif"]
    if "exif" in meta:
        lines.append(f"exif: {len(meta['exif'])} tags")
    status("  |  ".join(lines))


def cb_lqip(sender, app_data):
    img = fresh_image()
    if not img:
        return
    w = int(dpg.get_value("inp_lqip_w"))
    uri = img.lqip(width=w)
    status(f"LQIP: {len(uri)} chars")


def cb_dominant_color(sender, app_data):
    img = fresh_image()
    if not img:
        return
    color = img.dominant_color()
    status(f"Dominant color: {color}")


def cb_color_palette(sender, app_data):
    img = fresh_image()
    if not img:
        return
    count = int(dpg.get_value("inp_palette_count"))
    colors = img.color_palette(count=count)
    status(f"Palette: {', '.join(colors)}")


def cb_svg_placeholder(sender, app_data):
    img = fresh_image()
    if not img:
        return
    svg = img.svg_placeholder()
    status(f"SVG placeholder: {len(svg)} chars")


def cb_blurhash(sender, app_data):
    img = fresh_image()
    if not img:
        return
    try:
        bh = img.blurhash()
        status(f"BlurHash: {bh}")
    except ImportError:
        status("blurhash-python not installed (pip install nitro-image[blur])")
    except Exception as e:
        status(f"Error: {e}")


# -- Optimize & Responsive callbacks --

def cb_optimize(sender, app_data):
    img = fresh_image()
    if not img:
        return
    target = int(dpg.get_value("inp_target_kb"))
    try:
        data = img.optimize(target_kb=target)
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status(f"Optimized to {len(data) // 1024}KB (target: {target}KB)")
    except Exception as e:
        status(f"Error: {e}")


def cb_responsive(sender, app_data):
    img = fresh_image()
    if not img:
        return
    widths_str = dpg.get_value("inp_resp_widths")
    try:
        widths = [int(w.strip()) for w in widths_str.split(",") if w.strip()]
    except ValueError:
        status("Invalid widths - use comma-separated numbers")
        return
    try:
        result = img.responsive(widths)
        parts = [f"{w}px: {len(d) // 1024}KB" for w, d in sorted(result.items())]
        status(f"Responsive: {', '.join(parts)}")
    except Exception as e:
        status(f"Error: {e}")


# -- Presets callbacks --

def cb_preset_thumbnail(sender, app_data):
    if state["source_bytes"] is None:
        status("No image loaded")
        return
    try:
        data = Image.preset.thumbnail(state["source_bytes"])
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status(f"Preset thumbnail: {pil.width}x{pil.height}")
    except Exception as e:
        status(f"Error: {e}")


def cb_preset_avatar(sender, app_data):
    if state["source_bytes"] is None:
        status("No image loaded")
        return
    try:
        data = Image.preset.avatar(state["source_bytes"])
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status(f"Preset avatar: {pil.width}x{pil.height}")
    except Exception as e:
        status(f"Error: {e}")


def cb_preset_og(sender, app_data):
    if state["source_bytes"] is None:
        status("No image loaded")
        return
    try:
        data = Image.preset.og_image(state["source_bytes"])
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status(f"Preset OG image: {pil.width}x{pil.height}")
    except Exception as e:
        status(f"Error: {e}")


def cb_preset_banner(sender, app_data):
    if state["source_bytes"] is None:
        status("No image loaded")
        return
    try:
        data = Image.preset.banner(state["source_bytes"])
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status(f"Preset banner: {pil.width}x{pil.height}")
    except Exception as e:
        status(f"Error: {e}")


def cb_preset_avatar_placeholder(sender, app_data):
    initials = dpg.get_value("inp_initials")
    if not initials:
        status("Enter initials")
        return
    try:
        data = Image.preset.avatar_placeholder(initials)
        pil = PILImage.open(io.BytesIO(data))
        update_processed(pil, len(data))
        status(f"Avatar placeholder: {pil.width}x{pil.height}")
    except Exception as e:
        status(f"Error: {e}")


# -- Batch callback --

def cb_batch(sender, app_data):
    pattern = dpg.get_value("inp_batch_glob")
    output = dpg.get_value("inp_batch_output")
    parallel = dpg.get_value("chk_batch_parallel")
    if not pattern or not output:
        status("Enter glob pattern and output pattern")
        return
    try:
        results = (
            BatchImage(pattern)
            .resize(800)
            .jpeg(quality=80)
            .save(output, parallel=parallel)
        )
        status(f"Batch: processed {len(results)} files")
    except Exception as e:
        status(f"Batch error: {e}")


# ---------------------------------------------------------------------------
# Build UI
# ---------------------------------------------------------------------------

def build_ui():
    dpg.create_context()

    # -- Texture registry --
    with dpg.texture_registry():
        dpg.add_dynamic_texture(
            TEX_W, TEX_H, blank_texture(), tag="tex_original",
        )
        dpg.add_dynamic_texture(
            TEX_W, TEX_H, blank_texture(), tag="tex_processed",
        )

    # -- File dialogs --
    with dpg.file_dialog(
        directory_selector=False, show=False,
        callback=cb_load_file, tag="dlg_load",
        width=700, height=400,
    ):
        dpg.add_file_extension(".png")
        dpg.add_file_extension(".jpg")
        dpg.add_file_extension(".jpeg")
        dpg.add_file_extension(".webp")
        dpg.add_file_extension(".gif")
        dpg.add_file_extension(".bmp")
        dpg.add_file_extension(".*")

    with dpg.file_dialog(
        directory_selector=False, show=False,
        callback=cb_watermark_file, tag="dlg_watermark",
        width=700, height=400,
    ):
        dpg.add_file_extension(".png")
        dpg.add_file_extension(".jpg")
        dpg.add_file_extension(".*")

    with dpg.file_dialog(
        directory_selector=False, show=False,
        callback=cb_save_file, tag="dlg_save",
        width=700, height=400,
    ):
        dpg.add_file_extension(".png")
        dpg.add_file_extension(".jpg")
        dpg.add_file_extension(".webp")
        dpg.add_file_extension(".gif")
        dpg.add_file_extension(".*")

    # -- Main window --
    with dpg.window(tag="main_window"):

        # -- Top bar --
        with dpg.group(horizontal=True):
            dpg.add_button(label="Load Image", callback=lambda: dpg.show_item("dlg_load"))
            dpg.add_button(label="Load Sample", callback=cb_load_sample)
            dpg.add_button(label="Reset", callback=cb_reset)
            dpg.add_spacer(width=20)
            dpg.add_text("", tag="lbl_status")

        dpg.add_separator()

        # -- Image previews --
        with dpg.group(horizontal=True):
            with dpg.child_window(width=TEX_W + 20, height=TEX_H + 40):
                dpg.add_text("Original")
                dpg.add_image("tex_original")
                dpg.add_text("", tag="lbl_orig_info")
            dpg.add_spacer(width=10)
            with dpg.child_window(width=TEX_W + 20, height=TEX_H + 40):
                dpg.add_text("Processed")
                dpg.add_image("tex_processed")
                dpg.add_text("", tag="lbl_proc_info")

        dpg.add_separator()

        # -- Tabs --
        with dpg.tab_bar():

            # ---- Tab: Resize ----
            with dpg.tab(label="Resize"):
                with dpg.group(horizontal=True):
                    with dpg.child_window(width=250, height=200):
                        dpg.add_text("Resize")
                        dpg.add_input_int(label="Width", default_value=400, tag="inp_resize_w", width=120)
                        dpg.add_input_int(label="Height", default_value=0, tag="inp_resize_h", width=120)
                        dpg.add_checkbox(label="Allow upscale", tag="chk_upscale")
                        dpg.add_button(label="Apply Resize", callback=cb_resize)

                    with dpg.child_window(width=250, height=200):
                        dpg.add_text("Thumbnail")
                        dpg.add_input_int(label="Width", default_value=200, tag="inp_thumb_w", width=120)
                        dpg.add_input_int(label="Height", default_value=200, tag="inp_thumb_h", width=120)
                        dpg.add_button(label="Apply Thumbnail", callback=cb_thumbnail)

                    with dpg.child_window(width=250, height=200):
                        dpg.add_text("Cover")
                        dpg.add_input_int(label="Width", default_value=400, tag="inp_cover_w", width=120)
                        dpg.add_input_int(label="Height", default_value=400, tag="inp_cover_h", width=120)
                        dpg.add_button(label="Apply Cover", callback=cb_cover)

                    with dpg.child_window(width=250, height=200):
                        dpg.add_text("Contain")
                        dpg.add_input_int(label="Width", default_value=400, tag="inp_contain_w", width=120)
                        dpg.add_input_int(label="Height", default_value=400, tag="inp_contain_h", width=120)
                        dpg.add_input_text(label="BG", default_value="white", tag="inp_contain_bg", width=120)
                        dpg.add_button(label="Apply Contain", callback=cb_contain)

            # ---- Tab: Crop & Transform ----
            with dpg.tab(label="Crop & Transform"):
                with dpg.group(horizontal=True):
                    with dpg.child_window(width=300, height=200):
                        dpg.add_text("Crop")
                        dpg.add_input_int(label="Width", default_value=300, tag="inp_crop_w", width=120)
                        dpg.add_input_int(label="Height", default_value=300, tag="inp_crop_h", width=120)
                        dpg.add_combo(ANCHORS, label="Anchor", default_value="center", tag="combo_anchor", width=150)
                        dpg.add_button(label="Apply Crop", callback=cb_crop)

                    with dpg.child_window(width=300, height=200):
                        dpg.add_text("Rotate")
                        dpg.add_slider_float(
                            label="Degrees", default_value=0, min_value=0,
                            max_value=360, tag="slider_rotate", width=200,
                        )
                        dpg.add_checkbox(label="Expand canvas", default_value=True, tag="chk_expand")
                        dpg.add_button(label="Apply Rotate", callback=cb_rotate)

                    with dpg.child_window(width=200, height=200):
                        dpg.add_text("Transform")
                        dpg.add_button(label="Flip (vertical)", callback=cb_flip)
                        dpg.add_button(label="Mirror (horizontal)", callback=cb_mirror)
                        dpg.add_button(label="Grayscale", callback=cb_grayscale)

            # ---- Tab: Adjustments ----
            with dpg.tab(label="Adjustments"):
                dpg.add_slider_float(
                    label="Brightness", default_value=1.0, min_value=0.0,
                    max_value=3.0, tag="slider_brightness", width=400,
                )
                dpg.add_slider_float(
                    label="Contrast", default_value=1.0, min_value=0.0,
                    max_value=3.0, tag="slider_contrast", width=400,
                )
                dpg.add_slider_float(
                    label="Saturation", default_value=1.0, min_value=0.0,
                    max_value=3.0, tag="slider_saturation", width=400,
                )
                dpg.add_slider_float(
                    label="Sharpen", default_value=1.0, min_value=0.0,
                    max_value=5.0, tag="slider_sharpen", width=400,
                )
                dpg.add_slider_float(
                    label="Blur", default_value=0.0, min_value=0.0,
                    max_value=10.0, tag="slider_blur", width=400,
                )
                dpg.add_button(label="Apply Adjustments", callback=cb_adjust)

            # ---- Tab: Effects ----
            with dpg.tab(label="Effects"):
                dpg.add_button(label="Apply Sepia", callback=cb_sepia)
                dpg.add_spacer(height=10)
                dpg.add_slider_int(
                    label="Corner radius", default_value=20, min_value=1,
                    max_value=200, tag="slider_rounded", width=300,
                )
                dpg.add_button(label="Apply Rounded Corners", callback=cb_rounded)

            # ---- Tab: Overlay ----
            with dpg.tab(label="Overlay"):
                with dpg.group(horizontal=True):
                    with dpg.child_window(width=450, height=200):
                        dpg.add_text("Watermark")
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(
                                label="", tag="inp_wm_path",
                                width=250, hint="watermark image path",
                            )
                            dpg.add_button(
                                label="Browse",
                                callback=lambda: dpg.show_item("dlg_watermark"),
                            )
                        dpg.add_combo(
                            POSITIONS, label="Position",
                            default_value="bottom-right", tag="combo_wm_pos", width=150,
                        )
                        dpg.add_slider_float(
                            label="Opacity", default_value=0.3, min_value=0.0,
                            max_value=1.0, tag="slider_wm_opacity", width=200,
                        )
                        dpg.add_input_int(label="Margin", default_value=10, tag="inp_wm_margin", width=100)
                        dpg.add_button(label="Apply Watermark", callback=cb_watermark)

                    with dpg.child_window(width=450, height=200):
                        dpg.add_text("Text Overlay")
                        dpg.add_input_text(
                            label="Text", default_value="Sample",
                            tag="inp_text", width=200,
                        )
                        dpg.add_combo(
                            POSITIONS, label="Position",
                            default_value="bottom-right", tag="combo_text_pos", width=150,
                        )
                        dpg.add_slider_int(
                            label="Size", default_value=24, min_value=8,
                            max_value=120, tag="slider_text_size", width=200,
                        )
                        dpg.add_color_edit(
                            label="Color", default_value=(255, 255, 255, 255),
                            tag="picker_text_color", no_alpha=True, width=200,
                        )
                        dpg.add_slider_float(
                            label="Opacity", default_value=1.0, min_value=0.0,
                            max_value=1.0, tag="slider_text_opacity", width=200,
                        )
                        dpg.add_input_int(label="Margin", default_value=10, tag="inp_text_margin", width=100)
                        dpg.add_button(label="Apply Text", callback=cb_text_overlay)

            # ---- Tab: Format & Output ----
            with dpg.tab(label="Format & Output"):
                with dpg.group(horizontal=True):
                    with dpg.child_window(width=250, height=180):
                        dpg.add_text("Format")
                        dpg.add_radio_button(
                            ["JPEG", "PNG", "WebP", "GIF", "Auto"],
                            default_value="PNG", tag="radio_format",
                        )
                        dpg.add_slider_int(
                            label="Quality", default_value=85, min_value=1,
                            max_value=100, tag="slider_quality", width=150,
                        )

                    with dpg.child_window(width=300, height=180):
                        dpg.add_text("Output")
                        dpg.add_button(
                            label="Save As...",
                            callback=lambda: dpg.show_item("dlg_save"),
                        )
                        dpg.add_button(label="to_bytes()", callback=cb_to_bytes)
                        dpg.add_button(label="to_base64()", callback=cb_to_base64)
                        dpg.add_button(label="to_data_uri()", callback=cb_to_data_uri)
                        dpg.add_button(label="to_response()", callback=cb_to_response)

            # ---- Tab: Placeholders ----
            with dpg.tab(label="Placeholders"):
                dpg.add_button(label="Get Metadata", callback=cb_metadata)
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_input_int(
                        label="LQIP width", default_value=20,
                        tag="inp_lqip_w", width=80,
                    )
                    dpg.add_button(label="Generate LQIP", callback=cb_lqip)
                dpg.add_button(label="Dominant Color", callback=cb_dominant_color)
                with dpg.group(horizontal=True):
                    dpg.add_input_int(
                        label="Palette count", default_value=5,
                        tag="inp_palette_count", width=80,
                    )
                    dpg.add_button(label="Color Palette", callback=cb_color_palette)
                dpg.add_button(label="SVG Placeholder", callback=cb_svg_placeholder)
                dpg.add_button(label="BlurHash", callback=cb_blurhash)

            # ---- Tab: Optimize & Responsive ----
            with dpg.tab(label="Optimize"):
                with dpg.group(horizontal=True):
                    with dpg.child_window(width=300, height=120):
                        dpg.add_text("Optimize")
                        dpg.add_input_int(
                            label="Target KB", default_value=200,
                            tag="inp_target_kb", width=100,
                        )
                        dpg.add_button(label="Optimize", callback=cb_optimize)

                    with dpg.child_window(width=400, height=120):
                        dpg.add_text("Responsive")
                        dpg.add_input_text(
                            label="Widths (comma-sep)",
                            default_value="320, 640, 1024, 1920",
                            tag="inp_resp_widths", width=250,
                        )
                        dpg.add_button(label="Generate Responsive", callback=cb_responsive)

            # ---- Tab: Presets ----
            with dpg.tab(label="Presets"):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Thumbnail (200x200)", callback=cb_preset_thumbnail)
                    dpg.add_button(label="Avatar (128px circle)", callback=cb_preset_avatar)
                    dpg.add_button(label="OG Image (1200x630)", callback=cb_preset_og)
                    dpg.add_button(label="Banner (1920x400)", callback=cb_preset_banner)
                dpg.add_separator()
                dpg.add_text("Avatar Placeholder")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        label="Initials", default_value="SN",
                        tag="inp_initials", width=60,
                    )
                    dpg.add_button(
                        label="Generate Avatar Placeholder",
                        callback=cb_preset_avatar_placeholder,
                    )

            # ---- Tab: Batch ----
            with dpg.tab(label="Batch"):
                dpg.add_input_text(
                    label="Glob pattern",
                    default_value="*.jpg",
                    tag="inp_batch_glob", width=400,
                )
                dpg.add_input_text(
                    label="Output pattern",
                    default_value="output/{name}.webp",
                    tag="inp_batch_output", width=400,
                )
                dpg.add_checkbox(label="Parallel", tag="chk_batch_parallel")
                dpg.add_button(label="Process Batch", callback=cb_batch)

    # -- Viewport --
    dpg.create_viewport(
        title="Nitro Image Test App", width=1050, height=900,
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    build_ui()
