#!/usr/bin/env python
# coding: utf-8

# ## Documenting Our Functions

# ### Now let's put some work into documenting our code. We're going to add some docstrings to our functions, some inline notes so we can easily read the more complex bits of our script, and a larger explanation at the top of the script that we might move to a Readme.md file:

# In[4]:


"""
This script is used to intake the male survey data from UNICEF and save it to a simple database file after it has been checked 
for duplicates and missing data and after the headers have been properly matched with the data. It expects there to be a 
'mn.csv' file with the data and the 'mn_updated_headers.csv' file. It also expects there to be a SQLite file 
called 'data_wrangling.db' in the data directory. Finally, it expects to utilize the dataset library
(http://dataset.readthedocs.org/en/latest/).

if the script runs without finding any errors, it will save the cleaned data to the 'unicef_survey' table in the SQLite.
The saved data will have the following structure:
    - question: string
    - question_code: string
    - answer: string
    - response_number: integer
    - survey: string
    
The response number can later be used to join entire responses together (i.e., all of response_number 3 come from the same 
interview, etc.).

If you have any questions, please feel free to contact me via ...
"""
from csv import reader
import pickle
import dataset


# In[5]:


def get_rows(file_name):
    """Return a list of rows from a given csv filename."""
    rdr = reader(open(file_name, 'r', encoding='utf-8'))
    return [row for row in rdr]


# In[6]:


def eliminate_mismatches(header_rows, data_rows):
    """
    Return index numbers to skip in a list and final header rows in a list when given header rows and data rows from a
    UNICEF dataset. This function assumes the data_rows object has headers in the first element. It assumes those headers are
    the shortened UNICEF form. It also assumes the first element of each header row in the header data is the shortened UNICEF
    form. It will return the list of indexes to skip in the data rows (ones that don't match properly with headers) as the first
    element and will return the final cleaned header rows as the second element.
    """
    all_short_headers = [h[0] for h in header_rows]
    skip_index = []
    final_header_rows = []

    for header in data_rows[0]:
        if header not in all_short_headers:
            index = data_rows[0].index(header)
            if index not in skip_index:
                skip_index.append(index)
        else:
            for head in header_rows:
                if head[0] == header:
                    final_header_rows.append(head)
                    break
    return skip_index, final_header_rows


# In[7]:


def zip_data(headers, data):
    """
    Return a list of zipped data when given a header list and data list. Assumes the length of data elements per row and the
    length of headers are the same.
    
    example output: [(['question code', 'question summary', 'question text'], 'resp'), ...]
    """
    zipped_data = []
    for drow in data:
        zipped_data.append(zip(headers, drow))
    return zipped_data


# In[8]:


def create_zipped_data(final_header_rows, data_rows, skip_index):
    """
    Returns a list of zipped data rows (matching header and data) when given a list of final header rows, a list of data rows,
    and a list of indexes on those data rows to skip as they don't match properly. The function assumes the first row in the
    data rows contains the original data header values, and will remove those values from the final list.
    """
    new_data = []

    for row in data_rows[1:]:
        new_row = []

        for index, data in enumerate(row):
            if index not in skip_index:
                new_row.append(data)
        new_data.append(new_row)
    zipped_data = zip_data(final_header_rows, new_data)
    # Save the list to a file
    with open('zipped_data.pkl', 'wb') as file:
        pickle.dump(zipped_data, file)
        
    return zipped_data


# In[9]:


# Load the list from the file
def load_zipped_data():
    """retrives the list of zipped_data that was previously had been saved in a .pkl file."""
    with open('zipped_data.pkl', 'rb') as file:
        zipped_data = pickle.load(file)
        return zipped_data


# In[11]:


def find_missing_data(zipped_data):
    """
    Returns a count of how many answers are missing in an entire set of zipped data. This function assumes all responses are
    stored as the second element. It also assumes every response is stored in a list of these matched question, 
    answer groupings. It returns an integer.
    """
    missing_count = 0
    for response in zipped_data:
        for question, answer in response:
            if not answer:
                missing_count += 1
    return missing_count


# In[12]:


def find_duplicate_data(zipped_data):
    """
    Returns a list of unique elements and a number of duplicates found when given a UNICEF zipped_data list. This function 
    assumes that the first three rows of data are structured to have the house, cluster, and line number of the interview and
    uses these values to create a unique key that should not be repeated.
    """
    set_of_keys = set()
    for x in zipped_data:
        unique_key = ''
        for i, row in enumerate(x):
            if i in [0, 1, 2]:
                unique_key += str(row[1])+'-'
        set_of_keys.add(unique_key[:-1])

    uniques = []
    zipped_data = load_zipped_data()
    for x in zipped_data:
        unique_key = ''
        for i, row in enumerate(x):
            if i in [0, 1, 2]:
                unique_key += str(row[1])+'-'
        if not set_of_keys.remove(unique_key[:-1]):
            uniques.append(x)

    return uniques, len(set_of_keys)


# In[13]:


def save_to_sqlitedb(db_file, zipped_data, survey_type):
    """
    When given a path to a SQLite file, the cleaned zipped_data, and the UNICEF survey type that was used, saves the data to
    SQLite in a table called 'unicef_survey' with the following attributes:
        question, question_code, answer, response_number, survey
    """
    db = dataset.connect(db_file)
    table = db['unicef_survey']
    all_rows = []

    for row_num, data in enumerate(zipped_data):
        for question, answer in data:
            data_dict = {
                'question': question[1],
                'question_code': question[0],
                'answer': answer,
                'response_number': row_num,
                'survey': survey_type,
            }
            all_rows.append(data_dict)
            
    table.insert_many(all_rows)


