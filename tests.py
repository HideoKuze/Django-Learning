from django.test import TestCase
#Amend other tests so they will pass the polls without choices test
# Create your tests here.
import datetime
from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from polls.models import Poll, Choice

def create_poll(question, days):
		"""
		Creates a poll with the given 'question' published the given number of 'days' offset to now
		now (negative for polls published in the past,  positive for polls that have yet to be published).
		"""
		return Poll.objects.create(question=question,pub_date=timezone.now() + datetime.timedelta(days=days))	

class PollMethodTests(TestCase):
	#Testing the function from the Poll class

	def test_was_published_recently_with_future_poll(self):
		"""was_published_recently() should return False for polls whose
		pub_date is in the future"""

		future_poll = Poll(pub_date=timezone.now() + datetime.timedelta(30))
		self.assertEqual(future_poll.was_published_recently(), False)

	def test_was_published_recently_with_old_poll(self):
		"""
		was_published_recently() should return False for polls whose pub_date
		is older than 1 day
		"""
		old_poll = Poll(pub_date=timezone.now() - datetime.timedelta(days=30))
		self.assertEqual(old_poll.was_published_recently(), False)

	def test_was_published_recently_with_recent_poll(self):
		"""
		was_published_recently should return True for polls whose pub_date 
		is within the last day
		"""
		#We're creating an object to test 
		recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=1))
		self.assertEqual(recent_poll.was_published_recently(), True)


class PollViewTests(TestCase):
	def test_index_view_with_a_past_poll(self):
		"""
		Polls with pub_date in the past should be displayed.
		"""
		#Create_poll is a factory method, to remove repetition
		create_poll(question="Past poll.", days=-30).choice_set.create(choice_text='now full')
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['latest_poll_list'],
			['<Poll: Past poll.>']
			)

	def test_index_view_with_a_future_poll(self):
		"""Polls with a pub_date in the future should not be displayed on the index page."""
		#Needed to amend each line where we created a poll with code that would also give that 
		#poll at least one choice, so when we test for polls with choices we don't have 
		#tests conflicting with each other
		create_poll(question="future_poll", days=30).choice_set.create(choice_text='now full')
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, 'No polls are available.', status_code=200)
		self.assertQuerysetEqual(response.context['latest_poll_list'],[])

	def test_index_view_with_no_polls(self):
		"""
		If no polls exist, an appropriate message should be displayed.

		"""
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No polls are available')
		self.assertQuerysetEqual(response.context['latest_poll_list'], [])

	def test_index_view_with_future_poll_and_past_poll(self):
		"""
		Even if both past and future polls exist, only past polls should be
		displayed.
		"""

		create_poll(question='past poll', days=-30).choice_set.create(choice_text='now full')
		create_poll(question='future poll', days=30).choice_set.create(choice_text='now full')
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_poll_list'],
			['<Poll: past poll>'])

	def test_index_view_with_two_past_polls(self):
		'''
		The polls index page may display multiple polls.
		'''

		create_poll(question='past poll 1.', days=-30).choice_set.create(choice_text='now full')
		create_poll(question='past poll 2.', days=-30).choice_set.create(choice_text='now full 2')

		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: past poll 1.>', '<Poll: past poll 2.>'])

class PollIndexDetailTests(TestCase):
	def test_detail_view_with_a_future_poll(self):
		"""
		The detail view of a poll with a pub_date in the future should return 
		404 not found
		"""
		future_poll = create_poll(question='Future poll.', days=5)
		future_poll_choice = future_poll.choice_set.create(choice_text='Hello')
		response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
		self.assertEqual(response.status_code, 404)

	def test_detail_view_with_a_past_poll(self):
		""" The detail view of a poll with a pub_date in the past should return 200
		"""
		past_poll = create_poll(question='Past poll', days=-5)
		response = self.client.get(reverse("polls:detail", args=(past_poll.id,)))
		self.assertContains(response, past_poll.question, status_code=200)

class PollsAndChoices(TestCase):
	""" A poll without choices should not be displayed
	"""
	def test_poll_without_choices(self):
		#first make an empty poll to use as a test
		create_poll(question='Empty poll', days=-5)
		poll = create_poll(question='Full poll', days=-5)
		poll.choice_set.create(choice_text='Why yes it is!', votes=0)
		#create a response object to simulate someone using the site
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Full poll>'])

