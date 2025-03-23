import streamlit as st
from pathlib import Path
import os
from datetime import datetime
import json
import time
import shutil

def list_folders(base_folder):
    """List all folders inside the base directory."""
    base = Path(base_folder)
    return [folder.name for folder in base.iterdir() if folder.is_dir()]

def list_files(folder_path, file_type):
    """List files of the given type in the folder."""
    folder = Path(folder_path)
    return [file.name for file in folder.glob(f"*.{file_type}")]

BASE_FOLDER = "./data"  # Change this to your actual base folder
BASE_FOLDER_DELETE = "./delete_groundtruth"
st.set_page_config(
    page_title="Your App Title",  # Set the page title
    page_icon="📂",  # Optional: Set an icon
    layout="wide",  # Enables wide mode
    initial_sidebar_state="expanded"  # Expands the sidebar by default (optional)
)
st.title("File Manager")



# Session state initialization
if "add_file_key" not in st.session_state or "delete_file_key" not in st.session_state or "update_file_key" not in st.session_state:
    st.session_state.add_file_key = 0  
    st.session_state.delete_file_key = 0
    st.session_state.update_file_key = 0

if 'save_name' not in st.session_state:
    st.session_state.save_name = ""

if "upload_status" not in st.session_state:
    st.session_state.upload_status = "not_uploaded"  
    
if "cancel_add_file" not in st.session_state:
    st.session_state.cancel_add_file = 0  # Cancel add file flag
    
if "selected_folder_ADD" not in st.session_state or "selected_folder_VIEW" not in st.session_state.selected_folder_ADD or"selected_folder_DELETE" not in st.session_state:
    st.session_state.selected_folder_ADD = None
    st.session_state.selected_folder_DELETE = None
    st.session_state.selected_folder_VIEW = None

if "delete_status" not in st.session_state:
    st.session_state.delete_status = False
    
if "select_update_sample" not in st.session_state:
    st.session_state.select_update_sample = None

st.write(f"Current File Key: {st.session_state.add_file_key}")

functionality = st.tabs(["Add File", "Delete File", "Update File","restore File","view File"])

def sleep_after(seconds):
    time.sleep(seconds)
folders = list_folders(BASE_FOLDER)

with functionality[0]:
    
    st.session_state.selected_folder_ADD = st.selectbox("Select a folder", folders)

    st.write("Add File", st.session_state.selected_folder_ADD)
    
    uploaded_file = st.file_uploader("Choose a JSON file", type=["json"], key=f"add_file_{st.session_state.add_file_key}", accept_multiple_files=False)

    if uploaded_file:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Add File"):
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                save_filename = f"{st.session_state.selected_folder_ADD}-{timestamp}-{uploaded_file.name}"
                save_path = Path(BASE_FOLDER) / st.session_state.selected_folder_ADD / save_filename

                # Progress bar
                progress_bar = st.progress(0)

                with st.spinner("Uploading file..."):
                    for percent_complete in range(1, 101):
                        time.sleep(0.01)  # Simulate upload time
                        progress_bar.progress(percent_complete)

                try:
                    json_data = json.load(uploaded_file)

                    with open(save_path, "w") as f:
                        json.dump(json_data, f, indent=4)
                    st.session_state.save_name = save_filename

                    # st.session_state.upload_status = f"✅ File '{save_filename}' uploaded successfully to '{selected_folder_ADD}'!"
                    # st.success(st.session_state.upload_status)
                    st.session_state.upload_status = "uploded"

                except json.JSONDecodeError:
                    # st.session_state.upload_status = "❌ Invalid JSON file. Please upload a valid JSON file."
                    # st.error(st.session_state.upload_status)
                    st.session_state.upload_status = "json_error"

                # Reset uploader
                st.session_state.add_file_key += 1
                st.session_state.cancel_add_file += 1
                st.rerun()

        with col2:
            if st.button("Cancel Upload", key=f"cancel_add_file_{st.session_state.cancel_add_file}"):
                # st.session_state.upload_status = "⚠️ File upload canceled."
                st.session_state.upload_status = "canceled"
                st.warning(st.session_state.upload_status)

                # Reset uploader
                st.session_state.add_file_key += 1
                st.session_state.cancel_add_file += 1
                st.rerun()

    # Display persistent upload status message
    if st.session_state.upload_status=="not_uploaded" and uploaded_file is None:        
        # st.session_state.upload_status = "Please upload a valid JSON file."  # Reset status message
        st.info("Please upload a valid JSON file.")
        
    if st.session_state.upload_status=="json_error" and uploaded_file is None:
        
        st.session_state.upload_status = "❌ Invalid JSON file. Please upload a valid JSON file."
        st.error(st.session_state.upload_status)
        
    if st.session_state.upload_status=="canceled" and uploaded_file is None:
        
        st.session_state.upload_status = "⚠️ File upload canceled."
        st.warning(st.session_state.upload_status)
    
    if st.session_state.upload_status=="uploded" and uploaded_file is None:        
        st.session_state.upload_status = f"✅ File '{st.session_state.save_name}' uploaded successfully to '{st.session_state.selected_folder_ADD}'!"
        st.success(st.session_state.upload_status)
            # sleep_after(0.5)
            # st.rerun()
        # st.session_state.upload_status = "not_uploaded"




