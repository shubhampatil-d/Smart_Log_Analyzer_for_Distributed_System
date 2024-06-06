from flask import Flask, render_template, request,send_file
import re
import pandas as pd
import traceback
from scipy.stats import zscore
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import os
import base64
import io


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        print("came inside")
        # # df
        # stat_anal = stat_anal_fun(df)
        # d = {
        #     'stat_anam' : stat_anal
        # }
        
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
            

            def stats_shape(df):
                shape_info = df.shape
                return shape_info
            
            def stats_describe(df):
                describe= df.describe()
                return describe
            
            def stats_info(df):
                info=df.info()
                return info
            
            def stats_loglevels(df):
                log_level=df["Log_levels"].value_counts()
                return log_level
            
            def stats_treadid(df):
                treadid = df['Thread_id'].value_counts()
                return treadid
            
            def stats_anomoly(df):
                log_level_map={
                    'INFO':1,
                    'WARN':2,
                    'ERROR':3
                }
                df['log_level_map']= df["Log_levels"].map(log_level_map)
                df.dropna(subset=["log_level_map"],inplace=True)
                df['log_level_zscore']=zscore(df['log_level_map'])
                anomaly_threshold=3
                anomalies=df[abs(df['log_level_zscore'])>anomaly_threshold]
                return anomalies
            
            def text_message_len(df):
                df['message_len']=df['Messages'].apply(len)
                return df['message_len'].describe()
            
            # def visu(df):
            #     fig, ax = plt.subplots()
            #     # df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d')  # Change the format as needed
            #     hourly_dist=df['Timestamp'].value_counts().sort_index()
            #     hourly_dist.plot(kind='bar',xlabel='hour of the day',ylabel='no. of log entries')
            #     plot1=plt.show()
            #     plot_filename = f"{uuid.uuid4()}.png"  # Create a unique filename
            #     plot_path= f"/tmp/{plot_filename}" 
            #     fig.savefig(plot_path, format='png')
            #     return plot_path

            def visu(df):
                fig, ax = plt.subplots()
                # df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d')  # Change the format as needed
                hourly_dist = df['Timestamp'].value_counts().sort_index()
                hourly_dist.plot(kind='bar', xlabel='hour of the day', ylabel='no. of log entries')
                # Convert the plot to a base64 encoded string
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                plot1 = base64.b64encode(buffer.read()).decode()
                plt.close(fig)
                return plot1
            
            def visu2(df):
                fig, ax = plt.subplots()
                sns.countplot(data=df, x='Orgs', hue='Log_levels', ax=ax)
                plt.xticks(rotation=45)
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                plot_data = base64.b64encode(buffer.read()).decode()
                plt.close(fig)
                return plot_data
            
            # def plot_time_graph(df):
            #     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            #     plt.figure(figsize=(10, 6))
            #     sns.lineplot(x='Timestamp', y='Tread_id', data=df, marker='o')
            #     plt.title("Thread ID Variation Over Time")
            #     plt.xlabel("Timestamp")
            #     plt.ylabel("Thread ID")
            #     plt.xticks(rotation=45)
            #     # Convert the plot to a base64 encoded image for display in Flask
            #     buffer = io.BytesIO()
            #     plt.savefig(buffer, format='png')
            #     buffer.seek(0)
            #     plot_data = base64.b64encode(buffer.read()).decode()
            #     # plt.close(fig)
            #     return plot_data
            
            def log_level_dist(df):
                plt.figure(figsize=(10, 6))
                ax = sns.countplot(x="Log_levels", data=df)  # Bar plot for log levels
                # Annotate each bar with the count
                for p in ax.patches:
                    ax.annotate(
                    format(p.get_height(), '.0f'),  # Format the count as an integer
                    (p.get_x() + p.get_width() / 2., p.get_height()),  # Position of the annotation
                    ha='center',  # Horizontal alignment
                    va='center',  # Vertical alignment
                    xytext=(0, 10),  # Offset for better visibility
                    textcoords='offset points'  # Use relative offset
                     )

                plt.title("Log Levels Distribution")
                plt.xlabel("Log Levels")
                plt.ylabel("Count")

                # Convert the plot to a base64 encoded image for Flask
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                plot_data = base64.b64encode(buffer.read()).decode()    
                return plot_data
            
            
            # Create a plot to show the count of logs generated each hour
            def plot_hourly_log_counts(df):
                df["Timestamp"] = pd.to_datetime(df["Timestamp"])
                # Extract the hour from the 'Timestamp' column
                df["Hour"] = df["Timestamp"].dt.hour  # Get the hour of the day
                plt.figure(figsize=(10, 6))
                sns.countplot(x="Hour", data=df)  # Bar plot to show the count of logs per hour
                plt.title("Log Count by Hour")
                plt.xlabel("Hour of the Day")
                plt.ylabel("Log Count")

                # Annotate each bar with the count
                ax = plt.gca()  # Get current axes
                for p in ax.patches:
                    ax.annotate(
                        format(p.get_height(), '.0f'),  # Format the count
                        (p.get_x() + p.get_width() / 2, p.get_height()),  # Position of the annotation
                        ha='center',  # Horizontal alignment
                        va='center',  # Vertical alignment
                        xytext=(0, 10),  # Offset
                        textcoords='offset points'  # Offset in points
                    )

                # Convert the plot to a base64 encoded image for Flask
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                plot_data = base64.b64encode(buffer.read()).decode()
                return plot_data

            stats=stats_shape(df)
            textana=stats_describe(df)
            log_level=stats_loglevels(df)
            text_len=text_message_len(df)
            anomoly=stats_anomoly(df)
            thread=stats_treadid(df)
            plot1=visu(df)
            plot2=visu2(df)
            # plot3=plot_time_graph(df)
            plot4=log_level_dist(df)
            plot5=plot_hourly_log_counts(df)
            visual=stats_info(df)
            # plot_path = create_plot(df)

            return render_template('analysis.html',
                                   stats=stats,
                                   textana=textana.to_html(),
                                   textlen=text_len,
                                   loglevel=log_level,
                                   anomaly=anomoly.to_html(),
                                   threadid=thread,
                                   plot1=plot1,
                                   plot2=plot2,
                                   plot4=plot4,
                                   plot5=plot5,
                                   visual=visual)
                                #    plot_path = plot_path)

            return render_template('analysis.html',loglevel=log_level,textlen=text_len,anomoly=anomoly,tread=tread,stats=stats,textana=textana.to_html(),visual=visual)

            return render_template('analysis.html', table=df.to_html(), shape=shape_info)
        else:
            return "No file uploaded"
    except Exception as e:
        print("Error occurerd", e)
        return render_template('index.html')
    
# @app.route('/plot/<filename>')
# def serve_plot(filename):
#     plot_path = f"/tmp/{filename}"  # Path to the plot
#     if os.path.exists(plot_path):
#         return send_file(plot_path, mimetype='image/png')  # Serve the image
#     else:
#         return "Plot not found", 404

# @app.route('/analysis',methods=['GET'])
# def analysis():
#     # shape_info = df.shape
#     # sample_data= df.sample()
#     # descibe_data= df.describe()
#     # return render_template('result1.html',shape=shape_info,sample=sample_data,describ=descibe_data)
#     return render_template('result1.html')

# @app.route('/text_analysis')
# def text_analysis():
#     return render_template('result3.html')

if __name__ == '__main__':
    app.run(debug=True)
