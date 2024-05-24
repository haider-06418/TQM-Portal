# program configurations: global variables

''' file name '''
file_name = "tickets_raw_extracted.csv"

''' data source '''
data_source = f"Data/{file_name}"

file_name= file_name.rsplit('.', 1)[0].lower()

''' data destination CSV ''' 
data_destination_csv = f"Data/Processed/{file_name}_processed.csv"

''' data destination excel '''
data_destination_excel = f"Data/Processed/{file_name}_processed.xlsx"