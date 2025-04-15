import streamlit as st

# Initialize session state for navigation and data
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "details" not in st.session_state:
    st.session_state.details = {}
if "answers" not in st.session_state:
    st.session_state.answers = {i: None for i in range(10)}
if "attempted" not in st.session_state:
    st.session_state.attempted = set()

# Function for the landing page to collect user details
def landing_page():
    st.title("SeeThrough Exams")

    # User details form
    st.subheader("Enter your details")
    st.session_state.details["name"] = st.text_input("Name")
    st.session_state.details["reg_no"] = st.text_input("Registration Number")
    st.session_state.details["college"] = st.text_input("College")
    st.session_state.details["gender"] = st.radio("Gender", ["Male", "Female", "Other"])

    # Video Capture
    st.write("### Video Capture")
    st.session_state.details["photo"] = st.camera_input("Take a photo")

    # Submission button to navigate to the next page
    if st.button("Submit"):
        if all(st.session_state.details.values()):  # Ensure all fields are filled
            st.session_state.page = "photo_confirmation"

# Function for the photo confirmation page
def photo_confirmation_page():
    st.title("SeeThrough Exam")

    # Display captured photo and greet user
    st.subheader(f"Hello, {st.session_state.details['name']}!")
    st.image(st.session_state.details["photo"], caption="Your photo")

    # Start Test button to navigate to the test page
    if st.button("Start Test"):
        st.session_state.page = "test"

# Test Page with questions, options, and video feed
def test_page():
    st.title("SeeThrough Exams")

    # Video Feed in the top-right corner
    col1, col2 = st.columns([4, 1])
    with col2:
        st.write("### Video Feed")
        st.camera_input("Capture Video")  # Placeholder for video capture

    # Questions and options data
    questions = [
        "Who wrote the book '1984'?",
        "Which is the smallest planet in our solar system?",
        "What is the capital of Japan?",
        "Which element has the chemical symbol 'O'?",
        "Who developed the theory of relativity?",
        "What is the largest mammal on Earth?",
        "Which continent is the Sahara Desert located in?",
        "What is the freezing point of water?",
        "Which country hosted the 2016 Summer Olympics?",
        "Which is the tallest mountain in the world?"
    ]
    options = [
        ["George Orwell", "Aldous Huxley", "J.K. Rowling", "Ernest Hemingway"],
        ["Mercury", "Venus", "Earth", "Mars"],
        ["Tokyo", "Kyoto", "Osaka", "Hiroshima"],
        ["Oxygen", "Hydrogen", "Carbon", "Nitrogen"],
        ["Albert Einstein", "Isaac Newton", "Galileo Galilei", "Niels Bohr"],
        ["Blue Whale", "Elephant", "Giraffe", "Shark"],
        ["Africa", "Asia", "Australia", "South America"],
        ["0°C", "100°C", "-273°C", "32°C"],
        ["Brazil", "Russia", "China", "USA"],
        ["Mount Everest", "K2", "Kangchenjunga", "Lhotse"]
    ]

    # Pagination and question display
    questions_per_page = 5
    total_questions = len(questions)
    current_page = st.session_state.get("question_page", 0)

    def render_questions(start_index):
        st.subheader(f"Question {start_index + 1} to {min(start_index + questions_per_page, total_questions)}")
        for i in range(start_index, min(start_index + questions_per_page, total_questions)):
            st.write(f"{i + 1}. {questions[i]}")
            selected_option = st.radio(
                f"Options for Question {i + 1}",
                options[i],
                index=options[i].index(st.session_state.answers[i]) if st.session_state.answers[i] else 0,
                key=f"q{i}"
            )
            st.session_state.answers[i] = selected_option

    # Display current page questions
    render_questions(current_page * questions_per_page)

    # Navigation buttons for pagination
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", disabled=current_page == 0):
            st.session_state["question_page"] = max(0, current_page - 1)
    with col2:
        if st.button("Next", disabled=current_page == total_questions // questions_per_page - 1):
            st.session_state["question_page"] = min(total_questions // questions_per_page - 1, current_page + 1)

    # Save & Next button to update attempted status and navigate to next page
    if st.button("Save & Next"):
        st.session_state.attempted.update([i for i, ans in st.session_state.answers.items() if ans])
        if current_page == total_questions // questions_per_page - 1:
            st.session_state.page = "final"
        else:
            st.session_state["question_page"] = current_page + 1

    # Display summary of answered questions
    st.subheader("Overall Summary")
    st.write(f"Attempted: {len(st.session_state.attempted)}")
    st.write(f"Not Attempted: {total_questions - len(st.session_state.attempted)}")

# Final page with a thank you message
def final_page():
    st.title("SeeThrough Exams")
    st.title("Thank you for submitting the test! 😊")

# Page navigation logic
if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "photo_confirmation":
    photo_confirmation_page()
elif st.session_state.page == "test":
    test_page()
elif st.session_state.page == "final":
    final_page()
