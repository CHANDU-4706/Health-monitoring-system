import duckdb
import pandas as pd
import sys

startTime = f"{sys.argv[1]} {sys.argv[2]}" #ex:"2023-02-23 04:09:00"#
endTime = f"{sys.argv[3]} {sys.argv[4]}" #ex:"2023-02-23 04:11:00"#

SPARK_PATH = "/home/hdoop/Desktop/Spark/"

def find_query(date1, date2):
    years, months, days, hours, minutes = [], [], [], [], []
    parts = date1.split()
    left_part = parts[0].split('-')
    right_part = parts[1].split(':')
    year1, month1, day1 = int(left_part[0]), int(left_part[1]), int(left_part[2])
    hour1, minute1 = int(right_part[0]), int(right_part[1])

    parts = date2.split()
    left_part = parts[0].split('-')
    right_part = parts[1].split(':')
    year2, month2, day2 = int(left_part[0]), int(left_part[1]), int(left_part[2])
    hour2, minute2 = int(right_part[0]), int(right_part[1])
    ''' Getting years '''
    # Exactly N years
    if month1 == 1 and month2 == 12 and day1 == 1 and day2 == 31 and hour1 == 0 \
            and hour2 == 23 and minute1 == 0 and minute2 == 59:
        return [(str(year1), str(year2))], [], [], [], []
    # Exact start
    if year2 > year1 and month1 == 1 and day1 == 1 and hour1 == 0 and minute1 == 0:
        years.append((str(year1), str(year2 - 1)))
        year1 = year2
    # Exact end
    if year2 > year1 and month2 == 12 and day2 == 31 and hour2 == 23 and minute2 == 59:
        years.append((str(year1 + 1), str(year2)))
        year2 = year1
    # Years completed in between
    if year1 != year2:
        if year2 - year1 >= 2:
            years.append((str(year1 + 1), str(year2 - 1)))
        months_left, days_left, hours_left, minutes_left = find_months(month1, day1, hour1, minute1, 12, 31, 23, 59,
                                                                       str(year1))
        months_right, days_right, hours_right, minutes_right = find_months(1, 1, 0, 0, month2, day2, hour2, minute2,
                                                                           str(year2))
        return years, months_left + months_right, days_left + days_right, hours_left + hours_right \
            , minutes_left + minutes_right
    else:
        months, days, hours, minutes = find_months(month1, day1, hour1, minute1,
                                                   month2, day2, hour2, minute2, str(year1))
        return years, months, days, hours, minutes


def find_months(month1, day1, hour1, minute1, month2, day2, hour2, minute2, year):
    months, days, hours, minutes = [], [], [], []
    # Exactly N months
    if day1 == 1 and day2 == 31 and hour1 == 0 and hour2 == 23 and minute1 == 0 and minute2 == 59:
        return [(f'{year}-{str("%02d" % (month1,))}', f'{year}-{str("%02d" % (month2,))}')], [], [], []
    # Exact start
    if month2 > month1 and day1 == 1 and hour1 == 0 and minute1 == 0:
        months.append((f'{year}-{str("%02d" % (month1,))}', f'{year}-{str("%02d" % (month2 - 1,))}'))
        month1 = month2
    # Exact end
    if month2 > month1 and day2 == 31 and hour2 == 23 and minute2 == 59:
        months.append((f'{year}-{str("%02d" % (month1 + 1,))}', f'{year}-{str("%02d" % (month2 - 1,))}'))
        month2 = month1
    # Months completed in between
    if month1 != month2:
        if month2 - month1 >= 2:
            months.append((f'{year}-{str("%02d" % (month1 + 1,))}', f'{year}-{str("%02d" % (month2 - 1,))}'))
        days_left, hours_left, minutes_left = find_days(day1, hour1, minute1, 31, 23, 59,
                                                        f'{year}-{str("%02d" % (month1,))}')
        days_right, hours_right, minutes_right = find_days(1, 0, 0, day2, hour2, minute2,
                                                           f'{year}-{str("%02d" % (month2,))}')
        return months, days_left + days_right, hours_left + hours_right, minutes_left + minutes_right
    else:
        days, hours, minutes = find_days(day1, hour1, minute1, day2, hour2, minute2,
                                         f'{year}-{str("%02d" % (month1,))}')
        return months, days, hours, minutes


