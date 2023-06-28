from .comment import RedditComment
from .comment import NoCommentDataError

class NoPostDataError(Exception):
    pass

class RedditPost:
    def __init__(self, post_data):
        self_post = post_data[0]['data']['children'][0]['data']
        
        if 'subreddit' not in self_post.keys():
            raise NoPostDataError
        
        self.subreddit = self_post['subreddit']
        self.post_id = self_post['id']
        self.author = self_post['author']
        self.title = self_post['title']                               
        self.post_body = self_post['selftext']
        self.score = self_post['score']
        self.comments = []
        
        if len(post_data) > 1:
            for listing in post_data[1:]:
                for comment_data in listing['data']['children']:
                    try: self.comments.append(RedditComment(comment_data))
                    except NoCommentDataError: print("REDDIT API ERROR: No comment data, so comment was discarded.")

    def sort_comments_by_popularity(self):
        pass
    
    def get_most_popular_comment(self):
        pass
    
    def __eq__(self, other):
        if isinstance(other, RedditPost):
            return self.post_id == other.post_id
        return False
    
    def __hash__(self):
        return hash(self.post_id)
    
    def __str__(self):
        return f"{self.title}:\n{self.post_body}"