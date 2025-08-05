import os

def get_downloaded_forms_list(folder_path="downloaded_forms"):
    """
    Get a list of all file names in the downloaded_forms folder.
    
    Args:
        folder_path (str): Path to the folder containing the forms
        
    Returns:
        list: List of file names in the folder
    """
    form_names = []
    
    try:
        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' not found.")
            return form_names
        
        # Get all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Only add files (not directories)
            if os.path.isfile(file_path):
                form_names.append(filename)
        
        # Sort the list for consistent ordering
        form_names.sort()
        
    except Exception as e:
        print(f"Error reading folder: {e}")
    
    return form_names

def display_forms(forms_list, title="Downloaded Forms"):
    """Display a numbered list of forms."""
    if forms_list:
        print(f"\n{title} ({len(forms_list)} files):")
        print("=" * (len(title) + 20))
        
        for i, form_name in enumerate(forms_list, 1):
            print(f"{i:2d}. {form_name}")
        
        print(f"\nPython list:")
        print(forms_list)
    else:
        print(f"\nNo {title.lower()} found.")

def main():
    """Main function to create and display the forms list."""
    print("FHDA Finance Forms List Creator")
    print("=" * 35)
    
    # Get all forms from the downloaded_forms folder and create a Python list
    downloaded_forms_list = get_downloaded_forms_list()
    
    # Display the results
    display_forms(downloaded_forms_list)
    
    return downloaded_forms_list

if __name__ == "__main__":
    main()