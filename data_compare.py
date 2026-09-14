from data_correction import trimmed_data
from data_unify import unique_site_list, delete_duplicate
from pprint import pprint

combined_data = trimmed_data + unique_site_list

updated_data = delete_duplicate(combined_data, "institution_name", "institution_address")

if __name__ == '__main__':

    print(f'before update: {len(unique_site_list)}')
    print(f"{len(combined_data)}")
    print(f'{len(updated_data)}')

    number_of_updated = len(updated_data) - len(unique_site_list)

    pprint(updated_data[: number_of_updated])

