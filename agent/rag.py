"""
RAG (Retrieval Augmented Generation) module using ChromaDB for semantic search.
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken


class VectorStore:
    """
    Vector database for storing and retrieving insurance policy documents.
    Uses ChromaDB with sentence-transformers for embeddings.
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the ChromaDB database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        # all-MiniLM-L6-v2: Fast, efficient, 384-dim embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="insurance_policies",
            metadata={"description": "Insurance policy documents for semantic search"}
        )
        
        # Initialize tokenizer for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks based on token count.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum tokens per chunk
            overlap: Overlapping tokens between chunks
            
        Returns:
            List of text chunks
        """
        # Tokenize the text
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        # Create overlapping chunks
        start = 0
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move to next chunk with overlap
            start = end - overlap
            
            # Break if we're at the end
            if end >= len(tokens):
                break
        
        return chunks
    
    def add_document(
        self, 
        document_text: str, 
        document_id: str, 
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Add a document to the vector store with chunking.
        
        Args:
            document_text: Full text of the document
            document_id: Unique identifier for the document
            metadata: Additional metadata (e.g., policy_type, filename)
            
        Returns:
            Number of chunks created
        """
        if metadata is None:
            metadata = {}
        
        # Chunk the document
        chunks = self.chunk_text(document_text)
        
        # Generate embeddings for all chunks
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Prepare IDs and metadata for each chunk
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadata = [
            {
                **metadata,
                "document_id": document_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=chunk_ids,
            metadatas=chunk_metadata
        )
        
        return len(chunks)
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for relevant document chunks using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"policy_type": "motor"})
            
        Returns:
            List of dictionaries with keys: text, metadata, distance
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
        
        return formatted_results
    
    def get_document_count(self) -> int:
        """Get total number of chunks in the collection."""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection (use for reset/testing)."""
        self.client.delete_collection("insurance_policies")
    
    def reset(self):
        """Reset the vector store by deleting and recreating the collection."""
        try:
            self.delete_collection()
        except:
            pass
        
        self.collection = self.client.get_or_create_collection(
            name="insurance_policies",
            metadata={"description": "Insurance policy documents for semantic search"}
        )


def retrieve_policy_info(query: str, policy_type: Optional[str] = None, n_results: int = 3) -> str:
    """
    Retrieve relevant policy information using RAG.
    
    Args:
        query: User's question or search query
        policy_type: Optional filter for policy type (motor, home, health)
        n_results: Number of relevant chunks to retrieve
        
    Returns:
        Formatted string with relevant policy information
    """
    # Initialize vector store
    vector_store = VectorStore()
    
    # Check if collection is empty
    if vector_store.get_document_count() == 0:
        return "⚠️ Policy database not initialized. Please run scripts/ingest_policies.py first."
    
    # Prepare filter
    filter_metadata = {"policy_type": policy_type} if policy_type else None
    
    # Search for relevant chunks
    results = vector_store.search(query, n_results=n_results, filter_metadata=filter_metadata)
    
    if not results:
        return "No relevant policy information found."
    
    # Format results
    output = []
    for i, result in enumerate(results, 1):
        doc_id = result['metadata'].get('document_id', 'Unknown')
        policy_type = result['metadata'].get('policy_type', 'Unknown')
        relevance_score = 1 - result['distance']  # Convert distance to similarity
        
        output.append(f"--- Result {i} (Relevance: {relevance_score:.2%}) ---")
        output.append(f"Policy: {doc_id} ({policy_type})")
        output.append(f"\n{result['text']}\n")
    
    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    # Test the vector store
    vector_store = VectorStore()
    
    print(f"Total chunks in database: {vector_store.get_document_count()}")
    
    # Test search
    test_query = "What is covered under zero depreciation?"
    print(f"\nSearching for: '{test_query}'")
    results = retrieve_policy_info(test_query, n_results=2)
    print(results)
