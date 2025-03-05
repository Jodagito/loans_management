import io

import pandas as pd
from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


def build_report(table_data, filename, summary_text, columns):
    df = pd.DataFrame(table_data)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        title=filename,
        rightMargin=0, leftMargin=0, topMargin=20, bottomMargin=0)
    styles = getSampleStyleSheet()
    content = []
    styles.get('title').alignment = 0
    title = Paragraph(filename, styles.get('title'))
    content.append(title)
    content.append(Spacer(1, 12))

    summary = Paragraph(summary_text, styles["Normal"])
    content.append(summary)
    content.append(Spacer(1, 12))

    columns.extend(df.values.tolist())

    table = Table(columns, colWidths=[100, 70, 70, 70, 80, 80, 80],
                  hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.cornflowerblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    content.append(table)

    doc.build(content)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename=f"{filename}.pdf")


def build_excel_report(table_data, filename, summary_text, columns):
    df = pd.DataFrame(table_data, columns=columns)
    buffer = io.BytesIO()
    summary_text_break_lines_count = len(summary_text.split(":"))

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Report", index=False,
                    startrow=summary_text_break_lines_count + 1)

        workbook = writer.book
        worksheet = writer.sheets["Report"]
        worksheet.merge_range('A1:G1', filename, workbook.add_format(
            {'bold': True, 'align': 'center', 'font_size': 14}))
        worksheet.merge_range(f'A2:G{summary_text_break_lines_count}',
                              summary_text, workbook.add_format(
                                  {'bold': True, 'align': 'center',
                                   'font_size': 10}))

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{filename}.xlsx")
