# functions for data preprocessing


import string
import json
import re
import random


# convert text to lowercase
def lowercase_conversion(text_str):
    return text_str.lower()


# remove all or chosen punctuation from text
def remove_punctuation(text_str, commas = False):
    if commas == True:
        punctuation = string.punctuation.replace(",", "")
        # punctuation = punctuation.replace("#", "")
        # punctuation = punctuation.replace("-", "")
    else:
        punctuation = string.punctuation 

    return text_str.translate(str.maketrans('', '', punctuation)) # replaces punctuation with none
    # return text_str.translate(str.maketrans(punctuation, ' ' * len(punctuation))) # replaces punctuation with space


# remove all or leading/trailing spaces
def remove_extra_spaces(text_str, allspaces = False):
    if allspaces == True:
        cleaned_text = text_str.replace(" ", "")
        return cleaned_text
    else:
        words = text_str.split()
        cleaned_text = ' '.join(words)
        return cleaned_text
    

# add space where there is punctuation 
def add_spaces_with_punctuation(sentence):
    punctuation_pattern = r'([{}])'.format(re.escape(string.punctuation))
    spaced_sentence = re.sub(punctuation_pattern, r' \1 ', sentence)
    return spaced_sentence


# tokenization based on either comma or whitespace
def tokenize_string(input_string, commas=True):
    if commas:
        tokens = input_string.split(',')
    else:
        tokens = input_string.split()
    return tokens


# remove duplicates from tokenized ODN remark
def remove_duplicate_tokens(tokenized_remark):
    tokenized_remark = [item.strip() for item in tokenized_remark]
    return list(dict.fromkeys(tokenized_remark[::-1]))[::-1]


# load json file
def load_json(file_name):
    with open(file_name, 'r') as file:
        dictionary = json.load(file)
    return dictionary


# standardize abbreviations
def standard_abbreviations_fix(ODN_remark_str, abbreviation_mapping):
    ODN_remark_str = add_spaces_with_punctuation(ODN_remark_str)
    words = ODN_remark_str.split()
    standardized_words = [abbreviation_mapping.get(word.translate(str.maketrans('', '', string.punctuation)), word) for word in words]
    standardized_ODN_remark = ' '.join(standardized_words)
    return standardized_ODN_remark


# creates a random dataset of given size from the complete dataset
def create_random_sample(df, sample_size, selected_columns):
    random_indices = random.sample(range(len(df)), sample_size)
    random_sample = df.loc[random_indices, selected_columns]
    return random_sample
    

# # performs pre processing functions on the ODN remark string
# def pre_processing(ODN_remark):
#     standardized_ODN_remark = lowercase_conversion(ODN_remark)
#     standardized_ODN_remark = remove_punctuation(standardized_ODN_remark, True)
#     # standardized_ODN_remark = standard_abbreviations_fix(standardized_ODN_remrks, abbreviations)
#     standardized_ODN_remark = remove_extra_spaces(standardized_ODN_remark, False)
#     return standardized_ODN_remark


# preparing ODN remarks for RFO designation
def brew_ODN_remark(ODN_remark_list):
    updated_ODN_remark_list = [lowercase_conversion(ODN_remark) for ODN_remark in ODN_remark_list]
    # updated_ODN_remark_list = [standard_abbreviations_fix(ODN_remark, abbreviations) for ODN_remark in updated_ODN_remark_list]
    updated_ODN_remark_list = [remove_punctuation(ODN_remark) for ODN_remark in updated_ODN_remark_list]
    updated_ODN_remark_list = [remove_extra_spaces(ODN_remark, False) for ODN_remark in updated_ODN_remark_list]
    # updated_ODN_remark_list = [tokenize_string(ODN_remark, False) for ODN_remark in updated_ODN_remark_list]
    return updated_ODN_remark_list