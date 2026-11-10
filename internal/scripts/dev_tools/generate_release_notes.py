#! /usr/bin/env python3

import sys
import os
import re
import shutil
import subprocess
from enum import Enum

from github import Auth, Github
from datetime import datetime, timezone

GITHUB_ORG = 'dtcenter'

# label used to mark issues that should be listed in bold
BOLD_LABEL = 'priority: bold for release notes'

# existing release notes, relative to the top of the repository
RELEASE_NOTES_RST = os.path.join('docs', 'Users_Guide', 'release-notes.rst')

class Category(Enum):
    ENHANCEMENT = "Enhancement"
    BUGFIX = "Bugfix"
    NEW_WRAPPER = "New Wrapper"
    NEW_USE_CASE = "New Use Case"
    DOCUMENTATION = "Documentation"
    INTERNAL = "Internal"

CATEGORIES = (
    Category.ENHANCEMENT.value,
    Category.BUGFIX.value,
    Category.NEW_WRAPPER.value,
    Category.NEW_USE_CASE.value,
    Category.DOCUMENTATION.value,
    Category.INTERNAL.value,
)

# labels used to categorize issues whose title has no category prefix,
# checked in order. Issues with none of these (e.g. type: task) are left
# uncategorized for manual review
LABEL_CATEGORIES = (
    ('type: new wrapper', Category.NEW_WRAPPER.value),
    ('type: new use case', Category.NEW_USE_CASE.value),
    ('type: bug', Category.BUGFIX.value),
    ('type: enhancement', Category.ENHANCEMENT.value),
    ('type: new feature', Category.ENHANCEMENT.value),
    ('component: documentation', Category.DOCUMENTATION.value),
)


def main(dev_name, dev_start_date, dev_end_date=None, repo_name='METplus'):
    if dev_end_date is None:
        dev_end_date = datetime.now(timezone.utc)

    token = get_github_token()
    all_issues = get_all_issues_since_dev_start(token, repo_name,
                                                dev_start_date, dev_end_date)
    all_issues = remove_listed_issues(all_issues, repo_name)
    issues_by_category = get_issues_by_category(all_issues)

    print_banner('ADD THIS TO docs/Users_Guide/release-notes.rst')

    print_header(repo_name, dev_name, dev_end_date)
    print_issues_by_category(repo_name, issues_by_category)


def get_github_token():
    """Get a GitHub token from the GITHUB_TOKEN environment variable or,
    if that is not set, from the GitHub CLI (gh auth token)."""
    token = os.getenv('GITHUB_TOKEN')
    if token:
        return token

    if shutil.which('gh'):
        result = subprocess.run(['gh', 'auth', 'token'],
                                capture_output=True, text=True)
        token = result.stdout.strip()
        if result.returncode == 0 and token:
            return token

    print("ERROR: Must set GITHUB_TOKEN environment variable "
          "or authenticate with the GitHub CLI (gh auth login)")
    sys.exit(1)


def get_all_issues_since_dev_start(token, repo_name, dev_start_date,
                                   dev_end_date):
    print(f"Finding issues in {GITHUB_ORG}/{repo_name} that were closed "
          f"between {dev_start_date.strftime('%Y-%m-%d')} and "
          f"{dev_end_date.strftime('%Y-%m-%d')}...")
    github_obj = Github(auth=Auth.Token(token))
    org = github_obj.get_organization(GITHUB_ORG)
    repo = org.get_repo(repo_name)

    # since filters by last update time, so also filter by closed time
    all_issues = repo.get_issues(state='closed', since=dev_start_date)
    all_issues = [issue for issue in all_issues
                  if issue.pull_request is None
                  and dev_start_date <= issue.closed_at <= dev_end_date
                  and issue.state_reason != 'not_planned'
                  and not issue.title.startswith('Update Truth')]
    all_issues.sort(key=lambda x: x.number)
    return all_issues


