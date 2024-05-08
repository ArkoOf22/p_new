from django.http import HttpResponse
import os
import speech_recognition as sr
from google.cloud import translate_v2 as translate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required



def home_view(request):
    return render(request, 'app1/home.html')


def about_view(request):
    return render(request, 'app1/about.html')


def contact_view(request):
    return render(request, 'app1/contact.html')



def animation_view(request):
    if request.method == 'POST':
        kannada_text = request.POST.get('sen')

        #initialize the client

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/arkodeep/Downloads/p_new/assets/j1.json'

        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './assets/api_key_new.json'
        translate_client = translate.Client()
    # tokenizing the sentence

        target = 'en-IN'
        output = translate_client.translate(
            kannada_text,
            target_language=target)
        english_text=output['translatedText']

        english_text.lower()
        # tokenizing the sentence
        words = word_tokenize(english_text)

        tagged = nltk.pos_tag(words)
        tense = {}
        tense["future"] = len([word for word in tagged if word[1] == "MD"])
        tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
        tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
        tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])

        # stopwords that will be removed
        stop_words = set(
            ["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've", 'off', 'for',
             "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don',
             'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the',
             'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have', 'hasn', 'o', "aren't", "you'll",
             "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself',
             'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did',
             'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])

        # removing stopwords and applying lemmatizing nlp process to words
        lr = WordNetLemmatizer()
        filtered_text = []
        for w, p in zip(words, tagged):
            if w not in stop_words and w.isalnum():
                if p[1] == 'VBG' or p[1] == 'VBD' or p[1] == 'VBZ' or p[1] == 'VBN' or p[1] == 'NN':
                    filtered_text.append(lr.lemmatize(w, pos='v'))
                elif p[1] == 'JJ' or p[1] == 'JJR' or p[1] == 'JJS' or p[1] == 'RBR' or p[1] == 'RBS':
                    filtered_text.append(lr.lemmatize(w, pos='a'))

                else:
                    filtered_text.append(lr.lemmatize(w))

        # adding the specific word to specify tense
        words = filtered_text
        temp = []
        for w in words:
            if w == 'I':
                temp.append('Me')
            else:
                temp.append(w)
        words = temp
        probable_tense = max(tense, key=tense.get)

        if probable_tense == "past" and tense["past"] >= 1:
            temp = ["Before"]
            temp = temp + words
            words = temp
        elif probable_tense == "future" and tense["future"] >= 1:
            if "Will" not in words:
                temp = ["Will"]
                temp = temp + words
                words = temp
            else:
                pass
        elif probable_tense == "present":
            if tense["present_continuous"] >= 1:
                temp = ["Now"]
                temp = temp + words
                words = temp

        filtered_text = []
        for w in words:
            path = w + ".mp4"
            f = finders.find(path)
            # splitting the word if its animation is not present in database
            if not f:
                for c in w:
                    filtered_text.append(c)
               
            # otherwise animation of word
            else:
                filtered_text.append(w)
        words = filtered_text
        print(words)

        return render(request, 'app1/animation.html', {'words': words, 'text': english_text})
    else:
        return render(request, 'app1/animation.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # log the user in
            return redirect('animation')
    else:
        form = UserCreationForm()
    return render(request, 'app1/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log in user
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('animation')
    else:
        form = AuthenticationForm()
    return render(request, 'app1/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect("home")
