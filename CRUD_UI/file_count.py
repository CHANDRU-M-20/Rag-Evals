# import streamlit as st
# from pathlib import Path

# # Define the path to the INPUT FOLDER
# input_folder = Path("data_set")

# # Function to count files in a folder
# def count_files(folder_path):
#     return len([f for f in folder_path.iterdir() if f.is_file()])

# # Initialize session state to store folder counts
# if "folder_counts" not in st.session_state:
#     st.session_state.folder_counts = {}

# # Iterate over subfolders in INPUT FOLDER and store file counts
# for subfolder in input_folder.iterdir():
#     if subfolder.is_dir():  # Ensure it's a directory
#         st.session_state.folder_counts[subfolder.name] = count_files(subfolder)

# # Display the stored counts
# st.header("📂 File Counts in Each Folder")
# for folder, count in st.session_state.folder_counts.items():
#     st.metric(label=f"📁 {folder}", value=f"{count} file(s)")
import streamlit as st
from pathlib import Path

# Function to count records in JSONL files
def count_jsonl_records(file_list):
    jsonl_counts = {}
    for file_path in file_list:
        path = Path(file_path)
        if path.suffix == ".jsonl":  # Check if the file is JSONL
            try:
                with path.open("r", encoding="utf-8") as f:
                    jsonl_counts[path.name] = sum(1 for _ in f)  # Count lines in the file
            except Exception as e:
                jsonl_counts[path.name] = f"Error: {str(e)}"  # Handle errors gracefully
    return jsonl_counts

# Example: Assuming `st.session_state.filelist_view` contains the list of file paths
if "filelist_view" in st.session_state:
    jsonl_counts = count_jsonl_records
    (st.session_state.filelist_view)

    # Display the counts in Streamlit
    st.header("📂 JSONL File Record Counts")
    for file, count in jsonl_counts.items():
        st.metric(label=f"📄 {file}", value=f"{count} records")

