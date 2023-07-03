from api.googledrive.driveapi import DriveAPI

from api.reddit.redditapi import RedditAPI
import fandom
from wikipediaapi import Wikipedia

import json
import csv
from collections import namedtuple

from time import sleep

Question = namedtuple("Question", ["question", "answer"])

class PageMustNotExistError(Exception):
    pass

class DataCollector:
    def __init__(self, drive_cred_file: str = '../sessions/google-drive-cred.json'):
        self.google_drive = DriveAPI(drive_cred_file)
        self.wikipedia = Wikipedia('Project Magia v0.1.0 (by Kalvin Garcia)', 'en')
        self.reddit = RedditAPI("project-magia", by_line = "Kalvin Garcia")
        
        self.reddit.set_min_num_comments(1)

        with open("./datadump/status.json", "r") as file:
            self.status = json.loads(file.read())
            if self.status['visited'] == "":
                self.status['visited'] = {}
                
    def _dump_status(self):
        with open("./datadump/status.json", "w") as file:
            json.dump(self.status, file)
            file.close()

    def _get_all_reddit_posts(self, subreddit: str):
        posts = []
        posts.extend(self.reddit.get_best_posts(subreddit))
        posts.extend(self.reddit.get_hot_posts(subreddit))
        posts.extend(self.reddit.get_new_posts(subreddit))
        posts.extend(self.reddit.get_rising_posts(subreddit))
        posts.extend(self.reddit.get_top_posts(subreddit))
        return list(set(posts))
        
    def _collect_questions(self):
        if self.status['questions']['status'] == 'uncommenced':
            file = open("./datadump/questions.csv", "w", newline='', encoding = 'utf-8')
        else:
            file = open("./datadump/questions.csv", "a", newline='', encoding = 'utf-8')
        
        w = csv.writer(file)
        w.writerow(('question', 'answer'))
        while len(self.status['questions']['list_of_subreddits']) > 0:
            questions = []
            for post in self._get_all_reddit_posts(self.status['questions']['list_of_subreddits'].pop()):
                for comment in post.comments:
                    questions.append(Question(str(post), str(comment)))
            w.writerows(questions)
            self._dump_status()
        file.close()

        file_metadata = {'name': "questions.csv", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        self.status['questions']['status'] = 'complete'
        return self.google_drive.resumable_upload("./datadump/questions.csv", metadata = file_metadata, mimetype = 'text/csv')
    
    def _attempt_page_access(self, page: str):
        count = 0
        while True:
            try: return self.wikipedia.page(page)
            except:
                if count > 100:
                    raise PageMustNotExistError
                count += 1

    def _get_wiki_data(self, page: str):
        try:
            wiki_page = self._attempt_page_access(page)
            if wiki_page.exists and not self.status['visited'].get(page, False):
                self.status['visited'][page] = True
                sleep(1)
                return page + "\n\n" + wiki_page.text + "\n\n"  
            else:
                return ""
        except PageMustNotExistError:
            return ""
    
    def _get_related_data(self, page: str):
        related_information = ""
        try:
            for link in self._attempt_page_access(page).links:
                if link.find("List of") == -1:
                    related_information += self._get_wiki_data(link)
            return related_information
        except PageMustNotExistError:
            return related_information

    def _get_list_links(self, page: str):
        list_of_links = []
        
        try:
            for link in self._attempt_page_access(page).links:
                wiki_page = self._attempt_page_access(link)
                if link.find("List of") != -1 and wiki_page.exists and not self.status['visited'].get(link, False):
                    self.status['visited'][link] = True
                    sleep(1)
                    list_of_links.extend(wiki_page.links)
            return list_of_links
        except PageMustNotExistError:
            return list_of_links

    def _collect_anime_wiki_data(self) -> str:
        if self.status['anime']['status'] == 'uncommenced':
            file = open("./datadump/anime_corpus.txt", "w", encoding = 'utf-8')

            self.status['anime']['status'] = 'incomplete'
            file.write(self._get_wiki_data("Anime"))
            file.write(self._get_related_data('Anime'))

            self.status['anime']['list_of_anime'] = self._get_list_links("Lists of anime")
            self._dump_status()
        else:
            file = open("./datadump/anime_corpus.txt", "a", encoding = 'utf-8')

        while len(self.status['anime']['list_of_anime']) > 0:
            text_to_append = ""
            for _ in range(100):
                page = self.status['anime']['list_of_anime'].pop(0)
                text_to_append += self._get_wiki_data(page)
                text_to_append += self._get_related_data(page)
            file.write(text_to_append)
            self._dump_status()
        file.close()
            
        file_metadata = {'name': "anime_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/anime_corpus.txt", metadata = file_metadata, mimetype = 'text/plain')
            
    def _collect_manga_wiki_data(self) -> str:
        if self.status['manga']['status'] == 'uncommenced':
            file = open("./datadump/manga_corpus.txt", "w", encoding = 'utf-8')
            
            self.status['manga']['status'] = 'incomplete'
            file.write(self._get_wiki_data("Manga"))
            file.write(self._get_related_data('Manga'))

            self.status['manga']['list_of_manga'] = self._get_list_links("Lists of manga")
            self._dump_status()
        else:
            file = open("./datadump/manga_corpus.txt", "a", encoding = 'utf-8')

        while len(self.status['manga']['list_of_manga']) > 0:
            text_to_append = ""
            for _ in range(50):
                page = self.status['manga']['list_of_manga'].pop(0)
                text_to_append += self._get_wiki_data(page)
                text_to_append += self._get_related_data(page)
            file.write(text_to_append)
            self._dump_status()
        file.close()
        
        file_metadata = {'name': "manga_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/manga_corpus.txt", metadata = file_metadata, mimetype = 'text/plain')
    
    def _collect_game_wiki_data(self) -> str:
        if self.status['games']['status'] == 'uncommenced':
            file = open("./datadump/game_corpus.txt", "w", encoding = 'utf-8')
            
            self.status['games']['status'] = 'incomplete'
            file.write(self._get_wiki_data("Video games"))
            file.write(self._get_related_data('Video games'))

            self.status['games']['list_of_games'] = self._get_list_links("Lists of video games")
            self._dump_status()
        else:
            file = open("./datadump/game_corpus.txt", "a", encoding = 'utf-8')

        while len(self.status['games']['list_of_games']) > 0:
            text_to_append = ""
            for _ in range(50):
                page = self.status['games']['list_of_games'].pop(0)
                text_to_append += self._get_wiki_data(page)
                text_to_append += self._get_related_data(page)
            file.write(text_to_append)
            self._dump_status()
        file.close()
        
        file_metadata = {'name': "game_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
        return self.google_drive.resumable_upload("./datadump/game_corpus.txt", metadata = file_metadata, mimetype = 'text/plain')
    
    def collect_data(self):
        file = open("../sessions/modelinfo/dataloc.json", "r", encoding = 'utf-8')
        data_loc = json.loads(file.read())
        if data_loc['corpus_drive_ids'] == "":
            data_loc['corpus_drive_ids'] = {}
        file.close()

        if self.status['questions']['status'] != "complete":
            print("Questions")
            data_loc['corpus_drive_ids']['questions'] = self._collect_questions()
            file = open("../sessions/modelinfo/dataloc.json", "w", encoding = 'utf-8')
            json.dump(data_loc, file)
            file.close()
        
        if self.status['anime']['status'] != "complete":
            print("Anime")
            data_loc['corpus_drive_ids']['anime'] = self._collect_anime_wiki_data()
            file = open("../sessions/modelinfo/dataloc.json", "w", encoding = 'utf-8')
            json.dump(data_loc, file)
            file.close()

        if self.status['manga']['status'] != "complete":
            print("Manga")
            data_loc['corpus_drive_ids']['manga'] = self._collect_manga_wiki_data()
            file = open("../sessions/modelinfo/dataloc.json", "w", encoding = 'utf-8')
            json.dump(data_loc, file)
            file.close()

        if self.status['games']['status'] != "complete":
            print("Games")
            data_loc['corpus_drive_ids']['games'] = self._collect_game_wiki_data()
            file = open("../sessions/modelinfo/dataloc.json", "w", encoding = 'utf-8')
            json.dump(data_loc, file)
            file.close()

    def download_data(self, file_drive_id: str) -> bytes:
        return self.google_drive.download(file_drive_id).getvalue()
    
if __name__ == '__main__':
    DataCollector().collect_data()
        