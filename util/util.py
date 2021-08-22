import holidays
import isoweek
import sqlalchemy.exc

from models.db.db_meal_time import MealTime

from models.db.db_days_published import DaysPublished
from models.db.db_dish_model import Dish
from models.db.db_menu_for_meal_model import MenuForMeal
from models.db.db_message_of_the_day_model import MessageOfTheDay
from models.db.db_sections_model import Sections
from models.meal_enum import Meal

import datetime
from itertools import groupby, chain


def get_opening_time_for_date_meal(date: datetime.datetime, meal: Meal):
    ca_holiday = holidays.CA(prov="BC")

    return MealTime.query.get(
        (meal.name, date in ca_holiday or date.weekday() in [5, 6]))


def user_get_menu_for_date(date: datetime.datetime):
    meals: list[Meal] = list(Meal)

    full_menu = []

    for meal in meals:
        try:
            menu_db_result = (MenuForMeal.query
                              .with_entities(MenuForMeal.section_id, Sections, Dish)
                              .join(Sections)
                              .join(Dish)
                              .join(DaysPublished, DaysPublished.date == MenuForMeal.date)
                              .filter(MenuForMeal.date == date)
                              .filter(MenuForMeal.for_which_meal == meal.name)
                              .filter(DaysPublished.is_published)
                              .order_by(Sections.section_name).all())
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise e

        menu_for_meal = []

        try:
            for section, dishes in groupby(menu_db_result, lambda x: x[1]):
                menu_for_meal.append({"section_id": section.section_id, "section_name": section.section_name,
                                      "dishes": [dish[2].to_dict() for dish in dishes]})
        except AttributeError:
            pass

        opening_time = get_opening_time_for_date_meal(date, meal)

        full_menu.append({"meal_int": meal.value,
                          "meal_str": meal.name,
                          "open_time": opening_time.time_open,
                          "close_time": opening_time.time_close,
                          "menu": menu_for_meal})

    return full_menu


def user_get_menu_for_week(week_obj: isoweek.Week, days_shift=0):
    days = week_obj.days()

    full_menu = [{"date": d,
                  "is_published": True if DaysPublished.query.get(d) else False,
                  "menu": user_get_menu_for_date(d)} for d in days[days_shift:] + days[:days_shift]]

    return full_menu


def user_get_message_for_date(date: datetime.datetime):
    messages = MessageOfTheDay.query.filter(MessageOfTheDay.date == date).all()

    return messages


def user_get_messages_for_week(week_obj: isoweek.Week):
    days = week_obj.days()

    messages_in_week = [user_get_message_for_date(day) for day in days]

    messages_in_week = list(chain.from_iterable(messages_in_week))

    return messages_in_week
