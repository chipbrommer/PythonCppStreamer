#///////////////////////////////////////////////////////////////////////////////
# @file            MiniStrike_Tracker.py
# @brief           MiniStrike tracker script for handling video interfacing
#                  with an EO camera for navigation assistance
# @author          Chip Brommer
#///////////////////////////////////////////////////////////////////////////////

import datetime
import json
import argparse
import sys
import time
import cv2
import platform
import os
import subprocess
from modules.udp_client import UDPClient
from modules.tcp_server import TCPServer

# Define the version number
MAJOR_VERSION = 0
MINOR_VERSION = 0
BUILD_NUMBER = 6
VERSION = f"{MAJOR_VERSION}.{MINOR_VERSION}.{BUILD_NUMBER}"
DEFAULT_UDP_CLIENT_PORT = 2468  # Default udp client port
DEFAULT_TCP_SERVER_PORT = 3456  # Default tcp server port
PUBLISH_FREQUENCY_HZ = 1        # Desired message rate from the TCP server

# @brief - A function to handle connecting to the camera 
# @param device - device location for the camera
# @return - The connection to the camera
def connect_camera(device: str):
    try:
        # Detect if platform is windows, port will need to be an integer
        if platform.system() == "Windows":
            device = int(device)
        print(f"Opening camera port: {device}")
        camera = cv2.VideoCapture(device)
        return camera
    except Exception as e:
        print(f"Error opening camera port: {e}")
        sys.exit(2)

# @brief - A function to handle processing of a frame for desired items
# @param frame - video frame to be processed
# @param save - Boolean for if the frame is being written to a file
# @param file_out - file handle for writing out the video
# @param display - flag to display video to monitor
# @return azimuth, elevation, distance of the tracked item
def process_frame(frame, save: bool, file_out, display: bool, udp_client: UDPClient):
    azimuth = float(0.0)
    elevation = float(0.0)
    distance = float(0.0)
 
    # @TODO process frame for desired items and draw box. 

    # Display the frame if enabled
    if display | udp_client.is_display_enabled():
        cv2.imshow('MiniStrike Video Stream', frame)
    
    # Write the frame to the output video file if --save flag is provided
    if save:
        if file_out.isOpened():
            file_out.write(frame)

    return azimuth, elevation, distance

