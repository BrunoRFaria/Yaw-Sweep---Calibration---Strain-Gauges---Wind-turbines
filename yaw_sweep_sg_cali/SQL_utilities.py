"""
Module for SQL functions to make life easier
"""

import MySQLdb
from datetime import date, datetime, timedelta
from operator import attrgetter
import pandas as pd


def inputs_SQL():
    """
    Prompt the user to provide the necessary information
    to access the V52 DTU's SQL database.
    This function asks the user to input the following
    information: the database name, host address, username,
    and password for the SQL database of the V52 DTU. It returns
    a dictionary containing this information.
    Returns
    -------
    dict
        A dictionary containing the necessary information to access the
        V52 DTU's SQL database. The dictionary has the
        following keys:
        - 'database': the name of the SQL database.
        - 'host': the IP address of the host where the database is located.
        - 'user': the username required to access the database.
        - 'password': the password required to access the database.

    Notes
    -----
    If no local data is available, the user needs to provide
    this information in order to access the SQL database of the V52 DTU.

    Examples
    --------
    To obtain the necessary information to access the SQL
    database of the V52 DTU, call the function as follows:
    >>> inputs_SQL()
    Please input the following necessary SQL
          database information since there is no local
          data available
    user: your_username
    password: your_password
    {'database': 'v52_wtg', 'host': '130.226.48.160',
     'user': 'your_username', 'password': 'your_password'}
    """
    print('\n Please input the following necessary SQL\n\
          database information since there is no local\n\
          data available \n')
    I = {}
    I['database'] = 'v52_wtg'  # input('database:')
    I['host'] = '130.226.48.160'  # input('host:')
    I['user'] = input('user:')
    I['password'] = input('password:')
    return I


def get_time_series(start, stop):
    '''
    Generate a list of timestamps in 10-minute intervals
    between a start and stop date.
    Parameters
    ----------
    start : tuple
        A tuple of integers representing the start date
        and time in the format (year, month, day, hour, minute).
    stop : tuple
        A tuple of integers representing the stop date
        and time in the format (year, month, day, hour, minute).
    Returns
    -------
    list
        A list of strings representing timestamps in the
        format 'YYYY-MM-DD HH:MM:SS'.
    Notes
    -----
    The start and stop times are inclusive, so the
    resulting list will include both the start and stop timestamps.

    '''
    lst = []
    # Separates year,month,day and hour,minutes
    start, hh1, mm1 = date(start[0], start[1], start[2]), start[3], start[4]
    stop, hh2, mm2 = date(stop[0], stop[1], stop[2]), stop[3], stop[4]
    # How many years, months, days
    delta = stop - start
    # How many hours
    delta_hour = hh2 - hh1
    for i in range(delta.days + 1):
        # Updates the start point with the consecutive step adding the amount
        # of days
        YYYY, MM, DD = str(start + timedelta(i)).split('-')
    # Specific condition in case less than a day
        if delta.days == 0:  # Specific condition in case less than a hour
            if delta_hour == 0:
                for mm in range(int(mm1/10), int(mm2/10)):
                    hh = hh1  # it could be hh2
                    lst.append(_ts_string(YYYY, MM, DD, hh, mm))
            else:
                for mm in range(int(mm1/10), 6):
                    hh = hh1
                    lst.append(_ts_string(YYYY, MM, DD, hh, mm))
                for hh in range(hh1+1, hh2):
                    for mm in range(0, 6):
                        lst.append(_ts_string(YYYY, MM, DD, hh, mm))
                for mm in range(0, int(mm2/10)):
                    hh = hh2
                    lst.append(_ts_string(YYYY, MM, DD, hh, mm))
    # When for multiple days and in the first day
        elif i == 0:  # First loop in case mm1 is not equal to 0
            for mm in range(int(mm1/10), 6):
                hh = hh1
                lst.append(_ts_string(YYYY, MM, DD, hh, mm))
    # Remaining loops for all the hours and minutes within that day
            for hh in range(hh1+1, 24):
                for mm in range(0, 6):
                    lst.append(_ts_string(YYYY, MM, DD, hh, mm))
    #  When for multiple days and in the last day
        elif i == delta.days:
            for hh in range(0, hh2):
                for mm in range(0, 6):
                    lst.append(_ts_string(YYYY, MM, DD, hh, mm))
            for mm in range(0, int(mm2/10)):
                hh = hh2
                lst.append(_ts_string(YYYY, MM, DD, hh, mm))
    # When for multiple days and in between first and last
        else:
            for hh in range(0, 24):
                for mm in range(0, 6):
                    lst.append(_ts_string(YYYY, MM, DD, hh, mm))
    # print('Number of 10-minute series queried: ' + str(len(lst)))
    return lst


