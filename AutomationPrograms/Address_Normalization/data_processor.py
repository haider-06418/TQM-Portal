# Functions for Data Processing - Address Fields classification


# imports
import data_preprocessor
import random
abbreviations = data_preprocessor.load_json("abbreviations.json")


# performs pre processing functions on the address and returns information packed as a tuple
def pre_processing(address):
    standardized_address = data_preprocessor.lowercase_conversion(address)
    standardized_address = data_preprocessor.remove_multiple_commas(standardized_address)
    # standardized_address = data_preprocessor.remove_punctuation(standardized_address, True)
    standardized_address = data_preprocessor.standard_abbreviations_fix(standardized_address, abbreviations)
    # standardized_address = data_preprocessor.remove_extra_spaces(standardized_address, True)
    standardized_address = data_preprocessor.remove_extra_spaces(standardized_address, False)

    address_type = data_preprocessor.check_address_type(standardized_address)
    tokenized_address = data_preprocessor.standard_tokenization(standardized_address)
    tokenized_address = data_preprocessor.remove_duplicate_tokens(tokenized_address)

    # print(standardized_address)
    # print(address_type)
    # print(tokenized_address)

    return (standardized_address, address_type, tokenized_address)


# preparing unidentified addresses list for building name extraction
def brew_address_list(address_list):
    updated_address_list = [data_preprocessor.lowercase_conversion(address) for address in address_list]
    updated_address_list = [data_preprocessor.remove_multiple_commas(address) for address in updated_address_list]
    updated_address_list = [data_preprocessor.standard_abbreviations_fix(address, abbreviations) for address in updated_address_list]
    updated_address_list = [data_preprocessor.address_trimmer(address) for address in updated_address_list]
    # updated_address_list = [data_preprocessor.remove_punctuation(address) for address in updated_address_list]
    updated_address_list = [data_preprocessor.remove_extra_spaces(address, False) for address in updated_address_list]
    return updated_address_list


# finds index of the desired field, returns none if field not found
def field_finder(field_name, tokenized_list):

    street_keywords = ['street', 'lane']
    road_keywords = ['road', 'highway', 'khayaban', 'avenue', 'boulevard', 'shahrah', 'alley', 'commercial', 'nehr']
    house_keywords = ['house', 'house no', 'house number', 'house #', 'plot']
    apartment_keywords = ['flat', 'flat no', 'flat number', 'flat #', 'apartment', 'suite']
    floor_keywords = ['floor', 'level']
    # area_keywords = ['phase', 'scheme', 'sector', 'town', 'lines']
    area_keywords = ['phase', 'scheme', 'sector'] 
    keywords = []
    
    field_name = field_name.lower()

    if field_name == 'street':
        keywords = street_keywords
    elif field_name == 'road':
        keywords = road_keywords
    elif field_name == 'house':
        keywords = house_keywords
    elif field_name == 'apartment':
        keywords = apartment_keywords
    elif field_name == 'floor':
        keywords = floor_keywords
    elif field_name == 'area':
        keywords = area_keywords

    for index, token in enumerate(tokenized_list):
        if any(keyword in token for keyword in keywords):
            return index
    
    return None


# using a probability based algorithm to classify remaining fields
def probabilistic_identifiers(reference_tokenized_address, remaining_address):

    if len(remaining_address) == 0:
        return [], [], []    

    index_p_scores = []
    count = 0

    for item in remaining_address:
        true_index_in_original = reference_tokenized_address.index(item)+1
        # true_index_in_original = reference_tokenized_address.index(item)
        index_percentage = (true_index_in_original/len(reference_tokenized_address))*100
        index_p_scores.append((count, index_percentage))
        count += 1

    potienal_area = [(index, score) for index, score in index_p_scores if score > 50]
    remaining_fields = [(index, score) for index, score in index_p_scores if score <= 50]

    if len(remaining_fields) >= 2:
        max_score_index = max(remaining_fields, key=lambda x: x[1])[0]
        potienal_building_name_tuple = remaining_fields.pop(max_score_index)
        potienal_building_name = list()
        potienal_building_name.append(potienal_building_name_tuple)

        potienal_building_number = list(remaining_fields)
    
    elif len(remaining_fields) == 1:
        potienal_building_name = list(remaining_fields)
        potienal_building_number = []

    else:
        potienal_building_name, potienal_building_number = [], []

    areas_indexes = [ip_tuple[0] for ip_tuple in potienal_area]
    building_name_indexes = [ip_tuple[0] for ip_tuple in potienal_building_name]
    building_number_indexes = [ip_tuple[0] for ip_tuple in potienal_building_number]

    return areas_indexes, building_name_indexes, building_number_indexes