# @brief - A function to handle running of the TCP server 
# @param camera - the connection to the camera
# @param udp_client - the instance of the udp client
# @param tcp_server - the instance of the tcp server
# @param save - the program args.save 
# @param out_file - the filename/location to write video. 
# @param display - flag to display video to monitor
def run_loop(camera, udp_client, tcp_server, save = False, out_file = None, display = False):
    # Get camera properties
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    # Resize frame to lower resolution
    resized_width = int(frame_width / 2)
    resized_height = int(frame_height / 2)
    
    # Define the codec and create a VideoWriter object if --save flag is provided
    if save:
        writer = cv2.VideoWriter_fourcc(*'MJPG')
        file_out = cv2.VideoWriter(out_file, writer, fps, (resized_width,resized_height))
        print(f"Writing video to {out_file}")
    else:
        file_out = ""    

    try:
        # Calculate the time interval between messages
        time_interval = 1.0 / PUBLISH_FREQUENCY_HZ
        print(f"Configured to sending at {time_interval} seconds : {PUBLISH_FREQUENCY_HZ} Hz")
        lastSend = datetime.datetime.now()
        
        # Wait until at least one connection is established on the TCP server
        while tcp_server.get_num_connections() == 0:
            time.sleep(1)  # Sleep for 1 second before checking again
        
        # While loop to execute while we have a connection
        while tcp_server.get_num_connections() > 0 and camera.isOpened():
            # Read a new frame - break if we failed to read
            goodRead, frame = camera.read()
            if not goodRead:
                print("Failed to read camera frame")
                break
            
             # Resize the frame
            resized_frame = cv2.resize(frame, (resized_width, resized_height))

            # Send resized frame for image processing and receive an azimuth, elevation, and distance
            azimuth, elevation, distance = process_frame(resized_frame, save, file_out, display, udp_client)

            # Get the current timestamp of the day
            now = datetime.datetime.now()

            # If its time to send another update mesage, send it
            if (now - lastSend).total_seconds() >= time_interval:
                lastSend = now
                midnight = datetime.datetime.combine(now.date(), datetime.time())

                # Get the microseconds and then convert to seconds so we have msec precision. 
                microseconds = (now - midnight).microseconds 
                seconds = (now - midnight).seconds + microseconds / 1_000_000  

                data = {
                    'timestamp': seconds,           # timestamp of message sending
                    'azimuth': azimuth,             # Azimuth of the tracked item 
                    'elevation': elevation,         # Elevation of the tracked item 
                    'distance': distance            # Disatnce of the tracked item
                }

                # Convert data to JSON format
                json_data = json.dumps(data)

                # Send JSON data over the socket
                tcp_server.send_message(json_data.encode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:       
        # if we were saving to file, release the file 
        if save:
            file_out.release()

# @brief - Prints out the received args
def print_arguments(args):
    print("Received arguments:")
    
    if args.device:
        print(f"\tDevice: {args.device}")

    if args.save is not None:
        print(f"\tSave File: {args.save[0]}")
    else:
        print("\tNo save file specified.")

    if args.rate:
        print(f"\tTCP Server Rate: {args.rate}")

    if args.visual:
        print("\tVideo Display Enabled")

    if args.stream is not None:
        if args.stream == '':
            print("\tStream: IP address is required for streaming.")
        else:
            print(f"\tStream: {args.stream}")

            if args.multicast:
                print("\tMulticast Enabled")

    print("\n")
   
# @brief - Attempts to find a camera based on the OS
# @return - None if no camera, else a path to found camera
def find_camera_device_path():
    system = platform.system()
    if system == 'Windows':
        # On Windows, use Get-PnpDevice PowerShell command to list cameras
        try:
            result = subprocess.run(['powershell', 'Get-PnpDevice | Where-Object { $_.Class -eq "Camera" }'], capture_output=True, text=True)
            output = result.stdout
            
            # Extract camera paths from output
            lines = output.split('\n')
            camera_paths = [line.split()[-1] for line in lines if line.strip() and 'USB' in line]
            
            if camera_paths:
                return camera_paths[0]  # Return the first camera path found
            
        except Exception as e:
            print(f"Error while finding camera path: {e}")
            return None
        
    elif system == 'Linux':
        # On Linux, check for connected USB cameras using /dev/v4l/by-id
        try:
            by_id_dir = '/dev/v4l/by-id'
            
            # Get the list of symbolic links in /dev/v4l/by-id
            links = os.listdir(by_id_dir)
            
            # Find the first symbolic link that contains 'usb' in its name
            for link in links:
                if 'usb' in link:
                    # Construct the full path of the camera device
                    camera_path = os.path.join(by_id_dir, link)
                    # Resolve the symbolic link to get the actual device path
                    actual_path = os.path.realpath(camera_path)
                    return actual_path
                
        except Exception as e:
            print(f"Error while finding camera path: {e}")
            return None

        # If no USB camera found in v4l, iterate over possible camera paths
        # Check /dev/video0 to /dev/video9
        for i in range(10):  
            path = f"/dev/video{i}"
            if os.path.exists(path):
                return path
    else:
        print("ERROR: Unsupported operating system")
        return None

    print("ERROR: Camera not found")
    return None

# @brief - Main function for the application
def main():
    # Declare PUBLISH_FREQUENCY_HZ as global
    global PUBLISH_FREQUENCY_HZ  
    
    # Stream items
    stream_enabled = False
    stream_ip = ""
    stream_port = 0
    out_file = ""

    # Print a start up message
    print("\n=========================================")
    print("   MiniStrike EO Camera Target Tracker   ")
    print(f"            Version {VERSION}           ")
    print("=========================================\n\n")

    # Create an argument parser
    parser = argparse.ArgumentParser(description="Python script for MiniStrike to capture video from the received port for the camera connection.\n"
                                     + f" This script then acts as a TCP server on port {DEFAULT_TCP_SERVER_PORT} to trasmit data back to\n"
                                     + " connected clients at a desired message rate.")

    # Allowed Arguments
    parser.add_argument('--device', '-d',nargs=1, metavar='DEVICE_PATH', help='Specify the device location for the camera connection')
    parser.add_argument('--save', '-s', nargs=1, metavar='OUTPUT_FILE', help='Specify the output file for saving data')
    parser.add_argument('--rate', '-r', default=1, type=int, metavar='RATE_HZ', help='Specify the TCP message rate in Hz')
    parser.add_argument('--visual', '-v', action='store_true', help='Enable video output showing to screen')
    parser.add_argument('--stream', '-t', nargs=2, metavar=('IP', 'PORT'), help='Enable streaming to the specified IP address and port')
    parser.add_argument('--multicast', '-m', action='store_true', help='Enable multicast for steaming')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Check if any arguments were received
    if any(arg != parser.get_default(key) for key, arg in vars(args).items()):
        if args.save:
            out_file = args.save[0] + ".avi"  # Ensure the file extension is included

        if args.rate:
            PUBLISH_FREQUENCY_HZ = float(args.rate)

        if args.visual:
            displayEnabled = True
            
        if args.stream:
            if args.stream != '':
                stream_enabled = True
                stream_ip = args.stream[0]
                stream_port = args.stream[1]
                
    # If a device was received, use it, else attempt to find a camera 
    if args.device:
        camera_path = args.device
    else:
        camera_path = find_camera_device_path()

    # If here and we still do not have a camera path, exit    
    if camera_path is None:
        print("Error: No camera path received or found. Exiting")
        sys.exit(1)

    # Attempt to connect the camera
    camera = connect_camera(camera_path)

    try:
        # Check if the camera connection is open
        if camera.isOpened():
            print(f"Camera connected on at {camera_path}")
        else:
            print(f"Failed to open camera at {camera_path}")
            sys.exit(2)
            
        # Start the UDP Client
        udp_client = UDPClient('0.0.0.0', int(DEFAULT_UDP_CLIENT_PORT))
        udp_client.start()
        
        # Start the TCP Server
        tcp_server = TCPServer('0.0.0.0', int(DEFAULT_TCP_SERVER_PORT), None)
        tcp_server.start()

        # Run the main loop
        run_loop(camera, udp_client, tcp_server, args.save, out_file, args.visual)

    finally:
        # Clean up
        camera.release()
        cv2.destroyAllWindows()
        udp_client.stop()
        tcp_server.stop()
    
# @brief - Entry point - calls main function
if __name__ == "__main__":
    main()