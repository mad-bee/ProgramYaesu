#Create CSV files for import into Yaesus ADMS programme
#MOMZB
#15 June 2024


import pandas as pd
import requests

#Filename for saving raw download
RawDownload = "RepeatersRaw.CSV"  # type: str

# URL to download the CSV from
url = "https://ukrepeater.net/csvcreate_all.php?mode=analogue&mode=fusion"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}

# Sending GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Define the file path
    file_path = RawDownload
    
    # Write the content to a file
    with open(file_path, "wb") as file:
        file.write(response.content)

    print(f"File successfully downloaded to {file_path}")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")

import pandas as pd

# Function to find column index containing a specific string
def find_column_containing_string(search_string, search_range):
    for col in search_range.columns:
        if search_string in col:
            return col
    return None

# Read the CSV file
csv_file = RawDownload
uk_repeaters = pd.read_csv(csv_file)

ft5de = []  # List to store rows
ft70d = []  # List to store rows

# Initialize row and column indices
fCurReadRow = 0
fCurWriteRow = 0
fCurMemNumber = 1

# Find the column indices
fCallCol = find_column_containing_string('CALL', uk_repeaters)
fBandCol = find_column_containing_string('BAND', uk_repeaters)
fTxMHzCol = find_column_containing_string('txMHz', uk_repeaters)
fRxMHzCol = find_column_containing_string('rxMHz', uk_repeaters)
fCTCSSCol = find_column_containing_string('CTCSS', uk_repeaters)
fAnalogCol = find_column_containing_string('ANALOG', uk_repeaters)
fFusionCol = find_column_containing_string('FUSION', uk_repeaters)
fDstarCol = find_column_containing_string('DSTAR', uk_repeaters)
fDMRCol = find_column_containing_string('DMR', uk_repeaters)

while fCurReadRow < len(uk_repeaters):
    # Check if column exists before accessing it
    if fTxMHzCol is not None and fRxMHzCol is not None:
        sRepeaterName = uk_repeaters.at[fCurReadRow, 'CALL']

        bAnalog = not pd.isna(uk_repeaters.at[fCurReadRow, 'ANALOG'])
        bDMR = not pd.isna(uk_repeaters.at[fCurReadRow, 'DMR'])
        bDstar = not pd.isna(uk_repeaters.at[fCurReadRow, 'DSTAR'])
        bFusion = not pd.isna(uk_repeaters.at[fCurReadRow, 'FUSION'])

        # Determine values for txMHz and rxMHz
        txMHz_value = uk_repeaters.at[fCurReadRow, 'txMHz']
        rxMHz_value = uk_repeaters.at[fCurReadRow, 'rxMHz']

        if pd.isna(txMHz_value) or txMHz_value == 0:
            # If txMHz is NaN or 0, set both to rxMHz (or vice versa)
            txMHz_value = rxMHz_value if not pd.isna(rxMHz_value) and rxMHz_value != 0 else 1.0
        elif pd.isna(rxMHz_value) or rxMHz_value == 0:
            # If rxMHz is NaN or 0, set both to txMHz
            rxMHz_value = txMHz_value if not pd.isna(txMHz_value) and txMHz_value != 0 else 1.0

        if (uk_repeaters.at[fCurReadRow, 'BAND'] == "2M") or (uk_repeaters.at[fCurReadRow, 'BAND'] == "70CM"):
            if (bAnalog or bFusion) and not (sRepeaterName in ["GB7LL", "GB7TX", "GB7TT", "GB7BT"]):
                # FT5DE
                ft5de_row = [
                    fCurMemNumber,
                    "OFF",
                    txMHz_value,
                    rxMHz_value,
                    0,
                    "-/+",
                    "OFF",
                    "FM",
                    "FM" if bAnalog else "DN",
                    "ON",
                    sRepeaterName,
                    "TONE SQL" if not pd.isna(uk_repeaters.at[fCurReadRow, 'CTCSS']) else "OFF",
                    f"{uk_repeaters.at[fCurReadRow, 'CTCSS']} Hz" if not pd.isna(uk_repeaters.at[fCurReadRow, 'CTCSS']) else "",
                    23,
                    "RX Normal TX Normal",
                    "1600 Hz",
                    "RX 00",
                    "TX 00",
                    "High (5W)",
                    "OFF",
                    "ON",
                    "12.5KHz",
                    "OFF", "OFF", "OFF", "OFF", "ON", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "", int(0)
                ]
                ft5de.append(ft5de_row)

                # FT70D
                ft70d_row = [
                    fCurMemNumber,
                    "OFF",
                    txMHz_value,
                    rxMHz_value,
                    0,
                    "-/+",
                    "OFF",
                    "FM",
                    "ON",
                    "ANALOG" if bAnalog else "DN",
                    sRepeaterName[-6:],
                    "TONE SQL" if not pd.isna(uk_repeaters.at[fCurReadRow, 'CTCSS']) else "OFF",
                    f"{uk_repeaters.at[fCurReadRow, 'CTCSS']} Hz" if not pd.isna(uk_repeaters.at[fCurReadRow, 'CTCSS']) else "",
                    23,
                    "RX Normal TX Normal",
                    "1600 Hz",
                    "HIGH",
                    "OFF",
                    "ON",
                    "12.5KHz",
                    "ON",
                    "OFF", "OFF", "OFF", "OFF", "ON", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "OFF", "OFF", "OFF", "OFF", "OFF", "OFF",
                    "", int(0)
                ]
                ft70d.append(ft70d_row)

                fCurWriteRow += 1
                fCurMemNumber += 1

    fCurReadRow += 1

# Convert lists to DataFrames
ft5de_df = pd.DataFrame(ft5de)
ft70d_df = pd.DataFrame(ft70d)

# Fill remaining rows
while fCurMemNumber < 901:
    ft5de_row = [fCurMemNumber] + [""] * 53
    ft70d_row = [fCurMemNumber] + [""] * 51

    ft5de_df = pd.concat([ft5de_df, pd.DataFrame([ft5de_row])], ignore_index=True)
    ft70d_df = pd.concat([ft70d_df, pd.DataFrame([ft70d_row])], ignore_index=True)

    fCurMemNumber += 1


def custom_format(x):
    if isinstance(x, float) and x == 0:
        return f'{int(x)}'  # Convert 0.0 to integer 0
    else:
        return f'{x}'  # Keep other values unchanged

# Apply custom formatting to the DataFrame
ft70d_df = ft70d_df.applymap(custom_format)
ft5de_df = ft5de_df.applymap(custom_format)

# Process additions (if there are any)
# Note: Adjust this part based on how you want to handle additions from CSV file
# For example, if ft70d_add is a separate CSV file or additional rows in the same RepeatersRaw.CSV file
#ft70d_add = pd.DataFrame()  # Placeholder for additions, adjust as needed

# Write to CSV files
ft5de_df.to_csv('FT5DE_List.csv', index=False, header=False)
ft70d_df.to_csv('FT70D_List.csv', index=False, header=False)

print("Processing complete. CSV files have been created.")

