import pygal
from django.utils import timezone

class MealPieChart:
    def __init__(self, meals):
        self.chart = pygal.Pie()
        self.chart.title = 'Meals Breakdown'
        self.meals = meals

    def get_data(self):
        # Query the db for chart data, pack them into a dict and return it
        data = dict()
        for meal in self.meals:
            data[meal.meal_name] = meal.number_ordered
        return data

    def generate(self):
        chart_data = self.get_data()
        # add data to chart
        for key, value in chart_data.items():
            self.chart.add(key, value)
        return self.chart.render(is_unicode=True)

class SalesTrendChart:
    def __init__(self, meals):
        self.chart = pygal.Line(x_label_rotation=30)
        self.chart.title = 'Sales Trend by Date'
        self.meals = meals

    def get_data(self):
        data = []
        time_x_labels = []
        daily_revs = []

        def total_revenue(meals):
            total_rev = 0
            for meal in meals:
                total_rev += meal.price * meal.number_ordered
            return total_rev

        for i in range(7, 0, -1):
            day = timezone.now()-timezone.timedelta(days=i)
            day_str = str(day).split(" ")[0]
            time_x_labels.append(day_str)

            day_meals = self.meals.filter(date=day)
            day_rev = total_revenue(day_meals)
            daily_revs.append(day_rev)

        data.append(time_x_labels)
        data.append(daily_revs)

        return data

    def generate(self):
        self.chart.x_labels = self.get_data()[0]
        self.chart.add("Daily Revenue", self.get_data()[1])
        return self.chart.render(is_unicode=True)

class StackBarChart:
    def __init__(self, meals):
        self.chart = pygal.StackedBar()
        self.chart.title = 'Meals Prepared & Sold Today'
        self.meals = meals

    def get_data(self):
        meal_names = []
        meal_sold = []
        meal_remaining = []
        chart_data = []
        for meal in self.meals:
            meal_names.append(str(meal.meal_name))
            meal_sold.append(int(meal.number_ordered))
            meal_remaining.append(int(meal.avail_quantity))
        chart_data.append(meal_names)
        chart_data.append(meal_sold)
        chart_data.append(meal_remaining)
        return chart_data

    def generate(self):
        chart_data = self.get_data()
        self.chart.x_labels = chart_data[0]
        self.chart.add('Sold', chart_data[1])
        self.chart.add('Remaining', chart_data[2])
        return self.chart.render(is_unicode=True)
