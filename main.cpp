#include <iostream>
#include <cstring>
#include <thread>
#include <chrono>

#include "eo_interface.h"

// 0 = run colibri, 1 = build on linux, 2 = build on windows
constexpr int RUN_TYPE = 0;

int main()
{
    // Since I do not compile this on the colibri, I use this
    // flag to change my compilation based on the machine type I am testing with. 
    switch(RUN_TYPE)
    {
        case 0:
            {
                EO_Interface eo("./scripts/ImageTracking.py", "/dev/video0");
                eo.SetPythonServerMessageRateInHz(4);
                eo.EnableVideoCapture("video_output");
                eo.Start();
            }
            break;
        case 1:
            {
                std::string sPath = SCRIPTS_PATH;
                sPath += "/ImageTracking.py";
                EO_Interface eo(sPath, "/dev/video0");
                eo.EnableVideoCapture("videoCapture1");
                eo.SetPythonServerMessageRateInHz(4);
                eo.EnableVideoDisplay(true);
                eo.Start(); 
            }
            break;
        case 2:
            {
                std::string sPath = SCRIPTS_PATH;
                sPath += "/ImageTracking.py";
                EO_Interface eo(sPath, "1");
                eo.EnableVideoCapture("videoCapture1");
                eo.SetPythonServerMessageRateInHz(4);
                eo.EnableVideoDisplay(true);
                eo.Start();
            }
            break;
        default:
            break;
    }

    return 0;
}