def find_days(day1, hour1, minute1, day2, hour2, minute2, year_month):
    days, hours, minutes = [], [], []
    # Exactly N days
    if hour1 == 0 and hour2 == 23 and minute1 == 0 and minute2 == 59:
        return [(f'{year_month}-{str("%02d" % (day1,))}', f'{year_month}-{str("%02d" % (day2,))}')], [], []
    # Exact start
    if day2 > day1 and hour1 == 0 and minute1 == 0:
        days.append((f'{year_month}-{str("%02d" % (day1,))}', f'{year_month}-{str("%02d" % (day2 - 1,))}'))
        day1 = day2
    # Exact end
    if day2 > day1 and hour2 == 23 and minute2 == 59:
        days.append((f'{year_month}-{str("%02d" % (day1 + 1,))}', f'{year_month}-{str("%02d" % (day2,))}'))
        day2 = day1
    # Days completed in between
    if day1 != day2:
        if day2 - day1 >= 2:
            days.append((f'{year_month}-{str("%02d" % (day1 + 1,))}', f'{year_month}-{str("%02d" % (day2 - 1,))}'))
        hours_left, minutes_left = find_hours(hour1, minute1, 23, 59, f'{year_month}-{str("%02d" % (day1,))}')
        hours_right, minutes_right = find_hours(0, 0, hour2, minute2, f'{year_month}-{str("%02d" % (day2,))}')
        return days, hours_left + hours_right, minutes_left + minutes_right
    else:
        hours, minutes = find_hours(hour1, minute1, hour2, minute2, f'{year_month}-{str("%02d" % (day1,))}')
        return days, hours, minutes


def find_hours(hour1, minute1, hour2, minute2, year_month_day):
    hours, minutes = [], []
    # Exactly N hours
    if minute1 == 0 and minute2 == 59:
        return [(f'{year_month_day} {str("%02d" % (hour1,))}', f'{year_month_day} {str("%02d" % (hour2,))}')], []
    # Exact start
    if hour2 > hour1 and minute1 == 0:
        hours.append((f'{year_month_day} {str("%02d" % (hour1,))}', f'{year_month_day} {str("%02d" % (hour2 - 1,))}'))
        hour1 = hour2
    # Exact end
    if hour2 > hour1 and minute2 == 59:
        hours.append((f'{year_month_day} {str("%02d" % (hour1 + 1,))}', f'{year_month_day} {str("%02d" % (hour2,))}'))
        hour2 = hour1
    # Days completed in between
    if hour1 != hour2:
        if hour2 - hour1 >= 2:
            hours.append(
                (f'{year_month_day} {str("%02d" % (hour1 + 1,))}', f'{year_month_day} {str("%02d" % (hour2 - 1,))}'))
        minutes_left = find_minutes(minute1, 59, f'{year_month_day} {str("%02d" % (hour1,))}')
        minutes_right = find_minutes(0, minute2, f'{year_month_day} {str("%02d" % (hour2,))}')
        return hours, minutes_left + minutes_right
    else:
        minutes = find_minutes(minute1, minute2, f'{year_month_day} {str("%02d" % (hour1,))}')
        return hours, minutes


def find_minutes(minute1, minute2, year_month_day_minute):
    return [(f'{year_month_day_minute}:{"%02d" % (minute1,)}', f'{year_month_day_minute}:{"%02d" % (minute2,)}')]


def sql(file, ts1, ts2):
    return duckdb.query(
        f'''
        SELECT service,SUM(count) as count, SUM(avg_cpu*count)/SUM(count) as avg_cpu,
        SUM(avg_ram*count)/SUM(count) as avg_ram,SUM(avg_disk*count)/SUM(count) as avg_disk,
        MAX(max_cpu) as max_cpu,MAX(max_ram) as max_ram,MAX(max_disk) as max_disk
        FROM '{file}' as d
        WHERE d.timestamp >= TIMESTAMP '{ts1}' AND d.timestamp <= TIMESTAMP '{ts2}'
        GROUP BY d.service;
    ''').df()


