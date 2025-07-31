# Use official slim Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install LaTeX packages (the magic fix)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-publishers \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.enableCORS=false"]
