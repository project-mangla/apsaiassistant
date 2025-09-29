import json
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class DataManager:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.qa_file = os.path.join(data_dir, 'qa_data.json')
        self.admin_file = os.path.join(data_dir, 'admin_credentials.json')
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000,
            lowercase=True
        )
        
        # Load and prepare data for similarity search
        self._prepare_search_data()
    
    def _initialize_files(self):
        """Initialize data files with default content if they don't exist"""
        # Initialize Q&A data file
        if not os.path.exists(self.qa_file):
            default_qa_data = {
                "qa_pairs": [
                    {
                        "id": 1,
                        "question": "Who is the principal of APS Mangla?",
                        "answer": "Talat Wazir is the principal of APS Mangla"
                    },
                    {
                        "id": 2,
                        "question": "What subjects are taught in ICS?",
                        "answer": "ICS subjects include Physics, Maths, Computer, English, Urdu and Islamiyat for 1st year. For 2nd year, Pak Studies replaces Islamiyat"
                    }
                ],
                "embeddings": []
            }
            self._save_qa_data(default_qa_data)
        
        # Initialize admin credentials file
        if not os.path.exists(self.admin_file):
            default_admin = {
                "username": "admin",
                "password_hash": generate_password_hash("admin")
            }
            self._save_admin_credentials(default_admin)
    
    def _save_qa_data(self, data: Dict[str, Any]):
        """Save Q&A data to file"""
        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving Q&A data: {str(e)}")
    
    def _save_admin_credentials(self, data: Dict[str, Any]):
        """Save admin credentials to file"""
        try:
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving admin credentials: {str(e)}")
    
    def _load_qa_data(self) -> Dict[str, Any]:
        """Load Q&A data from file"""
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading Q&A data: {str(e)}")
            return {"qa_pairs": [], "embeddings": []}
    
    def _load_admin_credentials(self) -> Dict[str, Any]:
        """Load admin credentials from file"""
        try:
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading admin credentials: {str(e)}")
            return {}
    
    def _prepare_search_data(self):
        """Prepare data for similarity search"""
        qa_data = self._load_qa_data()
        qa_pairs = qa_data.get('qa_pairs', [])
        
        if not qa_pairs:
            self.questions = []
            self.answers = []
            self.qa_pairs = []
            self.question_vectors = None
            self.answer_vectors = None
            return
        
        # Extract questions and answers
        self.questions = [pair['question'] for pair in qa_pairs]
        self.answers = [pair['answer'] for pair in qa_pairs]
        self.qa_pairs = qa_pairs
        
        # Create combined text for better matching (questions + answers)
        combined_texts = [f"{pair['question']} {pair['answer']}" for pair in qa_pairs]
        
        try:
            # Fit vectorizer on combined texts and transform questions and answers separately
            self.vectorizer.fit(combined_texts)
            self.question_vectors = self.vectorizer.transform(self.questions)
            self.answer_vectors = self.vectorizer.transform(self.answers)
            logging.debug(f"Prepared search data for {len(qa_pairs)} Q&A pairs")
        except Exception as e:
            logging.error(f"Error preparing search data: {str(e)}")
            self.question_vectors = None
            self.answer_vectors = None
    
    def search_qa(self, query: str, min_confidence: float = 0.1) -> Tuple[Optional[str], float, str]:
        """
        Enhanced search that looks in both questions and answers
        Returns: (answer, confidence, search_type)
        search_type can be 'question_match', 'reverse_lookup', or 'no_match'
        """
        if not self.qa_pairs or self.question_vectors is None:
            return None, 0.0, 'no_match'
        
        try:
            # Transform query
            query_vector = self.vectorizer.transform([query.lower()])
            
            # Search in questions (normal Q&A)
            question_similarities = cosine_similarity(query_vector, self.question_vectors)[0]
            max_q_idx = np.argmax(question_similarities)
            max_q_similarity = question_similarities[max_q_idx]
            
            # Search in answers (reverse lookup)
            answer_similarities = cosine_similarity(query_vector, self.answer_vectors)[0]
            max_a_idx = np.argmax(answer_similarities)
            max_a_similarity = answer_similarities[max_a_idx]
            
            # Determine best match
            if max_q_similarity >= max_a_similarity and max_q_similarity >= min_confidence:
                # Normal question match
                return (
                    self.qa_pairs[max_q_idx]['answer'],
                    max_q_similarity,
                    'question_match'
                )
            elif max_a_similarity >= min_confidence:
                # Reverse lookup - found entity/person in answer, return the question context
                answer_text = self.qa_pairs[max_a_idx]['answer']
                question_text = self.qa_pairs[max_a_idx]['question']
                
                # Create contextual response for reverse lookup
                # Example: "Who is Talat Wazir?" -> "Talat Wazir is the principal of APS Mangla"
                return (
                    answer_text,
                    max_a_similarity,
                    'reverse_lookup'
                )
            
            return None, max(max_q_similarity, max_a_similarity), 'no_match'
            
        except Exception as e:
            logging.error(f"Error in search_qa: {str(e)}")
            return None, 0.0, 'no_match'
    
    def get_contextual_search_results(self, query: str) -> Dict[str, Any]:
        """
        Get detailed search results with context for intelligent response generation
        """
        answer, confidence, search_type = self.search_qa(query)
        
        # Analyze query for better context
        query_lower = query.lower().strip()
        
        # Detect question type
        question_words = ['what', 'who', 'when', 'where', 'why', 'how', 'which']
        is_question = any(word in query_lower for word in question_words) or query.endswith('?')
        
        # Detect greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|salam|assalam|assalamualaikum)\b',
            r'\b(good\s+(morning|afternoon|evening))\b',
        ]
        is_greeting = any(re.search(pattern, query_lower) for pattern in greeting_patterns)
        
        # Detect farewell patterns
        farewell_patterns = [
            r'\b(bye|goodbye|see\s+you|thanks|thank\s+you|khuda\s+hafiz)\b',
        ]
        is_farewell = any(re.search(pattern, query_lower) for pattern in farewell_patterns)
        
        # Detect small talk patterns
        small_talk_patterns = [
            r'\b(how\s+are\s+you|what\'s\s+up|how\s+is\s+it\s+going)\b',
            r'\b(what\s+can\s+you\s+do|what\s+do\s+you\s+know)\b',
        ]
        is_small_talk = any(re.search(pattern, query_lower) for pattern in small_talk_patterns)
        
        return {
            'answer': answer,
            'confidence': confidence,
            'search_type': search_type,
            'query_analysis': {
                'is_question': is_question,
                'is_greeting': is_greeting,
                'is_farewell': is_farewell,
                'is_small_talk': is_small_talk,
                'original_query': query,
                'processed_query': query_lower
            }
        }
    
    def add_qa_pair(self, question: str, answer: str) -> bool:
        """Add new Q&A pair"""
        try:
            qa_data = self._load_qa_data()
            qa_pairs = qa_data.get('qa_pairs', [])
            
            # Generate new ID
            new_id = max([pair.get('id', 0) for pair in qa_pairs], default=0) + 1
            
            # Add new pair
            qa_pairs.append({
                'id': new_id,
                'question': question,
                'answer': answer
            })
            
            qa_data['qa_pairs'] = qa_pairs
            self._save_qa_data(qa_data)
            
            # Refresh search data
            self._prepare_search_data()
            
            logging.info(f"Added new Q&A pair with ID {new_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding Q&A pair: {str(e)}")
            return False
    
    def update_qa_pair(self, qa_id: int, question: str, answer: str) -> bool:
        """Update existing Q&A pair"""
        try:
            qa_data = self._load_qa_data()
            qa_pairs = qa_data.get('qa_pairs', [])
            
            # Find and update the pair
            for pair in qa_pairs:
                if pair.get('id') == qa_id:
                    pair['question'] = question
                    pair['answer'] = answer
                    
                    qa_data['qa_pairs'] = qa_pairs
                    self._save_qa_data(qa_data)
                    
                    # Refresh search data
                    self._prepare_search_data()
                    
                    logging.info(f"Updated Q&A pair with ID {qa_id}")
                    return True
            
            logging.warning(f"Q&A pair with ID {qa_id} not found")
            return False
            
        except Exception as e:
            logging.error(f"Error updating Q&A pair: {str(e)}")
            return False
    
    def delete_qa_pair(self, qa_id: int) -> bool:
        """Delete Q&A pair"""
        try:
            qa_data = self._load_qa_data()
            qa_pairs = qa_data.get('qa_pairs', [])
            
            # Filter out the pair to delete
            original_count = len(qa_pairs)
            qa_pairs = [pair for pair in qa_pairs if pair.get('id') != qa_id]
            
            if len(qa_pairs) < original_count:
                qa_data['qa_pairs'] = qa_pairs
                self._save_qa_data(qa_data)
                
                # Refresh search data
                self._prepare_search_data()
                
                logging.info(f"Deleted Q&A pair with ID {qa_id}")
                return True
            
            logging.warning(f"Q&A pair with ID {qa_id} not found")
            return False
            
        except Exception as e:
            logging.error(f"Error deleting Q&A pair: {str(e)}")
            return False
    
    def get_all_qa_pairs(self) -> List[Dict[str, Any]]:
        """Get all Q&A pairs"""
        qa_data = self._load_qa_data()
        return qa_data.get('qa_pairs', [])
    
    def verify_admin_credentials(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        try:
            admin_data = self._load_admin_credentials()
            stored_username = admin_data.get('username')
            stored_hash = admin_data.get('password_hash')
            
            if not stored_username or not stored_hash:
                return False
            
            return username == stored_username and check_password_hash(stored_hash, password)
            
        except Exception as e:
            logging.error(f"Error verifying credentials: {str(e)}")
            return False
