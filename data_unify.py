import pandas as pd
import unicodedata, re, json, csv
from pprint import pprint
from config import EXCEL_FILE, WEB_SCRAP_FILE, GOOGLE_SITE_LIST, UPDATED_SITE_CACHE
from cache_utils import load_json, save_json

# ------------------------------------------------------------------
# data_unify.py is in order to simplify each data(table, sheet, ...)
# and combine them into one data set(list of dict) w/ key:
# institution_name, institution_address
# ------------------------------------------------------------------

# ----------------------
# normalize 'None' value
# ----------------------
def normalize_none_value(value):
    if value is None:
        return ''
    return str(value).strip()

# ---------------------------
# normalized institution name
# ---------------------------
def normalize_name(name):
    if name is None:
        return ''
    
    name = str(name).strip().lower()

    # remove accents
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))

    # remove punctuation
    name = re.sub(r'[^\w\s]', ' ', name)

    # remove extra space
    name = re.sub(r'\s+', ' ', name).strip()

    return name

# -------------------
# normalized address
# -------------------
def normalize_address(addr):

    if not addr:
        return ''

    addr = str(addr).strip().lower()

    addr = unicodedata.normalize('NFKD', addr)
    addr = ''.join(c for c in addr if not unicodedata.combining(c))

    addr = re.sub(r'[^\w\s]', ' ', addr)

    addr = re.sub(r'\s+', ' ', addr)

    return addr

# --------------------------------------
# extract columns for new simple data
# --------------------------------------
def simple_excel_data(data_frame):

    data = []

    # pull each row's institution name and combined address element, and insert it into new list
    for _, row in data_frame.iterrows():
        address_parts = [
            row.get('Address 1', ''),
            row.get('Address 2', ''),
            row.get('City', ''),
            row.get('State/Province', ''),
            row.get('Zip/Postal Code', ''),
            row.get('Country', ''),
        ]

        # clean data from excel, combine them together as string, stored as a list 
        address_parts = [
            str(x).strip()
            for x in address_parts if pd.notna(x) and str(x).strip() != ''
        ]

        full_address = normalize_address(', '.join(address_parts))

        record = {
            'institution_name': normalize_name(row.get('Institution Name','')),
            'institution_address': full_address
        }

        data.append(record)
    
    return data

# --------------------------------------
# extract columns for new simple data
# --------------------------------------
def simple_json_data(json_data):
    data = [] # list

    for item in json_data:
        record = {
            'institution_name': 
                normalize_name(item.get('name')),

            'institution_address':
                normalize_address(item.get('formatted_address'))
        }

        data.append(record)
    
    return data

# --------------------------------------
# extract columns for new simple data
# --------------------------------------
def simple_csv_data(csv_data):
    data = [] # list

    for item in csv_data:
        record = {
            'institution_name': 
                normalize_name(item.get('institution_name')),

            'institution_address':
                normalize_address(item.get('normalized_address'))
        }

        data.append(record)
    
    return data

# ------------------------
# read and load excel file
# ------------------------
def load_excel_data(file):
    df = pd.read_excel(file, skiprows=[1]) # skip the template in the original excel file
    return simple_excel_data(df)

# -----------------------
# open and load json file
# -----------------------
def load_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return simple_json_data(json_data)

# ----------------------------------
# open and google site list csv file
# ----------------------------------
def load_csv_file(filename):
    with open(
        filename, 
        'r',
        encoding='utf-8-sig'
    ) as cache_file:
        reader = csv.DictReader(cache_file)
        data = list(reader)

    return simple_csv_data(data) 

# -----------------
# delete duplicants
# -----------------
def delete_duplicate(data, key01, key02):
    final_list = []

    for item in data:
        name = item[key01]
        address = item[key02]

        is_duplicate = False

        for existing in final_list:
            existing_name = existing[key01]
            existing_address = existing[key02]

            # institution name must be the same
            if name != existing_name:
                continue

            # exact same address
            if address == existing_address:
                is_duplicate = True
                break

            # wildcard / substring address match
            if (
                address
                and existing_address
                and (
                    address in existing_address
                    or existing_address in address
                )
            ):
                is_duplicate = True
                break

        if not is_duplicate:
            final_list.append(item)

    return final_list




# simplified existed data
simplified_site_list = load_excel_data(EXCEL_FILE)
simplified_web_scrap_list = load_json_data(WEB_SCRAP_FILE)
simplified_google_data = load_csv_file(GOOGLE_SITE_LIST)

# clean each data
simplified_site_list_clean = delete_duplicate(simplified_site_list, "institution_name", "institution_address")
simplified_web_scrap_list_clean = delete_duplicate(simplified_web_scrap_list, "institution_name", "institution_address")
simplified_google_data_clean = delete_duplicate(simplified_google_data, "institution_name", "institution_address")

# combine three as one and clean it
combined_list = simplified_site_list_clean + simplified_web_scrap_list_clean + simplified_google_data_clean
unique_site_list = delete_duplicate(combined_list, "institution_name", "institution_address")

# initial site json data
site_cache = load_json(UPDATED_SITE_CACHE)

if not site_cache:
    site_cache = unique_site_list.copy()
    save_json(
        site_cache,
        UPDATED_SITE_CACHE
    )

if __name__ == '__main__':
    # ------------------------------------------test--------------------------------------------------#
    print(f'number of simplified_site_list: {len(simplified_site_list)}')
    print(f'number of simplified_site_list_clean: {len(simplified_site_list_clean)}')
    print(f'number of simplified_web_scrap_list: {len(simplified_web_scrap_list)}')
    print(f'number of simplified_web_scrap_list_clean: {len(simplified_web_scrap_list_clean)}')
    print(f'number of simplified_google_data: {len(simplified_google_data)}')
    print(f'number of simplified_google_data_clean: {len(simplified_google_data_clean)}')

    print(f'number of combined_list: {len(combined_list)}')
    print(f'number of unique_site_list: {len(unique_site_list)}') # initial site list: total number: 2874
