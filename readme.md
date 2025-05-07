# Riddle Generator App

A simple application that generates puzzles or riddles based on user input and creates downloadable images.

## Features

- Generate intelligent puzzles or riddles based on user input
- Preview puzzles as images with clean, minimalist design
- Download puzzles as PNG images
- Clean and modern UI

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd puzzle-generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables:
   - Copy the `.env` file or create a new one with your API keys.
   - Make sure to add your own GROQ API key (or keep the provided one if valid).

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## How to Use

1. Enter a word or phrase in the input field.
2. Click "Generate Puzzle" to create a unique puzzle.
3. Click "Preview Image" to see how the puzzle looks as an image.
4. Click "Download Image" to download the puzzle as a PNG file.

## Technologies Used

- Flask: Web framework
- Pillow: Image processing
- LLM API: AI text generation
- TailwindCSS: Styling
