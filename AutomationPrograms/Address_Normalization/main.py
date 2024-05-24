''' Address Normalization for Pakistani Based Addresses

The primary objective of this project is to develop a comprehensive address normalization system tailored specifically for 
Pakistani addresses. The system will transform addresses from diverse formats into a standardized structure that adheres to 
predefined guidelines and rules. By achieving consistency and uniformity in address data, the project aims to enhance data quality,
facilitate efficient address matching, enable precise geocoding, and simplify address-based searches and analysis. 

Process Overview:

Stage 1: Uniformaty - converting to lowercase and eradicating whitespaces
Stage 2: Standardization of Abbreviations
Stage 3: Address Parsing and Normalization
Stage 4: Building Name Extraction - using Levenshtein distance
Stage 5: Percentage accuracy

For more information please refer to README.md or the project report file. '''


# imports 
import data_preprocessor
import data_processor
import fields_seperation
import building_extraction
from config import *
import pandas as pd
abbreviations = data_preprocessor.load_json("abbreviations.json")


# USER DEFINED
columns = ['Ticket #', 'Type', 'House #', 'Apartment #', 'Building #', 'Building Name', 'Street', 'Road', 'Area & Sub Area', 'Neighbourhood', 'City']
file_extension = fname.rsplit('.', 1)[-1].lower()
if file_extension == 'csv':
    df_raw = data_preprocessor.load_corpus(fname, pandas = True, header = True)
elif file_extension in ['xls', 'xlsx']:
    df_raw = pd.read_excel(fname)
else:
    raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.") 
# df_raw = data_preprocessor.load_corpus(fname, pandas = True, header = True)
df_1 = df_raw.dropna(how='all')
df_2 = df_1.dropna(axis=1, how='all')
df = df_2.dropna(how='any')
df = df.copy()
df.rename(columns={'ticket #': 'ticket#'}, inplace=True)
# df = df.fillna('Information not found')
# df = df.drop(columns=columns_to_drop, axis=1)


# creating test data to normalize

# ideal test data size = 2% of original data size = 2% of 213874 = 4277.48 = 4275 (randomly generated)

# test = data_processor.create_random_sample(df, 40275, ['Ticket#', 'Address'])  

# test2 = df[['Ticket#', 'Address']][0:20] 
# test3 = data_processor.create_random_sample(df, 50, ['Ticket#', 'Address'])


# dataframe for storing normalized addresses 
address_df = data_preprocessor.create_dataframe(columns)


print('****** PREREQUISITIES COMPLETE ******\n')


# parsing and normalization

