from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mysql.connector
import google.generativeai as genai
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import requests
import time
from flask_mail import Message, Mail
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",       # your MySQL username
    password="", # your MySQL password
    database="dog_chatbot" # your database name (make sure that database exists)
)
cursor = db.cursor()

# Gemini API Configuration
GENAI_API_KEY = ""  # Replace with your actual Gemini API key
genai.configure(api_key=GENAI_API_KEY)

# TheDogAPI Configuration
THE_DOG_API_KEY = ""  # Replace with your actual Dog API key
DOG_API_URL = "https://api.thedogapi.com/v1/breeds"  # Example URL for TheDogAPI

# Dog-related Keywords for filtering
dog_keywords = {
    "affenpinscher", "afghan hound", "african hunting dog", "airedale terrier", "akbash dog", "akita",
    "alapaha blue blood bulldog", "alaskan husky", "alaskan malamute", "american bulldog", "american bully",
    "american eskimo dog", "american eskimo dog (miniature)", "american foxhound", "american pit bull terrier",
    "american staffordshire terrier", "american water spaniel", "anatolian shepherd dog", "appenzeller sennenhund",
    "australian cattle dog", "australian kelpie", "australian shepherd", "australian terrier", "azawakh",
    "barbet", "basenji", "basset bleu de gascogne", "basset hound", "beagle", "bearded collie", "beauceron",
    "bedlington terrier", "belgian malinois", "belgian tervuren", "bernese mountain dog", "bichon frise",
    "black and tan coonhound", "bloodhound", "bluetick coonhound", "boerboel", "border collie", "border terrier",
    "boston terrier", "bouvier des flandres", "boxer", "boykin spaniel", "bracco italiano", "briard", "brittany",
    "bull terrier", "bull terrier (miniature)", "bullmastiff", "cairn terrier", "cane corso", "cardigan welsh corgi",
    "catahoula leopard dog", "caucasian shepherd (ovcharka)", "cavalier king charles spaniel",
    "chesapeake bay retriever", "chinese crested", "chinese shar-pei", "chinook", "chow chow", "clumber spaniel",
    "cocker spaniel", "cocker spaniel (american)", "coton de tulear", "dalmatian", "doberman pinscher",
    "dogo argentino", "dutch shepherd", "english setter", "english shepherd", "english springer spaniel",
    "english toy spaniel", "english toy terrier", "eurasier", "field spaniel", "finnish lapphund", "finnish spitz",
    "french bulldog", "german pinscher", "german shepherd dog", "german shepherd", "german shorthaired pointer", 
    "giant schnauzer", "glen of imaal terrier", "golden retriever", "golden retriever dog", "gordon setter", 
    "great dane", "great pyrenees", "greyhound", "griffon bruxellois", "harrier", "havanese", "irish setter", 
    "irish terrier", "irish wolfhound", "labrador", "labrador retriever", "labrador retriever dog", 
    "labrador retriever (chocolate)", "labrador retriever (black)", "labrador retriever (yellow)", 
    "italian greyhound", "japanese chin", "japanese spitz", "keeshond", "komondor", "kooikerhondje", "kuvasz", 
    "lagotto romagnolo", "lancashire heeler", "leonberger", "lhasa apso", "maltese", "miniature american shepherd", 
    "miniature pinscher", "miniature schnauzer", "newfoundland", "norfolk terrier", "norwich terrier", 
    "nova scotia duck tolling retriever", "old english sheepdog", "olde english bulldogge", "papillon", "pekingese", 
    "pembroke welsh corgi", "perro de presa canario", "pharaoh hound", "plott", "pomeranian", "poodle", "poodle (miniature)", 
    "poodle (toy)", "pug", "puli", "pumi", "rat terrier", "redbone coonhound", "rhodesian ridgeback", "rottweiler", 
    "russian toy", "saint bernard", "saluki", "samoyed", "schipperke", "scottish deerhound", "scottish terrier", 
    "shetland sheepdog", "shiba inu", "shih tzu", "shiloh shepherd", "siberian husky", "silky terrier", 
    "smooth fox terrier", "soft coated wheaten terrier", "spanish water dog", "spanish water dog (spanish)", 
    "spinone italiano", "staffordshire bull terrier", "standard schnauzer", "swedish vallhund", "thai ridgeback", 
    "tibetan mastiff", "tibetan spaniel", "tibetan terrier", "toy fox terrier", "treeing walker coonhound", 
    "vizsla", "weimaraner", "welsh springer spaniel", "west highland white terrier", "whippet", "white shepherd", 
    "wire fox terrier", "wirehaired pointing griffon", "wirehaired vizsla", "xoloitzcuintli", "yorkshire terrier"

    # General dog-related terms
    "dog", "puppy", "puppies", "canine", "hound", "mutt", "pedigree", "purebred", "mongrel", "rescue",
    "adopt", "stray", "feral dog", "pet", "companion", "service animal", "working dog", "family dog",
    "emotional support animal", "therapy animal", "dog lover", "dog enthusiast", "fur baby", "paw parent",
    
    # Training & Commands
    "training", "obedience", "off-leash", "leash", "collar", "harness", "crate", "sit", "stay", "come",
    "heel", "down", "fetch", "jump", "roll over", "paw shake", "speak", "quiet", "leave it", "drop it",
    "focus", "watch me", "release", "crate training", "clicker", "positive reinforcement", "socialization",
    "basic obedience", "advanced training", "recall training", "leash manners", "impulse control",
    "agility training", "behavior shaping", "trick training", "off-leash recall", "e-collar training",
    
    # Dog Activities
    "play", "exercise", "running with dogs", "swimming with dogs", "hiking with dogs", "camping with dogs",
    "dog park", "dog cafe", "dog daycare", "dog spa", "obedience trials", "dog sports", "agility",
    "herding", "tracking", "scent work", "flyball", "frisbee", "dock diving", "tug-of-war", "hide and seek",
    "lure coursing", "hunting dog", "field trials", "cart pulling", "bikejoring", "weight pulling",
    
    # Dog Behavior
    "barking", "whining", "growling", "howling", "digging", "chewing", "biting", "licking", "zoomies",
    "separation anxiety", "territorial", "submissive", "dominance", "resource guarding", "reactivity",
    "fear aggression", "puppy biting", "housebreaking", "potty training", "marking", "scratching",
    "tail wagging", "body language", "hyperactivity", "excitability", "compulsive behaviors",
    
    # Dog Health & Care
    "vet", "veterinarian", "checkup", "spaying", "neutering", "vaccination", "rabies shot", "heartworm",
    "flea prevention", "tick prevention", "deworming", "allergies", "hypoallergenic dog", "raw diet",
    "kibble", "hydration", "arthritis", "hip dysplasia", "elbow dysplasia", "joint health", "glucosamine",
    "digestive health", "sensitive stomach", "probiotics for dogs", "ear infection", "eye infection",
    "hot spots", "yeast infection", "bloating", "obesity in dogs", "weight management",
    
    # Grooming & Hygiene
    "grooming", "brushing", "shedding", "nail trimming", "nail grinder", "dog shampoo", "dog conditioner",
    "hypoallergenic shampoo", "de-shedding brush", "furminator", "dog dryer", "blow drying", "ear cleaning",
    "dental hygiene", "dog toothpaste", "dog toothbrush", "tear stains", "paw balm", "dog cologne",
    "dog perfume", "dog grooming tools", "dog grooming table", "dog grooming clippers", "dog grooming scissors",
    "dog grooming gloves", "dog grooming wipes", "dog grooming kit", "dog grooming salon",
    
    # Dog Accessories & Essentials
    "dog bed", "dog crate", "dog blanket", "dog food bowl", "water dispenser", "slow feeder bowl",
    "dog jacket", "dog sweater", "dog boots", "dog leash", "dog harness", "retractable leash",
    "GPS tracker for dogs", "smart collar", "LED dog collar", "dog tag", "dog ID", "dog muzzle",
    "no-pull harness", "martingale collar", "head halter", "dog backpack", "dog stroller",
    
    # Dog Food & Treats
    "dog food", "raw diet", "dry food", "wet food", "grain-free food", "dog biscuits", "soft treats",
    "freeze-dried treats", "dental chews", "homemade dog treats", "organic dog treats", "training treats",
    "peanut butter for dogs", "jerky treats", "human food safe for dogs", "food allergies in dogs",
    
    # Dog-friendly Places & Travel
    "dog-friendly hotel", "dog-friendly restaurants", "pet-friendly airlines", "dog car seat",
    "dog seat belt", "car harness for dogs", "dog travel crate", "dog-friendly beaches", "pet passport",
    "dog parks near me", "dog-friendly road trip", "hiking with dogs", "airplane travel with dogs",
    
    # Dog Laws & Regulations
    "dog registration", "dog microchip", "pet insurance", "dog vaccination laws", "leash laws",
    "dog license", "dangerous dog laws", "banned breeds", "pet adoption rules", "emotional support dog laws",
    
    # Dog Safety & First Aid
    "dog first aid", "dog CPR", "dog choking", "heatstroke in dogs", "frostbite in dogs", "burns",
    "paw pad injuries", "snake bites", "poisoning symptoms in dogs", "emergency vet", "canine wound care",
    
    # Dog Sports & Competitions
    "dog show", "best in show", "westminster dog show", "crufts", "canine freestyle", "dog rally",
    "obedience trial", "protection sports", "IPO", "schutzhund", "herding trials", "weight pulling",
    
    # Puppy Care & Training
    "puppy teething", "puppy socialization", "puppy vaccinations", "puppy food", "puppy proofing",
    "puppy biting", "puppy leash training", "puppy crate training", "puppy potty training",
    "puppy behavior", "puppy energy levels", "puppy exercise needs", "puppy training timeline",
    
    # Fun & Miscellaneous
    "dog memes", "dog jokes", "funny dog videos", "dog costumes", "dog photography", "dog birthday party",
    "dog adoption stories", "famous dogs", "dog influencers", "celebrity dogs", "dog breed quiz",
    "dog personality quiz", "dog-related movies", "dog TV shows", "dog-themed books", "dog coloring pages",
    
    # Sounds & Communication
    "dog bark", "dog howl", "dog growl", "dog yelp", "dog whimper", "dog sniff", "dog panting",
    "dog tail language", "dog body language", "calming signals", "stress signals in dogs"

    "training", "obedience", "off-leash", "leash", "collar", "harness", "crate", "sit", "stay", "come", "train", "train my dog", "labrador",
    "german shepherd"
}

