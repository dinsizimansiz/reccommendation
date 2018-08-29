# Rigid import from the website.
#
# https://lxml.de/tutorial.html
#
from xml.dom .minidom import parseString as parseXML


try:
    from lxml import etree

except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                import cElementTree as etree
            except ImportError:
                try:
                    import elementtree.ElementTree as etree
                except ImportError:
                    print("Cannot be imported.")
                    exit(1)

import os

class AnnotationReader(object):\

    #
    #
    # @params{file is whether string or file pointer.}
    # @params{fileName opens a file called str(file) if fileName is true.}
    #
    #
    #

    def __init__(self,file,fileName = False):

        if type(file) == str and fileName:
            #Open as file
            self.file = file
            fp = open(file, "r")
            self.string = fp.read()
        elif type(file) == str and not fileName:
            #xml string
            self.string = file

        elif hasattr(file, "__class__") and str(file.__class__) == "<class '_io.TextIOWrapper'>":
            self.string = file.read()


        else:
            raise TypeError("Parameter file can be file pointer , string or filename.You have given {}".format(type(file)))


        self.root = etree.fromstring(self.string)


    def __str__(self):
        return self.root.tostring(self.root)

    def __repr__(self):
        return self.__str__(self)

    def getRoot(self):
        return self.root



class AnnotationWriter(object):
    #
    # @params{file} : name of a have had readen file or a string or file wrapper.
    # @params{fileName} : fileName checks for given parameter file is
    # a name of a read file or a string.
    #

    def __init__(self,
                 file,
                 isFileName = False,
                 writeDirectory = None,
                overwrite=False):


        assert(overwrite or writeDirectory),"You should define a " \
                                                     "write directory if " \
                                                     "don't want to overwrite."



        if AnnotationWriter.isFileWrapper(file):

            with file as fp:
                self.string = fp.read()

            if overwrite:
                self.writeDirectory = file.name

            else:
                self.writeDirectory = writeDirectory


        elif type(file) == str:
            if isFileName:

                with open(file) as fp:
                    self.string = fp.read()

                if overwrite:
                    self.writeDirectory = file

                else:
                    self.writeDirectory = writeDirectory

            else:
                self.string = file
                self.writeDirectory = writeDirectory
        else:
            self.string = file
            self.writeDirectory = writeDirectory


    #
    #
    # Set properties should be called with non-trivial parameters
    # if and only if given string is empty
    #
    def compile(self):
        if not self.string:
            curDir = os.getcwd()
            self.root = etree.Element("annotation")
            folder = etree.Element("folder")
            folder.text = self.folder if hasattr(self, "folder") else os.path.basename(
                os.path.dirname(self.writeDirectory))
            self.root.append(folder)
            filename = etree.Element("filename")
            filename.text = self.filename if hasattr(self, "filename") else os.path.basename(self.writeDirectory)
            self.root.append(filename)
            path = etree.Element("path")
            path.text = self.path if hasattr(self, "path") else os.path.join(curDir, self.writeDirectory)
            self.root.append(path)
            source = etree.Element("source")
            database = etree.Element("database")
            database.text = self.database if hasattr(self, "database") else "Unknown"
            source.append(database)
            self.root.append(source)
            size = etree.Element("size")
            width = etree.Element("width")
            width.text = self.width if hasattr(self, "width") else str(1600)
            size.append(width)
            height = etree.Element("height")
            height.text = self.height if hasattr(self, "height") else str(1200)
            size.append(height)
            depth = etree.Element("depth")
            depth.text = self.depth if hasattr(self, "depth") else str(3)
            size.append(depth)
            self.root.append(size)
            segmented = etree.Element("segmented")
            segmented.text = self.segmented if hasattr(self, "height") else str(0)
            self.root.append(segmented)

        else:
            try:
                self.root = etree.fromstring(self.string)
            except :
                raise Exception("Cannot parse self.string",self.string)
        del self.string


    #
    #
    #
    # AnnotationWriter can only be compiled once.
    # Then you get AttributeError

    def write(self):
        # Deleting tabs , new line characters and whitespaces
        # because they are looking ugly.
        xmlString = etree.tostring(self.root).decode()
        purgedString = self.__purge(xmlString)
        prettyXML = parseXML(purgedString).toprettyxml()
        lastXML = prettyXML[prettyXML.index("\n")+1:]
        with open(self.writeDirectory, "w") as fp:
            fp.write(lastXML)

    def setWriteDirectory(self, writeDir):
        self.writeDirecory = writeDir if os.path.exists(writeDir) else self.writeDirectory


    def setProperties(self,
                      folder = None,
                      filename=None,
                      path = None,
                      database = "Unknown",
                      width = 1600,
                      height = 1200,
                      depth = 3,
                      segmented = 0
                      ):
        if not self.string :
            self.folder = folder
            self.filename = filename
            self.path = path
            self.database = database
            self.width = str(width)
            self.height = str(height)
            self.depth = str(depth)
            self.segmented = str(segmented)

        else:
            raise Exception("If you want to set properties of annotation,"
                            "you should construct AnnotationWriter object "
                            "with empty string.")


    def __purge(self,string):

        return string.replace(" ","").replace("\t","").replace("\n","")


    def addObject(self,name, xmin, ymin, xmax, ymax,
                  pose="Unspecified",
                  truncated=0,
                  difficult=0):

        obj = self.__generateObject(name, xmin, ymin, xmax, ymax,
                                   pose, truncated, difficult)
        self.root.append(obj)



    def addObjects(self,iter):
        for i in iter:
            self.addObject(i[0],i[1],i[2],i[3],i[4])

    def __generateObject(self, name, xmin, ymin, xmax, ymax,
                        pose,
                        truncated,
                        difficult):
        obj = etree.Element('object')
        nameObj = etree.Element("name")
        nameObj.text = name
        obj.append(nameObj)
        poseObj = etree.Element("pose")
        poseObj.text = str(pose)
        obj.append(poseObj)
        truncatedObj = etree.Element("truncated")
        truncatedObj.text = str(truncated)
        obj.append(truncatedObj)
        difficultObj = etree.Element("difficult")
        difficultObj.text = str(difficult)
        obj.append(difficultObj)
        bndbox = self.__generateBoundaryBox(xmin, ymin, xmax, ymax)
        obj.append(bndbox)
        return obj

    def __generateBoundaryBox(self, xmin, ymin, xmax, ymax):

        bndbox = etree.Element("bndbox")
        xminObj = etree.Element("xmin")
        xminObj.text = str(xmin)
        bndbox.append(xminObj)
        yminObj = etree.Element("ymin")
        yminObj.text = str(ymin)
        bndbox.append(yminObj)
        xmaxObj = etree.Element("xmax")
        xmaxObj.text = str(xmax)
        bndbox.append(xmaxObj)
        ymaxObj = etree.Element("ymax")
        ymaxObj.text = str(ymax)
        bndbox.append(ymaxObj)

        return bndbox


    def getRoot(self) :
        return self.root

    @staticmethod
    def readFile(file):


        if AnnotationWriter.isFileWrapper(file) :
            return file.read()

        elif type(file) == str:
            fp = open(file, "r")
            return fp.read()

        else:
            raise TypeError("Given file can be name of a file or file wrapper."
                            "But you give {}".format(type(file)))


    @staticmethod
    def isFileWrapper(file):


        if hasattr(file, "__class__") and str(file.__class__) == "<class '_io.TextIOWrapper'>":
            return True

        else:
            return False



    @staticmethod
    def buildEmptyXML(path):
        return AnnotationWriter("", writeDirectory=path)



    def __str__(self):
        return etree.tostring(self.root).decode()

    def __repr__(self):
        return self.__str__(self)



