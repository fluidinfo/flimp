"""
Turns a filename into a list of deserialized items based upon csv data
"""
import sys
import csv

def parse(raw_file):
    """
    Given a filename, will load it and attempt to de-serialize the csv
    therein.

    Also makes sure we have a non-empty list as a result

    Assumes that the first line will be a list of column names
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

    # grab the headers
    headers = [header.strip().replace(' ', '_') for header in raw.next() if
               header]
    size = len(headers)
    data = list()

    # process each of the rows into a dictionary and add to the result list
    for row in raw:
        # sanity check on the size of the row
        if not len(row) == size:
            msg = "Can't process row with wrong number of items. Expected %d"\
                  " items but got %d instead. Row: %s" % (size, len(row),
                  ', '.join(row))
            raise ValueError(msg)
        item = dict(zip(headers, row))
        data.append(item)

    # Final check 
    if len(data) > 0:
        return data
    else:
        raise ValueError('No records found')
