#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== FUT Application Docker Installer ===${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Build the Docker image
echo -e "${YELLOW}Building fut application...${NC}"
if ! docker build -t fut-app .; then
    echo -e "${RED}Error: Failed to build Docker image${NC}"
    exit 1
fi

# Create the wrapper script
echo -e "${YELLOW}Installing fut command...${NC}"
sudo tee /usr/local/bin/fut > /dev/null << 'EOF'
#!/bin/bash

# Check if the first argument is 'gui'
if [ "$1" = "gui" ]; then
    echo "Starting GUI mode..."
    echo "Web interface will be available at: http://localhost:8501"
    echo "Press Ctrl+C to stop the server"
    echo ""
    docker run --rm -it -p 8501:8501 fut-app gui
else
    # For all other commands, run normally
    docker run --rm -it fut-app "$@"
fi
EOF

# Make it executable
if ! sudo chmod +x /usr/local/bin/fut; then
    echo -e "${RED}Error: Failed to make fut command executable${NC}"
    exit 1
fi

echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${GREEN}Usage:${NC}"
echo "  fut --help          # Show help"
echo "  fut gui            # Start web interface at http://localhost:8501"
echo "  fut template       # Create template"
echo "  fut configuracoes  # Configuration menu"
echo "  fut <other-args>   # Run other commands"
echo ""
echo -e "${YELLOW}Note: The 'fut' command is now available system-wide${NC}"