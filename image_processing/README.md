# impros

## Description

impros.py implements ImageProcessor class for computer vision, namely:
- face detection and localization
- significant facial parts detection (eyes, nose, mouth)
- images manipulation: crop, shift, rotation, mirroring and image-pyramid building

## Installation

Usage of Anaconda package is highly recommended as it covers most of the dependencies

First, install the **dependencies**:

1. `scikit-image` (should go along with Anaconda)
2. `cv2` – opencv3 lib for python (use this for Anaconda: `conda install -c menpo opencv3=3.1.0`)
3. `numpy`
4. `matplotlib`
5. `scipy`

## Usage

Import the module into your project with `from impros import ImageProcessor as impros`

*For now just read methods thorough comments as the reference*

**HOG implementation:**

1. Use *clf_constants.py* as a config file to tune up HOG and classifier params.
2. Run *prep_data.py* with `ALG='HOG'` to make cropped and shifted face images of each image in *./photos* directory and retrieve HOG descriptor for each of them.
3. This will create a csv file inside *./data* directory. Use that file to train a classifier.
4. Load it in *predict.py* with the `path` variable to get classification result.
5. Enjoy your life

**P.S.:** sample classifier is already provided in *./clfs* directory.


