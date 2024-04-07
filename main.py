import os
import random
import re
import time

from openai import OpenAI


class MainQuiz:

    def __init__(self, api_key, quiz_length):
        self.api_key = api_key
        self.quiz_length = quiz_length
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
            if i != "":
                if self.get_token_amount(chunk) < 1600:
                    chunk += (i + ".")
                else:
                    self.text_chunk.append(chunk)
                    break


        self.text_chunk.append(chunk)
        print(self.get_token_amount(chunk))
        return self.text_chunk



    def generate_questions(self, paragraph):
        client = OpenAI(api_key=self.api_key)
        
        question = f"Write {self.quiz_length} short quiz questions from only the lesson transcript below with simple answers and format the quiz with the Q and A separated by an @ symbol. Example: 'Q When did WW2 start A September 1939@ Q What colour is the sky A Blue' Transcript:\n\n{paragraph}\n\n"
        quiz_questions = client.chat.completions.create(
                          model="gpt-3.5-turbo",
                          messages=[{"role": "system", "content": question}], max_tokens=2000, temperature=0)
        return quiz_questions.choices[0].message.content.replace("\n", "")


    def format_quiz(self, db, QuizNames, new_quiz_name, app):
        print(len(self.text_chunk))
        self.quiz = []
        for i in self.text_chunk:
            print(i)
            try:
                self.quiz += self.generate_questions(paragraph=i).split("Q")
                
            except:
                time.sleep(10)
                continue
        print("-------QUIZ----------")
        print(self.quiz)
        print("End of Quiz")
        if self.quiz == []:
            return "FAILED"
        with app.app_context():
            db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 50
            db.session.commit()

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

        
        for question in self.answers:
            if question != [''] and question != [' '] and len(question) == 2:
                print("----Question---------")
                print(question)
                print("End of Question")
                if question[1] != f"{self.answers.index(question)}: " and question[1] != f"{self.answers.index(question)}. " and question[1] != '' and question[1] != ' ':
                    item = self.remove_a_followed_by_number(question[1])
                    self.final_quiz[question[0][2:].strip().replace(":", "").replace(".", "")] = self.remove_a_followed_by_colon(item).replace(".", "").strip()

        with app.app_context():
            db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 80
            db.session.commit()


        print(self.final_quiz)

        return self.final_quiz

    def spacing(self, index, questions):
        if (index + 3) > len(questions) - 1:
            return (index + 3) - (len(questions) - 1)
        else:
            return index + 3


    def multiple_answers(self, questions):

        client = OpenAI(api_key=self.api_key)
        question = f"Write 3 different hard incorrect answers using this answer below. Separate each answer with only an @ symbol and make each wrong answer similar length to the correct answer.\n\n{questions}\n\n"
        try:
            ai_text = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": question}], max_tokens=1000, temperature=0).choices[0].message.content.split("@")
            
        except:
            ai_text = "Error Occurred"


        random.shuffle(ai_text)
        ai_text = [self.remove_a_followed_by_colon(i.replace(":", "").replace("\n", "").replace(".", "")).strip() for i in ai_text if i != "" and i != " " and i != "\n" and i != "\n\n"]

        print(ai_text)
        return ai_text

