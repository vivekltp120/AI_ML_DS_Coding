__author__ = "Vivek"
__author_email__ = "vivekltp120@gmail.com"
import time
inspiring_quotes = [
    "The best way to predict the future is to create it. – Abraham Lincoln",
    "Your time is limited, so don’t waste it living someone else’s life. – Steve Jobs",
    "In the middle of every difficulty lies opportunity. – Albert Einstein",
    "Do what you can, with what you have, where you are. – Theodore Roosevelt",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
    "Don’t count the days, make the days count. – Muhammad Ali",
    "You miss 100% of the shots you don’t take. – Wayne Gretzky",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "It always seems impossible until it’s done. – Nelson Mandela",
    "Happiness is not something ready-made. It comes from your own actions. – Dalai Lama",
    "Dream big and dare to fail. – Norman Vaughan",
    "The only way to do great work is to love what you do. – Steve Jobs",
    "If you want to lift yourself up, lift up someone else. – Booker T. Washington",
    "Act as if what you do makes a difference. It does. – William James",
    "Keep your face always toward the sunshine—and shadows will fall behind you. – Walt Whitman",
    "The purpose of our lives is to be happy. – Dalai Lama",
    "Success usually comes to those who are too busy to be looking for it. – Henry David Thoreau",
    "You only live once, but if you do it right, once is enough. – Mae West",
    "Life is what happens when you’re busy making other plans. – John Lennon",
    "Do not go where the path may lead, go instead where there is no path and leave a trail. – Ralph Waldo Emerson",
    "The harder you work for something, the greater you’ll feel when you achieve it. – Anonymous",
    "Push yourself, because no one else is going to do it for you. – Anonymous",
    "Great things never come from comfort zones. – Anonymous",
    "Success doesn’t just find you. You have to go out and get it. – Anonymous",
    "The only limit to our realization of tomorrow is our doubts of today. – Franklin D. Roosevelt",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. – Ralph Waldo Emerson",
    "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
    "It does not matter how slowly you go as long as you do not stop. – Confucius",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
    "I am not a product of my circumstances. I am a product of my decisions. – Stephen Covey",
    "The only person you are destined to become is the person you decide to be. – Ralph Waldo Emerson",
    "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. – Christian D. Larson",
    "Hardships often prepare ordinary people for an extraordinary destiny. – C.S. Lewis",
    "Be the change that you wish to see in the world. – Mahatma Gandhi",
    "You are never too old to set another goal or to dream a new dream. – C.S. Lewis",
    "Don’t be pushed around by the fears in your mind. Be led by the dreams in your heart. – Roy T. Bennett",
    "Whether you think you can or think you can’t, you’re right. – Henry Ford",
    "Start where you are. Use what you have. Do what you can. – Arthur Ashe",
    "What you get by achieving your goals is not as important as what you become by achieving your goals. – Zig Ziglar",
    "The journey of a thousand miles begins with one step. – Lao Tzu",
    "Success is walking from failure to failure with no loss of enthusiasm. – Winston Churchill"
]
from colorama import Fore,Back,Style
import random
if __name__=="__main__":
    while True:
        print(Fore.GREEN,random.choice(inspiring_quotes))
        time.sleep(4)


