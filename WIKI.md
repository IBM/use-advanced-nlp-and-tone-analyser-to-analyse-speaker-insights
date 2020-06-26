# Short Title

Use Advanced NLP and Tone Analyser to extract insights

# Long Title

Use Advanced NLP and Tone Analyser to extract insights such as Categories, Concepts, Emotion, Entities, Keywords, Sentiment, and positive sentences from a text file.


# Author
* [Manoj Jahgirdar](https://www.linkedin.com/in/manoj-jahgirdar-6b5b33142/)
* [Manjula Hosurmath](https://www.linkedin.com/in/manjula-g-hosurmath-0b47031)

# URLs

### Github repo

* https://github.com/IBM/use-advanced-nlp-and-tone-analyser-to-analyse-speaker-insights


### Video Link
* 

# Summary

In this code pattern, given a text file, we learn how to extract insights such as Categories, Concepts, Emotion, Entities, Keywords, Sentiment, and positive sentencesusing Watson Natural Language Understanding and Tone Analyzer.

# Technologies

* [Python](https://developer.ibm.com/technologies/python): An open-source interpreted high-level programming language for general-purpose programming.

* [Object Storage](https://developer.ibm.com/technologies/object-storage): Store large amounts of data in a highly scalable manner.

# Description

This Code Pattern is part of the series [Extracting insights from Videos with IBM Watson]()

Part of the World Health Organization's guidance on limiting further spread of COVID-19 is to practice social distancing. As a result, Companies in most affected areas are taking precautionary measures by encouraging Work from Home and Educational Institutes are closing their facilities. Employees working from home must be aware of the happenings in their company and need to collaborate with their team, students at home must be up to date with their education.

With the help of technology, employees can continue to collaborate and be involved into their work with virtual meetings, schools and teachers can continue to engage with their students through virtual classrooms. These meetings can be recorded and deriving insights from these recordings can be beneficial for the end users.

In this code pattern we will learn how to to extract insights such as Categories, Concepts, Emotion, Entities, Keywords, Sentiment, and positive sentences from a given text file.

# Flow

<!--add an image in this path-->
![architecture](doc/source/images/architecture.png)

1. The transcribed text from the [previous code pattern of the series](https://github.com/IBM/build-custom-stt-model-with-diarization) is retrived from Cloud Object Storage.

2. Watson Natural Language Understanding and Watson Tone Analyzer is used to extract insights from the text.

3. The response from Natural Language Understanding and Watson Tone Analyzer is analyzed by the application and a Report is generated.

4. User can download the Report which consists of the textual insights.

# Instructions

> Find the detailed steps in the [README](https://github.com/IBM/build-custom-stt-model-with-diarization/blob/master/README.md) file.


1. Clone the repo

2. Create Watson Services

3. Add the Credentials to the Application

4. Deploy the Application

5. Run the Application

# Components and services

* [Natural Language Understanding](https://cloud.ibm.com/catalog/services/natural-language-understanding): Use advanced NLP to analyze text and extract meta-data from content such as concepts, entities, keywords, categories, sentiment, emotion, relations, and semantic roles. Apply custom annotation models developed using Watson Knowledge Studio to identify industry/domain specific entities and relations in unstructured text with Watson NLU.

* [Tone Analyzer](https://cloud.ibm.com/catalog/services/tone-analyzer): People show various tones, such as joy, sadness, anger, and agreeableness, in daily communications. Such tones can impact the effectiveness of communication in different contexts. Tone Analyzer leverages cognitive linguistic analysis to identify a variety of tones at both the sentence and document level. This insight can then used to refine and improve communications. It detects three types of tones, including emotion (anger, disgust, fear, joy and sadness), social propensities (openness, conscientiousness, extroversion, agreeableness, and emotional range), and language styles (analytical, confident and tentative) from text.

* [Object Storage](https://cloud.ibm.com/catalog/services/cloud-object-storage): IBM Cloud Object Storage is a highly scalable cloud storage service, designed for high durability, resiliency and security. Store, manage and access your data via our self-service portal and RESTful APIs. Connect applications directly to Cloud Object Storage use other IBM Cloud Services with your data.
