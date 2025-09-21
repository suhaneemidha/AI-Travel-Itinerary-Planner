# backend.py
import datetime
import math
import random
import re
import requests

# Optional TTS and speech recognition for non-headless mode
try:
    import pyttsx3
    import speech_recognition as sr
except ImportError:
    pyttsx3 = None
    sr = None

class VoiceAssistant:
    def __init__(self, headless=False):
        self.headless = headless
        self.assistant_name = "DeepSphere"
        self._setup_core_components()
        self._setup_apis()
        self._setup_responses()

    def _setup_core_components(self):
        if not self.headless:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.tts_engine = pyttsx3.init()
            self._configure_voice()
        else:
            self.recognizer = None
            self.microphone = None
            self.tts_engine = None

    def _setup_apis(self):
        self.gemini_api_key = "AIzaSyABGzhkOOwW8jKUW5QgLedd0ApJDiheW9o"
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def _setup_responses(self):
        self.responses = {
            "hello": ["Hello! How can I help you today?", "Hi there!", "Hello! Nice to meet you!"],
            "how are you": ["I'm doing great, thank you for asking!", "I'm fine, how about you?"],
            "what is your name": [f"I'm {self.assistant_name}, your personal assistant!", f"You can call me {self.assistant_name}."],
            "goodbye": ["Goodbye! Have a great day!", "See you later!", "Bye! Take care!"],
            "thank you": ["You're welcome!", "Happy to help!", "No problem!"],
            "trip": ["Sounds like an exciting trip! Tell me more about your destination.", "Planning a trip? What's your dream destination?"],
            "plan": ["I'd love to help plan your trip. What's the occasion?", "Let's plan an amazing adventure!"],
        }

    def _configure_voice(self):
        if self.tts_engine:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 1.0)

    # =========================
    # HEADLESS SPEAK FUNCTION
    # =========================
    def speak(self, text):
        if self.headless:
            print(f"Assistant: {text}")  # just print in headless mode
        else:
            print(f"Assistant: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    # =========================
    # GEMINI API CALL FOR CONVERSATION
    # =========================
    def ask_gemini(self, prompt, lang='en'):
        try:
            lang_prompt = f"Respond in {lang}." if lang != 'en' else ""
            full_prompt = f"You are a friendly AI travel assistant. Answer naturally and conversationally. Keep responses concise but helpful. Focus on travel planning, destinations, tips, etc.\n\nUser: {prompt}\nAssistant:"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.6, "maxOutputTokens": 500, "topP": 0.7, "topK": 30}
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                json=payload,
                headers=headers,
                timeout=30
            )
            if response.ok:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"].strip()
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    # =========================
    # GENERAL GEMINI CALL FOR STRUCTURED TASKS
    # =========================
    def call_gemini(self, prompt, generation_config=None, lang='en'):
        try:
            full_prompt = f"You are a friendly AI travel assistant. Answer naturally and conversationally. Keep responses concise but helpful. Focus on travel planning, destinations, tips, etc.\n\nUser: {prompt}\nAssistant:"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": generation_config or {"temperature": 0.7, "maxOutputTokens": 2000, "topP": 0.8, "topK": 40}
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                json=payload,
                headers=headers,
                timeout=30
            )
            if response.ok:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"].strip()
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    # =========================
    # ITINERARY GENERATION
    # =========================
    def generate_itinerary(self, start_date, end_date, num_people, budget, destination, preferences, mode='budget', refinement='', lang='en'):
        refinement_text = f" Additional notes: {refinement}" if refinement else ''
        prompt = f"""Generate a detailed {mode} travel itinerary for {destination} from {start_date} to {end_date} for {num_people} people with a budget of ₹{budget}. Preferences: {preferences}.{refinement_text}

Please format the response as structured HTML that can be directly inserted into a div, including:
- A summary section with trip details (dates, people, budget, mode)
- Daily sections (Day 1 - Date, etc.) with flights/hotels/transport/activities
- End with a ready-to-book section

Use professional styling classes like bg-white/10, rounded-lg, etc., compatible with Tailwind CSS. Keep it concise and actionable."""

        gen_config = {"temperature": 0.5, "maxOutputTokens": 3000}
        return self.call_gemini(prompt, gen_config)

    # =========================
    # MATH HANDLING
    # =========================
    def handle_math(self, command):
        try:
            expr = command.lower().strip()
            # SQUARE ROOT
            if "square root" in expr or "root" in expr:
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if numbers:
                    number = float(numbers[0])
                    return f"The square root of {number} is {math.sqrt(number):.4f}"
            # CUBE ROOT
            if "cube root" in expr:
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if numbers:
                    number = float(numbers[0])
                    return f"The cube root of {number} is {number ** (1/3):.4f}"
            # FACTORIAL
            if "factorial" in expr:
                numbers = re.findall(r'\d+', expr)
                if numbers:
                    number = int(numbers[0])
                    if number < 0:
                        return "Factorial is not defined for negative numbers"
                    if number > 20:
                        return f"Factorial of {number} is too large to calculate"
                    return f"The factorial of {number} is {math.factorial(number)}"
            # POWER
            if any(word in expr for word in ["power", "raised to", "to the power"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    base = float(numbers[0])
                    exp = float(numbers[1])
                    return f"{base} to the power of {exp} is {base ** exp}"
            # BASIC ARITHMETIC
            if any(word in expr for word in ["plus", "add", "minus", "subtract", "times", "multiply", "divided by", "divide", "mod", "modulo"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    num1 = float(numbers[0])
                    num2 = float(numbers[1])
                    if "plus" in expr or "add" in expr:
                        return f"{num1} plus {num2} equals {num1 + num2}"
                    if "minus" in expr or "subtract" in expr:
                        return f"{num1} minus {num2} equals {num1 - num2}"
                    if "times" in expr or "multiply" in expr:
                        return f"{num1} times {num2} equals {num1 * num2}"
                    if "divided by" in expr or "divide" in expr:
                        if num2 == 0:
                            return "Cannot divide by zero"
                        return f"{num1} divided by {num2} equals {num1 / num2:.4f}"
                    if "mod" in expr or "modulo" in expr:
                        if num2 == 0:
                            return "Cannot divide by zero"
                        return f"The remainder when {num1} is divided by {num2} is {int(num1) % int(num2)}"
            # FALLBACK
            numbers = re.findall(r'\d+(?:\.\d+)?', expr)
            if numbers:
                return f"I found numbers: {', '.join(numbers)}. Please specify an operation like 'plus', 'minus', 'times', or 'divided by'."
            return "I couldn't understand the math operation."
        except Exception as e:
            return f"Math error: {str(e)}"

    # =========================
    # PROCESS COMMAND
    # =========================
    def process_command(self, command, lang='en'):
        if not command:
            return "No input provided."

        command = command.lower().strip()

        # Basic responses
        for key, responses in self.responses.items():
            if key in command:
                return random.choice(responses)

        # Travel-specific
        if any(word in command for word in ["trip", "travel"]):
            return random.choice(self.responses.get("trip", ["Tell me more about your travel plans!"]))
        if "plan" in command:
            return random.choice(self.responses.get("plan", ["Let's plan it together!"]))

        # Time
        if "time" in command:
            return datetime.datetime.now().strftime("It's %I:%M %p")
        # Date
        if "date" in command or "day" in command:
            return datetime.datetime.now().strftime("Today is %A, %B %d, %Y")
        # Math
        math_keywords = ["plus","minus","times","multiply","divide","divided by","add","subtract","power","square root","cube root","factorial","mod","modulo"]
        if any(word in command for word in math_keywords) or any(char in command for char in "+-*/%**"):
            return self.handle_math(command)
        # Complex questions -> Gemini
        answer = self.ask_gemini(command, lang)
        return answer or "I'm not sure how to respond to that."