def slice_name_string_from(name_str):

    """
    Slice the input string `name_str` into a tuple
    of integers representing the date and time.
    Parameters
    ----------
    name_str : str
        The name of the data to be accessed, formatted
        as a string with the following order:
        'YYYYMMDDhhmm', where YYYY represents the year,
        MM represents the month, DD represents the day,
        hh represents the hour, and mm represents the minute.
    Returns
    -------
    initial : tuple of int
        A tuple representing the date and time extracted from
        `name_str`, with the following structure:
        (YYYY, MM, DD, hh, mm), where YYYY represents the year
        as a 4-digit integer, MM represents the
        month as an integer between 1 and 12, DD represents the
        day as an integer between 1 and 31, hh
        represents the hour as an integer between 0 and 23, and
        mm represents the minute as an integer
        between 0 and 59.
    """

    YYYY = int(name_str[0:4])
    MM = int(name_str[4:6])
    DD = int(name_str[6:8])
    hh = int(name_str[8:10])
    mm = int(name_str[10:12])
    initial = (YYYY, MM, DD, hh, mm)
    return initial


def slice_name_string_to(name_str):
    '''
    Slice the input name as a string to a tuple of
    int representing the end date and time.
    Note that 10 minutes are added to the end time,
    as `get_time_series` is non-inclusive for the stop (to).
    Parameters
    ----------
    name_str : str
        The name of the data to be accessed.
    Returns
    -------
    end_date : tuple of int
        A tuple of integers representing the year,
        month, day, hour, and minute of the end time.
    '''
    YYYY = int(name_str[0:4])
    MM = int(name_str[4:6])
    DD = int(name_str[6:8])
    hh = int(name_str[8:10])
    mm = int(name_str[10:12])
    end_not_included_date = datetime(YYYY, MM, DD, hh, mm)
    end_date = end_not_included_date + timedelta(minutes=10)
    attrs = ('year', 'month', 'day', 'hour', 'minute')
    return attrgetter(*attrs)(end_date)


def SQLconnect(I):
    """
    Establishes a connection with a MySQL database
    using the provided credentials in the input dictionary.
    Parameters
    ----------
    I : dict
        A dictionary that contains the necessary
        information to access the
        right MySQL database. It should contain
        the following keys:
        - host: str
            The host name or IP address of the MySQL server.
        - user: str
            The username for the MySQL account.
        - password: str
            The password for the MySQL account.
        - database: str
            The name of the MySQL database to connect to.

    Returns
    -------
    cnx : connections.Connection
        A connection object that can be used
        to interact with the MySQL database.
    """
    cnx = MySQLdb.connect(
              host=I['host'],
              user=I['user'],
              passwd=I['password'],
              db=I['database'])
    return cnx


def _ts_string(YYYY, MM, DD, hh, mm):
    '''
    Converts the hh and mm from int to string (1 to '01')
    and adds all together.
    Parameters
    ----------
    YYYY : str
    Four-digit year.
    MM : str
    Two-digit month (01-12).
    DD : str
    Two-digit day (01-31).
    hh : int
    Hour (0-23).
    mm : int
    Minute (0-5, representing 0-50).

    Returns
    -------
    str
    A string with the format 'YYYYMMDDhhmm'
    '''
    return YYYY + MM + DD + '{:02d}{:02d}'.format(hh, mm*10)


def SQLdataframe(cnx, table_name, limit='default', col='*',
                 row='1=1', logical_statements=[]):
    '''
    Accesses an SQL database and retrieves data as a Pandas DataFrame.
    Parameters
    ----------
    cnx : connections.Connection
        A connection to the SQL database.
    table_name : str
        The name of the table to retrieve data from.
    limit : str, optional
        The maximum number of rows to retrieve. The default
        is 'default', which retrieves all rows.
    col : str, optional
        The columns to retrieve from the table. The default
        is '*', which retrieves all columns.
    row : str, optional
        The filter condition for the rows to retrieve. The default
        is '1=1', which retrieves all rows.
    logical_statements : list, optional
        Additional filter conditions as a list of strings. The
        default is [], which means no additional filter conditions.
    Returns
    -------
    df : pandas.DataFrame
        A DataFrame containing the retrieved data.
    Raises
    ------
    Exception
        If the query string is invalid or if there is
        an error in the database connection.
    '''
    if limit != 'default':
        string = "SELECT {:s} FROM {:s} WHERE {:s} LIMIT {:d}".format(
                col, table_name, row, limit)
    else:
        string = "SELECT {:s} FROM {:s} WHERE {:s}".format(
                col, table_name, row)
    if len(logical_statements) > 0:
        string += ' AND ' + ' AND '.join(logical_statements)
    # print(string)
    df = pd.read_sql(
        string,
        con=cnx
        )
    return df