def move_to_delete_folder(base_folder, base_folder_delete,selected_folder, files_to_delete):
    
    delete_folder = Path(base_folder_delete) / selected_folder 
    delete_folder.mkdir(parents=True, exist_ok=True)  # Ensure the delete folder exists

    for file in files_to_delete:
        src_path = Path(base_folder) / selected_folder / file
        dest_path =delete_folder / file

        if src_path.exists():
            shutil.move(src_path, dest_path)
            
with functionality[1]:
    st.session_state.selected_folder_DELETE = st.selectbox("Select a folder", folders, key="delete_folder")

    if st.session_state.selected_folder_DELETE:
        st.write("📂 Deleting Files in:", st.session_state.selected_folder_DELETE)
        
        # List JSON files in the selected folder
        files = list_files(Path(BASE_FOLDER, st.session_state.selected_folder_DELETE), "json")

        if files:
            delete_file = st.multiselect("Select file(s) to delete", files, key="delete_file")

            if delete_file:
                if st.button("Delete Selected Files"):
                                    # Progress bar
                    progress_bar = st.progress(0)

                    with st.spinner("Files are being deleted..."):
                        for percent_complete in range(1, 101):
                            time.sleep(0.01)  # Simulate upload time
                        progress_bar.progress(percent_complete)
                        
                    move_to_delete_folder(BASE_FOLDER, BASE_FOLDER_DELETE,st.session_state.selected_folder_DELETE, delete_file)
                    st.session_state.delete_status = True
                    st.success(f"✅ Files deleted successfully - {len(delete_file)} ")
                    # st.rerun()
            else:
                st.warning("⚠️ No files selected for deletion.")
        else:
            st.info("No files available for deletion.")
        
    if st.session_state.delete_status:
        st.success(f"✅ Files deleted successfully - {len(delete_file)} ")
        st.session_state.delete_status = False
        st.rerun()
        
        

