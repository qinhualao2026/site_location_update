import requests, csv
from io import StringIO
from config import USER_NAME, PASSWORD, LOGIN_URL,EXPORT_URL
from .csv_reader import last_id

session = requests.Session()

# ------------------------------------
# step 1: get latest registration info 
# ------------------------------------
login_data = {
    "sign_in_username": USER_NAME,
    "sign_in_password": PASSWORD 
} # form data may vary, check it out using dev tool on browser(F12)

# login as admin 
response = session.post(
    LOGIN_URL,
    data = login_data
)

# read all registration data
csv_response = session.get(EXPORT_URL)
csv_class = StringIO(csv_response.text)
csv_reader = csv.reader(csv_class)
csv_data = list(csv_reader)             # this is real registration data w/ header

# seperate header and content
csv_header = csv_data[0]
registration = csv_data[1:]

# -------------------------------------------------------
# step 2: get new record by compare previous record w/ ID
# -------------------------------------------------------
current_id = int(registration[0][0])   # the first record from the web page

# compare and get new registration record
if(current_id == last_id):
    print("now new registration")
else:
    new_registration = [
        row for row in registration if int(row[0]) > last_id
    ]

trimmed_registration = []             # new 'list' is w/ id, manufacturer, institution_name, institution_address, institution_location in each row
for row in new_registration:
    trimmed_registration.append(row[0:2] + row[13:16])

# current status: now can catch new record compare w/ date 09/09 record