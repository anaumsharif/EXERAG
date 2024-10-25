import os



# Load environment variables from .env file
# load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    FILE_TYPE = os.getenv("FILE_TYPE", "pdf,image")  # pdf,image,docx



class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    LLAMA_PARSE_API_KEY = os.getenv("LLAMA_PARSE_API_KEY")
    PINECONE_INDEX_NAME = "geniqv1"
    SOURCE = os.getenv("SOURCE")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    REGION_NAME = os.getenv("REGION_NAME")
    SAS_URL = os.getenv("SAS_URL")
    AZURE_CONTAINER_NAME=os.getenv("AZURE_CONTAINER_NAME")
    CONNECTION_STR=os.getenv("CONNECTION_STR")
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    FILE_URLS = os.getenv("FILE_URLS")
    GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
    BRANCH_NAME = os.getenv("BRANCH_NAME")
    REPO_NAME = os.getenv("REPO_NAME")
    INTEGRATION_TOKEN = os.getenv("INTEGRATION_TOKEN")# db
    DATABASE_IDS = os.getenv("DATABASE_IDS")  # db
    PAGE_IDS = os.getenv("PAGE_IDS") # pages
    NOTION_BASE_URL = os.getenv("NOTION_BASE_URL")  # all
    DATABASE_URL = os.getenv("DATABASE_URL")
    PAGE_URL = os.getenv("PAGE_URL")
    BLOCK_URL = os.getenv("BLOCK_URL")
    FILES=os.getenv("FILES")

class ProductionConfig(Config):
    ENV = "production"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = "testing"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    SAS_URL = os.getenv("SAS_URL")



config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
