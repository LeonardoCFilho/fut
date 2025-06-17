#!/bin/bash

# Build the Docker image
echo "Building fut application..."
docker build -t fut-app .

# Create the wrapper script
echo "Installing fut command..."
sudo tee /usr/local/bin/fut > /dev/null << 'EOF'
#!/bin/bash
docker run --rm -it fut-app "$@"
EOF

# Make it executable
sudo chmod +x /usr/local/bin/fut

echo "Installation complete! You can now use: fut <args>"