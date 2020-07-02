'''Import Libraries'''

from flask import Flask, render_template, request, redirect, jsonify
import requests
from werkzeug import secure_filename
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, EntitiesOptions, KeywordsOptions, \
    SyntaxOptions, SyntaxOptionsTokens, CategoriesOptions, ConceptsOptions, \
    EmotionOptions, MetadataOptions, RelationsOptions, SemanticRolesOptions
from ibm_watson import ToneAnalyzerV3
from operator import itemgetter
from wordcloud import WordCloud, STOPWORDS
import os
import json
import math
import matplotlib.pyplot as plt
from datetime import datetime
import time

''' Initialize Flask Variables '''

app = Flask(__name__)

app.config["CORPUS_UPLOAD"] = "static/raw/"
app.config["AUDIO_UPLOAD"] = "static/audios/"
app.config["COS_VIDEOS"] = "videos/"
app.config["COS_AUDIOS"] = "audios/"

''' Initialize other constants for COS and STT '''


# Constants for IBM COS values
COS_ENDPOINT = ""
COS_API_KEY_ID = ""
COS_AUTH_ENDPOINT = ""
COS_RESOURCE_CRN = ""
COS_BUCKET_LOCATION = "us-standard"
bucket_name = ""

# Constants for NLU & Tone Analyzer values
NLU_API_KEY_ID = ""
NLU_URL = ""
TONE_API_KEY_ID = ""
TONE_URL = ""


''' Methods for IBM Cloud Object Storage '''

with open('credentials.json', 'r') as credentialsFile:
    credentials = json.loads(credentialsFile.read())

# connect to IBM cloud object storage
endpoints = requests.get(credentials.get('endpoints')).json()
iam_host = (endpoints['identity-endpoints']['iam-token'])
cos_host = (endpoints['service-endpoints']
            ['cross-region']['us']['public']['us-geo'])

# Constrict auth and cos endpoint
auth_endpoint = "https://" + iam_host + "/identity/token"
service_endpoint = "https://" + cos_host

# Assign Bucket Name
try:
    bucket_name = credentials.get('bucket_name')
except Exception as e:
    bucket_name = "notassigned"

# Set Constants for IBM COS values
COS_ENDPOINT = service_endpoint
COS_API_KEY_ID = credentials.get('apikey')
COS_AUTH_ENDPOINT = auth_endpoint

COS_RESOURCE_CRN = credentials.get('resource_instance_id')

# Create client
cos = ibm_boto3.resource("s3",
                         ibm_api_key_id=COS_API_KEY_ID,
                         ibm_service_instance_id=COS_RESOURCE_CRN,
                         ibm_auth_endpoint=COS_AUTH_ENDPOINT,
                         config=Config(signature_version="oauth"),
                         endpoint_url=COS_ENDPOINT
                         )


@app.route('/COSBucket',  methods=['GET', 'POST'])
def setupCOSBucket():
    if request.method == 'POST':
        temp = request.form
        bkt = json.loads(temp['bkt'])
        with open('credentials.json', 'r') as credentialsFile:
            cred = json.loads(credentialsFile.read())
        cred.update(bkt)
        print(json.dumps(cred, indent=2))
        with open('credentials.json', 'w') as fp:
            json.dump(cred, fp,  indent=2)
        return jsonify({'flag': 0})


@app.route('/initCOS')
def initializeCOS():
    try:
        global bucket_name
        flag = False
        buckets = cos.buckets.all()
        with open('credentials.json', 'r') as credentialsFile:
            cred = json.loads(credentialsFile.read())
        for bucket in buckets:
            if cred['bucket_name'] == bucket.name:
                flag = True
                bucket_name = cred['bucket_name']
                break
        if not flag:
            respo = {"message": "Bucket \"" +
                     bucket_name + "\" does not exists"}
        else:
            respo = {"message": "Bucket \"" + bucket_name + "\" found!"}

    except ClientError as be:
        respo = {"message": "CLIENT ERROR: {0}\n".format(be)}
    except Exception as e:
        respo = {"message": " {0}".format(e)}
    print(json.dumps(respo, indent=2))
    return json.dumps(respo, indent=2)


def get_bucket_contents(bucket_name):
    myList = []
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        for file in files:
            myList.append([file.key, file.size])
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
        return myList
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))


def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(
        bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()
        return file["Body"].read()
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))


def delete_item(bucket_name, item_name):
    print("Deleting item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).delete()
        print("Item: {0} deleted!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete item: {0}".format(e))
        
@app.route('/getAudioFiles')
def getAudioFiles():
    jsonList = []
    for file in get_bucket_contents(bucket_name):
        if file[0][0] == 't':
            myDict = {'audioFile': file[0], 'fileSize': convert_size(file[1])}
            jsonList.append(myDict)
    return json.dumps(jsonList, indent=2)


''' Methods for IBM Watson Natural Language Understanding '''

with open('naturallanguageunderstanding.json', 'r') as credentialsFile:
    credentials1 = json.loads(credentialsFile.read())

NLU_API_KEY_ID = credentials1.get('apikey')
NLU_URL = credentials1.get('url')

nlu_authenticator = IAMAuthenticator(NLU_API_KEY_ID)
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    authenticator=nlu_authenticator
)

