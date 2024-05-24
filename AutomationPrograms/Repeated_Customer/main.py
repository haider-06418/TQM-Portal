# main python file

import pandas as pd
from config import *

def repeated_customers(df):
    # Group by 'Cell #' and count the number of tickets for each customer
    customer_counts = df.groupby('Cell #').size().reset_index(name='Ticket Count')

    # Filter customers with more than one ticket
    repeated_customers_df = customer_counts[customer_counts['Ticket Count'] > 1]
    
    repeated_customers_count_df = repeated_customers_df
    
    repeated_customers_count_df = repeated_customers_count_df.drop_duplicates(subset='Cell #')
    repeated_customers_count_df = repeated_customers_count_df[['Cell #', 'Ticket Count']]
    repeated_customers_count_df = repeated_customers_count_df.sort_values(by='Ticket Count', ascending=False)

    # Merge with the original DataFrame to get the details of repeated customers
    result_df = pd.merge(df, repeated_customers_df, on='Cell #', how='right')
    result_df = result_df.sort_values(by=['Ticket Count', 'Cell #'], ascending=[False, True])

    return result_df, repeated_customers_count_df

def main():
    # df = pd.read_csv(data_source, encoding='latin1', dtype={0: 'str'})
    file_extension = data_source.rsplit('.', 1)[-1].lower()
    if file_extension == 'csv':
        df = pd.read_csv(data_source, encoding='latin1', dtype={0: 'str'})
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(data_source)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")
    print('*** Data Loaded ***\n')
    
    df_repeated, df_repeated_count = repeated_customers(df)
    print('*** Data Filtered for Repeated Customers ***\n')
    
    # df_repeated.to_csv(data_destination_csv, index=False)
    # df_repeated.to_excel(data_destination_excel, sheet_name = 'Sheet1', index=False)
    # df_repeated_count.to_excel(data_destination_excel, sheet_name = 'Sheet2', index=False)
    
    with pd.ExcelWriter(data_destination_excel) as writer:
        df_repeated.to_excel(writer, sheet_name='Sheet1', index=False)
        df_repeated_count.to_excel(writer, sheet_name='Sheet2', index=False)
    
    print('*** Data Saved Successfully ***\n')
    print(f'Processed Data Stored successfully in {data_destination_excel}.\n')

main()
