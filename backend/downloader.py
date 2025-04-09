import os
import requests
import time
from urllib.parse import urlparse, urlencode, parse_qs
from playwright.sync_api import sync_playwright

def get_semesters(username, password):
    """Return predefined semesters with their category IDs"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Login to verify credentials
        print(f"Logging in as {username}...")
        page.goto("http://192.248.50.240/login/index.php", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        try:
            page.wait_for_url("**/my/**", timeout=10000)
            print("Login successful")
        except Exception as e:
            print(f"Login failed: {e}")
            browser.close()
            return {"error": "Login failed"}
        
        browser.close()
        
        # Return predefined semester structure
        return [
            # Common Core
            {'id': '12', 'name': 'Semester 1 (Common Core)', 'url': 'http://192.248.50.240/course/index.php?categoryid=12'},
            {'id': '13', 'name': 'Semester 2 (Common Core)', 'url': 'http://192.248.50.240/course/index.php?categoryid=13'},
            
            # Computer Engineering
            {'id': '15', 'name': 'Semester 3 (Computer Engineering)', 'url': 'http://192.248.50.240/course/index.php?categoryid=15'},
            {'id': '16', 'name': 'Semester 4 (Computer Engineering)', 'url': 'http://192.248.50.240/course/index.php?categoryid=16'},
            {'id': '17', 'name': 'Semester 5 (Computer Engineering)', 'url': 'http://192.248.50.240/course/index.php?categoryid=17'},
            {'id': '18', 'name': 'Semester 6 (Computer Engineering)', 'url': 'http://192.248.50.240/course/index.php?categoryid=18'},
            {'id': '19', 'name': 'Semester 7 (Computer Engineering)', 'url': 'http://192.248.50.240/course/index.php?categoryid=19'},
            {'id': '20', 'name': 'Semester 8 (Computer Engineering)', 'url': 'http://192.248.50.240/course/index.php?categoryid=20'}
        ]

def get_modules(username, password, semester_id):
    """Get available modules for a specific semester"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Login process
        print(f"Logging in as {username}...")
        page.goto("http://192.248.50.240/login/index.php", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        try:
            page.wait_for_url("**/my/**", timeout=10000)
            print("Login successful")
        except Exception as e:
            print(f"Login may have failed: {e}")
            browser.close()
            return {"error": "Login failed"}
        
        # Navigate to semester page
        semester_url = f"http://192.248.50.240/course/index.php?categoryid={semester_id}"
        page.goto(semester_url, wait_until="networkidle")
        
        # Find all course boxes
        modules = []
        course_boxes = page.query_selector_all('.coursebox')
        
        for course_box in course_boxes:
            try:
                # Extract course ID
                course_id = course_box.get_attribute('data-courseid')
                
                # Extract course name
                name_element = course_box.query_selector('.coursename a')
                if name_element:
                    course_name = name_element.text_content().strip()
                    course_url = name_element.get_attribute('href')
                    
                    # Extract teacher info
                    teachers = []
                    teacher_elements = course_box.query_selector_all('.teachers a')
                    for teacher in teacher_elements:
                        teachers.append(teacher.text_content().strip())
                    
                    modules.append({
                        'id': course_id,
                        'name': course_name,
                        'url': course_url,
                        'teachers': teachers
                    })
            except Exception as e:
                print(f"Error processing module: {e}")
        
        browser.close()
        return modules

# Keep the existing download_materials function unchanged

def download_materials(username, password, module_url, save_path):
    absolute_save_path = os.path.abspath(save_path)
    os.makedirs(absolute_save_path, exist_ok=True)
    print(f"Base download directory: {absolute_save_path}")

    with sync_playwright() as p:
        # Launch with specific options to avoid detection
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-web-security']
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Login process
        print(f"Logging in as {username}...")
        page.goto("http://192.248.50.240/login/index.php", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        try:
            page.wait_for_url("**/my/**", timeout=10000)
            print("Login successful")
        except Exception as e:
            print(f"Login may have failed: {e}")
        
        # Store cookies for direct downloads
        cookies = context.cookies()
        cookie_jar = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Navigate to module page
        print(f"Navigating to {module_url}")
        page.goto(module_url, wait_until="networkidle")
        time.sleep(2)  # Wait to ensure page is fully loaded
        
        # Extract module name from page title
        page_title = page.title()
        print(f"Page title: {page_title}")
        
        # Better module name extraction for Moodle format: "Course: EE6350 Artificial Intelligence (23rd) | ELMS"
        if ": " in page_title:
            # Get everything after the first ": " but before any following "|"
            module_name = page_title.split(": ")[1].split(" |")[0].strip()
        elif " - " in page_title:
            # Alternative format "EE6350 - Artificial Intelligence - Moodle"
            module_name = page_title.split(" - ")[0].strip()
        else:
            # Just use the whole title as fallback
            module_name = page_title.strip()
        
        # If we still don't have a good name, extract from URL
        if not module_name or len(module_name) < 3:
            # Extract course ID from URL
            parsed_url = urlparse(module_url)
            query_params = parse_qs(parsed_url.query)
            course_id = query_params.get('id', ['unknown'])[0]
            module_name = f"Course_{course_id}"
        
        print(f"Extracted module name: {module_name}")
        
        # Sanitize folder name - remove characters that aren't allowed in filenames
        import re
        module_folder_name = re.sub(r'[\\/*?:"<>|]', "_", module_name)
        module_folder_name = module_folder_name.strip()
        
        # Create module-specific folder
        module_folder_path = os.path.join(absolute_save_path, module_folder_name)
        os.makedirs(module_folder_path, exist_ok=True)
        print(f"Created module folder: {module_folder_path}")
        
        # Find all resource links directly on the page
        downloaded_count = 0
        
        # Click on each resource link instead of navigating directly
        resource_elements = page.query_selector_all('a.aalink')
        
        for i, resource_element in enumerate(resource_elements):
            try:
                # Get name before clicking
                name_element = resource_element.query_selector('.instancename')
                resource_name = name_element.text_content().split(" File")[0] if name_element else f"resource_{i}"
                href = resource_element.get_attribute('href')
                
                if href and "resource" in href:
                    print(f"Attempting to download: {resource_name}")
                    
                    # Modify URL to force download
                    # Extract the ID parameter 
                    parsed_url = urlparse(href)
                    query_params = parse_qs(parsed_url.query)
                    resource_id = query_params.get('id', [''])[0]
                    
                    if resource_id:
                        # Construct direct file URL with forcedownload parameter
                        file_url = f"http://192.248.50.240/mod/resource/view.php?id={resource_id}&redirect=1&forcedownload=1"
                        
                        print(f"Direct download URL: {file_url}")
                        
                        # Use requests with session cookies to download
                        response = requests.get(
                            file_url, 
                            cookies=cookie_jar,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                'Referer': module_url
                            },
                            allow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            # Try to get filename from content-disposition header
                            content_disposition = response.headers.get('content-disposition')
                            if content_disposition and 'filename=' in content_disposition:
                                import re
                                filename_match = re.search(r'filename="?([^";]+)', content_disposition)
                                filename = filename_match.group(1) if filename_match else f"{resource_name}.pdf"
                            else:
                                # Fallback to URL parsing or use resource name
                                filename = os.path.basename(urlparse(response.url).path)
                                if not filename or filename == '' or '?' in filename:
                                    filename = f"{resource_name}.pdf"
                            
                            # Save the file to module folder
                            file_path = os.path.join(module_folder_path, filename)
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            print(f"Successfully downloaded: {filename}")
                            downloaded_count += 1
                        else:
                            print(f"Failed to download with status: {response.status_code}")
            except Exception as e:
                print(f"Failed to process resource: {str(e)}")
            
            # Avoid overwhelming the server
            time.sleep(1)

        browser.close()
        
        # List files in the module directory
        print(f"Files downloaded to {module_folder_path}:")
        try:
            files = os.listdir(module_folder_path)
            for file in files:
                print(f"  - {file}")
            
            if not files:
                print("  No files found in directory!")
        except Exception as e:
            print(f"Error listing files: {e}")
            
        return f"Downloaded {downloaded_count} files to: {module_folder_path}"
    absolute_save_path = os.path.abspath(save_path)
    os.makedirs(absolute_save_path, exist_ok=True)
    print(f"Base download directory: {absolute_save_path}")

    with sync_playwright() as p:
        # Launch with specific options to avoid detection
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-web-security']
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Login process
        print(f"Logging in as {username}...")
        page.goto("http://192.248.50.240/login/index.php", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        try:
            page.wait_for_url("**/my/**", timeout=10000)
            print("Login successful")
        except Exception as e:
            print(f"Login may have failed: {e}")
        
        # Store cookies for direct downloads
        cookies = context.cookies()
        cookie_jar = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Navigate to module page
        print(f"Navigating to {module_url}")
        page.goto(module_url, wait_until="networkidle")
        time.sleep(2)  # Wait to ensure page is fully loaded
        
        # Extract module name from page title
        page_title = page.title()
        print(f"Page title: {page_title}")
        
        # Extract module name properly - format is usually "Course Name: Section - Moodle"
        if ":" in page_title:
            module_name = page_title.split(":")[0].strip()
        else:
            module_name = page_title.split("-")[0].strip() if "-" in page_title else page_title.strip()
        
        # If we still don't have a good name, extract from URL
        if not module_name or len(module_name) < 3:
            # Extract course ID from URL
            parsed_url = urlparse(module_url)
            query_params = parse_qs(parsed_url.query)
            course_id = query_params.get('id', ['unknown'])[0]
            module_name = f"Course_{course_id}"
        
        print(f"Extracted module name: {module_name}")
        
        # Sanitize folder name - remove characters that aren't allowed in filenames
        import re
        module_folder_name = re.sub(r'[\\/*?:"<>|]', "_", module_name)
        module_folder_name = module_folder_name.strip()
        
        # Create module-specific folder
        module_folder_path = os.path.join(absolute_save_path, module_folder_name)
        os.makedirs(module_folder_path, exist_ok=True)
        print(f"Created module folder: {module_folder_path}")
        
        # Rest of the download code remains the same, but make sure to save to module_folder_path
        # ...
        
        # When saving files, use:
        file_path = os.path.join(module_folder_path, filename)
    absolute_save_path = os.path.abspath(save_path)
    os.makedirs(absolute_save_path, exist_ok=True)
    print(f"Base download directory: {absolute_save_path}")

    with sync_playwright() as p:
        # Launch with specific options to avoid detection
        browser = p.chromium.launch(
            headless=False,  # Set to False for debugging
            args=['--disable-web-security']
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Login process
        print(f"Logging in as {username}...")
        page.goto("http://192.248.50.240/login/index.php", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        try:
            page.wait_for_url("**/my/**", timeout=10000)
            print("Login successful")
        except Exception as e:
            print(f"Login may have failed: {e}")
        
        # Store cookies for direct downloads
        cookies = context.cookies()
        cookie_jar = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Navigate to module page
        print(f"Navigating to {module_url}")
        page.goto(module_url, wait_until="networkidle")
        time.sleep(2)  # Wait to ensure page is fully loaded
        
        # Extract module name from page title
        module_name = page.title().split(":")[0].strip()
        if not module_name or len(module_name) < 3:
            # Fallback to URL if title is too short
            module_name = urlparse(module_url).path.split('/')[-1]
            if not module_name or module_name == "view.php":
                module_name = f"module_{urlparse(module_url).query}"
        
        # Create a sanitized folder name
        import re
        module_folder_name = re.sub(r'[<>:"/\\|?*]', '_', module_name)  # Remove invalid filename chars
        
        # Create module-specific folder
        module_folder_path = os.path.join(absolute_save_path, module_folder_name)
        os.makedirs(module_folder_path, exist_ok=True)
        print(f"Saving files to module folder: {module_folder_path}")
        
        # Find all resource links directly on the page
        downloaded_count = 0
        
        # Click on each resource link instead of navigating directly
        resource_elements = page.query_selector_all('a.aalink')
        
        for i, resource_element in enumerate(resource_elements):
            try:
                # Get name before clicking
                name_element = resource_element.query_selector('.instancename')
                resource_name = name_element.text_content().split(" File")[0] if name_element else f"resource_{i}"
                href = resource_element.get_attribute('href')
                
                if href and "resource" in href:
                    print(f"Attempting to download: {resource_name}")
                    
                    # Modify URL to force download
                    # Extract the ID parameter 
                    parsed_url = urlparse(href)
                    query_params = parse_qs(parsed_url.query)
                    resource_id = query_params.get('id', [''])[0]
                    
                    if resource_id:
                        # Construct direct file URL with forcedownload parameter
                        file_url = f"http://192.248.50.240/mod/resource/view.php?id={resource_id}&redirect=1&forcedownload=1"
                        
                        print(f"Direct download URL: {file_url}")
                        
                        # Use requests with session cookies to download
                        response = requests.get(
                            file_url, 
                            cookies=cookie_jar,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                'Referer': module_url
                            },
                            allow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            # Try to get filename from content-disposition header
                            content_disposition = response.headers.get('content-disposition')
                            if content_disposition and 'filename=' in content_disposition:
                                import re
                                filename_match = re.search(r'filename="?([^";]+)', content_disposition)
                                filename = filename_match.group(1) if filename_match else f"{resource_name}.pdf"
                            else:
                                # Fallback to URL parsing or use resource name
                                filename = os.path.basename(urlparse(response.url).path)
                                if not filename or filename == '' or '?' in filename:
                                    filename = f"{resource_name}.pdf"
                            
                            # Save the file to module folder
                            file_path = os.path.join(module_folder_path, filename)
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            print(f"Successfully downloaded: {filename}")
                            downloaded_count += 1
                        else:
                            print(f"Failed to download with status: {response.status_code}")
            except Exception as e:
                print(f"Failed to process resource: {str(e)}")
            
            # Avoid overwhelming the server
            time.sleep(1)

        browser.close()
        
        # List files in the module directory
        print(f"Files downloaded to {module_folder_path}:")
        try:
            files = os.listdir(module_folder_path)
            for file in files:
                print(f"  - {file}")
            
            if not files:
                print("  No files found in directory!")
        except Exception as e:
            print(f"Error listing files: {e}")
            
        return f"Downloaded {downloaded_count} files to: {module_folder_path}"
    absolute_save_path = os.path.abspath(save_path)
    os.makedirs(absolute_save_path, exist_ok=True)
    print(f"Saving files to: {absolute_save_path}")

    with sync_playwright() as p:
        # Launch with specific options to avoid detection
        browser = p.chromium.launch(
            headless=False,  # Set to False for debugging
            args=['--disable-web-security']
        )
        
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Login process
        print(f"Logging in as {username}...")
        page.goto("http://192.248.50.240/login/index.php", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        try:
            page.wait_for_url("**/my/**", timeout=10000)
            print("Login successful")
        except Exception as e:
            print(f"Login may have failed: {e}")
        
        # Store cookies for direct downloads
        cookies = context.cookies()
        cookie_jar = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Navigate to module page
        print(f"Navigating to {module_url}")
        page.goto(module_url, wait_until="networkidle")
        time.sleep(2)  # Wait to ensure page is fully loaded
        
        # Find all resource links directly on the page
        downloaded_count = 0
        
        # Click on each resource link instead of navigating directly
        resource_elements = page.query_selector_all('a.aalink')
        
        for i, resource_element in enumerate(resource_elements):
            try:
                # Get name before clicking
                name_element = resource_element.query_selector('.instancename')
                resource_name = name_element.text_content().split(" File")[0] if name_element else f"resource_{i}"
                href = resource_element.get_attribute('href')
                
                if href and "resource" in href:
                    print(f"Attempting to download: {resource_name}")
                    
                    # Modify URL to force download
                    # Extract the ID parameter 
                    parsed_url = urlparse(href)
                    query_params = parse_qs(parsed_url.query)
                    resource_id = query_params.get('id', [''])[0]
                    
                    if resource_id:
                        # Construct direct file URL with forcedownload parameter
                        # This is a common pattern in Moodle to bypass the preview and force download
                        file_url = f"http://192.248.50.240/mod/resource/view.php?id={resource_id}&redirect=1&forcedownload=1"
                        
                        print(f"Direct download URL: {file_url}")
                        
                        # Use requests with session cookies to download
                        response = requests.get(
                            file_url, 
                            cookies=cookie_jar,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                'Referer': module_url
                            },
                            allow_redirects=True  # Follow redirects to get the actual file
                        )
                        
                        if response.status_code == 200:
                            # Try to get filename from content-disposition header
                            content_disposition = response.headers.get('content-disposition')
                            if content_disposition and 'filename=' in content_disposition:
                                import re
                                filename_match = re.search(r'filename="?([^";]+)', content_disposition)
                                filename = filename_match.group(1) if filename_match else f"{resource_name}.pdf"
                            else:
                                # Fallback to URL parsing or use resource name
                                filename = os.path.basename(urlparse(response.url).path)
                                if not filename or filename == '' or '?' in filename:
                                    filename = f"{resource_name}.pdf"
                            
                            # Save the file
                            file_path = os.path.join(absolute_save_path, filename)
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            print(f"Successfully downloaded: {filename}")
                            downloaded_count += 1
                        else:
                            print(f"Failed to download with status: {response.status_code}")
            except Exception as e:
                print(f"Failed to process resource: {str(e)}")
            
            # Avoid overwhelming the server
            time.sleep(1)

        browser.close()
        
        # List files in the directory to verify downloads
        print(f"Files in download directory:")
        try:
            files = os.listdir(absolute_save_path)
            for file in files:
                print(f"  - {file}")
            
            if not files:
                print("  No files found in directory!")
        except Exception as e:
            print(f"Error listing files: {e}")
            
        return f"Downloaded {downloaded_count} files to: {absolute_save_path}"