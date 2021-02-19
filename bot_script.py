#!/usr/bin/python
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import tweepy
import logging
import time
from Plant import Plant
from Plant import Personality
from Plant import SunExposure
from Plant import Size
from random import randint
nltk.download('twitter_samples')
nltk.download('vader_lexicon')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

sun_exposure_questions = [
    'On a hot summer day, do you find yourself laying all day in the sun or seeking shadow?',
    'Are you a morning person or a night owl?',
    'Do you consider yourself an introvert or an extrovert?'
]

personality_questions = [
    'Would you consider yourself to be an empath?',
    'Do you mind a high maintenance partner?',
    'Would you like to spend a lot of time with your partner?',
    'Are you the type of person that randomly gives presents?'
]

appearance_questions = [
    'On a scale from 1 (very ordinary) to 10 (fashion week), where would you see your looks?',
    'Do you focus more on looks or more on character?',
    'Do you prefer a lazy home outfit, or full out fashion week?'
]

size_questions = [
    'Would you describe your living space as luxurious and spacious, or small and cozy?',
    'Do you prefer a tall partner or a small partner?'
]

all_questions = [
    sun_exposure_questions,
    personality_questions,
    appearance_questions,
    size_questions
]

questions2ask = 3
questionsCnt = 0
alreadyMatched = False
stopWaiting = False


def initialize_plants():
    plants = [Plant(True, 'Spider plant', 'Peter', Personality.Sturdy, SunExposure.Indifferent, False, Size.Medium),
              Plant(True, 'Monstera monkey mask', 'Leia', Personality.Medium, SunExposure.Indirect, True, Size.Medium),
              Plant(True, 'Calathea Freddie', 'Freddie', Personality.Sensitive, SunExposure.Indirect, True, Size.Small),
              Plant(True, 'Ficus elastica', 'Tineke', Personality.Medium, SunExposure.Direct, True, Size.Small),
              Plant(True, 'Strelitzia', 'Wanda', Personality.Sensitive, SunExposure.Direct, False, Size.Huge),
              Plant(False, 'Pilea Peperomioides', 'Bill', Personality.Sturdy, SunExposure.Indifferent, False, Size.Small),
              Plant(False, 'Fan palm', 'Luke', Personality.Medium, SunExposure.Indirect, True, Size.Huge),
              Plant(False, 'Cowboy Cactus `Ephorbia`', 'Roger', Personality.Sturdy, SunExposure.Direct, True, Size.Medium),
              Plant(False, 'Alocasia macrorrhiza', 'Steve', Personality.Sensitive, SunExposure.Direct, False, Size.Huge),
              Plant(False, 'Mimosa pudica', 'Mimi', Personality.Sensitive, SunExposure.Direct, True, Size.Small)]

    return plants


def main():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("i43i0N9plzAa7wf4huwpxsvcN", "V7yAapEx33sxfR3HKTYYQVWlWdZA3acVVDynkXPau39BdK4V0M")
    auth.set_access_token("1360611491611869184-0OfpGHTFo9JYA3ZIaqJIKMNFdmPzve", "r45sGkAn1Y6c4GZZjbuxnmBbEVJB2DolDXapNab2ZVfL4")

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    while True:
        communicate(api)
        logger.info("Waiting...")
        time.sleep(15)


# Method used to for the communication of the bot
def communicate(api):
    # Loop through all tweets that the bot is mentioned
    for tweet in tweepy.Cursor(api.mentions_timeline).items():
        # Check if the tweet contains the 'match me' phrase
        if any(keyword in tweet.text.lower() for keyword in ['match me']):
            print('Tweet by: @' + tweet.user.screen_name)
            logger.info(f"Text is {tweet.text}")
            # Skip all the tweets which are replies to another status
            if tweet.in_reply_to_status_id is not None:
                continue

            logger.info(f"Answering to {tweet.user.name}")
            try:
                # Send the first question
                initial_question = api.update_status(
                    status='@%s Welcome to our plant matching program! <3 Quick thinking! Please describe yourself'
                           ' as you would in a Tinder bio - be creative, and use three adjectives.' % tweet.user.screen_name,
                    in_reply_to_status_id=tweet.id,
                    auto_populate_reply_metadata=True
                )

                # Flag to know when plant is matched to the person
                global alreadyMatched
                alreadyMatched = False

                # Flag to know when to stop waiting for user's answer (3x30 seconds)
                global stopWaiting
                stopWaiting = False

                # Counter for the questions (the bot will ask only 3 questions as total)
                global questionsCnt
                questionsCnt = 1

                # Reset the waiting counter
                waitingCounter1 = 0
                while True:
                    waitingCounter1 += 1
                    if waitingCounter1 > 3:
                        break

                    # Loop through all the tweets of the user
                    for user_reply in api.user_timeline(user_id=tweet.user.id):
                        # Check if this tweet is a reply to the question of the both
                        if user_reply.in_reply_to_status_id == initial_question.id:
                            # Initialize the plants in order to be able to filter them depending on the answers
                            plants = initialize_plants()
                            # Get the reply text without the tag of the bot (first 15 symbols)
                            text = user_reply.text[15:]

                            # Sentiment analysis in order to decide the positivity in the answer
                            SA = nltk.sentiment.vader.SentimentIntensityAnalyzer()
                            text_PS = SA.polarity_scores(text)
                            if text_PS['compound'] == 0:
                                logger.info(f"{user_reply.user.name} is so neutral person...")
                            elif text_PS['compound'] < 0:
                                # Get only the negative plants
                                plants = [plant for plant in plants if not plant.positive]
                            else:
                                # Get only the positive plants
                                plants = [plant for plant in plants if plant.positive]

                            # Method that proceeds the next questions
                            ask_next_question(api, user_reply, '', plants)

                    # Stop the loop if all the questions are asked, it is matched or bored from waiting the person
                    if questionsCnt == questions2ask | alreadyMatched | stopWaiting:
                        break

                    logger.info("Waiting for the first answer...")
                    time.sleep(30)

            except tweepy.TweepError as e:
                print(e.reason)

            except StopIteration:
                break


