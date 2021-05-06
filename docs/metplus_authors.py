#! /usr/bin/env python3

# Script: authors.py
# Author: George McCabe <mccabe@ucar.edu>
# Description: script containing list of current and former authors and
#  functions to get formatted versions

# Rotate Authorship:
#   Move the first item in the CURRENT_AUTHORS list to the end of the list

# each list item is a tuple with the author name (last name, first initial) and
# the affiliation string from docs/index.rst or None if no affiliation to list
CURRENT_AUTHORS = [
    ('Dan Adriaansen', 'NCAR'),
    ('Minna Win-Gildenmeister', 'NCAR'),
    ('George McCabe', 'NCAR'),
    ('Julie Prestopnik', 'NCAR'),
    ('John Opatz', 'NCAR'),
    ('John Halley Gotway', 'NCAR'),
    ('Tara Jensen', 'NCAR'),
    ('Jonathan Vigh', 'NCAR'),
    ('Mallory Row', 'IMSG'),
    ('Christina Kalb', 'NCAR'),
    ('Hank Fisher', 'NCAR'),
    ('Lisa Goodrich', 'NCAR'),
]

# former team members that should still be listed in citation/author list
FORMER_AUTHORS = [
    ('James Frimel', 'CIRA'),
    ('Lindsay Blank', None),
    ('Todd Arbetter', None),
]

ALL_AUTHORS = CURRENT_AUTHORS + FORMER_AUTHORS

def get_citation_authors():
    """! Returns a string containing all of the authors separated by
     commas formatted by last name comma first initial
    """
    authors = []
    for author, _ in ALL_AUTHORS:
        first, last = author.split(' ', 1)
        authors.append(f'{last}, {first[0]}.')

    return ', '.join(authors)

def get_authors_and_orgs():
    """! Returns RST formatted of names and reference to organization
     if applicable. Organization reference strings are found in
     docs/index.rst
    """
    authors = []
    for author_name, org_name in ALL_AUTHORS:
        suffix = f' [#{org_name}]_' if org_name else ''
        authors.append(f'* {author_name}{suffix}')

    return '<br/>'.join(authors)
