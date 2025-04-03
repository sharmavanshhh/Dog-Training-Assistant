# Dog Training Assistant

A chatbot application designed to help dog owners with personalized training advice, behavior analysis, and health recommendations. The assistant provides guidance on various dog training methods, from basic commands to specific behavioral issues. The system also offers real-time responses and integrates with external APIs for breed and health-related information.

## Features

- **Personalized Training Plans**: Helps create customized training routines for dogs based on breed, age, and other factors.
- **Dog Breed Information**: Fetches detailed information about various dog breeds (e.g., temperament, lifespan, size, etc.) using TheDogAPI.
- **Live Chat**: Real-time interaction with the chatbot to answer dog-related training queries.
- **Voice Integration**: Option to hear bot responses with an integrated text-to-speech feature.
- **Speech Recognition**: Allows users to interact with the chatbot using voice input.

## Tech Stack

- **Frontend**: React.js  
- **Backend**: Flask (Python)  
- **APIs**:  
  - [TheDogAPI](https://thedogapi.com/) for breed-related information  
  - [Gemini API](https://gemini.openai.com/) for generative chatbot responses  
- **Database**: MySQL (for storing user history and training plans)  
- **Voice Synthesis**: Web Speech API for text-to-speech functionality  

## Installation

### Prerequisites  

1. Make sure you have Python 3.x installed.  
2. Install Node.js (for React frontend).  
3. Ensure you have MySQL set up for the database.  

### Quick Setup  

To install all dependencies, run the `setup.bat` script:  

```bash
setup.bat
```

This script will:  
- Set up a Python virtual environment  
- Install backend dependencies (`pip install -r requirements.txt`)  
- Install frontend dependencies (`npm install`)  

### Manual Setup  

If you prefer manual installation, follow these steps:  

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/codebyharshe/Dog-Training-Assistant.git
   cd Dog-Training-Assistant
   ```

2. **Backend Setup (Flask)**:  
   - Navigate to the backend folder and create a virtual environment:  
     ```bash
     cd backend
     python -m venv venv
     source venv/bin/activate  # For macOS/Linux
     .\venv\Scripts\activate  # For Windows
     ```

   - Install the required dependencies:  
     ```bash
     pip install -r requirements.txt
     ```

   - **Update API keys, SQL credentials, and email settings**:  
     - Open `app.py` and update the following details:  
       - **API Keys**: Replace with your own API keys for [Gemini](https://gemini.openai.com/) and [TheDogAPI](https://thedogapi.com/).  
       - **MySQL Credentials**: Update the database credentials (`host`, `user`, `password`, `database`) with your own MySQL configuration.  
       - **Email Settings**: Set up your email credentials for sending notifications.  

     ```python
     # Example for updating API keys and database credentials in app.py

     GEMINI_API_KEY = "your-gemini-api-key"
     DOG_API_KEY = "your-dog-api-key"
     DB_HOST = "localhost"
     DB_USER = "your-db-user"
     DB_PASSWORD = "your-db-password"
     DB_NAME = "your-db-name"
     EMAIL_ADDRESS = "your-email@example.com"
     EMAIL_PASSWORD = "your-email-password"
     ```

3. **Frontend Setup (React)**:  
   - Navigate to the frontend folder:  
     ```bash
     cd frontend
     ```

   - Install the required dependencies:  
     ```bash
     npm install
     ```

## Running the Application  

To start both the backend and frontend, run:  

```bash
perro.bat
```

This script will:  
- Activate the Python virtual environment  
- Start the Flask backend server (`python app.py`)  
- Start the React frontend (`npm start`)  

Alternatively, you can manually run:  

```bash
# In backend folder
cd backend
source venv/bin/activate  # For macOS/Linux
.\venv\Scripts\activate  # For Windows
python app.py

# In another terminal, start frontend
cd frontend
npm start
```

### Access the Application  

- Once both the backend and frontend servers are running, navigate to `http://localhost:3000` in your browser to interact with the Dog Training Assistant.  

## Usage  

1. **Start a Chat Session**: Once the frontend is loaded, type or speak a query to start interacting with the chatbot.  
2. **Get Training Advice**: The bot will ask for details about the dog (breed, age, etc.) and generate a personalized training routine.  
3. **Breed Information**: The bot will provide detailed breed information based on your input.  
4. **Listen to Responses**: Click the speaker icon below the bot's response to hear it out loud.  

## Contributing  

1. Fork this repository.  
2. Create a new branch (`git checkout -b feature-name`).  
3. Commit your changes (`git commit -m 'Add some feature'`).  
4. Push to the branch (`git push origin feature-name`).  
5. Open a pull request.  

## License  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  

## Acknowledgements  

- **Gemini API** for generating chatbot responses.  
- **TheDogAPI** for providing dog breed information.  
- **React.js** and **Flask** for creating the frontend and backend.  
```

