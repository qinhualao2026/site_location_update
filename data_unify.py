import pandas as pd
import unicodedata, re
from config import EXCEL_FILE


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

# -------------------------------------
# read and load excel file
# -------------------------------------
def load_excel_data(file):
    df = pd.read_excel(file, skiprows=[1]) # skip the template in the original excel file
    return simple_excel_data(df)






if __name__ == '__main__':

    # simplified excel file
    simplified_site_list = load_excel_data(EXCEL_FILE)

    print(type(simplified_site_list))
    print(simplified_site_list[:2])