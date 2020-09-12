#!/usr/bin/python3

import sqlite3
import time
import curses

top_offset = 2
padding = 1
border = 1

def fetch():
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

def generate_padding():
    return ' ' * padding

def format_cell(text, cell_width):
    content_width = cell_width - border*2 - padding*2
    content = ('{0: <' + str(content_width) + '}').format(text)
    return '{0}{1}{2}{1}{0}'.format(u'\u2503', generate_padding(), content)

def format_client_row(client, column_width):
    return format_cell(client, column_width)

def format_domain_row(domain, column_width):
    return format_cell(domain, column_width)

def max_width(strings):
    result = 0
    for string in strings:
        result = max(result, len(string))
    return result

def create_window(index, column_width):
    return curses.newwin(curses.LINES - top_offset, column_width, top_offset, column_width * index)

def render_client_lines(client, domains, column_width, window):
    line = 0
    window.addstr(line, 0, format_client_row(client, column_width))
    line += 1
    window.addstr(line, 0, format_cell('', column_width))
    line += 1
    for domain in domains:
        window.addstr(line, 0, format_domain_row(domain, column_width))
        line += 1
        if line + top_offset >= curses.LINES:
            break


def render_client(client, domains, index):
    column_width = max_width(domains.keys()) + (padding*2) + (border*2)
    if (index+1) * column_width > curses.COLS:
        return
    window = create_window(index, column_width)
    render_client_lines(client, domains, column_width, window)
    window.refresh()

def render(stdscr, clients):
    stdscr.addstr(0, 0, time.ctime())
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
#clients = fetch()
#print(table_rows(clients))
