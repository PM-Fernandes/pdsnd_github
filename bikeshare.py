"""US Bikeshare Data exploration"""

import os
import time
import pandas as pd

def init_load():
    """
    Cycle thorugh current path files and pick .CSV with labels matching to bike data layout

    Returns
        (pd df) df_city - cities, filename, last modified from current directory
    """
    cur_path = os.getcwd() + "\\"

    print("Loading files in folder: {}".format(cur_path))

    files_counter = 0
    files_okay_counter = 0
    columns_test=[]
    file_test = 0
    okay_files={}

    files_list = os.listdir(cur_path)

    labels = ['Unnamed: 0', 'Start Time', 'End Time', 'Trip Duration', 'Start Station', 'End Station', 'User Type', 'Gender', 'Birth Year']

    for file in files_list:
        if file.split('.')[-1] == 'csv':
            files_counter += 1

            try:
                last_modified = pd.to_datetime(os.path.getmtime(file),unit='s')
                columns_test = list(pd.read_csv(file,nrows=0))

                if len(columns_test) == 9:
                    if columns_test == labels:
                        file_test = 1

                elif len(columns_test) == 7:
                    if columns_test == labels[:7]:
                        file_test = 1

            finally:
                if file_test == 1:
                    files_okay_counter += 1
                    okay_files[file] = last_modified
                columns_test = []
                file_test = 0

    df_city = pd.DataFrame(okay_files.items(),columns=['Filename','Last Modified'])
    print('CSV files available: {}'.format(files_counter))
    print('CSV files okay to be used: {} \n'.format(files_okay_counter))
    print(df_city)

    df_city['City'] = [city.replace('_',' ').split('.')[0] for city in list(okay_files.keys())]

    return df_city

