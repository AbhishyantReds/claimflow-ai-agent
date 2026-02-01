"""
Tests for RAG system (Vector store, embeddings, semantic search)
"""
import pytest
from agent.rag import VectorStore, retrieve_policy_info


class TestVectorStore:
    """Test VectorStore class"""
    
    def test_initialization(self, tmp_path):
        """Test vector store initialization"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        assert vector_store is not None
        assert vector_store.collection is not None
    
    def test_add_document(self, tmp_path):
        """Test adding a document to vector store"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        doc_text = "Motor insurance provides coverage for vehicles."
        num_chunks = vector_store.add_document(
            document_text=doc_text,
            document_id="test_doc",
            metadata={"policy_type": "motor"}
        )
        
        assert num_chunks > 0
        assert vector_store.get_document_count() == num_chunks
    
    def test_chunking(self, tmp_path):
        """Test text chunking functionality"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        # Short text should create 1 chunk
        short_text = "This is a short text."
        chunks = vector_store.chunk_text(short_text, chunk_size=50)
        assert len(chunks) >= 1
        
        # Long text should create multiple chunks
        long_text = " ".join(["This is a sentence."] * 200)
        chunks = vector_store.chunk_text(long_text, chunk_size=100, overlap=20)
        assert len(chunks) > 1
    
    def test_search(self, tmp_path):
        """Test semantic search"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        # Add documents
        vector_store.add_document(
            "Motor insurance covers vehicle damage and third-party liability.",
            "motor_doc",
            {"policy_type": "motor", "policy_name": "Motor Policy"}
        )
        
        vector_store.add_document(
            "Health insurance covers hospitalization and medical expenses.",
            "health_doc",
            {"policy_type": "health", "policy_name": "Health Policy"}
        )
        
        # Search for motor insurance
        results = vector_store.search("vehicle damage", n_results=2)
        
        assert len(results) > 0
        assert results[0]['metadata']['policy_type'] == 'motor'
        assert 'text' in results[0]
        assert 'distance' in results[0]
    
    def test_search_with_filter(self, tmp_path):
        """Test semantic search with metadata filter"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        # Add documents of different types
        vector_store.add_document(
            "Motor insurance for cars and bikes.",
            "motor_doc",
            {"policy_type": "motor"}
        )
        
        vector_store.add_document(
            "Home insurance for property damage.",
            "home_doc",
            {"policy_type": "home"}
        )
        
        # Search only motor policies
        results = vector_store.search(
            "insurance coverage",
            n_results=5,
            filter_metadata={"policy_type": "motor"}
        )
        
        assert len(results) > 0
        for result in results:
            assert result['metadata']['policy_type'] == 'motor'
    
    def test_empty_search(self, tmp_path):
        """Test search on empty collection"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        results = vector_store.search("test query", n_results=5)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_reset(self, tmp_path):
        """Test resetting the vector store"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        # Add document
        vector_store.add_document("Test document", "test", {})
        assert vector_store.get_document_count() > 0
        
        # Reset
        vector_store.reset()
        assert vector_store.get_document_count() == 0


class TestRetrievePolicyInfo:
    """Test retrieve_policy_info helper function"""
    
    def test_empty_database(self, tmp_path):
        """Test with empty vector database"""
        # Temporarily modify the default path
        import agent.rag as rag_module
        original_init = rag_module.VectorStore.__init__
        
        def mock_init(self, persist_directory=str(tmp_path / "empty_chroma")):
            original_init(self, persist_directory)
        
        rag_module.VectorStore.__init__ = mock_init
        
        result = retrieve_policy_info("What is covered?", n_results=2)
        
        # Should return warning message
        assert "not initialized" in result.lower() or "no relevant" in result.lower()
        
        # Restore original
        rag_module.VectorStore.__init__ = original_init
    
    def test_with_data(self, tmp_path):
        """Test retrieval with populated database"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        # Add sample policy document
        vector_store.add_document(
            "Zero depreciation cover ensures full claim amount without depreciation.",
            "zero_dep_policy",
            {"policy_type": "motor", "policy_name": "Zero Depreciation"}
        )
        
        # Modify the default init temporarily
        import agent.rag as rag_module
        original_init = rag_module.VectorStore.__init__
        
        def mock_init(self, persist_directory=str(tmp_path / "test_chroma")):
            original_init(self, persist_directory)
        
        rag_module.VectorStore.__init__ = mock_init
        
        result = retrieve_policy_info("zero depreciation", policy_type="motor", n_results=1)
        
        assert "Zero depreciation" in result or "zero depreciation" in result.lower()
        
        # Restore
        rag_module.VectorStore.__init__ = original_init


class TestEmbeddingModel:
    """Test embedding model functionality"""
    
    def test_embedding_generation(self, tmp_path):
        """Test that embeddings are generated correctly"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        # Generate embeddings
        texts = ["Test sentence one", "Test sentence two"]
        embeddings = vector_store.embedding_model.encode(texts)
        
        assert embeddings.shape[0] == 2  # Two embeddings
        assert embeddings.shape[1] == 384  # 384 dimensions for all-MiniLM-L6-v2
    
    def test_embedding_similarity(self, tmp_path):
        """Test that similar texts have similar embeddings"""
        vector_store = VectorStore(persist_directory=str(tmp_path / "test_chroma"))
        
        text1 = "Vehicle insurance coverage"
        text2 = "Car insurance protection"
        text3 = "Health medical treatment"
        
        emb1 = vector_store.embedding_model.encode([text1])[0]
        emb2 = vector_store.embedding_model.encode([text2])[0]
        emb3 = vector_store.embedding_model.encode([text3])[0]
        
        # Calculate cosine similarity
        import numpy as np
        
        sim_1_2 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        sim_1_3 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # Similar texts should have higher similarity
        assert sim_1_2 > sim_1_3
