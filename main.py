import zipfile, os, io, re
from PIL import Image
from pptx import Presentation
from pptx.util import Inches

# path
zip_path = ""  # file tujuan
out_path = ""  # tempat hasil file disimpan

image_exts = {".png", ".jpg", ".jpeg"}
with zipfile.ZipFile(zip_path, "r") as z:
    candidates = []
    for info in z.infolist():
        if info.is_dir():
            continue
        ext = os.path.splitext(info.filename)[1].lower()
        if ext not in image_exts:
            continue
        base = os.path.basename(info.filename)
        if base.startswith(".") or "__MACOSX" in info.filename:
            continue
        candidates.append(info.filename)

    def natural_key(path):
        parts = re.split(r"(\d+)", os.path.basename(path))
        return [int(p) if p.isdigit() else p.lower() for p in parts]

    candidates.sort(key=natural_key)

    if not candidates:
        raise ValueError("can't find PNG/JPG in the ZIP.")

    first = Image.open(io.BytesIO(z.read(candidates[0])))
    first_w, first_h = first.size

    prs = Presentation()
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(13.333333 * first_h / first_w)
    blank_layout = prs.slide_layouts[6]

    for filename in candidates:
        image_data = io.BytesIO(z.read(filename))
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(
            image_data, 0, 0,
            width=prs.slide_width,
            height=prs.slide_height
        )

    prs.save(out_path)

print(f"succeed make {len(candidates)} slide.")
print(f"Resolution first image: {first_w} × {first_h} px")
print(f"File out: {out_path}")
