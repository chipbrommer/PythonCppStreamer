# To change called script: 
    
## If running on Windows:
    1. Add the desired script to the "scripts" directory.
    2. Modify the main.cpp and change the called script here: sPath += "/ImageTracker.py";
        NOTE: MAKE SURE YOU KEEP THE "/"
    

## Independant gstreamer commands
SENDER COMMANDS:
gst-launch-1.0 v4l2src device=/dev/video0 ! 'image/jpeg, format=YUY2, width=1280, height=960' ! jpegdec ! videoconvert ! jpegenc ! 'image/jpeg, format=YUY2, width=1280, height=960, framerate=60/1' ! tee name=t \
t. ! queue ! 'image/jpeg, format=YUY2, width=1280, height=960, framerate=60/1' ! rtpjpegpay ! udpsink host=192.168.1.112 port=5305 \
t. ! queue ! 'image/jpeg, format=YUY2, width=1280, height=960, framerate=60/1' ! jpegdec ! videoconvert ! jpegenc ! avimux ! filesink location=text.avi

gst-launch-1.0 v4l2src device=/dev/video0 ! 'image/jpeg, format=YUY2, width=1280, height=960' ! jpegdec ! videoconvert ! jpegenc ! 'image/jpeg, format=YUY2, width=1280, height=960, framerate=60/1' ! tee name=t \
t. ! queue ! 'image/jpeg, format=YUY2, width=1280, height=960, framerate=60/1' ! rtpjpegpay ! udpsink host=224.1.1.1 port=5305 auto-multicast=true multicast-iface=eth0 \
t. ! queue ! 'image/jpeg, format=YUY2, width=1280, height=960, framerate=60/1' ! jpegdec ! videoconvert ! jpegenc ! avimux ! filesink location=text.avi


RECEIVER COMMAND: 
gst-launch-1.0 -v udpsrc port=5305 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)jpeg" ! rtpjpegdepay ! decodebin ! videoconvert ! autovideosink sync=false

gst-launch-1.0 -v udpsrc multicast-group=224.1.1.1 port=5305 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)jpeg" ! rtpjpegdepay ! decodebin ! videoconvert ! autovideosink sync=false
