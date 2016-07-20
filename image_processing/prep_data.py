import prep_data_hog as hog

ALG = 'hog' # can be 'hog', 'daisy', 'orb'

if ALG.lower() == 'hog':
    root = './photos'
    hog.prep_data_hog(root)