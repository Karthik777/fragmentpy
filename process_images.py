__author__ = 'srlaxminaarayanan'
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2.cv as cv
import cv2
import os
from PIL import Image
import json
import numpy as np
import urllib2
from StringIO import StringIO
from io import BytesIO
import match_faces as mf
import base64
CASCADE = "haarcascade_frontalface_alt.xml"
OUTPUT_DIRECTORY = "face_root_directory/"

IMAGE_SCALE = 2
haar_scale = 1.2
min_neighbors = 3
min_size = (20, 20)
haar_flags = 0
normalized_face_dimensions = (100, 100)


def convert_rgb_to_bgr(open_cv_image):
    try:
        new_image = cv.CreateImage((open_cv_image.width, open_cv_image.height), cv.IPL_DEPTH_8U, open_cv_image.channels)
        cv.CvtColor(open_cv_image, new_image, cv.CV_RGB2BGR)
    except:
        print "Error converting image to BGR"
        return None
    return new_image


def download_photo_as_open_cv_image(photo_url):
    try:
        img = urllib2.urlopen(photo_url).read()
    except urllib2.HTTPError:
        # possible case of 404 on image
        print "Error fetching image: %s" % photo_url
        return None
    img = StringIO(img)
    pil_image = Image.open(img)
    try:
        open_cv_image = cv.fromarray(np.array(pil_image))[:, :]
    except TypeError:
        print "unsupported image type"
        return None
    open_cv_image = convert_rgb_to_bgr(open_cv_image)
    return open_cv_image

def process_image(base64string):
    image_string = BytesIO(base64.b64decode(base64string))
    image = Image.open(image_string)
    open_cv_image = cv.fromarray(np.array(image))[:, :]
    open_cv_image = convert_rgb_to_bgr(open_cv_image)
    return get_face_in_stream_photo(open_cv_image)


def normalize_image_for_face_detection(img):
    gray = cv.CreateImage((img.width, img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / IMAGE_SCALE),
                   cv.Round(img.height / IMAGE_SCALE)), 8, 1)
    if img.channels > 1:
        cv.CvtColor(img, gray, cv.CV_BGR2GRAY)
    else:
        # image is already grayscale
        gray = cv.CloneMat(img[:, :])
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
    cv.EqualizeHist(small_img, small_img)
    return small_img


def _is_in_bounds(region_of_interest, constraint_coordinate, open_cv_image):
    '''
    Region of interest: (x, y, w, h)
    Constraint Coordinate: x and y as a percent from left and top
    '''
    constraint_coordinate = (constraint_coordinate[0] / 100.0, constraint_coordinate[1] / 100.0)
    translated_coordinate = (open_cv_image.width * constraint_coordinate[0], open_cv_image.height * constraint_coordinate[1])
    x_min = region_of_interest[0]
    x_max = region_of_interest[2] + x_min
    y_min = region_of_interest[1]
    y_max = region_of_interest[3] + y_min

    if x_min <= translated_coordinate[0] <= x_max and y_min <= translated_coordinate[1] <= y_max:
        return True
    return False


def normalize_face_size(face):
    normalized_face_dimensions = (100, 100)
    face_as_array = np.asarray(face)
    resized_face = cv2.resize(face_as_array, normalized_face_dimensions)
    resized_face = cv.fromarray(resized_face)
    return resized_face


def normalize_face_histogram(face):
    face_as_array = np.asarray(face)
    equalized_face = cv2.equalizeHist(face_as_array)
    equalized_face = cv.fromarray(equalized_face)
    return equalized_face


def normalize_face_color(face):
    gray_face = cv.CreateImage((face.width, face.height), 8, 1)
    if face.channels > 1:
        cv.CvtColor(face, gray_face, cv.CV_BGR2GRAY)
    else:
        # image is already grayscale
        gray_face = cv.CloneMat(face[:, :])
    return gray_face[:, :]


def normalize_face_for_save(face):
    face = normalize_face_size(face)
    face = normalize_face_color(face)
    face = normalize_face_histogram(face)
    return face


def face_detect_on_photo(img, constraint_coordinate):
    cascade = cv.Load(CASCADE)
    faces = []

    small_img = normalize_image_for_face_detection(img)
    faces_coords = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                        haar_scale, min_neighbors, haar_flags, min_size)
    for ((x, y, w, h), n) in faces_coords:
        if constraint_coordinate is not None and not _is_in_bounds((x, y, w, h), constraint_coordinate, small_img):
            continue
        pt1 = (int(x * IMAGE_SCALE), int(y * IMAGE_SCALE))
        pt2 = (int((x + w) * IMAGE_SCALE), int((y + h) * IMAGE_SCALE))
        face = img[pt1[1]:pt2[1], pt1[0]: pt2[0]]
        face = normalize_face_for_save(face)
        faces.append(face)
    return faces


#  @task

def get_face_in_photo(photo_url, service_id, picture_name, name, x, y):
    photo_in_memory = download_photo_as_open_cv_image(photo_url)

    # TODO: make the network call asynchronous as well with a callback function
    if photo_in_memory is None:
        return
    if x is None and y is None:
        # case for profile picture that isnt necessarily tagged
        # only return a result if exactly one face is in the image
        faces = face_detect_on_photo(photo_in_memory, None)
        if len(faces) == 1:
            save_face(name, service_id, faces[0], picture_name)
        return
    for face in face_detect_on_photo(photo_in_memory, (x, y)):
        save_face(name, service_id, face, picture_name)


def get_face_in_stream_photo(photo_in_memory):
    # photo_in_memory = download_photo_as_open_cv_image(photo_url)
    results=[]
    # TODO: make the network call asynchronous as well with a callback function
    if photo_in_memory is None:
        return

    faces = face_detect_on_photo(photo_in_memory, None)
    if len(faces) == 1:
        result = mf.predict_image(faces[0])
        if result is None:
            return ("Not Completed",result);
        return ("Completed", result);
    return


def save_profile_photos(imageQuery, name):
    all_photos = imageQuery
    picture_count = 0
    photo_url = all_photos
    picture_name = "profile_%s" % picture_count
    get_face_in_photo(photo_url, None, picture_name, name, None, None)
    picture_count += 1


def _create_folder_name(name, service_id):
    if service_id is None:
       service_id=""
    split_name = name.split(" ")
    first = split_name[0]
    last = split_name[len(split_name) - 1]
    folder_name = "%s_%s_%s" % (last, first, service_id)
    return folder_name


def save_face(name, service_id, face, picture_name):
    folder_name = _create_folder_name(name, service_id)
    if not os.path.exists(OUTPUT_DIRECTORY + folder_name):
        os.makedirs(OUTPUT_DIRECTORY + folder_name)
    filename = "%s.jpg" % picture_name
    full_path = OUTPUT_DIRECTORY + folder_name + "/" + filename
    try:
        cv2.imwrite(full_path, np.asarray(face))
    except UnicodeEncodeError:
        print "Did not save picture because of unicode exception"
        # TODO: Use django smart_bytes to save the image here
    print "Saving: %s" % full_path

