def outlier_threshold(dataframe, column, q1=0.25, q3=0.75):
    Q1 = dataframe[column].quantile(q1)
    Q3 = dataframe[column].quantile(q3)
    IQR = Q3 - Q1
    max_limit = Q3 + 1.5 * IQR
    min_limit = Q1 - 1.5 * IQR
    print(f"for {column} --> min. limit: {min_limit}, max. limit: {max_limit}")
    return min_limit, max_limit


def check_outliers(dataframe, column, q1=0.25, q3=0.75):
    min_limit, max_limit = outlier_threshold(dataframe, column, q1, q3)
    if dataframe[(dataframe[column] < min_limit) | (dataframe[column] > max_limit)].any(axis=None):
        return True
    else:
        return False


def grab_outliers(dataframe, column, q1=0.25, q3=0.75, index=False):
    min_limit, max_limit = outlier_threshold(dataframe, column, q1, q3)
    dataframe_with_outliers = dataframe[(dataframe[column] < min_limit) | (dataframe[column] > max_limit)]
    print(dataframe_with_outliers)
    if index:
        outlier_index = dataframe[(dataframe[column] < min_limit) | (dataframe[column] > max_limit)].index
        return outlier_index


def replace_with_threshold(dataframe, column, q1=0.25, q3=0.75):
    min_limit, max_limit = outlier_threshold(dataframe, column, q1, q3)
    dataframe.loc[dataframe[column] < min_limit, column] = min_limit
    dataframe.loc[dataframe[column] > max_limit, column] = max_limit


def remove_outliers(dataframe, column, q1=0.25, q3=0.75):
    min_limit, max_limit = outlier_threshold(dataframe, column, q1, q3)
    dataframe_without_outliers = dataframe[~((dataframe[column] < min_limit) | (dataframe[column] > max_limit))]
    return dataframe_without_outliers
