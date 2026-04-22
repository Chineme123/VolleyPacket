# --- IMPORT ---
import pandas as pd

def load_data(file_path):
    data_frame = data_frame.rename(columns={
        'Names': 'Name',
        'Examination Number': 'ExamNo',
        'Photo Link': 'PhotoLink',
        'Examination Date': 'ExamDate',
        'Email Address': 'Email',
        'Phone Number': 'PhoneNumber',   # add this line
    })
    data_frame = data_frame.fillna('')
    data_frame['ExamDate'] = pd.to_datetime(data_frame['ExamDate'])
    return data_frame

if __name__ == "__main__":
    file_path = './data/main_data.xlsx'
    data = load_data(file_path)
    print(data.head())