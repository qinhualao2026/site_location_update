import openpyxl
import requests
import time
from tqdm import tqdm
from pprint import pprint
from config import (
    MRE_SITE_LIST, 
    MRE_QUERY_FIELDS, 
    GOOGLE_FETCH_HEADER, 
    GEO_TAG_CACHE_FILE
)
from excel_utils import (
    get_sheet_header, 
    write_geo_tag_to_excel, 
    make_lookup_key
)
from cache_utils import load_json, save_json
from data_correction import query_google_places
from ge_data_handling import place_candidates

def get_text_query(header_dict, query_field):

    site_queries = []

    for row_number in range(3, sheet.max_row + 1):
        site = {
            field: sheet.cell(
                row = row_number,
                column = header_dict[field],
            ).value
            for field in query_field
        }

        query = make_lookup_key(site,query_field)
        site_queries.append(query)

    return site_queries

def google_places_api_lookup(
        google_fetch_headers, 
        query_list, cache_file_path, 
        sleep_time=1
):

    url = 'https://places.googleapis.com/v1/places:searchText'

    # field returned from Google Places API 

    cache = load_json(cache_file_path)

    # store current updating site list
    current_results = {}

    with requests.Session() as session:
        for item in tqdm(query_list, desc="Looking up Google Place API:"):

            site_name = item.strip()

            if not site_name:
                continue

            cache_key = site_name

            # check query text existed in google places cache file
            if cache_key in cache:
                # print(f'CACHE HIT: {cache_key}')  # for testing 
                result = cache[cache_key]
            else:
                #  print(f"API CALL: {cache_key}")   # for testing
                try:
                    result = query_google_places(
                        site_name,
                        session,
                        url,
                        google_fetch_headers
                    )
                    cache[cache_key] = result
                    save_json(cache, cache_file_path)

                    time.sleep(sleep_time)

                except requests.RequestException as e:
                    print(f'Google Place API request failed for {site_name}: {e}')

                    result = {
                        'places': []
                    }
            current_results[cache_key] = result

    return current_results


# -----------------------------------test-----------------------------
if __name__ == "__main__":
    # open xlsx file and read the sheet
    wb = openpyxl.load_workbook(MRE_SITE_LIST)

    try: 
        sheet = wb["Master"]

        # step 1: read xlsx file and get header information
        header_dict = get_sheet_header(sheet)

        # step 2: use header information to combine cell information into queires
        site_queries = get_text_query(
            header_dict,
            MRE_QUERY_FIELDS
        ) # post-con: combine w/ names and addrs, split w/ ' '

    finally:
        wb.close()

    # testing
    sliced_queries = site_queries[: 5]

    # step 3: query Google Places API
    geo_tag_information = google_places_api_lookup(GOOGLE_FETCH_HEADER, sliced_queries, GEO_TAG_CACHE_FILE)
    
    # step 4: load cache file
    cache_data = load_json(GEO_TAG_CACHE_FILE)

    # step 5: select place
    place_candidate_lists = place_candidates(cache_data)

    # step 6: put geo tag back in the original xlsx file
    write_geo_tag_to_excel(
        place_candidate_lists,
        MRE_SITE_LIST,
        MRE_QUERY_FIELDS
    )