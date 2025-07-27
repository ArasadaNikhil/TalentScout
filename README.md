# TalentScout
A Hiring Assistant for Candidate Screening.
## Setup

1. **Install dependencies**
   - pip install -r requirements.txt

2. **Get Groq API key**
   - Visit [console.groq.com](https://console.groq.com)
   - Sign up (free)
   - Create API key

3. **Create .env file**
   - GROQ_API_KEY=your_key_here

4. **Run the app**
   streamlit run app.py

## How to Use

- Chat with the AI interviewer
- Type `bye`, `exit`, or `quit` to end
- Your info (email, phone, experience) is automatically extracted

## Files

- `app.py` - Main application
- `chatbot.py` - AI logic
- `validators.py` - State management
- `requirements.txt` - Dependencies
