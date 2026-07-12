import base64
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


def _build(letter: str, session: dict, precedents: list) -> bytes:
    """Render the claim letter to PDF bytes (no filesystem — serverless-safe)."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="WingHeader", parent=styles["Heading1"],
                              fontSize=18, spaceAfter=6, textColor="#111111"))
    story = [
        Paragraph("WINGMAN — COMPENSATION CLAIM", styles["WingHeader"]),
        Paragraph(
            f"Flight {session.get('flight_number', '')} &nbsp;|&nbsp; "
            f"{session.get('origin', '')} → {session.get('destination', '')} &nbsp;|&nbsp; "
            f"Delay: {session.get('delay_minutes', 0)} min", styles["Normal"]),
        Spacer(1, 0.3 * inch),
    ]
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
    return buf.getvalue()


async def generate_pdf_base64(letter: str, session: dict, precedents: list) -> str:
    """Return the claim PDF as a base64 data payload (frontend downloads it directly)."""
    return base64.b64encode(_build(letter, session, precedents)).decode("ascii")
