#include <iostream>
#include <cstring>
#include <thread>
#include <chrono>

#define TESTING_CLASS

#ifndef TESTING_CLASS

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#include <tchar.h>
#else
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#endif

#include "nlohmann/json.hpp"

using json = nlohmann::json;

int main() {
#ifdef _WIN32
    // Windows-specific code
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Failed to initialize Winsock" << std::endl;
        return 1;
    }
#endif

    // Create a socket
    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == -1)
    {
        std::cout << "Failed to create socket!\n";
        exit(0);
    }

    // Specify the server address and port
    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;

#ifdef _WIN32
    // Windows-specific code
    if (InetPton(AF_INET, _T("127.0.0.1"), &(serverAddress.sin_addr)) <= 0) {
#else
    // Linux-specific code
    if (inet_pton(AF_INET, "127.0.0.1", &(serverAddress.sin_addr)) <= 0) {
#endif
        std::cerr << "Invalid address or address family" << std::endl;
        return 1;
    }

    serverAddress.sin_port = htons(3456);  // Use the desired port


    std::atomic_bool connected = false;

    // Attempt to connect to the server
    while (!connected) {
        int rtn = connect(clientSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress)); 

        if (rtn >= 0)
        {
            std::cout << "Connection successful!" << std::endl;
            connected = true;
        }
        else
        {
            std::cerr << "Server unavailable - Retrying in 1 second..." << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    // Receive and process JSON structures
    while (true)
    {
        char buffer[1024];
        int bytesRead = recv(clientSocket, buffer, sizeof(buffer), 0);

        if (bytesRead > 0)
        {
            // Convert received data to std::string
            std::string receivedData(buffer, bytesRead);

            // Parse JSON
            try
            {
                json jsonData = json::parse(receivedData);

                // Access keys: timestamp, latitude, longitude
                if (jsonData.contains("timestamp") &&
                    jsonData.contains("latitude") &&
                    jsonData.contains("longitude") &&
                    jsonData.contains("azimuth") &&
                    jsonData.contains("elevation"))
                {
                    double timestamp = jsonData["timestamp"];
                    double latitude = jsonData["latitude"];
                    double longitude = jsonData["longitude"];
                    double azimuth = jsonData["azimuth"];
                    double elevation = jsonData["elevation"];

                    // Do something with the parsed data
                    std::cout << "Timestamp: " << timestamp << "\n";
                    std::cout << "Latitude: " << latitude << "\n";
                    std::cout << "Longitude: " << longitude << "\n";
                    std::cout << "Azimuth: " << azimuth << "\n";
                    std::cout << "Elevation: " << elevation << std::endl;
                }
                else
                {
                    std::cout << "JSON data does not contain required keys." << std::endl;
                }
            }
            catch (const std::exception& e)
            {
                std::cerr << "Error parsing JSON: " << e.what() << std::endl;
            }
        }
        else {
            // Handle disconnection or error
            std::cout << "Server disconnected or error occurred." << std::endl;
            break;
        }
    }

    // Close the socket
#ifdef _WIN32
    closesocket(clientSocket);
    WSACleanup();
#else
    close(clientSocket);
#endif

    return 0;
    }

#else

#include "eo_interface.h"

constexpr bool RUN_ON_COLIBRI = false;

int main()
{
    // Since I do not compile this on the colibri, I use this
    // flag to change my compilation and copy the desired files over. 
    if (RUN_ON_COLIBRI == true)
    {
        EO_Interface eo("./scripts/ImageTracker.py", "/dev/video0");
        eo.Start();
    }
    else
    {
        std::string sPath = SCRIPTS_PATH;
        sPath += "/ImageTracker.py";
        EO_Interface eo(sPath, "/dev/video0");
        eo.Start();
    }

    return 0;
}
#endif