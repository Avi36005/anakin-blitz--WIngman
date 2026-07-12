import os
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "wingman_claims")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def claim_pdf_path(claim_id: str) -> str:
    return os.path.join(OUTPUT_DIR, f"wingman_claim_{claim_id}.pdf")


async def generate_pdf(claim_id: str, letter: str, session: dict, precedents: list) -> str:
    path = claim_pdf_path(claim_id)
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="WingHeader", parent=styles["Heading1"],
                              fontSize=18, spaceAfter=6, textColor="#111111"))
    story = []

    story.append(Paragraph("WINGMAN — COMPENSATION CLAIM", styles["WingHeader"]))
    story.append(Paragraph(
        f"Flight {session.get('flight_number', '')} &nbsp;|&nbsp; "
        f"{session.get('origin', '')} → {session.get('destination', '')} &nbsp;|&nbsp; "
        f"Delay: {session.get('delay_minutes', 0)} min", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    for para in (letter or "").split("\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("&", "&amp;"), styles["Normal"]))
            story.append(Spacer(1, 0.08 * inch))

    if precedents:
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("SUPPORTING PRECEDENTS", styles["Heading2"]))
        for p in precedents[:3]:
            story.append(Paragraph(
                f"• {p.get('case_title', '')} ({p.get('year', '')}) — "
                f"{p.get('key_ruling_one_line', '')}", styles["Normal"]))
            story.append(Spacer(1, 0.06 * inch))

    doc.build(story)
    return path
