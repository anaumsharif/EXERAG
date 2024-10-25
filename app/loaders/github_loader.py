from langchain_community.document_loaders import GithubFileLoader , GitHubIssuesLoader
from io import BytesIO
# from loaders.base_loader import BaseDataLoader
import os
from utils.preprocess import make_text_tokenization_safe
from langchain.schema import Document
# Load environment variables from the .env file
from utils.initialize import load_env_variables
from utils.config_settings import config
from loaders.base_loader import BaseDataLoader

env_name = load_env_variables()

access_token = config[env_name].GITHUB_ACCESS_TOKEN
github_repo_name = config[env_name].REPO_NAME
github_branch_name = config[env_name].BRANCH_NAME
    
def docs_preprocessing(documents):
    cleaned_docs = []
    try:
        
        for doc in documents:
            file_path = doc.metadata['source'] 
            file_name = doc.metadata['path']
            file_sha = doc.metadata['sha']
            file_content = make_text_tokenization_safe(doc.page_content) # Use content directly without conversion
            cleaned_docs.append(Document(page_content=file_content, metadata={
                    'source' : file_path , 'name' : file_name, "sha" : file_sha
                }))
    except Exception as e:
        print(f"Error processing files: {str(e)}")
    return cleaned_docs

class GithubLoader(BaseDataLoader):
    def __init__(self):
        super().__init__()
        self.access_token = access_token
        self.github_repo_name = github_repo_name
        self.github_branch_name = github_branch_name
        self.file_types = os.getenv("FILE_TYPE", "all").split(",") 
    
        
    
    def load_data(self,file_type):
            """
            Process all files in the gtihub using GithubFileLoader.
            Returns a list of extracted texts.
            """
            self.file_types=file_type.split(",")  
            if 'all' in self.file_types:
                self.loader = GithubFileLoader(
                repo= github_repo_name ,  # the repo name
                branch= github_branch_name,  # the branch name
                access_token=access_token,
                github_api_url="https://api.github.com",
                file_filter=lambda file_path: True,
                # load all files.
            )
                documents = self.loader.load()
                cleaned_documents = docs_preprocessing(documents)
                return cleaned_documents
    
            else :
                self.loader = GithubFileLoader(
                repo= github_repo_name ,  # the repo name
                branch= github_branch_name,  # the branch name
                access_token=access_token,
                github_api_url="https://api.github.com",
                file_filter=lambda file_path: file_path.endswith(tuple(self.file_types)),
                # load all files.
            )
                documents = self.loader.load()
                cleaned_documents = docs_preprocessing(documents)
                return cleaned_documents
                 


            



