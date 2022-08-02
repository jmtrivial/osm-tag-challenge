import tweepy
from mastodon import Mastodon
import flickrapi
import json
import random
import os


import config

JLZ_flickr_simple_id = "jeanlouis_zimmermann"
JLZ_flickr_id = "40911451@N00"
album_id = '72177720298086796'
published_file = os.path.join(os.path.dirname(__file__), 'published.json')


def get_flickr_osm_tags(id):

    flickr = flickrapi.FlickrAPI(config.flickr_api_key, config.flickr_secret, format='parsed-json')

    print("Récupération des tags de la photo", id)
    tags = flickr.tags.getListPhoto(photo_id=id)
    return [x["raw"] for x in tags["photo"]["tags"]["tag"] if "=" in x["raw"] and not x["raw"].startswith("osm:")]


def get_last_published_image():
    result = None
    try:
        with open(published_file, 'r') as f:
            result = json.load(f)

        if len(result) == 0:
            return None

        return result[-1]

    except FileNotFoundError:
        pass
    return result


def has_answers_tweet(id):
    # Authenticate to Twitter

    try:
        # Create client object
        client = tweepy.Client(config.twitter_bearer_token)

        # Create a tweet
        print("Récupération des infos du tweet", id)
        response = client.get_tweets([int(id)], tweet_fields=["public_metrics"])
        if len(response.data) > 0:
            return response.data[0].public_metrics["reply_count"] + response.data[0].public_metrics["quote_count"] > 0
        else:
            return False

    except:
        print("Erreur pendant la récupération des infos du tweet")
        return None


def tweet_tags(tags, id):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(config.twitter_api_key, config.twitter_api_key_secret)
    auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)

    try:
        # Create API object
        api = tweepy.API(auth)

        # Create a tweet
        print("Publication du tweet")
        if len(tags) == 0:
            texts = ["Alors, toujours pas de proposition de tag ?",
                     "Qui se lance ?",
                     "Une idée de tag ?",
                     "La photo est trop dure ?",
                     "Allo, y'a quelqu'un ?",
                     "Allo Houston !",
                     "À la rescousse !",
                     "je me sens seul.",
                     "si je vois gêne dites-le ;-)",
                     "Soyez pas timides !",
                     "Ben alors ?",
                     "un volontaire ?",
                     "Plouf, plouf…",
                     "🎵The show must go on 🎶"]
            text = random.choice(texts)
        else:
            texts1 = ["Allez, on vous aide un peu : ", "On pourrait proposer par exemple" , "Quelques suggestions : "]
            texts2 = ["", ". Qu'en pensez-vous ?", "C'est un début, bien sûr. Vous complétez ?"]
            text =  random.choice(texts1) + ", ".join(tags) + random.choice(texts2)
        status = api.update_status(text, in_reply_to_status_id=id)
        return status

    except:
        print("Erreur pendant la publication du tweet")
        return None

# get last published image
last_publication = get_last_published_image()

# get tags
tags = get_flickr_osm_tags(last_publication["id"])


# has answers (twitter)
answers_twitter = has_answers_tweet(last_publication["twitter"])

if answers_twitter is not None and not answers_twitter:
    print("Publication d'une réponse")
    result_twitter = tweet_tags(tags, last_publication["twitter"])

    if result_twitter is None:
        print("Erreur: Twitter n'a pas été alimenté.")

# TODO: answers on mastodon