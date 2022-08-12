import json
from flask import Flask, request, send_file, redirect
from  flask_caching import Cache
import image_reader
import random
from image_reader import file_paths
from collections import Counter

image_dictionary = {}
tagged_images = {}
inverted_dict = {}

cache = Cache()


app = Flask(__name__)

app.config['CACHE_TYPE'] = 'simple'

cache.init_app(app)

url = "http://127.0.0.1:5000/home"

# opens all files in Image Folder and stores it in a cache
@app.route('/')
@cache.cached(timeout=0)
def load():

    # open and store images in image_dictionary using file names as keys
    image_reader.image_reader(image_dictionary)
    print("Done loading")
    print(image_dictionary)

    # populate tagged_images
    tagged_images[file_paths[0]] = ['banana','yellow']
    tagged_images[file_paths[1]] = ['broccoli','green']
    tagged_images[file_paths[2]] = ['chipmunk','brown']
    tagged_images[file_paths[3]] = ['elephant','grey']
    tagged_images[file_paths[4]] = ['L-block-left','grey', 'shape']
    tagged_images[file_paths[5]] = ['L-block-right','grey', 'shape']
    tagged_images[file_paths[6]] = ['square-block','yellow','grey', 'shape']

    # invert images and tags
    global inverted_dict
    inverted_dict = image_reader.invert_tags(tagged_images)
    
    return redirect(url)


@app.route('/home', methods =["GET", "POST"])
def home():
    if request.method == "POST":
       # getting input with name = img in HTML form
       image_request = request.form.get("img")
       image_file = image_dictionary[image_request]
       return return_file(image_file)
    return '<form action=http://127.0.0.1:5000/home method="post"><label for="img">Name:</label><br><input type="text" id="img" name="img"><br><button type="submit">Enter</button>'
 
def return_file(img):
    return send_file(img)  

@app.route('/search')
def search():
    
    # get tags and separate them into a list
    tags = request.args.get('tags')
    all_tags = tags.split(",")

    image_files_all = []

    # images are in path form, not file form
    # adds all images with the tags to a single list
    # might be slow if there are lots of images under a single tag
    for tag in all_tags:
        for img in inverted_dict[tag]:
            image_files_all.append(img)

    # if there is more than 1 tag
    # counts number of occurences of each image in image_files_all 
    # keeps only images that occur more than once because they fall under both tags
    if len(all_tags)>1:
        counts = Counter(image_files_all)
        image_files_dupids = [img for img in counts if counts[img] > 1]
        return json.dumps(image_files_dupids)
    else:
        return json.dumps(image_files_all)

    # pass file name into image_dictionary to get path to image
if __name__ == '__main__':  
    app.run()

