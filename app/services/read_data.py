import pandas as pd


import os


def detect_header_row(file_path, max_scan=20):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        raw = pd.read_csv(file_path, header=None, nrows=max_scan)
    else:
        raw = pd.read_excel(file_path, header=None, nrows=max_scan)
    best_row = 0
    best_filled = 0
    for i, row in raw.iterrows():
        filled = row.notna().sum() - (row.astype(str).str.strip() == "").sum()
        if filled > best_filled:
            best_filled = filled
            best_row = i
    return best_row


def load_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    header_row = detect_header_row(file_path)
    if ext == ".csv":
        data_frame = pd.read_csv(file_path, header=header_row)
    else:
        data_frame = pd.read_excel(file_path, header=header_row)

    data_frame.columns = data_frame.columns.str.strip()
    col_map = {col: col.lower() for col in data_frame.columns}
    data_frame = data_frame.rename(columns=col_map)

    canonical = {
        'name': 'Name', 'names': 'Name',
        'examination number': 'ExamNo', 'exam number': 'ExamNo', 'examno': 'ExamNo',
        'photo link': 'PhotoLink', 'photolink': 'PhotoLink',
        'examination date': 'ExamDate', 'examdate': 'ExamDate',
        'email address': 'Email', 'email': 'Email',
        'phone number': 'PhoneNumber', 'phonenumber': 'PhoneNumber',
    }
    data_frame = data_frame.rename(columns={
        col: canonical[col] for col in data_frame.columns if col in canonical
    })

    data_frame = data_frame.fillna('')

    if 'ExamDate' in data_frame.columns:
        data_frame['ExamDate'] = pd.to_datetime(
            data_frame['ExamDate'], errors='coerce'
        )

    return data_frame
