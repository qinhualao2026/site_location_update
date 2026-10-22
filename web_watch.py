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
def convert_data(data, header_dict):
    result = [
        {
            "Manufacturer": item[header_dict["Manufacturer"]],
            "license_type": item[header_dict["License Type"]],
            "institution_name": item[header_dict["Institution Name"]],
            "institution_address": item[header_dict["Institution Address"]],
            "institution_location": item[header_dict["Institution Location"]],
            "IsDeleted": item[header_dict["IsDeleted"]]
        }
        for item in data
    ]

    return result

# ------------------
# create header dict
# ------------------
def csv_header_dict(csv_reader):
    
    headers = next(csv_reader)  # it will read the first row of csv file
    header_dict = {
        name: index for index, name in enumerate(headers)
    }
    return header_dict

# -------------------------------------
# get latest registration info from web
# -------------------------------------
def get_new_registration_data():

    with requests.Session() as session:

        # step 1: get latest registration info 
        login_data = {
            "sign_in_username": USER_NAME,
            "sign_in_password": PASSWORD 
        }                                       # form data may vary, check it out using dev tool on browser(F12)

        response = session.post(
            LOGIN_URL,
            data = login_data,
            timeout = 30
        )                                       # login as admin 

        response.raise_for_status()             # request error exceptions

        # read all registration data
        csv_response = session.get(
            EXPORT_URL,
            timeout = 15
        )
        csv_response.raise_for_status()

        csv_class = StringIO(csv_response.text)
        csv_reader = csv.reader(csv_class)

        # create header dict
        header_dict = csv_header_dict(csv_reader)

        registration = list(csv_reader)

        # step 2: get new record by compare 
        # previous record w/ ID
        last_id = get_last_id()                # based on 09/08 web data; ID No.: 1817
        current_id = int(registration[0][header_dict["ID"]])   # the first record from the web page

        # no new registration
        if current_id == last_id:
            print("no new registration")
            return [], current_id

        # get new records newer than last_id
        new_registration = []

        for row in registration:
            if int(row[header_dict["ID"]]) <= last_id:
                break

            new_registration.append(row)
            
        final_registration_data = convert_data(
            new_registration, 
            header_dict
        )

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

