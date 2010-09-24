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

def parse(raw_file, header_cleaner=clean_header):
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
        item = dict(zip(headers, row))
        data.append(item)

    # Final check that we actually got some data.
    if data:
        return data
    else:
        raise ValueError('No records found')
