#///////////////////////////////////////////////////////////////////////////////
# @file            MiniStrike_Tracker.py
# @brief           MiniStrike tracker script for handling video interfacing
#                  with an EO camera for navigation assistance
# @author          Chip Brommer
#///////////////////////////////////////////////////////////////////////////////

import datetime
import socket
import json
import time
import argparse
import sys

# Define the version number
VERSION = "0.0.1"
DEFAULT_SERVER_PORT = 3456      # Default server port to server on

# @brief - A function to handle connecting to the camera 
# @param port - the port location of the camera
# @return - The connection to the camera
def connect_camera(port):
    try:
        print(f"Opening camera port: {port}")
    except:
        print(f"Error opening camera port")
        sys.exit(1)

# @brief - A function to handle running of the TCP server 
# @param camera - the connection to the camera
# @param ip - the ip to bind on
# @param port - the port to bind on
def run_server(camera, ip, port):
    # Create a socket to communicate with MiniStrike OFS
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket
        server_address = (ip, port) 
        server_socket.bind(server_address)
        
        # Listen for incoming connections
        server_socket.listen(1)

        # Get the local IP address and port
        local_ip, local_port = server_socket.getsockname()

        print(f"Waiting for MiniStrike connection on {local_ip}:{local_port}...")
        
        # Blocks until it accepts the incoming connection from MiniStrike
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        
        # Set the publish time frequency (in Hz)
        publish_frequency = 1 

        # Calculate the time interval between messages
        time_interval = 1.0 / publish_frequency
        
        # While loop to execute while we have a connection
        while client_socket.fileno() != -1:
            # Get the current timestamp of the day
            now = datetime.datetime.now()
            midnight = datetime.datetime.combine(now.date(), datetime.time())
            seconds = (now - midnight).seconds
            
            data = {
                'timestamp': seconds,           # timestamp of message sending
                'latitude': 37.7749,            # @todo with actual latitude
                'longitude': -122.4194,         # @todo with actual longitude
                'azimuth': -1.234,              # @todo with actual azimuth
                'elevation': 1.5678             # @todo with actual elevation
            }

            # Convert data to JSON format
            json_data = json.dumps(data)

            try:
                # Send JSON data over the socket
                client_socket.sendall(json_data.encode('utf-8'))
                
            except (BrokenPipeError, OSError):
                print("Client disconnected")
                client_socket.close()
                
            # Wait for the specified time interval before publishing again
            time.sleep(time_interval)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Proper clean up
        print("Closing.")
        server_socket.close()

# @brief - Main function for the application
def main():
    # Print a start up message
    print("=========================================")
    print("   MiniStrike EO Camera Target Tracker   ")
    print(f"            Version {VERSION}        ")
    print("=========================================\n\n")

    # Create an argument parser
    parser = argparse.ArgumentParser(description="MiniStrike EO Camera Handler")

    # Add arguments for port and save file
    parser.add_argument('--port', help='Specify the port for the camera connection', required=True)
    parser.add_argument('--save', help='Specify the output file for saving data')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Print received arguments
    print("Received arguments:")
    print(f"\tPort: {args.port}")
    print(f"\tSave File: {args.save}")
    print("\n")

    # Open the camera port
    camera = connect_camera(args.port)

    try:
        # Check if the port is open
        #if camera.is_open:
        #    print(f"Camera connected on port {args.port}")
        #else:
        #    print(f"Failed to open camera port {args.port}")

        # Run the server
        run_server(camera, '0.0.0.0', int(DEFAULT_SERVER_PORT))

    finally:
        # Close the camera port
        # camera.close()
        print(f"Closing camera.")
    
# @brief - Entry point - calls main function
if __name__ == "__main__":
    main()