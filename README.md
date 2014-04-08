AnnotationPipeline
==================

Scripts to convert papers between the different formats in the pipeline.

<h3>Training a TEES model</h3>

<ol>
<li>Add DOIs to a file</li>
<li>Run doi_to_annotation_format</li>
<li>Do manual sentence splitting</li>
<li>Run clean_after_sentence_split</li>
<li>Annotate in Brat</li>
<li>Run convert_to_IXML (currently parsing is commented out, recomment that)</li>
<li>Train TEES</li>
</ol>

Run TEES with this command:

<code>python train.py --trainFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml --develFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml --testFile /home/elias/NTNU/AnnotationPipeline/IXML/corpus_interaction.xml -o output -t OC -p CoreNLP</code>

<h3>Classifying on TEES</h3>

<ol>
<li>Add DOIs to a file</li>
<li>???</li>
<li>Classify on TEES</li>
</ol>

Run TEES with this command:

<code>python classify.py ???</core>
