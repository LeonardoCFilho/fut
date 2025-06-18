#!/bin/bash

# Check if the first argument is 'gui'
if [ "$1" = "gui" ]; then
    echo "Starting GUI mode..."
    echo "Web interface will be available at: http://localhost:8501"
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Stop any existing containers using port 8501
    echo "Checking for existing containers on port 8501..."
    existing_containers=$(docker ps -q --filter "publish=8501")
    if [ ! -z "$existing_containers" ]; then
        echo "Stopping existing containers: $existing_containers"
        docker stop $existing_containers
        docker rm $existing_containers
        sleep 2
    fi
    
    # Start container with explicit port mapping
    echo "Starting container with command:"
    echo "docker run --rm --name fut-gui-$(date +%s) -p 8501:8501 fut-app gui"
    
    container_name="fut-gui-$(date +%s)"
    
    # Run the container
    docker run --rm \
        --name "$container_name" \
        -p 8501:8501 \
        fut-app gui
        
else
    # For all other commands, run normally
    echo "Running command: docker run --rm -it fut-app $@"
    docker run --rm -it fut-app "$@"
fi