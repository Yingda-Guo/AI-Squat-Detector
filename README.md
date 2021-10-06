
# Deep Learning AI Trainer - Squat Counter

Combining Computer Vision with Deep Learning Algorithm, this python application can detect human legs in real-time. Based on the angle changes, the application can detect squat movement and count the number of squats. The applicaiton supports a real-time streaming with low hardware requirement, even without a GPU.

This is a upgrade of [Deep Learning AI Trainer: Weight Lift Counter](https://github.com/Yingda-Guo/Deep-Learning-AI-Trainer-Weight-Lift-Counter) by using more advanced movement detection algorithm.

![squat1](https://user-images.githubusercontent.com/13625416/128951652-95c137cd-9403-423f-b3e4-d9d7ba9f9704.gif)
## Environment Setup

    conda create -n AI-Training python=3.7 
    conda install -n AI-Training tensorflow # Install tensorflow 
    conda install -n AI-Training -c conda-forge opencv # Install opencv
    conda activate AI-Training # Activate virtual environment
    pip install mediapipe # Install mediapipe # install mediapipe
    python -c 'import tensorflow as tf; print(tf.__version__)' # Check setup

## Run App
   

For video file import:
    
    python run.py -v squat_resource/squat0.mp4
For live-camera-streaming:

    python live_streaming.py

## Demo

Video1:

![squat1](https://user-images.githubusercontent.com/13625416/128951657-0c5051a4-e09d-4ec1-b74b-ab71d1543cd4.gif)

Video2:

![squat2](https://user-images.githubusercontent.com/13625416/128952009-516027e6-4b78-4ab8-89a2-adb3ded2b029.gif)

Live-Streaming:

![squat3](https://user-images.githubusercontent.com/13625416/128952367-5c28fc54-8684-4f6b-8bad-b93476d85f48.gif)