with functionality[2]:
    update_column = st.columns([1,1,1])
    with update_column[0]:
        st.session_state.selected_folder_UPDATE = st.selectbox("Select a folder", folders, key="update_folder")
        st.write("📂 Updating Files in:", st.session_state.selected_folder_UPDATE)
    with update_column[1]:
        # List JSON files in the selected folder
        if st.session_state.selected_folder_UPDATE:
            files = list_files(Path(BASE_FOLDER, st.session_state.selected_folder_UPDATE), "json")
            if files:
                st.session_state.selected_file_update = st.selectbox("Select a file", files, key="update_file")
                if st.session_state.selected_file_update:
                    selected_file_for_update  =Path(BASE_FOLDER, st.session_state.selected_folder_UPDATE, st.session_state.selected_file_update)
                    st.write("📂 Updating Files in:", st.session_state.selected_file_update)
            else:
                st.warning("⚠️ No JSON files found in this folder.")
   
        
        
    
    with update_column[2]:
        try:
            with open(selected_file_for_update, "r") as f:
                data = json.load(f)
        except Exception as e:
            st.error(f"⚠️ Error opening file: {e}")
            data = None

        if data:
            # Create a key to track the multiselect's previous value
            if 'previous_samples' not in st.session_state:
                st.session_state.previous_samples = []
                
            # Get the current selection
            current_selection = st.multiselect("Select a sample to update", data, key="update_sample")
            
            # Update our session state with the selection
            st.session_state.select_update_sample = current_selection
            
            # Check if the selection has changed
            if st.session_state.previous_samples != current_selection:
                # Clear the edited values when selection changes
                    if 'edited_json_values' in st.session_state:
                        st.session_state.edited_json_values = {}
                    # Update the previous samples tracker
                    st.session_state.previous_samples = current_selection

        # Initialize container for edited values if it doesn't exist
    if 'edited_json_values' not in st.session_state:
        st.session_state.edited_json_values = {}

    # Initialize deletion confirmation state
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = {}

    # Check if any sample is selected for update
    if st.session_state.select_update_sample:
        for idx, sample in enumerate(st.session_state.select_update_sample):
            # Create a unique key for this sample that includes some identifier from the sample
            # This helps ensure we're tracking the correct sample even if order changes
            sample_id = str(idx)  # Default to index
            if isinstance(sample, dict) and 'id' in sample:
                sample_id = f"{sample['id']}_{idx}"  # Use ID if available
            elif isinstance(sample, dict) and 'name' in sample:
                sample_id = f"{sample['name']}_{idx}"  # Use name if available
                
            sample_key = f"json_edit_{sample_id}"
            delete_key = f"delete_confirm_{sample_id}"
            
            # Initialize this sample's edited value if not already set
            if sample_key not in st.session_state.edited_json_values:
                st.session_state.edited_json_values[sample_key] = json.dumps(sample, indent=4)
            
            # Initialize delete confirmation state for this sample
            if delete_key not in st.session_state.delete_confirmation:
                st.session_state.delete_confirmation[delete_key] = False
            
            with st.expander(f"Updating Sample {idx}"):
                # Display the original JSON sample
                st.subheader("Original JSON:")
                st.json(sample)
                
                # Create a text area for editing and store the edits in session state
                st.subheader("Edit JSON:")
                edited_json = st.text_area(
                    "Make your changes below:",
                    value=st.session_state.edited_json_values[sample_key],
                    height=400,
                    key=sample_key
                )
                
                # Update the session state with the edited value
                st.session_state.edited_json_values[sample_key] = edited_json
                
                # Create columns for buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                
                # Save button in first column
                with col1:
                    if st.button(f"Save Changes", key=f"save_btn_{sample_id}"):
                        try:
                            # Parse the edited JSON to validate it
                            updated_sample = json.loads(edited_json)
                            
                            # Find this sample in the original data and update it
                            for i, item in enumerate(data):
                                if item == sample:  # Match the original sample
                                    data[i] = updated_sample  # Replace with updated version
                                    break
                            
                            # Save the entire updated data back to the file
                            with open(selected_file_for_update, "w") as f:
                                json.dump(data, f, indent=4)
                            
                            st.success(f"✅ Sample {idx} updated successfully!")
                            
                            # Clear the edited values to force refresh on next load
                            st.session_state.edited_json_values = {}
                            
                            # Optionally refresh the page to show the updated data
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON format: {e}")
                        except Exception as e:
                            st.error(f"❌ Error saving changes: {e}")
                
                # Delete button and confirmation in second and third columns
                with col2:
                    if not st.session_state.delete_confirmation[delete_key]:
                        if st.button(f"Delete Sample", key=f"delete_btn_{sample_id}"):
                            st.session_state.delete_confirmation[delete_key] = True
                
                with col3:
                    if st.session_state.delete_confirmation[delete_key]:
                        st.warning("Are you sure you want to delete this sample?")
                        
                        confirm_col, cancel_col = st.columns(2)
                        
                        with confirm_col:
                            if st.button("Yes, Delete", key=f"confirm_delete_{sample_id}", type="primary"):
                                try:
                                    # Find this sample in the original data and remove it
                                    for i, item in enumerate(data):
                                        if item == sample:  # Match the original sample
                                            del data[i]  # Remove the sample
                                            break
                                    
                                    # Save the updated data back to the file
                                    with open(selected_file_for_update, "w") as f:
                                        json.dump(data, f, indent=4)
                                    
                                    st.success(f"✅ Sample {idx} deleted successfully!")
                                    
                                    # Reset confirmation state
                                    st.session_state.delete_confirmation = {}
                                    
                                    # Clear the edited values to force refresh on next load
                                    st.session_state.edited_json_values = {}
                                    
                                    # Refresh the page to show updated data
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting sample: {e}")
                        
                        with cancel_col:
                            if st.button("Cancel", key=f"cancel_delete_{sample_id}"):
                                st.session_state.delete_confirmation[delete_key] = False
                                st.rerun()

    # Add a button to save all changes at once (optional)
    if st.session_state.select_update_sample and len(st.session_state.select_update_sample) > 1:
        if st.button("Save All Changes", key="save_all_btn"):
            success_count = 0
            error_messages = []
            
            for idx, sample in enumerate(st.session_state.select_update_sample):
                # Use the same sample ID logic as above
                sample_id = str(idx)
                if isinstance(sample, dict) and 'id' in sample:
                    sample_id = f"{sample['id']}_{idx}"
                elif isinstance(sample, dict) and 'name' in sample:
                    sample_id = f"{sample['name']}_{idx}"
                    
                sample_key = f"json_edit_{sample_id}"
                edited_json = st.session_state.edited_json_values.get(sample_key)
                
                if edited_json:
                    try:
                        # Parse the edited JSON
                        updated_sample = json.loads(edited_json)
                        
                        # Find and update in the original data
                        for i, item in enumerate(data):
                            if item == sample:
                                data[i] = updated_sample
                                success_count += 1
                                break
                    except Exception as e:
                        error_messages.append(f"Error with Sample {idx}: {str(e)}")
            
            if success_count > 0:
                try:
                    # Save all updates to the file
                    with open(selected_file_for_update, "w") as f:
                        json.dump(data, f, indent=4)
                    
                    st.success(f"✅ Successfully updated {success_count} samples!")
                    
                    if error_messages:
                        st.warning("Some samples had errors:")
                        for msg in error_messages:
                            st.write(msg)
                    
                    # Clear the edited values to force refresh on next load
                    st.session_state.edited_json_values = {}
                    
                    # Refresh to show updated data
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving to file: {e}")
            elif error_messages:
                st.error("❌ No samples were updated due to errors.")
                for msg in error_messages:
                    st.write(msg)
                        







