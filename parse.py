import sys, os
import xlsxwriter

# Check args and get in the subdir that the caller wants us in
if len(sys.argv) < 2:
    sys.exit('Usage: %s plotdir' % sys.argv[0])

if not os.path.exists(sys.argv[1]):
    print('************pwd is ',os.getcwd())
    print('ERROR: plotdir %s was not found!' % sys.argv[1])
    sys.exit(1)

subdir=sys.argv[1]
os.chdir(subdir)

#-------------------------------------------------------------------------------------------------------------------------------------------
# Library of plot functions
def plot_generic_import(ws, max_rows):
    # This fuction can durably handle importing IMB log files to a worksheet
    # The data will start in Cell A3 and run thru \n
    # All platform data columns are interleaved so better visual comparisons can be made
    # Todo: add something about the build/details of the fi provider in ws_comment
    r = c = 0
    ws_comment = ''
    num_data_rows = -1 #Because the first row will be the headings of the type (strings like #bytes, #t[usec], etc)

    # Write a comment into cell A1 with the cmd line invocation for all benchs in platforms
    for platform in platforms:
        ws_comment += "{}\n".format(rawfiles[platform][0]) #Line 0 should always have platform and cmd invocation
        while not str(rawfiles[platform][curline[platform]]).__contains__('#---------------------------------'):
            ws_comment += str(rawfiles[platform][curline[platform]])
            curline[platform] += 1
        curline[platform] += 1 #Skip the ### line
        while str.startswith(str(rawfiles[platform][curline[platform]]), "#"): #skip over any other comment lines
            curline[platform] += 1
        ws_comment += '**************************\n'
    ws.write_comment('A1', ws_comment, {'x_scale':5.5, 'y_scale':5.5})

    # Row 0 is handled below
    r = 1

    # Col 0 is a special case, only write from the first file for that and sanity check all the values are ==
    while rawfiles[platforms[0]][curline[platforms[0]]] != '\n' and num_data_rows < max_rows:
        row_lists = {}
        for platform in platforms:
            row_lists[platform] = str(rawfiles[platform][curline[platform]]).split()
            curline[platform] += 1
        #Sanity check
        # todo, this should do all platforms, not just first two
        if row_lists[platforms[0]][0] != row_lists[platforms[1]][0]:
            print('Going to thorw error for', row_lists[platforms[0]][0], " and ", row_lists[platforms[1]][0])
            raise ValueError('The first element in column 0 should all be the same all the time')

        row_zero = []
        temp_row = []
        # Column 0
        try:
            temp_row.append(float(row_lists[platforms[0]][0]))
        except ValueError:
            temp_row.append(row_lists[platforms[0]][0])

        # All the other columns
        num_columns = len(row_lists[platforms[0]])
        for i in range(1, num_columns, 1):
            for platform in platforms:
                try:
                    temp_row.append(float(row_lists[platform][i]))
                except ValueError:
                    temp_row.append(row_lists[platform][i])
                # Put the platform for this number in Column 0
                row_zero.append(platform)
        #Write all data to a row at once
        #Yes we write row 0 several times with the same values, oh well.
        ws.write_row(r, 0, temp_row)
        ws.write_row(0, 1, row_zero)
        r += 1   
        num_data_rows += 1

    return num_data_rows


def plot_min_max_avg_thru(title, ws, wb, max_rows):
    ws.title = title

    num_data_rows = plot_generic_import(ws, max_rows)
    if num_data_rows > max_rows:
        num_data_rows = max_rows

    c = 1
    num_of_platforms = len(platforms)
    c += num_of_platforms #Skip over the #repetitions

    min_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_min_latency'
    min_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        min_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    min_latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base':10,
    })
        
    min_latency_chart.set_y_axis({
        'name': "t_minium[usec]",
    })
    min_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('A21', min_latency_chart)


    max_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_max_latency'
    max_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        max_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    max_latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base': 10,
    })
    max_latency_chart.set_y_axis({
        'name': "t_maxium[usec]",
    })
    max_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('I21', max_latency_chart)


    avg_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_avg_latency'
    avg_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        avg_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    avg_latency_chart.set_x_axis({
        'name': 'Message Size (bytes)',
        'log_base': 10,
    })
        
    avg_latency_chart.set_y_axis({
        'name': "t_average[usec]",
    })
    avg_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('Q21', avg_latency_chart)

    thru_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    chart_name = title+'_throughput'
    thru_chart.set_title({'name': chart_name})
    for plaform in platforms:
        thru_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    thru_chart.set_x_axis({
        'name': "Message Size (bytes)",
    })
    thru_chart.set_y_axis({
        'name': "Mbytes/sec",
        'log_base': 10,
    })
    thru_chart.set_size({'width':500, 'height': 400})
    ws.insert_chart('O1', thru_chart)


