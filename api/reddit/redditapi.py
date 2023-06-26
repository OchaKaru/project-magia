import requests
from time import sleep

from util.post import RedditPost

class RedditAPI:    
    def __init__(self, app_id: str, version: str = "v0.1.0", by_line: str = "anon", platform: str = "linux"):
        self.BEST_POSTS_URL = "https://www.reddit.com/r/{}/best.json?{}"
        self.HOT_POSTS_URL = "https://www.reddit.com/r/{}/hot.json?{}"
        self.NEW_POSTS_URL = "https://www.reddit.com/r/{}/new.json?{}"
        self.RISING_POSTS_URL = "https://www.reddit.com/r/{}/new.json?{}"
        self.TOP_POSTS_URL = "https://www.reddit.com/r/{}/rising.json?{}"
        self.POST_COMMENTS_URL = "https://www.reddit.com/r/{}/comments/{}.json"
        
        self.headers = {'User-Agent': f'{platform}:{app_id}:{version} (by {by_line})'}
        
        self.filters = {
            'min_upvote_ratio': 0.0,
            'max_upvote_ratio': 1.0,
            'min_score': 0,
            'max_score': float('inf'),
            'min_len_media_embeded': 0,
            'max_len_media_embeded': float('inf'),
            'is_reddit_media_domain': False,
            'is_meta': False,
            'post_hint': None,
            'over_18': False,
            'media_only': False,
            'min_num_comments': 0,
            'max_num_comments': float('inf'),
            'is_video': False
        }
    
    def set_min_upvote_ratio(self, min_upvote_ratio: float):
        self.filters['min_upvote_ratio'] = min_upvote_ratio
        
    def set_max_upvote_ratio(self, max_upvote_ratio: float):
        self.filters['max_upvote_ratio'] = max_upvote_ratio
        
    def set_min_score(self, min_score: int):
        self.filters['min_score'] = min_score
    
    def set_max_score(self, max_score: int):
        self.filters['max_score'] = max_score
        
    def set_min_len_media_embeded(self, min_len_media_embeded: int):
        self.filters['min_len_media_embeded'] = min_len_media_embeded
    
    def set_max_len_media_embeded(self, max_len_media_embeded: int):
        self.filters['max_len_media_embeded'] = max_len_media_embeded
        
    def set_is_reddit_media_domain(self, is_reddit_media_domain: bool):
        self.filters['is_reddit_media_domain'] = is_reddit_media_domain
        
    def set_is_meta(self, is_meta: bool):
        self.filters['is_meta'] = is_meta
        
    def set_post_hint(self, post_hint: str):
        self.filters['post_hint'] = post_hint
    
    def set_over_18(self, over_18: bool):
        self.filters['over_18'] = over_18
        
    def set_media_only(self, media_only: bool):
        self.filters['media_only'] = media_only
        
    def set_min_num_comments(self, min_num_comments: int):
        self.filters['min_num_comments'] = min_num_comments
        
    def set_max_num_comments(self, max_num_comments: int):
        self.filters['max_num_comments'] = max_num_comments
        
    def set_is_video(self, is_video: bool):
        self.filters['is_video'] = is_video
        
    def _match_filters(self, link_data) -> bool:
        if link_data['upvote_ratio'] < self.filters['min_upvote_ratio'] or link_data['upvote_ratio'] > self.filters['max_upvote_ratio']:
            return False
        if link_data['score'] < self.filters['min_score'] or link_data['score'] > self.filters['max_score']:
            return False
        if len(link_data['media_embed']) < self.filters['min_len_media_embeded'] or len(link_data['media_embed']) > self.filters['max_len_media_embeded']:
            return False
        if link_data['is_reddit_media_domain'] != self.filters['is_reddit_media_domain'] or link_data['is_meta'] != self.filters['is_meta']:
            return False
        if link_data['media_only'] != self.filters['media_only'] or link_data['is_video'] != self.filters['is_video'] or link_data['over_18'] != self.filters['over_18']:
            return False
        if self.filters['post_hint'] is not None and link_data['post_hint'] != self.filters['post_hint']:
            return False
        if link_data['num_comments'] < self.filters['min_num_comments'] or link_data['num_comments'] > self.filters['max_num_comments']:
            return False
        
        return True

    def _get_post_by_id(self, subreddit: str, post_id: str) -> RedditPost:
        response = requests.get(self.POST_COMMENTS_URL.format(subreddit, post_id), headers = self.headers)

        if response.ok:
            return RedditPost(response.json())
        else:
            print(f'Error {response.status_code}')
            return None
            
    def _add_post_to_list(self, post_list: list, subreddit: str, link_data):
        if self._match_filters(link_data):
            post = self._get_post_by_id(subreddit, link_data['id'])
            if post is not None:
                post_list.append(post)
        
    def get_best_posts(self, subreddit, after: str = "", before: str = "") -> list:
        posts = []
        
        done = False
        while done is not True:
            params = f"after={after}&before={before}"
        
            response = requests.get(self.BEST_POSTS_URL.format(subreddit, params), headers = self.headers)            
            if response.ok:
                listing_data = response.json()['data']

                for link_json in listing_data['children']:
                    link_data = link_json['data']
                    self._add_post_to_list(posts, subreddit, link_data)
                    sleep(1)

                if listing_data['after'] == None:
                    done = True

                after = listing_data['after']
                before = ""
            else:
                print(f'Error {response.status_code}')
                break
                
            sleep(1)
                
        return posts
        
    def get_hot_posts(self, subreddit, region: str = "GLOBAL", after: str = "", before: str = "") -> list:
        posts = []
        
        done = False
        while done is not True:
            params = f"g={region}&after={after}&before={before}"
        
            response = requests.get(self.HOT_POSTS_URL.format(subreddit, params), headers = self.headers)            
            if response.ok:
                listing_data = response.json()['data']

                for link_json in listing_data['children']:
                    link_data = link_json['data']
                    self._add_post_to_list(posts, subreddit, link_data)
                    sleep(1)
                        
                if listing_data['after'] == None:
                    done = True

                after = listing_data['after']
                before = ""
            else:
                print(f'Error {response.status_code}')
                break
                
            sleep(1)
                
        return posts
                
    def get_new_posts(self, subreddit, after: str = "", before: str = "") -> list:
        posts = []
        
        done = False
        while done is not True:
            params = f"after={after}&before={before}"
        
            response = requests.get(self.NEW_POSTS_URL.format(subreddit, params), headers = self.headers)          
            if response.ok:
                listing_data = response.json()['data']

                for link_json in listing_data['children']:
                    link_data = link_json['data']
                    self._add_post_to_list(posts, subreddit, link_data)
                    sleep(1)
                        
                if listing_data['after'] == None:
                    done = True

                after = listing_data['after']
                before = ""
            else:
                print(f'Error {response.status_code}')
                break
                
            sleep(1)
                
        return posts
                
    def get_rising_posts(self, subreddit, after: str = "", before: str = "") -> list:
        posts = []
        
        done = False
        while done is not True:
            params = f"after={after}&before={before}"
        
            response = requests.get(self.RISING_POSTS_URL.format(subreddit, params), headers = self.headers)            
            if response.ok:
                listing_data = response.json()['data']

                for link_json in listing_data['children']:
                    link_data = link_json['data']
                    self._add_post_to_list(posts, subreddit, link_data)
                    sleep(1)
                        
                if listing_data['after'] == None:
                    done = True

                after = listing_data['after']
                before = ""
            else:
                print(f'Error {response.status_code}')
                break
                
            sleep(1)
                
        return posts

    def get_top_posts(self, subreddit, time: str = "all", after: str = "", before: str = "") -> list:
        posts = []
        
        done = False
        while done is not True:
            params = f"t={time}&after={after}&before={before}"
        
            response = requests.get(self.TOP_POSTS_URL.format(subreddit, params), headers = self.headers)
            if response.ok:
                listing_data = response.json()['data']

                for link_json in listing_data['children']:
                    link_data = link_json['data']
                    self._add_post_to_list(posts, subreddit, link_data)
                    sleep(1)
                        
                if listing_data['after'] == None:
                    done = True

                after = listing_data['after']
                before = ""
            else:
                print(f'Error {response.status_code}')
                break
                
            sleep(1)
                
        return posts
    
if __name__ == '__main__':
    reddit = RedditAPI("project-magia", by_line = "Kalvin Garcia")
    print(reddit.get_top_posts("animequestions", time = "day")[0].comments[0])