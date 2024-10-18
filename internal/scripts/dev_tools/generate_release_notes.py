#! /usr/bin/env python3

import sys
import os

from github import Github
from datetime import datetime, timezone

CATEGORIES = (
    'Enhancement',
    'Bugfix',
    'New Wrapper',
    'New Use Case',
    'Documentation',
    'Internal',
)


def main(dev_name, dev_start_date, dev_end_date=datetime.today(), repo_name='METplus'):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
      print("ERROR: Must set GITHUB_TOKEN environment variable")
      sys.exit(1)

    print_banner('ADD THIS TO docs/Users_Guide/release-notes.rst')

    print_header(repo_name, dev_name, dev_end_date)
    all_issues = get_all_issues_since_dev_start(token, repo_name, dev_start_date)
    issues_by_category = get_issues_by_category(all_issues)
    print_issues_by_category(repo_name, issues_by_category)

    print_banner('ADD THIS TO METplus Coordinated Release Acceptance Testing')

    print_release_testing(repo_name, dev_name, all_issues)


def get_all_issues_since_dev_start(token, repo_name, dev_start_date):
    github_obj = Github(token)
    org = github_obj.get_organization('dtcenter')
    repo = org.get_repo(repo_name)

    all_issues = repo.get_issues(state='closed', since=dev_start_date)
    all_issues = [issue for issue in all_issues if issue.pull_request is None]
    all_issues = [issue for issue in all_issues if not issue.title.startswith('Update Truth')]
    return all_issues


def print_banner(msg):
    print(f"\n{'*' * len(msg)}\n{msg}\n{'*' * len(msg)}\n")


def print_header(repo_name, dev_name, dev_end_date):
    header = f"{repo_name} Version {dev_name.replace('-', ' ')} Release Notes ({dev_end_date.strftime('%Y-%m-%d')})"
    print(header)
    print('-' * len(header))


def print_issues_by_category(repo_name, issues_by_category):
    for category, issues in issues_by_category.items():
        print()
        if category != 'none':
            print(f"  .. dropdown:: {category}\n")
        else:
            print('COULD NOT PARSE CATEGORY FROM THESE:\n')
        if issues is None:
            print('     NONE')
            continue
        for issue in issues:
            title = issue.title.removeprefix(category).lstrip(' :')
            num = issue.number
            print(f"     * {title}")
            print(f"       (`#{num} <https://github.com/dtcenter/{repo_name}/issues/{num}>`_)")


def get_issues_by_category(all_issues):
    issues_by_category = dict.fromkeys(CATEGORIES)
    issues_by_category['none'] = []
    for issue in all_issues:
        found_cat = False
        for category in CATEGORIES:
            if issue.title.startswith(f"{category}:"):
                if issues_by_category[category] is None:
                    issues_by_category[category] = []
                issues_by_category[category].append(issue)
                found_cat = True
                break
        if not found_cat:
            if issues_by_category['none'] is None:
                issues_by_category['none'] = []
            issues_by_category['none'].append(issue)
    return issues_by_category


def print_release_testing(repo_name, dev_name, all_issues):
    dev_info = dev_name.split('-')[1]
    for issue in all_issues:
        num = issue.number
        print(f"| **OPEN** || [#{num}](https://github.com/dtcenter/{repo_name}/issues/{num}) | {dev_info} |||")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dev_name',
                        help="name of development cycle, e.g. 6.0.0-beta6")
    parser.add_argument('start_date',
                        help="YYYYMMDD date when development cycle started")
    parser.add_argument('-r', '--repo',
                        default='METplus',
                        help="Repository to parse, default is METplus")
    args = parser.parse_args()

    ymd = args.start_date
    try:
        year = int(ymd[:4])
        month = int(ymd[4:6])
        day = int(ymd[6:8])
    except ValueError:
        print('ERROR: Argument must be YYYYMMDD')
        sys.exit(1)

    start_date = datetime(year, month, day, tzinfo=timezone.utc)
    main(repo_name=args.repo, dev_name=args.dev_name, dev_start_date=start_date)
