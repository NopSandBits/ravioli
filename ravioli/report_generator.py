from operator import itemgetter


def report_all_functions(results, errors, args):

    # Print globals.
    __print_heading("Globals")
    for result in results:
        for g in result['globals_vars']:
            print(result['filename'] + ':' + str(g.line_number) + ' ' + g.name)

    # Assemble all the functions into one list.
    functions = []
    for result in results:
        for f in result['functions']:
            functions.append({'filename': result['filename'], 'line_number': f.line_number, 'name': f.name,
                              'complexity': f.complexity})

    # Sort the functions by complexity.
    functions = sorted(functions, key=itemgetter('complexity'), reverse=True)

    # Only display results above a threshold.
    functions = [f for f in functions if f['complexity'] >= args.t]

    # Print functions.
    __print_heading("Functions                                                            complexity")
    for f in functions:
        remaining_filename = __print_wrapped_and_indented_string(f['filename'], 72)
        print(remaining_filename + ':' + str(f['line_number']))

        # Wrap long function names.
        print("    ", end='')
        remaining_function_name = __print_wrapped_and_indented_string(f['name'], 70)
        print('{name:70} {complexity:3}'.format(name=remaining_function_name, complexity=f['complexity']))

    if args.e:
        __print_heading("Errors")
        for e in errors:
            print("*** ERROR PROCESSING: " + e.filename)
            print(e.message)


def report_ksf_for_all_modules(results, errors, args):

    # Sort by spaghetti factor.
    results = sorted(results, key=itemgetter('ksf'), reverse=True)

    # Only display results above a threshold.
    results = [r for r in results if r['ksf'] >= args.t]

    __print_heading("File                                         complexity   globals   lines   ksf")
    for result in results:
        remaining_filename = __print_wrapped_and_indented_string(result['filename'], 50)
        if remaining_filename != result['filename']:
            # Some of the filename has already been printed.
            print("{file:46}  {complexity:3}       {globals:3}   {loc:5}   {ksf:3}".format(
                file=remaining_filename, complexity=result['max_scc'], globals=len(result['globals_vars']),
                loc=result['loc'], ksf=result['ksf']))
        else:
            print("{file:50}  {complexity:3}       {globals:3}   {loc:5}   {ksf:3}".format(
                file=remaining_filename, complexity=result['max_scc'], globals=len(result['globals_vars']),
                loc=result['loc'], ksf=result['ksf']))

    if args.e:
        __print_heading("Errors")
        for e in errors:
            print("*** ERROR PROCESSING: " + e.filename)
            print(e.message)


def __print_wrapped_and_indented_string(str, width):
    remaining_str = str
    space_for_str = width
    while len(remaining_str) > space_for_str:
        if len(remaining_str) == len(str):
            # This is the first line.
            print(remaining_str[:space_for_str])
            remaining_str = remaining_str[space_for_str:]
            space_for_str = width - 4
        else:
            print("    ", end='')
            print(remaining_str[:space_for_str])
            remaining_str = remaining_str[space_for_str:]
    if remaining_str != str:
        # We wrapped some of the string. Print an indent so that the next
        # print is indented.
        print("    ", end='')
    return remaining_str


def __print_heading(text):
    print("-------------------------------------------------------------------------------")
    print(text)
    print("-------------------------------------------------------------------------------")

