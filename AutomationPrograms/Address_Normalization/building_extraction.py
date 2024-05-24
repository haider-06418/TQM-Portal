# Functions for Building Name Extraction: Extracting Building Names using a corpus


# imports
import re
import pandas as pd
from fuzzywuzzy import process, fuzz
import data_preprocessor
import data_processor


# returns None if building name is found to match with pattern
def refine_building_names(building_name):
    if not re.match(r'^(building( all blocks| block)?|block)( [a-zA-Z0-9]+)?$', building_name, re.I):
        return building_name
    return 'None'


# extracts addresses with unidentified building names and correctly identified building names for extraction 
def preparing_extraction(address_df, normalized_df):
    normalized_df = normalized_df.merge(address_df, left_on='Ticket #', right_on='Ticket#', how='left').drop('Ticket#', axis=1)
    
    # lst_addresses = normalized_df[(normalized_df['Building Name'] == 'None') & (normalized_df['Type'] == 'apartment')]['Address'].tolist()
    # lst_ticketnumbers = normalized_df[(normalized_df['Building Name'] == 'None') & (normalized_df['Type'] == 'apartment')]['Ticket #'].tolist()
    lst_addresses = normalized_df[normalized_df['Building Name'] == 'None']['Address'].tolist()
    lst_ticketnumbers = normalized_df[normalized_df['Building Name'] == 'None']['Ticket #'].tolist()
    
    buildings_corpus_lst = data_preprocessor.load_corpus('data/reference_data/buildings_directory.txt')
    
    building_names_df = normalized_df[(normalized_df['Building Name'] != 'None') & (normalized_df['Type'] == 'apartment')]
    building_names_df.loc[:, 'Building Name'] = building_names_df['Building Name'].apply(refine_building_names)
    
    removed_building_addresses = building_names_df[building_names_df['Building Name'] == 'None']['Address'].tolist()
    removed_tickets = building_names_df[building_names_df['Building Name'] == 'None']['Ticket #'].tolist()
    
    lst_addresses.extend(removed_building_addresses)
    lst_ticketnumbers.extend(removed_tickets)
    
    updated_lst_addresses = data_processor.brew_address_list(lst_addresses)
    
    return updated_lst_addresses, buildings_corpus_lst, lst_ticketnumbers


# Additional checking mechanism for building names
def layer2checks(address, buildingname, buildingnamecorpus):
    if buildingname not in address:
        for potiental_building_name in buildingnamecorpus:
            if potiental_building_name in address:
                buildingname = potiental_building_name 
                return buildingname
        return buildingname
    else:
        return True


# Extract building names from addresses based on fuzzy matching with a default adjustable threshold
def extract_building_names(addresses, building_names, threshold=70):
    extracted_names = []
    
    for address in addresses:
        matches = process.extract(address, building_names, limit=1, scorer=fuzz.token_set_ratio)
        best_match, score = matches[0][0], matches[0][1]
        
        if score <= threshold:
            best_match = 'None'
        
        verify_building_name = layer2checks(address, best_match, building_names)
        if verify_building_name == True:
            extracted_names.append(best_match)
        else:
            extracted_names.append(verify_building_name)

    return extracted_names


# Placing extraced building names in the normalized dataframe
def correction(df, ticketnumbers, building_names):
    if len(ticketnumbers) != len(building_names):
        raise ValueError("Both ticketnumbers and building_names should have the same length")

    for ticket, building in zip(ticketnumbers, building_names):
        if building != "None":
            row = df[df['Ticket #'] == ticket]
            
            if row['Type'].values[0] == 'house':
                df.loc[df['Ticket #'] == ticket, 'Type'] = 'apartment'
    
            if row['Building Name'].values[0] == "None":
                df.loc[df['Ticket #'] == ticket, 'Building Name'] = building
                
            else:
                if row['Building #'].values[0] == "None":
                    df.loc[df['Ticket #'] == ticket, 'Building #'] = row['Building Name'].values[0]
                    
                df.loc[df['Ticket #'] == ticket, 'Building Name'] = building
                
    return df


# Building Name Extraction Pipeline
def building_name_extraction_pipeline(df, df_normalized):
    lst_addresses, lst_building_names, lst_ticketnumbers = preparing_extraction(df, df_normalized)
    extracted_building_names = extract_building_names(lst_addresses, lst_building_names)
    corrected_df = correction(df_normalized, lst_ticketnumbers, extracted_building_names)
    return corrected_df
