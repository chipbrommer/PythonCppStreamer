#pragma once 
/////////////////////////////////////////////////////////////////////////////////
// @file            eo_interface.h
// @brief           EO interface class declaration
// @author          Chip Brommer
/////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////
//
// Define:
#ifndef EO_INTERFACE_H
#define EO_INTERFACE_H
// 
// Includes:
//          name                    reason included
//          ------------------      ------------------------
#include    <string>                // strings
#include    <fstream>               // file stream
#include    <chrono>                // sleep duration
#include    <thread>                // sleep
#include    <atomic>                // atomic bool
#include    "nlohmann/json.hpp"     // json handling
//
#ifdef _WIN32                       // if Windows -----
#include <winsock2.h>               // sockets 
#include <ws2tcpip.h>               // sockets 
#pragma comment(lib, "ws2_32.lib")  // sockets 
#else                               // else if (Linux) ----
#include <unistd.h>                 // 
#include <arpa/inet.h>              // 
#include <sys/socket.h>             // 
#endif                              // end if 
//
// Other: Convenience declarations to ease code for different OS types. 
#ifndef _WIN32                                      // --- if not windows (Linux) ---
using SOCKET = int;                                 // SOCKET like windows
const int SD_BOTH = SHUT_RDWR;                      // SD_BOTH like windows
#define closesocket(s) close(s)                     // closesocket line windows
using SOCKADDR_IN = sockaddr_in;                    // sockaddr_in to mimic windows
using SOCKADDR = sockaddr;                          // sockaddr to mimic windows
#endif                                              // end if
//      
constexpr int DEFAULT_PORT = 3456;                  // 
const std::string DEFAULT_IP = "127.0.0.1";         // loop back address
constexpr int DEFAULT_TIMEOUT_SECS = 30;            // default timeout for attempting connection
constexpr int BUFFER_SIZE = 800;                    // default buffer size for read
constexpr int DEFAULT_MESSAGE_RATE = 1;             // default rate for python TCP server is 1 Hz
//
/////////////////////////////////////////////////////////////////////////////////

/// @brief A class to spawn/start the Python equivalent and connection. 
class EO_Interface
{
public:
    /// @brief Enum for the connection status of the interface
    enum class ConnectionStatus : int
    {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        CONNECTION_ERROR,
        PYTHON_START_ERROR,
        RECONNECTING,
    };

    // @brief Constructor
    EO_Interface(const std::string& scriptFilePath, const std::string& cameraPort, const std::string& ip = DEFAULT_IP,
        const int port = DEFAULT_PORT, const int timeout = DEFAULT_TIMEOUT_SECS, const int messageRate = DEFAULT_MESSAGE_RATE, 
        std::string videoFilePath = "");

    /// @brief Deconstructor
    ~EO_Interface() {}

    /// @brief Set the timeout for how long to attempt connecting
    /// @param timeout - length of time in seconds
    /// @return true if set successfully, false if failed (typically means script already running)
    bool SetConnectingTimeout(const int timeoutSeconds);

    /// @brief Sets the filepath to forward to the python script for execution
    /// @param videoFilePath - the file path and name for to enable saving the video within the python script
    /// @return true if set successfully, false if failed (typically means script already running)
    bool EnableVideoCapture(const std::string& videoFilePath);

    /// @brief When running on a linux machine with a monitor, it may be desired to visually see the video. Enable that here.
    /// @param onoff - Enable the video dispay from camera to the dispkay monitor
    /// @return true if set successfully, false if failed (typically means script already running)
    bool EnableVideoDisplay(const bool onoff);

    /// @brief Sets the filepath to forward to the python script for execution
    /// @param rate - the desired rate for the data messages coming from the python TCP server
    /// @return true if set successfully, false if failed (typically means script already running)
    bool SetPythonServerMessageRateInHz(const int rate);

    /// @brief Setup the EO Interface for the connection to the python script
    /// @param ip - ip address for the connection
    /// @param port - the port number for the connection
    /// @return true if set successfully, false if failed (typically means script already running)
    bool Setup(const std::string& ip, const int port);

    /// @brief Establishes the connection for this class to the python script
    /// @return true if set successful connection, false if failed
    bool Connect();

    /// @brief - BLOCKING FUNCTION - a working loop for receiving and processing data from the python script
    /// @return false if the server is not connected
    bool Start();

    /// @brief Stops the connection to the Python server
    /// @return false if server not start or on error, true on successful stop
    bool Stop();

    /// @brief Reads data from the the python script
    /// @return string containings the read contents. 
    std::string Read();

    /// @brief Wrate data to the python script
    /// @param data - string of data to write to the python script
    /// @return - false if failed to write, else true
    bool Write(const std::string& data);

    /// @brief Get the current connection status of the client
    /// @return - class enum represented connection status
    ConnectionStatus GetConnectionStatus() const;

private:

    /// @brief Process the received data from the python client
    /// @param data - data received from the python server to be processed
    void ProcessData(const std::string& data);

    /// @brief a function that can be called to attempt reconnection if it was dropped. 
    void Reconnect();

#ifdef _WIN32
    WSADATA             mWsaData;                   //< WSA Data for windows connection
#endif
    std::string         mIpAddress;                 //< Ip address for the client connection
    std::string         mCameraPort;                //< Port for the camera connection to send to the python script
    int                 mPort;                      //< Port number for the client connection
    int                 mMessageRate;               //< Message rate for the python TCP server
    std::string         mScriptFilePath;            //< File path for the python script 
    std::string         mVideoFilePath;             //< Video file path to be forwarded to the python script
    bool                mVideoCaptureEnabled;       //< Flag for video capture being enabled 
    bool                mDisplay;                   //< Flag sent to python script to display the video to monitor
    std::atomic_bool    mStarted;                   //< Flag for the connection being started
    SOCKET              mSocket;                    //< Connection socket
    int                 mTimeout;                   //< Timeout for the connection loop
    char                mReadBuffer[BUFFER_SIZE];   //< Read buffer for reading from the python script server
    long                mRxCount;                   //< Rx Count we have successfully received
    long                mTxCount;                   //< Tx count we have successfully sent
    ConnectionStatus    mConnectionStatus;          //< Enum for the current connection status
};

#endif // EO_INTERFACE_H