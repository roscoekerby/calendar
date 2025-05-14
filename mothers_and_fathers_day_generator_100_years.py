from ics import Calendar, Event
from datetime import datetime, timedelta
import calendar

def get_nth_weekday(year, month, weekday, n):
    """Returns the date of the nth weekday (e.g., 2nd Sunday) in a given month/year."""
    count = 0
    for day in range(1, 32):
        try:
            date = datetime(year, month, day)
        except ValueError:
            break
        if date.weekday() == weekday:
            count += 1
            if count == n:
                return date
    return None

def generate_calendar(start_year=2025, end_year=2125):
    c = Calendar()

    for year in range(start_year, end_year + 1):
        # Mother's Day: 2nd Sunday in May
        mothers_day = get_nth_weekday(year, 5, calendar.SUNDAY, 2)
        if mothers_day:
            e = Event()
            e.name = "Mother's Day"
            e.begin = mothers_day.strftime('%Y-%m-%d')
            e.make_all_day()
            c.events.add(e)

        # Father's Day: 3rd Sunday in June
        fathers_day = get_nth_weekday(year, 6, calendar.SUNDAY, 3)
        if fathers_day:
            e = Event()
            e.name = "Father's Day"
            e.begin = fathers_day.strftime('%Y-%m-%d')
            e.make_all_day()
            c.events.add(e)

    # Save to .ics file
    with open("mother_and_father_days.ics", "w") as f:
        f.writelines(c)

    print("Calendar file 'mother_and_father_days.ics' created.")

# Run the script
if __name__ == "__main__":
    generate_calendar()
