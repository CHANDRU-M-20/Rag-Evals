import streamlit as st
import json
from pathlib import Path
import os

class JSONLFileEditor:
    def __init__(self, base_folder):
        """
        Initialize the JSONL File Editor with a base folder path
        
        Args:
            base_folder (str): Base directory containing JSONL files
        """
        self.base_folder = Path(base_folder)
        
        # Initialize session state variables if not already present
        if 'selected_folder_UPDATE' not in st.session_state:
            st.session_state.selected_folder_UPDATE = None
        if 'selected_file_update' not in st.session_state:
            st.session_state.selected_file_update = None
        if 'select_update_sample' not in st.session_state:
            st.session_state.select_update_sample = []
        if 'previous_samples' not in st.session_state:
            st.session_state.previous_samples = []
        if 'edited_jsonl_values' not in st.session_state:
            st.session_state.edited_jsonl_values = {}
        if 'delete_confirmation' not in st.session_state:
            st.session_state.delete_confirmation = {}

    def list_folders(self):
        """
        List all subdirectories in the base folder
        
        Returns:
            list: List of folder names
        """
        return [f.name for f in self.base_folder.iterdir() if f.is_dir()]

    def list_files(self, folder, extension="jsonl"):
        """
        List files with a specific extension in a given folder
        
        Args:
            folder (str): Folder name to search in
            extension (str, optional): File extension to filter. Defaults to "jsonl"
        
        Returns:
            list: List of file names with the specified extension
        """
        folder_path = self.base_folder / folder
        return [f.name for f in folder_path.glob(f"*.{extension}") if f.is_file()]

    def load_jsonl_file(self, folder, filename):
        """
        Load a JSONL file and return its contents
        
        Args:
            folder (str): Folder containing the file
            filename (str): Name of the JSONL file
        
        Returns:
            list: List of JSON objects from the file, or None if error
        """
        try:
            file_path = self.base_folder / folder / filename
            data = []
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        data.append(json.loads(line))
            return data
        except Exception as e:
            st.error(f"⚠️ Error opening file: {e}")
            return None

    def render_file_selection(self):
        """
        Render Streamlit components for folder and file selection
        
        Returns:
            tuple: Selected folder and file, or (None, None)
        """
        # Create columns for selection
        update_column = st.columns([1,1,1])
        
        # Folder selection
        with update_column[0]:
            folders = self.list_folders()
            st.session_state.selected_folder_UPDATE = st.selectbox(
                "Select a folder", 
                folders, 
                key="update_folder"
            )
            st.write("📂 Updating Files in:", st.session_state.selected_folder_UPDATE)
        
        # File selection
        with update_column[1]:
            if st.session_state.selected_folder_UPDATE:
                files = self.list_files(st.session_state.selected_folder_UPDATE)
                if files:
                    st.session_state.selected_file_update = st.selectbox(
                        "Select a file", 
                        files, 
                        key="update_file"
                    )
                    if st.session_state.selected_file_update:
                        st.write("📄 Selected file:", st.session_state.selected_file_update)
                else:
                    st.warning("⚠️ No JSONL files found in this folder.")
        
        return (st.session_state.selected_folder_UPDATE, 
                st.session_state.selected_file_update)

    def create_sample_display_options(self, data):
        """
        Create display options for multiselect with sample previews
        
        Args:
            data (list): List of JSON objects
        
        Returns:
            list: List of display options with index, preview, and original data
        """
        display_options = []
        for i, item in enumerate(data):
            # Create a preview string (showing first few keys and values)
            preview = {}
            keys_to_show = list(item.keys())[:3]  # Show first 3 keys
            for key in keys_to_show:
                preview[key] = item[key]
            
            # Store both the index and preview
            display_options.append({
                "index": i,
                "preview": str(preview),
                "original": item
            })
        
        return display_options

    def render_sample_selection(self, display_options):
        """
        Render multiselect for samples and track selection
        
        Args:
            display_options (list): List of display options for samples
        
        Returns:
            list: Selected samples
        """
        current_selection = st.multiselect(
            "Select a sample to update", 
            options=display_options,
            format_func=lambda x: f"Line {x['index']}: {x['preview']}",
            key="update_sample"
        )
        
        # Update our session state with the selection
        st.session_state.select_update_sample = current_selection
        
        # Check if the selection has changed
        if st.session_state.previous_samples != current_selection:
            # Clear the edited values when selection changes
            if 'edited_jsonl_values' in st.session_state:
                st.session_state.edited_jsonl_values = {}
            # Update the previous samples tracker
            st.session_state.previous_samples = current_selection
        
        return current_selection

    def render_sample_editor(self, data, selected_samples, file_path):
        """
        Render editor for selected samples with save and delete functionality
        
        Args:
            data (list): Complete data from the file
            selected_samples (list): Samples selected for editing
            file_path (Path): Full path to the JSONL file
        """
        if selected_samples:
            for idx, sample_info in enumerate(selected_samples):
                # Use the line index as a unique identifier
                sample_id = str(sample_info["index"])
                sample = sample_info["original"]
                sample_key = f"jsonl_edit_{sample_id}"
                delete_key = f"delete_confirm_{sample_id}"
                
                st.write(f"📝 Updating Line {sample_id}")
                
                # Initialize this sample's edited value if not already set
                if sample_key not in st.session_state.edited_jsonl_values:
                    st.session_state.edited_jsonl_values[sample_key] = json.dumps(sample, indent=4)
                
                # Initialize delete confirmation state for this sample
                if delete_key not in st.session_state.delete_confirmation:
                    st.session_state.delete_confirmation[delete_key] = False
                
                with st.expander(f"Updating Line {sample_id}"):
                    # Display the original JSON sample
                    st.subheader("Original JSON:")
                    st.json(sample)
                    
                    # Create a text area for editing and store the edits in session state
                    st.subheader("Edit JSON:")
                    edited_json = st.text_area(
                        "Make your changes below:",
                        value=st.session_state.edited_jsonl_values[sample_key],
                        height=400,
                        key=sample_key
                    )
                    
                    # Update the session state with the edited value
                    st.session_state.edited_jsonl_values[sample_key] = edited_json
                    
                    # Create columns for buttons
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    # Save button handling
                    with col1:
                        if st.button(f"Save Changes", key=f"save_btn_{sample_id}"):
                            self._save_single_sample(data, sample_id, edited_json, file_path)
                    
                    # Delete button and confirmation handling
                    with col2:
                        if not st.session_state.delete_confirmation[delete_key]:
                            if st.button(f"Delete Line", key=f"delete_btn_{sample_id}"):
                                st.session_state.delete_confirmation[delete_key] = True
                    
                    with col3:
                        if st.session_state.delete_confirmation[delete_key]:
                            self._handle_delete_confirmation(data, sample_id, file_path, delete_key)

            # Add a button to save all changes if multiple samples are selected
            if len(selected_samples) > 1:
                self._render_save_all_button(data, file_path)

    def _save_single_sample(self, data, sample_id, edited_json, file_path):
        """
        Save a single sample to the JSONL file
        
        Args:
            data (list): Complete data from the file
            sample_id (str): ID of the sample to save
            edited_json (str): Edited JSON string
            file_path (Path): Full path to the JSONL file
        """
        try:
            # Parse the edited JSON to validate it
            updated_sample = json.loads(edited_json)
            
            # Update data at the specific line
            original_index = int(sample_id)
            data[original_index] = updated_sample
            
            # Save the entire updated data back to the file
            self._write_jsonl_file(data, file_path)
            
            st.success(f"✅ Line {sample_id} updated successfully!")
            
            # Clear the edited values to force refresh on next load
            st.session_state.edited_jsonl_values = {}
            
            # Refresh the page to show the updated data
            st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON format: {e}")
        except Exception as e:
            st.error(f"❌ Error saving changes: {e}")

    def _handle_delete_confirmation(self, data, sample_id, file_path, delete_key):
        """
        Handle delete confirmation dialog
        
        Args:
            data (list): Complete data from the file
            sample_id (str): ID of the sample to delete
            file_path (Path): Full path to the JSONL file
            delete_key (str): Session state key for delete confirmation
        """
        st.warning("Are you sure you want to delete this line?")
        
        confirm_col, cancel_col = st.columns(2)
        
        with confirm_col:
            if st.button("Yes, Delete", key=f"confirm_delete_{sample_id}", type="primary"):
                try:
                    # Remove the item at the specific index
                    original_index = int(sample_id)
                    del data[original_index]
                    
                    # Save the updated data back to the file
                    self._write_jsonl_file(data, file_path)
                    
                    st.success(f"✅ Line {sample_id} deleted successfully!")
                    
                    # Reset confirmation state
                    st.session_state.delete_confirmation = {}
                    
                    # Clear the edited values to force refresh on next load
                    st.session_state.edited_jsonl_values = {}
                    
                    # Refresh the page to show updated data
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting line: {e}")
        
        with cancel_col:
            if st.button("Cancel", key=f"cancel_delete_{sample_id}"):
                st.session_state.delete_confirmation[delete_key] = False
                st.rerun()

    def _render_save_all_button(self, data, file_path):
        """
        Render a button to save all changes for multiple selected samples
        
        Args:
            data (list): Complete data from the file
            file_path (Path): Full path to the JSONL file
        """
        if st.button("Save All Changes", key="save_all_btn"):
            success_count = 0
            error_messages = []
            
            for sample_info in st.session_state.select_update_sample:
                sample_id = str(sample_info["index"])
                sample_key = f"jsonl_edit_{sample_id}"
                edited_json = st.session_state.edited_jsonl_values.get(sample_key)
                
                if edited_json:
                    try:
                        # Parse the edited JSON
                        updated_sample = json.loads(edited_json)
                        
                        # Update at the specific index
                        original_index = int(sample_id)
                        data[original_index] = updated_sample
                        success_count += 1
                    except Exception as e:
                        error_messages.append(f"Error with Line {sample_id}: {str(e)}")
            
            if success_count > 0:
                try:
                    # Save all updates to the file
                    self._write_jsonl_file(data, file_path)
                    
                    st.success(f"✅ Successfully updated {success_count} samples!")
                    
                    if error_messages:
                        st.warning("Some samples had errors:")
                        for msg in error_messages:
                            st.write(msg)
                    
                    # Clear the edited values to force refresh on next load
                    st.session_state.edited_jsonl_values = {}
                    
                    # Refresh to show updated data
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving to file: {e}")
            elif error_messages:
                st.error("❌ No samples were updated due to errors.")
                for msg in error_messages:
                    st.write(msg)

    def _write_jsonl_file(self, data, file_path):
        """
        Write data to a JSONL file
        
        Args:
            data (list): List of JSON objects to write
            file_path (Path): Full path to the JSONL file
        """
        with open(file_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

    def run(self):
        """
        Main method to run the JSONL file editor interface
        """
        # File selection
        folder, filename = self.render_file_selection()
        
        # If a file is selected, load and process it
        if folder and filename:
            file_path = self.base_folder / folder / filename
            
            # Load the data
            data = self.load_jsonl_file(folder, filename)
            
            if data:
                # Create display options for sample selection
                display_options = self.create_sample_display_options(data)
                
                # Render sample selection
                selected_samples = self.render_sample_selection(display_options)
                
                # Render sample editor if samples are selected
                self.render_sample_editor(data, selected_samples, file_path)

# Example usage in a Streamlit app
def main():
    st.title("JSONL File Editor")
    
    # Replace BASE_FOLDER with your actual base directory path
    BASE_FOLDER = "data_set/Inputs"
    BASE_FOLDER_RESULT = "data_set/Results"
    
    
    # editor = JSONLFileEditor(BASE_FOLDER)
    # if editor:
    #     editor.run()
    tabs = st.tabs(["Inputs", "Results"])
    if tabs == "Inputs":
        st.write(BASE_FOLDER)
        editor = JSONLFileEditor(BASE_FOLDER)
        editor.run()
        
    # if tabs == "Results":
    
    #     editor_result = JSONLFileEditor(BASE_FOLDER_RESULT)
    #     editor_result.run()

if __name__ == "__main__":
    main()
    