FROM python:3.12-slim

# Install git and bash
RUN apt-get update && apt-get install -y git bash && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository (main branch only)
RUN git clone --branch main --single-branch https://github.com/LeonardoCFilho/fut.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r Arquivos/requirements.txt

# Create a marker file to indicate Docker environment
RUN touch /.dockerenv

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV DOCKER_CONTAINER=true

# Create entrypoint script using printf (more reliable than echo)
RUN printf '#!/bin/bash\n\
echo "Entrypoint called with arguments: $@"\n\
\n\
if [ "$1" = "gui" ]; then\n\
    echo "Starting Streamlit GUI on 0.0.0.0:8501..."\n\
    echo "Current working directory: $(pwd)"\n\
    echo "Available files:"\n\
    ls -la\n\
    \n\
    echo "Available Python files:"\n\
    find . -name "*.py" -type f | head -10\n\
    \n\
    streamlit_file=""\n\
    \n\
    for file in app.py main.py streamlit_app.py fut.py; do\n\
        if [ -f "$file" ]; then\n\
            if grep -q "import streamlit\\|from streamlit" "$file" 2>/dev/null; then\n\
                streamlit_file="$file"\n\
                echo "Found Streamlit app: $file"\n\
                break\n\
            fi\n\
        fi\n\
    done\n\
    \n\
    if [ -z "$streamlit_file" ]; then\n\
        if [ -f "fut.py" ]; then\n\
            streamlit_file="fut.py"\n\
            echo "Using fut.py as Streamlit file (fallback)"\n\
        else\n\
            echo "No Streamlit file found!"\n\
            exit 1\n\
        fi\n\
    fi\n\
    \n\
    echo "Starting Streamlit with file: $streamlit_file"\n\
    exec streamlit run "$streamlit_file" \\\n\
        --server.address=0.0.0.0 \\\n\
        --server.port=8501 \\\n\
        --server.headless=true \\\n\
        --browser.gatherUsageStats=false\n\
else\n\
    echo "Running regular Python application..."\n\
    exec python3 fut.py "$@"\n\
fi\n' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]