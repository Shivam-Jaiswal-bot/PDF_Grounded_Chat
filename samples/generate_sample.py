"""Generate samples/sample.pdf — a fictional 4-page company handbook for Lumora Labs.

Run from project root:
    python samples/generate_sample.py
"""
from __future__ import annotations

import os

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    PageBreak,
)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sample.pdf")


def build():
    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15,
        spaceAfter=8,
    )

    doc = SimpleDocTemplate(
        OUT,
        pagesize=LETTER,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        title="Lumora Labs Employee Handbook",
        author="Lumora Labs People Operations",
    )

    story = []

    # Page 1 — Introduction & Mission
    story.append(Paragraph("Lumora Labs Employee Handbook", h1))
    story.append(Paragraph("Edition 4.2 — Effective March 2026", body))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("1. About Lumora Labs", h2))
    story.append(Paragraph(
        "Lumora Labs is a fictional applied-research company headquartered in Bengaluru, India, "
        "with satellite offices in Lisbon and Toronto. The company was founded in 2017 by Anika Rao "
        "and Marcus Belo to build privacy-first machine learning tools for small and mid-sized businesses. "
        "As of January 2026, Lumora Labs employs 184 people across three continents.",
        body,
    ))
    story.append(Paragraph("2. Mission Statement", h2))
    story.append(Paragraph(
        "Our mission is to make trustworthy AI accessible to every organization, regardless of size or "
        "technical maturity. We pursue this mission through three commitments: open documentation of our "
        "methods, conservative handling of customer data, and a strong bias toward small, auditable models.",
        body,
    ))
    story.append(Paragraph("3. Core Values", h2))
    story.append(Paragraph(
        "Lumora Labs operates by five core values: Curiosity, Candor, Craft, Care, and Calm. "
        "These values guide hiring, performance reviews, and product decisions. The annual Lumora Prize "
        "of 5,000 USD is awarded each December to the team that best exemplifies these values in a shipped project.",
        body,
    ))

    story.append(PageBreak())

    # Page 2 — Working Hours, Leave, Remote Work
    story.append(Paragraph("4. Working Hours and Remote Work", h2))
    story.append(Paragraph(
        "Standard working hours at Lumora Labs are 9:30 AM to 6:00 PM local time, Monday through Friday, "
        "with a one-hour lunch break. All employees are entitled to work remotely up to three days per week. "
        "Tuesdays and Thursdays are designated in-office collaboration days for engineering teams.",
        body,
    ))
    story.append(Paragraph("5. Leave Policy", h2))
    story.append(Paragraph(
        "Full-time employees receive 24 days of paid annual leave each calendar year, in addition to 12 public holidays. "
        "Unused leave may be carried over up to a maximum of 10 days into the following year. "
        "Sick leave is provided separately at 12 days per year and does not require a medical certificate "
        "for absences of two days or fewer. Parental leave is 26 weeks for primary caregivers and 8 weeks for secondary caregivers.",
        body,
    ))
    story.append(Paragraph("6. Travel and Expenses", h2))
    story.append(Paragraph(
        "Business travel must be approved by a direct manager at least seven calendar days in advance. "
        "Daily meal allowances are 60 USD for travel within India, 90 USD for Europe, and 110 USD for North America. "
        "All expense receipts must be submitted within 14 days of return through the Lumora Expense Portal.",
        body,
    ))

    story.append(PageBreak())

    # Page 3 — Security & Data
    story.append(Paragraph("7. Information Security", h2))
    story.append(Paragraph(
        "All Lumora Labs employees must complete the Annual Security Refresher within 30 days of their hire date "
        "and again every 12 months. The course covers phishing recognition, secure development practices, and the "
        "company's incident response procedure. Failure to complete the refresher on time results in temporary suspension "
        "of production system access until the course is finished.",
        body,
    ))
    story.append(Paragraph("8. Customer Data Handling", h2))
    story.append(Paragraph(
        "Customer data classified as Tier 1 (containing personally identifiable information) must be encrypted at rest "
        "using AES-256 and may only be accessed from company-managed devices. Tier 2 data (aggregated, non-identifying) "
        "may be analyzed on approved cloud notebooks. Tier 3 data (fully synthetic) carries no handling restrictions. "
        "Customer data must never be copied to personal storage, including private email accounts and personal cloud drives.",
        body,
    ))
    story.append(Paragraph("9. Incident Response", h2))
    story.append(Paragraph(
        "Suspected security incidents must be reported to security@lumoralabs.example within one hour of discovery. "
        "The on-call security engineer will acknowledge the report within 30 minutes and convene an incident review "
        "within 4 business hours. Post-incident reviews are blameless and are published internally within 10 working days.",
        body,
    ))

    story.append(PageBreak())

    # Page 4 — Performance, Compensation, Contact
    story.append(Paragraph("10. Performance Reviews", h2))
    story.append(Paragraph(
        "Lumora Labs runs two formal performance review cycles per year, in June and December. "
        "Each review includes self-assessment, peer feedback from at least three colleagues, and a manager review. "
        "Promotions are evaluated only during the December cycle. Employees on a Performance Improvement Plan are "
        "reviewed monthly for the duration of the plan, which is typically 90 days.",
        body,
    ))
    story.append(Paragraph("11. Compensation and Benefits", h2))
    story.append(Paragraph(
        "Compensation is reviewed annually each January. The company contributes the local statutory minimum to retirement "
        "plans plus an additional 4% match on voluntary employee contributions up to 10% of base salary. "
        "All employees receive private medical insurance covering themselves, a spouse, and up to two children. "
        "A learning budget of 1,500 USD per employee per year may be spent on books, courses, and conferences.",
        body,
    ))
    story.append(Paragraph("12. Contact and Acknowledgement", h2))
    story.append(Paragraph(
        "Questions about this handbook should be directed to people-ops@lumoralabs.example. "
        "By continuing employment with Lumora Labs after the effective date of this edition, employees acknowledge "
        "they have read and agree to the policies described herein. This handbook supersedes all prior editions.",
        body,
    ))

    doc.build(story)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
