FROM python:3.11-slim

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository (main branch only)
RUN git clone --branch main --single-branch https://github.com/LeonardoCFilho/fut.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "fut.py"]
CMD ["--help"]