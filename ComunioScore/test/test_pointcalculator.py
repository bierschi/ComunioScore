import unittest
from ComunioScore import PointCalculator


class TestPointCalculator(unittest.TestCase):

    def setUp(self) -> None:

        self.pointcalculator = PointCalculator()

    def test_get_points_from_rating(self):

        points_5_1 = self.pointcalculator.get_points_from_rating(rating=5.1)
        self.assertEqual(points_5_1, -6, msg="Rating 5.1 must be -6 points")

        points_8_1 = self.pointcalculator.get_points_from_rating(rating=8.1)
        self.assertEqual(points_8_1, 9, msg="Rating 8.1 must be 9 points")

    def test_get_points_for_goal(self):

        points_keeper = self.pointcalculator.get_points_for_goal(position='keeper')
        self.assertEqual(points_keeper, 6, msg="Points for keeper goal must be 6")

        points_defender = self.pointcalculator.get_points_for_goal(position='defender')
        self.assertEqual(points_defender, 5, msg="Points for defender goal must be 5")

        points_midfielder = self.pointcalculator.get_points_for_goal(position='midfielder')
        self.assertEqual(points_midfielder, 4, msg="Points for midfielder goal must be 4")

        points_striker = self.pointcalculator.get_points_for_goal(position='striker')
        self.assertEqual(points_striker, 3, msg="Points for striker goal must be 3")

    def test_get_points_for_offs(self):

        points_yellow_red = self.pointcalculator.get_points_for_offs(off_type='yellow_red')
        self.assertEqual(points_yellow_red, -3, msg="Points for yellow_red off must be -3")

        points_red = self.pointcalculator.get_points_for_offs(off_type='red')
        self.assertEqual(points_red, -6, msg="Points for red off must be -6")

    def test_get_penalty(self):

        points_penalty = self.pointcalculator.get_penalty()
        self.assertEqual(points_penalty, 3, msg="Points for penalty must be 3")

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
