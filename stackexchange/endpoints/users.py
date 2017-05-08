from stackexchange.endpoints.mixins import Filtered
from stackexchange.errors import StackExchangeInvalidEndpointPathError


class Users(Filtered):
    def _get_relative_position(self, offset=1):
        if self.path.endswith('me'):
            position = offset + 1
        else:
            position = offset + 2
        return position

    def me(self):
        return self.extend_with(name='me', offset=1)

    def badges(self):
        position = self._get_relative_position()
        return self.extend_with(name='badges', offset=position)

    def notifications(self, unread=False):
        position = self._get_relative_position()
        path = 'notifications'
        if unread:
            path += '/unread'
        return self.extend_with(name=path, offset=position)

    def comments(self, to_id=None):
        position = self._get_relative_position()
        path = 'comments'
        if to_id is not None:
            path += '/{}'.format(to_id)
        return self.extend_with(name=path, offset=position)

    def network_activity(self):
        position = self._get_relative_position()
        return self.extend_with(name='network-activity', offset=position)

    def posts(self):
        position = self._get_relative_position()
        return self.extend_with(name='posts', offset=position)

    def privileges(self):
        position = self._get_relative_position()
        return self.extend_with(name='privileges', offset=position)

    def questions(self):
        position = self._get_relative_position()
        return self.extend_with(name='questions', offset=position)

    def featured(self):
        if not self.path.endswith('questions'):
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/featured'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_with(name='featured', offset=position)

    def no_answers(self):
        if self.path.endswith('questions'):
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/no-answers'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_with(name='no-answers', offset=position)

    def unaccepted(self):
        if self.path.endswith('questions'):
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/unaccepted'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_with(name='unaccepted', offset=position)

    def unanswered(self):
        if not self.path.endswith('questions'):
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/unanswered'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_with(name='unanswered', offset=position)

    def answers(self):
        position = self._get_relative_position()
        return self.extend_with(name='answers', offset=position)

    def favorites(self):
        position = self._get_relative_position()
        return self.extend_with(name='favorites', offset=position)

    def mentioned(self):
        position = self._get_relative_position()
        return self.extend_with(name='mentioned', offset=position)

    def reputation(self):
        position = self._get_relative_position()
        return self.extend_with(name='reputation', offset=position)

    def reputation_history(self, full=False):
        position = self._get_relative_position()
        path = 'reputation-history'
        if full:
            path += '/full'
        return self.extend_with(name=path, offset=position)

    def inbox(self, unread=False):
        position = self._get_relative_position()
        path = 'inbox'
        if unread:
            path += '/unread'
        return self.extend_with(name=path, offset=position)

    def top_tags(self):
        position = self._get_relative_position()
        return self.extend_with(name='top-tags', offset=position)

    def tags(self):
        position = self._get_relative_position()
        return self.extend_with(name='tags', offset=position)

    def write_permissions(self):
        position = self._get_relative_position()
        return self.extend_with(name='write-permissions', offset=position)

    def moderators(self, elected=False):
        path = 'moderators'
        if elected:
            path += '/elected'
        return self.extend_with(name=path, offset=2)

    def suggested_edits(self):
        position = self._get_relative_position()
        return self.extend_with(name='suggested-edits', offset=position)

    def top_answers(self, tags):
        """
        Get the top questions a user has posted with a set of tags.
        :param list[str] tags: the list of tag names
        """
        position = self._get_relative_position()
        path = 'tags/{}/top-answers'.format(','.join(tags))
        return self.extend_with(name=path, offset=position)

    def top_questions(self, tags):
        position = self._get_relative_position()
        path = 'tags/{}/top-questions'.format(','.join(tags))
        return self.extend_with(name=path, offset=position)

    def timeline(self):
        position = self._get_relative_position()
        return self.extend_with(name='timeline', offset=position)

    def top_answer_tags(self):
        position = self._get_relative_position()
        return self.extend_with(name='top-answer-tags', offset=position)

    def top_question_tags(self):
        """
        Get the top tags (by score) a single user has posted answers in.
        """
        position = self._get_relative_position()
        return self.extend_with(name='top-question-tags', offset=position)
