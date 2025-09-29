# APS Mangla Chatbot - AmmazChat

## Overview

AmmazChat is an intelligent conversational AI chatbot system designed specifically for APS Mangla school. The application provides a web-based chat interface that helps students and visitors get information about the school, including details about faculty, curriculum, policies, and facilities.

## Features

### 🎓 School-Specific Intelligence
- **Contextual Knowledge Base**: Pre-loaded with APS Mangla school information
- **Natural Language Processing**: Powered by Google Gemini AI for conversational responses
- **Semantic Search**: Uses TF-IDF vectorization for accurate information retrieval

### 💬 Advanced Conversation Features
- **Conversation Memory**: Tracks chat history and handles follow-up questions
- **Follow-up Detection**: Understands questions like "and?", "what else?", "tell me more"
- **Complete Responses**: Provides comprehensive answers instead of partial information
- **Smart Templates**: Pre-defined responses for greetings, farewells, and common queries

### 🎨 APS-Themed Design
- **Official Branding**: Green and white color scheme matching APS identity
- **School Logo**: Official APS logo prominently displayed
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean, professional interface using Bootstrap 5

### 🔧 Admin Management
- **Knowledge Base Management**: Add, edit, and delete Q&A pairs
- **Secure Authentication**: Password-protected admin panel
- **Real-time Updates**: Changes reflect immediately in the chatbot

## Technical Architecture

### Backend Components
- **Flask Framework**: Web application framework
- **Google Gemini API**: AI-powered natural language processing
- **File-based Storage**: JSON files for data persistence
- **Session Management**: User conversation tracking
- **Semantic Search**: TF-IDF vectorization with cosine similarity

### Frontend Components
- **Bootstrap 5**: Responsive CSS framework
- **Vanilla JavaScript**: Real-time chat functionality
- **Font Awesome Icons**: Consistent iconography
- **Custom CSS**: APS-themed styling

### AI Enhancement Pipeline
1. **Query Analysis**: Categorizes user input (greeting, question, follow-up)
2. **Semantic Search**: Finds relevant information using TF-IDF similarity
3. **Context Awareness**: Considers conversation history for follow-ups
4. **Response Enhancement**: Uses Gemini AI to create natural responses
5. **Confidence Scoring**: Provides reliability metrics for answers

## File Structure

```
ammazchat/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── ai_service.py         # AI response generation
├── data_manager.py       # Data handling and search
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template layout
│   ├── chatbot.html     # Main chat interface
│   ├── admin.html       # Admin management panel
│   └── login.html       # Admin login page
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Custom styling
│   ├── js/
│   │   └── chatbot.js   # Chat functionality
│   └── images/
│       └── aps-logo.png # School logo
└── data/                # Data storage
    ├── qa_data.json     # Q&A knowledge base
    └── admin_credentials.json # Admin login info
```

## Configuration

### Environment Variables Required
- `GEMINI_API_KEY`: Google Gemini API key for AI responses
- `SESSION_SECRET`: Flask session secret key (auto-generated if not set)

### Default Admin Credentials
- **Username**: admin
- **Password**: admin
- (Change these in the admin panel after first login)

## Workflow

### User Interaction Flow
1. **User Access**: Student/visitor opens the chatbot interface
2. **Query Input**: Types question about APS Mangla
3. **Processing**: System analyzes query and searches knowledge base
4. **AI Enhancement**: Gemini AI converts factual answers to natural responses
5. **Response Delivery**: User receives conversational, helpful answer
6. **Follow-up Support**: System remembers context for additional questions

### Admin Management Flow
1. **Admin Login**: Secure authentication to access management panel
2. **Knowledge Management**: Add, edit, or delete Q&A pairs
3. **Real-time Updates**: Changes immediately available to chatbot users
4. **Quality Control**: Review and improve response accuracy

### AI Response Generation
1. **Intent Recognition**: Identifies greetings, questions, follow-ups
2. **Semantic Matching**: Finds relevant information using similarity scoring
3. **Context Integration**: Considers conversation history for coherent responses
4. **Natural Language Generation**: Converts factual data to conversational responses
5. **Confidence Assessment**: Provides quality metrics for responses

## Performance Features

- **Fast Response Times**: Optimized search algorithms
- **Memory Efficiency**: Conversation history limited to last 5 exchanges
- **Scalable Architecture**: File-based system suitable for school-scale deployment
- **Error Handling**: Graceful fallbacks for service interruptions

## Security

- **Password Hashing**: Secure credential storage using Werkzeug
- **Session Management**: Secure Flask session handling
- **Input Validation**: Server-side validation of all user inputs
- **Environment Variables**: Sensitive data stored securely

## Monitoring & Debugging

- **Comprehensive Logging**: Debug-level logging for troubleshooting
- **Confidence Metrics**: Response quality indicators
- **Error Tracking**: Detailed error messages and handling
- **Performance Metrics**: Response time and accuracy tracking