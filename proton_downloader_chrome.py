import os
import time
import random 
import glob # <--- NEW: Import glob for file listing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Define the selector for the modal backdrop which causes the click interception error
MODAL_BACKDROP_SELECTOR = (By.CLASS_NAME, "modal-two-backdrop")
CONFIRM_BUTTON_SELECTOR = (By.CSS_SELECTOR, ".button-solid-norm:nth-child(2)")

# Constants
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloaded_configs")
TARGET_COUNTRY_NAME = "United States"
MAX_DOWNLOADS_PER_SESSION = 20 # Maximum downloads before relogin
RELOGIN_DELAY = 120 # Delay in seconds between sessions to cool down the IP

# Create the download directory if it doesn't exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
    print(f"Created download directory: {DOWNLOAD_DIR}")


class ProtonVPN:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        
        # --- Optimization for GitHub Actions/Server Environments ---
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        
        # *** Key Configuration: Setting the Download Path in Chrome ***
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True 
        }
        self.options.add_experimental_option("prefs", prefs)

        self.driver = None

    def setup(self):
        """Initializes the WebDriver (Chrome) with Headless options."""
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_window_size(1936, 1048)
        self.driver.implicitly_wait(10)
        print("WebDriver initialized successfully in Headless mode (Chrome).")

    def teardown(self):
        """Closes the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed.")
            
    def login(self, username, password):
        try:
            self.driver.get("https://protonvpn.com/")
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//a[contains(@href, 'https://account.protonvpn.com/login')]").click()
            time.sleep(2)
            user_field = self.driver.find_element(By.ID, "username")
            user_field.clear()
            user_field.send_keys(username)
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, ".button-large").click()
            time.sleep(2)
            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.clear()
            pass_field.send_keys(password)
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, ".button-large").click()
            time.sleep(5)
            print("Login Successful.")
            return True
        except Exception as e:
            print(f"Error Login: {e}")
            return False

    def navigate_to_downloads(self):
        try:
            downloads_link_selector = (By.CSS_SELECTOR, ".navigation-item:nth-child(7) .text-ellipsis")
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(downloads_link_selector)
            ).click()
            time.sleep(3)
            print("Navigated to Downloads section.")
            return True
        except Exception as e:
            print(f"Error Navigating to Downloads: {e}")
            return False

    def logout(self):
        try:
            self.driver.get("https://account.protonvpn.com/logout") 
            time.sleep(3)
            print("Logout Successful.")
            return True
        except Exception as e:
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".p-1").click()
                time.sleep(1)
                self.driver.find_element(By.CSS_SELECTOR, ".mb-4 > .button").click()
                time.sleep(2)
                print("Logout Successful via UI.")
                return True
            except Exception as e:
                print(f"Error Logout: {e}")
                return False

    def get_downloaded_filenames(self):
        """Returns a set of filenames (without full path) currently in the download directory."""
        return set(os.path.basename(f) for f in glob.glob(os.path.join(DOWNLOAD_DIR, '*')) if os.path.isfile(f))

    def process_downloads(self):
        """
        Processes downloads for the target country, skipping previously downloaded files.
        Returns True if all downloads for the country are finished, False otherwise.
        """
        try:
            self.driver.execute_script("window.scrollTo(0,0)")
            time.sleep(2)

            try:
                self.driver.find_element(By.CSS_SELECTOR, ".flex:nth-child(4) > .mr-8:nth-child(3) > .relative").click()
                time.sleep(2)
            except:
                pass
            
            # --- NEW: Get list of already downloaded files ---
            downloaded_files = self.get_downloaded_filenames()
            print(f"Found {len(downloaded_files)} configurations already downloaded.")
            # ----------------------------------------------------

            countries = self.driver.find_elements(By.CSS_SELECTOR, ".mb-6 details")
            print(f"Found {len(countries)} total countries to check.")
            
            download_counter = 0
            all_downloads_finished = True 

            for country in countries:
                try:
                    country_name_element = country.find_element(By.CSS_SELECTOR, "summary")
                    country_name = country_name_element.text.split('\n')[0].strip()
                    
                    if TARGET_COUNTRY_NAME not in country_name:
                        continue
                    
                    print(f"--- Processing target country: {country_name} ---")

                    self.driver.execute_script("arguments[0].open = true;", country)
                    time.sleep(0.5)

                    rows = country.find_elements(By.CSS_SELECTOR, "tr")

                    for index, row in enumerate(rows[1:]): # Skip header row
                        
                        # --- 1. Identify the file name before clicking the button ---
                        # The filename is usually displayed in the second column (or similar)
                        # We look for the button cell and the filename cell (usually the first cell in the row)
                        
                        try:
                            # Assuming the server name/filename is the first column in the row
                            file_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(1)")
                            filename_base = file_cell.text.strip().replace(" ", "-") # Match filename format
                            
                            # ProtonVPN uses 'wg-SERVERNAME.conf' for WireGuard and 'SERVERNAME.udp.ovpn' for OpenVPN
                            # Since we click the button, we need to know the *final* file name.
                            # We assume the name is derived from the cell content plus an extension.
                            
                            # Find the actual download button in the row
                            btn = row.find_element(By.CSS_SELECTOR, ".button")
                            
                            # Since ProtonVPN page doesn't explicitly show the full filename until download:
                            # We rely on the name displayed in the first cell, which is the server ID (e.g., US-FREE-10)
                            # We assume the generated filename uses this server ID (e.g., wg-US-FREE-10.conf)
                            # To be safe, we check for both OpenVPN and WireGuard naming conventions:
                            
                            server_id = file_cell.text.strip()
                            possible_filenames = [
                                f"wg-{server_id}.conf", 
                                f"{server_id.lower().replace('-', '')}.udp.ovpn" # Example: usfree10.udp.ovpn
                            ]
                            
                            # Check if either possible filename exists in the downloaded set
                            if any(f in downloaded_files for f in possible_filenames):
                                print(f"Skipping config (Server ID: {server_id}). Already downloaded.")
                                continue

                        except Exception as e:
                            print(f"Could not determine filename for row {index}. Proceeding cautiously. Error: {e}")
                            # If we cannot parse the name, we must assume it's new and download it.
                            pass 

                        # --- 2. Check session limit ---
                        if download_counter >= MAX_DOWNLOADS_PER_SESSION:
                            print(f"Session limit reached ({MAX_DOWNLOADS_PER_SESSION}). Stopping for relogin...")
                            all_downloads_finished = False 
                            return all_downloads_finished
                        
                        random_delay = random.randint(60, 90)
                        
                        # --- 3. Execute Download ---
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(0.5)

                            ActionChains(self.driver).move_to_element(btn).click().perform()

                            confirm_btn = WebDriverWait(self.driver, 30).until(
                                EC.element_to_be_clickable(CONFIRM_BUTTON_SELECTOR)
                            )
                            confirm_btn.click()

                            WebDriverWait(self.driver, 30).until(
                                EC.invisibility_of_element_located(MODAL_BACKDROP_SELECTOR)
                            )
                            
                            download_counter += 1
                            print(f"Successfully downloaded config (Server ID: {server_id}). Total in session: {download_counter}. Waiting {random_delay}s...")
                            time.sleep(random_delay) 

                            # --- NEW: Update the list of downloaded files immediately ---
                            downloaded_files.add(f"wg-{server_id}.conf") # Add primary WireGuard name to avoid future re-downloads
                            # We don't need to add the OpenVPN name if we skip the OpenVPN tab, 
                            # but we add the primary name we expect.
                            
                        except (TimeoutException, ElementClickInterceptedException) as e:
                            print(f"CRITICAL ERROR: Failed to download config {server_id}. Rate limit or session issue detected. Shutting down session.")
                            all_downloads_finished = False
                            return all_downloads_finished
                        
                        except Exception as e:
                            print(f"General error during download {server_id}: {e}. Shutting down session.")
                            all_downloads_finished = False
                            return all_downloads_finished
                            
                    # Finished processing all rows for United States.
                    print(f"All available configs for {country_name} processed in this run.")
                    break 

                except Exception as e:
                    print(f"Error processing country block: {e}")
                    all_downloads_finished = False 
                    return all_downloads_finished


        except Exception as e:
            print(f"Error in main download loop: {e}")
            all_downloads_finished = False
            
        return all_downloads_finished 


    def run(self, username, password):
        """Executes the full automation workflow with relogin cycle."""
        
        all_downloads_finished = False
        session_count = 0
        
        try:
            while not all_downloads_finished and session_count < 10: 
                
                session_count += 1
                print(f"\n###################### Starting Session {session_count} ######################")
                
                # 1. Setup Driver and Login
                self.setup()
                if not self.login(username, password):
                    print("Failed to log in. Aborting run.")
                    break
                
                # 2. Navigate and Download
                if self.navigate_to_downloads():
                    all_downloads_finished = self.process_downloads()
                
                # 3. Logout
                self.logout()
                self.teardown() 
                
                if all_downloads_finished:
                    print("\n###################### All configurations downloaded successfully! ######################")
                else:
                    print(f"Session {session_count} completed. Waiting {RELOGIN_DELAY} seconds before relogging in...")
                    time.sleep(RELOGIN_DELAY) 

        except Exception as e:
            print(f"Runtime Error in main loop: {e}")
        finally:
            self.teardown()


if __name__ == "__main__":
    USERNAME = os.environ.get("VPN_USERNAME")
    PASSWORD = os.environ.get("VPN_PASSWORD")
    
    if not USERNAME or not PASSWORD:
        print("---")
        print("ERROR: VPN_USERNAME or VPN_PASSWORD not loaded from environment variables.")
        print("Please configure them as Secrets in your GitHub repository.")
        print("---")
    else:
        print("Account info loaded from environment variables. Starting workflow...")
        proton = ProtonVPN()
        proton.run(USERNAME, PASSWORD)
