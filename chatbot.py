import os
from groq import Groq
import re
from validators import EmailValidator, PhoneValidator

class TalentScoutChatbot:
    """AI Hiring Assistant powered by Groq with proper conversation ending"""
    
    def __init__(self):
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"
        
        self.system_prompt = """
        You are a Hiring Assistant chatbot for TalentScout, a recruitment agency specializing in technology placements.

        YOUR PURPOSE: Assist in initial screening of candidates by gathering essential information and posing relevant technical questions.

        REQUIRED INFORMATION TO COLLECT (in order):
        1. Full Name(First name and Last name)
        2. Email Address  
        3. Phone Number
        4. Years of Experience
        5. Desired Position(s)
        6. Current Location
        7. Tech Stack (programming languages, frameworks, databases, tools)

        PROCESS:
        1. Greet candidate and provide brief overview of your purpose
        2. Gather ALL required information systematically
        3. Once tech stack is declared, generate 3-5 technical questions tailored to their specified technologies
        4. Maintain context throughout conversation
        5. If user says goodbye/quit/exit keywords, gracefully conclude with next steps

        CONSTRAINTS:
        - Stay focused on hiring/recruitment purpose
        - Do not deviate from the core functionality
        - Keep responses professional and concise
        - Handle unexpected inputs with meaningful fallback responses
        """
        
        self.conversation_history = []
        self.candidate_info = {}
        
        # Initialize validators
        self.email_validator = EmailValidator()
        self.phone_validator = PhoneValidator()
    
    def is_exit_keyword(self, user_input):
        """Robust exit keyword detection"""
        if not user_input:
            return False
            
        exit_keywords = ['quit', 'exit', 'bye', 'goodbye', 'stop', 'end', 'finish', 'done']
        user_lower = user_input.lower().strip()
        
        # Check for exact matches
        if user_lower in exit_keywords:
            return True
        
        # Check for exit keywords as separate words
        words = user_lower.split()
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in exit_keywords:
                return True
                
        # Check for common exit phrases
        exit_phrases = [
            'i want to quit', 'i want to exit', "i'm done", "that's all",
            'end interview', 'finish interview', 'i have to go', 'gotta go'
        ]
        
        for phrase in exit_phrases:
            if phrase in user_lower:
                return True
                
        return False
    
    def extract_candidate_info(self, user_input, bot_response):
        """Extract and store candidate information from conversation"""
        user_lower = user_input.lower()
        
        # Extract email using validator
        if 'email' not in self.candidate_info:
            extracted_email = self.email_validator.extract_email(user_input)
            if extracted_email:
                self.candidate_info['email'] = extracted_email
        
        # Extract phone using validator
        if 'phone' not in self.candidate_info:
            extracted_phone = self.phone_validator.extract_phone(user_input)
            if extracted_phone:
                self.candidate_info['phone'] = extracted_phone
        
        # Extract years of experience
        exp_pattern = r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)'
        exp_match = re.search(exp_pattern, user_lower)
        if exp_match and 'experience' not in self.candidate_info:
            self.candidate_info['experience'] = exp_match.group(1) + ' years'
    
    def get_farewell_message(self):
        """Generate a professional farewell message"""
        return """Thank you so much for your time today! 🙏 

It was wonderful getting to know you and learning about your experience. We'll carefully review everything we discussed and be in touch within the next few days if your profile aligns with our current opportunities. 

Best of luck with your job search! 🎯"""
    
    def get_response(self, user_input):
        """Get AI response from Groq with proper exit handling"""
        try:
            # Check for exit keywords FIRST - this is crucial
            if self.is_exit_keyword(user_input):
                return self.get_farewell_message()
            
            # Build messages for Groq
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history (keep last 12 exchanges for context)
            for msg in self.conversation_history[-12:]:
                messages.append(msg)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get response from Groq
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.4,
                max_tokens=250,
                top_p=0.9
            )
            
            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            # Extract candidate information
            self.extract_candidate_info(user_input, assistant_response)
            
            return assistant_response
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again in a moment. Error: {str(e)}" 