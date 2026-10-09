from pprint import pprint

from web_watch import get_new_registration_data, update_last_id
from data_correction import correct_registration_data
from data_compare import find_new_sites, update_site_cache
from address_utils import parse_new_site
from excel_utils import write_site_to_excel
from config import MRE_SITE_LIST

def main():
    # step 1: get new registration data
    registration_data, current_id = (
        get_new_registration_data()
    )

    # no new registration:
    if not registration_data:
        print("no new registration will be added at this time.")
        return
    
    print(f'# of new registration: {len(registration_data)}')

    # step 2: correct data w/ Google Places API
    corrected_data = correct_registration_data(registration_data)

    print(f'# of corrected sites data: {len(corrected_data)}')

    # step 3: compare w/ existing site data
    new_sites = find_new_sites(corrected_data)

    print(f'# of new sites added: {len(new_sites)}')
    pprint(new_sites)

    # ---------------------------parse address into excel spreadsheet -----------
    
    # step 4: pick us address and parse address into separate components
    parsed_site_list = parse_new_site(
        new_sites
    )

    # write parsed address info into excel file
    write_site_to_excel(parsed_site_list, MRE_SITE_LIST)

    # step 5: update site cache
    update_site_cache(new_sites)

    # final step: update checkpoint
    update_last_id(current_id)
    print(f"Last ID updated to: {current_id}")

if __name__ == '__main__':
    main()