# Method that proceed the next questions
def ask_next_question(api, tweet, prev_question, plants):
    global alreadyMatched
    global stopWaiting
    global questionsCnt
    if questionsCnt == questions2ask:
        message = ''
        if len(plants) == 0:
            # Send constant plastic plant when there is no match
            message = 'Love has found you in a peculiar way.... I have matched you with a plastic plant! You can' \
                      ' always rely on them and they are very relaxed. Just the partner for you! I hope you invite me' \
                      ' to the wedding ;)'
        elif len(plants) == 1:
            # Send the matched plant
            message = 'Love has found you... It`s a match! I have matched you with %s. May you live happily ever after' \
                      ' <3' % plants[0].name
        else:
            # Send a random plant from all the matched ones
            random_plant_index = randint(0, len(plants) - 1)
            message = 'Love has found you... It`s a match! I have matched you with %s. May you live happily ever after' \
                      ' <3' % plants[random_plant_index].name

        # Final message for the match
        if message != '':
            api.update_status(
                status=message,
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True
            )
            # Set the flag to true, because the user is already matched with a plant
            alreadyMatched = True

        return

    # Next questions generation
    topic_index, question_index, next_question = generate_next_question(prev_question)

    # Send the next question
    question_tweet = api.update_status(
        status=next_question,
        in_reply_to_status_id=tweet.id,
        auto_populate_reply_metadata=True
    )

    questionsCnt += 1

    waitingCounter2 = 0
    while True:
        waitingCounter2 += 1
        if waitingCounter2 > 3:
            stopWaiting = True
            break

        for user_reply in api.user_timeline(user_id=tweet.user.id):
            if user_reply.in_reply_to_status_id == question_tweet.id:
                text = user_reply.text[15:]
                plants = filter_plants(topic_index, question_index, text.lower(), plants)
                ask_next_question(api, user_reply, next_question, plants)

        if alreadyMatched | stopWaiting:
            break

        logger.info("Waiting for the next answer...")
        time.sleep(30)


# Method to randomly generate the next questions
def generate_next_question(prev_question):
    next_topic_index = randint(0, len(all_questions) - 1)
    next_topic = all_questions[next_topic_index]
    next_question_index = randint(0, len(next_topic) - 1)
    next_question = next_topic[next_question_index]

    while next_question == prev_question:
        temp1, temp2, next_question = generate_next_question(prev_question)

    return next_topic_index, next_question_index, next_question


# Method to filter the plants based on the question and the answer
def filter_plants(topic, question, answer, plants):
    filtered_plants = []
    incorrect_answer = True
    if topic == 0:
        if question == 0:
            if ('sun' in answer) | ('sunny' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Direct]
            elif ('shadow' in answer) | ('dark' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Indirect]
        elif question == 1:
            if 'morning' in answer:
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Direct]
            elif ('night' in answer) | ('owl' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Indirect]
        elif question == 2:
            if 'introvert' in answer:
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Indirect]
            elif 'extrovert' in answer:
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Direct]

        if incorrect_answer:
            filtered_plants = [plant for plant in plants if plant.sun_exposure == SunExposure.Indifferent]
    elif topic == 1:
        if question == 0 | question == 2 | question == 3:
            if ('yes' in answer) | ('true' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.personality == Personality.Sensitive]
            elif ('no' in answer) | ('false' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.personality == Personality.Sturdy]

        if question == 1:
            if ('no' in answer) | ('false' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.personality == Personality.Sensitive]
            elif ('yes' in answer) | ('true' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.personality == Personality.Sturdy]

        if incorrect_answer:
            filtered_plants = [plant for plant in plants if plant.personality == Personality.Medium]
    elif topic == 2:
        if question == 0:
            if any(word in answer for word in ['1', '2', '3', '4', '5']):
                filtered_plants = [plant for plant in plants if not plant.looks]
            elif any(word in answer for word in ['6', '7', '8', '9', '10']):
                filtered_plants = [plant for plant in plants if plant.looks]
        elif question == 1:
            if 'looks' in answer:
                filtered_plants = [plant for plant in plants if plant.looks]
            elif ('character' in answer) | ('inside' in answer):
                filtered_plants = [plant for plant in plants if not plant.looks]
        elif question == 2:
            if 'fashion' in answer:
                filtered_plants = [plant for plant in plants if plant.looks]
            elif ('lazy' in answer) | ('home' in answer):
                filtered_plants = [plant for plant in plants if not plant.looks]
    elif topic == 3:
        if question == 0:
            if ('spacious' in answer) | ('luxurious' in answer) | ('huge' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.size == Size.Huge]
            elif ('small' in answer) | ('cozy' in answer):
                incorrect_answer = False
                filtered_plants = [plant for plant in plants if plant.size == Size.Small]
        elif question == 1:
            if ('tall' in answer) | ('long' in answer):
                filtered_plants = [plant for plant in plants if plant.size == Size.Huge]
            elif ('small' in answer) | ('mini' in answer):
                filtered_plants = [plant for plant in plants if plant.size == Size.Small]

        if incorrect_answer:
            filtered_plants = [plant for plant in plants if plant.size == Size.Medium]

    return filtered_plants


if __name__ == "__main__":
    main()

