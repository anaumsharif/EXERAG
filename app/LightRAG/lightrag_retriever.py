import os
import PyPDF2  # Ensure you have this package installed for PDF reading
import docx  # For reading DOCX files
from lightrag import LightRAG,QueryParam
from lightrag.storage import JsonKVStorage, NanoVectorDBStorage, NetworkXStorage
from dotenv import load_dotenv

from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()

OPENAI_API_KEY= config[env_name].OPENAI_API_KEY

# Set essential parameters for LightRAG
working_dir = './dickens'
chunk_token_size = 1200
chunk_overlap_token_size = 100
tiktoken_model_name = 'gpt-4o-mini'
node_embedding_algorithm = 'node2vec'
node2vec_params = {
    'dimensions': 1536,
    'num_walks': 10,
    'walk_length': 40,
    'window_size': 2,
    'iterations': 3,
    'random_seed': 3
}
llm_model_name = 'meta-llama/Llama-3.2-1B-Instruct'

# Initialize mode variable
mode = "naive"  # Set the mode here

# Initialize LightRAG
light_rag = LightRAG(
    working_dir=working_dir,
    chunk_token_size=chunk_token_size,
    chunk_overlap_token_size=chunk_overlap_token_size,
    tiktoken_model_name=tiktoken_model_name,
    node_embedding_algorithm=node_embedding_algorithm,
    node2vec_params=node2vec_params,
    llm_model_name=llm_model_name,
    vector_db_storage_cls=NanoVectorDBStorage,
    graph_storage_cls=NetworkXStorage,
    key_string_value_json_storage_cls=JsonKVStorage
)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ''
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def insert_documents_from_directory(directory):
    """Insert text from various document types into LightRAG."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            light_rag.insert(text)  # Insert extracted text directly
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)
            light_rag.insert(text)  # Insert extracted text directly
        # Add other file types (like images) as needed
        # elif filename.endswith('.jpg') or filename.endswith('.png'):
        #     # Process images if necessary
        #     pass

def query_light_rag(query, mode=mode):
    """Query LightRAG with the specified parameters."""
    query_params = QueryParam(
        mode=mode,
        only_need_context=False,
        response_type="Multiple Paragraphs",
        top_k=60,
        max_token_for_text_unit=4000,
        max_token_for_global_context=4000,
        max_token_for_local_context=4000
    )
    response = light_rag.query(query, param=query_params)  # Use query instead of retrieve
    return response

def qa_chain_with_source(query):
    """Perform a question-answering operation with sources, document ID, and graph ID."""
    # Retrieve relevant documents
    retrieval_response = query_light_rag(query)
    
    # Check if retrieval_response is a string (answer) or a structured response
    if isinstance(retrieval_response, str):
        answer = retrieval_response  # If it's just a string, assign directly
        results = []  # No results to return if it's just an answer
    else:
        # Handle the structured response
        answer = retrieval_response.get('answer', 'No answer found.')  # Get the answer if available
        results = []
        if 'documents' in retrieval_response:
            for doc in retrieval_response['documents']:
                doc_id = doc.get('document_id', None)  # Extract document ID
                graph_id = doc.get('graph_id', None)  # Extract graph ID
                source = doc.get('source', None)  # Extract source
                results.append({
                    'document_id': doc_id,
                    'graph_id': graph_id,
                    'source': source
                })
    
    return {
        'answer': answer,
        'results': results  # Return all results including document and graph IDs
    }

if __name__ == "__main__":
    # Example directory for inserting documents
    dataset_directory = './dataset'  # Specify your dataset directory here
    
    # Insert documents from the dataset directory
    insert_documents_from_directory(dataset_directory)
    
    # Example usage
    query = "What is Casual Decoder?"
    
    # Perform QA with source tracking
    qa_response = qa_chain_with_source(query)
    print("QA Response:", qa_response)
