import pandas as pd

data_frame = pd.read_excel('./data/volley_packet_test_data.xlsx')
data_frame = data_frame.fillna('')
data_frame['ExamDate'] = pd.to_datetime(data_frame['ExamDate'])