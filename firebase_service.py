import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred)
db = firestore.client()

def log_interaction(query, budget, style, images):
    """Store in Firestore"""
    doc_ref = db.collection('design_requests').document()
    doc_ref.set({
        'query': query,
        'budget': budget,
        'style': style,
        'images': images,
        'timestamp': datetime.now().isoformat()
    })
