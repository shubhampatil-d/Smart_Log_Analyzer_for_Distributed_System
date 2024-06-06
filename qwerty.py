from flask import request, render_template
import re
import pandas as pd

def upload():
    file = request.files['file']
    patterns = re.compile(r'^\d{4}-\d{2}-\d{2}')
    
    if file:
        file_content = file.stream.read().decode("utf-8")
        lines = file_content.split('\n')

        # Preprocess the data
        timestamp = []
        log_level = []
        message = []
        orgs = []
        thread_id = []

        for line in lines:
            if patterns.match(line):
                parts = line.split(" ")
                timestamps = " ".join([parts[0], parts[1].split(",")[0]])
                timestamp.append(timestamps)
                loglevels = parts[2]
                log_level.append(loglevels)
                messages = parts[4]
                message.append(messages)
                org = parts[3]
                orgs.append(org)
                treadid = parts[1].split(",")[1]
                thread_id.append(treadid)

        df = pd.DataFrame({
            "Timestamp": timestamp,
            "Thread_id": thread_id,
            "Log_levels": log_level,
            "Orgs": orgs,
            "Messages": message})

        shape_info = df.shape

        return render_template('analysis.html')

        # return render_template('result.html', table=df.to_html(), shape=shape_info)
    else:
        return "No file uploaded"