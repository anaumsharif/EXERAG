import requests
import os
from dotenv import load_dotenv
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

from base_loader import BaseDataLoader

# Load environment variables from the .env file
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()


class SharePointDataLoader(BaseDataLoader):
    def __init__(self):
        super().__init__()
        self.site_url = os.getenv("SHAREPOINT_SITE_URL")
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

    

        # Check for missing environment variables
        if not all([self.site_url, self.tenant_id, self.client_id, self.client_secret]):
            missing_vars = []
            if not self.site_url:
                missing_vars.append("SHAREPOINT_SITE_URL")
            if not self.tenant_id:
                missing_vars.append("TENANT_ID")
            if not self.client_id:
                missing_vars.append("CLIENT_ID")
            if not self.client_secret:
                missing_vars.append("CLIENT_SECRET")
            raise ValueError(f"Missing credentials: {', '.join(missing_vars)}")


        print(f"SHAREPOINT_SITE_URL: {self.site_url}")

        # Authenticate with SharePoint
        self.ctx = self._authenticate()

    def _authenticate(self):
        print("Attempting to authenticate...")
        client_credentials = ClientCredential(self.client_id, self.client_secret)
        ctx = ClientContext(self.site_url).with_credentials(client_credentials)
        print("Authentication successful.")
        return ctx

    def load_data(self):
        try:
            print(f"Loading data from site: {self.site_url}")

            # Get the root folder of the SharePoint site
            root_folder = self.ctx.web.get_folder_by_server_relative_url("")
            files = root_folder.files
            self.ctx.load(files)
            self.ctx.execute_query()

            # Filter files by file type (e.g., PDF)
            files_to_process = [
                file for file in files if file.name.endswith(self.file_type)
            ]

            print(f"Files to download: {[file.name for file in files_to_process]}")

            self.process_files(files_to_process)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise RuntimeError(f"An error occurred: {str(e)}")

    def process_files(self, files):
        for i, file in enumerate(files):
            local_file_path = os.path.join(self.download_folder, file.name)

            print(f"Downloading file {i + 1}/{len(files)}: {file.name}")

            with open(local_file_path, "wb") as local_file:
                file_content = file.read()
                local_file.write(file_content)

            print(f"Downloaded file {i + 1}/{len(files)}: {file.name}")
