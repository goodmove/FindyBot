import image_processing.prep_data_hog as hog

ALG = 'hog' # can be 'hog', 'daisy', 'orb'

if ALG.lower() == 'hog':
    root = './image_processing/photos'
    hog.prep_data_hog(root)