def query(date1, date2):
    columns = ['service', 'count', 'avg_cpu', 'avg_ram', 'avg_disk', 'max_cpu', 'max_ram', 'max_disk']
    years, months, days, hours, minutes = find_query(date1, date2)
    final_df = pd.DataFrame(columns=columns)
    # Querying years
    for tup in years:
        ts1 = tup[0] + '-01-01 00:00:00'
        ts2 = tup[1] + '-01-01 00:00:00'
        final_df = pd.concat([final_df, sql(SPARK_PATH+'/MapReduceOutput/year.parquet', ts1, ts2)])
    # Querying months
    for tup in months:
        ts1 = tup[0] + '-01 00:00:00'
        ts2 = tup[1] + '-01 00:00:00'
        final_df = pd.concat([final_df, sql(SPARK_PATH+'/MapReduceOutput/month.parquet', ts1, ts2)])
    # Querying days
    for tup in days:
        ts1 = tup[0] + ' 00:00:00'
        ts2 = tup[1] + ' 00:00:00'
        final_df = pd.concat([final_df, sql(SPARK_PATH+'/MapReduceOutput/day.parquet', ts1, ts2)])
    # Querying hours
    for tup in hours:
        ts1 = tup[0] + ':00:00'
        ts2 = tup[1] + ':00:00'
        final_df = pd.concat([final_df, sql(SPARK_PATH+'/MapReduceOutput/hour.parquet', ts1, ts2)])
    # Querying minutes
    for tup in minutes:
        ts1 = tup[0] + ':00'
        ts2 = tup[1] + ':00'
        final_df = pd.concat([final_df, sql(SPARK_PATH+'/MapReduceOutput/minute.parquet', ts1, ts2)])
    final_df.reset_index(inplace=True)
    # Aggregating the results
    result_df = pd.DataFrame(columns=columns)
    for group, frame in final_df.groupby('service'):
        service = group
        count = sum(frame['count'])
        avg_cpu = sum(frame['count'] * frame['avg_cpu']) / sum(frame['count'])
        avg_ram = sum(frame['count'] * frame['avg_ram']) / sum(frame['count'])
        avg_disk = sum(frame['count'] * frame['avg_disk']) / sum(frame['count'])
        max_cpu = max(frame['max_cpu'])
        max_ram = max(frame['max_ram'])
        max_disk = max(frame['max_disk'])
        record = {'service': service, 'count': count, 'avg_cpu': avg_cpu, 'avg_ram': avg_ram, 'avg_disk': avg_disk,
                  'max_cpu': max_cpu, 'max_ram': max_ram, 'max_disk': max_disk}
        result_df = pd.concat([result_df, pd.DataFrame(record, columns=columns, index=[0])], ignore_index=True)
    return result_df

result_df = query(startTime, endTime)


f = open(SPARK_PATH+"/realTimeView.txt")
state = int(f.read(1))
f.close()


pd.set_option('display.max_columns', None)
con = duckdb.connect(database=':memory:')
dt = con.execute(f'''SELECT service,SUM(count) as count, SUM(avg_cpu*count)/SUM(count) as avg_cpu,
SUM(avg_ram*count)/SUM(count) as avg_ram,
SUM(avg_disk*count)/SUM(count) as avg_disk,
Max(max_cpu) as max_cpu,
Max(max_disk) as max_disk,
Max(max_ram) as max_ram
FROM '{SPARK_PATH}/SparkOutput{state}/*.parquet' as d
WHERE d.timestamp >= TIMESTAMP '{startTime}' AND d.timestamp <= TIMESTAMP '{endTime}'
GROUP BY d.service;''')

result = dt.fetchdf()
result_df = pd.concat([result_df,result])
d_df = pd.DataFrame(columns=['service', 'count', 'avg_cpu', 'avg_ram', 'avg_disk', 'max_cpu', 'max_ram', 'max_disk'])
for group, frame in result_df.groupby('service'):
    service = group
    count = sum(frame['count'])
    avg_cpu = sum(frame['count'] * frame['avg_cpu']) / sum(frame['count'])
    avg_ram = sum(frame['count'] * frame['avg_ram']) / sum(frame['count'])
    avg_disk = sum(frame['count'] * frame['avg_disk']) / sum(frame['count'])
    max_cpu = max(frame['max_cpu'])
    max_ram = max(frame['max_ram'])
    max_disk = max(frame['max_disk'])
    record = {'service': service, 'count': count, 'avg_cpu': avg_cpu, 'avg_ram': avg_ram, 'avg_disk': avg_disk,
              'max_cpu': max_cpu, 'max_ram': max_ram, 'max_disk': max_disk}
    d_df = pd.concat([d_df, pd.DataFrame(record, columns=['service', 'count', 'avg_cpu', 'avg_ram', 'avg_disk', 'max_cpu', 'max_ram', 'max_disk'], index=[0])], ignore_index=True)

print(d_df)

