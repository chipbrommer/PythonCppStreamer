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
import cv2
import math

# Define the version number
VERSION = "0.0.3"
SENSOR_SIZE_DIAGONAL_MM = 7.66  # Diagonal size of the camera sensor in mm
FOCAL_LENGTH_MM = 15.0          # Focal length of the lens in mm
DEFAULT_SERVER_PORT = 3456      # Default server port to server on
PUBLISH_FREQUENCY_HZ = 1        # desired message rate from the TCP server

# @brief - A function to handle connecting to the camera 
# @param port - port for the camera
# @return - The connection to the camera
def connect_camera(port):
    try:
        print(f"Opening camera port: {port}")
        camera = cv2.VideoCapture(port)
        return camera
    except Exception as e:
        print(f"Error opening camera port: {e}")
        sys.exit(2)

# @brief - A function to calculate FOV - assume a square camera sensor for ease
# @param sensor_size_diagonal_mm - The diagonal size of the sense
# @param focal_length_mm - The focal lenght of the lense
# @return - the horizontal and vertical field of view
def calculate_fov(sensor_size_diagonal_mm, focal_length_mm):
    fov_horizontal = 2 * math.degrees(math.atan(sensor_size_diagonal_mm / (2 * focal_length_mm)))
    fov_vertical = fov_horizontal 
    return fov_horizontal, fov_vertical

# @brief - A function to handle running of the TCP server 
# @param camera - the connection to the camera
# @param ip - the ip to bind on
# @param port - the port to bind on
# @param save - the program args.save 
# @param out_file - the port to bind on
def run_server(camera, ip, port, save = False, out_file = None):
    # Calculate FOV
    #fov_horizontal, fov_vertical = calculate_fov(SENSOR_SIZE_DIAGONAL_MM, FOCAL_LENGTH_MM)
    #print(f"Horizontal FOV: {fov_horizontal:.2f} degrees")
    #print(f"Vertical FOV: {fov_vertical:.2f} degrees\n")

    # Get camera properties
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    # Resize frame to lower resolution (e.g., 1080p)
    resized_width = int(frame_width / 2)
    resized_height = int(frame_height / 2)
    
    # Define the codec and create a VideoWriter object if --save flag is provided
    if save:
        writer = cv2.VideoWriter_fourcc(*'MJPG')
        file_out = cv2.VideoWriter(out_file, writer, fps, (resized_width,resized_height))
        print(f"Writing video to {out_file}")

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
        
        # Calculate the time interval between messages
        time_interval = 1.0 / PUBLISH_FREQUENCY_HZ
        print(f"TCP Server sending at {time_interval} seconds")
        lastSend = datetime.datetime.now()
        
        # While loop to execute while we have a connection
        while client_socket.fileno() != -1 and camera.isOpened():
            # Read a new frame - break if we failed to read
            goodRead, frame = camera.read()
            if not goodRead:
                print("Failed to read camera frame")
                break
            
             # Resize the frame
            resized_frame = cv2.resize(frame, (resized_width, resized_height))

            # Define azimuth and elevation 
            azimuth = float(0.0)
            elevation = float(0.0)

            # Display the frame
            cv2.imshow('Object Tracking - Video Stream', resized_frame)
            
            # Write the frame to the output video file if --save flag is provided
            if save and file_out.isOpened():
                file_out.write(resized_frame)
            
            # Get the current timestamp of the day
            now = datetime.datetime.now()

            # if its time to send another update mesage, send it
            if (now - lastSend).total_seconds() >= time_interval:
                lastSend = now
                midnight = datetime.datetime.combine(now.date(), datetime.time())
                seconds = (now - midnight).seconds

                data = {
                    'timestamp': seconds,           # timestamp of message sending
                    'latitude': 37.7749,            # @todo with actual latitude
                    'longitude': -122.4194,         # @todo with actual longitude
                    'azimuth': azimuth,             # @todo with actual azimuth
                    'elevation': elevation          # @todo with actual elevation
                }

                # Convert data to JSON format
                json_data = json.dumps(data)

                try:
                    # Send JSON data over the socket
                    client_socket.sendall(json_data.encode('utf-8'))

                except (BrokenPipeError, OSError):
                    print("Client disconnected")
                    client_socket.close()

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Proper clean up
        print("Closing.")
        server_socket.close()
        
        # if we were saving to file, release the file 
        if save:
            file_out.release()

# @brief - Main function for the application
def main():
    # Declare PUBLISH_FREQUENCY_HZ as global
    global PUBLISH_FREQUENCY_HZ

    # Print a start up message
    print("=========================================")
    print("   MiniStrike EO Camera Target Tracker   ")
    print(f"            Version {VERSION}           ")
    print("=========================================\n\n")

    # Create an argument parser
    parser = argparse.ArgumentParser(description="MiniStrike EO Camera Handler")

    # Add arguments for port and save file
    parser.add_argument('--port', help='Specify the port for the camera connection', required=True)
    parser.add_argument('--save', nargs=1, metavar='<output_file>', help='Specify the output file for saving data')
    parser.add_argument('--rate', default=1, type=float, help='Specify the TCP message rate in Hz')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Print received arguments
    print("Received arguments:")
    print(f"\tPort: {args.port}")
    if args.save:
        print(f"\tSave File: {args.save}")
        out_file = args.save + ".avi"
    else:
        out_file = ""
    print("\n")

    if args.rate:
        PUBLISH_FREQUENCY_HZ = float(args.rate)
        print(f"received rate: {args.rate}")

    # Open the camera port
    camera = connect_camera(args.port)

    try:
        # Check if the camera connection is open
        if camera.isOpened():
            print(f"Camera connected on port {args.port}")
        else:
            print(f"Failed to open camera port {args.port}")
            sys.exit(3)

        # Run the server
        run_server(camera, '0.0.0.0', int(DEFAULT_SERVER_PORT), args.save, out_file)

    finally:
        # Clean up
        camera.release()
        cv2.destroyAllWindows()
    
# @brief - Entry point - calls main function
if __name__ == "__main__":
    main()