# bills/pdf_generator.py
import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_bills_pdf(bills):
    """Génère un PDF à partir d'une liste de factures et retourne les bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='FacTrackTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E3A5F'),
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='FacTrackSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#718096'),
        alignment=TA_LEFT,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='FacTrackCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1A202C'),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='FacTrackEmpty',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#E74C3C'),
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=12,
    ))

    elements = []
    elements.append(Paragraph('FacTrack', styles['FacTrackTitle']))
    elements.append(Paragraph('Liste des factures', styles['FacTrackSubtitle']))
    elements.append(Paragraph(f'Généré le {datetime.date.today().strftime("%d/%m/%Y")}', styles['FacTrackSubtitle']))
    elements.append(Spacer(1, 10))

    total_amount = sum(float(bill.price_total or 0) for bill in bills)
    paid_count = sum(1 for bill in bills if bill.paid)
    unpaid_count = len(bills) - paid_count

    summary_data = [[
        Paragraph('<b>Total factures</b><br/>{}'.format(len(bills)), styles['FacTrackCenter']),
        Paragraph('<b>Montant total</b><br/>{:,.0f} FCFA'.format(total_amount).replace(',', ' '), styles['FacTrackCenter']),
        Paragraph('<b>Payées</b><br/>{}'.format(paid_count), styles['FacTrackCenter']),
        Paragraph('<b>Impayées</b><br/>{}'.format(unpaid_count), styles['FacTrackCenter']),
    ]]
    summary_table = Table(summary_data, colWidths=[60 * mm, 70 * mm, 45 * mm, 45 * mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F4F8')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    def _bill_type_color(bill):
        return colors.HexColor('#2E86AB') if bill.type == 'SONABEL' else colors.HexColor('#20B2AA')

    def _footer(canvas, doc_obj):
        canvas.saveState()
        footer_text = f'FacTrack © - Exporté le {datetime.date.today().strftime("%d/%m/%Y")}'
        page_text = f'Page {canvas.getPageNumber()}'
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#718096'))
        canvas.drawString(doc_obj.leftMargin, 10 * mm, footer_text)
        canvas.drawRightString(doc_obj.pagesize[0] - doc_obj.rightMargin, 10 * mm, page_text)
        canvas.restoreState()

    if bills:
        table_data = [[
            Paragraph('<b>Type</b>', styles['FacTrackCenter']),
            Paragraph('<b>Période</b>', styles['FacTrackCenter']),
            Paragraph('<b>Date limite</b>', styles['FacTrackCenter']),
            Paragraph('<b>Prix total</b>', styles['FacTrackCenter']),
            Paragraph('<b>Ancien index</b>', styles['FacTrackCenter']),
            Paragraph('<b>Nouveau index</b>', styles['FacTrackCenter']),
            Paragraph('<b>Consommation</b>', styles['FacTrackCenter']),
            Paragraph('<b>Statut</b>', styles['FacTrackCenter']),
        ]]

        for bill in bills:
            table_data.append([
                Paragraph(bill.type, styles['FacTrackCenter']),
                Paragraph(bill.period.strftime('%m/%Y') if bill.period else '', styles['FacTrackCenter']),
                Paragraph(bill.deadline.strftime('%d/%m/%Y') if bill.deadline else '', styles['FacTrackCenter']),
                Paragraph(f'{bill.price_total} FCFA', styles['FacTrackCenter']),
                Paragraph(str(bill.previous_index), styles['FacTrackCenter']),
                Paragraph(str(bill.new_index), styles['FacTrackCenter']),
                Paragraph(str(bill.total_consumption), styles['FacTrackCenter']),
                Paragraph(
                    '<font color="#27AE60">Payée</font>' if bill.paid else '<font color="#E74C3C">Impayée</font>',
                    styles['FacTrackCenter']
                ),
            ])

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[22 * mm, 22 * mm, 28 * mm, 28 * mm, 22 * mm, 22 * mm, 24 * mm, 22 * mm],
        )

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])

        for index, bill in enumerate(bills, start=1):
            row = index
            row_color = colors.white if index % 2 else colors.HexColor('#F0F4F8')
            table_style.add('BACKGROUND', (0, row), (-1, row), row_color)
            table_style.add('LINEBEFORE', (0, row), (0, row), 3, _bill_type_color(bill))
            status_color = colors.HexColor('#27AE60') if bill.paid else colors.HexColor('#E74C3C')
            table_style.add('TEXTCOLOR', (7, row), (7, row), status_color)

        table.setStyle(table_style)
        elements.append(table)
    else:
        elements.append(Paragraph('Aucune facture trouvée', styles['FacTrackEmpty']))
    
    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf