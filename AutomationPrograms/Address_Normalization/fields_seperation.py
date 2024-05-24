# Functions for Fields Seperation - Address Fields Seperation of misplaced fields due to missing comma leading to inaccurate tokenization


# imports 
import re


# identifing misplaced fields
def fields_seperation(tokenized_list):
    keyword_lists = {
        'House': ['house', 'house no', 'house number', 'house #', 'plot'],
        'Apartment': ['flat', 'flat no', 'flat number', 'flat #', 'apartment', 'suite', 'floor', 'fl', 'level'],
        'Street': ['street', 'lane'],
        'Road': ['road', 'highway', 'khayaban', 'avenue', 'boulevard', 'shahrah', 'alley', 'commercial'],
        'Area': ['phase', 'scheme', 'sector'],
    }

    sep_identify = []
    index_count = 0

    for item in tokenized_list:
        fields_found = []        
        for field, keyword_list in keyword_lists.items():
            if any(re.search(r'\b' + re.escape(keyword) + r'\b', item, re.I) for keyword in keyword_list):
                if field not in fields_found:
                    fields_found.append(field)

        if len(fields_found) > 1:
            sep_identify.append((index_count, fields_found))

        index_count += 1
     
    return sep_identify


# house and street seperation in defense addresses
def separate_house_street_defense(s):
    match = re.match(r"(house\s#\s\w\s-\s\d+(?:\s?/\s?\d*)?\s?)(.*)", s, re.I)
    if not match:
        match = re.match(r"(house\s#\s\d+(?:\s?/\s?\d*)?\s?)(.*)", s, re.I)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None


# layer 1 checks and correction
def layer1checks(tokenized_list, data):
    tokenized_list = list(tokenized_list)
    to_seperate_fields = fields_seperation(tokenized_list)

    if len(to_seperate_fields) == 0:
        return None
    
    defense_house_checker = False

    if data['Type'] == ['house']:
        if data['Neighbourhood'] == ['defence'] or data['Neighbourhood'] == ['clifton']:
            defense_house_checker = True

    for fields_seperation_info in to_seperate_fields:

        if fields_seperation_info[1] == ['House', 'Street']:
            
            if defense_house_checker == True:
                # defense house / street seperator
                houseNo, street = separate_house_street_defense(tokenized_list[fields_seperation_info[0]])
                if (houseNo, street) != (None, None):
                    tokenized_list.pop(fields_seperation_info[0])
                    tokenized_list.insert(0, houseNo)
                    tokenized_list.insert(1, street)

            else:
                # generic house / street seperator
                houseNo, street = separate_house_street_defense(tokenized_list[fields_seperation_info[0]])
                if (houseNo, street) != (None, None):
                    tokenized_list.pop(fields_seperation_info[0])
                    tokenized_list.insert(0, houseNo)
                    tokenized_list.insert(1, street)

    return tokenized_list