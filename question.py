class Question():
    class Type():
        multiple_choice = 1
        text = 2
    def __init__(self, id):
        self.id = id
        self.question = None
        self.type = None
        self.answers = []
        self.correct_answers = []
        self.media = None

class Answer():
    def __init__(self, id):
        self.id = id
        self.answer = None
