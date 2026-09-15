from pprint import pprint

from web_watch import get_new_registration_data, update_last_id
from data_correction import correct_registration_data
from data_compare import update_site_data

def main():
    # step 1: get new registration data
    registration_data, current_id = (
        get_new_registration_data()
    )

    # no new registration:
    if not registration_data:
        print("no new registration.")
        return
    print(f'# of new registration: {len(registration_data)}')

    # step 2: correct data w/ Google Places API
    corrected_data = correct_registration_data(registration_data)

    print(f'# of corrected sites data: {len(corrected_data)}')

    # step 3: compare w/ existing site data
    new_sites = update_site_data(corrected_data)

    print(f'# of new sites added: {len(new_sites)}')
    pprint(new_sites)

    # step 4: update checkpoint
    update_last_id(current_id)
    print(f"Last ID updated to: {current_id}")

if __name__ == '__main__':
    main()