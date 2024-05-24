# main python file

import pandas as pd
from config import *
from datetime import datetime
import queues as queueinfo

def extract_city(df):
    df = df.copy()
    df['Customer User'].fillna('Information Missing', inplace=True)
    customer_info_list = df['Customer User'].tolist()
    city_list = []
    for customer_info in customer_info_list:
        if customer_info == 'Information Missing':
            city_list.append('Missing')
        else:
            local_customer_info = customer_info.split("|")
            customer_address = local_customer_info[-2]
            customer_address_token = customer_address.split(",") 
            customer_city = customer_address_token[-1].strip()
            city_list.append(customer_city)
    df['City'] = city_list
    return df


def separate_dataframes_by_city(df):
    city_dataframes = []
    unique_cities = df['City'].unique()
    for city in unique_cities:
        city_df = df[df['City'] == city]
        city_df = city_df.sort_values(by='Total Hours', ascending=False)
        city_dataframes.append(city_df)
    return city_dataframes


def out_of_TAT(df):
    df['Created'] = pd.to_datetime(df['Created'])
    
    current_time = datetime.now()
    df['Total Hours'] = (current_time - df['Created']).dt.total_seconds() / 3600
    
    df['Total Hours'] = df['Total Hours'].round().astype(int)
    
    df = extract_city(df)

    condition = (df['City'].isin(['Karachi', 'Lahore']) & (df['Total Hours'] > 48)) | (~df['City'].isin(['Karachi', 'Lahore']) & (df['Total Hours'] > 24))
    
    filtered_df = df[condition] 
        
    filtered_df = filtered_df.sort_values(by='Total Hours', ascending=False)
    
    return filtered_df


def main():
    file_extension = data_source.rsplit('.', 1)[-1].lower()
    if file_extension == 'csv':
        df = pd.read_csv(data_source, encoding='latin1', dtype={0: 'str'})
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(data_source)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")
    print('*** Data Loaded ***\n')

    # Existing out_of_TAT functionality
    df_tat_exceed = out_of_TAT(df)
    print('*** Data Scanned for Out of TAT Tickets ***\n')
    
    # Existing city-wise distribution
    df_cities_list = separate_dataframes_by_city(df_tat_exceed)
    print('*** Data Sorted City Wise ***\n')
    
    # Saving city-wise distribution
    with pd.ExcelWriter(data_destination_excel) as writer:
        df_tat_exceed.to_excel(writer, sheet_name='All', index=False)
        for city_df in df_cities_list:   
            city_df.to_excel(writer, sheet_name=city_df['City'].iloc[0], index=False)

    # Create separate DataFrames for each queue
    for file_index, queues in enumerate(queueinfo.queue_sheets):
        queue_dfs = []
        for queue in queues:
            queue_df = df_tat_exceed[df_tat_exceed['Queue'].isin(queue)]
            queue_dfs.append(queue_df)
        
        # Saving the DataFrame for each queue in a separate sheet
        with pd.ExcelWriter(f"Data/Processed/{folder_name}/{file_name}_processed_file_{queueinfo.queue_file_names[file_index]}.xlsx") as queue_writer:
            for sheet_index, queue_df in enumerate(queue_dfs):
                sheet_name = queueinfo.queue_sheet_names[file_index][sheet_index]
                queue_df.to_excel(queue_writer, sheet_name=sheet_name, index=False)

    print('*** Data Saved Successfully ***\n')
    print(f'Processed Data Stored successfully.\n')


main()
