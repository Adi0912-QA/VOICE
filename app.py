from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import openai
from firebase_service import log_interaction

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/api/design', methods=['POST'])
def get_design():
    data = request.json
    query = data.get('query')
    budget = data.get('budget')
    style = data.get('style')

    try:
        # Get design inspirations
        images = get_design_inspirations(query)
        
        # Generate AI suggestions
        suggestions = generate_design_ideas(query, budget, style)
        
        # Log interaction
        log_interaction(query, budget, style, images)
        
        return jsonify({
            'success': True,
            'images': images,
            'suggestions': suggestions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_design_inspirations(query):
    """Fetch images from APIs"""
    results = []
    
    # Google Custom Search
    google_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': os.getenv('GOOGLE_API_KEY'),
        'cx': os.getenv('GOOGLE_CSE_ID'),
        'q': f"{query} interior design",
        'searchType': 'image',
        'num': 5
    }
    google_response = requests.get(google_url, params=params).json()
    
    # Unsplash API
    unsplash_url = "https://api.unsplash.com/search/photos"
    headers = {'Authorization': f'Client-ID {os.getenv("UNSPLASH_ACCESS_KEY")}'}
    unsplash_params = {'query': query, 'per_page': 5}
    unsplash_response = requests.get(unsplash_url, headers=headers, params=unsplash_params).json()
    
    # Combine results
    for item in google_response.get('items', []):
        results.append(item['link'])
    
    for item in unsplash_response.get('results', []):
        results.append(item['urls']['regular'])
    
    return results[:8]

def generate_design_ideas(query, budget, style):
    """Generate AI suggestions"""
    prompt = f"""As an interior designer, suggest ideas for:
    Theme: {query}
    Budget: {budget}
    Style: {style}
    Include color schemes, materials, and space optimization tips."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True, port=5000)
