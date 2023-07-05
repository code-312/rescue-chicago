AGE_DICT={
    'Baby':'0',
    'Young':'1',
    'Adult':'2',
    'Senior':'3'
}

SIZE_DICT={
    'Small':'0',
    'Medium':'1',
    'Large': '2',
    'Extra Large': '3'
}

TARGET_COLS = ["coat", "organization_name", "breed_primary", "breed_secondary", 
               "color_primary", "color_secondary", "color_tertiary", "city", "state"]

BINARY_COLS = ["breed_mixed", "breed_unknown", "good_with_children", "good_with_dogs", 
               "good_with_cats", "attribute_spayed_neutered", "attribute_house_trained", 
               "attribute_shots_current", "attribute_special_needs"]
