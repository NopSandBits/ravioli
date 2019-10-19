import argparse
import os
import traceback
from pathlib import Path

from ravioli.complexity import calculate_complexity
from ravioli.global_finder import find_globals
from ravioli.line_counter import count
from ravioli.report_generator import report_all_functions, report_ksf_for_all_modules


def run(filename, args):
    errors, results = process_files(args, filename)

    if args.f:
        report_all_functions(results, errors, args)
    else:
        report_ksf_for_all_modules(results, errors, args)


def process_files(args, filename):
    results = []
    errors = []
    if not os.path.isdir(filename):
        # This is a single file.
        results.append(run_single_file(filename))
    else:
        # This is a directory. Run on all the files we can find.
        source_files = get_source_files(args)

        for f in source_files:
            result = run_single_file(str(f))
            if __file_result_is_valid(result):
                # Only save results that are valid.
                results.append(result)
            if type(result) is ParsingError:
                errors.append(result)
    return errors, results


class ParsingError:
    def __init__(self, filename, message):
        self.filename = filename
        self.message = message


def run_single_file(filename):
    try:
        with open(filename, 'r') as f:
            contents = f.read()
            functions = calculate_complexity(contents)
            globals_vars = find_globals(contents)
            loc = count(contents)
            # Find the maximum complexity (scc) of all functions.
            max_scc = find_max_complexity(functions)
            # Calculate the spaghetti factor.
            ksf = max_scc + (5 * len(globals_vars)) + (loc // 20)
            return {'filename': filename, 'functions': functions, 'max_scc': max_scc, 'globals_vars': globals_vars,
                    'loc': loc, 'ksf': ksf}
    except:
        # There was an error parsing this file.
        return ParsingError(filename, traceback.format_exc())


def find_max_complexity(functions):
    if len(functions) > 0:
        max_scc = max([f.complexity for f in functions])
    else:
        max_scc = 0
    return max_scc


def get_source_files(args):
    source_files = list(Path(args.source).glob('**/*.c'))
    if args.x is not None:
        source_files = []
        for ext in args.x:
            source_files += list(Path(args.source).glob('**/*.' + str(ext)))
    return source_files


def main():
    parser = argparse.ArgumentParser(description='Calculate complexity metrics for C code, specifically the Koopman '
                                                 'Spaghetti Factor (KSF).')
    parser.add_argument('source', help='the source file or folder for which to calculate metrics')
    parser.add_argument('-f', action='store_true', help='output a complete list of all globals and functions sorted '
                                                        'by complexity')
    parser.add_argument('-t', default=0, type=int, metavar='threshold', help='Only display results at or above this '
                                                                             'threshold (KSF or function complexity)')
    parser.add_argument('-e', action='store_true', help='show any errors encountered processing source files')
    parser.add_argument('-x', action='append', required=False, help='File extensions to include in the analysis (-x c -x cc -x h ...). If omitted, only .c files are analyzed')

    args = parser.parse_args()
    run(args.source, args)


def __file_result_is_valid(result):
    return type(result) is not ParsingError


if __name__ == "__main__":
    main()
