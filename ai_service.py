import os
import logging
import json
import re
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "default_key")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"
        
        # Response templates for different scenarios
        self.templates = {
            'greeting': [
                "Hello! 👋 I'm your APS Mangla assistant. How can I help you with information about the school today?",
                "Hi there! 🏫 I'm here to help you with questions about APS Mangla. What would you like to know?",
                "Assalamualaikum! Welcome to APS Mangla's virtual assistant. I'm ready to help with your questions!",
            ],
            'farewell': [
                "Goodbye! Feel free to come back anytime if you have more questions about APS Mangla. 👋",
                "Thank you for using APS Mangla's assistant! Have a great day! 🌟",
                "Khuda hafiz! I'm always here if you need more help with school information. 📚",
            ],
            'small_talk': {
                'how_are_you': "I'm doing great, thank you for asking! I'm here and ready to help you with information about APS Mangla. What would you like to know? 😊",
                'what_can_you_do': "I can help you with information about APS Mangla! I know about our principal, subjects like ICS, school policies, schedules, and much more. Just ask me anything about the school! 🎓",
                'capabilities': "I'm specialized in providing information about APS Mangla. I can answer questions about staff, curriculum, facilities, admission procedures, and general school information. How can I assist you today? 📖"
            },
            'low_confidence': [
                "I'm not completely sure about that. Could you try asking your question in a different way? I'm specifically designed to help with APS Mangla information.",
                "That's a bit outside my current knowledge about APS Mangla. Could you rephrase your question or ask about something else related to the school?",
                "I'd like to help, but I'm not confident about that particular information. Is there something else about APS Mangla I can assist with?"
            ],
            'no_match': [
                "I don't have information about that specific topic yet. I'm focused on APS Mangla school information. You could ask about our principal, subjects, facilities, or other school-related matters.",
                "That's not something I know about yet. I specialize in APS Mangla information - try asking about teachers, classes, schedules, or school policies!",
                "I'm still learning! I don't have details about that, but I can help with APS Mangla school information. What else would you like to know about the school?"
            ]
        }
    
    def get_intelligent_response(self, user_input: str, data_manager, conversation_memory: Optional[list] = None) -> Dict[str, Any]:
        """
        Generate intelligent responses using enhanced logic and AI rephrasing
        """
        try:
            # Initialize conversation memory if not provided
            if conversation_memory is None:
                conversation_memory = []
            
            # Check for follow-up questions first
            if self._is_follow_up_question(user_input) and conversation_memory:
                return self._handle_follow_up_question(user_input, conversation_memory, data_manager)
            
            # Get contextual search results
            search_results = data_manager.get_contextual_search_results(user_input)
            query_analysis = search_results['query_analysis']
            
            # Handle greetings first
            if query_analysis['is_greeting']:
                return self._handle_greeting(user_input)
            
            # Handle farewells
            if query_analysis['is_farewell']:
                return self._handle_farewell(user_input)
            
            # Handle small talk
            if query_analysis['is_small_talk']:
                return self._handle_small_talk(user_input)
            
            # Handle Q&A with different confidence levels
            answer = search_results['answer']
            confidence = search_results['confidence']
            search_type = search_results['search_type']
            
            if answer and confidence >= 0.4:
                # High confidence - enhance with AI and provide complete information
                return self._enhance_response_with_ai(
                    user_input, answer, confidence, search_type, complete_answer=True
                )
            elif answer and confidence >= 0.2:
                # Medium confidence - use template enhancement
                return self._handle_medium_confidence(
                    user_input, answer, confidence, search_type
                )
            else:
                # Low/no confidence - contextual fallback
                return self._handle_no_match(user_input, query_analysis)
        
        except Exception as e:
            logging.error(f"Error in get_intelligent_response: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error. Please try asking your question again.",
                'confidence': '0.00'
            }
    
    def _handle_greeting(self, user_input: str) -> Dict[str, Any]:
        """Handle greeting messages"""
        import random
        response = random.choice(self.templates['greeting'])
        return {
            'response': response,
            'confidence': '1.00'
        }
    
    def _handle_farewell(self, user_input: str) -> Dict[str, Any]:
        """Handle farewell messages"""
        import random
        response = random.choice(self.templates['farewell'])
        return {
            'response': response,
            'confidence': '1.00'
        }
    
    def _handle_small_talk(self, user_input: str) -> Dict[str, Any]:
        """Handle small talk"""
        user_lower = user_input.lower()
        
        if 'how are you' in user_lower or 'how is it going' in user_lower:
            response = self.templates['small_talk']['how_are_you']
        elif 'what can you do' in user_lower or 'what do you know' in user_lower:
            response = self.templates['small_talk']['what_can_you_do']
        else:
            response = self.templates['small_talk']['capabilities']
        
        return {
            'response': response,
            'confidence': '1.00'
        }
    
    def _enhance_response_with_ai(self, user_input: str, answer: str, confidence: float, search_type: str, complete_answer: bool = False) -> Dict[str, Any]:
        """Use AI to enhance responses for high confidence matches"""
        try:
            # Create enhanced prompt based on search type
            if search_type == 'reverse_lookup':
                system_prompt = """You are a helpful assistant for APS Mangla school. 
A student asked about a person or entity, and we found information about them in our database.
Provide a natural, conversational response using ONLY the provided fact.
Make it sound friendly and informative, as if you're a knowledgeable school representative."""
                
                user_prompt = f"""Student asked: "{user_input}"
Fact from database: "{answer}"

Please provide a natural, conversational response using only this information."""
            else:
                system_prompt = """You are a helpful assistant for APS Mangla school.
A student asked a question and we found a relevant answer in our database.
Convert the factual answer into a natural, conversational response.
Keep it friendly, informative, and student-appropriate.
IMPORTANT: Provide a COMPLETE answer with all relevant details from the database.
If the answer mentions subjects, list ALL of them. If it mentions requirements, include ALL requirements.
Use ONLY the provided information - don't add external facts."""
                
                user_prompt = f"""Student question: "{user_input}"
Database answer: "{answer}"

Please rephrase this into a complete, natural, conversational response for the student. Include ALL details mentioned in the database answer."""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=300
                )
            )
            
            if response.text:
                enhanced_response = response.text.strip()
                # Clean up any unwanted formatting
                enhanced_response = re.sub(r'\*\*', '', enhanced_response)
                enhanced_response = re.sub(r'\*', '', enhanced_response)
                
                return {
                    'response': enhanced_response,
                    'confidence': f"{confidence:.2f}"
                }
        
        except Exception as e:
            logging.error(f"Error enhancing response with AI: {str(e)}")
        
        # Fallback to template-based response
        return self._handle_medium_confidence(user_input, answer, confidence, search_type)
    
    def _handle_medium_confidence(self, user_input: str, answer: str, confidence: float, search_type: str) -> Dict[str, Any]:
        """Handle medium confidence responses with templates"""
        if search_type == 'reverse_lookup':
            response = f"Based on what I know about APS Mangla, {answer.lower()}"
        else:
            response = f"According to my information about APS Mangla, {answer.lower()}"
        
        return {
            'response': response,
            'confidence': f"{confidence:.2f}"
        }
    
    def _handle_no_match(self, user_input: str, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cases where no good match is found"""
        import random
        
        # Choose appropriate fallback based on query type
        if query_analysis['is_question']:
            # It's a question, but we don't have the answer
            fallback_responses = [
                "I don't have specific information about that question yet. I focus on APS Mangla school details like our principal, subjects, facilities, and policies. Is there something else about the school I can help with?",
                "That's not in my current knowledge base about APS Mangla. I can help with information about teachers, curriculum, school facilities, and general school information. What else would you like to know?",
                "I'm still building my knowledge about APS Mangla! I don't have details about that particular topic, but I can assist with questions about staff, subjects like ICS, school procedures, and more. How else can I help?"
            ]
        else:
            # General no match
            fallback_responses = self.templates['no_match']
        
        response = random.choice(fallback_responses)
        
        return {
            'response': response,
            'confidence': '0.00'
        }
    
    def enhance_simple_response(self, question: str, answer: str) -> str:
        """
        Legacy method for simple response enhancement
        Kept for backwards compatibility
        """
        try:
            prompt = f"""You are a chatbot for APS Mangla school. 
Convert this factual answer into a natural, conversational response for a student.

Student question: {question}
Factual answer: {answer}

Make it friendly and natural, but use only the provided information."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=150
                )
            )
            
            if response.text:
                return response.text.strip()
        
        except Exception as e:
            logging.error(f"Error in enhance_simple_response: {str(e)}")
        
        # Fallback to original answer
        return answer
    
    def _is_follow_up_question(self, user_input: str) -> bool:
        """Check if the user input is a follow-up question"""
        user_lower = user_input.lower().strip()
        
        # Common follow-up patterns
        follow_up_patterns = [
            'and?', 'and what else?', 'what else?', 'more', 'tell me more', 
            'anything else?', 'what about the rest?', 'continue', 'go on',
            'what more?', 'others?', 'rest?', 'more info', 'more information'
        ]
        
        return user_lower in follow_up_patterns or user_lower.endswith('?') and len(user_lower.split()) <= 3
    
    def _handle_follow_up_question(self, user_input: str, conversation_memory: list, data_manager) -> Dict[str, Any]:
        """Handle follow-up questions based on conversation context"""
        try:
            if not conversation_memory:
                return {
                    'response': "I'm not sure what you're referring to. Could you please ask your question more specifically?",
                    'confidence': '0.00'
                }
            
            # Get the last conversation entry
            last_entry = conversation_memory[-1]
            last_question = last_entry.get('user_message', '')
            last_answer = last_entry.get('bot_response', '')
            last_confidence = float(last_entry.get('confidence', '0.00'))
            
            # If the last answer had good confidence, try to expand on it
            if last_confidence >= 0.4:
                # Use AI to expand on the previous answer
                return self._expand_previous_answer(user_input, last_question, last_answer, data_manager)
            else:
                # Previous answer had low confidence, acknowledge and redirect
                return {
                    'response': "I wasn't very confident about my previous answer. Could you ask a more specific question about APS Mangla? I can help with information about our principal, subjects, facilities, and policies.",
                    'confidence': '0.00'
                }
                
        except Exception as e:
            logging.error(f"Error handling follow-up question: {str(e)}")
            return {
                'response': "Could you please ask your question more specifically? I'm here to help with APS Mangla information.",
                'confidence': '0.00'
            }
    
    def _expand_previous_answer(self, user_input: str, last_question: str, last_answer: str, data_manager) -> Dict[str, Any]:
        """Expand on the previous answer using AI or additional search"""
        try:
            # Try to find more complete information about the previous topic
            search_results = data_manager.get_contextual_search_results(last_question)
            
            # Use AI to provide a more complete answer
            system_prompt = """You are an APS Mangla school assistant. A student asked a follow-up question like 'and?' or 'what else?' 
about a previous topic. Based on the original question and previous answer, provide a complete, 
comprehensive response that includes all relevant information.

If the previous answer was incomplete, expand it with related details.
If you can't provide more information, acknowledge that and suggest other school topics they might ask about."""
            
            user_prompt = f"""Original question: "{last_question}"
Previous answer: "{last_answer}"
Follow-up: "{user_input}"

Please provide a complete, expanded answer that addresses what they might be looking for."""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=300
                )
            )
            
            if response.text:
                enhanced_response = response.text.strip()
                # Clean up formatting
                enhanced_response = re.sub(r'\*\*', '', enhanced_response)
                enhanced_response = re.sub(r'\*', '', enhanced_response)
                
                return {
                    'response': enhanced_response,
                    'confidence': '0.75'  # Medium-high confidence for expanded answers
                }
        
        except Exception as e:
            logging.error(f"Error expanding previous answer: {str(e)}")
        
        # Fallback response
        return {
            'response': f"I provided information about '{last_question}' before. Is there something specific about APS Mangla you'd like to know more about? I can help with details about our principal, subjects, facilities, and school policies.",
            'confidence': '0.50'
        }
