from config import UPDATED_SITE_CACHE, NEW_SITE_LIST_CACHE
from cache_utils import load_json, save_json
from pprint import pprint

def is_duplicate(item, existing_list):
    name = item["institution_name"]
    address = item["institution_address"]

    for existing_item in existing_list:
        existing_name = existing_item["institution_name"]
        existing_address = existing_item["institution_address"]

        if (
            name == existing_name
            and address == existing_address
        ):
            return True

    return False

# -------------------------        
# update all site list file
# -------------------------
def update_site_data(data):

    all_site_list = load_json(UPDATED_SITE_CACHE)
    new_site = load_json(NEW_SITE_LIST_CACHE)

    # NEW_SITE_LAST_CACHE may not exist on the first run
    if not new_site:
        new_site = []

    data_updated = False

    current_new_sites = []

    for item in data:
        if is_duplicate(item, all_site_list):
            continue

        all_site_list.append(item)
        new_site.append(item)
        current_new_sites.append(item)

        data_updated = True

    # update  ALL site list file and new site list cache
    if data_updated:
        save_json(
            all_site_list,
            UPDATED_SITE_CACHE
        )
        save_json(
            new_site,
            NEW_SITE_LIST_CACHE
        )

    return current_new_sites


# todo: Need Persistance Data to track: 
# 1. latest unique site list
# 2. update current ID value

if __name__ == '__main__':

    from web_watch import get_new_registration_data
    from data_correction import correct_registration_data

    registration_data, current_id = (
        get_new_registration_data()
    )

    corrected_data = correct_registration_data(
        registration_data
    )

    current_new_sites = update_site_data(
        corrected_data
    )

    print(f'current ID: {current_id}')
    print(f'total # of new sites added: {len(current_new_sites)}')
    pprint(current_new_sites)