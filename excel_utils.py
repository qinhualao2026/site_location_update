import openpyxl
from data_unify import normalize_none_value
# get header info
def get_sheet_header(sheet):
    header_dict = {}

    for cell in sheet[1]:
        if cell.value:
            header_dict[cell.value] = cell.column

    return header_dict

# set existing site names in .xlsx file
def get_existing_site_names(sheet, name_column):
    exising_names = set()

    for row_number in range(2, sheet.max_row + 1):
        value = sheet.cell(
            row = row_number,
            column = name_column
        ).value

        name = normalize_none_value(value)

        if name:
            exising_names.add(name)

    return exising_names

# write parsed places info into GE .xlsx file
def write_site_to_excel_GE(parsed_place, file_path):
    wb = openpyxl.load_workbook(file_path)

    try:
        sheet = wb["Master"]
        header_dict = get_sheet_header(sheet)

        unique_field = "GE Provided Institution Name"
        name_column = header_dict[unique_field]

        existing_names = get_existing_site_names(sheet, name_column)

        new_row  = sheet.max_row + 1

        for site in parsed_place:
            site_name = normalize_none_value(
                site.get(unique_field)
            )

            if not site_name:
                raise ValueError(
                    f"Missing value for: {unique_field}"
                ) 

            if site_name in existing_names:
                continue


            for key, value in site.items():
                column = header_dict[key]
                sheet.cell(
                    row = new_row,
                    column = column, 
                    value = value
                )

            existing_names.add(site_name)
            new_row += 1

        wb.save(file_path) 

    finally:
        wb.close()                      



# write parsed address info into excel file
def write_site_to_excel(parsed_place, file_path):

    # load xlsx file here in the function
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Master']

    header_dict = get_sheet_header(sheet)

    new_row  = sheet.max_row + 1

    print(f"sheet.max_row: {sheet.max_row}")
    
    for site in parsed_place:
        for key, value in site.items():
            column = header_dict[key]
            sheet.cell(
                row = new_row,
                column = column, 
                value = value
            )

        new_row += 1

    wb.save(file_path)     
# -------------------------test-------------------------
if __name__ == "__main__":
    from web_watch import get_new_registration_data
    from data_correction import correct_registration_data
    from data_compare import find_new_sites
    from address_utils import parse_new_site
    from pprint import pprint

    registration_data, current_id = (
        get_new_registration_data()
    )
    print(f"current ID in form is: {current_id}")

    corrected_data = correct_registration_data(
        registration_data
    )

    current_new_sites = find_new_sites(
        corrected_data
    )

    new_parsed_site_list = parse_new_site(
        current_new_sites
    )

    # test write site info into the spreadsheet
    # write_site_to_excel(new_parsed_site_list)




