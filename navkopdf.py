from fpdf import FPDF
from fpdf.fonts import FontFace
from fpdf.drawing import DeviceGray, DeviceRGB

def navlog2pdf(navlog, pdf_path):
    pdf = FPDF(orientation="landscape", format="A4")
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    title1  = f'"{navlog.title}"'
    title2  = (
        f'IAS: {navlog.ias:<14}'
        f'Wind: {navlog.wind_direction}/{navlog.wind_speed} kt {"":<14}'
        f'Variation: {navlog.var:<+14}'
        '\n'
    )

    chkp_colspan = 5
    style = FontFace(color=DeviceGray(0), fill_color=DeviceGray(0.90)) 

    with pdf.table(num_heading_rows=2, line_height=10) as table:
        titlerow = table.row()
        headerrow = table.row()
        startrow = table.row()

        titlerow.cell(title1, colspan=4, align='C', style=FontFace(size_pt=10))
        titlerow.cell(title2, colspan=14, align='C', style=FontFace(size_pt=10))

        headerrow.cell('Leg') ; startrow.cell('0', align='R')
        headerrow.cell('Acc') ; startrow.cell('0', align='R')
        headerrow.cell('ETO') ; startrow.cell('--', align='C')
        headerrow.cell('ATO') ; startrow.cell(' ', style=style)
        headerrow.cell('Checkpoint', colspan=chkp_colspan) ; startrow.cell(navlog.start_name, colspan=chkp_colspan)
        headerrow.cell('Alt') ; startrow.cell('--', align='C')
        headerrow.cell('MH') ; startrow.cell('--', align='C')
        headerrow.cell('TH') ; startrow.cell('--', align='C')
        headerrow.cell('WCA') ; startrow.cell('--', align='C')
        headerrow.cell('TT') ; startrow.cell('--', align='C')
        headerrow.cell('TAS') ; startrow.cell('--', align='C')
        headerrow.cell('GS') ; startrow.cell('--', align='C')
        headerrow.cell('Leg') ; startrow.cell('0', align='R')
        headerrow.cell('Acc') ; startrow.cell('0', align='R')

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

