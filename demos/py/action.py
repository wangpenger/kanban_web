import web
import logging
import logging.config
import sqlite3_crud
import data_element
import time
'''
error page: return render.error_page(name)
'''

members_separator = "|"
card_owner_separator = '&'
task_status_backlog = 0
task_status_ongoing = 1
task_status_pending = 2
task_status_done = 3
task_status_deleted = 999
PATH_LOG_CONF = '/home/your user name/proj2/conf/logger.conf'

logging.config.fileConfig(PATH_LOG_CONF)
logger = logging.getLogger("example01")
render = web.template.render('../templates/')

urls = (
		'/kanban', 'Index',
		'/pre_create_task', 'PreCreateTask',
		'/action_create_task', 'CreateTask',
		'/pre_task_burn',	'PreTaskBurn',
		'/action_task_burn',	'TaskBurned',
		'/action_delete_task',  'DeleteTask',
		'/action_move_taskcard',  'MoveTaskCard',
		'/action_error', 	'ErrorPage',
		'/burndown',		'BurnDownChart',
		'/yesterday_did',		'YesterdayDid'
)

def get_team_sprint_info(team_id):
	conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
	fetch_sql = 'select * from team_info where team_id = ?'
	if conn is not None:
		result = sqlite3_crud.fetch(conn, fetch_sql, team_id)
		if result is not None:
			logger.debug('successfully fetch sprint info: team_id=%s', team_id)
			team_info = data_element.TeamInfo()
			for e in range(len(result)):
				team_info.setteam_name(result[e][1])
				team_info.setname2(result[e][2])
				#team_info.setdesc(result[e].desc) #for reserved.
				team_info.setcurrent_sprint_id(result[e][4])
				week_in_year_info = "%s%d" % ('W-',int(time.strftime("%W")) + 1)
				team_info.setsprint_week_no(week_in_year_info)
				return team_info
	else:
			logger.error('get_sprint_info failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)

def queryMembers(tandem_memberIDs):
	tandem_memberIDs = tandem_memberIDs.replace(members_separator, ',')
	conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
	fetch_sql = 'select * from team_members_info where id in (' + tandem_memberIDs +') order by card_id asc'
	if conn is not None:
		result = sqlite3_crud.fetchall(conn, fetch_sql)
		if result is not None:
			logger.debug('successfully fetch [%d] records(memberIDs=%s) from team_members_info', len(result),tandem_memberIDs)
			name_list = ''
			for e in range(len(result)):
				name_list += result[e][3] + card_owner_separator  #result[e][3]: 3 indicates the index of name in table.
			name_list = name_list[0:len(name_list)-1]
	else:
		logger.error('queryMembers failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
	return name_list

class Index:
	def queryTasks(self, team_id):
		conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
		fetch_sql = 'select *,b.id task_cost_id from task_info a,task_cost b where a.is_current = 1 and a.task_status != 999 and a.team_id = ? and a.task_id = b.task_id order by task_id asc'
		if conn is not None:
			result = sqlite3_crud.fetch(conn, fetch_sql, team_id)
			if result is not None:
				logger.debug('successfully fetch [%d] records from task_info', len(result))
		else:
			logger.error('queryTasks failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
		return result
	def GET(self):
		client_ip = web.ctx.ip
		logger.info('the user [%s] access the website.', client_ip)
		team_id = [1]
		result_all = self.queryTasks(team_id)
		if result_all is None:
			return render.error_page("query tasks from db failed.")
		else:
			result = []
			result_ongoing = []
			result_pending = []
			result_done = []
			for e in range(len(result_all)):
				names = queryMembers(result_all[e][4])
				tuple_names=names,
				result_all[e] = result_all[e] + tuple_names
				if result_all[e][6] == task_status_backlog:
					result.append(result_all[e])	#result_backlog
				elif result_all[e][6] == task_status_ongoing:
					result_ongoing.append(result_all[e])
				elif result_all[e][6] == task_status_pending:
					result_pending.append(result_all[e])
				elif result_all[e][6] == task_status_done:
					result_done.append(result_all[e])
				else:
					result.append(result_all[e])	#default:result_backlog
		team_info = get_team_sprint_info(team_id)
		return render.home_page(team_info,result,result_ongoing,result_pending,result_done)

def queryAllPersonInfo():
	conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
	fetch_sql = 'SELECT * FROM team_members_info WHERE team_id = ? order by card_id asc'
	team_id = [1]
	if conn is not None:
		result = sqlite3_crud.fetch(conn, fetch_sql, team_id)
		if result is not None:
			logger.debug('successfully fetch [%d] records from team_members_info', len(result))
	else:
		logger.error('query person failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
	return result;
		
class PreCreateTask:
	def GET(self):
		person_result = queryAllPersonInfo()
		if person_result is not None:
			return render.pre_create_task(person_result)
		else:
			return render.error_page("query member info in db failed.")
		
class CreateTask:
	def POST(self):
		forms = web.input()
		task_name = forms.get('task_name').encode("UTF-8")
		remarks = forms.get('remarks').encode("UTF-8")
		task_effort = forms.get('task_effort').encode("UTF-8")
		task_owner = forms.get('task_owner').encode("UTF-8")
		task_priority = forms.get('task_priority').encode("UTF-8")
		task_color = forms.get('task_color').encode("UTF-8")
		
		#get the max task_id in table.
		conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
		team_id = [1]
		fetch_sql = 'select max(task_id) from task_info where team_id = ?'
		result = sqlite3_crud.fetch(conn, fetch_sql, team_id)
		if result is None:
			max_task_id = 0
		else:
			max_task_id = result[0][0]
			if max_task_id is None:
				max_task_id = 0
		#insert into task_info
		conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
		new_task_id = max_task_id + 1
		sql_task_info = ['insert into task_info(task_id,task_name,task_remarks,task_owner,task_priority,task_status,is_current,sprint_id,team_id,task_color) values(?,?,?,?,?,?,?,?,?,?)',\
						 'insert into task_cost(task_id,task_effort,task_surplus,is_current,team_id) values(?,?,?,?,?)']
		task_info_data = [(new_task_id,task_name,remarks,task_owner,task_priority,0,1,0,1,task_color),\
						  (new_task_id,task_effort,task_effort,1,1)]
		save_result = sqlite3_crud.save_trans(conn, sql_task_info, task_info_data)
		
		executeMsg = 'task creation successfully!' if save_result else 'task creation failed!'
		returnMSG = "<script type=\"text/javascript\">\
					setTimeout('window.opener.location.reload();', 1000);\
					setTimeout('window.close()', 1000);\
					</script><h3>" + executeMsg + "</h3>"
		return returnMSG

class PreTaskBurn:
	def GET(self):
		forms = web.input()
		task_info = data_element.TaskInfo()
		task_info.setid(forms.get('id'))
		task_info.settask_name(forms.get('task_name'))
		task_info.settask_effort(forms.get('task_effort'))
		task_info.settask_status(forms.get('task_status'))
		task_info.settask_cost_id(forms.get('task_cost_id'))
		task_info.settask_id(forms.get('task_id'))

		person_result = queryAllPersonInfo()
		if person_result is not None:
			return render.pre_task_burn(task_info, person_result)
		else:
			return render.error_page("query member info in db failed.")

class TaskBurned:
	def update_task_info(self, task_info):
		conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
		updateInfo_sql = ['update task_info set task_name = ?,task_owner = ? where id = ?',\
							'update task_cost set task_effort = ? where id = ?']
		task_info_data = [(task_info.gettask_name(), task_info.gettask_owner(), task_info.getid()), \
							(task_info.gettask_effort(),task_info.gettask_cost_id())]
		if conn is not None:
			result = sqlite3_crud.save_trans(conn, updateInfo_sql, task_info_data)
			if result == True:
				logger.info('successfully update task info(id=%s, new name=%s, new owner=%s, new effort = %s)',\
							task_info.getid(), task_info.gettask_name(), task_info.gettask_owner(), task_info.gettask_effort())
				return True;
		else:
			logger.error('burn task failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
		return False;

        #'reserved' in table daily_cost is used for task executer.
	def add_task_daily_cost(self, daily_cost):
		conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
		daily_cost_sql = ['delete from daily_cost where task_id = ? and cost_day = ? and is_current = ? and team_id = ? and reserved = ?',\
						'insert into daily_cost(task_id,cost_day,task_cost,is_current,team_id,reserved) values(?,?,?,?,?,?)',\
						'update task_cost set task_surplus = task_effort - (select CASE WHEN sum(task_cost) is NULL THEN 0 ELSE sum(task_cost) END  from daily_cost where task_id = ? and is_current = ? and team_id = ?) \
						where task_id = ? and is_current = ? and team_id = ?']
		task_daily_data = [(daily_cost.gettask_id(), daily_cost.getcost_day(), 1, 1, daily_cost.getreserved()),\
							(daily_cost.gettask_id(),  daily_cost.getcost_day(), daily_cost.gettask_cost(), 1, 1, daily_cost.getreserved()),\
							(daily_cost.gettask_id(), 1, 1, daily_cost.gettask_id(), 1, 1)]
		if conn is not None:
			result = sqlite3_crud.save_trans(conn, daily_cost_sql, task_daily_data)
			if result == True:
				logger.debug('successfully add task_daily_cost(task_id:%s, cost_day: %s, task_cost: %s)',\
							daily_cost.gettask_id(), daily_cost.getcost_day(), daily_cost.gettask_cost())
				return True;
			else:
				logger.error('add task_daily_cost failed:task_id:%s, cost_day: %s, task_cost: %s',\
							daily_cost.gettask_id(), daily_cost.getcost_day(), daily_cost.gettask_cost())
		else:
			logger.error('add daily cost for task failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
		return False;

	def POST(self):
		forms = web.input()

		##TaskInfo
		task_info = data_element.TaskInfo()
		task_info.setid(forms.get('id').encode('UTF-8'))
		task_info.settask_id(forms.get('task_id').encode('UTF-8'))
		task_info.settask_name(forms.get('task_name').encode('UTF-8'))
		task_info.settask_effort(forms.get('task_effort').encode('UTF-8'))
		task_info.settask_status(forms.get('task_status'))
		task_info.settask_owner(forms.get('task_owner').encode('UTF-8'))
		task_info.settask_cost_id(forms.get('task_cost_id').encode('UTF-8'))

		##DailyCost info
		daily_cost = data_element.DailyCost()

		if task_info.gettask_status() == '0':
			save_result = self.update_task_info(task_info)
		else:
			daily_cost.settask_id(forms.get('task_id').encode('UTF-8'))
			daily_cost.setcost_day(forms.get('datepicker').encode('UTF-8'))         #input format:07/18/2015
			daily_cost.settask_cost(forms.get('task_cost').encode('UTF-8'))
			daily_cost.setreserved(forms.get('task_owner').encode('UTF-8'))
			save_result = self.add_task_daily_cost(daily_cost)

		executeMsg = 'update task successfully!' if save_result else 'update creation failed!'
		returnMSG = "<script type=\"text/javascript\">\
					setTimeout('window.opener.location.reload();', 1000);\
					setTimeout('window.close()', 1000);\
					</script><h3>" + executeMsg + "</h3>"
		return returnMSG

def update_task_status(task_keyid, task_new_status):
	sql_task_delete = 'update task_info set task_status = ? where id = ?'
	task_info_data = (task_new_status, task_keyid)
	conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
	save_result = sqlite3_crud.save(conn, sql_task_delete, task_info_data)
	if save_result == True:
		logger.info('successfully update task(keyid=%s) status to %s.', task_keyid, task_new_status)
	else:
		logger.error('failed update task(keyid=%s) status to %s.', task_keyid, task_new_status)
	return save_result

class DeleteTask:
	def POST(self):
		forms = web.input()
		task_key_id = forms.get('id').encode("UTF-8")
		
		save_result = update_task_status(task_key_id, task_status_deleted)
		if save_result == True:
			logger.info('successfully delete task : task_keyid = %s', task_key_id)
		else:
			logger.error('failed to delete task : task_keyid = %s', task_key_id)
		return save_result

class MoveTaskCard:
	def POST(self):
		forms = web.input()
		task_key_id = forms.get('id').encode('UTF-8')
		task_new_status = forms.get('new_status').encode('UTF-8')
		
		save_result = update_task_status(task_key_id, task_new_status)
		return save_result

def getTotalManHours(data):
	conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
	fetch_sql = 'select CASE WHEN sum(manhours) IS NULL THEN 0 ELSE sum(manhours) END as totol_hours, sprint_workday from team_manhours where team_id = ? and is_current = ?'
	if conn is not None:
		result = sqlite3_crud.fetch(conn, fetch_sql, data)
		if result is not None:
			logger.debug('successfully fetch total manhours = %d,totol workday = %d from team_manhours', result[0][0], result[0][1])
			return result;
	else:
		logger.error('get manhours failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
	return None

def getBurnedHoursGroupByDate(data):
	conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
	fetch_sql = 'select cost_day, sum(task_cost) totol_cost from daily_cost where is_current = ? and team_id = ? \
				 group by cost_day order by cost_day asc'
	if conn is not None:
		result = sqlite3_crud.fetch(conn, fetch_sql, data)
		if result is not None:
			logger.debug('successfully fetch %d datas from daily_cost', len(result))
			return result;
	else:
		logger.error('get burned manhours failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
	return None

class BurnDownChart:
	def GET(self):
		info = (1,1)
		result = getTotalManHours(info)
		if result is not None:
			totalHours = result[0][0]
			workday_count = result[0][1]
			x_axis_day_index = []
			ideal_burndown = []
			step_len = totalHours / workday_count
			for i in range(workday_count):
				#x_axis_day_index.append("%s%d"%(('Day', i+1)))
				x_axis_day_index.append(i+1)
				ideal_burndown.append(totalHours - (step_len*(i+1)))

			actualBurnedArray = []
			burnedHours = getBurnedHoursGroupByDate(info)
			for i in range(len(burnedHours)):
				tmpHours = totalHours - burnedHours[i][1]
				actualBurnedArray.append(tmpHours)
				totalHours = tmpHours
			return render.burndown_chart(x_axis_day_index, ideal_burndown, actualBurnedArray)
		else:
			return render.error_page('query task manhours failed.')

class YesterdayDid:
	def getRecentTask(self, data):
		conn = sqlite3_crud.get_conn(sqlite3_crud.DB_FILE_PATH)
		fetch_sql = 'select a.task_name,a.task_owner,b.cost_day,b.task_cost,b.reserved from task_info a,daily_cost b \
					 where a.is_current = ? and a.team_id = ? and a.task_id = b.task_id and b.cost_day <= \
					 (select max(cost_day) from daily_cost where is_current = ? and team_id = ?) order by b.cost_day desc, b.id desc'
		if conn is not None:
			result = sqlite3_crud.fetch(conn, fetch_sql, data)
			if result is not None:
				logger.debug('successfully fetch %d datas from task info and daily cost', len(result))
				for e in range(len(result)):
					names = queryMembers(result[e][1])
					tuple_names=names,
					result[e] = result[e] + tuple_names
					names_executer = queryMembers(result[e][4])  #reserved indicates the task executer
					tuple_names_executer=names_executer,
					result[e] = result[e] + tuple_names_executer
				return result
		else:
			logger.error('get task_info and cost failed:conn to db[%s] is None', sqlite3_crud.DB_FILE_PATH)
		return None


	def GET(self):
		data = (1,1,1,1)
		result = self.getRecentTask(data)
		if result is not None:
			return render.yesterday_did_page(result)
		else:
			return render.error_page('query yesterday task data failed.')

class ErrorPage:
	def GET(self):
		forms = web.input()
		info = forms.get('info')
		return render.error_page(info)

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
