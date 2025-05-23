from langchain.chains import ConversationChain
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class RepairAssistant:
    def __init__(self, session_id: str):
        logger.info(f"Initializing RepairAssistant with session ID: {session_id}")
        self.session_id = session_id
        
        try:
            # Initialize OpenAI
            logger.info("Initializing OpenAI LLM...")
            try:
                self.llm = ChatOpenAI(
                    temperature=0.7,
                    model_name="gpt-4-turbo-preview",
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("OpenAI LLM initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI LLM: {str(e)}")
                logger.error(f"OpenAI API Key: {settings.OPENAI_API_KEY[:8]}...")
                raise
            
            # Initialize MongoDB message history
            logger.info("Setting up MongoDB connection...")
            try:
                from pymongo import MongoClient
                # First test the MongoDB connection
                client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
                # Force a connection attempt
                client.admin.command('ping')
                logger.info("MongoDB server connection test successful")
                
                # Initialize the message history
                message_history = MongoDBChatMessageHistory(
                    connection_string=settings.MONGODB_URI,
                    database_name=settings.MONGODB_DB,
                    collection_name="chat_history",
                    session_id=session_id
                )

                # Check for existing messages in the history
                messages = message_history.messages
                if messages:
                    logger.info(f"Found existing session {session_id} with {len(messages)} messages")
                else:
                    logger.info(f"Starting new session {session_id}")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {str(e)}")
                logger.error(f"MongoDB URI: {settings.MONGODB_URI}")
                logger.error(f"Full error details: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise Exception(f"MongoDB Connection Error: {type(e).__name__}: {str(e)}")

            # Setup conversation memory
            self.memory = ConversationBufferMemory(
                chat_memory=message_history,
                return_messages=True
            )

            # Initialize Qdrant client
            logger.info("Setting up Qdrant connection...")
            try:
                logger.info(f"Attempting Qdrant connection to: {settings.QDRANT_HOST}")
                self.qdrant_client = QdrantClient(
                    url=settings.QDRANT_HOST,
                    api_key=settings.QDRANT_API_KEY,
                    prefer_grpc=False,
                    timeout=10,  # Adding explicit timeout
                    verify=False  # Temporarily disable SSL verification for testing
                )
                # Test Qdrant connection and get collection info
                collections = self.qdrant_client.get_collections()
                logger.info(f"Qdrant connection established. Available collections: {collections}")
                
                # Check if our collection exists and get its details
                try:
                    collection_info = self.qdrant_client.get_collection("ApplianceRepair")
                    logger.info(f"ApplianceRepair collection info: {collection_info}")
                    collection_stats = self.qdrant_client.get_collection_stats("ApplianceRepair")
                    logger.info(f"ApplianceRepair collection stats: {collection_stats}")
                    if collection_stats.vectors_count == 0:
                        logger.warning("ApplianceRepair collection exists but contains no vectors!")
                except Exception as e:
                    logger.error(f"Failed to get collection info: {str(e)}")
            except Exception as e:
                logger.error(f"Qdrant connection failed: {str(e)}")
                logger.error(f"Qdrant Host: {settings.QDRANT_HOST}")
                logger.error(f"Error type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
            
            # Setup vector store with OpenAI embeddings
            logger.info("Setting up vector store...")
            try:
                logger.info("Initializing OpenAI embeddings for vector store...")
                embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-large",
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("OpenAI embeddings initialized successfully")
                
                logger.info("Setting up Qdrant vector store with embeddings...")
                self.vector_store = Qdrant(
                    client=self.qdrant_client,
                    collection_name="ApplianceRepair",
                    embeddings=embeddings
                )
                logger.info("Qdrant vector store setup complete with OpenAI embeddings")
            except Exception as e:
                logger.error(f"Vector store setup failed: {str(e)}")
                raise

            # Initialize conversation chain
            logger.info("Initializing conversation chain...")
            self.chain = ConversationChain(
                llm=self.llm,
                memory=self.memory,
                verbose=True
            )
            logger.info("Initialization complete")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to initialize RepairAssistant: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_repair_solution(self, query: str, model_number: str = None):
        logger.info("Starting repair solution generation")
        
        # Search for relevant repair documents
        relevant_docs = []
        logger.info("Searching vector store for repair information")
        # Construct a more natural search query that matches the content style
        search_query = f"how to diagnose and repair {query}"
        if model_number:
            search_query += f" for model {model_number}"
        logger.info(f"Executing Qdrant search with query: {search_query}")
        try:
            logger.info("Attempting Qdrant similarity search...")
            # Try with more results and no score threshold for testing
            search_params = {
                "k": 5  # Reduced number of matches to focus on most relevant
            }
            logger.info(f"Search parameters: {search_params}")
            
            # Try a basic similarity search first
            logger.info(f"Attempting similarity search with query: {search_query}")
            relevant_docs = self.vector_store.similarity_search(
                search_query,
                k=search_params["k"]
            )
            logger.info(f"Search completed. Found {len(relevant_docs)} results")

            if len(relevant_docs) == 0:
                logger.warning("No relevant documents found in the vector store")
            
            # Log raw results with scores
            logger.info("\n=== SIMILARITY SEARCH RESULTS WITH SCORES ===")
            for i, doc in enumerate(relevant_docs):
                logger.info(f"\nResult {i+1}:")
                logger.info(f"Content preview: {doc.page_content[:200]}...")
                logger.info("-" * 50)
            
            logger.info("Qdrant similarity search completed successfully")
        except Exception as e:
            logger.error(f"Qdrant search failed: {str(e)}")
            logger.error(f"Query: {search_query}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            relevant_docs = []
            
        logger.info(f"Found {len(relevant_docs)} relevant documents")
        for i, doc in enumerate(relevant_docs):
            logger.info(f"Document {i+1} summary:")
            logger.info(f"Content (first 200 chars): {doc.page_content[:200]}...")
            logger.info(f"Source: {doc.metadata.get('source', 'N/A')}")
            if hasattr(doc, 'score'):
                logger.info(f"Similarity score: {doc.score}")

        # Construct prompt with context
        # Log the raw documents before context building
        logger.info("\n=== RAW QDRANT SEARCH RESULTS ===")
        for i, doc in enumerate(relevant_docs):
            logger.info(f"\nDocument {i+1} Full Content:")
            logger.info("-" * 50)
            logger.info(f"Full content: {doc.page_content}")
            logger.info(f"Metadata: {doc.metadata}")
            logger.info("-" * 50)

        # Build and log the context
        context = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
        logger.info("\n=== CONSTRUCTED CONTEXT ===")
        logger.info(f"Context length: {len(context)} characters")
        logger.info(f"Context content:\n{context}")
        logger.info("=" * 50)
        
        # Log the full prompt
        # Construct and log the full prompt
        prompt = f"""You are an expert appliance repair technician. 
        User Query: {query}
        {"Model Number: " + model_number if model_number else ""}
        
        Relevant repair information:
        {context if context else "No specific repair information found for this model."}
        
        Please provide step-by-step repair instructions, safety precautions, and any required parts.
        """
        
        # Log the complete prompt
        logger.info("\n=== FINAL PROMPT TO LLM ===")
        logger.info(prompt)
        logger.info("=" * 50)
        
        # Get response from LLM
        logger.info("Sending prompt to LLM...")
        response = await self.chain.apredict(input=prompt)
        logger.info("Received response from LLM")
        return response

    async def find_replacement_parts(self, model_number: str):
        """Search for replacement parts and return Amazon affiliate links"""
        # TODO: Implement Amazon Product API integration
        pass
