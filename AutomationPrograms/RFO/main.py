# main python file

import pandas as pd
import functions as support
from config import *


rfo_mapping = support.load_json("Mapping/rfo_mapping.json")
spelling_mapping = support.load_json("Mapping/spelling_mapping.json")


def correct_spelling(input_list, spelling_mapping):
    corrected_list = []

    for sentence in input_list:
        words = sentence.split()
        corrected_words = []

        for word in words:
            corrected_word = spelling_mapping.get(word, word)
            corrected_words.append(corrected_word)

        corrected_sentence = ' '.join(corrected_words)
        corrected_list.append(corrected_sentence)

    return corrected_list


def special_checks(RFO_fetched, queue_name):
    
    DEV_Status = True if queue_name and "dev" in queue_name.lower() else False
    HD_ADT_Status = True if queue_name.lower() == "hd-adt" else False
    
    if RFO_fetched == 'Abnormal Optical Power':
        if DEV_Status == True or HD_ADT_Status == True:
            RFO_updated = 'ADT'
            return RFO_updated
    
    return RFO_fetched


def map_remarks_to_rfo(remarks, queue):
    
    # HD-ADT queue to ADT RFO tap o tap
    HD_ADT_Status = True if queue.lower() == "hd-adt" else False
    if HD_ADT_Status == True:
        rfo = 'ADT'
        return rfo
    
    # keywords which are present in more than one RFO's remarks
    special_mappings = {
        "micro": {"dev": "ADT"},
        "macro": {"dev": "ADT"},
        "pressure": {"dev": "ADT"},
        "cut": {"dev": "ADT"},
        "issue has been resolve": {"dev": "ADT"},
        "link has been restored": {"dev": "ADT"},
        "bend": {"dev": "ADT"}, 
    }

    queue_value = "dev" if queue and "dev" in queue.lower() else "unknown"
    
    for keyword, mappings in special_mappings.items():
        if keyword in remarks:
            rfo = mappings.get(queue_value, "Unknown")
            if rfo != "Unknown":
                return rfo
    
    for rfo, keywords in rfo_mapping.items():
        for keyword in keywords:
            if f' {keyword} ' in f' {remarks} ':
                rfo = special_checks(rfo, queue)
                return rfo
    return "Unknown"

            
def mapping(data_source_path):
    
    # data preprocessing stage
    
    # df = pd.read_csv(data_source_path, encoding='latin1', dtype={0: 'str'})
    file_extension = data_source_path.rsplit('.', 1)[-1].lower()
    if file_extension == 'csv':
        df = pd.read_csv(data_source_path, encoding='latin1', dtype={0: 'str'})
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(data_source_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")
    
    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all')
    
    df['ODN Remarks'] = df['ODN Remarks'].fillna("No Remarks Found")
    lst_odn_remarks = df['ODN Remarks'].tolist()
    lst_odn_remarks_preprocessed = support.brew_ODN_remark(lst_odn_remarks)
    
    print('*** Data Preprocessing Done ***\n')
    
    # rfo spelling correction stage

    lst_odn_remarks_correctedspelling = correct_spelling(lst_odn_remarks_preprocessed, spelling_mapping)

    print('*** Spellings Corrected ***\n')

    # rfo mapping stage 

    df['ODN Remarks Preprocessed'] = lst_odn_remarks_correctedspelling
    # df['ODN Remarks Preprocessed'] = lst_odn_remarks_preprocessed
    
    df['RFO'] = df.apply(lambda row: map_remarks_to_rfo(row['ODN Remarks Preprocessed'], str(row['Queue'])), axis=1)

    df.drop('ODN Remarks Preprocessed', axis=1, inplace=True)

    print('*** RFO Mapping Done ***\n')

    # converting to excel and csv

    # df.to_csv(data_destination_csv, index=False)
    df.to_excel(data_destination_excel, sheet_name = 'Sheet1', index=False)
    
    print('*** Data Saved Successfully ***\n')
    print(f'Processed Data Stored successfully in {data_destination_excel}.\n')

mapping(data_source)
