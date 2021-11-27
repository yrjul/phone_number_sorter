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


class ChunkSorter:
    def __init__(self, file_name, chunk_file_name_format):
        self.file_name = file_name
        self.chunk_file_name_format = chunk_file_name_format
        self.chunk_filenames_list = []
        self.number_of_chunks = 0

    def split_file_to_chunks(self, number_of_lines_in_chunk):
        file = open(self.file_name, 'r')
        while True:
            lines = file.readlines(number_of_lines_in_chunk)
            if not lines:
                break
            numbers_list = []
            for line in lines:
                numbers_list.append(line[3:])
            numbers_list.sort()
            self.write_chunk_to_file(''.join(numbers_list), self.number_of_chunks)
            self.number_of_chunks += 1

    def write_chunk_to_file(self, data, chunk_number):
        file_name = self.chunk_file_name_format.format(chunk_number)
        try:
            with open(file_name, 'w') as file:
                file.write(data)
        except Exception as e:
            print(type(e).__name__, e.args)
            sys.exit(1)
        self.chunk_filenames_list.append(file_name)


class ChunksMerger:
    def __init__(self, chunk_filenames_list, number_of_chunks, buffer_size, output_file_name):
        self.chunk_filenames_list = chunk_filenames_list
        self.number_of_chunks = number_of_chunks
        self.buffer_size = buffer_size
        self.output_file_name = output_file_name

    def merge(self):
        open_chunk_files = self._get_list_of_open_files(self.chunk_filenames_list)
        try:
            with open(self.output_file_name, 'w') as output_file:
                while True:
                    merge_buffer = []
                    for chunk in open_chunk_files:
                        for line in chunk.readlines(self.buffer_size):
                            merge_buffer.append(line)
                    if not merge_buffer:
                        break
                    merge_buffer.sort()
                    for phone_number in merge_buffer:
                        output_file.write("+79" + phone_number)
        except Exception as e:
            print(type(e).__name__, e.args)
            sys.exit(1)
        finally:
            self._close_files(open_chunk_files)

    @staticmethod
    def _get_list_of_open_files(chunk_filenames_list):
        files = []
        for i in range(len(chunk_filenames_list)):
            files.append(open(chunk_filenames_list[i]))
        return files

    @staticmethod
    def _close_files(list_of_open_files):
        for file in list_of_open_files:
            file.close()


def main():
    input_file_name = 'phone_numbers_list.txt'
    chunk_file_name_format = input_file_name + "_tmp_{0}"
    output_file_name = 'sorted_phone_numbers_list.txt'
    chunk_size = 5 * 1024 * 1024  # megabyte
    min_buffer_size = 1000
    time_print = True
    cleanup = True

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
        create_file_with_numbers(input_file_name, n)
        end = time.time()
        if time_print:
            print(f"creation time: {end - start:.3f}", "s")
    elif sys.argv[1] == '--sort':
        input_file_name = sys.argv[2]
        if len(sys.argv) == 4:
            input_file_name = sys.argv[3]
        start = time.time()
        cs = ChunkSorter(input_file_name, chunk_file_name_format)
        cs.split_file_to_chunks(chunk_size)
        buffer_size = max(min_buffer_size, chunk_size // cs.number_of_chunks)
        ChunksMerger(cs.chunk_filenames_list, cs.number_of_chunks, buffer_size, output_file_name).merge()
        end = time.time()
        if time_print:
            print(f"sorting time: {end - start:.3f} s")
        if cleanup:
            for file in cs.chunk_filenames_list:
                os.remove(file)
    return 0


if __name__ == '__main__':
    if main() == 1:
        sys.exit(1)
