import os
import boto3
import json

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

def find_best_form(user_input, forms_list):
    """
    Use Amazon Bedrock Claude to find the most likely form based on user input.
    
    Args:
        user_input (str): What the user wants to fill out
        forms_list (list): List of available form names
        
    Returns:
        str: The most likely form name from the list
    """
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Create the prompt
        prompt = f"""You are a helpful assistant that matches user requests to the most appropriate form from a list of available forms.

User request: "{user_input}"

Available forms:
{chr(10).join([f"- {form}" for form in forms_list])}

Please analyze the user's request and return ONLY the exact filename of the most appropriate form from the list above. Consider:
- Keywords in the user's request
- The purpose or type of form they might need
- Common business/finance form purposes

Return only the filename, nothing else."""

        # Prepare the request body for Claude
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        suggested_form = response_body['content'][0]['text'].strip()
        
        # Validate that the suggested form is in our list
        if suggested_form in forms_list:
            return suggested_form
        else:
            # Fallback: try to find a partial match
            for form in forms_list:
                if suggested_form.lower() in form.lower() or form.lower() in suggested_form.lower():
                    return form
            
            # If no match found, return the first form as fallback
            print(f"Warning: Claude suggested '{suggested_form}' which wasn't found in the list.")
            return forms_list[0] if forms_list else None
            
    except Exception as e:
        print(f"Error connecting to Bedrock: {e}")
        print("Falling back to simple keyword matching...")
        
        # Fallback: simple keyword matching
        user_lower = user_input.lower()
        for form in forms_list:
            form_words = form.lower().replace('.pdf', '').replace('_', ' ').split()
            if any(word in user_lower for word in form_words):
                return form
        
        # If no keyword match, return first form
        return forms_list[0] if forms_list else None

# def display_forms(forms_list, title="Downloaded Forms"):
#     """Display a numbered list of forms."""
#     if forms_list:
#         print(f"\n{title} ({len(forms_list)} files):")
#         print("=" * (len(title) + 20))
#         
#         for i, form_name in enumerate(forms_list, 1):
#             print(f"{i:2d}. {form_name}")
#         
#         print(f"\nPython list:")
#         print(forms_list)
#     else:
#         print(f"\nNo {title.lower()} found.")

# def main():
#     """Main function to create and display the forms list."""
#     print("FHDA Finance Forms List Creator")
#     print("=" * 35)
#     
#     # Get all forms from the downloaded_forms folder and create a Python list
#     downloaded_forms_list = get_downloaded_forms_list()
#     
#     # Display the results
#     display_forms(downloaded_forms_list)
#     
#     return downloaded_forms_list

# if __name__ == "__main__":
#     main()

user_input = input("What form do you need to fill out? Describe your request: ").strip()

# Get the list of available forms
forms_list = get_downloaded_forms_list()

if not forms_list:
    print("No forms found in the downloaded_forms folder. Please run form-downloader.py first.")
else:
    print(f"\nFound {len(forms_list)} available forms.")
    print("Analyzing your request with Claude...")
    
    # Use Claude to find the best matching form
    best_form = find_best_form(user_input, forms_list)
    
    if best_form:
        print(f"\n✅ Based on your request, the most likely form you need is:")
        print(f"📄 {best_form}")
        
        # Optional: Open the form (you can uncomment this if you want to automatically open it)
        # import subprocess
        # form_path = os.path.join("downloaded_forms", best_form)
        # subprocess.run(["open", form_path])  # On macOS
        # print(f"Opening {best_form}...")
    else:
        print("❌ Could not determine the best form for your request.")

