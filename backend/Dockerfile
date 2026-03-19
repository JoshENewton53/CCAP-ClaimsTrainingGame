FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Flan-T5 into the image so it never re-downloads at runtime
RUN python -c "from transformers import T5ForConditionalGeneration, T5Tokenizer; T5Tokenizer.from_pretrained('google/flan-t5-base'); T5ForConditionalGeneration.from_pretrained('google/flan-t5-base')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /ai_models/models

EXPOSE 5000

CMD ["python", "app.py"]