natural_language_understanding.set_service_url(NLU_URL)

''' Methods for IBM Watson Tone Analyser '''

with open('toneanalyzer.json', 'r') as credentialsFile:
    credentials2 = json.loads(credentialsFile.read())

TONE_API_KEY_ID = credentials2.get('apikey')
TONE_URL = credentials2.get('url')

tone_analyzer_authenticator = IAMAuthenticator(TONE_API_KEY_ID)

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=tone_analyzer_authenticator
)

tone_analyzer.set_service_url(TONE_URL)

''' Method to delete files from Cloud Object Storage '''


def deleteFiles(fileName):
    try:
        fileNameLocal = fileName.split('/')[1]

        fileToDelete = 'rm static/audios/' + fileNameLocal

        os.system(fileToDelete)
        item_name = fileName

        delete_item(bucket_name, item_name)

        myFlag = {"flag": 0}
    except OSError as err:
        myFlag = {"flag": 1}

    return json.dumps(myFlag, indent=2)


''' Method to handle POST upload '''


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    try:
        if request.method == 'POST':
            f = request.files["video"]
            filename_converted = f.filename.replace(
                " ", "-").replace("'", "").lower()
            cmd = 'rm -r static/raw/*'
            os.system(cmd)
            f.save(os.path.join(
                app.config["CORPUS_UPLOAD"], secure_filename("corpus-file.txt")))

        myResponse = {"message": 1}
    except Exception as e:
        print("Unable {0}".format(e))
        myResponse = {"message": str(e)}

    return json.dumps(myResponse, indent=2)


@app.route('/deleteUploadedFile')
def deleteUploadedFile():
    fileName = request.args['fileName']
    return deleteFiles(fileName)

''' Method to analyse text with NLU and Tone Analyser '''


