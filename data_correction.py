import requests, time
from tqdm import tqdm
from pprint import pprint
from cache_utils import load_cache, save_cache
from config import GOOGLE_PLACES_API_KEY, GOOGLE_CACHE
from web_watch import final_registration_data
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
            'places.formattedAddress,'
            'places.types,'
            'places.displayName,'
            'places.addressDescriptor.landmarks.displayName,'
            'places.addressDescriptor.landmarks.types'
        )
    }

    cache = load_cache(GOOGLE_CACHE)

    with requests.Session() as session:
        for item in tqdm(data, desc="Looking up Google Place API:"):

            name = item.get("institution_name", "").strip()
            address = item.get('institution_address', "").strip()

            # treat '---' as ''
            if address == "---":
                address = ""

            # case #1: entity has no name and address
            if not name and not address:
                continue

            # case #2: entity name and address
            if name and address:
                query_text = f"{name} {address}"

            # case #3: entity only has name
            elif name:
                query_text = name

            # case #4: entity only has address
            else:
                query_text = address

            cache_key = query_text
            
            if cache_key in cache:
                result = cache[cache_key]
            else:
                try:
                    result = query_google_places(
                        query_text,
                        session,
                        url,
                        headers
                    )
                    cache[cache_key] = result
                    save_cache(cache, GOOGLE_CACHE)

                    time.sleep(sleep_time)

                except requests.RequestException as e:
                    print(f'Google Place API request failed for {address}: {e}')

                    result = {
                        'places': []
                    }

# --------------------------------
# trim received google places data
# --------------------------------

TYPE_PRIORITY = [
    "general_hospital",
    "hospital",
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

        best_place = select_best_place(places)

        if not best_place:
            continue

        display_name = best_place.get("displayName", {}).get("text", "")
        formatted_address = best_place.get("formattedAddress", "")

        record = {
            "institution_name": normalize_name(display_name),
            "institution_address": normalize_address(formatted_address)
        }

        simplified_data.append(record)

    return simplified_data


if __name__ == '__main__':

    # google_places_api_lookup(final_registration_data, GOOGLE_PLACES_API_KEY)

    # load google place cache 
    cache = load_cache(GOOGLE_CACHE)

    # it will be using to compare w/ registration database(in data_unify.py)
    trimmed_data = simplify_google_place_cache(cache)
    pprint(trimmed_data)