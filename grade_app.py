"""
Student Grade Manager - Streamlit UI (no pandas)

Mark range   Grade
90 to 100    A
80 to 89     B
70 to 79     C
60 to 69     D
Below 60     E

Run with:  streamlit run grade_manager_app.py
"""

import csv
import io

import streamlit as st


def get_grade(mark: float) -> str:
    if 90 <= mark <= 100:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    return "E"


def init_state():
    # Streamlit reruns the script on every interaction,
    # so the student list must live in session_state.
    if "students" not in st.session_state:
        st.session_state.students = []


def add_student(name: str, mark: float) -> tuple[bool, str]:
    name = name.strip()
    if not name:
        return False, "Please enter a valid student name."
    if any(s["Name"].lower() == name.lower() for s in st.session_state.students):
        return False, f"Student '{name}' already exists."
    if not 0 <= mark <= 100:
        return False, "Mark must be between 0 and 100."

    grade = get_grade(mark)
    st.session_state.students.append({"Name": name, "Mark": mark, "Grade": grade})
    return True, f"Added {name} with grade {grade}."


def students_to_csv(students: list[dict]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["Name", "Mark", "Grade"])
    writer.writeheader()
    writer.writerows(students)
    return buffer.getvalue().encode("utf-8")


def show_add_form():
    st.subheader("Add Student")
    # clear_on_submit resets the inputs after each add
    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        name = col1.text_input("Student name")
        mark = col2.number_input(
            "Mark (0 to 100)", min_value=0.0, max_value=100.0, step=0.5, value=0.0
        )
        submitted = st.form_submit_button("Add Student", type="primary")

    if submitted:
        ok, msg = add_student(name, mark)
        (st.success if ok else st.error)(msg)


def show_student_info():
    st.subheader("Student Details")
    students = st.session_state.students

    if not students:
        st.info("No students added yet.")
        return

    marks = [s["Mark"] for s in students]
    avg_mark = round(sum(marks) / len(marks), 2)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", len(students))
    c2.metric("Average", avg_mark)
    c3.metric("Highest", max(marks))
    c4.metric("Lowest", min(marks))

    # st.table accepts a plain list of dicts
    st.table(students)

    # Grade distribution without pandas
    counts = {g: 0 for g in "ABCDE"}
    for s in students:
        counts[s["Grade"]] += 1
    st.caption("Grade count:  " + "   ".join(f"**{g}**: {n}" for g, n in counts.items()))

    col_a, col_b = st.columns(2)
    col_a.download_button(
        "Download CSV",
        students_to_csv(students),
        file_name="students.csv",
        mime="text/csv",
    )
    if col_b.button("Clear all students"):
        st.session_state.students = []
        st.rerun()


def main():
    st.set_page_config(page_title="Student Grade Manager", page_icon="🎓")
    init_state()

    st.title("🎓 Student Grade Manager")

    with st.sidebar:
        st.header("Grading Scale")
        st.markdown(
            """
| Mark range | Grade |
|---|---|
| 90 - 100 | A |
| 80 - 89 | B |
| 70 - 79 | C |
| 60 - 69 | D |
| Below 60 | E |
"""
        )

    # Form and details on the same page
    show_add_form()
    st.divider()
    show_student_info()


if __name__ == "__main__":
    main()