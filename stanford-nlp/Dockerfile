FROM java:8

COPY . /stanford_nlp
WORKDIR /stanford_nlp/stanford-ner-2018-02-27
EXPOSE 9199

# RUN wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-01-31.zip

CMD ["java", "-Djava.ext.dirs=./lib", "-cp", "stanford-ner.jar", "edu.stanford.nlp.ie.NERServer", "-port", "9199", "-loadClassifier", "../edu/stanford/nlp/models/ner/english.muc.7class.caseless.distsim.crf.ser.gz"]