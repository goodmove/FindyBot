## Usage

**HOG implementation:**

1. Use *image_processing/clf_constants.py* as a config file to tune up HOG and classifier params.
2. Run *prep_data.py* with `ALG='HOG'` to make cropped and shifted face images of each image in *<path_to_photos>* directory and retrieve HOG descriptor for each of them.
3. This will create a csv file inside *image_processing/data* directory. Use that file to train a classifier.
4. Load it in *predict.py* with the `path` variable to get classification result.
5. Enjoy your life