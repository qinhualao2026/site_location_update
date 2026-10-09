# --------------------------
# parse address information;
# current status: US only
# --------------------------

# get google place component value based on certain 'types' value
def get_address_component(
        address_components, 
        component_type, 
        text_type = "shortText"
):
    for component in address_components:
        if component_type in component.get("types",[]):
            return component.get(text_type, "")

    return ""

# parse site information into relative attribute
def parse_place_information(google_place):
    components = google_place.get("addressComponents", [])

    # common address 
    city = get_address_component(components, "locality")
    state = get_address_component(components, "administrative_area_level_1")
    zip_code = get_address_component(components, "postal_code")
    country = get_address_component(components, "country")

    institution_name = (
        google_place.get("displayName", {}).get("text", "")
    )

    # for U.S. site location:
    if country == 'US':
        street_number = get_address_component(components, "street_number")
        street = get_address_component(components, "route")

        address_1 = " ".join(
            value for value in [street_number, street] if value
        )
    # other countries:
    else:
        state = get_address_component(components, "administrative_area_level_1", "longText")
        country = get_address_component(components, "country", "longText")

        address_parts = []

        for component in components:
            types = component.get("types", [])
            
            # skip common address parts
            if any(
                address_type in types for address_type in [
                    "locality",
                    "administrative_area_level_1",
                    "postal_code",
                    "country"
                ]
            ):
                continue

            value = component.get("longText", "")

            if value:
                address_parts.append(value)

        address_1 = ", ".join(address_parts)

    return {
        "Institution Name": institution_name,
        "Address 1": address_1,
        "Address 2": "",
        "City": city,
        "State/\nProvince": state,
        "Zip/Postal Code": zip_code,
        "Country": country
    }

def parse_new_site(current_new_sites):
    parsed_sites = []

    for item in current_new_sites:
        google_place = item.get("google_place", {})

        parsed_place = parse_place_information(google_place)

        if not parsed_place:
            continue

        parsed_sites.append(parsed_place)

    return parsed_sites

# ----------------------------------test-----------------------------
if __name__ == "__main__":
    from web_watch import get_new_registration_data
    from data_correction import correct_registration_data
    from data_compare import find_new_sites
    from pprint import pprint

    registration_data, current_id = (
        get_new_registration_data()
    )

    corrected_data = correct_registration_data(
        registration_data
    )

    current_new_sites = find_new_sites(
        corrected_data
    )

    new_parsed_site_list = parse_new_us_site(
        current_new_sites
    )

    pprint(new_parsed_site_list)

