from utils import annotation
from keras_retinanet import models
from keras_retinanet.utils.image import preprocess_image,resize_image
from numpy import expand_dims
import os
from cv2 import imread
from keras.backend import clear_session
from sys import stderr




def predictAndWrite(parameterDict : dict):

    #model_save_dir specifies save directory of model.
    #score_threshold score of acceptance of a prediction.
    #images_path specifies the directory of input images of model.
    #backbone_name specifies the backbone_name parameter of models.load_model function.
    #label_dict specifies the label name of given number
    #overwrite is a boolean value which will be binded to AnnotationWriter constructor's overwrite parameter.
    #data_path specifies the folder which XML's will be stored.
    #For example
    # {0:"Rbc",etc.}

    imagesPath = parameterDict["images_path"]
    model_save_dir = parameterDict["model_save_dir"]
    scoreThreshold = parameterDict.get("score_threshold", 0.5)
    backboneName = parameterDict.get("backbone_name", "resnet50")
    labelDict = parameterDict.get("label_dict", {0: "lbl"})
    overwrite = parameterDict.get("overwrite", False)
    dataPath = parameterDict.get("data_path", os.path.join(imagesPath, "data"))




    allImgs = [os.path.join(imagesPath, img) for img in os.listdir(imagesPath)
               if img.endswith(".jpg")]


    model = models.load_model(model_save_dir,
                      backbone_name=backboneName, convert=True)
    for imgName in allImgs:
        realImg = imread(imgName)
        img = realImg.copy()
        img = preprocess_image(img)
        img, scale = resize_image(img, min_side=1590, max_side=1590 * 4 / 3)
        boxes, scores, labels = model.predict_on_batch(expand_dims(img, axis=0))
        boxes = boxes.reshape(boxes.shape[1:])
        boxes /= scale
        boxes = boxes.astype(int)
        labels = labels.reshape(labels.shape[1:])
        scores = scores.reshape(scores.shape[1:])
        xmlName = os.path.basename(imgName).split(".")[0] + ".xml"
        annoWriter = annotation.AnnotationWriter(
            os.path.join(dataPath,xmlName), overwrite=overwrite)
        annoWriter.compile()


        for box, label, score in zip(boxes, labels, scores):
            if label == -1:
                continue
            elif score < scoreThreshold:
                continue
            else:
                annoWriter.addObject(labelDict[label], *box)

        annoWriter.write()

    clear_session()

def predictAndSplittedWrite(parameterDict : dict):

    #images_path specifies the directory which images are stored.
    #model_save_dir specifies the path of the model snapshot.
    #merge_dir specifies the directory which recommendation XML's and found XML's are merged.
    #unfound_dir specifies the directory which unfound cells' XML's are stored.
    #recomendation_dir specifies the directory which recommendation XML's are stored.
    #data_path is the directory of the XML data .



    labelDict = parameterDict.get("label_dict", None)
    model_save_dir = parameterDict["model_save_dir"]
    imagesPath = parameterDict["images_path"]
    mergeDir = parameterDict.get("merge_dir",None)
    unfoundDir = parameterDict.get("unfound_dir",None)
    recommendationDir = parameterDict.get("recomendation_dir",None)
    dataPath = parameterDict.get("data_path", os.path.join(imagesPath, "data"))
    csvPath = parameterDict.get("csv_path",None)
    backboneName = parameterDict.get("backbone_name", "resnet50")
    scoreThreshold = parameterDict.get("score_threshold", 0.2)


    assert(not csvPath and not labelDict) , "You should have to specify at least one of csvPath or labelDict"


    if csvPath :
        if labelDict :
            stderr.write("Given parameter label_dict will be overwritten by csvPath labels.")

        labelDict = dict()
        with open(csvPath) as file:
            for line in file.readlines():
                line = line.split(",")
                labelDict[line[0]] = line[1]


    dispatcher = annotation.AnnotationDispatcher()
    allImgs = [os.path.join(imagesPath, img) for img in os.listdir(imagesPath)
               if img.endswith(".jpg")]

    model = models.load_model(model_save_dir,
                              backbone_name=backboneName, convert=True)
    for imgName in allImgs:
        img = imread(imgName)

        img = preprocess_image(img)
        img, scale = resize_image(img, min_side = 1590, max_side = 1590*4/3)
        boxes, scores, labels = model.predict_on_batch(expand_dims(img, axis=0))

        boxes /= scale

        boxes = boxes.reshape(boxes.shape[1:])
        boxes = boxes.astype(int)
        labels = labels.reshape(labels.shape[1:])
        scores = scores.reshape(scores.shape[1:])
        controlList = []
        counter = 0
        for i in range(len(labels)):
            if labels[i] == -1:
                continue
            if scores[i] <= scoreThreshold:
                continue
            controlList.append([])
            controlList[counter].append(labelDict[labels[i]])

            for elem in boxes[i]:
                controlList[counter].append(elem)

            counter += 1


        xmlName = os.path.basename(imgName)[:-3] + "xml"
        anno = annotation.AnnotationReader(os.path.join(".", "goruntuler-part1v2", "data", xmlName),
                                           fileName=True)
        disjointChildren, childrenCannotBeFound = dispatcher(controlList, anno)
        disjointAnnoWriter = annotation.AnnotationWriter.buildEmptyXML(os.path.join(recommendationDir,
                                                                                    xmlName))
        disjointAnnoWriter.compile()
        disjointAnnoWriter.addObjects(disjointChildren)

        disjointAnnoWriter.write()
        cannotBeFoundAnnoWriter = annotation.AnnotationWriter.buildEmptyXML(os.path.join(unfoundDir,
                                                                                         xmlName))
        cannotBeFoundAnnoWriter.compile()
        cannotBeFoundAnnoWriter.addObjects(childrenCannotBeFound)
        cannotBeFoundAnnoWriter.write()

        mergedData = annotation.AnnotationWriter(os.path.join(dataPath,
                                                              xmlName),
                                                 isFileName=True, writeDirectory=os.path.join(mergeDir, xmlName))
        mergedData.compile()
        mergedData.addObjects(disjointChildren)
        mergedData.write()
