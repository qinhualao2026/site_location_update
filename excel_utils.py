import openpyxl
from data_unify import normalize_none_value
from config import GE_KEY_FIELDS, MRE_KEY_FIELDS
# get header info
def get_sheet_header(sheet):
    header_dict = {}

    for cell in sheet[1]:
        if cell.value:
            header_dict[cell.value] = cell.column

    return header_dict

# store fields as tuple
def make_site_key(site, key_fields):
    values = []

    for field in key_fields:
        value = normalize_none_value(site.get(field))
        values.append(value.casefold())

    return tuple(values)
    

# set existing site names in .xlsx file
def get_existing_site_keys(sheet, header_dict, key_fields):

    # make sure no fields in sheet column is missing
    missing_fields = [
        field
        for field in key_fields if field not in header_dict
    ]

    if missing_fields:
        raise ValueError(
            f"Missing Excel headers: {missing_fields}"
        )

    # generate existing site for later comparison
    # each item in the set here is 'tuple'
    existing_names = set()

    for row_number in range(2, sheet.max_row + 1):
        site = {
            field: sheet.cell(
                row = row_number,
                column = header_dict[field],
            ).value
            for field in key_fields
        }

        site_key = make_site_key(site, key_fields)

        if site_key:
            existing_names.add(site_key)

    return existing_names

# write parsed places info into GE .xlsx file
def write_site_to_excel_GE(parsed_place, file_path):
    wb = openpyxl.load_workbook(file_path)

    try:
        sheet = wb["Master"]
        header_dict = get_sheet_header(sheet)

        exsiting_keys = get_existing_site_keys(
            sheet,
            header_dict,
            GE_KEY_FIELDS
        )

        new_row  = sheet.max_row + 1

        for site in parsed_place:
            site_keys = make_site_key(
                site,
                GE_KEY_FIELDS
            )

            if not site_keys[0]:
                raise ValueError(
                    f"Missing value for: GE Provided Institution Name"
                ) 

            # prevent duplicants
            if site_keys in exsiting_keys:
                continue

            for field, value in site.items():
                column = header_dict[field]
                sheet.cell(
                    row = new_row,
                    column = column, 
                    value = value
                )

            exsiting_keys.add(site_keys)
            new_row += 1

        wb.save(file_path) 

    finally:
        wb.close()                      


# write parsed address info into excel file
def write_site_to_excel(parsed_place, file_path):

    wb = openpyxl.load_workbook(file_path)

    try:
        sheet = wb['Master']
        header_dict = get_sheet_header(sheet)

        existing_keys = get_existing_site_keys(
            sheet,
            header_dict,
            MRE_KEY_FIELDS
        )

        new_row  = sheet.max_row + 1
        
        for site in parsed_place:
            site_keys = make_site_key(
                site,
                MRE_KEY_FIELDS
            )

            if not site_keys[0]:
                raise ValueError(
                    f"Missing column: Institution Name"
                )

            if site_keys in existing_keys:
                continue
            
            for field, value in site.items():
                column = header_dict[field]
                sheet.cell(
                    row = new_row,
                    column = column, 
                    value = value
                )

            existing_keys.add(site_keys)
            new_row += 1

        wb.save(file_path)

    finally:
        wb.close()  
 
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






