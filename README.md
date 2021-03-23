# TwitterBot
Twitter bot that is used to match people with plants

# How prepare the environment
Before running the script, do this:
1. Create a virtual environment
	* $ python3 -m venv venv
	* $ source venv/bin/activate
2. Install the dependencies
	* $ pip install tweepy
	* $ pip install nltk
3. Obtain API keys from twitter
4. Fill them in in the script below

# How to communicate with the bot
1. You need to tweet to the bot a text that includes the text 'match me'
2. Then the bot will answer in 15 seconds with an questions that you need to answer
3. You answer the question that the bot asked you
4. Then the bot will ask you another question and will wait 3x30 seconds for your answer, afterwards it will leave you.
5. You need to answer this questions, too
6. Then the bot will ask the last third question and will wait again 3x30 seconds for the answer.
7. When you answer the last (third) questions, the bot will match you with a special plant
8. Then the bot will continue with the other tweets, if there are any
