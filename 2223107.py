import pandas as pd

def absent_finder(attendance_df):
    attendance_df = attendance_df.sort_values(by=["student_id", "attendance_date"])
    result = []

    for student_id, group in attendance_df.groupby("student_id"):
        group = group.reset_index(drop=True)
        streaks = []
        start_date = None
        end_date = None
        count = 0

        for i in range(len(group)):
            if group.loc[i, "status"] == "Absent":
                if start_date is None:
                    start_date = group.loc[i, "attendance_date"]
                end_date = group.loc[i, "attendance_date"]
                count += 1
            else:
                if count > 3:
                    streaks.append((start_date, end_date, count))
                start_date, end_date, count = None, None, 0

        if count > 3:
            streaks.append((start_date, end_date, count))

        if streaks:
            latest_streak = streaks[-1] 
            result.append({
                "student_id": student_id,
                "absence_start_date": latest_streak[0],
                "absence_end_date": latest_streak[1],
                "total_absent_days": latest_streak[2]
            })

    return pd.DataFrame(result)

def valid_email(email):
    if "@" not in email or "." not in email:
        return False

    part = email.split("@")
    if len(part) != 2:
        return False

    name_part, domain_part = part
    domain_parts = domain_part.split(".")

   
    if not (name_part[0].isalpha() or name_part[0] == "_"):
        return False

    
    if len(domain_parts) < 2 or domain_parts[-1] != "com":
        return False

    return True


def run(path=r"C:\Users\tyagi\Downloads\data - sample.xlsx", 
        attendance_sheet="Attendance_data", students_sheet="Student_data"):
    
    
    
    df = pd.read_excel(path, sheet_name=attendance_sheet)
    df["attendance_date"] = pd.to_datetime(df["attendance_date"])

    
    students_df = pd.read_excel(path, sheet_name=students_sheet)

    
    absences_df = absent_finder(df)

    
    merged_df = absences_df.merge(students_df, on="student_id", how="left")

    
    merged_df["email"] = merged_df["parent_email"].apply(lambda x: x if valid_email(str(x)) else None)

    
    merged_df["msg"] = merged_df.apply(
        lambda row: (f"Dear Parent, your child {row['student_name']} was absent from "
                     f"{row['absence_start_date']} to {row['absence_end_date']} for "
                     f"{row['total_absent_days']} days. Please ensure their attendance improves.") 
        if pd.notna(row["email"]) else None, axis=1
    )

    final_df = merged_df[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'msg']]
    
    return final_df



