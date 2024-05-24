# program configurations: global variables


''' data source '''

# edit file name inside the " " in the line below:
file_name = "Karachi Feb 2024.csv"

data_source = f"Data/{file_name}"

file_name= file_name.rsplit('.', 1)[0].lower()

# file_name = "sample_khi_1"
# file_name = "sample_nationwide_1"
# data_source = f"Data/Random_Datasets/{file_name}.csv"


''' data destination CSV ''' 
data_destination_csv = f"Data/Processed/{file_name}_processed.csv"


''' data destination excel '''
data_destination_excel = f"Data/Processed/{file_name}_processed.xlsx"