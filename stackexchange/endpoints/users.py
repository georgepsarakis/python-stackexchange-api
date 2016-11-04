from stackexchange.api import StackExchangeAPIEndpoint
from stackexchange.endpoints.misc import Filtered
from stackexchange.errors import StackExchangeInvalidEndpointPathError


class Users(StackExchangeAPIEndpoint, Filtered):
    def _get_relative_position(self, offset=1):
        if self.path.last_segment == 'me':
            position = offset + 1
        else:
            position = offset + 2
        return position

    def me(self):
        return self.extend_path(name='me', position=1)

    def badges(self):
        position = self._get_relative_position()
        return self.extend_path(name='badges', position=position)

    def notifications(self, unread=False):
        position = self._get_relative_position()
        path = 'notifications'
        if unread:
            path += '/unread'
        return self.extend_path(name=path, position=position)

    def comments(self, to_id=None):
        position = self._get_relative_position()
        path = 'comments'
        if to_id is not None:
            path += '/{}'.format(to_id)
        return self.extend_path(name=path, position=position)

    def network_activity(self):
        position = self._get_relative_position()
        return self.extend_path(name='network-activity', position=position)

    def posts(self):
        position = self._get_relative_position()
        return self.extend_path(name='posts', position=position)

    def privileges(self):
        position = self._get_relative_position()
        return self.extend_path(name='privileges', position=position)

    def questions(self):
        position = self._get_relative_position()
        return self.extend_path(name='questions', position=position)

    def featured(self):
        if self.path.last_segment != 'questions':
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/featured'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_path(name='featured', position=position)

    def no_answers(self):
        if self.path.last_segment != 'questions':
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/no-answers'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_path(name='no-answers', position=position)

    def unaccepted(self):
        if self.path.last_segment != 'questions':
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/unaccepted'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_path(name='unaccepted', position=position)

    def unanswered(self):
        if self.path.last_segment != 'questions':
            raise StackExchangeInvalidEndpointPathError(
                'Featured Questions path: /users/{ids}/questions/unanswered'
            )
        position = self._get_relative_position(offset=2)
        return self.extend_path(name='unanswered', position=position)

    def answers(self):
        position = self._get_relative_position()
        return self.extend_path(name='answers', position=position)

    def favorites(self):
        position = self._get_relative_position()
        return self.extend_path(name='favorites', position=position)

    def mentioned(self):
        position = self._get_relative_position()
        return self.extend_path(name='mentioned', position=position)

    def reputation(self):
        position = self._get_relative_position()
        return self.extend_path(name='reputation', position=position)

    def reputation_history(self, full=False):
        position = self._get_relative_position()
        path = 'reputation-history'
        if full:
            path += '/full'
        return self.extend_path(name=path, position=position)

    def inbox(self, unread=False):
        position = self._get_relative_position()
        path = 'inbox'
        if unread:
            path += '/unread'
        return self.extend_path(name=path, position=position)

    def top_tags(self):
        position = self._get_relative_position()
        return self.extend_path(name='top-tags', position=position)

    def tags(self):
        position = self._get_relative_position()
        return self.extend_path(name='tags', position=position)

    def write_permissions(self):
        position = self._get_relative_position()
        return self.extend_path(name='write-permissions', position=position)

    def moderators(self, elected=False):
        path = 'moderators'
        if elected:
            path += '/elected'
        return self.extend_path(name=path, position=2)

    def suggested_edits(self):
        position = self._get_relative_position()
        return self.extend_path(name='suggested-edits', position=position)

    def top_answers(self, tags):
        """
        Get the top questions a user has posted with a set of tags.
        :param list[str] tags: the list of tag names
        """
        position = self._get_relative_position()
        path = 'tags/{}/top-answers'.format(','.join(tags))
        return self.extend_path(name=path, position=position)

    def top_questions(self, tags):
        position = self._get_relative_position()
        path = 'tags/{}/top-questions'.format(','.join(tags))
        return self.extend_path(name=path, position=position)

    def timeline(self):
        position = self._get_relative_position()
        return self.extend_path(name='timeline', position=position)

    def top_answer_tags(self):
        position = self._get_relative_position()
        return self.extend_path(name='top-answer-tags', position=position)

    def top_question_tags(self):
        """
        Get the top tags (by score) a single user has posted answers in.
        """
        position = self._get_relative_position()
        return self.extend_path(name='top-question-tags', position=position)
