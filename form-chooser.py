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
    Use Amazon Bedrock Claude to find the top 3 most likely forms based on user input.
    
    Args:
        user_input (str): What the user wants to fill out
        forms_list (list): List of available form names
        
    Returns:
        list: The top 3 most likely form names from the list
    """
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Create the prompt
        prompt = f"""You are a helpful assistant that matches user requests to the most appropriate forms from a list of available forms.

User request: "{user_input}"

Available forms:
{chr(10).join([f"- {form}" for form in forms_list])}

Please analyze the user's request and return the TOP 3 most appropriate forms from the list above, ranked from most likely to least likely. Consider:
- Keywords in the user's request
- The purpose or type of form they might need
- Common business/finance form purposes

Return ONLY the 3 exact filenames, one per line, in order of likelihood. Do not include numbers, bullets, or any other text. Example format:
Form_Name_1.pdf
Form_Name_2.pdf
Form_Name_3.pdf"""

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
        suggested_forms_text = response_body['content'][0]['text'].strip()
        
        # Parse the response into a list of forms
        suggested_forms = [form.strip() for form in suggested_forms_text.split('\n') if form.strip()]
        
        # Validate and filter forms that exist in our list
        valid_forms = []
        for suggested_form in suggested_forms[:3]:  # Take only top 3
            if suggested_form in forms_list:
                valid_forms.append(suggested_form)
            else:
                # Try to find a partial match
                for form in forms_list:
                    if suggested_form.lower() in form.lower() or form.lower() in suggested_form.lower():
                        if form not in valid_forms:  # Avoid duplicates
                            valid_forms.append(form)
                        break
        
        # If we have less than 3 valid forms, fill with fallback matches
        if len(valid_forms) < 3:
            print(f"Warning: Claude suggested forms that weren't all found in the list. Using fallback matching.")
            return fallback_keyword_matching(user_input, forms_list, 3)
        
        return valid_forms[:3]
            
    except Exception as e:
        print(f"Error connecting to Bedrock: {e}")
        print("Falling back to simple keyword matching...")
        
        return fallback_keyword_matching(user_input, forms_list, 3)

def fallback_keyword_matching(user_input, forms_list, num_results=3):
    """
    Fallback method to find forms using simple keyword matching.
    
    Args:
        user_input (str): User's request
        forms_list (list): List of available forms
        num_results (int): Number of results to return
        
    Returns:
        list: Top matching forms
    """
    user_lower = user_input.lower()
    scored_forms = []
    
    for form in forms_list:
        score = 0
        form_words = form.lower().replace('.pdf', '').replace('_', ' ').split()
        
        # Score based on word matches
        for word in form_words:
            if word in user_lower:
                score += len(word)  # Longer matches get higher scores
        
        if score > 0:
            scored_forms.append((score, form))
    
    # Sort by score (descending) and return top results
    scored_forms.sort(reverse=True)
    
    # If we have scored results, return them
    if scored_forms:
        return [form for score, form in scored_forms[:num_results]]
    
    # If no keyword matches, return first few forms
    return forms_list[:num_results]

user_input = input("What form do you need to fill out? Describe your request: ").strip()

# Get the list of available forms
forms_list = get_downloaded_forms_list()

if not forms_list:
    print("No forms found in the downloaded_forms folder. Please run form-downloader.py first.")
else:
    print(f"\nFound {len(forms_list)} available forms.")
    print("Analyzing your request with Claude...")
    
    # Use Claude to find the top 3 matching forms
    best_forms = find_best_form(user_input, forms_list)
    
    if best_forms:
        print(f"\n✅ Based on your request, here are the top 3 most likely forms you need:")
        for i, form in enumerate(best_forms, 1):
            print(f"{i}. 📄 {form}")
        
        print(f"\nTop recommendation: {best_forms[0]}")
        
        # Optional: Open the top recommended form (you can uncomment this if you want to automatically open it)
        # import subprocess
        # form_path = os.path.join("downloaded_forms", best_forms[0])
        # subprocess.run(["open", form_path])  # On macOS
        # print(f"Opening {best_forms[0]}...")
    else:
        print("❌ Could not determine the best forms for your request.")

