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

import logging
from log_config import setup_logging

# adding logger object
logger = logging.getLogger(__name__)

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

    # record cache initiation
    logger.info(
        "Geo tag cache ready | file=%s | entries=%d",
        cache_file_path,
        len(cache)
    )

    # store current updating site list
    current_results = {}

    # Reset counters for each lookup run; api_calls includes failed requests.
    skipped_empty = 0
    cache_hits = 0
    api_calls = 0
    api_failed = 0

    with requests.Session() as session:
        for item in tqdm(query_list, desc="Looking up Google Place API:"):

            site_name = item.strip()

            if not site_name:
                # Count empty queries before skipping them.
                skipped_empty += 1
                continue

            cache_key = site_name

            # check query text existed in google places cache file
            if cache_key in cache:
                # Count cache hits, including repeated queries in this run.
                cache_hits += 1
                
                # [DEBUG] level logging
                logger.debug(
                    "Geo tag cache hit | query=%s",
                    cache_key
                )

                result = cache[cache_key]
            else:
                try:

                    # [DEBUG] level logging
                    logger.debug(
                        "Google Places API request started | query=%s",
                        site_name
                    )
                    
                    # Count each request attempt before calling the API.
                    api_calls += 1
                    result = query_google_places(
                        site_name,
                        session,
                        url,
                        google_fetch_headers
                    )

                    # logging
                    logger.debug(
                        "Google Places API request completed | query=%s | place_count=%d",
                        site_name,
                        len(result.get("places", []))
                    )

                    cache[cache_key] = result
                    save_json(cache, cache_file_path)

                    # logging
                    logger.debug(
                        "Geo tag cache saved |  file=%s | query=%s | entries=%d",
                        cache_file_path,
                        cache_key,
                        len(cache)
                    )

                    time.sleep(sleep_time)

                except requests.RequestException as e:
                    # Count failures separately from successful empty responses.
                    api_failed += 1
                    logger.exception(
                        "Google Places API request failed | query=%s",
                        site_name
                    )

                    result = {
                        'places': []
                    }
            current_results[cache_key] = result

    # Summarize input entries; duplicate query keys may share one result.
    logger.info(
        "Google Places lookup finished | total=%d | skipped_empty=%d "
        "| cache_hits=%d | api_calls=%d | api_failed=%d",
        len(query_list),
        skipped_empty,
        cache_hits,
        api_calls,
        api_failed,
    )

    return current_results


# -----------------------------------test-----------------------------
if __name__ == "__main__":
    # start logging
    setup_logging()

    logger.info(
        "Geo tag update started | excel=%s | sheet=%s",
        MRE_SITE_LIST,
        "Master"
    )
    
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

    # record total number of quries and number of sliced quries
    logger.info(
        "Quries prepared | total=%d | selected=%d",
        len(site_queries),
        len(site_queries)
    )

    # step 3: query Google Places API
    geo_tag_information = google_places_api_lookup(GOOGLE_FETCH_HEADER, site_queries, GEO_TAG_CACHE_FILE)
    
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
