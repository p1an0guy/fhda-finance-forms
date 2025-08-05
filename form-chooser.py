import os
import importlib.util
import sys

# Import from form-downloader.py (handle hyphen in filename)
spec = importlib.util.spec_from_file_location("form_downloader", "form-downloader.py")
form_downloader = importlib.util.module_from_spec(spec)
sys.modules["form_downloader"] = form_downloader
spec.loader.exec_module(form_downloader)

def get_existing_forms(folder_path="downloaded_forms"):
    """
    Get a list of all file names currently in the downloaded_forms folder.
    
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

def display_forms(forms_list, title="Forms"):
    """Display a numbered list of forms."""
    if forms_list:
        print(f"\n{title} ({len(forms_list)} files):")
        print("=" * (len(title) + 20))
        
        for i, form_name in enumerate(forms_list, 1):
            print(f"{i:2d}. {form_name}")
        
        print(f"\nPython list: {forms_list}")
    else:
        print(f"\nNo {title.lower()} found.")

def main():
    """Main function to demonstrate form management."""
    print("FHDA Finance Forms Manager")
    print("=" * 30)
    
    # Option 1: Get forms from the downloaded_files list (from form-downloader.py)
    downloaded_forms = form_downloader.get_downloaded_files()
    display_forms(downloaded_forms, "Recently Downloaded Forms")
    
    # Option 2: Get forms from scanning the actual folder
    existing_forms = get_existing_forms()
    display_forms(existing_forms, "Forms in Folder")
    
    # Show if there are any differences
    if downloaded_forms and existing_forms:
        if set(downloaded_forms) == set(existing_forms):
            print("\n✅ Downloaded list matches folder contents!")
        else:
            print("\n⚠️  Downloaded list differs from folder contents:")
            only_in_downloaded = set(downloaded_forms) - set(existing_forms)
            only_in_folder = set(existing_forms) - set(downloaded_forms)
            
            if only_in_downloaded:
                print(f"Only in downloaded list: {list(only_in_downloaded)}")
            if only_in_folder:
                print(f"Only in folder: {list(only_in_folder)}")

def demo_download():
    """Demonstrate downloading forms and showing the list."""
    print("FHDA Finance Forms Manager - Download Demo")
    print("=" * 45)
    
    print("Downloading forms...")
    downloaded_forms = form_downloader.download_forms()
    
    print(f"\n📋 Downloaded forms list from form-downloader.py:")
    print(f"   {downloaded_forms}")
    
    # Now show both lists
    existing_forms = get_existing_forms()
    
    if set(downloaded_forms) == set(existing_forms):
        print("\n✅ Downloaded list matches folder contents!")
    else:
        print("\n⚠️  Downloaded list differs from folder contents")
        
    return downloaded_forms