#!/usr/bin/env python
import os
import sys
import time
import shutil
from redminelib import Redmine
from Extract_Files import MassExtractor
from Sequence_File import SequenceInfo


def redmine_setup(api_key):
    """
    :param api_key: API key available from your Redmine user account settings. Stored in setup.py.
    :return: instantiated Redmine API object
    """
    redmine_url = 'https://redmine.biodiversity.agr.gc.ca/'
    redmine = Redmine(redmine_url, key=api_key, requests={'verify': False})
    return redmine


def retrieve_issues(redmine_instance):
    """
    :param redmine_instance: instantiated Redmine API object
    :return: returns an object containing all issues for OLC CFIA (http://redmine.biodiversity.agr.gc.ca/projects/cfia/)
    """
    issues = redmine_instance.issue.filter(project_id='cfia')
    return issues


def new_automation_jobs(issues):
    """
    :param issues: issues object pulled from Redmine API
    :return: returns a new subset of issues that are Status: NEW and match a term in AUTOMATOR_KEYWORDS)
    """
    new_jobs = {}
    for issue in issues:
        # Only new issues
        if issue.status.name == 'New':
            # Strip whitespace and make lowercase ('subject' is the job type i.e. Diversitree)
            subject = issue.subject.lower().replace(' ', '')
            # Check for presence of an automator keyword in subject line
            if subject == 'iridaretrieve':
                new_jobs[issue] = subject
    return new_jobs


def retrieve_issue_description(issue):
    """
    :param issue: object pulled from Redmine instance
    :return: parsed issue description as a list
    """
    description = issue.description.split('\n')
    for line in range(len(description)):
        description[line] = description[line].rstrip()
    return description


def get_validated_seqids(sequences_list):
    """
    A inputted list is checked for Seq-ID format, each of the Elements that are validated are returned to the user
    sequences_list: list of Seq-IDs to be validated
    """

    validated_sequence_list = list()
    regex = r'^(2\d{3}-\w{2,10}-\d{3,4})$'
    import re
    for sequence in sequences_list:
        # if re.match(regex, sequence.sample_name):
        validated_sequence_list.append(sequence)
        # else:
        #     raise ValueError("Invalid seq-id \"%s\"" % sequence.sample_name)

    if len(validated_sequence_list) < 1:
        raise ValueError("Invalid format for redmine request. Couldn't find any fastas or fastqs to extract")

    return validated_sequence_list


if __name__ == '__main__':
    dependencies = ['reformat.sh', 'kmercountexact.sh']
    for dependency in dependencies:
        if shutil.which(dependency) is None:
            print('Dependency {} not found. Quitting...'.format(dependency))
            quit(code=1)
    print('Enter your Redmine API Key: ')
    api_key = input('Enter your Redmine API Key: ')
    print('Enter the path to the External Drive: ')
    mounted_drive = input('Enter the path to the External Drive: ')
    redmine = redmine_setup(api_key)
    if ' ' in mounted_drive:
        mounted_drive = mounted_drive.encode('unicode_escape').decode()
    # try:
    while True:
        if not os.path.ismount(mounted_drive):
            print('The drive specified ({}) is not connected! Process will not start until it is connected.'.format(mounted_drive))
            time.sleep(60)
            continue

        issues = retrieve_issues(redmine_instance=redmine)
        new_jobs = new_automation_jobs(issues)
        if len(new_jobs) > 0:
            for job, job_type in new_jobs.items():
                print('Responding to redmine request number: {}'.format(job.id))
                description = retrieve_issue_description(job)
                if not os.path.isdir(os.path.join(mounted_drive, str(job.id))):
                    os.makedirs(os.path.join(mounted_drive, str(job.id)))

                output_folder = os.path.join(mounted_drive, str(job.id))
                sequences_info = list()
                for input_line in description:
                    if input_line is not '':
                        sequences_info.append(SequenceInfo(input_line))
                sequences_info = get_validated_seqids(sequences_info)
                missing_files = MassExtractor(nas_mnt='/mnt/nas/').move_files(sequences_info, output_folder)
                print('IRIDA retrieve request complete.')
                redmine.issue.update(resource_id=job.id,
                                     notes='Irida retrieve complete!',
                                     status_id=4)
        time.sleep(60)
    # except:
    #     pass
