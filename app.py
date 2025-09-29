import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from data_manager import DataManager
from ai_service import AIService

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Railway!"  # You can change this

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway assigns port via $PORT
    app.run(host="0.0.0.0", port=port)
    
# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-key-change-in-production")

# Initialize services
data_manager = DataManager()
ai_service = AIService()

@app.route('/')
def index():
    """Main chatbot page"""
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with enhanced intelligence and conversation memory"""
    try:
        message = request.form.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        logging.debug(f"Received message: {message}")
        
        # Initialize conversation memory if not exists
        if 'conversation_memory' not in session:
            session['conversation_memory'] = []
        
        # Get intelligent response using enhanced AI service with conversation context
        response_data = ai_service.get_intelligent_response(
            message, data_manager, session.get('conversation_memory', [])
        )
        
        # Update conversation memory
        conversation_entry = {
            'user_message': message,
            'bot_response': response_data['response'],
            'confidence': response_data['confidence'],
            'timestamp': str(len(session['conversation_memory']))
        }
        
        # Keep only last 5 exchanges to prevent session bloat
        session['conversation_memory'].append(conversation_entry)
        if len(session['conversation_memory']) > 5:
            session['conversation_memory'] = session['conversation_memory'][-5:]
        
        # Mark session as modified for Flask to save it
        session.modified = True
        
        logging.debug(f"Response data: {response_data}")
        logging.debug(f"Updated conversation memory: {len(session['conversation_memory'])} entries")
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({
            'error': 'Sorry, I encountered an error while processing your message.',
            'response': 'I apologize, but something went wrong. Please try asking your question again.',
            'confidence': '0.00'
        }), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username and password and data_manager.verify_admin_credentials(username, password):
            session['admin_authenticated'] = True
            session['admin_username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    flash('Successfully logged out!', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    """Admin panel"""
    if not session.get('admin_authenticated'):
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))
    
    qa_pairs = data_manager.get_all_qa_pairs()
    return render_template('admin.html', qa_pairs=qa_pairs)

@app.route('/admin/add', methods=['POST'])
def add_qa_pair():
    """Add new Q&A pair"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    
    if question and answer:
        success = data_manager.add_qa_pair(question, answer)
        if success:
            flash('Q&A pair added successfully!', 'success')
        else:
            flash('Failed to add Q&A pair.', 'danger')
    else:
        flash('Both question and answer are required.', 'warning')
    
    return redirect(url_for('admin'))

@app.route('/admin/edit/<int:qa_id>', methods=['POST'])
def edit_qa_pair(qa_id):
    """Edit existing Q&A pair"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    
    if question and answer:
        success = data_manager.update_qa_pair(qa_id, question, answer)
        if success:
            flash('Q&A pair updated successfully!', 'success')
        else:
            flash('Failed to update Q&A pair.', 'danger')
    else:
        flash('Both question and answer are required.', 'warning')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:qa_id>')
def delete_qa_pair(qa_id):
    """Delete Q&A pair"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    success = data_manager.delete_qa_pair(qa_id)
    if success:
        flash('Q&A pair deleted successfully!', 'success')
    else:
        flash('Failed to delete Q&A pair.', 'danger')
    
    return redirect(url_for('admin'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('chatbot.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logging.error(f"Internal server error: {str(error)}")
    return render_template('chatbot.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