def plot_min_max_avg(title, ws, wb, max_rows):
    ws.title = title

    num_data_rows = plot_generic_import(ws, max_rows)
    if num_data_rows > max_rows:
        num_data_rows = max_rows

    c = 1
    num_of_platforms = len(platforms)
    c += num_of_platforms #Skip over the #repetitions

    min_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_min_latency'
    min_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        min_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    min_latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base':10,
    })
        
    min_latency_chart.set_y_axis({
        'name': "t_minium[usec]",
    })
    min_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('A21', min_latency_chart)


    max_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_max_latency'
    max_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        max_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    max_latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base': 10,
    })
    max_latency_chart.set_y_axis({
        'name': "t_maxium[usec]",
    })
    max_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('I21', max_latency_chart)


    avg_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_avg_latency'
    avg_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        avg_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    avg_latency_chart.set_x_axis({
        'name': 'Message Size (bytes)',
        'log_base': 10,
    })
        
    avg_latency_chart.set_y_axis({
        'name': "t_average[usec]",
    })
    avg_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('Q21', avg_latency_chart)


def plot_latency_thru(title, ws, wb, max_rows):
    ws.title = title

    num_data_rows = plot_generic_import(ws, max_rows)
    if num_data_rows > max_rows:
        num_data_rows = max_rows

    c = 1
    num_of_platforms = len(platforms)
    c += num_of_platforms #Skip over the #repetitions

    if num_data_rows == 1:
        latency_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    else:
        latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_latency'
    latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base': 10,
    })
    latency_chart.set_y_axis({
        'name': "t[usec]",
    })
    latency_chart.set_size({'width':1000, 'height': 600})
    ws.insert_chart('A26', latency_chart)

    thru_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    chart_name = title+'_throughput'
    thru_chart.set_title({'name': chart_name})

    for plaform in platforms:
        thru_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    thru_chart.set_x_axis({
        'name': "Message Size (bytes)",
    })
    thru_chart.set_y_axis({
        'name': "Mbytes/sec",
    })
    thru_chart.set_size({'width':640, 'height': 500})
    ws.insert_chart('J1', thru_chart)


def plot_nobytes_min_max_avg(title, ws, wb, max_rows):
    ws.title = title

    # 1 Chart for one row of data
    num_data_rows = plot_generic_import(ws, max_rows)
    num_data_rows = 1
 
    the_chart = wb.add_chart({'type': 'column'})
    chart_name = title+'_latency'
    the_chart.set_title({'name': chart_name})

    # Add them by column
    c = 1
    num_of_platforms = len(platforms)
    #next_column_set_start = c + 1 
    #t[min]

    for i in range (0,3): #3 runs, min, max, avg
            the_chart.add_series({
                'name': [title, 1, c],
                'categories': [title, 0, c, 0, c+(num_of_platforms-1)],  
                'values': [title, 2, c, 2, c+(num_of_platforms-1)], 
            })
            c += num_of_platforms

    the_chart.set_y_axis({
        'name': "t[usec]",
    })

    the_chart.set_x_axis({
        'name': "Platform",
    })
    the_chart.set_size({'width':1000, 'height': 600})
    ws.insert_chart('A6', the_chart)



def plot_latency_thru_msgcnt(title, ws, wb, max_rows):
    ws.title = title

    num_data_rows = plot_generic_import(ws, max_rows)
    if num_data_rows > max_rows:
        num_data_rows = max_rows

    c = 1
    num_of_platforms = len(platforms)
    c += num_of_platforms #Skip over the #repetitions

    latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_latency'
    latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base': 10,
    })
    latency_chart.set_y_axis({
        'name': "t[usec]",
    })
    latency_chart.set_size({'width':1000, 'height': 600})
    ws.insert_chart('A22', latency_chart)

    thru_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    chart_name = title+'_throughput'
    thru_chart.set_title({'name': chart_name})

    for plaform in platforms:
        thru_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    thru_chart.set_x_axis({
        'name': "Message Size (bytes)",
    })
    thru_chart.set_y_axis({
        'name': "Mbytes/sec",
    })
    thru_chart.set_size({'width':540, 'height': 400})
    ws.insert_chart('L1', thru_chart)

    msgcnt_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    chart_name = title+'_msg_count'
    msgcnt_chart.set_title({'name': chart_name})

    for plaform in platforms:
        msgcnt_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    msgcnt_chart.set_x_axis({
        'name': "Message Size (bytes)",
    })
    msgcnt_chart.set_y_axis({
        'name': "Messages/sec",
    })
    msgcnt_chart.set_size({'width':540, 'height': 400})
    ws.insert_chart('R22', msgcnt_chart)