def day_input():
    """
    User day of week prompt

    Returns
        (int) day - day of week number
        (str) day_str - day of week string
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    while True:
        day = None
        day_str = 'all'
        try:
            day_prompt = input("Please input a number for the specific day (1-Monday to 7-Sunday), or 'all':")
            day = int(day_prompt)
            if 0 < day > len(days):
                int('exception throw')
            day_str = day_prompt + '-' + days[day-1]
            if input('\nDay of week: ' + day_str + '. Confirm? Y/N:').lower() in ['yes','y']:
                break
        except (ValueError,TypeError):
            if day_prompt.lower() == 'all':
                if input('\nALL days. Confirm? Y/N:').lower() in ['yes','y']:
                    break
            else:
                print("\n'" + day_prompt + "' is out of range")
    return day, day_str

def month_input():
    """
    User month prompt

    Returns
        (int) month - month number
        (str) month_name - month name
    """
    months = ['January', 'February', 'March', 'April', 'May', 'June']
    while True:
        month = None
        month_name = 'all'
        try:
            month_prompt = input("Please input a number for the month in scope (1-January to 6-June), or 'all':")
            month = int(month_prompt)
            if 0 < month > len(months):
                int('exception throw')
            month_name = months[month-1]
            if input('\nMonth: ' + month_name + '. Confirm? Y/N:').lower() in ['y','yes']:
                break
        except (ValueError,KeyError,IndexError,TypeError):
            if month_prompt.lower() == 'all':
                if input('\nALL months. Confirm? Y/N:').lower() in ['yes','y']:
                    break
            else:
                print("\n'" + month_prompt + "' is out of range")
                continue
    return month,month_name

def get_filters(df_city):
    """
    User prompt for analysis scope

    Args:
        (pd df) df_city - cities, filename, last modified from current directory
    Returns:
        (str) city_file - city filename
        (int) day - number for day of week or None for all days
        (int) month - number for month or None for all months
        (str) scope - all filters in scope
    """

    while True:
        try:
            city_input = input('Please input a city name or number from the list above:')
            city_index = int(city_input)
            if 0 <= city_index < df_city.shape[0]:
                city = df_city['City'][city_index].title()
                city_file = df_city['Filename'][city_index]
            else:
                int('exception throw')
        except ValueError:
            city=city_input.lower().replace('_',' ').split('.')[0]
            if city in df_city['City'].unique():
                city_index = df_city[df_city['City'] == city].index[0]
                city = city.title()
                city_file = df_city['Filename'][city_index]
            else:
                print("\n{} not found".format(city))
                print(df_city)
                continue
        except (KeyError,IndexError):
            print("\n{} not found".format(city))
            print(df_city)
            continue

        if input('\nCity: ' + city + '. Confirm? Y/N:').lower() in ['y','yes']:
            break

    scope = 'City: ' + city
    print('\nWould you like to filter this analysis by month and/or day of the week?')

    day = None
    day_str = 'all'
    month = None
    month_name = 'all'

    while True:
        try:
            window_input = input("Please input: 'day', 'month', 'both' or 'none'?\n")
            window_input = window_input.lower()
            if window_input in ['day','days','day of the week']:
                print('\nDay only:')
                day, day_str = day_input()
                scope += ', day: ' + day_str
                break
            elif window_input in ['month','months']:
                print('\nMonth only:')
                month,month_name = month_input()
                scope += ', month: ' + month_name
                break
            elif window_input == 'both':
                month,month_name = month_input()
                day, day_str = day_input()
                scope += ', day: ' + day_str + ', month: ' + month_name
                break
            elif window_input == 'none':
                if input('All days and months for ' + city + '. Confirm? Y/N:').lower() in ['y','yes']:
                    break
            else:
                print("\n'" + window_input + "' invalid choice")
        except TypeError:
            print("\n'" + window_input + "' unexpected input.")

    return city_file, day, month, scope

def greeting(scope):
    """
    Scope print to user

    Args:
        (str) scope - all filters in scope
    """
    print('\n In scope - ' + scope)
    time.sleep(1.5)
    print('Starting analysis')
    time.sleep(1)

def load_data(city_file, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city_file - filename for the city to be analyzed
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        (pd df) df - Pandas DataFrame containing city data filtered by month and day
    """
    days_dict = {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
    months_dict = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June'}
    df = pd.read_csv(city_file)
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['Start Time'])
    df['Start Hour'] = df['Start Time'].dt.hour
    df['Month'] = df['Start Time'].dt.month
    df['day_week'] = df['Start Time'].dt.weekday
    df['Pick and Drop'] = list(zip(df['Start Station'],df['End Station']))
    # month filter check
    if month:
        df = df[df['Month']==month]
    # day of week filter check
    if day:
        df = df[df['day_week']==day-1]
    # mapping of month and day of week names
    df['day_week'] = df['day_week'].map(days_dict)
    df['Month'] = df['Month'].map(months_dict)

    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    # display the most common month
    print('Most common month in scope: ' + df['Month'].mode()[0])
    # display the most common day of week
    print('Most common day of week in scope: ' + df['day_week'].mode()[0])
    # display the most common start hour
    print('Most common start hour for travels in scope: {}'.format(df['Start Hour'].mode()[0]))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # display most commonly used start station
    print('Most common station for trip start: ' + df['Start Station'].mode()[0])
    # display most commonly used end station
    print('Most common station for trip end: ' + df['End Station'].mode()[0])
    # display most frequent combination of start station and end station trip
    print('Most common pick and drop stations: {}'.format(df['Pick and Drop'].mode()[0]))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # display total travel time
    print('Total Trip Duration: {}'.format(df['Trip Duration'].sum()))
    # display mean travel time
    print('Mean Trip Duration: {}'.format(df['Trip Duration'].mean()))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # Display counts of user types
    print('User type count:')
    print(df.groupby('User Type')['User Type'].count().to_dict())
    # Display counts of gender
    if 'Gender' in df.columns:
        print('\nGender count:')
        print(df.groupby('Gender')['Gender'].count().to_dict())
    # Display earliest, most recent, and most common year of birth
    if 'Birth Year' in df.columns:
        print('\nEarliest birth year: {}'.format(int(df['Birth Year'].min())))
        print('Most recent birth year: {}'.format(int(df['Birth Year'].max())))
        print('Most common birth year: {}'.format(int(df['Birth Year'].mode()[0])))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)

def dataframe_window(df):
    """Window dataframe content 5 rows at a time"""
    row_count = df.shape[0]
    print('There are {} rows in scope for this analysis.'.format(row_count))
    if input('\nWould you like to check the first 5 rows of data? Y/N:').lower() in ['yes','y']:
        i = 5
        while i <= row_count:
            print(df.iloc[i-5:i,9:])
            if i < row_count and input('\nWould you like to continue for the next 5? Y/N:').lower() in ['yes','y']:
                if i+5 > row_count:
                    i = row_count
                else:
                    i +=5
                continue
            else:
                break

def main():
    """Main module"""
    while True:
        df_city = init_load()
        # city,city_file,month,day = get_filters(city_data)
        city_file, day, month, scope = get_filters(df_city)
        greeting(scope)
        df = load_data(city_file, month, day)
        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        dataframe_window(df)

        restart = input("\nWould you like to restart? 'yes' or 'no'?\n")
        if restart.lower() not in ('yes','y'):
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nExecution cancelled by user. Pressing: "Ctrl + c" will trigger this behaviour.')
    finally:
        print('Program ended')
