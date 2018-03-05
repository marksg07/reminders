#!/usr/bin/python

from datetime import datetime as dt, timedelta
import datetime
__test = 0

class Todo:
    def __init__(self, name, dt_or_none):
        self.name = name
        self.dt = dt_or_none

    def __str__(self):
        st = '%-20s ' % (self.name)
        if self.dt is None:
            st += 'Someday'
        else:
            st += str_timedelta(self.dt - dt.now())
        return st

    def __repr__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            repr(self.name),
            repr(self.dt)
        )

class Subject:
    def __init__(self, todos=[], lt=None):
        self.todos = todos
        self.last_time = lt

    def check(self, at_time):
        self.last_time = at_time

    def add_todo(self, todo):
        self.todos.append(todo)

    def __repr__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            repr(self.todos),
            repr(self.last_time)
        )


def str_timedelta(td):
    # td interpreted as time - current
    if td.days < 0:
        suff = 'ago'
        td = timedelta() - td  # get positive time
    else:
        suff = 'from now'
    if td.days > 0:
        days = td.days
        if td.seconds > 3600*12:
            days += 1
        pref = '%d days' % (days)
    elif td.seconds >= 3600:
        hours = (td.seconds + 1800) / 3600
        pref = '%d hours' % (hours)
    elif td.seconds >= 60:
        minutes = (td.seconds + 30) / 60
        pref = '%d minutes' % (minutes)
    else:
        return 'Now'
    return pref + ' ' + suff

def cron_addreminder(text, at_dt):
    print('crontab -l > mycron')
    print('echo "%s zenity --notification --text \\"REMINDER\\n%s\\"" >> mycron' % 
        (at_dt.strftime('%M %H %d %m %w'), text))
    print('crontab mycron')
    print('rm mycron')

if __test:
    print 'testing str_td'
    print str_timedelta(timedelta(2, 1, 8))
    print str_timedelta(timedelta(0, 1800, 8))
    print str_timedelta(timedelta() - timedelta(0, 1800, 8))
    print str_timedelta(timedelta(1, 3600*18, 0))
    print str_timedelta(timedelta() - timedelta(1, 3600*18, 0))


if __name__ == '__main__':
    with open('saved_reminders') as f:
        rems = eval(f.read())
    import os
    os.system('cp saved_reminders sr.bak')
    skip_print = 0
    while(1):
        if not skip_print:
            for name, subject in rems.iteritems():
                print '%-20s Last checked' % (name), str_timedelta(subject.last_time - dt.now())
                for todo in subject.todos:
                    print '\t' + str(todo)
                print
        skip_print = 0
        act = raw_input('''Actions:
0 Save and exit
1 Don't save and exit
2 Check subject
3 Complete todo
4 View as ordered list
5 Sort all
6 View subjects, ordered by last check
Which action? ''').strip()
        if act == '0':
            break
        elif act == '1':
            exit(0)
        elif act == '2':
            subjs = rems.keys()
            for i, s_name in enumerate(subjs):
                print i, s_name
            try:
                s_name = subjs[int(raw_input('Which subject? '))]
            except:
                print 'Invalid subject.'
                continue
            subj = rems[s_name]
            subj.check(dt.now())
            while 1:
                act = raw_input('''Subject actions:
0 Update done
1 Add todo
Which action? ''').strip()
                if act == '0':
                    break
                elif act == '1':
                    n = raw_input('Todo: ').strip()
                    while 1:
                        d = raw_input('What time (x days/hours/minutes/d/h/m || m/d[/yy]) || nothing for "sometime"?').strip()
                        if d == '':
                            due_time = None
                            break
                        try:
                            due_time = dt.strptime(d + '23', '%m/%d/%y %H')
                        except ValueError:
                            try:
                                due_time = dt.strptime(d + '/%d 23' % (dt.now().year), '%m/%d/%Y %H')
                            except ValueError:
                                val = d.split(' ')[0]
                                days = 0
                                secs = 0
                                try:
                                    if d[-4:] == 'days' or d[-1] == 'd':
                                        days = int(val)
                                    elif d[-5:] == 'hours' or d[-1] == 'h':
                                        secs = 3600 * int(val)
                                    elif d[-7:] == 'minutes' or d[-1] == 'm':
                                        secs = 60 * int(val)
                                except ValueError:
                                    print 'Invalid time.'
                                    continue
                                due_time = dt.now() + timedelta(days, secs)
                        break
                    todo = Todo(n, due_time)
                    subj.add_todo(todo)

        elif act == '3':
            subjs = rems.keys()
            for i, s_name in enumerate(subjs):
                print i, s_name
            try:
                s_name = subjs[int(raw_input('Which subject? '))]
            except:
                print 'Invalid subject.'
                continue
            subj = rems[s_name]
            for i, todo in enumerate(subj.todos):
                print i, todo.name
            try:
                t_i = int(raw_input('Which todo? '))
            except:
                print 'Invalid todo.'
                continue
            del subj.todos[t_i]
        elif act == '4':
            todos = []
            for name, subject in rems.iteritems():
                for todo in subject.todos:
                    todos.append((name, todo))

            def __sortkey4(t):
                todo = t[1]
                if todo.dt is None:
                    return dt(2100, 1, 1)
                return todo.dt

            todos = sorted(todos, key=__sortkey4)
            for name, todo in todos:
                print '%-10s' % ('(%s)' % (name)), str(todo)
            skip_print = 1
        elif act == '5':
            def __sortkey5(todo):
                if todo.dt is None:
                    return dt(2100, 1, 1)
                return todo.dt

            for name, subject in rems.iteritems():
                subject.todos = sorted(subject.todos, key=__sortkey5)

        elif act == '6':
            sort_rems = sorted(rems.iteritems(), key=lambda t: t[1].last_time)
            for name, subject in sort_rems:
                print '%-20s Last checked %s' % (name, str_timedelta(subject.last_time - dt.now()))
            skip_print = 1



    with open('saved_reminders', 'w') as f:
        f.write(repr(rems))
    try:
        with open('saved_reminders') as f:
            a = eval(f.read())
    except:
        print 'Write failed, restoring backup'
        os.system('cp saved_reminders sr.fail')
        os.system('cp sr.bak saved_reminders')
        os.system('rm sr.bak')
        print 'Backup restored. Failed attempted write in sr.fail.'