def SQL_read_table(I):
    """
    Accesses the SQL database and retrieves
    a DataFrame of time series data based
    on the specified parameters.
    Parameters
    ----------
    I : dict
        A dictionary containing the necessary
        information to access the SQL database,
        including 'host', 'port', 'user', 'password'
        , and 'table_name'.

        The dictionary can also include the
        following optional parameters:
        - 'cols': A list of column names to retrieve.
        If not specified or set to 'all',
                  all columns will be retrieved.
        - 'SQLrowlimit': The maximum number of rows to
        retrieve from the SQL database.
                         If not specified or set to None,
                         all rows will be retrieved.
        - 'rows': A dictionary of row names and timestamps
        for filtering the results.
                  The keys are the row names, and the values
                  are lists of timestamps.
                  The resulting data will include all rows
                  that match any of the specified
                  timestamps.
        - 'logical_statements': A list of additional logical
        statements to add to the SQL query.
                                Each statement should be a string
                                in SQL format and will be
                                combined with 'AND' statements.
    Returns
    -------
    df : pandas.DataFrame
        A DataFrame containing the time series data
        retrieved from the SQL database.
    """
    # function implementation
    cnx = SQLconnect(I)
    table_name = I['table_name']
    if 'cols' in I:
        if I['cols'] == 'all':
            cols = '*'
        else:
            cols = ','.join(I['cols'])
    else:
        cols = '*'
    if 'SQLrowlimit' in I and I['SQLrowlimit'] is not None:
        N = I['SQLrowlimit']
    else:
        N = 'default'
    if 'rows' in I:
        rows = I['rows']
        strings = []
        for row in rows:
            for ts in rows[row]:
                string = " `{}` LIKE '{}'".format(row, ts)
                strings.append(string)
        row = '(' + ' OR '.join(strings) + ')'
    else:
        row = '1=1'
    if 'logical_statements' in I:
        logical_statements = I['logical_statements']
    else:
        logical_statements = []
    df = SQLdataframe(cnx, table_name, limit=N, col=cols, row=row,
                      logical_statements=logical_statements)
    cnx.close()
    return df
    # So, I deleted rows, SQLrowlimit logicalstatement


def get_data_from_SQL(
        user, password, timestamps, database, cols,
        tablename, host, logical_statements=[]):
    '''
    This function automatically access the SQL
    database for a range
    of time instances, sensors, and more
    importantly the SQL definition
    of user, password, database and host.
    And generate a dataframe
    with all the accessed data.
    Parameters
    ----------
    user : str
    password : str
    timestamps : list
        list of strings with the time instants
        that data should be loaded.
    database : str
    cols : list
        channels to be loaded (e.g. sensors)
    tablename : str
        depends on the timestamps to be .
        format fulfilled
    host : str
    logical_statements : list, optional
        in case the sampling frequency
        wants to be changed for example.
        check line 114 in Load_Data.py
        The default is [].
    Returns
    -------
    df_out : data_frame
        contains the time series from the SQL database.
    '''
    dic = {}
    if timestamps == '*':
        inp = dict(
                user=user,
                password=password,
                host=host,
                database=database,
                cols=cols,
                table_name=tablename,
                logical_statements=logical_statements,
                )
        df_out = SQL_read_table(inp)
    else:
        dic = {}
    # breakpoint()
        for s, name in enumerate(timestamps):
            YYYY = name[:4]
            MM = name[4:6]
    # what does this line is doing?
            table_name = tablename.format(YYYY, MM)
            if table_name not in dic:
                dic[table_name] = {'Name': [name]}
            else:
                dic[table_name]['Name'].append(name)
        for s, table_name in enumerate(dic):
            inp = dict(
                        user=user,
                        password=password,
                        host=host,
                        database=database,
                        cols=cols,
                        table_name=table_name,
                        rows=dic[table_name],
                        logical_statements=logical_statements,
                        )
            df = SQL_read_table(inp)
            if s == 0:
                df_out = df
            else:
                df_out = df_out.append(df, ignore_index=True)
    return df_out
