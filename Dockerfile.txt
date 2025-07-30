# Use an official Python image as the base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Update the package list and install a more comprehensive set of LaTeX packages
# This is the crucial change to fix the compilation error
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-publishers \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements file
COPY requirements.txt .

# Install the Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's code
COPY . .

# Tell Render that your app runs on port 8501
EXPOSE 8501

# The command to run your Streamlit app
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.enableCORS=false"]