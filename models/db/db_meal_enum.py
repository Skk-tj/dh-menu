from sqlalchemy.dialects import postgresql

meal_enum_sql = postgresql.ENUM("Breakfast", "Lunch", "Dinner", name="meal", create_type=False)
