import textwrap


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT_MARGIN = 54
RIGHT_MARGIN = 54
TOP_MARGIN = 784
BOTTOM_MARGIN = 60
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

BODY_COLOR = (0.15, 0.20, 0.29)
MUTED_COLOR = (0.39, 0.45, 0.55)
ACCENT_COLOR = (0.08, 0.45, 0.51)


def _escape_pdf_text(value):
  return (
    value.replace("\\", "\\\\")
    .replace("(", "\\(")
    .replace(")", "\\)")
  )


def _wrap_text(value, font_size, width=CONTENT_WIDTH):
  max_chars = max(28, int(width / (font_size * 0.54)))
  return textwrap.wrap(
    value,
    width=max_chars,
    break_long_words=False,
    break_on_hyphens=False,
  ) or [""]


class PdfWriter:
  def __init__(self):
    self.objects = []

  def reserve(self):
    self.objects.append(None)
    return len(self.objects)

  def add(self, content):
    self.objects.append(content)
    return len(self.objects)

  def set(self, object_id, content):
    self.objects[object_id - 1] = content

  def build(self, root_id):
    payload = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0]

    for index, content in enumerate(self.objects, start=1):
      offsets.append(len(payload))
      payload += f"{index} 0 obj\n".encode("ascii")
      payload += content
      payload += b"\nendobj\n"

    startxref = len(payload)
    payload += f"xref\n0 {len(self.objects) + 1}\n".encode("ascii")
    payload += b"0000000000 65535 f \n"

    for offset in offsets[1:]:
      payload += f"{offset:010d} 00000 n \n".encode("ascii")

    payload += (
      f"trailer\n<< /Size {len(self.objects) + 1} /Root {root_id} 0 R >>\n"
      f"startxref\n{startxref}\n%%EOF"
    ).encode("ascii")
    return payload


class CvPdf:
  def __init__(self):
    self.pages = [[]]
    self.y = TOP_MARGIN

  def _new_page(self):
    self.pages.append([])
    self.y = TOP_MARGIN

  def _ensure_space(self, amount):
    if self.y - amount < BOTTOM_MARGIN:
      self._new_page()

  def spacer(self, amount):
    self._ensure_space(amount)
    self.y -= amount

  def line(self, text, size=11, font="F1", color=BODY_COLOR, leading=None, x=LEFT_MARGIN):
    if leading is None:
      leading = size + 4
    self._ensure_space(leading)
    escaped = _escape_pdf_text(text)
    self.pages[-1].append(
      f"BT /{font} {size} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg "
      f"1 0 0 1 {x} {self.y:.1f} Tm ({escaped}) Tj ET"
    )
    self.y -= leading

  def paragraph(self, text, size=11, font="F1", color=BODY_COLOR, width=CONTENT_WIDTH, x=LEFT_MARGIN, leading=None):
    if leading is None:
      leading = size + 4
    for line in _wrap_text(text, size, width):
      self.line(line, size=size, font=font, color=color, x=x, leading=leading)

  def rule(self, color=MUTED_COLOR):
    self._ensure_space(16)
    y = self.y + 2
    self.pages[-1].append(
      f"q {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG 1 w "
      f"{LEFT_MARGIN} {y:.1f} m {PAGE_WIDTH - RIGHT_MARGIN} {y:.1f} l S Q"
    )
    self.y -= 14

  def bullet_list(self, entries):
    for entry in entries:
      lines = _wrap_text(entry, 11, CONTENT_WIDTH - 20)
      for index, line in enumerate(lines):
        prefix = "- " if index == 0 else "  "
        self.line(f"{prefix}{line}", size=11, font="F1", color=BODY_COLOR, x=LEFT_MARGIN + 4)


def build_cv_pdf(profile, focus_areas, strengths, skills, experience, education, projects, certifications):
  cv = CvPdf()

  cv.line(profile["name"], size=22, font="F2", color=BODY_COLOR, leading=28)
  cv.line(profile["headline"], size=13, font="F1", color=ACCENT_COLOR, leading=18)
  cv.line(
    f'{profile["location"]}  |  {profile["email"]}  |  {profile["phone"]}',
    size=10,
    font="F1",
    color=MUTED_COLOR,
    leading=18,
  )
  cv.rule()

  cv.line("Profile", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  cv.paragraph(profile["summary"])
  cv.spacer(4)

  cv.line("Core Focus", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  cv.paragraph(", ".join(focus_areas))
  cv.spacer(4)

  cv.line("Strengths", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  for strength in strengths:
    cv.line(strength["title"], size=11, font="F2", color=BODY_COLOR)
    cv.paragraph(strength["description"], size=10, color=MUTED_COLOR, leading=14)
    cv.spacer(2)

  cv.line("Experience", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  for item in experience:
    cv.line(f'{item["role"]} | {item["organization"]}', size=11, font="F2", color=BODY_COLOR)
    cv.line(item["period"], size=10, font="F1", color=MUTED_COLOR, leading=14)
    cv.paragraph(item["description"], size=10, leading=14)
    cv.spacer(2)

  cv.line("Selected Projects", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  for project in projects:
    cv.line(f'{project["title"]} | {project["category"]}', size=11, font="F2", color=BODY_COLOR)
    cv.line(project["period"], size=10, font="F1", color=MUTED_COLOR, leading=14)
    cv.paragraph(project["description"], size=10, leading=14)
    cv.bullet_list(project["highlights"])
    cv.spacer(4)

  cv.line("Technical Capabilities", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  for skill in skills:
    cv.line(skill["title"], size=11, font="F2", color=BODY_COLOR)
    cv.paragraph(", ".join(skill["entries"]), size=10, color=MUTED_COLOR, leading=14)
    cv.spacer(2)

  cv.line("Education", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  for item in education:
    cv.line(item["title"], size=11, font="F2", color=BODY_COLOR)
    cv.line(f'{item["org"]} | {item["period"]}', size=10, font="F1", color=MUTED_COLOR, leading=14)
    cv.spacer(2)

  cv.line("Certifications", size=14, font="F2", color=ACCENT_COLOR, leading=18)
  cv.paragraph(", ".join(certifications), size=10, color=MUTED_COLOR, leading=14)

  writer = PdfWriter()
  pages_id = writer.reserve()
  page_refs = []

  for operations in cv.pages:
    stream = "\n".join(operations).encode("latin-1", errors="replace")
    content_id = writer.add(
      f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream"
    )
    page_id = writer.reserve()
    page_refs.append((page_id, content_id))

  kids = " ".join(f"{page_id} 0 R" for page_id, _ in page_refs)
  writer.set(pages_id, f"<< /Type /Pages /Count {len(page_refs)} /Kids [{kids}] >>".encode("ascii"))

  for page_id, content_id in page_refs:
    writer.set(
      page_id,
      (
        f"<< /Type /Page /Parent {pages_id} 0 R "
        f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
        "/Resources << /Font << "
        "/F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
        "/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
        ">> >> "
        f"/Contents {content_id} 0 R >>"
      ).encode("ascii"),
    )

  catalog_id = writer.add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii"))
  return writer.build(catalog_id)
