__author__ = "Vivek"
__author_email__ = "vivekltp120@gmail.com"


import pandas as pd
import numpy as np
import os


students_data = [
    {
        "Name": "John",
        "Gender": "M",
        "DOB": "5/4/88",
        "Maths": 55,
        "Physics": 45,
        "Chemistry": 56,
        "English": 87,
        "Biology": 21,
        "Economics": 52,
        "History": 89,
        "Civics": 65
    },
    {
        "Name": "Suresh",
        "Gender": "M",
        "DOB": "4/5/87",
        "Maths": 75,
        "Physics": 55,
        "Chemistry": None,
        "English": 64,
        "Biology": 90,
        "Economics": 61,
        "History": 58,
        "Civics": 2
    },
    {
        "Name": "Ramesh",
        "Gender": "M",
        "DOB": "25/5/1989",
        "Maths": 25,
        "Physics": 54,
        "Chemistry": 89,
        "English": 76,
        "Biology": 95,
        "Economics": 87,
        "History": 56,
        "Civics": 74
    },
    {
        "Name": "Jessica",
        "Gender": "F",
        "DOB": "12/8/90",
        "Maths": 78,
        "Physics": 55,
        "Chemistry": 86,
        "English": 63,
        "Biology": 54,
        "Economics": 89,
        "History": 75,
        "Civics": 45
    },
    {
        "Name": "Jennifer",
        "Gender": "F",
        "DOB": "2/9/89",
        "Maths": 58,
        "Physics": 96,
        "Chemistry": 78,
        "English": 46,
        "Biology": 96,
        "Economics": 77,
        "History": 83,
        "Civics": 53
    }
]


def average_student(df: pd.DataFrame=None):
    global avg_df
    # print(df.iloc[:,3:7])
    # avg_df=df.fillna(0).loc[:,["Maths","Physics","Chemistry","English"]].apply(np.average,axis=1)
    # axis=1 along row means --->
    # Average for all subject student wise
    avg_df = df.fillna(0).iloc[:, 3:].apply(np.average, axis=1)
    df["Average"] = avg_df
    print("Average:\n\n ", df)


def drop_column(df: pd.DataFrame=None):
    # Drop the column
    new_df = pd.concat([df, avg_df], axis=1)
    print("After dropping the column:\n\n", new_df.drop(["Gender", "Name"], axis=1))


def rename_column(df: pd.DataFrame=None):
    # replace column levels
    df.rename(columns={"Maths": "Mathematics"}, inplace=True)
    print("After rename:\n\n", df)


def setaxis(df: pd.DataFrame=None):
    # set the column or row(index) level
    # to set the axis for the column and row(index)
    df_index = df.set_axis(["a", "b", "c", "d", "e"], axis='index')
    print("After set index:\n\n", df_index)
    # set the column as index
    print("After set column as index:\n\n", df.set_index("Name"))


def write_data(df: pd.DataFrame=None, file_name="out.xlsx", sheet_name="sheet_1"):
    # write df dinto the csv file
    with pd.ExcelWriter(file_name) as ewriter:
        df.to_excel(ewriter, sheet_name=sheet_name)



def read_xlsx(file: str) -> list[pd.DataFrame]:
    """ Reads data from an xlsx file and returns a DataFrame.
    Params
    -------
    file: Path to the xlsx file to be read.
    
    return
    ------- 
      DataFrame containing the data from the file.
    """
    result=[]
    if os.path.exists(file) and os.path.splitext(file)[1] in [".xls", ".xlsx"]:
        xls=pd.ExcelFile(file)
        print(xls.sheet_names)
        for sheet in xls.sheet_names:
            sheet_df = sheet+"_df"
            sheet_df=pd.read_excel(xls,sheet_name=sheet)
            result.append(sheet_df)
        return result    
    else:
        raise FileNotFoundError(f"The file {file} does not exist or is not an xlsx file.")

def read_data(file: str)-> pd.DataFrame:
    """ Reads data from a file and returns a DataFrame.
    # csv file  reader
    Params
    -------
    file: Path to the file to be read.
    
    return
    ------- 
      DataFrame containing the data from the file.
    """
    reader = None
    if os.path.exists(file) and os.path.splitext(file) == ".csv":
        reader = pd.read_csv(file)
    return reader



    
                    

def student_analysis(students_data, average_student, drop_column, rename_column, setaxis, write_data):
    df = pd.DataFrame(students_data)
    average_student(df)
    drop_column(df)
    rename_column(df)
    setaxis(df)
    write_data(df)

if __name__ == "__main__":
    student_analysis(students_data, average_student, drop_column, rename_column, setaxis, write_data)
    