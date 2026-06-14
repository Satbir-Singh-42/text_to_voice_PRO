#!/bin/bash
echo "========================================="
echo "  Text to Voice PRO — Multi-Language"
echo "========================================="
pip3 install gtts pygame -q
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get install -y python3-tk libsdl2-mixer-2.0-0 2>/dev/null || true
fi
python3 text_to_voice_pro.py
