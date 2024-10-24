# Imports
import streamlit as st
import os
from processor import ask_question, grade_assignments, quiz_doc, load_documents, list_documents, strictness_level

# Define the directory where the assignments will be saved
assignments_directory = "/Users/vgowda/Desktop/BoltGrader/streamlit/data"

# Create the directory if it doesn't exist
if not os.path.exists(assignments_directory):
    os.makedirs(assignments_directory)

# All Sidebar Functionality

maximum_grade = 100
external_print = ""
quart = ""

with st.sidebar:
    st.image("/Users/vgowda/Desktop/BoltGrader/logo-removebg-preview.png")
    
    st.divider()
    
    # Upload rubric criteria (single file)
    rubric = st.file_uploader(
        "Upload Rubric",
        accept_multiple_files=False,
        type=["pdf"],
        help="Upload the rubric you would like to grade the assignments over",
    )
    
    if st.button("Upload Rubric"):
        if rubric:  # If a rubric file is uploaded
            file_path = os.path.join(assignments_directory, rubric.name)
            with open(file_path, "wb") as f:
                f.write(rubric.getbuffer())  # Save the file
            st.write(f"Saved {rubric.name}")
        else:
            st.write("Please upload a rubric file.")
    
    st.divider()

    # Upload assignments (multiple PDF files)
    uploaded_assignments = st.file_uploader(
        "Upload Assignments",
        accept_multiple_files=True,
        type=["pdf"],  
        help="Upload the assignments to be graded (must be PDF)",
    )
    
    if st.button("Upload Assignments"):
        if uploaded_assignments:  # Check if assignments are uploaded
            for uploaded_file in uploaded_assignments:
                file_path = os.path.join(assignments_directory, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())  # Save each assignment file
                st.write(f"Loaded {uploaded_file.name} to directory")
        else:
            st.write("Please upload assignment files.")
        
    st.divider()
    
    grading_difficulty = st.radio(
        "Grading Difficulty",
        [":green[Easy]", ":orange[Medium]", ":red[Hard]"],
    )
    
    st.divider()
    grade_button = st.button("Grade")   
    if grade_button:  # When "Grade" button is pressed
        st.write("Analyzing uploaded documents...")
        load_documents()  # Reload documents
        grading_result = grade_assignments()  # Call the grading function
        st.write("Analysis complete. Here's what I found:")
        external_print = grading_result
  
# Handling user questions      
user_query = st.chat_input("Search") 
    

    
st.sidebar.divider()
st.sidebar.subheader("Current Documents")
for doc in list_documents():
    st.sidebar.text(doc)
    
if user_query:
    result = quiz_doc(user_query)
    quart = result
    
with st.chat_message(name="Bolt", avatar="⚡"):
    st.write(quart)
    if grade_button:
        st.write(external_print)


if grading_difficulty ==  ":green[Easy]":
    difficulty_value = 1
elif grading_difficulty == ":orange[Medium]":
    difficulty_value = 3
elif grading_difficulty == ":red[Hard]":
    difficulty_value = 5
    
grading_difficulty = strictness_level
        
print(grading_difficulty)
print(difficulty_value)