class AnnotationDispatcher(object):


    def __init__(self):
        pass

    def __call__(self,firstAnnotation,secondAnnotation):

        if type(firstAnnotation ) == AnnotationWriter or type(firstAnnotation) == AnnotationReader:
            firstChildren = AnnotationDispatcher.getChildren(firstAnnotation)
        elif type(firstAnnotation) == list:
            firstChildren = firstAnnotation
        else:
            raise TypeError("firstAnnotation must be list or AnnotationWriter or AnnotationReader.\n")


        if type(secondAnnotation) == AnnotationWriter or type(secondAnnotation) == AnnotationReader:
            secondChildren = AnnotationDispatcher.getChildren(secondAnnotation)
        elif type(secondAnnotation) == list :
            secondChildren = secondAnnotation
        else:
            raise TypeError("firstAnnotation must be list or AnnotationWriter or AnnotationReader.\n")


        disjointChildren = list(firstChildren)
        for i in firstChildren:
            for j in secondChildren:
                intersection = AnnotationDispatcher.intersectionOverUnion(i[1:],j[1:])
                if intersection >= 0.05:
                    disjointChildren.remove(i)
                    break



        childrenCannotBeFound = list(secondChildren)
        for i in secondChildren:
            for j in firstChildren:
                intersection = AnnotationDispatcher.intersectionOverUnion(i[1:],j[1:])
                if intersection >= 0.05:
                    childrenCannotBeFound.remove(i)
                    break


        return (disjointChildren,childrenCannotBeFound)


    @staticmethod
    def intersectionOverUnion(firstBox, secondBox):
        xA = max(firstBox[0], secondBox[0])
        yA = max(firstBox[1], secondBox[1])
        xB = min(firstBox[2], secondBox[2])
        yB = min(firstBox[3], secondBox[3])

        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

        boxAArea = (firstBox[2] - firstBox[0] + 1) * (firstBox[3] - firstBox[1] + 1)
        boxBArea = (secondBox[2] - secondBox[0] + 1) * (secondBox[3] - secondBox[1] + 1)

        iou = interArea / float(boxAArea + boxBArea - interArea)

        return iou



    @staticmethod
    def getChildren(anno):
        children = []
        root = anno.getRoot()
        tmp = [child for child in root.iterchildren("object")]
        for child in tmp:
            bndBox = list(child.iterchildren("bndbox"))[0]
            label = list(child.iterchildren("name"))[0].text
            xmin = int(list(bndBox.iterchildren("xmin"))[0].text)
            ymin = int(list(bndBox.iterchildren("ymin"))[0].text)
            xmax = int(list(bndBox.iterchildren("xmax"))[0].text)
            ymax = int(list(bndBox.iterchildren("ymax"))[0].text)
            children.append((label, xmin, ymin, xmax, ymax))

        return children



