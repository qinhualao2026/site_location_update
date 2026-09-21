import openpyxl
from config import TEMP_EXCEL_FILE

# get header info
def get_sheet_header(sheet):
    header_dict = {}

    for cell in sheet[1]:
        if cell.value:
            header_dict[cell.value] = cell.column

    return header_dict

# write parsed address info into excel file
def write_site_to_excel(parsed_address):

    # load xlsx file here in the function
    wb = openpyxl.load_workbook(TEMP_EXCEL_FILE)
    sheet = wb['Master']

    header_dict = get_sheet_header(sheet)

    new_row  = sheet.max_row + 1
    for site in parsed_address:
        for key, value in site.items():
            column = header_dict[key]
            sheet.cell(
                row = new_row,
                column = column, 
                value = value
            )

        new_row += 1

    wb.save(TEMP_EXCEL_FILE)
    
# -------------------------test-------------------------
if __name__ == "__main__":
    from web_watch import get_new_registration_data
    from data_correction import correct_registration_data
    from data_compare import update_site_data
    from address_utils import parse_new_us_site
    from pprint import pprint

    registration_data, current_id = (
        get_new_registration_data()
    )

    corrected_data = correct_registration_data(
        registration_data
    )

    current_new_sites = update_site_data(
        corrected_data
    )

    new_parsed_site_list = parse_new_us_site(
        current_new_sites
    )

    # test write site info into the spreadsheet
    write_site_to_excel(new_parsed_site_list)





