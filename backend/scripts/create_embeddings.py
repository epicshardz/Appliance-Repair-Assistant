import os
import logging
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from tqdm import tqdm

# Load environment variables
load_dotenv()

def create_vector_store(documents):
    # Initialize OpenAI embeddings
    print("Initializing OpenAI embeddings...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    print("Connecting to Qdrant cloud...")
    try:
        # Initialize Qdrant client
        qdrant_host = os.getenv("QDRANT_HOST")
        if not qdrant_host:
            raise ValueError("QDRANT_HOST not found in environment variables")
            
        print(f"Connecting to Qdrant at {qdrant_host}")
        client = QdrantClient(
            url=qdrant_host,
            api_key=os.getenv("QDRANT_API_KEY"),
            prefer_grpc=False,
            timeout=10,  # Adding explicit timeout
            verify=False  # Temporarily disable SSL verification for testing
        )
        
        # Test connection
        client.get_collections()
        print("Successfully connected to Qdrant")

        # Check if collection exists
        if client.collection_exists("ApplianceRepair"):
            print("Collection exists, recreating...")
            client.delete_collection("ApplianceRepair")
        
        # Create collection
        print("Creating collection...")
        client.create_collection(
            collection_name="ApplianceRepair",
            vectors_config={
                "size": 3072,  # text-embedding-3-large dimension
                "distance": "Cosine"
            }
        )
        print("Collection created successfully")

        print(f"Creating vector store with {len(documents)} documents...")
        # Create Qdrant vector store
        vector_store = Qdrant(
            client=client,
            collection_name="ApplianceRepair",
            embeddings=embeddings
        )

        # Add documents in batches
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"Adding batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}...")
            vector_store.add_documents(batch)

        return vector_store

    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")
        print("\nConnection details:")
        print(f"Host: {qdrant_host}")
        print(f"Collection: {os.getenv('QDRANT_COLLECTION', 'ApplianceRepair')}")
        print("\nTroubleshooting steps:")
        print("1. Verify Qdrant host URL in backend/.env")
        print("2. Check if Qdrant cloud service is accessible")
        print("3. Verify API key in backend/.env")
        print("4. Check network connectivity")
        raise

def load_and_split_documents(data_dir: str):
    # Load documents from directory - handle both PDF and text files
    loaders = [
        DirectoryLoader(
            data_dir,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        ),
        DirectoryLoader(
            data_dir,
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True
        )
    ]
    
    documents = []
    
    print("Loading documents...")
    for loader in loaders:
        try:
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded {len(docs)} documents from {loader.glob}")
        except Exception as e:
            print(f"Warning: Error loading some documents: {str(e)}")
            continue
    
    print(f"Loaded {len(documents)} total documents")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    
    print("Splitting documents...")
    splits = text_splitter.split_documents(documents)
    print(f"Created {len(splits)} splits")

    return splits

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Error: OPENAI_API_KEY not found in environment variables")
        logger.error("Please set your OpenAI API key in the backend/.env file")
        return

    try:
        # Load and split documents
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data')
        if not os.path.exists(data_dir):
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Data')
        
        logger.info(f"Loading documents from: {data_dir}")
        
        splits = load_and_split_documents(data_dir)
        logger.info(f"Created {len(splits)} document splits")

        # Create vector store with documents
        logger.info("Creating vector store...")
        vector_store = create_vector_store(splits)
        
        # Verify vectors were created
        try:
            client = QdrantClient(
                url=os.getenv("QDRANT_HOST"),
                api_key=os.getenv("QDRANT_API_KEY"),
                prefer_grpc=False
            )
            collection_info = client.get_collection("ApplianceRepair")
            stats = client.get_collection_stats("ApplianceRepair")
            logger.info(f"Collection info: {collection_info}")
            logger.info(f"Collection stats: {stats}")
            logger.info("Successfully created embeddings and stored in Qdrant")
        except Exception as e:
            logger.error(f"Failed to verify vectors: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error("Make sure you have:")
        logger.error("1. Valid OpenAI API key in backend/.env")
        logger.error("2. Text files in the Data directory")
        logger.error("3. Network connection to Qdrant cloud")

if __name__ == "__main__":
    main()
