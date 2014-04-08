AnnotationPipeline
==================

Scripts to convert papers between the different formats in the pipeline.

<h3>Training a TEES model</h3>

1. Add DOIs to a file
2. Run doi_to_annotation_format
3. Do manual sentence splitting
4. Run clean_after_sentence_split
5. Annotate in Brat
6. Run convert_to_IXML (currently parsing is commented out, recomment that)
7. Train TEES

Run TEES with this command:

python train.py --trainFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml --develFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml --testFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml -o output -t OC -p CoreNLP

<h3>Classifying on TEES</h3>

1. Add DOIs to a file
2. ???
3. Classify on TEES

Run TEES with this command:

python classify.py ???
