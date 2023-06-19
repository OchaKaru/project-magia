class RedditComment:
    def __init__(self, comment_data):
        comment = comment_data['data']
        
        self.subreddit = comment['subreddit']
        self.author = comment['author']
        self.comment_body = comment['body']
        self.score = comment['score']
        
        self.comments = []
        
        if comment['replies'] != "":
            for comment_data in comment['replies']['data']['children']:
                self.comments.append(RedditComment(comment_data))
                
    def __str__(self):
        return self.comment_body
            
        