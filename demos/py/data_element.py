class M(type):
    def __new__(cls, name, bases, classdict):  
        for attr in classdict.get('__slots__', ( )):  
            if attr.startswith('_'):  
                def getter(self, attr=attr):   
                    return getattr(self, attr)  
                def setter(self, val=0, attr=attr):  
                    return setattr(self, attr, val)

                classdict['get' + attr[1:]] = getter  
                classdict['set' + attr[1:]] = setter  
        return type.__new__(cls, name, bases, classdict) 


class TaskInfo(object):
    __metaclass__ = M
    __slots__ = ['_id','_task_id','_task_name','_task_remarks','_task_owner','_task_owner',\
                '_task_priority','_task_status','_is_current','_sprint_id','_team_id','_reserved','_task_cost_id','_task_effort',\
                '_task_surplus','_cost_reserved']

class DailyCost(object):
    __metaclass__ = M
    __slots__ = ['_id', '_task_id', '_cost_day', '_task_cost', '_reserved']

class TeamInfo(object):
    __metaclass__ = M
    __slots__ = ['_id','_team_id','_team_name','_name2','_desc','_current_sprint_id','_curr_sprint_workday', '_sprint_week_no']

'''
if __name__ == "__main__":
	print dir(Point)
	p = Point()
	p.setx(10)
	print (p.getx())
'''
