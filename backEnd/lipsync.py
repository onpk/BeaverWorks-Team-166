# make sure to run this in google colab, haven't tested on anywhere else

### make sure that CUDA is available in Edit -> Nootbook settings -> GPU
!nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
!update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python3.8 2
!update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python3.9 1
!sudo apt install python3.8

!sudo apt-get install python3.8-distutils

!python --version

!apt-get update

!apt install software-properties-common

!sudo dpkg --remove --force-remove-reinstreq python3-pip python3-setuptools python3-wheel

!apt-get install python3-pip

print('Git clone project and install requirements...')
!git clone https://github.com/Winfredy/SadTalker &> /dev/null
%cd SadTalker
!export PYTHONPATH=/content/SadTalker:$PYTHONPATH
!python3.8 -m pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
!apt update
!apt install ffmpeg &> /dev/null
!python3.8 -m pip install -r requirements.txt
!rm -rf checkpoints
!bash scripts/download_models.sh

import requests
from PIL import Image
from io import BytesIO
import glob
import os
import sys
from base64 import b64encode
from IPython.display import display, HTML

def capture_image():
    try:
        response = requests.get("https://thispersondoesnotexist.com/")
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print("An error occurred while capturing the image:", e)
        return None

def run_sadtalker_with_image(img):
    try:
        img_path = 'captured_image.png'
        img.save(img_path)
        # Create the 'results' directory if it doesn't exist
        if not os.path.exists('./results'):
            os.makedirs('./results')
        !python3.8 inference.py --driven_audio ./examples/driven_audio/RD_Radio31_000.wav \
                   --source_image {img_path} \
                   --result_dir ./results --still --preprocess full --enhancer gfpgan
        return True
    except Exception as e:
        print("An error occurred while running SadTalker:", e)
        return False

def display_result():
    try:
        if os.path.exists('./results/'):
            results = sorted(os.listdir('./results/'))
            if results:
                mp4_files = glob.glob('./results/*.mp4')
                if mp4_files:
                    mp4_name = mp4_files[0]
                    mp4 = open('{}'.format(mp4_name),'rb').read()
                    data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
                    print('Display animation: {}'.format(mp4_name), file=sys.stderr)
                    display(HTML("""
                      <video width=256 controls>
                            <source src="%s" type="video/mp4">
                      </video>
                      """ % data_url))
                else:
                    print("No .mp4 files found in the 'results' directory.")
            else:
                print("The 'results' directory is empty.")
        else:
            print("The 'results' directory does not exist.")
    except Exception as e:
        print("An error occurred while displaying the result:", e)

def main():
    source_image = capture_image()
    if source_image:
        display(source_image)
        if run_sadtalker_with_image(source_image):
            display_result()
        else:
            print("Failed to run SadTalker.")
    else:
        print("Failed to capture the image.")

if __name__ == "__main__":
    main()
