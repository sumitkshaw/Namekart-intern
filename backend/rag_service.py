# # rag_service.py
# import json
# import sqlite3
# from typing import List, Dict, Any
# from sentence_transformers import SentenceTransformer
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# import re
# from datetime import datetime

# class SimpleRAG:
#     def __init__(self, db_path: str = "./notes.db"):
#         """Initialize RAG pipeline with local sentence transformer"""
#         self.db_path = db_path
        
#         # Use a small, efficient sentence transformer model (no API key needed)
#         # This model works offline and is free
#         self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        
#         # Simple in-memory vector store
#         self.vector_store = {
#             'embeddings': [],
#             'documents': [],
#             'metadata': []
#         }
        
#         # Initialize and load existing notes
#         self.load_notes_to_vector_store()
    
#     def chunk_text(self, text: str, chunk_size: int = 200) -> List[str]:
#         """Simple text chunking by sentence and character limit"""
#         # Split by sentences first
#         sentences = re.split(r'[.!?]+', text)
#         chunks = []
#         current_chunk = ""
        
#         for sentence in sentences:
#             sentence = sentence.strip()
#             if not sentence:
#                 continue
                
#             # If adding this sentence exceeds chunk size, start new chunk
#             if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = sentence
#             else:
#                 current_chunk += " " + sentence if current_chunk else sentence
        
#         # Add remaining chunk
#         if current_chunk.strip():
#             chunks.append(current_chunk.strip())
        
#         # If no chunks created (very short text), return original text
#         return chunks if chunks else [text]
    
#     def create_embeddings(self, texts: List[str]) -> np.ndarray:
#         """Generate embeddings using sentence transformers"""
#         return self.embeddings_model.encode(texts)
    
#     def load_notes_to_vector_store(self):
#         """Load all notes from database into vector store"""
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
            
#             cursor.execute("""
#                 SELECT id, content, created_at, updated_at, version 
#                 FROM notes 
#                 ORDER BY created_at DESC
#             """)
            
#             notes = cursor.fetchall()
#             conn.close()
            
#             # Clear existing vector store
#             self.vector_store = {
#                 'embeddings': [],
#                 'documents': [],
#                 'metadata': []
#             }
            
#             all_chunks = []
#             all_metadata = []
            
#             for note_id, content, created_at, updated_at, version in notes:
#                 # Chunk the note content
#                 chunks = self.chunk_text(content)
                
#                 for i, chunk in enumerate(chunks):
#                     all_chunks.append(chunk)
#                     all_metadata.append({
#                         'note_id': note_id,
#                         'chunk_index': i,
#                         'created_at': created_at,
#                         'updated_at': updated_at,
#                         'version': version,
#                         'full_content': content[:100] + "..." if len(content) > 100 else content
#                     })
            
#             if all_chunks:
#                 # Generate embeddings for all chunks
#                 embeddings = self.create_embeddings(all_chunks)
                
#                 self.vector_store['embeddings'] = embeddings
#                 self.vector_store['documents'] = all_chunks
#                 self.vector_store['metadata'] = all_metadata
            
#             print(f"✅ Loaded {len(all_chunks)} chunks from {len(notes)} notes into vector store")
            
#         except Exception as e:
#             print(f"❌ Error loading notes: {e}")
    
#     def add_note_to_vector_store(self, note_id: int, content: str, created_at: str, updated_at: str, version: int):
#         """Add a new note to the vector store"""
#         chunks = self.chunk_text(content)
        
#         for i, chunk in enumerate(chunks):
#             # Create embedding for this chunk
#             embedding = self.create_embeddings([chunk])[0]
            
#             # Add to vector store
#             if len(self.vector_store['embeddings']) == 0:
#                 self.vector_store['embeddings'] = embedding.reshape(1, -1)
#             else:
#                 self.vector_store['embeddings'] = np.vstack([
#                     self.vector_store['embeddings'], 
#                     embedding.reshape(1, -1)
#                 ])
            
#             self.vector_store['documents'].append(chunk)
#             self.vector_store['metadata'].append({
#                 'note_id': note_id,
#                 'chunk_index': i,
#                 'created_at': created_at,
#                 'updated_at': updated_at,
#                 'version': version,
#                 'full_content': content[:100] + "..." if len(content) > 100 else content
#             })
    
#     def retrieve_similar_notes(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
#         """Retrieve similar notes based on query"""
#         if len(self.vector_store['documents']) == 0:
#             return []
        
#         # Create embedding for query
#         query_embedding = self.create_embeddings([query])
        
