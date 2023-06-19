from util.comment import RedditComment

class RedditPost:
    def __init__(self, post_data):
        self_post = post_data[0]['data']['children'][0]['data']
        
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
                    self.comments.append(RedditComment(comment_data))

    def sort_comments_by_popularity(self):
        pass
    
    def get_most_popular_comment(self):
        pass
            
    def __str__(self):
        return f"{self.title}:\n{self.post_body}"