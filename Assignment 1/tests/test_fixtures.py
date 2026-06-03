from advising_agent.fixtures import load_courses, load_prerequisites, load_student_profile


def test_fixtures_load_and_match_catalog_size():
    courses = load_courses()
    prerequisites = load_prerequisites()
    student = load_student_profile()

    assert len(courses) == 10
    assert {course.code for course in courses} == set(prerequisites)
    assert student.max_credits_next_term == 9

