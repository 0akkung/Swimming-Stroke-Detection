# Swimming Stroke Detection

A computer vision project using OpenCV detect swimming strokes in videos.

## Technologies and Libraries

- **Python**: Our programming language.
- **OpenCV**: a real-time optimized Computer Vision library, tools, and hardware.
- **Mediapipe**: An open source, cross-platform, customizable ML solution for live and streaming media.
- **NumPy**: a Python library used for working with arrays.
- **Matplotlib Pyplot**: a collection of functions that make matplotlib work like MATLAB. We use this to plot graphs.

## Getting Started

### Prerequisites
Before you install this program, you must install [**python**](https://www.python.org/downloads/source/) in your computer. This program require python 
**version 3.8 - 3.11** to run Mediapipe.

* To check python version, you can type this command on your terminal.
  ```sh
  python --version
  ```

### Installation

1. Clone the project into your repository
   ```sh
   git clone https://github.com/0akkung/Swimming-Stroke-Detection.git
   ```
2. To install the necessary packages, run
   ```sh
   pip install -r requirements.txt
   ```
3. Run the program
   ```sh
   python main.py
   ```
   
## Progress Report
| Week | Progress                                                                              |
|------|---------------------------------------------------------------------------------------|
| 1    | Installing Python with mediapipe and opencv and testing it                            |
| 2    | Live video tracking using webcam, calculate arms angles making graph using Matplotlib |

## Progress Breakdown

### Week 1

* Installed Python, OpenCV & Mediapipe
* Tested and learned basic on how to use OpenCV and Mediapipe
* Detect body movement using Mediapipe and counting stroke based on both arms angles

### Resources:

1. [OpenCV Course - Full Tutorial with Python](https://www.youtube.com/watch?v=oXlwWbU8l2o&t=974s)
2. [Human body Pose Tracking | Faster Pose Detection on CPU | Pose Estimation | Machine Learning
](https://www.youtube.com/watch?v=0JU3kpYytuQ)
3. [AI Pose Estimation with Python and MediaPipe | Plus AI Gym Tracker Project
](https://www.youtube.com/watch?v=06TE_U21FK4)

### Week 2

* Make temporary timer to visualize elapsed time
* Calculate strokes per minute and stroke per distance
* Detect direction the person in the video is facing (forward and backward)
* Visualize graph for angles of each arms

### Resources:

1. [Set Countdown timer to Capture Image using Python-OpenCV
](https://www.geeksforgeeks.org/set-countdown-timer-to-capture-image-using-python-opencv/)