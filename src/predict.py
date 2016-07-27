import src.image_processing.hog as hog
# import src.image_processing.predict_daisy as daisy

ALG = 'hog' # can be 'hog', 'daisy', 'orb'

def predict(path=None, link=None):
    global ALG
    if ALG.lower() == 'hog':
        # print(hog.predict_hog(path))
        return hog.predict(path=path, link=link)
    # elif ALG.lower() == 'daisy':
    #     print(hog.predict_daisy(path=path, link=link))
    #     # return hog.predict_hog(path=path, link=link)


# path = ''
# predict(path)