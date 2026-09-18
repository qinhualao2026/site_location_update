import requests, time
from tqdm import tqdm
from pprint import pprint
from cache_utils import load_json, save_json
from config import GOOGLE_PLACES_API_KEY, GOOGLE_CACHE

from data_unify import normalize_name, normalize_address

# ----------------------------------------------
# google places api access with times limitation
# ----------------------------------------------
def query_google_places(query_text, session, url, headers):

    payload = {
        "textQuery": query_text # use 'query_text(both institution_name and address)
    }
    response = session.post(
        url,
        json = payload,
        headers = headers,
        timeout = 10
    )
    response.raise_for_status()
    return response.json()

def google_places_api_lookup(data, api_key, sleep_time=1):

    url = 'https://places.googleapis.com/v1/places:searchText'

    # add on new fieldmask to get 'places.displayName' 
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            'places.types,'
            'places.displayName,'
            'places.formattedAddress,'
            'places.addressComponents,'
        )
    }

    cache = load_json(GOOGLE_CACHE)

    # store current updating site list
    current_results = {}

    with requests.Session() as session:
        for item in tqdm(data, desc="Looking up Google Place API:"):

            name = item.get("institution_name", "").strip()
            address = item.get('institution_address', "").strip()
            location = item.get('institution_location', "").strip()

            # treat '---' as ''
            if name == "---":
                name = ""

            if address == "---":
                address = ""

            # same as address
            if location == "---":
                location = ""

            # generate query text for api search
            query_text = " ".join(
                value for value in [name, address, location] if value
            )

            if not query_text:
                continue

            cache_key = query_text
            
            if cache_key in cache:
                # print(f'CACHE HIT: {cache_key}')
                result = cache[cache_key]
            else:
                # print(f"API CALL: {cache_key}")
                try:
                    result = query_google_places(
                        query_text,
                        session,
                        url,
                        headers
                    )
                    cache[cache_key] = result
                    save_json(cache, GOOGLE_CACHE)

                    time.sleep(sleep_time)

                except requests.RequestException as e:
                    print(f'Google Place API request failed for {query_text}: {e}')

                    result = {
                        'places': []
                    }
            current_results[cache_key] = result

    return current_results

# --------------------------------
# trim received google places data
# --------------------------------

TYPE_PRIORITY = [
    "hospital",
    "general_hospital",
    "medical_clinic",
    "health"
]

# pick up the most potential data
def select_best_place(places):
    for prefered_type in TYPE_PRIORITY:
        for place in places:
            place_type = place.get("types", [])
            if prefered_type in place_type:
                return place

# convert picked data to list of dict
def simplify_google_place_cache(cache):
    simplified_data = []

    for query, result in cache.items():
        places = result.get("places", [])
        
        if not places:
            continue

        # find out place candidate
        best_place = select_best_place(places)

        if not best_place:
            continue

        display_name = best_place.get("displayName", {}).get("text", "")
        formatted_address = best_place.get("formattedAddress", "")

        record = {
            "institution_name": normalize_name(display_name),
            "institution_address": normalize_address(formatted_address),
            "google_place": best_place
        }

        simplified_data.append(record)

    return simplified_data

# ---------------------------
# normalize and simplify data
# ---------------------------
def correct_registration_data(data):
    # query Google Places
    current_results = google_places_api_lookup(
        data, 
        GOOGLE_PLACES_API_KEY
    )

    # simplify Google Places cache data
    trimmed_data = simplify_google_place_cache(current_results)

    return trimmed_data

# --------------------------------------test----------------------------------------
if __name__ == '__main__':

    from web_watch import get_new_registration_data

    registration_data, current_id = (
        get_new_registration_data()
    )

    print(f'current ID: {current_id}\ntotal # of new registration: {len(registration_data)}')

    trimmed_data = correct_registration_data(registration_data)

    print(f'correct sites: {len(trimmed_data)}')
    pprint(trimmed_data[0])