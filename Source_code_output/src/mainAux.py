from bookInputOutput import get_files_in_folder
from helpers import PATH_BOOKS_OBJECT

from auxConvertOccurrences import convert_occurrences_export
from auxBookVerifSpeakers import compare_occurrences
from auxClustering import get_signature

if __name__ == '__main__':
    files = get_files_in_folder(PATH_BOOKS_OBJECT)
    for book_file in files:
        filename = book_file[:-5]
        convert_occurrences_export(filename)
        compare_occurrences(filename)
    get_signature(files)
        
    
