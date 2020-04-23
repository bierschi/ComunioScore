import logging


class PointCalculator:
    """ class PointCalculator to calculate the points for rating, goals and offs

    USAGE:
            calc = PointCalculator()
    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class PointCalculator')

    @staticmethod
    def get_points_from_rating(rating):
        """ calculates the points from rating

        :param rating: rating number
        :return: points for given rating
        """

        if (rating >= 0) and (rating <= 4.6):
            return -8
        elif (rating >= 4.7) and (rating <= 4.9):
            return -7
        elif (rating >= 5.0) and (rating <= 5.2):
            return -6
        elif (rating >= 5.3) and (rating <= 5.4):
            return -5
        elif (rating >= 5.5) and (rating <= 5.6):
            return -4
        elif (rating >= 5.7) and (rating <= 5.8):
            return -3
        elif (rating >= 5.9) and (rating <= 6.0):
            return -2
        elif (rating >= 6.1) and (rating <= 6.2):
            return -1
        elif (rating >= 6.3) and (rating <= 6.4):
            return 0
        elif (rating >= 6.5) and (rating <= 6.6):
            return 1
        elif (rating >= 6.7) and (rating <= 6.8):
            return 2
        elif (rating >= 6.9) and (rating <= 7.0):
            return 3
        elif (rating >= 7.1) and (rating <= 7.2):
            return 4
        elif (rating >= 7.3) and (rating <= 7.4):
            return 5
        elif (rating >= 7.5) and (rating <= 7.6):
            return 6
        elif (rating >= 7.7) and (rating <= 7.8):
            return 7
        elif (rating >= 7.9) and (rating <= 8.0):
            return 8
        elif (rating >= 8.1) and (rating <= 8.4):
            return 9
        elif (rating >= 8.5) and (rating <= 8.8):
            return 10
        elif (rating >= 8.9) and (rating <= 9.2):
            return 11
        elif (rating >= 9.3) and (rating <= 10.0):
            return 12

    @staticmethod
    def get_points_for_goal(position):
        """ calculates points for goals

        :param position: position type
        :return: points for the position type
        """

        if position is 'Goalkeeper':
            return 6
        elif position is 'Defender':
            return 5
        elif position is 'Midfielder':
            return 4
        elif position is 'Forward':
            return 3

    @staticmethod
    def get_points_for_offs(off_type):
        """ get points for offs

        :return: points for the off type
        """

        if off_type is 'yellow_red':
            return -3
        elif off_type is 'red':
            return -6

    @staticmethod
    def get_penalty():
        """ get points for penalty

        :return: points for penalty
        """
        return 3
