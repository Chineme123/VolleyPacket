# --- IMPORT ---
import pandas as pd

def load_data(file_path):
    data_frame = pd.read_excel(file_path)
    data_frame = data_frame.fillna('')
    data_frame['ExamDate'] = pd.to_datetime(data_frame['ExamDate'])
    return data_frame

if __name__ == "__main__":
    file_path = './data/volley_packet_test_data.xlsx'
    data = load_data(file_path)
    print(data.head())