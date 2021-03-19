cd /home/pi/Programs/FYDP/rpi-hub/
until sudo python3 device.py; do
    echo "Program crashed, restarting." >&2
    sleep 1
done
