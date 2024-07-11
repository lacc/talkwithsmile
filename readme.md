https://qengineering.eu/install%20pytorch%20on%20raspberry%20pi%205.html


sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip libjpeg-dev libopenblas-dev libopenmpi-dev libomp-dev
#sudo -H pip3 install setuptools==58.3.0
sudo -H pip3 install Cython

apt-get install portaudio19-dev


python -m venv name-env
source name-env/bin/activate

pip install setuptools numpy Cython
pip install requests

python -m pip install --upgrade pip
python -m pip cache purge
python -m pip install torch torchvision tochaudio

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip3 install torchaudio --index-url https://download.pytorch.org/whl/cpu


pip install
---
Cython
SpeechRecognition
pygame
gtts
openai
PyPDF2
docx2txt
python-pptx
pyaudio