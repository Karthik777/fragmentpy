import os
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2.cv as cv
import cv2
import create_pics_from_facebook as cf
import numpy as np

CASCADE = "haarcascade_frontalface_alt.xml"
face_dir = "face_root_directory/"

min_size = (20, 20)
IMAGE_SCALE = 2
haar_scale = 1.2
min_neighbors = 3
haar_flags = 0
label_dict = {}
variable_faces = []
import random

class LabelStore():
  def __init__(self,id,name):
    #self.model = model
    #self.model = cv2.createFisherFaceRecognizer()
    self.name = name
    self.id =id

  def name(self):
    return self.name

  def id(self):
    return id



def images_from_target_person1(person, max_pics, recognizers):
    id_counter = 1
    for recognizer in recognizers:
        label_dict[recognizer][id_counter] = person
    picture_dir = face_dir + person + "/"
    all_pictures = os.listdir(picture_dir)
    variable_pic = random.choice(all_pictures)
    variable_faces.append(picture_dir + variable_pic)
    all_pictures.remove(variable_pic)
    random.shuffle(all_pictures)
    all_pictures = all_pictures[:max_pics]

    for picture_name in all_pictures:
        full_path = picture_dir + picture_name
        try:
            face = cv.LoadImage(full_path, cv2.IMREAD_GRAYSCALE)
        except IOError:
            continue
        yield face[:, :], full_path
    id_counter += 1

def images_from_target_person(person, max_pics, recognizers):

    id_counter = 1
    for recognizer in recognizers:
        label_dict[recognizer][id_counter] = person
    picture_dir = face_dir + person + "/"
    all_pictures = os.listdir(picture_dir)
    variable_pic = random.choice(all_pictures)
    variable_faces.append(picture_dir + variable_pic)
    all_pictures.remove(variable_pic)
    random.shuffle(all_pictures)
    all_pictures = all_pictures[:max_pics]

    for picture_name in all_pictures:
        full_path = picture_dir + picture_name
        try:
            face = cv.LoadImage(full_path, cv2.IMREAD_GRAYSCALE)
        except IOError:
            continue
        yield face[:, :], id_counter , full_path
    id_counter += 1


def images_from_random_people(all_people, max_pics, recognizer):
    num_to_train = 8
    id_counter = 2
    random.shuffle(all_people)
    all_people = all_people
    num_training_added = 0
    for person in all_people:
        label_dict[recognizer][id_counter] = person
        if "DS_STORE" in face_dir + person:
            continue
        try:
            all_pictures = os.listdir(face_dir + person + "/")
        except:
            continue
        if len(all_pictures) < 20:
            continue
        random.shuffle(all_pictures)
        all_pictures = all_pictures[:max_pics]
        for picture_name in all_pictures:
            picture_dir = face_dir + person + "/"
            full_path = picture_dir + picture_name
            try:
                face = cv.LoadImage(full_path, cv2.IMREAD_GRAYSCALE)
            except IOError:
                continue
            yield face[:, :], id_counter , full_path
        num_training_added += 1
        if num_training_added > num_to_train:
            break
        id_counter += 1


def train_recognizers(recognizers,labellist):

    for recognizer in recognizers:
        label_dict[recognizer] = {}
    images = []
    labels = []
    num_faces = 0
    max_pics = 50

    all_people = os.listdir(face_dir)
    person = random.choice(all_people)
    all_people.remove(person)
    for face, id_counter, path in images_from_target_person(person, max_pics, recognizers):
        images.append(np.asarray(face))
        labels.append(id_counter)
        labellist.append(LabelStore(id_counter,path))
    for recognizer in recognizers:
        image_copy = list(images)
        label_copy = list(labels)
        for face, id_counter, path in images_from_random_people(all_people, max_pics, recognizer):
            image_copy.append(np.asarray(face))
            label_copy.append(id_counter)
            labellist.append(LabelStore(id_counter,path))
            num_faces += 1

        image_array = np.asarray(image_copy)
        label_array = np.asarray(label_copy)
        recognizer.train(image_array, label_array)
    return recognizers


def iterate_over_random_people():
    num_people = 5
    people_names = os.listdir(face_dir)
    random.shuffle(people_names)
    people_to_use = people_names[:num_people]
    # variable faces is a full image path
    for person in people_to_use:
        picture_dir = face_dir + person + "/"
        try:
            all_pictures = os.listdir(picture_dir)
        except:
            continue
        if len(all_pictures) == 0:
            continue
        some_picture = random.choice(all_pictures)
        full_path = picture_dir + some_picture
        variable_faces.append(full_path)
    for filename in variable_faces:
        try:
            image = cv.LoadImage(filename, cv2.IMREAD_GRAYSCALE)
        except IOError:
            continue
        yield image[:, :], filename


