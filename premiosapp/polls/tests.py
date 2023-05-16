import datetime 

from django.test import TestCase
from django.utils import timezone
from .models import Question
from django.urls.base import reverse

#Testeamos, modelos o vistas
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """was published recently return False for questions pub_date in the future"""
        time = timezone.now()+datetime.timedelta(days=30)
        future_question= Question(question_text='¿Cuál es el mejor curso de IA?',pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)
    
    def test_was_published_recently_with_present_question(self):
        """was published recently return True for questions pub_date in the present"""
        time = timezone.now()
        present_question = Question(question_text='¿Cual es el mejor curso de IA?',pub_date=time)
        self.assertIs(present_question.was_published_recently(),True)
    
    def test_was_published_recently_with_less_than_a_day_gone(self):
        """was published recently return True for question pub_date with less than a day gone"""
        time=timezone.now() - datetime.timedelta(days=1)
        past_question_day_gone=Question(question_text='¿Cual es el mejor curso de IA?',pub_date=time)
        self.assertIs(past_question_day_gone.was_published_recently(),True)

    def test_was_published_with_more_than_one_day_past(self):
        """was published recently return False for questions pub_date with more than a day gone"""
        time=timezone.now() - datetime.timedelta(days=2)
        past_question_more_than_day= Question(question_text='¿Cual es el mejor curso de Ia?',pub_date=time)
        self.assertIs(past_question_more_than_day.was_published_recently(),False)

def create_question(question_text, days): 
    """
    Create a question with the given 'question_text' and published the given number
    of 'days' offset to now (negative for questions published in the past, positive
    for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    
    def test_no_questions(self):
        """if no questions exist, an appropiate message is displayed """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'Not polls are Available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_no_future_question_are_displayed(self):
        """If question future are create in DB,do not show up in the home"""
        response = self.client.get(reverse("polls:index"))
        time = timezone.now() + datetime.timedelta(days=30)
        future_question=create_question(question_text='¿Question?',days=20)
        self.assertContains(response, 'Not polls are Available')
        self.assertNotIn(future_question, response.context["latest_question_list"])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page"""
        question_past=create_question("Pregunta de prueba", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertIn(question_past, response.context['latest_question_list'])

    def test_future_question_and_past_question(self): 
        """
        Even if both past and future question exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self): 
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1", days=-30)
        question2 = create_question(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

    def test_two_future_question(self):
        """The questions index page may display multiple questions. """
        question_future1 = create_question(question_text="future1_question",days=30)
        question_future2 = create_question(question_text="future2_QUESTION",days=10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )
class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question=create_question(question_text="Future question.", days=30)
        url = reverse('polls:detail',args=(future_question.id,))
        response=self.client.get(url)
        self.assertEqual(response.status_code, 404)
        

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question=create_question(question_text="Past question.", days=-30)
        url = reverse('polls:detail',args=(past_question.id,))
        response=self.client.get(url)
        self.assertContains(response, past_question.question_text)