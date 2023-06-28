from api.googledrive.driveapi import DriveAPI

from api.reddit.redditapi import RedditAPI
import fandom
import wikipedia

import json
import csv
from collections import namedtuple

from time import sleep

Question = namedtuple("Question", ["question", "answer"])

class DataCollector:
    def __init__(self, drive_cred_file: str = '../sessions/google-drive-cred.json'):
        self.google_drive = DriveAPI(drive_cred_file)
        self.reddit = RedditAPI("project-magia", by_line = "Kalvin Garcia")
        
        self.reddit.set_min_num_comments(1)
        
    def _get_all_reddit_posts(self, subreddit: str):
        posts = []
        posts.extend(self.reddit.get_best_posts(subreddit))
        posts.extend(self.reddit.get_hot_posts(subreddit))
        posts.extend(self.reddit.get_new_posts(subreddit))
        posts.extend(self.reddit.get_rising_posts(subreddit))
        posts.extend(self.reddit.get_top_posts(subreddit))
        return list(set(posts))
        
    def _collect_questions(self):
        questions = []
        for subreddit in ["askanime", "animequestions", "VideoGameQuestions", "AskGamers," "ASKGAMING", "AskGames"]:
            for post in self._get_all_reddit_posts(subreddit):
                for comment in post.comments:
                    questions.append(Question(str(post), str(comment)))
        with open("./datadump/questions.csv", "w", newline='', encoding = 'utf-8') as file:
            w = csv.writer(file)
            w.writerow(('question', 'answer'))
            w.writerows(questions)
            file.close()

        file_metadata = {'name': "questions.csv", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/questions.csv", metadata = file_metadata, mimetype = 'text/csv')
            
    def _collect_anime_wiki_data(self):
        with open("./datadump/anime_corpus.txt", "w", encoding = 'utf-8') as file:
            anime = wikipedia.page("Anime")
            file.write("Anime\n\n" + anime.content + "\n\n")
            
            for link in anime.links:
                file.write(link + "\n\n" + wikipedia.page(link).content + "\n\n")
                sleep(1)
                
            list_of_links = []                
            for link in wikipedia.page("Lists of anime").links:
                if link.find("List of") != -1:
                    list_of_links.extend(wikipedia.page(link).links)
                    sleep(1)

            for link in list_of_links:
                file.write(link + "\n\n" + wikipedia.page(link).content + "\n\n")
                sleep(1)
            
            file.close()
            
        file_metadata = {'name': "anime_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/anime_corpus.txt", metadata = file_metadata, mimetype = 'text/plain')
            
    def _collect_manga_wiki_data(self):
        with open("./datadump/manga_corpus.txt", "w", encoding = 'utf-8') as file:
            manga = wikipedia.page("Manga")
            file.write("Manga\n\n" + manga.content + "\n\n")
            
            for link in manga.links:
                file.write(link + "\n\n" + wikipedia.page(link).content + "\n\n")
                sleep(1)
                
            list_of_links = []                
            for link in wikipedia.page("Lists of manga").links:
                if link.find("List of") != -1:
                    list_of_links.extend(wikipedia.page(link).links)
                    sleep(1)

            for link in list_of_links:
                file.write(link + "\n\n" + wikipedia.page(link).content + "\n\n")
                sleep(1)
            
            file.close()
        
        file_metadata = {'name': "manga_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/manga_corpus.txt", metadata = file_metadata, mimetype = 'text/plain')
    
    def _collect_game_wiki_data(self):
        with open("./datadump/game_corpus.txt", "w", encoding = 'utf-8') as file:
            game = wikipedia.page("Video game")
            file.write("Video game\n\n" + game.content + "\n\n")
            
            for link in manga.links:
                file.write(link + "\n\n" + wikipedia.page(link).content + "\n\n")
                sleep(1)
                
            list_of_links = []                
            for link in wikipedia.page("Lists of video games").links:
                if link.find("List of") != -1:
                    list_of_links.extend(wikipedia.page(link).links)
                    sleep(1)

            for link in list_of_links:
                file.write(link + "\n\n" + wikipedia.page(link).content + "\n\n")
                sleep(1)
            
            file.close()
        
        file_metadata = {'name': "game_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/game_corpus.txt", metadata = file_metadata, mimetype = 'text/plain')
    
    def collect_data(self):
        with open("../sessions/dataloc.json", "rw", encode = 'utf-8') as file:
            data_loc = json.loads(file.read())
        
            data_loc['corpus_drive_ids'] = {}
            data_loc['corpus_drive_ids']['questions'] = self._collect_questions()
            data_loc['corpus_drive_ids']['anime'] = self._collect_anime_wiki_data()
            data_loc['corpus_drive_ids']['manga'] = self._collect_manga_wiki_data()
            data_loc['corpus_drive_ids']['games'] = self._collect_game_wiki_data()
            
            file.write(json.dump(data_loc))
            file.close()

    def download_data(self, file_drive_id: str) -> bytes:
        return self.google_drive.download(file_drive_id)..getvalue()
    
if __name__ == '__main__':
    DataCollector().collect_data()
        