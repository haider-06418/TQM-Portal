# pip dependencies

# pip install -r requirements.txt


# program configurations: global variables

''' Place file in Data folder and enter it's name enclosed in the " " below under the file name field '''


''' file name '''
file_name = "open_tickets.csv"
# file_name = "Cases_Created_26.csv"



    
''''    ---- DO NOT EDIT BELOW THIS LINE --- '''

from datetime import datetime
from pathlib import Path
import os

def get_path_absolute_till_project_folder():
    script_file_path = os.path.abspath(__file__)
    project_folder_path = os.path.dirname(script_file_path)
    return project_folder_path

def get_folder(work_flow):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    foldername = work_flow + ' run ' + formatted_datetime
    folder_path_str = get_path_absolute_till_project_folder() + f"/Data/Processed/{foldername}" 
    folder_path = Path(folder_path_str)
    folder_path.mkdir(parents=True, exist_ok=True)  
    return foldername

folder_name = get_folder('Out of TAT')

''' data source '''
data_source = f"Data/{file_name}"

file_name= file_name.rsplit('.', 1)[0].lower()

''' data destination CSV ''' 
# data_destination_csv = f"Data/Processed/{folder_name}/{file_name}_processed.csv"

''' data destination excel '''
data_destination_excel = f"Data/Processed/{folder_name}/{file_name}_processed_city.xlsx"