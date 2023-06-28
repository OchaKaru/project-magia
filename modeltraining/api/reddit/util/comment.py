class NoCommentDataError(Exception):
    pass

class RedditComment:
    def __init__(self, comment_data):
        comment = comment_data['data']
        
        if 'subreddit' not in comment.keys():
            raise NoCommentDataError

        self.subreddit = comment['subreddit']
        self.author = comment['author']
        self.comment_body = comment['body']
        self.score = comment['score']
        
        self.comments = []
        
        if comment['replies'] != "":
            for comment_data in comment['replies']['data']['children']:
                try: self.comments.append(RedditComment(comment_data))
                except NoCommentDataError: print("REDDIT API ERROR: No comment data, so comment was discarded.")
                
    def __str__(self):
        return self.comment_body
            
        