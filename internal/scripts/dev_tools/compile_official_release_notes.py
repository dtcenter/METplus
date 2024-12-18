#! /usr/bin/env python3

# Written by George McCabe <mccabe@ucar.edu>
# Helper script that parses release notes from development releases,
# gathers all issues by category, sorts them by issue number, then
# outputs the formatted content
# Note: Careful review and massaging of output is likely needed
# Run this script from the top of the repository to parse
# Assumes location and name of release notes RST file

import re

infile = './docs/Users_Guide/release-notes.rst'

with open(infile, 'r') as file_handle:
    content = file_handle.read().splitlines()

category = None
items = {}
# gather issues and organize them by category
for line in content:
    if match := re.match(r'  .. dropdown:: (.*)', line):
        category = match.group(1)
        if not items.get(category):
            items[category] = []
        continue
    if category is None: continue
    if not line: continue
    if line.strip().startswith('.. _'):
        break
    if line.lstrip().startswith('*'):
        items[category].append(line)
    elif line.strip().lower() == 'none' or line.startswith('MET') or line.startswith('---') or line.startswith('==='):
        continue
    elif not items.get(category):
        continue
    else:
        items[category][-1] += f'\n{line}'

# get issues in each category to sort
issues = {}
for cat, item_list in items.items():
    if not issues.get(cat):
        issues[cat] = {}
    for issue in item_list:
        match = re.match(r'.*\#(\d+).*', issue.replace('\n', ''))
        if match:
            issues[cat][match.group(1)] = issue

# sort issues within each category and print formatted result
for cat in issues:
    nums = sorted([int(item) for item in issues[cat].keys()])
    print(f"  .. dropdown:: {cat}\n")
    for num in nums:
        print(issues[cat][str(num)])
    print()
