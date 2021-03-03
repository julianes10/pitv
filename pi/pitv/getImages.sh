# Launch screenshoot
SCR_FILE="/opt/pipapi/pipapi/static_pipapi/pg_screen.png"
CAM_FILE="/opt/pipapi/pipapi/static_pipapi/pg_photo.jpg"
rm -f $SCR_FILE $CAM_FILE

SCR_CMD="sudo -u pi -- /opt/pipapi/telegramBOT/screenshoot2.sh $SCR_FILE"
CAM_CMD="/opt/pipapi/picam/raspistillForce.sh -a 12 -n -w 320 -h 240 -awb auto -ex auto -vf -hf -o  $CAM_FILE"

# Generating screen file
$SCR_CMD
# Generating cam file
$CAM_CMD