#         # Calculate cosine similarity
#         similarities = cosine_similarity(
#             query_embedding, 
#             self.vector_store['embeddings']
#         )[0]
        
#         # Get top-k most similar chunks
#         top_indices = np.argsort(similarities)[::-1][:top_k]
        
#         results = []
#         for idx in top_indices:
#             results.append({
#                 'content': self.vector_store['documents'][idx],
#                 'similarity_score': float(similarities[idx]),
#                 'metadata': self.vector_store['metadata'][idx]
#             })
        
#         return results
    
#     def generate_response(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """Simple response generation based on retrieved documents"""
#         if not retrieved_docs:
#             return {
#                 'response': "No relevant notes found for your query.",
#                 'sources': [],
#                 'context_used': []
#             }
        
#         # Simple prompt template
#         context_chunks = []
#         sources = []
        
#         for doc in retrieved_docs:
#             context_chunks.append(f"- {doc['content']}")
#             sources.append({
#                 'note_id': doc['metadata']['note_id'],
#                 'similarity': doc['similarity_score'],
#                 'preview': doc['metadata']['full_content']
#             })
        
#         context = "\n".join(context_chunks)
        
#         # Simple rule-based response generation (no LLM needed)
#         response = self._generate_simple_response(query, context, retrieved_docs)
        
#         return {
#             'response': response,
#             'sources': sources,
#             'context_used': context_chunks,
#             'query': query,
#             'timestamp': datetime.now().isoformat()
#         }
    
#     def _generate_simple_response(self, query: str, context: str, docs: List[Dict]) -> str:
#         """Simple rule-based response generation"""
#         query_lower = query.lower()
        
#         # Count relevant documents
#         num_results = len(docs)
#         avg_similarity = sum(doc['similarity_score'] for doc in docs) / len(docs)
        
#         if avg_similarity > 0.7:
#             confidence = "high"
#         elif avg_similarity > 0.5:
#             confidence = "moderate"
#         else:
#             confidence = "low"
        
#         # Generate response based on patterns
#         if any(word in query_lower for word in ['find', 'search', 'look', 'show']):
#             response = f"I found {num_results} relevant notes with {confidence} confidence matching your search."
#         elif any(word in query_lower for word in ['what', 'how', 'why', 'when']):
#             response = f"Based on your notes, here's what I found: {num_results} related entries with {confidence} relevance."
#         else:
#             response = f"Here are {num_results} notes related to your query (confidence: {confidence})."
        
#         # Add top result preview
#         if docs and docs[0]['similarity_score'] > 0.3:
#             top_content = docs[0]['content'][:150]
#             response += f"\n\nMost relevant excerpt: \"{top_content}...\""
        
#         return response
    
#     def search_notes(self, query: str, top_k: int = 3) -> Dict[str, Any]:
#         """Main RAG pipeline function"""
#         try:
#             # Step 1: Retrieve similar documents
#             retrieved_docs = self.retrieve_similar_notes(query, top_k)
            
#             # Step 2: Generate response
#             response = self.generate_response(query, retrieved_docs)
            
#             return {
#                 'success': True,
#                 'data': response
#             }
            
#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'data': None
#             }
    
#     def evaluate_retrieval(self, query: str, expected_note_ids: List[int], top_k: int = 3) -> Dict[str, float]:
#         """Simple evaluation metric for retrieval quality"""
#         results = self.retrieve_similar_notes(query, top_k)
        
#         retrieved_note_ids = [doc['metadata']['note_id'] for doc in results]
        
#         # Precision: How many retrieved docs are relevant?
#         relevant_retrieved = len(set(retrieved_note_ids) & set(expected_note_ids))
#         precision = relevant_retrieved / len(retrieved_note_ids) if retrieved_note_ids else 0
        
#         # Recall: How many relevant docs were retrieved?
#         recall = relevant_retrieved / len(expected_note_ids) if expected_note_ids else 0
        
#         # F1 Score
#         f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
#         return {
#             'precision': precision,
#             'recall': recall,
#             'f1_score': f1,
#             'retrieved_count': len(retrieved_note_ids),
#             'expected_count': len(expected_note_ids)
#         }

# # Example usage and testing
# if __name__ == "__main__":
#     # Initialize RAG pipeline
#     rag = SimpleRAG()
    
#     # Test search
#     test_query = "meeting notes"
#     result = rag.search_notes(test_query)
    
#     print(f"Query: {test_query}")
#     print(f"Result: {json.dumps(result, indent=2)}")