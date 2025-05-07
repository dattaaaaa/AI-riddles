from flask import Flask, render_template, request, jsonify, send_file
import requests
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import os
from dotenv import load_dotenv
import base64
import math

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get API key from environment variable
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your_groq_api_key_here')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'gemma2-9b-it'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-puzzle', methods=['POST'])
def generate_puzzle():
    try:
        # Get user input
        data = request.get_json()
        word = data.get('word', '').strip()
        
        if not word:
            return jsonify({'error': 'Please enter a word or phrase'}), 400
        
        # Generate puzzle using GROQ API
        system_prompt = """
        You are a puzzle creator. Create an intelligent, challenging puzzle or riddle where the answer is the provided word or phrase.
        The puzzle should be clever, not obvious, and require some thinking to solve.
        Keep the puzzle to 3-5 sentences maximum. Do not include the answer in your response.
        Do not hint about number of letters or number of words.
        Think and give good puzzles only.
        The output should be only puzzle nothing else.
        """
        
        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': GROQ_MODEL,
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': f'Create a puzzle where the answer is: {word}'
                }
            ],
            'temperature': 0.7,
            'max_tokens': 200
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        puzzle_text = response.json()['choices'][0]['message']['content'].strip()
        
        return jsonify({'puzzle': puzzle_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_font_size(text, image_width, image_height):
    """Calculate the optimal font size to fit text in the image."""
    # Start with a large font size and reduce until it fits
    max_font_size = 100
    min_font_size = 20
    target_width_ratio = 0.85  # Use 85% of the image width
    target_height_ratio = 0.85  # Use 85% of the image height
    
    # Binary search for the optimal font size
    font_size = max_font_size
    while max_font_size - min_font_size > 1:
        font_size = (max_font_size + min_font_size) // 2
        try:
            # Try to find a font file
            try:
                font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'ArialMT-Light.ttf')
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    # Try common system fonts
                    font = ImageFont.truetype("Arial", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("Helvetica", font_size)
                except IOError:
                    font = ImageFont.load_default()
            
            # Calculate wrapped text dimensions
            lines = textwrap.wrap(text, width=int(image_width * target_width_ratio / (font_size * 0.6)))
            wrapped_text = '\n'.join(lines)
            
            # Get text dimensions
            dummy_img = Image.new('RGB', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            text_bbox = dummy_draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Check if text fits
            if (text_width <= image_width * target_width_ratio and 
                text_height <= image_height * target_height_ratio):
                min_font_size = font_size
            else:
                max_font_size = font_size
                
        except Exception:
            max_font_size = font_size
    
    return min_font_size, lines

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        puzzle_text = data.get('puzzle', '').strip()
        
        if not puzzle_text:
            return jsonify({'error': 'No puzzle text provided'}), 400
        
        # Create high-quality image with puzzle text
        width, height = 1920, 1080  # High-resolution landscape
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Calculate optimal font size
        font_size, wrapped_lines = calculate_font_size(puzzle_text, width, height)
        wrapped_text = '\n'.join(wrapped_lines)
        
        # Load font with calculated size
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Arial.ttf')
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.truetype("Arial", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("Helvetica", font_size)
            except IOError:
                font = ImageFont.load_default()
        
        # Center text in image
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((width - text_width) / 2, (height - text_height) / 2)
        
        # Draw text on image with antialiasing
        draw.multiline_text(position, wrapped_text, fill='black', font=font, align='center')
        
        # Add a subtle border/shadow for better readability
        image = image.filter(ImageFilter.SMOOTH)
        
        # Save image to memory in high quality
        img_io = io.BytesIO()
        image.save(img_io, 'PNG', quality=95, optimize=True, dpi=(300, 300))
        img_io.seek(0)
        
        # Return image data as base64 for preview
        encoded_img = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return jsonify({'image': encoded_img})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-image', methods=['GET'])
def download_image():
    try:
        # Get puzzle text from URL parameter instead of POST body
        puzzle_text = request.args.get('puzzle', '').strip()
        
        if not puzzle_text:
            return jsonify({'error': 'No puzzle text provided'}), 400
        
        # Create high-quality image with puzzle text
        width, height = 1920, 1080  # High-resolution landscape
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Calculate optimal font size
        font_size, wrapped_lines = calculate_font_size(puzzle_text, width, height)
        wrapped_text = '\n'.join(wrapped_lines)
        
        # Load font with calculated size
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Arial.ttf')
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.truetype("Arial", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("Helvetica", font_size)
            except IOError:
                font = ImageFont.load_default()
        
        # Center text in image
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((width - text_width) / 2, (height - text_height) / 2)
        
        # Draw text on image with antialiasing
        draw.multiline_text(position, wrapped_text, fill='black', font=font, align='center')
        
        # Apply smoothing for better text quality
        image = image.filter(ImageFilter.SMOOTH)
        
        # Save image to memory in high quality
        img_io = io.BytesIO()
        image.save(img_io, 'PNG', quality=100, optimize=True, dpi=(300, 300))
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='puzzle.png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)