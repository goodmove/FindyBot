import src.image_processing.hog as hog

ALG = 'hog' # can be 'hog', 'daisy', 'orb'

if ALG.lower() == 'hog':
    root = 'src/image_processing/photos'
    hog.prep_data(root)