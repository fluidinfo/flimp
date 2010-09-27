"""
Turns a filename into a list of deserialized items based upon csv data
"""
import csv

def clean_header(header):
    """
    A simple default "normalizer" to clean each header of the CSV file
    """
    # strip or underscore whitespace and turn to lowercase
    return header.strip().replace(' ', '_').lower()

def clean_row_item(item):
    """
    A simple default "normalizer" to clean/cast an item found in a row in the
    CSV file.

    We want to cast the values appropriately:

        "1" - return an integer
        "1.2" - return a float
        "True" - case insensitive check to return a boolean
        "" - None
        "a string" - return the string
    """
    stripped_item = item.strip() # allows us to check for numeric value
    if stripped_item.isdigit(): # is the value an integer?
        return int(stripped_item)
    try:
        value = float(stripped_item) # is the value a float?
        return value
    except:
        pass # fail silently and continue to attempt to cast
    bool_check = stripped_item.lower() # normalise
    if bool_check == "true": # is this a representation of True?
        return True
    elif bool_check == "false": # or False?
        return False
    if not item: # does it contain anything..?
        return None
    return item # just return it as the string that it is...

def parse(raw_file, header_cleaner=clean_header, item_cleaner=clean_row_item):
    """
    Given a filename, will load it and attempt to de-serialize the csv
    therein.

    Also makes sure we have a non-empty list as a result.

    Assumes that the first line will be a list of column names.

    The header_cleaner argument is for a function to be called for each header
    in order to "clean" it into an appropriate tag name.
    """
    # try to determine some useful information about the CSV file
    header = csv.Sniffer().has_header(raw_file.read(1024))
    if not header:
        raise ValueError("The CSV file doesn't appear to contain headers")
    raw_file.seek(0)
    dialect = csv.Sniffer().sniff(raw_file.read(1024))
    raw_file.seek(0)

    # read in the file
    raw = csv.reader(raw_file, dialect)

    # grab /clean the headers
    headers = [header_cleaner(header) for header in raw.next() if header]
    data = list()

    # process each of the rows into a dictionary and add to the result list
    for row in raw:
        item = dict(zip(headers, [item_cleaner(item) for item in row]))
        data.append(item)

    # Final check that we actually got some data.
    if data:
        return data
    else:
        raise ValueError('No records found')
