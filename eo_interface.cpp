/////////////////////////////////////////////////////////////////////////////////
// @file            eo_interface.cpp
// @brief           EO interface class implementation
// @author          Chip Brommer
/////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////
//
// Includes:
//          name                    reason included
//          ------------------      ------------------------
#include    "eo_interface.h"        // class header
#include    <iostream>              // console io
//
/////////////////////////////////////////////////////////////////////////////////


EO_Interface::EO_Interface(const std::string& scriptFilePath, const std::string& cameraPort, const std::string& ip,
    const int port, const int timeoutSeconds, const int messageRate, const std::string videoFilePath)
    : mScriptFilePath(scriptFilePath), mCameraPort(cameraPort), mIpAddress(ip),
    mPort(port), mTimeout(timeoutSeconds), mMessageRate(messageRate), mVideoFilePath(videoFilePath),
    mVideoCaptureEnabled(false), mDisplay(false), mStarted(false), mSocket(-1), mReadBuffer{},
    mRxCount(0), mTxCount(0), mConnectionStatus(ConnectionStatus::DISCONNECTED)
{
    // If we received a desired path for the video output saving, 
    // then enable the flag for passing to the python script. 
    if (!mVideoFilePath.empty()) mVideoCaptureEnabled = true;

    // If windows, initialize the wsa data
#ifdef _WIN32
    mWsaData = {};
#endif
}

bool EO_Interface::SetConnectingTimeout(const int timeoutSeconds)
{
    // Prevent if already connected. 
    if (mStarted)
    {
        return false;
    }

    mTimeout = timeoutSeconds;
    return mTimeout == timeoutSeconds;
}

bool EO_Interface::EnableVideoCapture(const std::string& videoFilePath)
{
    // Prevent if already connected. 
    if (mStarted)
    {
        return false;
    }

    mVideoFilePath = videoFilePath;
    mVideoCaptureEnabled = true;
    return mVideoCaptureEnabled;
}

bool EO_Interface::EnableVideoDisplay(const bool onoff)
{
    // Prevent if already connected. 
    if (mStarted)
    {
        return false;
    }

    mDisplay = onoff;
    return mDisplay == onoff;
}

bool EO_Interface::SetPythonServerMessageRateInHz(const int rate)
{
    // Prevent if already connected. 
    if (mStarted)
    {
        return false;
    }

    mMessageRate = rate;
    return mMessageRate == rate;
}

bool EO_Interface::Setup(const std::string& ip, const int port)
{
    // Prevent if already connected. 
    if (mStarted)
    {
        return false;
    }

    mIpAddress = ip;
    mPort = port;
    return mIpAddress == ip && mPort == port;
}

bool EO_Interface::Connect()
{
    mConnectionStatus = ConnectionStatus::CONNECTING;

    // Initialize Winsock for Windows
#ifdef _WIN32
    if (WSAStartup(MAKEWORD(2, 2), &mWsaData) != 0)
    {
        std::cerr << "[EO_iFace] Failed to initialize Winsock\n";
        mConnectionStatus = ConnectionStatus::CONNECTION_ERROR;
        return false;
    }
#endif

    // Create a command based on the OS type. This prevents the python script from
    // taking over the current console output. 
    std::string command;
#ifdef _WIN32
    command = "start cmd /c python ";
#else
    if(mDisplay)
        command = "gnome-terminal --window -- python3 ";
    else
        command = "python3 ";
#endif

    // Append the received path and the arguemnts needed here for the full command
    command += mScriptFilePath + " --port " + mCameraPort + " --rate " + std::to_string(mMessageRate);

    if (mDisplay)
    {
        command += " --display";
    }

    if (mVideoCaptureEnabled)
    {
        command += " --save " + mVideoFilePath;
    }

    // For linux, redirect the console output and errors to /dev/null and add
    // an '&' to the end of the command instructing it to run in the background. 
#ifndef _WIN32
    command += " > /dev/null 2>&1 &";
#endif

    // Execute the Python script with appropriate arguments
    std::cout << "[EO_iFace] Executing command: " << command << "\n";
    int result = system(command.c_str());

    if (result == 0)
    {
        std::cout << "[EO_iFace] Command executed successfully\n";
    }
    else
    {
        std::cerr << "[EO_iFace] Command execution failed with code: " << result << "\n";
        mConnectionStatus = ConnectionStatus::PYTHON_START_ERROR;
        return false;
    }

    // Attempt to create the socket for communication
    mSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (mSocket < 0)
    {
        std::cerr << "[EO_iFace] Error creating socket\n";
        mConnectionStatus = ConnectionStatus::CONNECTION_ERROR;
        return false;
    }

    sockaddr_in serverAddress{};
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(mPort);

    if (inet_pton(AF_INET, mIpAddress.c_str(), &serverAddress.sin_addr) <= 0)
    {
        std::cerr << "[EO_iFace] Invalid address / Address not supported\n";
        closesocket(this->mSocket);
        mConnectionStatus = ConnectionStatus::CONNECTION_ERROR;
        return false;
    }

    // Attempt to connect to the python script
    time_t startTime = std::time(nullptr);
    while (std::time(nullptr) - startTime <= mTimeout)
    {
        int result = connect(mSocket, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress));

        // Check for success
        if (result == 0)
        {
            std::cout << "[EO_iFace] Connection successful\n";
            mStarted = true;
            mConnectionStatus = ConnectionStatus::CONNECTED;
            return mStarted;
        }
        else
        {
            // Connection still in progress, continue
            std::this_thread::sleep_for(std::chrono::seconds(1));
            std::cout << "[EO_iFace] Server not found, re-attempting...\n";
            continue;
        }
    }

    // Connection attempt timed out
    std::cerr << "[EO_iFace] Connection attempt timed out\n";
    closesocket(this->mSocket);
    mConnectionStatus = ConnectionStatus::CONNECTION_ERROR;
    return false;
}

