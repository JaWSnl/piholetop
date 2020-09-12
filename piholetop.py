#!/usr/bin/python3

import sqlite3
import time
import curses

top_offset = 2
padding = 1
border = 1
column_width = 30

def fetch():
    try:
        now = int(time.time())
        one_hour_ago = now - (60*60)
        conn = sqlite3.connect('/etc/pihole/pihole-FTL.db')
        cur = conn.cursor()
        clients = {}
        for row in cur.execute('SELECT client, domain FROM queries WHERE timestamp > ?', (one_hour_ago,)):
            client = row[0]
            if client not in clients:
                clients[client] = {}
            domain = row[1].split('.')[-2] + '.' + row[1].split('.')[-1]
            if domain not in clients[client]:
                clients[client][domain] = 1
            clients[client][domain] += 1
        return clients
    except sqlite3.Error as e:
        return {}

def generate_padding():
    return ' ' * padding

def format_cell(text, cell_width):
    content_width = cell_width - border*2 - padding*2
    content = ('{0: <' + str(content_width) + '}').format(text)
    return '{0}{1}{2}{1}{0}'.format(u'\u2503', generate_padding(), content)

def format_client_row(client):
    return format_cell(client)

def format_domain_row(domain):
    return format_cell(domain)

def max_width(strings):
    result = 0
    for string in strings:
        result = max(result, len(string))
    return result

def addstr_safe(window, y, x, text):
    (height, width) = window.getmaxyx()
    if width <= (x + len(text)) and width > x:
        window.addstr(y, x, 'E' * (width - x - 1))
    try:
        window.addstr(y, x, text)
    except curses.error as e:
        # Do nothing for now
        return

def render_client_lines(client, domains, window):
    line = 0
    addstr_safe(window, line, 0, format_client_row(client))
    line += 1
    addstr_safe(window, line, 0, format_cell(''))
    line += 1
    for domain, count in domains:
        addstr_safe(window, line, 0, format_domain_row(domain))
        line += 1
        if line + top_offset >= curses.LINES:
            break

def render_client(client, domains, index):
    #column_width = max_width(domains.keys()) + (padding*2) + (border*2)
    column_x = column_width * index
    if (index+1) * column_width > curses.COLS:
        return
    pad = curses.newpad(curses.LINES - top_offset, column_width)
    for y in range(0,curses.LINES-top_offset-1):
        for x in range(0,column_width-1):
            pad.addch(y,x,'O')
#    render_client_lines(client, domains, column_width, pad)
    pad.refresh(0, 0, top_offset, column_x, curses.LINES-1, column_x+column_width-1)

def render(stdscr, clients):
    addstr_safe(stdscr, 0, 0, time.ctime())
    i = 0
    for client, domains in clients.items():
        render_client(client, domains, i)
        i += 1
    stdscr.refresh()

def main(stdscr):
    stdscr.nodelay(True)
    while True:
        c = stdscr.getch()
        if c == curses.ERR:
            render(stdscr, fetch())
        elif c == ord('q'):
            break  # exit

curses.wrapper(main)
#print(fetch())
