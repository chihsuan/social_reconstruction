import time
import datetime

def to_frame(subtitle_time):
    start_time = subtitle_time[0][:13]
    end_time = subtitle_time[0][17:]
    return _convert_(start_time), _convert_(end_time)

def _convert_(input_time, FRAME_PER_SECOND=24):
    format_time = time.strptime(input_time.split(',')[0], '%H:%M:%S' )
    frame = float(datetime.timedelta(hours=format_time.tm_hour, minutes=format_time.tm_min, 
        seconds=format_time.tm_sec).total_seconds() * FRAME_PER_SECOND) + float(input_time[-3:]) / 1000
    
    return  round(frame, 3)



