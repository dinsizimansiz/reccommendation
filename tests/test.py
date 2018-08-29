from utils.annotation import AnnotationWriter

if __name__ == "__main__":

    #Sifirdan obje yaratma
    prey = AnnotationWriter.buildEmptyXML("abc_4391.xml")
    #Default En ustteki ozellikleri giriyor
    #folder girmezsen ustundeki klasoru aliyor.
    #filename girmezsen buildEmptyXMLe girdigin dosya adini kullaniyor.
    #path girmezsen os.getcwd() kullaniyor.
    #database girmezsen Unknownu kullaniyor.
    #size girmezsen widtH:1600 height:1200 depth:3
    #segmented girmezsen 0
    prey.setProperties()
    #Compile i obje eklemeden once yap.
    prey.compile()
    prey.addObject("PLT - Normal",244,38,277,74)
    prey.write()

    modifiedPrey = AnnotationWriter("abc_4391.xml", isFileName=True, overwrite=True)
    modifiedPrey.compile()
    modifiedPrey.addObject("PLT - Normal",11,180,46,209)
    modifiedPrey.write()
    modifiedPrey.addObject("PLT - Normal",846,73,893,102)
    modifiedPrey.write()


    fileTest = open("abc_4391.xml")
    filePrey = AnnotationWriter(fileTest,overwrite=True)
    filePrey.compile()
    filePrey.addObject("PLT - Normal",556,91,595,113)
    filePrey.write()


