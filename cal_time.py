#!/usr/bin/env python3
"""
Time difference calculator
Calculates the difference between two manually entered time points
and outputs the difference in days, hours, minutes, and seconds.
"""

import datetime
import sys

def parse_time(time_str):
    """
    Parse time string in format 'YYYY-M-D H:M:S' to datetime object
    """
    return datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

def calculate_time_difference(time1_str, time2_str):
    """
    Calculate the difference between two time points
    """
    time1 = parse_time(time1_str)
    time2 = parse_time(time2_str)

    # Determine which time is later to handle potential negative differences
    if time2 >= time1:
        diff = time2 - time1
        positive_diff = True
    else:
        diff = time1 - time2
        positive_diff = False

    total_seconds = int(diff.total_seconds())

    # Calculate days, hours, minutes, seconds
    days = diff.days
    hours, remainder = divmod(total_seconds - days * 24 * 3600, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds

def main():
    print("时间差计算器")
    print("根据程序内部设定的时间进行计算")
    print("示例格式：YYYY-M-D H:M:S")
    print("例如：2026-4-29 18:20:30")

    # Manual input of two time values inside the program
    time1_input = "2026-4-29 18:20:30"  # First time point
    time2_input = "2026-5-1 12:15:45"   # Second time point

    print(f"\n第一个时间点: {time1_input}")
    print(f"第二个时间点: {time2_input}")

    try:
        days, hours, minutes, seconds = calculate_time_difference(time1_input, time2_input)

        print("\n时间差:")
        print(f"{days} day")
        print(f"{hours} h")
        print(f"{minutes} min")
        print(f"{seconds} s")

    except ValueError as e:
        print(f"时间格式错误: {e}")
        print("请使用格式：YYYY-M-D H:M:S")

if __name__ == "__main__":
    main()