import predict_hog as hog

ALG = 'hog' # can be 'hog', 'daisy', 'orb'

def predict(path):
    global ALG
    if ALG.lower() == 'hog':
        print(hog.predict_hog(path))


path='6.jpg'
predict(path)