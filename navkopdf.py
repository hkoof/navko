from fpdf import FPDF

def navlog2pdf(navlog, pdf_path):
    pdf = FPDF(orientation="landscape", format="A4")
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    with pdf.table() as table:
        header = table.row()
        startrow = table.row()

        header.cell('Leg') ; startrow.cell('0', align='R')
        header.cell('Acc') ; startrow.cell('0', align='R')
        header.cell('ETO') ; startrow.cell(' ')
        header.cell('ATO') ; startrow.cell(' ')
        header.cell('Checkpoint', colspan=4) ; startrow.cell(navlog.start_name, colspan=4)
        header.cell('Alt') ; startrow.cell('')
        header.cell('MH') ; startrow.cell('')
        header.cell('TH') ; startrow.cell('')
        header.cell('WCA') ; startrow.cell('')
        header.cell('TT') ; startrow.cell('')
        header.cell('TAS') ; startrow.cell('')
        header.cell('GS') ; startrow.cell('')
        header.cell('Leg') ; startrow.cell('0', align='R')
        header.cell('Acc') ; startrow.cell('0', align='R')

        for leg in navlog.legs:
            row = table.row()

            row.cell(f'{leg.time}', align='R')
            row.cell(f'{leg.time_acc}', align='R')
            row.cell('')
            row.cell('')
            row.cell(f'{leg.name}', colspan=4)

            row.cell(f'{leg.alt:>}' if leg.alt else '', align='R')
            row.cell(f'{leg.mh:0>3d}' if leg.mh else '', align='R')
            row.cell(f'{leg.th:0>3d}' if leg.th else '', align='R')

            wca_str = ''
            if leg.wca == 0: wca_str = '0'
            elif leg.wca != None: wca_str = f'{leg.wca:>+d}'
            row.cell(wca_str, align='R')

            row.cell(f'{leg.tt:0>3d}' if leg.tt else '', align='R')
            row.cell(f'{leg.tas:>}' if leg.tas else '', align='R')
            row.cell(f'{leg.gs:>}' if leg.gs else '', align='R')

            row.cell(f'{leg.dist:>4.0f}', align='R')
            row.cell(f'{leg.dist_acc:>4.0f}', align='R')

    pdf.output(pdf_path)

