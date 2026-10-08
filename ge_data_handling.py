import openpyxl
import requests
import time
from tqdm import tqdm
from config import  GE_EXCEL_FILE, NOMINATIM_CACHE_FILE, GE_GOOGLE_CACHE_FILE, GOOGLE_PLACES_API_KEY, TEMP_GE_SITE_LIST
from cache_utils import load_json, save_json
from data_correction import query_google_places, select_best_place
from address_utils import get_address_component
from excel_utils import write_site_to_excel_GE

# this function is in order to get site names from existing excel file
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

# ----------------------------------
# use nominatim geocoding/search API -- NOT GOOD
# ----------------------------------
def query_nominatim(site_name, session, url, headers):
    params = {
        "q": site_name,
        "format": "json",
        "addressdetails": 1,
        "limit": 10,
        "countrycodes": "us"
    }

    response = session.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    return response.json()

def nominatim_site_lookup(site_list, sleep_time = 1.5):

    url = 'https://nominatim.openstreetmap.org/search'

    headers = {
        "User-Agent": "mre-location-project/1.0"
    }

    cache = load_json(NOMINATIM_CACHE_FILE)

    with requests.Session() as session:
        for site_name in tqdm(
            site_list,
            desc="Looking UP nominatim geocoding/search API"
        ):
            if not site_name:
                continue

            if site_name in cache:
                continue

            try:
                results = query_nominatim(
                    site_name,
                    session,
                    url,
                    headers
                )

                cache[site_name] = results

                save_json(
                    cache,
                    NOMINATIM_CACHE_FILE
                )
            except requests.HTTPError as e:
                if e.response.status_code == 429:
                    print(
                        f"\n rate limit reached at: {site_name}"
                    )
                    print("stop querying information")
                    break

                print(
                    f"\nnominatim request failed for "
                    f"{site_name}: {e}"
                )

            except requests.RequestException as e:
                print(
                    f"\nOSM request failed for "
                    f"{site_name}: {e}"
                )

            time.sleep(sleep_time)  

    return cache

# ----------------------------------------------
# using google places api to get geo information
# and cache it
# ----------------------------------------------

def google_places_api_lookup_GE(data, api_key, sleep_time=1):

    url = 'https://places.googleapis.com/v1/places:searchText'

    # field returned from Google Places API 
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            'places.types,'
            'places.displayName,'
            'places.formattedAddress,'
            'places.addressComponents,'
            'places.location'                     # geo tag: latitude, longitude
        )
    }

    cache = load_json(GE_GOOGLE_CACHE_FILE)

    # store current updating site list
    current_results = {}

    with requests.Session() as session:
        for item in tqdm(data, desc="Looking up Google Place API:"):

            site_name = item.strip()

            if not site_name:
                continue

            cache_key = site_name

            # check query text existed in google places cache file
            if cache_key in cache:
                print(f'CACHE HIT: {cache_key}')  # for testing 
                result = cache[cache_key]
            else:
                #  print(f"API CALL: {cache_key}")   # for testing
                try:
                    result = query_google_places(
                        site_name,
                        session,
                        url,
                        headers
                    )
                    cache[cache_key] = result
                    save_json(cache, GE_GOOGLE_CACHE_FILE)

                    time.sleep(sleep_time)

                except requests.RequestException as e:
                    print(f'Google Place API request failed for {site_name}: {e}')

                    result = {
                        'places': []
                    }
            current_results[cache_key] = result

    return current_results

# ------------------------------------------
# process google places api data based on GE
# ------------------------------------------
def place_candidates(cache):
    site_candidates = {}

    for key, values in cache.items():
        places = values.get("places", [])

        if not places:
            continue

        place_candidate = select_best_place(places)
        
        if not place_candidate:
            place_candidate = places[0]

        site_candidates[key] = place_candidate

    return site_candidates
        
# -------------
# organize data
# -------------
def parse_place_information(cache_key, cache_value):
    address_components = cache_value.get("addressComponents", [])

    institution_name = cache_value.get("displayName", {}).get("text", "")

    street_number = get_address_component(
        address_components,
        "street_number"
    )

    street = get_address_component(
        address_components,
        "route"
    )

    address_1 = " ".join(
        value for value in [street_number, street] if value
    )

    city = get_address_component(address_components, "locality")
    state = get_address_component(address_components, "administrative_area_level_1")
    zip_code = get_address_component(address_components, "postal_code")
    country = get_address_component(address_components, "country")   

    # geo tag
    location = cache_value.get("location", {})
    latitude = location.get("latitude", "")
    longitude = location.get("longitude", "") 

    return {
        "GE Provided Institution Name": cache_key,
        "Institution Name": institution_name,
        "Address 1": address_1,
        "Address 2": "",
        "City": city,
        "State/\nProvince": state,
        "Zip/Postal Code": zip_code,
        "Country": country,
        "Latitude": latitude,
        "Longitude": longitude
    }    

def parse_place_dict(cache):

    parsed_sites = []

    for key, value in cache.items():
        place = parse_place_information(key, value)

        if not place:
            continue

        parsed_sites.append(place)

    return parsed_sites

# -----------------------------------test----------------------------

if __name__ == "__main__":
    
    ge_site_list = get_site_names(GE_EXCEL_FILE, "Site Name")
    print(len(ge_site_list))

    # delete duplicants and sort the list
    ge_site_list = sorted(set(ge_site_list))
    print(len(ge_site_list))

    # down the list # to 20 for testing
    sliced_ge_site_list = ge_site_list[: 105]
    
    # using google places api 
    test_results = google_places_api_lookup_GE(sliced_ge_site_list, GOOGLE_PLACES_API_KEY)
    
    # load Google Places API cache file
    ge_google_cache_data = load_json(GE_GOOGLE_CACHE_FILE)

    # select proper place information
    ge_place_candidates = place_candidates(ge_google_cache_data)

    # parse address information
    parsed_site_list = parse_place_dict(ge_place_candidates)

    # write proecessed information into .xlsx file
    write_site_to_excel_GE(parsed_site_list, TEMP_GE_SITE_LIST)
    