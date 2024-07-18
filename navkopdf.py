from fpdf import FPDF

def navlog2pdf(navlog, pdf_path):
    pdf = FPDF(orientation="landscape", format="A4")
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    with pdf.table() as table:
        header = table.row()
        header.cell('Leg')
        header.cell('Acc')
        header.cell('ETO')
        header.cell('ATO')
        header.cell('Checkpoint', colspan=4)
        header.cell('Alt')
        header.cell('MH')
        header.cell('TH')
        header.cell('WCA')
        header.cell('TT')
        header.cell('TAS')
        header.cell('GS')
        header.cell('Leg')
        header.cell('Acc')

        for leg in navlog.legs:
            row = table.row()

            row.cell(f'{leg.time}')
            row.cell(f'{leg.time_acc}')
            row.cell('')
            row.cell('')
            row.cell(f'{leg.name:<30}', colspan=4)

            row.cell(f'{leg.alt:>}' if leg.alt else '')
            row.cell(f'{leg.mh:>}' if leg.mh else '')
            row.cell(f'{leg.th:>}' if leg.th else '')
            row.cell(f'{leg.wca:>+d}' if leg.wca else '')
            row.cell(f'{leg.tt:>}' if leg.tt else '')
            row.cell(f'{leg.tas:>}' if leg.tas else '')
            row.cell(f'{leg.gs:>}' if leg.gs else '')

            row.cell(f'{leg.dist:>4.0f}')
            row.cell(f'{leg.dist_acc:>4.0f}')

    pdf.output(pdf_path)