def get_listed_issue_numbers(repo_name):
    """Get the issue numbers already listed as release note entries in the
    existing release notes so they are not listed again. Only entries on their
    own line are matched, not issues referenced in the upgrade instructions."""
    top_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir, os.pardir))
    rst_path = os.path.join(top_dir, RELEASE_NOTES_RST)
    if repo_name != 'METplus' or not os.path.exists(rst_path):
        return set()
    with open(rst_path, 'r') as file_handle:
        content = file_handle.read()
    return {int(num) for num in
            re.findall(r'^\s*\(`#(\d+) <', content, flags=re.MULTILINE)}


def remove_listed_issues(all_issues, repo_name):
    listed = get_listed_issue_numbers(repo_name)
    skipped = [issue for issue in all_issues if issue.number in listed]
    if skipped:
        print('Skipping issues already listed in release notes: '
              f"{', '.join(str(issue.number) for issue in skipped)}")
    return [issue for issue in all_issues if issue.number not in listed]


def print_banner(msg):
    print(f"\n{'*' * len(msg)}\n{msg}\n{'*' * len(msg)}\n")


def print_header(repo_name, dev_name, dev_end_date):
    dev_fmt = dev_name.replace('-', ' ').replace('beta', 'Beta ').replace('rc', 'RC ')
    header = f"{repo_name} Version {dev_fmt} Release Notes ({dev_end_date.strftime('%Y-%m-%d')})"
    print(header)
    print('-' * len(header))


def print_issues_by_category(repo_name, issues_by_category):
    for category, issues in issues_by_category.items():
        print()
        if category != 'none':
            header = category
            if header in (Category.ENHANCEMENT.value, Category.NEW_WRAPPER.value, Category.NEW_USE_CASE.value):
                header = f'{header}s'
            elif header == Category.INTERNAL.value:
                header = 'Build, repository, and test'
            print(f"  .. dropdown:: {header}\n")
        elif issues:
            print('COULD NOT PARSE CATEGORY FROM THESE:\n')

        if issues is None:
            print('     None')
            continue
        for issue in issues:
            title = issue.title.removeprefix(category).lstrip(' :')
            num = issue.number
            if BOLD_LABEL in [label.name for label in issue.labels]:
                title = f'**{title}**'
            print(f"     * {title}")
            print(f"       (`#{num} <https://github.com/{GITHUB_ORG}/{repo_name}/issues/{num}>`_)")


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
            category = get_category_from_labels(issue)
            if category:
                if issues_by_category[category] is None:
                    issues_by_category[category] = []
                issues_by_category[category].append(issue)
                continue
            if issues_by_category['none'] is None:
                issues_by_category['none'] = []
            issues_by_category['none'].append(issue)
    return issues_by_category


def get_category_from_labels(issue):
    label_names = [label.name for label in issue.labels]
    for label, category in LABEL_CATEGORIES:
        if label in label_names:
            return category
    return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dev_name',
                        help="name of development cycle, e.g. 6.0.0-beta6")
    parser.add_argument('start_date',
                        help="YYYYMMDD date when development cycle started")
    parser.add_argument('-e', '--end_date',
                        help="YYYYMMDD date when development cycle ended "
                             "(inclusive), default is today")
    parser.add_argument('-r', '--repo',
                        default='METplus',
                        help="Repository to parse, default is METplus")
    args = parser.parse_args()

    def parse_ymd(ymd):
        try:
            return datetime.strptime(ymd, '%Y%m%d').replace(tzinfo=timezone.utc)
        except ValueError:
            print(f'ERROR: Date must be YYYYMMDD: {ymd}')
            sys.exit(1)

    start_date = parse_ymd(args.start_date)
    end_date = None
    if args.end_date:
        end_date = parse_ymd(args.end_date).replace(hour=23, minute=59,
                                                    second=59)
    main(repo_name=args.repo, dev_name=args.dev_name,
         dev_start_date=start_date, dev_end_date=end_date)
