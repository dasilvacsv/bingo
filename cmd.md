# Create virtual environment
python -m venv bingo_env

# Activate it (Windows)
bingo_env\Scripts\activate

# Activate it (Linux/Mac)
# source bingo_env/bin/activate

pip install opencv-python numpy Pillow pytesseract requests


visiontest.py 
helps measure the region that you want to analyze with the image processing

docker build -t bingo_api .
docker run -p 8000:8000 -v $(pwd)/debug:/app/debug bingo-api