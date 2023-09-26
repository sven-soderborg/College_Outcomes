import pandas as pd


def read_scorecard_data() -> pd.DataFrame:
    """
    To save processing time, we will read just the headers of the scorecard data first.
    Then isolate all column names containing "EARN".
    Then read the whole csv using usecols with those columns and university identifiers
    """
    all_cols = pd.read_csv(
        r"Data\most_recent_cohorts_field_of_study.csv", nrows=0
    ).columns.tolist()
    useful_cols = [col for col in all_cols if "EARN" in col]
    useful_cols.extend(["INSTNM", "OPEID6", "MAIN", "CIPCODE", "CREDLEV", "CONTROL"])

    # Read CIPCODE as string so we have leading zeros
    # Fill in 'PrivacySuppressed' with NaN
    earn_df = pd.read_csv(
        r"Data\most_recent_cohorts_field_of_study.csv",
        usecols=useful_cols,
        dtype={"CIPCODE": str},
        na_values="PrivacySuppressed",
        skipinitialspace=True,
    )

    return earn_df


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter for Utah schools and Bachelor's degrees.
    Also add a column for the first two digits of CIPCODE (denotes general field of study)
    """
    # Read and merge Utah schools
    utah_schools = pd.read_csv(r"Data\utah_oiep6.csv")
    utah_df = utah_schools.merge(
        df, on="OPEID6", how="left", suffixes=("", "_y")
    )  # Left join so we're filtering for UT schools
    utah_df.drop(utah_df.filter(regex="_y$").columns.tolist(), axis=1, inplace=True)

    # Filter for Bachelor's degrees
    bachelors_df = utah_df[utah_df["CREDLEV"] == 3]

    # Add column for general field of study
    bachelors_df["CIPFIELD"] = bachelors_df["CIPCODE"].str[:2]

    ### Add CIPFIELD descriptions ###
    # Load and clean CIPCODE descriptions
    cips_df = pd.read_csv("Data/CIPCode2020.csv", usecols=["CIPCode", "CIPTitle"])
    cips_df.rename(columns={"CIPCode": "CIPFIELD", "CIPTitle": "CIPDEF"}, inplace=True)
    cips_df["CIPFIELD"] = cips_df["CIPFIELD"].str.replace('="', "").str.replace('"', "")
    cip_fams_df = cips_df[cips_df["CIPFIELD"].str.len() == 2]

    # Merge CIPFIELD descriptions
    bachelors_df = bachelors_df.merge(cip_fams_df, on="CIPFIELD", how="left")

    # Move CIPFIELD to 6th column and CIPDEF to 7th column
    cols = list(bachelors_df.columns)
    cols = cols[:4] + [cols[-1]] + [cols[-2]] + cols[4:-2]
    bachelors_df = bachelors_df[cols]

    return bachelors_df


if __name__ == "__main__":
    df = read_scorecard_data()
    df = filter_data(df)
    df.to_csv(r"Data\clean_field_of_study.csv", index=False)