# with functionality[3]:
        
            
            
    # with st.expander("PREVIEW DATA"):
        
    #     try:
    #         with open(selected_file_for_update, "r") as f:
    #             data = json.load(f)
    #             st.json(data)  # Display JSON in a readable format
    #     except Exception as e:
    #         st.error(f"⚠️ Error opening file: {e}")
    
            
    
    
    
            
            
            
            
            
            
    
with functionality[4]:  # View File tab
    st.session_state.selected_folder_VIEW = st.selectbox("Select a folder", folders, key="view_folder")

    if st.session_state.selected_folder_VIEW is not None:
        st.write("📂 Viewing Files in:", st.session_state.selected_folder_VIEW)

        folder_path = Path(BASE_FOLDER,st.session_state.selected_folder_VIEW)
        files = [file.name for file in folder_path.iterdir() if file.is_file() and file.suffix == ".json"]

        if files:
            selected_file = st.selectbox("Select a file", files, key="view_file")

            if selected_file and st.button("View File"):
                file_path = folder_path / selected_file

                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        st.json(data)  # Display JSON in a readable format
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file. Cannot display content.")
                except Exception as e:
                    st.error(f"⚠️ Error opening file: {e}")

        else:
            st.warning("⚠️ No JSON files found in this folder.")
        

    
    
        
    
    
        