def contains_dog_keywords(message):
    """Check if the message contains dog-related keywords."""
    message = message.lower()
    for keyword in dog_keywords:
        if keyword.lower() in message:
            return True
    return False

def get_breed_info(breed_name):
    """Fetch breed info from TheDogAPI."""
    try:
        response = requests.get(DOG_API_URL)  # No need for API key
        # print(response.json()) 
        if response.status_code == 200:
            breeds = response.json()
            for breed in breeds:
                if breed_name.lower() in breed["name"].lower():
                    return breed  # Return full breed data
        return None
    except Exception as e:
        print(f"Error fetching breed info: {e}")
        return None

    
def get_training_advice(breed_name, training_type):
    """Fetch training advice from Gemini."""
    prompt = f"Provide training tips for a {breed_name} on {training_type}."
    generation_config = genai.GenerationConfig(
        temperature=0.5,
        top_p=0.9,
    )
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(
        prompt,
        generation_config=generation_config,
    )
    return response.text if response else "No training advice available."


def is_breed_related(message):
    """Check if the message contains a breed name."""
    breed_list = [
    "affenpinscher", "afghan hound", "african hunting dog", "airedale terrier", "akbash dog", "akita",
    "alapaha blue blood bulldog", "alaskan husky", "alaskan malamute", "american bulldog", "american bully",
    "american eskimo dog", "american eskimo dog (miniature)", "american foxhound", "american pit bull terrier",
    "american staffordshire terrier", "american water spaniel", "anatolian shepherd dog", "appenzeller sennenhund",
    "australian cattle dog", "australian kelpie", "australian shepherd", "australian terrier", "azawakh",
    "barbet", "basenji", "basset bleu de gascogne", "basset hound", "beagle", "bearded collie", "beauceron",
    "bedlington terrier", "belgian malinois", "belgian tervuren", "bernese mountain dog", "bichon frise",
    "black and tan coonhound", "bloodhound", "bluetick coonhound", "boerboel", "border collie", "border terrier",
    "boston terrier", "bouvier des flandres", "boxer", "boykin spaniel", "bracco italiano", "briard", "brittany",
    "bull terrier", "bull terrier (miniature)", "bullmastiff", "cairn terrier", "cane corso", "cardigan welsh corgi",
    "catahoula leopard dog", "caucasian shepherd (ovcharka)", "cavalier king charles spaniel",
    "chesapeake bay retriever", "chinese crested", "chinese shar-pei", "chinook", "chow chow", "clumber spaniel",
    "cocker spaniel", "cocker spaniel (american)", "coton de tulear", "dalmatian", "doberman pinscher",
    "dogo argentino", "dutch shepherd", "english setter", "english shepherd", "english springer spaniel",
    "english toy spaniel", "english toy terrier", "eurasier", "field spaniel", "finnish lapphund", "finnish spitz",
    "french bulldog", "german pinscher", "german shepherd dog", "german shepherd", "german shorthaired pointer", 
    "giant schnauzer", "glen of imaal terrier", "golden retriever", "golden retriever dog", "gordon setter", 
    "great dane", "great pyrenees", "greyhound", "griffon bruxellois", "harrier", "havanese", "irish setter", 
    "irish terrier", "irish wolfhound", "labrador", "labrador retriever", "labrador retriever dog", 
    "labrador retriever (chocolate)", "labrador retriever (black)", "labrador retriever (yellow)", 
    "italian greyhound", "japanese chin", "japanese spitz", "keeshond", "komondor", "kooikerhondje", "kuvasz", 
    "lagotto romagnolo", "lancashire heeler", "leonberger", "lhasa apso", "maltese", "miniature american shepherd", 
    "miniature pinscher", "miniature schnauzer", "newfoundland", "norfolk terrier", "norwich terrier", 
    "nova scotia duck tolling retriever", "old english sheepdog", "olde english bulldogge", "papillon", "pekingese", 
    "pembroke welsh corgi", "perro de presa canario", "pharaoh hound", "plott", "pomeranian", "poodle", "poodle (miniature)", 
    "poodle (toy)", "pug", "puli", "pumi", "rat terrier", "redbone coonhound", "rhodesian ridgeback", "rottweiler", 
    "russian toy", "saint bernard", "saluki", "samoyed", "schipperke", "scottish deerhound", "scottish terrier", 
    "shetland sheepdog", "shiba inu", "shih tzu", "shiloh shepherd", "siberian husky", "silky terrier", 
    "smooth fox terrier", "soft coated wheaten terrier", "spanish water dog", "spanish water dog (spanish)", 
    "spinone italiano", "staffordshire bull terrier", "standard schnauzer", "swedish vallhund", "thai ridgeback", 
    "tibetan mastiff", "tibetan spaniel", "tibetan terrier", "toy fox terrier", "treeing walker coonhound", 
    "vizsla", "weimaraner", "welsh springer spaniel", "west highland white terrier", "whippet", "white shepherd", 
    "wire fox terrier", "wirehaired pointing griffon", "wirehaired vizsla", "xoloitzcuintli", "yorkshire terrier"
]

    message = message.lower()
    breeds = ""
    for breed in breed_list:
        breeds = breed+"s"
        if breed in message or breeds in message:
            breeds = ""
            return True, breed
    return False, None

