import openpyxl
from config import GE_EXCEL_FILE, GE_JSON_FILE
from cache_utils import save_json

def get_site_names(file_path, attribute):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb["Export"]

    site_name_column = None

    for cell in sheet[1]:
        if cell.value == attribute:
            site_name_column = cell.column
            break

    site_names = []

    for row in range(2, sheet.max_row + 1):
        site_name = sheet.cell(
            row = row,
            column = site_name_column
        ).value

        if site_name is not None:
            site_names.append(site_name.lower())

    return site_names

# -----------------------------------test----------------------------

if __name__ == "__main__":
    site_list = get_site_names(GE_EXCEL_FILE, "Site Name")

    print(f"# of sites: {len(site_list)}")

    site_list = sorted(set(site_list))

    print(f"after remove duplicants: {len(site_list)}")

    save_json(site_list, GE_JSON_FILE)