def parse(dataframe):

    global address_df

    list_of_addresses = dataframe['Address'].tolist()
    tickets = dataframe['Ticket#'].tolist()
    
    for index in range(len(dataframe)):
        ticketno = tickets[index]
        address = list_of_addresses[index]

        data = {'Ticket #': [], 'Type': [], 'House #': [], 'Apartment #': [], 'Building #': [], 'Building Name': [], 'Street': [], 'Road': [], 'Area & Sub Area': [], 'Neighbourhood': [], 'City': []}
        
        address_info = data_processor.pre_processing(address)
        address_type = address_info[1]
        tokenized_address = address_info[2]
        reference_tokenized_address = list(tokenized_address)

        ''' Ticket # '''
        data['Ticket #'].append(ticketno)

        ''' Type '''
        data['Type'].append(address_type)

        ''' City '''
        data['City'].append(tokenized_address.pop(-1).strip())
        
        
        ''' Road '''
        road_index = data_processor.field_finder('road', tokenized_address)
        if road_index is not None:
            data['Road'].append(tokenized_address.pop(road_index).strip())
        else:
            data['Road'].append('None')
        
        road_index = data_processor.field_finder('road', tokenized_address)
        if road_index is not None:
            data['Road'].append(tokenized_address.pop(road_index).strip())
            value_lst = data['Road']
            joined_string = ', '.join(value_lst)
            data['Road'] = [joined_string.strip()]
            

        ''' Neighbourhood '''
        data['Neighbourhood'].append(tokenized_address.pop(-1).strip())


        ''' Layer 1 Field Seperation Checks'''
        layer1_tokenized_address = fields_seperation.layer1checks(tokenized_address, data)

        if layer1_tokenized_address is not None:
            tokenized_address = layer1_tokenized_address


        # ''' Road '''
        # road_index = data_processor.field_finder('road', tokenized_address)
        # if road_index is not None:
        #     data['Road'].append(tokenized_address.pop(road_index).strip())
        # else:
        #     data['Road'].append('None')
        
        # road_index = data_processor.field_finder('road', tokenized_address)
        # if road_index is not None:
        #     data['Road'].append(tokenized_address.pop(road_index).strip())
        #     value_lst = data['Road']
        #     joined_string = ', '.join(value_lst)
        #     data['Road'] = [joined_string.strip()]


        ''' Street '''
        street_index = data_processor.field_finder('street', tokenized_address)
        if street_index is not None:
            data['Street'].append(tokenized_address.pop(street_index).strip())
        else:
            data['Street'].append('None')

        street_index = data_processor.field_finder('street', tokenized_address)
        if street_index is not None:
            data['Street'].append(tokenized_address.pop(street_index).strip())
            value_lst = data['Street']
            joined_string = ', '.join(value_lst)
            data['Street'] = [joined_string.strip()]
        

        '''Appartment # '''
        appartment_index = data_processor.field_finder('apartment', tokenized_address)
        if appartment_index is not None:
            data['Apartment #'].append(tokenized_address.pop(appartment_index).strip())
        else:
             data['Apartment #'].append('None')

        floor_index = data_processor.field_finder('floor', tokenized_address)
        if floor_index is not None:
            if data['Apartment #'] == ['None']:
                data['Apartment #'] = [tokenized_address.pop(floor_index).strip()]
            else:
                data['Apartment #'].append(tokenized_address.pop(floor_index))
                value_lst = data['Apartment #']
                joined_string = ' '.join(value_lst)
                data['Apartment #'] = [joined_string.strip()]


        ''' House # '''
        house_index = data_processor.field_finder('house', tokenized_address)
        if house_index is not None:
            data['House #'].append(tokenized_address.pop(house_index).strip())
        else:
            data['House #'].append('None')

        
        ''' Area/Sub Area '''
        area_index = data_processor.field_finder('area', tokenized_address)
        if area_index is not None:
            data['Area & Sub Area'].append(tokenized_address.pop(area_index).strip())
        else:
            data['Area & Sub Area'].append('None')

        p_area_index, p_buildingname_index, p_buildingnumber_index = data_processor.probabilistic_identifiers(reference_tokenized_address, tokenized_address)
            
        if len(p_area_index) > 0:
                if data['Area & Sub Area'] != ['None']:
                    for index in p_area_index:
                        data['Area & Sub Area'].append(tokenized_address[index].strip())
                    value_lst = data['Area & Sub Area']
                    joined_string = ', '.join(value_lst)
                    data['Area & Sub Area'] = [joined_string.strip()]
                else:
                    data['Area & Sub Area'] = []
                    for index in p_area_index:
                        data['Area & Sub Area'].append(tokenized_address[index].strip())
                    value_lst = data['Area & Sub Area']
                    joined_string = ', '.join(value_lst)
                    data['Area & Sub Area'] = [joined_string.strip()]

        # for index in sorted(p_area_index, reverse=True):
        #     tokenized_address.pop(index)

        
        if address_type == 'house':
            if len(p_buildingname_index) + len(p_buildingnumber_index) > 0:
                area_indexes_more = p_buildingnumber_index + p_buildingname_index 

                if data['Area & Sub Area'] != ['None']:
                        temp = data['Area & Sub Area']
                        data['Area & Sub Area'] = []
                        for index in area_indexes_more:
                            data['Area & Sub Area'].append(tokenized_address[index].strip())
                        value_lst = list(data['Area & Sub Area'])
                        for x in temp:
                            value_lst.append(x)
                        joined_string = ', '.join(value_lst)
                        data['Area & Sub Area'] = [joined_string.strip()]
                else:
                    data['Area & Sub Area'] = []
                    for index in area_indexes_more:
                        data['Area & Sub Area'].append(tokenized_address[index].strip())
                    value_lst = data['Area & Sub Area']
                    joined_string = ', '.join(value_lst)
                    data['Area & Sub Area'] = [joined_string.strip()]

                # for index in sorted(area_indexes_more, reverse=True):
                #     tokenized_address.pop(index)    
        else:
            ''' Building Name '''
            if len(p_buildingname_index)>0:
                for index in p_buildingname_index:
                    data['Building Name'].append(tokenized_address[index].strip())
                value_lst = data['Building Name']
                joined_string = ', '.join(value_lst)
                data['Building Name'] = [joined_string.strip()]

            ''' Building Number '''
            if len(p_buildingnumber_index)>0:
                for index in p_buildingnumber_index:
                    data['Building #'].append(tokenized_address[index].strip())
                value_lst = data['Building #']
                joined_string = ', '.join(value_lst)
                data['Building #'] = [joined_string.strip()]

            # if len(tokenized_address) > 0:
            #     if len(p_area_index) > 0:
            #         for index in sorted(p_area_index, reverse=True):
            #             tokenized_address.pop(index)

            # if len(tokenized_address) > 0:
            #     if len(p_buildingname_index) > 0:
            #         for index in sorted(p_buildingname_index, reverse=True):
            #             tokenized_address.pop(index) 

            # if len(tokenized_address) > 0:
            #     if len(p_buildingnumber_index) > 0:
            #         for index in sorted(p_buildingnumber_index, reverse=True):
            #             tokenized_address.pop(index)


        ''' Shifting Entries '''
        if address_type == 'house' and data['House #'] == ['None'] and data['Apartment #'] != ['None']:
            data['House #'] = data['Apartment #']
            data['Apartment #'] = []


        ''' Null Entires'''
        for field in data:
            if len(data[field]) == 0:
                data[field].append('None')
      

        df_temp = data_preprocessor.create_dataframe(columns, data, datacheck=True)
        address_df = pd.concat([address_df, df_temp], axis=0)

    return address_df


# calling parse function

parse(df)

# parse(test)

# parse(test2)
# parse(test3)


print('****** DATA PREPROCESSING DONE ******\n')
print('****** DATA NORMALIZATION DONE ******\n')


# building extraction for unidentified buildings

print('**** INITIALIZING BUILDING EXTRACTION ****\n')

normalized_df = building_extraction.building_name_extraction_pipeline(df, address_df)

print('****** BUILDING EXTRACTION DONE ******\n')


# Renaming columns
normalized_df.rename(columns={'Area & Sub Area': 'Sub Area', 'Neighbourhood': 'Area'}, inplace=True)

# storing processed data

# address_df.to_csv(fname_normalized, index=False)
# address_df.to_excel(fname_normalized_excel, sheet_name = 'Sheet1', index=False)

normalized_df.to_csv(fname_normalized, index=False)
normalized_df.to_excel(fname_normalized_excel, sheet_name = 'Sheet1', index=False)


print('********* DATA STORAGE DONE *********\n')
print(f'Processed Data Stored successfully in {fname_normalized}.\n')

# analysis of normalization
df_normalized = data_preprocessor.load_corpus(fname_normalized , pandas = True, header = True)
data_processor.analyze(df, df_normalized, fname, fname_normalized)