def plot_thru_msgcnt(title, ws, wb, max_rows):
    ws.title = title

    num_data_rows = plot_generic_import(ws, max_rows)
    if num_data_rows > max_rows:
        num_data_rows = max_rows

    c = 1
    num_of_platforms = len(platforms)
    c += num_of_platforms #Skip over the #repetitions    

    thru_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    chart_name = title+'_throughput'
    thru_chart.set_title({'name': chart_name})

    for plaform in platforms:
        thru_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    thru_chart.set_x_axis({
        'name': "Message Size (bytes)",
    })
    thru_chart.set_y_axis({
        'name': "Mbytes/sec",
    })
    thru_chart.set_size({'width':540, 'height': 400})
    ws.insert_chart('L1', thru_chart)

    msgcnt_chart = wb.add_chart({'type': 'column', 'subtype':'clustered'})
    chart_name = title+'_msg_count'
    msgcnt_chart.set_title({'name': chart_name})

    for plaform in platforms:
        msgcnt_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    msgcnt_chart.set_x_axis({
        'name': "Message Size (bytes)",
    })
    msgcnt_chart.set_y_axis({
        'name': "Messages/sec",
    })
    msgcnt_chart.set_size({'width':540, 'height': 400})
    ws.insert_chart('A22', msgcnt_chart)


def plot_pure_ovrl(title, ws, wb, max_rows):
    ws.title = title

    num_data_rows = plot_generic_import(ws, max_rows)
    if num_data_rows > max_rows:
        num_data_rows = max_rows

    c = 1
    num_of_platforms = len(platforms)
    c += num_of_platforms #Skip over the #repetitions

    pure_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_pure_latency'
    pure_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        pure_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    pure_latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base':10,
    })

    pure_latency_chart.set_y_axis({
        'name': "t_pure[usec]",
    })
    pure_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('A21', pure_latency_chart)


    ovrl_latency_chart = wb.add_chart({'type': 'scatter', 'subtype':'straight_with_markers'})
    chart_name = title+'_ovrl_latency'
    ovrl_latency_chart.set_title({'name': chart_name})
    for plaform in platforms:
        ovrl_latency_chart.add_series({
            'name': plaform,
            'categories': [title, 2, 0, 2+num_data_rows, 0 ],
            'values': [title, 2, c, 2+num_data_rows, c],
            'marker': {'type': 'automatic'},
        })
        c += 1

    ovrl_latency_chart.set_x_axis({
        'name': "Message Size (bytes)",
        'log_base': 10,
    })
    ovrl_latency_chart.set_y_axis({
        'name': "t_ovrl[usec]",
    })
    ovrl_latency_chart.set_size({'width':500, 'height': 520})
    ws.insert_chart('I21', ovrl_latency_chart) 
                                             

#-------------------------------------------------------------------------------------------------------------------------------------------
# Library of helper functions

#get_rawfiles will set rawfiles, curline, and platforms
def get_rawfiles(prefixs, suffixs):
    filenames = [fn for fn in os.listdir(os.curdir)]
    filenames = list(filter(lambda x: x.startswith(tuple(prefixs)), filenames))
    filenames = list(filter(lambda x: x.endswith(tuple(suffixs)), filenames))

    for file in filenames:
        tmp=file.split('.')
        f = open(file, "r")
        rawfiles[tmp[1]] = f.readlines()
        print(f"Found platform = {tmp[1]}")
        platforms.append(tmp[1])
        curline[tmp[1]] = 0
        f.close()

# Resets all line cursors to 0, probably in prep for another call to advance_curline
def reset_curline():
    for platform in platforms:
        curline[platform] = 0

# Seek the targetstring in the rawfiles (they should be in sync)
# Curline is set to the next item and clobbered after that item is found
# returns the benchmark name for the benchmark we just found
def advance_curline(targetString):
    for platform in platforms:
        while not rawfiles[platform][curline[platform]] == targetString:
            curline[platform] += 1

    # Sanity check all the current cursors in rawfiles are the same benchmark name
    for platform in platforms:       
        if rawfiles[platform][curline[platform]] != rawfiles[platform][curline[platform]] or \
           rawfiles[platform][curline[platform]+1] != rawfiles[platform][curline[platform]+1] :
            raise AssertionError("Curline sanity check failed on targetsrting: " + targetString + \
                 "Are you sure all log files are from the same run with no errors?")

    retval = targetString.split()[2]
    try:
        if rawfiles[platforms[0]][curline[platforms[0]]+1].startswith('# #processes ='):
             retval = "{0}_p={1}".format(retval, rawfiles[platforms[0]][curline[platforms[0]]+1].split()[3] )
    except(ValueError):
        print('no process?')

    return retval


