import requests, csv
from io import StringIO
from pprint import pprint
from cache_utils import load_json,save_json
from config import USER_NAME, PASSWORD, LOGIN_URL,EXPORT_URL, LAST_ID_JSON

# read cache file and get the first ID value as the last id
def get_last_id():
    data = load_json(LAST_ID_JSON)
    return int(data['last_id'])

# --------------
# update last id
# --------------
def update_last_id(current_id):
    save_json(
        {"last_id": current_id},
        LAST_ID_JSON
    )
# ------------------------------
# convert list into list of dict
# ------------------------------ 
def convert_data(data):
    result = [
        {
            "Manufacturer": item[1],
            "license_type": item[2],
            "institution_name": item[3],
            "institution_address": item[4],
            "institution_location": item[5]
        }
        for item in data
    ]

    return result

# -------------------------------------
# get latest registration info from web
# -------------------------------------
def get_new_registration_data():

    session = requests.Session()

    # step 1: get latest registration info 
    login_data = {
        "sign_in_username": USER_NAME,
        "sign_in_password": PASSWORD 
    }                                       # form data may vary, check it out using dev tool on browser(F12)

    response = session.post(
        LOGIN_URL,
        data = login_data
    )                                       # login as admin 

    response.raise_for_status()             # request error exceptions

    # read all registration data
    csv_response = session.get(EXPORT_URL)
    csv_response.raise_for_status()

    csv_class = StringIO(csv_response.text)
    csv_reader = csv.reader(csv_class)
    csv_data = list(csv_reader)             # this is real registration data w/ header

    # skip csv header and read from row01
    registration = csv_data[1:]

    # step 2: get new record by compare 
    # previous record w/ ID
    last_id = get_last_id()                # based on 09/08 web data; ID No.: 1817
    current_id = int(registration[0][0])   # the first record from the web page

    # no new registration
    if current_id == last_id:
        print("no new registration")
        return [], current_id

    # get new records newer than last_id
    new_registration = [
        row 
        for row in registration 
        if int(row[0]) > last_id          # compare occur here
    ]
        
    trimmed_registration = []  

    for row in new_registration:
        trimmed_registration.append(row[0:3] + row[13:17])

    final_registration_data = convert_data(trimmed_registration)

    return (
        final_registration_data, 
        current_id                        # keep track of current id
    )

# ---------------------------------------test----------------------------------------
if __name__ == '__main__':
    
    final_registration_data, current_id = (
        get_new_registration_data()
    )

    print(f'new added number of site: {len(final_registration_data)}')
    print(f'current ID: {current_id}')

    pprint(final_registration_data)



