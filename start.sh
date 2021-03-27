cd /home/pi/Programs/FYDP/
amixer set Headphone 100%
until sudo venv/bin/python3.7 rpihub/device.py --tts --tts_data; do
    echo "Program crashed, restarting." >&2
    sleep 1
done