#-------------------------------------------------------------------------------------------------------------------------------------------
# IMB test family handlers
# Each handler's max_rows parm can be tuned below

def parse_MPI1():
    # Setup to parse all *MPI1*.out files line by line and generate a xlsx file    
    wb = xlsxwriter.Workbook("IMB-MPI1-%s.xlsx"%(os.path.basename(subdir)))
    default_max_rows = 30

    try:
        # Graph_pingpongs
        advance_curline('# Benchmarking PingPong \n')
        ws = wb.add_worksheet('PingPong')
        plot_latency_thru('PingPong', ws, wb, default_max_rows+1)
    except(IndexError):
        reset_curline()

    try :
        advance_curline('# Benchmarking PingPing \n')
        ws = wb.add_worksheet('PingPing')
        plot_latency_thru('PingPing', ws, wb, default_max_rows+1)
    except(IndexError):
        reset_curline()

    try :
        # Graph Biband
        reset_curline()
        while 1:
            tmp_name = advance_curline('# Benchmarking Biband \n')
            ws = wb.add_worksheet(tmp_name)
            plot_thru_msgcnt(tmp_name, ws, wb, default_max_rows+1)
            
    except(IndexError):
        reset_curline()


    try :
        # Graph Uniband
        while 1:
            tmp_name = advance_curline('# Benchmarking Uniband \n')
            ws = wb.add_worksheet(tmp_name)
            plot_thru_msgcnt(tmp_name, ws, wb, default_max_rows+1)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Barrier
        tmp_name = advance_curline('# Benchmarking Barrier \n')
        ws = wb.add_worksheet(tmp_name)
        plot_nobytes_min_max_avg(tmp_name, ws, wb, default_max_rows)

    except(IndexError):
        reset_curline()

    try :
        # Graph Sendrecv
        while 1:
            tmp_name = advance_curline('# Benchmarking Sendrecv \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg_thru(tmp_name, ws, wb, default_max_rows+1)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Exchange
        while 1:
            tmp_name = advance_curline('# Benchmarking Exchange \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg_thru(tmp_name, ws, wb, default_max_rows+1)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Allreduce
        while 1:
            tmp_name = advance_curline('# Benchmarking Allreduce \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Reduce
        while 1:
            tmp_name = advance_curline('# Benchmarking Reduce \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Reduce_local
        while 1:
            tmp_name = advance_curline('# Benchmarking Reduce_local \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Reduce_scatter
        while 1:
            tmp_name = advance_curline('# Benchmarking Reduce_scatter \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Reduce_scatter_block
        while 1:
            tmp_name = advance_curline('# Benchmarking Reduce_scatter_block \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Allgather
        while 1:
            tmp_name = advance_curline('# Benchmarking Allgather \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Allgatherv
        while 1:
            tmp_name = advance_curline('# Benchmarking Allgatherv \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Gather
        while 1:
            tmp_name = advance_curline('# Benchmarking Gather \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Gatherv
        while 1:
            tmp_name = advance_curline('# Benchmarking Gatherv \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Scatter
        while 1:
            tmp_name = advance_curline('# Benchmarking Scatter \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Scatterv
        while 1:
            tmp_name = advance_curline('# Benchmarking Scatterv \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Alltoall
        while 1:
            tmp_name = advance_curline('# Benchmarking Alltoall \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Alltoallv
        while 1:
            tmp_name = advance_curline('# Benchmarking Alltoallv \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Bcast
        while 1:
            tmp_name = advance_curline('# Benchmarking Bcast \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()




    #########################
    # End
    print('parse_MPI1-----> parsed directory ' + subdir)
    wb.close()



def parse_P2P():
    # Setup to parse all *P2P*.out files line by line and generate a xlsx file    
    wb = xlsxwriter.Workbook("IMB-P2P-%s.xlsx"%(os.path.basename(subdir)))
    default_max_rows = 30

    try :
        # Graph PingPong
        while 1:
            tmp_name = advance_curline('# Benchmarking PingPong\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph PingPing
        while 1:
            tmp_name = advance_curline('# Benchmarking PingPing\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Unirandom
        while 1:
            tmp_name = advance_curline('# Benchmarking Unirandom\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Birandom
        while 1:
            tmp_name = advance_curline('# Benchmarking Birandom\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Corandom
        while 1:
            tmp_name = advance_curline('# Benchmarking Corandom\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Stencil2D
        while 1:
            tmp_name = advance_curline('# Benchmarking Stencil2D (4 x 4)\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph Stencil3D
        while 1:
            tmp_name = advance_curline('# Benchmarking Stencil3D (2 x 2 x 4)\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)
            
    except(IndexError):
        reset_curline()

    try :
        # Graph SendRecv_Replace
        while 1:
            tmp_name = advance_curline('# Benchmarking SendRecv_Replace\n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru_msgcnt(tmp_name, ws, wb, default_max_rows)

    except(IndexError):
        reset_curline()



    #########################
    # End
    print('parse_P2P-----> parsed directory ' + subdir)
    wb.close()




def parse_RMA():
    # Setup to parse all *RMA*.out files line by line and generate a xlsx file    
    wb = xlsxwriter.Workbook("IMB-RMA-%s.xlsx"%(os.path.basename(subdir)))
    default_max_rows = 30

    try :
        # Graph Unidir_put
        while 1:
            tmp_name = advance_curline('# Benchmarking Unidir_put \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph Bidir_put
        while 1:
            tmp_name = advance_curline('# Benchmarking Bidir_put \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Unidir_get
        while 1:
            tmp_name = advance_curline('# Benchmarking Unidir_get \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph Bidir_get
        while 1:
            tmp_name = advance_curline('# Benchmarking Bidir_get \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Put_local
        while 1:
            tmp_name = advance_curline('# Benchmarking Put_local \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph Put_all_local
        while 1:
            tmp_name = advance_curline('# Benchmarking Put_all_local \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

  
    try :
        # Graph One_put_all
        while 1:
            tmp_name = advance_curline('# Benchmarking One_put_all \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph One_get_all
        while 1:
            tmp_name = advance_curline('# Benchmarking One_get_all \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph All_put_all
        while 1:
            tmp_name = advance_curline('# Benchmarking All_put_all \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph All_get_all
        while 1:
            tmp_name = advance_curline('# Benchmarking All_get_all \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph Exchange_put
        while 1:
            tmp_name = advance_curline('# Benchmarking Exchange_put \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()


    try :
        # Graph Exchange_get
        while 1:
            tmp_name = advance_curline('# Benchmarking Exchange_get \n')
            ws = wb.add_worksheet(tmp_name)
            plot_min_max_avg(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Get_accumulate
        while 1:
            tmp_name = advance_curline('# Benchmarking Get_accumulate \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Accumulate
        while 1:
            tmp_name = advance_curline('# Benchmarking Accumulate \n')
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)  
            
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Fetch_and_op
        while 1:
            tmp_name = advance_curline('# Benchmarking Fetch_and_op \n')
            tmp_name = tmp_name + "_nonagg"
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)
            tmp_name = advance_curline('# Benchmarking Fetch_and_op \n')
            tmp_name = tmp_name + "_aggregate"
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)
    
    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Compare_and_swap
        while 1:
            tmp_name = advance_curline('# Benchmarking Compare_and_swap \n')
            tmp_name = tmp_name + "_nonagg" #shortened to be <= 31 chars
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)
            tmp_name = advance_curline('# Benchmarking Compare_and_swap \n')
            tmp_name = tmp_name + "_aggregate"
            ws = wb.add_worksheet(tmp_name)
            plot_latency_thru(tmp_name, ws, wb, default_max_rows)

    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    try :
        # Graph Truly_passive_put
        while 1:
           tmp_name = advance_curline('# Benchmarking Truly_passive_put \n')
           ws = wb.add_worksheet(tmp_name)
           plot_pure_ovrl(tmp_name, ws, wb, default_max_rows)

    except(IndexError, xlsxwriter.exceptions.DuplicateWorksheetName):
        reset_curline()

    #########################
    # End
    print('parse_RMA-----> parsed directory ' + subdir)
    wb.close()



###############################################################
# Start main program
# lobal vars that will be reused/clobbered for every parse function
rawfiles = {}
platforms = []
curline = {}

get_rawfiles(['IMB-MPI1'], ['out'])
parse_MPI1()

# rawfiles = {}
# platforms = []
# curline = {}

# get_rawfiles(['IMB-P2P'], ['out'])
# parse_P2P()

# rawfiles = {}
# platforms = []
# curline = {}

# get_rawfiles(['IMB-RMA'], ['out'])
# parse_RMA()


# Good exit:
exit(0)
