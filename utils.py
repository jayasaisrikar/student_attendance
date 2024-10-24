from datetime import datetime, timedelta

def is_within_time_range(start_time, end_time, current_time=None):
    if current_time is None:
        current_time = datetime.now().time()
    
    start = datetime.strptime(start_time, "%H:%M").time()
    end = datetime.strptime(end_time, "%H:%M").time()
    
    return start <= current_time <= end

def get_time_difference(start_time, end_time):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    
    difference = end - start
    return difference.total_seconds() / 3600  # Return difference in hours

def format_timedelta(td):
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m"