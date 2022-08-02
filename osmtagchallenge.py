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


def tweet_image(url):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(config.twitter_api_key, config.twitter_api_key_secret)
    auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)

    try:
        # Create API object
        api = tweepy.API(auth)

        # Create a tweet
        print("Publication du tweet")
        status = api.update_status("#OpenStreetMap tag challenge\n" + url)
        return status.id

    except TwitterException:
        print("Erreur pendant la publication du tweet")
        return None

def toot_image(url):
    try:
        mastodon = Mastodon(
            client_id = os.path.join(os.path.dirname(__file__), 'osmtagchallenge.secret'),
            api_base_url = 'https://mastodon.social'
        )
        mastodon.log_in(
            config.mastodon_login,
            config.mastodon_password
        )
        print("Publication du toot")
        status = mastodon.toot("#OpenStreetMap tag challenge\n" + url)
        return status["id"]

    except:
        print("Erreur pendant la publication du toot")
        return None

def get_photos(photoset_id):

    flickr = flickrapi.FlickrAPI(config.flickr_api_key, config.flickr_secret, format='parsed-json')

    print("Récupération de la première page de l'album")
    photos = flickr.photosets.getPhotos(user_id=JLZ_flickr_id, photoset_id=photoset_id)

    result = [p["id"] for p in photos["photoset"]["photo"]]

    if photos["photoset"]["pages"] != 1:
        for page in range(2, photos["photoset"]["pages"]):
            print("Récupération de la page " + str(page) + " de l'album")
            photos = flickr.photosets.getPhotos(user_id=JLZ_flickr_id, photoset_id=photoset_id, page=page)
            result += [p["id"] for p in photos["photoset"]["photo"]]

    return result


def build_image_url(image_id, album_id):
    return "https://www.flickr.com/photos/" + JLZ_flickr_simple_id + "/" + image_id + "/in/album-" + album_id + "/"


def get_already_published_list():
    result = []
    try:
        with open(published_file, 'r') as f:
            result = json.load(f)

    except FileNotFoundError:
        pass
    return result


# get photos
photos = get_photos(album_id)

# get already published photos
already_published = get_already_published_list()

already_published_flat = [x["id"] if isinstance(x, map) else x for x in already_published]

# only keep new ones
photos = [p for p in photos if p not in already_published_flat]

# randomly select one image
selected = random.choice(photos)

# tweet this image
result_twitter = tweet_image(build_image_url(selected, album_id))

# toot this image
result_mastodon = toot_image(build_image_url(selected, album_id))

# save the tweeted image
if result_twitter is not None or result_mastodon is not None:
    already_published.append({"id": selected, "twitter": result_twitter, "mastodon": result_mastodon})

    with open(published_file, 'w') as f:
        json.dump(already_published, f)
else:
    print("Erreur: ni Twitter ni Mastodon n'ont été alimentés.")
