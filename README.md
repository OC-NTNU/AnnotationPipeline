AnnotationPipeline
==================

Scripts to convert papers between the different formats in the pipeline.

Process:

1. Add DOIs to a file
2. Run doi_to_annotation_format
3. Do manual sentence splitting, manually edit charOffsets
4. Run fix_newlines
5. Annotate in Brat
6. Run convert_to_IXML (currently parsing is commented out, recomment that)
7. Train TEES

Run TEES with this command:

python train.py --trainFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml --develFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml --testFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml -o output -t OC -p CoreNLP