def generate_bot_response(user_message, session_id):
    """Generate chatbot response using Gemini in a streaming format."""
    try:
        cursor.execute(
            "SELECT user_message, bot_response FROM chat_history WHERE session_id = %s ORDER BY id ASC",
            (session_id,),
        )
        chat_history = cursor.fetchall()

        # Format chat history
        formatted_history = "".join(
            [f"User: {u}\nBot: {b}\n" for u, b in chat_history]
        )
        full_prompt = f"{formatted_history}\nUser: {user_message}\nBot:"

        # Initialize Gemini model
        generation_config = genai.GenerationConfig(
            temperature=0.5,
            top_p=0.9,
        )
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        response = model.generate_content(
            full_prompt,
            stream=True,    # Enable streaming
            generation_config=generation_config
        )  
        # Stream the response with on-the-fly formatting
 # Stream the response with on-the-fly formatting
        for chunk in response:
            if chunk.text:
                formatted_chunk = chunk.text

                # Remove all '*' (asterisks) from the text
                formatted_chunk = formatted_chunk.replace("*", "")

                # Yield the formatted chunk in real-time
                yield formatted_chunk

    except Exception as e:
        print("Error:", e)
        yield "Sorry, an unexpected error occurred while generating a response."



# Create Table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100),
    user_message TEXT,
    bot_response TEXT
)
""")
db.commit()

# Define global context for tracking user intent
user_context = {}

# Strip out unnecessary words (like 'buddy', 'bro', etc.)
def normalize_message(message):
    words_to_ignore = ['buddy', 'bro', 'man', 'dude', 'mate', 'pal', 'friend', 'krypto']
    normalized_message = ' '.join([word for word in message.split() if word.lower() not in words_to_ignore])
    return normalized_message

# WebSocket Chat Handling
@socketio.on("user_message")
def handle_message(data):
    global user_context  # Access the global dictionary

    session_id = data.get("session_id")
    message = data.get("message")
    message_lower = message.lower()
    message_lower = normalize_message(message_lower)

    print(f"User ({session_id}): {message}")

    greeting_keywords = [
        "hi", "hello", "hey", "greetings", "howdy", "hola", "namaste", "yo", "sup",
        "what's up", "good morning", "good afternoon", "good evening", "good day",
        "hiya", "how’s it going", "how are you", "what’s new", "long time no see",
        "how have you been", "nice to meet you", "pleased to meet you",
        "how do you do", "morning", "afternoon", "evening", "aloha", "salutations",
        "wassup", "bonjour", "hallo", "hi how are you ", "krypto" ]
    
    creator_questions = [
        "who made you", "who developed you", "who created you", "who designed you", 
        "who built you", "who programmed you", "who is your creator", "who invented you", 
        "who coded you", "who built this chatbot", "who made this bot", "who designed this bot", 
        "who is behind you", "who is your developer", "who is your programmer", "who trained you", 
        "who owns you", "who is your maker", "who is your father", "who is your parent", 
        "who is your boss", "who is your owner", "who constructed you", "who wrote your code", 
        "who gave you life", "who built this AI", "who made this AI", "who developed this chatbot", 
        "who created this AI", "who is responsible for you"
    ]

    farewell_keywords = ["bye", "goodbye", "see you", "take care", "later", "farewell", "see ya", "talk to you later", "thank you", "thanks", "appreciate it", "catch you later", "adios", "au revoir", "sayonara", "peace out", "toodles", "ciao"
                         "okay thank you", "thank you so much", "thanks a lot", "thank you very much", "thank you for your help", "thank you for your assistance", "thank you for your support", "thank you for your time", "thank you for everything", 
                         "thank you for being there", "thank you for your kindness", "thank you for your understanding", "thank you for your patience", "thanks", "thanku", "thank you", "thank you for your help", "thank you for your assistance", 
                         "thank you for your support", "thank you for your time", "thank you for everything",]
    
    if any(message_lower == farewell for farewell in farewell_keywords):
        response_text = "Goodbye! Hope you and your pup have a pawsome day! 🐾"
        for char in response_text:  # Streaming response character by character
            emit("bot_response", {"response": char}, broadcast=True)
            time.sleep(0.02)  # Slight delay for smooth streaming
        cursor.execute(
        "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, response_text))
        db.commit()
        return 

    # Check if the last message was about training
    if session_id in user_context and user_context[session_id] == "training":
        bot_response = ""
        response_stream = generate_bot_response(message, session_id)
        for chunk in response_stream:
            bot_response += chunk
            emit("bot_response", {"response": chunk}, broadcast=True)
        cursor.execute("INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, bot_response))
        db.commit()
        return 
    # If the user asked about dog training, update the context
    elif "training" in message_lower or "train my dog" in message_lower or "help with my dog" in message_lower:
        user_context[session_id] = "training"
        cursor.execute("INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, "training session initiated"))
        db.commit()
        
    

    # Check for greetings
    if any(message_lower == greeting for greeting in greeting_keywords) or any(message_lower.rstrip(" ?") == greeting for greeting in greeting_keywords) or any(message_lower == greeting for greeting in greeting_keywords):
        response_text = "Hi there! Perro here, paws-itively ready to help! How can I assist you today?"
        for char in response_text:  # Streaming response character by character
            emit("bot_response", {"response": char}, broadcast=True)
            time.sleep(0.02)  # Slight delay for smooth streaming
        cursor.execute(
        "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, response_text))
        db.commit()
        return 

    # Check for creator-related questions
    elif any(message_lower == question for question in creator_questions) or any(message_lower.rstrip(" ?") == question for question in creator_questions):
        response_text = "Oh, you want to know about my developer? Well, let me tell you – He’s a total catch! his name’s Vansh Sharma, and trust me, He’s is smartest coder around! He’s the genius behind my dog-tastic personality! 🐶💻"
        for char in response_text:
            emit("bot_response", {"response": char}, broadcast=True)
            time.sleep(0.02)
        cursor.execute(
        "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, response_text))
        db.commit()
        return

    # Check if the message contains dog-related keywords
    if not contains_dog_keywords(message):
        response_text = "Hmm, that's an interesting question! But I can only help with dog-related topics. Let me know how I can assist you?!"
        for char in response_text:
            emit("bot_response", {"response": char}, broadcast=True)
            time.sleep(0.02)
        cursor.execute(
        "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, response_text))
        db.commit()
        return

    # Check if the message is breed-related (e.g., "Tell me about Labradors")
    is_breed_info, breed_name = is_breed_related(message)
    if is_breed_info:
        breed_info = get_breed_info(breed_name)  # Fetch breed info from TheDogAPI
        if breed_info:
            breed_details = f"Breed: {breed_info['name']}\n"
            breed_details += f"Life Span: {breed_info.get('life_span', 'N/A')}\n"
            breed_details += f"Temperament: {breed_info.get('temperament', 'N/A')}\n"
            breed_details += f"Bred For: {breed_info.get('bred_for', 'N/A')}\n"
            breed_details += f"Weight: {breed_info['weight']['metric']} kg\n"
            breed_details += f"Height: {breed_info['height']['metric']} cm\n"

             # Convert the line breaks to <br /> for frontend HTML rendering
            breed_details_html = breed_details.replace("\n", "<br>")
            
            # Stream breed details word by word
            for word in breed_details_html.split():
                emit("bot_response", {"response": word + " "}, broadcast=True)
                time.sleep(0.03)
            cursor.execute(
            "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
            (session_id, message, breed_details))
            db.commit()
        else:
            response_text = f"Sorry, I couldn't find any information on the {breed_name.capitalize()}."
            for char in response_text:
                emit("bot_response", {"response": char}, broadcast=True)
                time.sleep(0.02)
            cursor.execute(
            "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
            (session_id, message, response_text))
            db.commit()
        return

    # Generate regular bot response if no specific action is taken
    response_stream = generate_bot_response(message, session_id)
    bot_response = ""  # Collect full response

    for chunk in response_stream:
        # bot_response += chunk
        emit("bot_response", {"response": chunk}, broadcast=True) # Stream Gemini response in chunks
        time.sleep(0.02)

    # Save final bot response in MySQL
    cursor.execute(
        "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
        (session_id, message, bot_response),
    )
    db.commit()


# Initialize Flask-Mail (you can use environment variables for sensitive data like email and password)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)


@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    """Generate a summary of the chat session and send email with the summary and PDF"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        user_email = data.get("email")  # Email provided by the user

        # Fetch the full chat history for the session
        cursor.execute(
            "SELECT user_message, bot_response FROM chat_history WHERE session_id = %s ORDER BY id ASC",
            (session_id,)
        )
        chat_history = cursor.fetchall()

        if not chat_history:
            return jsonify({"summary": "No chat history found for this session."})

        # Format chat history for Gemini
        formatted_chat = ""
        for user_msg, bot_resp in chat_history:
            formatted_chat += f"User: {user_msg}\nBot: {bot_resp}\n"

        # Generate summary using Gemini
        prompt = f"Summarize the following dog training conversation:\n\n{formatted_chat}"
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        response = model.generate_content(prompt)
        summary = response.text if response else "Could not generate summary."

        # Generate PDF
        pdf_path = f"chat_session_{session_id}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        y_position = 750
        c.drawString(100, y_position, f"Chat Session: {session_id}")
        y_position -= 20

        for user_msg, bot_resp in chat_history:
            c.drawString(80, y_position, f"You: {user_msg}")
            y_position -= 20
            c.drawString(100, y_position, f"Krypto: {bot_resp}")
            y_position -= 30  # Space between messages
            if y_position < 50:  # New page if running out of space
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 750
        c.save()

        # Create the email message with Flask-Mail
        msg = Message("Chat Summary & PDF of Your Dog Training Session", 
                      sender="", recipients=[user_email])
        
        msg.body = f"Dear user,\n\nHere is the summary of your dog training session:\n\n{summary}"

        # Attach the generated PDF
        with open(pdf_path, "rb") as pdf_attachment:
            msg.attach(pdf_path, "application/pdf", pdf_attachment.read())

        # Send the email via Flask-Mail
        mail.send(msg)

        # Optionally delete the PDF after sending the email to avoid clutter
        os.remove(pdf_path)

        return jsonify({"summary": summary, "message": "Summary and PDF sent to your email."})

    except Exception as e:
        print("Error:", e)
        return jsonify({"summary": "An error occurred while generating the summary and sending the email."})
    
@app.route("/download_chat", methods=["POST"])
def download_chat():
    """Generate a PDF of the chat session and allow download"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")

        # Fetch chat history from MySQL
        cursor.execute(
            "SELECT user_message, bot_response FROM chat_history WHERE session_id = %s ORDER BY id ASC",
            (session_id,),
        )
        chat_history = cursor.fetchall()

        if not chat_history:
            return jsonify({"error": "No chat history found for this session."}), 404

        # Generate PDF
        pdf_path = f"chat_session_{session_id}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        y_position = 750  # Start position for text

        c.drawString(100, y_position, f"Chat Session: {session_id}")
        y_position -= 20

        for user_msg, bot_resp in chat_history:
            c.drawString(80, y_position, f"You: {user_msg}")
            y_position -= 20
            c.drawString(100, y_position, f"Krypto: {bot_resp}")
            y_position -= 30  # Space between messages

            if y_position < 50:  # New page if running out of space
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 750

        c.save()

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred while generating the PDF."}), 500


@app.route("/")
def home():
    return "Dog Trainer Chatbot Backend Running"

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