def directory_name_to_display_name(path):
    path = path.replace(face_dir, "")
    path = path.split("/")[0]
    path = "_".join(path.split("_")[:2])
    return path


def predict_image(face):
    global variable_faces
    num_iterations = 300
    matches_this_iteration = 0
    for j in xrange(num_iterations):
        try:
            listlabel=[]
            recognizers = []
            variable_faces = []
            num_recognizers = 3
            for j in xrange(num_recognizers):
                lbh_recognizer = cv2.createLBPHFaceRecognizer()
                recognizers.append(lbh_recognizer)
            recognizers = train_recognizers(recognizers,listlabel)
            average_confidence = 0
            CONFIDENCE_THRESHOLD = 100.0
            labels = []
            for lbh_recognizer in recognizers:
                [label, confidence] = lbh_recognizer.predict(np.asarray(face))
                average_confidence += confidence
                labels.append(label)
            average_confidence /= num_recognizers
            if len(set(labels))==1 and average_confidence < CONFIDENCE_THRESHOLD:
                    matches_this_iteration += 1
                    if matches_this_iteration == 3:
                        return (directory_name_to_display_name(findlabel(listlabel,labels[0])))
        except:
            continue
    return None

def findlabel(list,labelid):
    for i in list:
        if i.id == labelid:
            return i.name



if __name__ == '__main__':
    total_matches = 0
    false_positives = 0
    misses = 0
    num_iterations = 300
    matches_this_iteration = 0
    for j in xrange(num_iterations):
        try:
            listlabel=[]
            recognizers = []
            variable_faces = []
            num_recognizers = 3
            for j in xrange(num_recognizers):
                lbh_recognizer = cv2.createLBPHFaceRecognizer()
                recognizers.append(lbh_recognizer)
            recognizers = train_recognizers(recognizers,listlabel)

            all_people = os.listdir(face_dir)

            person= all_people[3]
            test_people = list(images_from_target_person1(person,200,recognizers))
            # target person is the established individual that we're trying to
            # match against
            target_person = test_people[0][1]
            target_path = target_person
            target_person = directory_name_to_display_name(target_person)

            # For this test, the known person is always the first person in the list,
            # so we match based on the idea that the correct estimation is when the algorithm picks the first element
            # first_item = True

            false_positives_this_iteration = 0
            average_confidence = 0
            CONFIDENCE_THRESHOLD = 100.0
            for face, actual_name in test_people:
                # for this test, we know that test_people[0][0] is the face of
                # the target person.  If this algorithm works, then it will
                # validate that assertion
                path = actual_name
                actual_name = directory_name_to_display_name(actual_name)
                labels = []
                for lbh_recognizer in recognizers:
                    [label, confidence] = lbh_recognizer.predict(np.asarray(face))
                    print(label,findlabel(listlabel,label))
                    average_confidence += confidence
                    labels.append(label)
                average_confidence /= num_recognizers
                # this is just asserting that an ID of 1 has been found for
                # every recognizer
                if len(set(labels)) == 1 and average_confidence < CONFIDENCE_THRESHOLD:
                    # if first_item:
                        matches_this_iteration += 1
                        if matches_this_iteration > 2:
                            print (findlabel(listlabel,labels[0]))
                            print "SUCCESSFUL MATCH",
                            print "%s looks like the target, %s.  Confidence %s" % (path, target_path, average_confidence)
                else:
                    # this case is reached sometimes since we're using
                    # random data and I didn't protect against that
                    # duplication
                    if actual_name == target_person:
                        total_matches += 1
                        # print "DIDNT MATCH",
                    else:
                        false_positives_this_iteration += 1
                        print "FALSE POSITIVE",

                # else:
                #     # A miss is okay since we err on the side of uncertainty
                #     # rather than create a false positive
                #     if first_item:
                #         misses += 1
                # first_item = False

            # this IF statement exists to catch the latter case below
            # if sum([false_positives_this_iteration, matches_this_iteration]) == 1:
            #     false_positives += false_positives_this_iteration
            #     total_matches += matches_this_iteration
            # elif false_positives_this_iteration >= 1 and matches_this_iteration == 1:
            #     # TODO: this case means that multiple people were matches to
            #     # the same person.  In this case, you can just use the one with
            #     # greater confidence and this generally produces the correct
            #     # results
            #     total_matches += 1
        except:
            continue
    # print "Total matches: %s" % total_matches
    # print "False positives: %s" % false_positives
    # print "Misses: %s" % misses
    print(matches_this_iteration)

    # all_people = os.listdir(face_dir)
    # person = random.choice(all_people)
    #
    # test_people = list(images_from_target_person1(person, 50, recognizers))