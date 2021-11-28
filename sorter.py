"""
Created on 27.11.2021 01:45

Description:
1. creation of a file containing N phone numbers (+79XXXXXXXXX)
2. reading the list of phone numbers from a file and saving it sorted to another file
"""

from random import randint
import sys
import os
import time

HELP = """create a file numbers.txt containing a list of N phone numbers:
    --create N numbers.txt
create a file with a standard name (phone_numbers_list.txt) containing a list of N phone numbers:
    --create N

read the list of phone numbers from the numbers.txt file and save it sorted to the sorted.txt file:
    --sort numbers.txt sorted.txt
read the list of phone numbers from the numbers.txt file and save it sorted to the file with a
standard name (sorted_phone_numbers_list.txt):
    --sort numbers.txt
"""


def create_file_with_numbers(file_name, n):
    with open(file_name, 'w') as file:
        for i in range(n):
            file.write("+79" + str(randint(0, 999999999)).zfill(9) + '\n')


class PhoneNumberSorter:
    def __init__(self, input_file_name, output_file_name, chunk_file_name_format):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.chunk_file_name_format = chunk_file_name_format
        self.chunk_file_names_list = []
        self.number_of_chunks = 0

    def split_file_to_chunks(self, number_of_lines_in_chunk):
        file = open(self.input_file_name)
        while True:
            lines = file.readlines(number_of_lines_in_chunk)
            if not lines:
                break
            numbers_list = []
            for line in lines:
                numbers_list.append(line[3:])
            numbers_list.sort()
            self._write_chunk_to_file(''.join(numbers_list), self.number_of_chunks)
            self.number_of_chunks += 1

    def _write_chunk_to_file(self, data, chunk_number):
        file_name = self.chunk_file_name_format.format(chunk_number)
        try:
            with open(file_name, 'w') as file:
                file.write(data)
        except Exception as e:
            print(type(e).__name__, e.args)
            sys.exit(1)
        self.chunk_file_names_list.append(file_name)

    def merge(self):
        open_chunk_files = self._get_list_of_open_files(self.chunk_file_names_list)
        try:
            with open(self.output_file_name, 'w') as output_file:
                while self._identify_the_file_with_min_number():
                    while True:
                        pointer = self.file_with_min_number.tell()
                        phone_number = self.file_with_min_number.readline()
                        if not phone_number:
                            break
                        if self.prev_min_number is None:
                            output_file.write("+79" + phone_number)
                        elif phone_number <= self.min_number:
                            output_file.write("+79" + phone_number)
                        else:
                            self.file_with_min_number.seek(pointer)
                            break
        except Exception as e:
            print(type(e).__name__, e.args)
            sys.exit(1)
        finally:
            self._close_files(open_chunk_files)

    def _get_list_of_open_files(self, chunk_filenames_list):
        self.open_chunk_files = []
        for i in range(len(chunk_filenames_list)):
            self.open_chunk_files.append(open(chunk_filenames_list[i]))
        return self.open_chunk_files

    def _identify_the_file_with_min_number(self):
        self.min_number = None
        self.prev_min_number = None
        self.file_with_min_number = None
        self.first_numbers = []
        for chunk_file in self.open_chunk_files:
            pointer = chunk_file.tell()
            number = chunk_file.readline()
            if not number:
                chunk_file.close()
                self.open_chunk_files.remove(chunk_file)
                continue
            else:
                self.first_numbers.append((number, chunk_file))
                chunk_file.seek(pointer)
        if not self.first_numbers:
            return None  # all chunk files are empty
        for number, chunk_file in self.first_numbers:
            if self.min_number is None:
                self.min_number = number
                self.file_with_min_number = chunk_file
            if number <= self.min_number:
                self.prev_min_number = self.min_number
                self.min_number = number
                self.file_with_min_number = chunk_file
        return self.file_with_min_number

    def remove_chunk_files(self):
        for chunk_file_name in self.chunk_file_names_list:
            os.remove(chunk_file_name)

    @staticmethod
    def _close_files(list_of_open_files):
        for file in list_of_open_files:
            file.close()


def solution_verification(output_file_name):
    previous_line = None
    line_counter = 0
    with open(output_file_name) as output_file:
        while True:
            line = output_file.readline()
            if not line:
                break
            if previous_line is not None and line < previous_line:
                print(f"mistake in the file {output_file_name} on line {line_counter + 1}")
                break
            previous_line = line
            line_counter += 1


def main():
    input_file_name = 'phone_numbers_list.txt'
    chunk_file_name_format = input_file_name + "_tmp_{0}"
    output_file_name = 'sorted_phone_numbers_list.txt'
    chunk_size = 50 * 1024 * 1024  # megabyte
    time_print = True  # set True to print execution time
    remove_chunk_files = True  # set False to not remove chunk files
    check_the_solution = False  # set True to check the solution

    if len(sys.argv) == 1:
        print(HELP)
        return 0

    if len(sys.argv) > 4 or len(sys.argv) < 3 or sys.argv[1] not in ['--create', '--sort']:
        print("invalid arguments\n")
        print(HELP)
        return 1

    if sys.argv[1] == '--create':
        if not sys.argv[2].isnumeric():
            print("invalid arguments\n")
            print(HELP)
            return 1
        n = int(sys.argv[2])
        if len(sys.argv) == 4:
            input_file_name = sys.argv[3]
        start = time.time()
        # creation
        create_file_with_numbers(input_file_name, n)
        end = time.time()
        if time_print:
            print(f"creation time: {end - start:.3f}", "s")
    elif sys.argv[1] == '--sort':
        input_file_name = sys.argv[2]
        if len(sys.argv) == 4:
            input_file_name = sys.argv[3]
        start = time.time()
        # sorting
        pns = PhoneNumberSorter(input_file_name, output_file_name, chunk_file_name_format)
        pns.split_file_to_chunks(chunk_size)
        pns.merge()
        end = time.time()
        if time_print:
            print(f"sorting time: {end - start:.3f} s")
        if remove_chunk_files:
            pns.remove_chunk_files()
        if check_the_solution:
            solution_verification(output_file_name)
    return 0


if __name__ == '__main__':
    if main() == 1:
        sys.exit(1)