bool EO_Interface::Start()
{
    if (!mStarted && !Connect())
    {
        return false;
    }

    while (mStarted)
    {
        std::string data(Read());

        if (data != "")
        {
            ProcessData(data);
        }
    }

    return true;
}

bool EO_Interface::Stop()
{
    if (!mStarted)
    {
        return false;
    }

    if (!closesocket(mSocket))
    {
#ifdef _WIN32
        int err = WSAGetLastError();
#else
        int err = errno;
#endif
        std::cerr << "[EO_iFace] Error closing socket: " << err << "\n";
        return false;
    }

#ifdef _WIN32
    if (WSACleanup() != 0)
    {
        int err = WSAGetLastError();
        std::cerr << "[EO_iFace] Error cleaning up Winsock: " << err << "\n";
        return false;
    }
#endif

    mStarted = false;
    mConnectionStatus = ConnectionStatus::DISCONNECTED;
    return true;
}

std::string EO_Interface::Read()
{
    if (!mStarted)
    {
        return std::string();
    }

    // Receive data from the connection
    int bytesRead = recv(mSocket, mReadBuffer, sizeof(mReadBuffer), 0);
    if (bytesRead > 0)
    {
        std::string receivedData(mReadBuffer, bytesRead);
        mRxCount++;
        return receivedData;
    }
    else if (bytesRead == 0)
    {
        // Server disconnected
        std::cerr << "[EO_iFace] Server disconnected\n";
        mConnectionStatus = ConnectionStatus::RECONNECTING;
        Reconnect(); // Call function to handle reconnection
    }
    else if (bytesRead < 0)
    {
#ifdef _WIN32
        int err = WSAGetLastError();

        if (err == WSAECONNRESET)
        {
#else
        int err = errno;

        if (err == ECONNRESET)
        {
#endif
            // Connection reset by remote host - attempt reconnect
            std::cerr << "[EO_iFace] Connection reset by remote host\n";
            Reconnect();
        }
        else
        {
            std::cerr << "[EO_iFace] Error reading from socket: " << err << "\n";
        }

        }

    return std::string();
    }

bool EO_Interface::Write(const std::string & data)
{
    if (!mStarted)
    {
        return false;
    }

    // Send data over the connection
    int bytesSent = send(mSocket, data.c_str(), static_cast<int>(data.size()), 0);

    if (bytesSent == static_cast<int>(data.size()))
    {
        // Data sent successfully
        mTxCount++;
        return true;
    }
    else if (bytesSent < 0)
    {
#ifdef _WIN32
        int err = WSAGetLastError();
#else
        int err = errno;
#endif
        std::cerr << "[EO_iFace] Error writing to socket: " << err << "\n";
    }

    // Default return / partial return
    return false;
}

EO_Interface::ConnectionStatus EO_Interface::GetConnectionStatus() const
{
    return mConnectionStatus;
}

void EO_Interface::ProcessData(const std::string & data)
{
    // Attempt to parse the data as Json we are looking for.
    try
    {
        nlohmann::json jsonData = nlohmann::json::parse(data);

        std::string out(std::to_string(mRxCount) + " :: ");

        // Access keys individually and append to the 'out' string
        if (jsonData.contains("timestamp"))
        {
            double timestamp = jsonData["timestamp"];
            out += "Timestamp: " + std::to_string(timestamp) + " ";
        }

        if (jsonData.contains("latitude"))
        {
            double latitude = jsonData["latitude"];
            out += "Latitude: " + std::to_string(latitude) + " ";
        }

        if (jsonData.contains("longitude"))
        {
            double longitude = jsonData["longitude"];
            out += "Longitude: " + std::to_string(longitude) + " ";
        }

        if (jsonData.contains("azimuth"))
        {
            double azimuth = jsonData["azimuth"];
            out += "Azimuth: " + std::to_string(azimuth) + " ";
        }

        if (jsonData.contains("elevation"))
        {
            double elevation = jsonData["elevation"];
            out += "Elevation: " + std::to_string(elevation) + " ";
        }

        if (jsonData.contains("distance"))
        {
            double distance = jsonData["distance"];
            out += "Distance: " + std::to_string(distance) + " ";
        }

        std::cout << out << "\n";
    }
    catch (const std::exception& e)
    {
        std::cerr << "[EO_iFace] Error parsing JSON: " << e.what() << std::endl;
    }
}

void EO_Interface::Reconnect()
{
    mConnectionStatus = ConnectionStatus::DISCONNECTED;

    // Stop the current connection
    if (Stop())
    {
        std::cerr << "[EO_iFace] Stopped previous connection\n";
    }
    else
    {
        std::cerr << "[EO_iFace] Error stopping previous connection\n";
    }

    // Attempt to reconnect once
    if (Connect())
    {
        std::cerr << "[EO_iFace] Reconnected successfully\n";
    }
    else
    {
        std::cerr << "[EO_iFace] Reconnection attempt failed\n";
        Stop();
    }
}