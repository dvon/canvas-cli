# Code from canvas4.py---just the parts needed for downloading
# submissions and extracting zip files.


from canvas_token import TERM, SITE, TOKEN
        # canvas_token.py, in same folder, should look like:
        # TERM = 'Spring 2017'
        # SITE = 'https://messiah.instructure.com'
        # TOKEN = [Developer token generated from Canvas ...]

import json
import os
import shutil
import urllib.parse
import urllib.request
import zipfile

TEMP = 'temp'
PER_PAGE = 100
SHOW_UNPUBLISHED_COURSES = False
SHOW_ALL_ASSIGNMENTS = False
MAX_ATTACHMENT_MB = 100
DELETE_ZIPS = True


def get_courses():
    """
    """
    
    url = '{}/api/v1/courses'.format(SITE)
    values = { 'enrollment_type' : 'teacher',
               'include[]'       : 'term',
               'per_page'        : PER_PAGE }

    data = urllib.parse.urlencode(values).encode('utf-8')
    request = urllib.request.Request(url, data, method='GET')
    request.add_header('Authorization', 'Bearer ' + TOKEN)
    response = urllib.request.urlopen(request)
    response = json.loads(response.read().decode())

    courses = []

    for course in response:
        if course['term']['name'] == TERM and \
                (SHOW_UNPUBLISHED_COURSES or
                (course['workflow_state'] == 'available')):
            courses.append(course)

    try:
        courses.sort(key=lambda course:
                str(9 - int(course['name'][-3])) +
                course['name'][-7:])

    except ValueError:
        # Will get here if one of the courses doesn't end with
        # course and section numbers.
        courses.sort(key=lambda course: course['name'])
    
    return courses
    
    
def prompt_for_course_id():
    """
    Prompt user to choose course (from per-term courses in the
    current term, as specified by TERM).

    :return: Canvas id of the course chosen by the user.
    """

    courses = get_courses()
    print()

    for i in range(len(courses)):
        print('{}. {} ({})'.format(i + 1, courses[i]['name'],
                courses[i]['term']['name']))

    i = int(input('\nCourse number? ')) - 1

    return str(courses[i]['id'])


def prompt_for_assignment(course_id):
    """
    Prompt user to choose assignment (from assignments in this
    course with submissions to grade, sorted by due date).

    :param course_id: Canvas id of course (as returned by
                      prompt_for_course_id).

    :return: dict version of Canvas object for assignment chosen
             by the user.
    """

    url = '{}/api/v1/courses/{}/assignments'.format(
            SITE, course_id)
    values = { 'per_page' : PER_PAGE }
    data = urllib.parse.urlencode(values).encode('utf-8')
    request = urllib.request.Request(url, data, method='GET')
    request.add_header('Authorization', 'Bearer ' + TOKEN)
    response = urllib.request.urlopen(request)
    response = json.loads(response.read().decode())

    assignments = []

    for assignment in response:
        if ('needs_grading_count' in assignment and \
                assignment['needs_grading_count'] > 0) or \
                (SHOW_ALL_ASSIGNMENTS and \
                not (assignment['due_at'] == None)):
            assignments.append(assignment)

    assignments.sort(key=lambda assignment: assignment['due_at'])
    print()

    for i in range(len(assignments)):
        print('{}. {}'.format(i + 1, assignments[i]['name']))

    i = int(input('\nAssignment number? ')) - 1
    print()

    return assignments[i]


def get_students(course_id):
    """
    Return dict mapping student ids to names, for all students
    enrolled in a course.  (Canvas won't allow teacher user to
    access other user profiles, so there's no way to get the
    names directly from the ids, or vice versa.)

    :param course_id: Canvas id of course (as returned by
                      prompt for course id).

    :return: dict mapping student ids to names.
    """

    url = '{}/api/v1/courses/{}/users'.format(SITE, course_id)
    values = { 'enrollment_type' : 'student',
               'per_page'        : PER_PAGE }
    data = urllib.parse.urlencode(values).encode('utf-8')
    request = urllib.request.Request(url, data, method='GET')
    request.add_header('Authorization', 'Bearer ' + TOKEN)
    response = urllib.request.urlopen(request)
    response = json.loads(response.read().decode())
    students = {}

    for student in response:
        students[str(student['id'])] = student['sortable_name']

    return students


