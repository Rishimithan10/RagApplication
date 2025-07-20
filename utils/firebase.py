import requests
from config import fire_base_api_key
import firebase_admin
from firebase_admin import credentials, firestore

def firebase_signup(email, password, first_name, last_name):

    # Step 1: Sign up user using Firebase Auth REST API
    if not firebase_admin._apps:
        cred = credentials.Certificate("ragapplication-28e4f-firebase-adminsdk-fbsvc-dfff17bce0.json")  # 🔁 Replace with your actual path
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={fire_base_api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload).json()

    # Handle signup error
    if "error" in response:
        return {"success": False, "error": response["error"]["message"]}

    # Extract user ID and ID token
    user_id = response.get("localId")
    id_token = response.get("idToken")

    # Step 2: Store additional user info in Firestore
    try:
        db.collection("users").document(user_id).set({
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        })
        return {
            "success": True,
            "message": "Signup successful and user data stored",
            "user_id": user_id,
            "id_token": id_token
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Signup succeeded but failed to store user data in Firestore",
            "error": str(e)
        }

def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={fire_base_api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=payload).json()

def refresh_firebase_token(refresh_token):
    url = f"https://securetoken.googleapis.com/v1/token?key={fire_base_api_key}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    return requests.post(url, data=payload).json()
def get_user_details(user_id):
    if not firebase_admin._apps:
        cred = credentials.Certificate("ragapplication-28e4f-firebase-adminsdk-fbsvc-dfff17bce0.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
