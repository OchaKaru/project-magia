from api.googledrive.driveapi import DriveAPI
from api.reddit.redditapi import RedditAPI

import fandom
import wikipedia

import csv
from collections import namedtuple

Question = namedtuple("Question", ["question", "answer"])

class DataCollector:
    def __init__(self, drive_cred_file: str = '../sessions/google-drive-cred.json'):
        self.google_drive = DriveAPI(drive_cred_file)
        self.reddit = RedditAPI("project-magia", by_line = "Kalvin Garcia")
        
        self.reddit.set_min_num_comments(1)
        
    def _get_all_reddit_posts(self, subreddit: str):
        posts = []
        post.extend(self.reddit.get_best_posts(subreddit))
        post.extend(self.reddit.get_hot_posts(subreddit))
        post.extend(self.reddit.get_new_posts(subreddit))
        post.extend(self.reddit.get_rising_posts(subreddit))
        post.extend(self.reddit.get_top_posts(subreddit))
        return list(set(posts))
        
    def _collect_questions(self):
        questions = []
        for subreddit in []:
            for post in self._get_all_reddit_posts(subreddit):
                for comment in post.comments:
                    questions.append(Question(str(post), str(comment)))
        with open("./datadump/questions.csv", "w", newline='', encoding='utf-8') as file:
            w = csv.writer(file)
            w.writerow(('question', 'answer'))
            w.writerows(questions)
            
    def _collect_anime_wiki_data():
        pass
    
    def _collect_manga_wiki_data():
        pass
    
    def _collect_game_wiki_data():
        pass
    
if __name__ == '__main__':
    dc = DataCollector()
    dc._collect_questions()
        