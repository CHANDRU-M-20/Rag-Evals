import streamlit as st
from pathlib import Path
import os
import pandas as pd
from datetime import datetime
import json

def list_folders(base_folder):
    """List all folders inside the base directory."""
    base = Path(base_folder)
    return [folder.name for folder in base.iterdir() if folder.is_dir()]

def list_files(folder_path, file_type):
    """List files of the given type in the folder."""
    folder = Path(folder_path)
    return [file.name for file in folder.glob(f"*.{file_type}")]

# Base data folder
BASE_FOLDER = "./data"  # Change this to your actual base folder

st.title("File Manager")

# Sidebar options

st.header("Options")

# Select folder first
folders = list_folders(BASE_FOLDER)
if folders:
    selected_folder = st.selectbox("Select a folder", folders)
    folder_path = Path(BASE_FOLDER) / selected_folder
    
    # Select file type
    file_type = "json"
    files = list_files(folder_path, file_type)
    
    if files:
        # Select file
        selected_file = st.selectbox("Select a file", files)
        file_path = folder_path / selected_file
        
        # Display Add and Delete buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add File", key="add_file_display"):
                st.session_state.show_upload = True
        with col2:
            if st.button("Delete File", key="delete_btn"):
                st.session_state.confirm_delete = True
        
        # Confirmation card for deleting a file
        if st.session_state.get("confirm_delete", False):
            st.warning(f"Are you sure you want to delete {selected_file}?")
            with col1:
                if st.button("Yes, Delete", key="confirm_yes"):
                    if file_path.exists():
                        os.remove(file_path)
                        st.success(f"File {selected_file} deleted successfully!")
                    else:
                        st.error("File not found!")
                    st.session_state.confirm_delete = False
                    st.rerun()
            with col2:
                if st.button("Cancel", key="confirm_no"):
                    st.session_state.confirm_delete = False
                    st.rerun()
    
    # File upload section (only visible after clicking Add File button)
    if st.session_state.get("show_upload", False):
        uploaded_file = st.file_uploader("Upload a JSON file", type=["json"], key="file_upload")
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm Upload", key="confirm_upload"):
                    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                    save_filename = f"{selected_folder}-{timestamp}-{uploaded_file.name}"
                    save_path = folder_path / save_filename
                    
                    with open(save_path, "w") as f:
                        json_data = json.load(uploaded_file)
                        json.dump(json_data, f, indent=4)
                        
                    st.success(f"File {save_filename} uploaded successfully to {selected_folder}!")
                    st.session_state.show_upload = False
                    st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_upload"):
                    st.session_state.show_upload = False
                    st.rerun()
else:
    st.warning("No folders found in the base directory.")

# Display file contents
if 'selected_file' in locals() and file_path.exists():
    if file_type == "json":
        with open(file_path, "r") as f:
            df = json.load(f)
        st.write(df)
