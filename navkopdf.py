from fpdf import FPDF
from fpdf.fonts import FontFace
from fpdf.drawing import DeviceGray, DeviceRGB

def navlog2pdf(navlog, pdf_path):
    pdf = FPDF(orientation="landscape", format="A4")
    pdf.add_page()
    pdf.set_font("Courier", size=10)

    title1  = f'"{navlog.title}"'
    title2  = (
        f'IAS: {navlog.ias:<14}'
        f'Wind: {navlog.wind_direction}/{navlog.wind_speed} kt {"":<14}'
        f'Variation: {navlog.var:<+14}'
        '\n'
    )

    colspan = 3
    chkp_colspan = 15
    notes_colspan = 12
    style = FontFace(color=DeviceGray(0), fill_color=DeviceGray(0.90)) 

    with pdf.table(num_heading_rows=2, line_height=10) as table:
        titlerow = table.row()
        headerrow = table.row()
        startrow = table.row()

        titlerow.cell(title1, colspan=10, align='C', style=FontFace(size_pt=10))
        titlerow.cell(title2, colspan=54, align='C', style=FontFace(size_pt=10))

        headerrow.cell('Leg', align='C', colspan=2) ; startrow.cell('0', align='R', colspan=2)
        headerrow.cell('Acc', align='C', colspan=2) ; startrow.cell('0', align='R', colspan=2)
        headerrow.cell('ETO', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('ATO', align='C', colspan=colspan) ; startrow.cell(' ', style=style, colspan=colspan)
        headerrow.cell('Checkpoint', colspan=chkp_colspan) ; startrow.cell(navlog.start_name, colspan=chkp_colspan)
        headerrow.cell('Alt', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('MH', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('TH', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('WCA', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('TT', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('TAS', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('GS', align='C', colspan=colspan) ; startrow.cell('--', align='C', colspan=colspan)
        headerrow.cell('Leg', align='C', colspan=colspan) ; startrow.cell('0', align='R', colspan=colspan)
        headerrow.cell('Acc', align='C', colspan=colspan) ; startrow.cell('0', align='R', colspan=colspan)
        headerrow.cell('Notes', colspan=notes_colspan) ; startrow.cell('', colspan=notes_colspan)

        for leg in navlog.legs:
            row = table.row()

            row.cell(f'{leg.time}', align='R', colspan=2)
            row.cell(f'{leg.time_acc}', align='R', colspan=2)
            row.cell('', style=style, colspan=colspan)
            row.cell('', style=style, colspan=colspan)
            row.cell(f'{leg.name}', colspan=chkp_colspan)

            row.cell(f'{leg.alt:>}' if leg.alt != None else '', align='R', colspan=colspan)
            row.cell(f'{leg.mh:0>3d}' if leg.mh != None else '', align='R', colspan=colspan)
            row.cell(f'{leg.th:0>3d}' if leg.th != None else '', align='R', colspan=colspan)

            wca_str = ''
            if leg.wca == 0: wca_str = '0'
            elif leg.wca != None: wca_str = f'{leg.wca:>+d}'
            row.cell(wca_str, align='R', colspan=colspan)

            row.cell(f'{leg.tt:0>3d}' if leg.tt != None else '', align='R', colspan=colspan)
            row.cell(f'{leg.tas:>}' if leg.tas != None else '', align='R', colspan=colspan)
            row.cell(f'{leg.gs:>}' if leg.gs != None else '', align='R', colspan=colspan)

            row.cell(f'{leg.dist:>4.0f}', align='R', colspan=colspan)
            row.cell(f'{leg.dist_acc:>4.0f}', align='R', colspan=colspan)
            row.cell('', colspan=notes_colspan)


    pdf.output(pdf_path)

