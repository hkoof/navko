from fpdf import FPDF
from fpdf.fonts import FontFace
from fpdf.drawing import DeviceGray, DeviceRGB

def navlog2pdf(navlog, pdf_path):
    pdf = FPDF(orientation="landscape", format="A4")
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    chkp_colspan = 5
    style = FontFace(color=DeviceGray(0), fill_color=DeviceGray(0.94)) 

    with pdf.table(line_height=12) as table:
        header = table.row()
        startrow = table.row()

        header.cell('Leg') ; startrow.cell('0', align='R')
        header.cell('Acc') ; startrow.cell('0', align='R')
        header.cell('ETO') ; startrow.cell('_', align='C', padding=(0,0,2,0,))
        header.cell('ATO') ; startrow.cell(' ', style=style)
        header.cell('Checkpoint', colspan=chkp_colspan) ; startrow.cell(navlog.start_name, colspan=chkp_colspan)
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
            row.cell('', style=style)
            row.cell('', style=style)
            row.cell(f'{leg.name}', colspan=chkp_colspan)

            row.cell(f'{leg.alt:>}' if leg.alt != None else '', align='R')
            row.cell(f'{leg.mh:0>3d}' if leg.mh != None else '', align='R')
            row.cell(f'{leg.th:0>3d}' if leg.th != None else '', align='R')

            wca_str = ''
            if leg.wca == 0: wca_str = '0'
            elif leg.wca != None: wca_str = f'{leg.wca:>+d}'
            row.cell(wca_str, align='R')

            row.cell(f'{leg.tt:0>3d}' if leg.tt != None else '', align='R')
            row.cell(f'{leg.tas:>}' if leg.tas != None else '', align='R')
            row.cell(f'{leg.gs:>}' if leg.gs != None else '', align='R')

            row.cell(f'{leg.dist:>4.0f}', align='R')
            row.cell(f'{leg.dist_acc:>4.0f}', align='R')

    pdf.output(pdf_path)

