import os
import openai
import random
import re


class MainQuiz:
    def remove_a_followed_by_number(self, s):
        # Use a regular expression to match the pattern "A" followed by one or more digits
        pattern = r"A\d+(.|:)?"
        # Replace any matches with an empty string
        return re.sub(pattern, "", s)

    def remove_a_followed_by_colon(self, s):
        # Use a regular expression to match the pattern "A:"
        pattern = r"A:"
        # Replace any matches with an empty string
        return re.sub(pattern, "", s)



    def get_token_amount(self, text):
        updated_text = "".join(text.split())
        self.tokens = (len(updated_text) / 4)
        return self.tokens

    def paragraph(self, paragraph):
        self.paragraph = paragraph
        self.text_chunk = []
        chunk = ""
        for i in self.paragraph.split("."):
            if self.get_token_amount(chunk) < 1200:
                chunk += (i + ".")
            else:
                self.text_chunk.append(chunk)
                chunk = ""

        self.text_chunk.append(chunk)
        return self.text_chunk



    def generate_questions(self, paragraph):

        openai.api_key = os.environ.get("OPENAIKEY")
        question = f"Write 10 short quiz questions from the lesson transcript below with simple answers and format the quiz with the Q and A separated by an @ symbol:\n\n{paragraph}\n\n"
        quiz_questions = openai.Completion.create(model="text-davinci-003", prompt=question, max_tokens=500, temperature=0)
        return quiz_questions["choices"][0]["text"].replace("\n", "")


    def format_quiz(self):

        self.quiz = []
        for i in self.text_chunk:
            print(i)
            try:
                self.quiz += self.generate_questions(paragraph=i).split("Q")
            except:
                break


        print(self.quiz)
        for i in self.quiz:
            if "@A" in i:
                self.answers = [i.split("@A") for i in self.quiz]
            if f"A{self.quiz.index(i) + 1}" in i:
                self.answers = [i.split(f"A{self.quiz.index(i) + 1}") for i in self.quiz]
            if "@a" in i:
                self.answers = [i.split("@a") for i in self.quiz]
            elif "@" in i:
                self.answers = [i.split("@") for i in self.quiz]
            elif ":" in i:
                self.answers = [i.split(":") for i in self.quiz]


        self.final_quiz = {}

        print(self.answers)

        for question in self.answers:
            if question != [''] and question != [' '] and len(question) == 2:
                if question[1] != f"{self.answers.index(question)}: " and question[1] != f"{self.answers.index(question)}. " and question[1] != '' and question[1] != ' ':
                    item = self.remove_a_followed_by_number(question[1])
                    self.final_quiz[question[0][2:].strip().replace(":", "").replace(".", "")] = self.remove_a_followed_by_colon(item).replace(".", "").strip()




        print(self.final_quiz)

        return self.final_quiz

    def spacing(self, index, questions):
        if (index + 3) > len(questions) - 1:
            return (index + 3) - (len(questions) - 1)
        else:
            return index + 3


    def multiple_answers(self, questions):

        openai.api_key = os.environ.get("OPENAIKEY")
        question = f"Write 3 different incorrect answers using this answer below. Separate each answer with only an @ symbol and make each wrong answer similar length to the correct answer.\n\n{questions}\n\n"
        try:
            ai_text = openai.Completion.create(model="text-davinci-003", prompt=question, max_tokens=500,
                                                            temperature=0)["choices"][0]["text"].split("@")
        except:
            ai_text = "Error Occurred"


        random.shuffle(ai_text)
        ai_text = [self.remove_a_followed_by_colon(i.replace(":", "").replace("\n", "").replace(".", "")).strip() for i in ai_text if i != "" and i != " " and i != "\n" and i != "\n\n"]

        print(ai_text)
        return ai_text