@app.route('/analyseText', methods=['GET', 'POST'])
def analyseText():
    if request.method == 'POST':
        opt = request.form
        options = json.loads(opt['options'])
        
        ''' Prepare the text for Analysis'''
        
        text = get_item(bucket_name, 'transcript/'+options.get('file'))
        text = text.decode("utf-8")
        text = text.replace('%HESITATION', '')
        
        print(text)
        
        ''' Initialize a return variable '''
        
        myJsonDict = {}
    
        ''' Extract Category with NLU '''
        
        if options.get('category') == "True":
            response = natural_language_understanding.analyze(
                language='en',
                text=text,
                features=Features(categories=CategoriesOptions(limit=1))).get_result()

            category = response['categories'][0]
            
            # Return category ['label'] ['score']
            myJsonDict.update({"category" : category})
        else:
            pass
        
        ''' Extract Concepts with NLU '''
        
        if options.get('concepts') == "True":
            response = natural_language_understanding.analyze(
                language='en',
                text=text,
                features=Features(concepts=ConceptsOptions(limit=3))).get_result()

            concepts = sorted(response['concepts'],
                  key=itemgetter('relevance'), reverse=True)
            
            myJsonDict.update({"concepts": concepts})
            # Return concepts ['text'] ['relevence'] ['dbpedia_resource']
        else:
            pass
        
        ''' Extract Entity with NLU '''
        
        if options.get('entity') == "True":
            response = natural_language_understanding.analyze(
                language='en',
                text = text,
                features=Features(entities=EntitiesOptions(limit=1))).get_result()

            entity = sorted(response['entities'], key=itemgetter('relevance'), reverse=True)

            myJsonDict.update({"entity": entity[0]})
            # Return entity[0] ['type'] ['text'] ['relevance']
        else:
            pass
        
        ''' Extract Sentiments and Emotions with NLU '''
        
        if options.get('sentiments') == "True":
            response = natural_language_understanding.analyze(
                language='en',
                text=text,
                features=Features(keywords=KeywordsOptions(sentiment=True, emotion=True, limit=10))).get_result()

            keywords = sorted(response['keywords'],
                  key=itemgetter('relevance'), reverse=True)

            keywords_sentiments_emotions = []

            for i in keywords:

                keywords_sentiments_emotions_buffer = {
                    'keyword': i['text'],
                    'sentiment': i['sentiment']['label'],
                    'emotion': ''
                }
                maximum = i['emotion']['sadness']
                keywords_sentiments_emotions_buffer['emotion'] = 'sadness'

                if i['emotion']['joy'] > maximum:
                    maximum = i['emotion']['joy']
                    keywords_sentiments_emotions_buffer['emotion'] = 'joy'

                elif i['emotion']['fear'] > maximum:
                    maximum = i['emotion']['fear']
                    keywords_sentiments_emotions_buffer['emotion'] = 'fear'

                elif i['emotion']['disgust'] > maximum:
                    maximum = i['emotion']['disgust']
                    keywords_sentiments_emotions_buffer['emotion'] = 'disguest'

                elif i['emotion']['anger'] > maximum:
                    maximum = i['emotion']['anger']
                    keywords_sentiments_emotions_buffer['emotion'] = 'anger'

                keywords_sentiments_emotions.append(keywords_sentiments_emotions_buffer)
           
            myJsonDict.update({"sentiments": keywords_sentiments_emotions})
            # Return keywords_sentiments_emotions ['keyword'] ['sentiment'] ['emotion']
        else:
            pass
        
        ''' Analyse tone to get top 5 positive sentences '''
        
        if options.get('positiveSentences') == "True":
            tone_analysis = tone_analyzer.tone(
                {'text': text},
                content_type='application/json'
            ).get_result()

            sentences_with_joy = []
            print(json.dumps(tone_analysis, indent=2))
            
            try:
                for tone in tone_analysis['sentences_tone']:
                    try:
                        if tone['tones'][0]['tone_name'] == "Joy":
                            tempDict = {"sentence_id": tone['sentence_id'],
                                        "text": tone['text'],
                                        "score": tone['tones'][0]['score']}
                            sentences_with_joy.append(tempDict)
                    except:
                        continue
            
                sentences_with_joy = sorted(
                    sentences_with_joy, key=itemgetter('score'), reverse=True)

                myJsonDict.update({"positiveSentences": sentences_with_joy[:5]})
            except:
                tempDict = {"sentence_id": '',
                            "text": 'Text file too small to get positive sentences, please try again with a bigger document.',
                            "score": '100'}
                myJsonDict.update(
                    {"positiveSentences": [tempDict]})
            # return sentences_with_joy[:5] ['text'] ['score']
        else:
            pass
        
        ''' Pre-Processing parts of speech to plot Word Cloud '''
        
        response = natural_language_understanding.analyze(
            language='en',
            text=text,
            features=Features(
                syntax=SyntaxOptions(
                    sentences=True,
                    tokens=SyntaxOptionsTokens(
                        lemma=True,
                        part_of_speech=True,
                    )))).get_result()

        verbs = []
        for i in response['syntax']['tokens']:
            if i['part_of_speech'] == 'VERB':
                verbs.append(i['text'])
        
        nouns = []
        for i in response['syntax']['tokens']:
            if i['part_of_speech'] == 'NOUN':
                nouns.append(i['text'])
                
        adj = []
        for i in response['syntax']['tokens']:
            if i['part_of_speech'] == 'ADJ':
                adj.append(i['text'])
                
        nouns_adjectives = []
        for x in nouns:
            nouns_adjectives.append(x)

        for y in adj:
            nouns_adjectives.append(y)
            
        comment_words_verbs = ' '
        comment_words_nouns_adj = ' '
        stopwords = set(STOPWORDS)

        for val in verbs:
            val = str(val)
            tokens = val.split()
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()
            for words in tokens:
                comment_words_verbs = comment_words_verbs + words + ' '
        
        for val in nouns_adjectives:
            val = str(val)
            tokens = val.split()
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()
            for words in tokens:
                comment_words_nouns_adj = comment_words_nouns_adj + words + ' '
        
        wordcloud_verbs = WordCloud(width=800, height=800,
                                    background_color='white',
                                    stopwords=stopwords,
                                    min_font_size=10,
                                    max_font_size=150,
                                    random_state=42).generate(comment_words_verbs)
        
        wordcloud_nouns_adj = WordCloud(width = 800, height = 800, 
                background_color ='white',
                colormap="Dark2",
                stopwords = stopwords, 
                min_font_size = 10,
                max_font_size=150, 
                random_state=42).generate(comment_words_nouns_adj)
        
        todayDate = datetime.today().strftime('%m-%d-%Y-%s')
        
        verbsWC = 'static/images/verbs'+todayDate+'.png'
        plt.switch_backend('Agg')
        plt.figure(figsize=(5, 5), facecolor=None)
        plt.imshow(wordcloud_verbs)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.title("Verbs")
        plt.savefig(verbsWC, title=True)
        
        nounsAdjWC = 'static/images/nouns_adjectives'+todayDate+'.png'
        plt.switch_backend('Agg')
        plt.figure(figsize = (5, 5), facecolor = None) 
        plt.imshow(wordcloud_nouns_adj) 
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.title("Nouns & Adjectives")
        plt.savefig(nounsAdjWC, title=True)
        
        wordclouds = [nounsAdjWC, verbsWC]
        
        myJsonDict.update({"wordclouds": wordclouds})
        # print(json.dumps(options, indent=2))
        return jsonify(myJsonDict)
        


''' Other Methods '''


@app.route('/')
def index():
    return render_template('index.html')

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


port = os.getenv('VCAP_APP_PORT', '8082')
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=port)