def unzip(filename, delete=False, copy_to_zip_dir=False):
    """
    Unzip a zip file.

    :param filename: name of zip file.
    :param delete: if True delete the original zip file.
    :param copy_to_zip_dir: if True copy all files to original
                            zip file's directory and delete
                            unzipped directory structure.
    """

    try:
        archive = zipfile.ZipFile(filename)

        if os.path.exists(TEMP):
            if os.path.isdir(TEMP):
                shutil.rmtree(TEMP)
            else:
                os.remove(TEMP)

        os.mkdir(TEMP)

        for name in archive.namelist():
            archive.extract(name, TEMP)

        archive.close()

        if delete:
            os.remove(filename)

        if copy_to_zip_dir:
            for path, dirs, files in os.walk(TEMP):
                for f in files:
                    shutil.copy(os.path.join(path, f), '.')

            shutil.rmtree(TEMP)

    except zipfile.BadZipFile:
        print('    FAILED TO UNZIP {} :(\n'.format(filename))


def download_attachment(attachment, student_name='?'):
    """
    Download Canvas attachment object's associated file (where
    attachment object comes from assignment submission object).
    If file is a zip file, will also unzip it, copy it's files
    to the original zip files directory, delete the zip file and
    delete the unzipped directory structure.

    :param attachment: Canvas attachment object associated with
                       file to download.
    :param student_name: name of student whose assignment
                         submission included the attachment
                         (optional, just for progress message).
    """

    filename = attachment['filename']
    print('Downloading {} ({})...'.format(filename, student_name))
    size = round(attachment['size'] / 1048576)

    if size > MAX_ATTACHMENT_MB:
        print('    TOO BIG! ({} MB)'.format(size))
    else:
        try:
            response = urllib.request.urlopen(attachment['url'])
            f = open(filename, 'wb')
            f.write(response.read())
            f.close()

            if filename.endswith('.zip'):
                unzip(filename, DELETE_ZIPS, True)

        except urllib.error.HTTPError:
            print('    DOWNLOAD FAILED :(')


def download_submission(course_id, assignment, student_name,
        student_id):
    """
    Download one student's assignment submission.  Create folder
    for the student if it doesn't exist.  Put submission
    attachments there.  If multiple attachments have the same
    file name, overwrite all but the last one submitted.

    :param course_id: Canvas id of course (as returned by
                      prompt_for_course_id).
    :param assignment: Canvas assignment object (as returned by
                       prompt_for_assignment).
    :param student_name: student's name (Canvas sortable name,
                         generally "Last, First"; value from
                         dict returned by get_students).
    :param student_id: Canvas id associated with student (value
                       from dict return by get_students).
    """

    if not student_id:
        students = get_students(course_id)

        for k, v in students.items():
            if v == student_name:
                student_id = k

    url = '{}/api/v1/courses/{}/assignments/{}'.format(
            SITE, course_id, assignment['id'])
    url += '/submissions/{}?include=submission_history'.format(
            student_id)
    request = urllib.request.Request(url)
    request.add_header('Authorization', 'Bearer ' + TOKEN)
    response = urllib.request.urlopen(request)
    submission = json.loads(response.read().decode())

    attachments = []

    for submission in submission['submission_history']:
        if 'attachments' in submission:
            attachments += submission['attachments']

    if len(attachments) == 0:
        print('**** Nothing submitted by {}.'.format(student_name))

    if len(attachments) > 0:
        # moss can't handle spaces in directory names...
        student_dir = student_name.replace(', ', '_').replace(
                ' ', '_')

        if not os.path.exists(student_dir):
            os.mkdir(student_dir)

        os.chdir(student_dir)

        for attachment in attachments:
            download_attachment(attachment, student_name)

        os.chdir('..')


def download_all():
    """
    Prompt user to choose course, and then to choose an
    assignment from those within the course that have ungraded
    submissions.  Then run download_submission for the chosen
    assignment, for all students within the course.
    """

    course_id = prompt_for_course_id()
    assignment = prompt_for_assignment(course_id)
    students = get_students(course_id)

    for student in sorted(students.items(),
            key=lambda student: student[1]):
        download_submission(course_id, assignment, student[1],
                student[0])


if __name__ == '__main__':
    download_all()
