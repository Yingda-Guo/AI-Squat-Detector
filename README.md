# AI-Squat-Detector
AI Training Project #2: Squat Detecor. An improved algorithm to detect squat. The app supports video load and live-camera-streaming. 

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
