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

# --------------    
# find new sites
# --------------
def find_new_sites(data):
    all_site_list = load_json(UPDATED_SITE_CACHE)

    current_new_sites = []

    for item in data:
        # compare w/ database 
        if is_duplicate(item, all_site_list):
            continue

        # Currently, this function only checks against previous site records.
        # Duplicates within the passed-in data are not detected.

        current_new_sites.append(item)

    return current_new_sites

# -----------------
# update site cache
# -----------------
def update_site_cache(current_new_sites):

    if not current_new_sites:
        return

    all_site_list = load_json(UPDATED_SITE_CACHE)
    new_site = load_json(NEW_SITE_LIST_CACHE)

    if not new_site:
        new_site = []

    for item in current_new_sites:
        new_site_record = {
            "institution_name": item["institution_name"],
            "institution_address": item["institution_address"] 
        }

        all_site_list.append(new_site_record)
        new_site.append(new_site_record)

    # save all site list json file 
    save_json(
        all_site_list,
        UPDATED_SITE_CACHE
    )
        
    # save updated site list json file
    save_json(
        new_site,
        NEW_SITE_LIST_CACHE
    )

# -----------------------------------test---------------------------------#
if __name__ == '__main__':

    from web_watch import get_new_registration_data
    from data_correction import correct_registration_data

    registration_data, current_id = (
        get_new_registration_data()
    )

    corrected_data = correct_registration_data(
        registration_data
    )

    current_new_sites = find_new_sites(
        corrected_data
    )

    print(f'current ID: {current_id}')
    print(f'total # of new sites found: {len(current_new_sites)}')
    # pprint(current_new_sites)