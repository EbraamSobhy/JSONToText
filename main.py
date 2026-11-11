
import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from xml.sax.saxutils import escape


def format_key(key):
    """Convert technical field names into readable labels."""
    key = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(key))
    key = key.replace("_", " ").replace("-", " ")
    return key.capitalize()


def format_value(value):
    """Make values easier for non-technical readers to understand."""
    if value is None:
        return "Not provided"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "None"
    return str(value)


def process_json(data, story, styles, level=0):
    """Convert JSON data into readable PDF sections."""

    if isinstance(data, dict):
        for key, value in data.items():

            if isinstance(value, (dict, list)):
                story.append(Spacer(1, 10))
                story.append(
                    Paragraph(
                        escape(format_key(key)),
                        styles["Section"]
                    )
                )
                process_json(value, story, styles, level + 1)

            else:
                text = (
                    f"<b>{escape(format_key(key))}:</b> "
                    f"{escape(format_value(value))}"
                )
                story.append(
                    Paragraph(text, styles["NormalCustom"])
                )

    elif isinstance(data, list):
        if not data:
            story.append(
                Paragraph("No entries available.", styles["NormalCustom"])
            )
            return

        for index, item in enumerate(data, 1):
            if isinstance(item, (dict, list)):
                story.append(Spacer(1, 8))
                story.append(
                    Paragraph(f"Entry {index}", styles["SubSection"])
                )
                process_json(item, story, styles, level + 1)
            else:
                story.append(
                    Paragraph(
                        f"• {escape(format_value(item))}",
                        styles["NormalCustom"]
                    )
                )


def json_to_pdf(input_file, output_file):

    # Read JSON file
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # PDF setup
    pdf = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#23476A"),
        spaceBefore=10,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="SubSection",
        parent=styles["Heading3"],
        textColor=colors.HexColor("#555555"),
        spaceBefore=8,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="NormalCustom",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=6
    ))

    story = []

    # Document title
    story.append(Paragraph(
        "Information Report",
        styles["Title"]
    ))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(
        width="100%",
        color=colors.grey
    ))
    story.append(Spacer(1, 15))

    # Convert JSON content
    process_json(data, story, styles)

    # Generate PDF
    pdf.build(story)

    print(f"PDF successfully created: {output_file}")


if __name__ == "__main__":
    json_to_pdf("input.json", "output.pdf")

