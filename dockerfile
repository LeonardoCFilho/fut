FROM python:3.12-slim

# Install git and bash
RUN apt-get update && apt-get install -y git bash && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository (main branch only)
RUN git clone --branch main --single-branch https://github.com/LeonardoCFilho/fut.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r Arquivos/requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

ENTRYPOINT ["python3", "fut.py"]
CMD ["--help"]