# creates a random dataset of given size from the complete dataset
def create_random_sample(df, sample_size, selected_columns):
    random_indices = random.sample(range(len(df)), sample_size)
    random_sample = df.loc[random_indices, selected_columns]
    return random_sample


# calculating bias for correct analysis
def calculate_bias(df):
    list_of_addresses = df['Address'].tolist()
    
    bias_count = 0

    house_keywords = ['house', 'house no', 'house number', 'house #', 'plot']
    apartment_keywords = ['flat', 'flat no', 'flat number', 'flat #', 'apartment', 'building', 'suite']
    neighbourhood_keywords = ['defence', 'pechs']

    for address in list_of_addresses:

        standardized_address = data_preprocessor.lowercase_conversion(address)
        standardized_address = data_preprocessor.remove_multiple_commas(standardized_address)
        standardized_address = data_preprocessor.standard_abbreviations_fix(standardized_address, abbreviations)
        standardized_address = data_preprocessor.remove_extra_spaces(standardized_address, False)

        house_found = any(keyword in standardized_address for keyword in house_keywords)
        apartment_found = any(keyword in standardized_address for keyword in apartment_keywords)
        neighbourhood_found = any(keyword in standardized_address for keyword in neighbourhood_keywords)

        if house_found == True and apartment_found == False and 'floor' in standardized_address:
            bias_count += 0.85
        elif house_found and apartment_found and neighbourhood_found:
            bias_count += 0.75

    return int(bias_count)


# analysis of the normalization
def analyze(df, df_normalized, fname, fname_normalized):
    total_addresses = len(df_normalized)

    missing_houseno = df_normalized.loc[df_normalized['Type'] == 'house', 'House #'].isna().sum()
    missing_appartmentno = df_normalized.loc[df_normalized['Type'] == 'apartment', 'Apartment #'].isna().sum()
    missing_buildingname = df_normalized.loc[df_normalized['Type'] == 'apartment', 'Building Name'].isna().sum()

    # buildingname_bias = calculate_bias(df)
    # missing_buildingname = missing_buildingname - buildingname_bias

    type_counts = df_normalized['Type'].value_counts()
    total_houses = type_counts.get('house', 0)
    total_appartments = type_counts.get('apartment', 0)

    total_incorrect_normalized = missing_houseno + missing_appartmentno + missing_buildingname

    total_correct_normalized = total_addresses - total_incorrect_normalized
    percentage_accuracy = (total_correct_normalized/total_addresses)*100
    percentage_accuracy = round(percentage_accuracy, 2)

    print('Run Stats: \n')
    print(f'Source file: {fname}')
    print(f'Destination file: {fname_normalized}\n')
    print(f'Total # of Addresses: {total_addresses}')
    print(f'Total Correct Normalizations: {total_correct_normalized}')
    print(f'Total Incorrect Normalizations: {total_incorrect_normalized}\n')
    print(f'Success Percentage: {percentage_accuracy}%\n')
    print(f'Incorrect Normalized Fields Info: \n')
    print(f'Field Name: House #')
    print(f'Total # of Houses: {total_houses}')
    print(f'Missing House #: {missing_houseno}')
    print(f'Success Percentage: {round(((total_houses-missing_houseno)/total_houses)*100, 2)}%\n')
    print(f'Field Name: Apartment #')
    print(f'Total # of Appartments: {total_appartments}')
    print(f'Missing Apartment #: {missing_appartmentno}')
    print(f'Success Percentage: {round(((total_appartments-missing_appartmentno)/total_appartments)*100, 2)}%\n')
    print(f'Field Name: Building Name')
    print(f'Total # of Appartments: {total_appartments}')
    print(f'Missing Building Name: {missing_buildingname}')
    print(f'Success Percentage: {round(((total_appartments-missing_buildingname)/total_appartments)*100, 2)}%\n')
