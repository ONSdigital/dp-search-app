FROM java:8

WORKDIR /home
RUN wget -O ner.zip http://nlp.stanford.edu/software/stanford-ner-2015-04-20.zip
RUN unzip ner.zip
COPY english.muc.7class.caseless.distsim.crf.ser.gz /home/stanford-ner-2015-04-20

EXPOSE 9199

WORKDIR /home/stanford-ner-2015-04-20

#CMD ["java", "-Djava.ext.dirs=./lib", "-cp", "stanford-ner.jar", "edu.stanford.nlp.ie.NERServer", "-port", "9199", "-loadClassifier", "classifiers/english.muc.7class.distsim.crf.ser.gz"]

CMD ["java", "-Djava.ext.dirs=./lib", "-cp", "stanford-ner.jar", "edu.stanford.nlp.ie.NERServer", "-port", "9199", "-loadClassifier", "english.muc.7class.caseless.distsim.crf.ser.gz"]
