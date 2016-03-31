#coding:utf-8
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .forms import buildForm

def index(request):
    return HttpResponse('HW!!')

def home(request):
    return render(request, 'home.html')

def build(request):
    form = buildForm()
    return render(request, 'build.html', {'form': form})

def project(request):
    PROJECTS = [
        {'project': '43P', 'version': '0315_MP','buglist':[{"ID":"560","linked":"http://172.20.0.66/redmine/issues/560"}]},
    ]
    issues = sql()
    issues_list = issues.GetAllProjectsIssues()

    print "--success-- %s" %issues_list
    '''
    '''
    return render(request, 'projectdelay.html', {'projects':issues_list})




import MySQLdb


class sql:

    db = ""
    cursor = ""

    def __init__(self):
        self._connect()

    def _connect(self):

        global  db
        db = MySQLdb.connect("localhost", "root", "xulei", "redmine_default")

    def _query(self, sql):

        global cursor, db
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            db.close

    def GetLastedVesionByProjects(self, project_id):

        project_version = []
        global db
        cursor = db.cursor()
        cursor.execute('select id from versions where project_id=%s order by effective_date asc' %(project_id))
        datas = cursor.fetchall()

        for data in datas:
            print 'data[0]:' + str(data[0])

            if int(self.GetVersionCustomValueByColumn(data[0], 'build')) == 1:
                print 'continue'
                continue
            project_version.append(project_id)
            project_version.append(data[0])
            break;
        cursor.close()
        return project_version

    def GetProjectsByVersion(self):
        projects = []
        global db
        cursor = db.cursor()
        cursor.execute('select distinct project_id from versions')
        datas = cursor.fetchall()
        for data in datas:
            projects.append(data[0])
        cursor.close()
        print projects
        return projects


    def GetEachVersionIssues(self, project_id, version_id):

        open_id = self.getOpenId()
        project_issues = {}
        global db
        cursor = db.cursor()
        cursor.execute('select id,status_id from issues where project_id=%s and fixed_version_id =%s' %(project_id, version_id))

        datas = cursor.fetchall()

        buglist = []
        for data in datas:
            if data[1] == open_id:
                bug = {}
                bug['ID'] = data[0]
                bug['linked'] = 'http://192.168.33.43/redmine/issues/%s' %(data[0])
                bug['owner']= self.GetOwnerByIssueID(data[0])
                print bug['owner']
                buglist.append(bug)

        project_name = self.GetNameByProjectID(project_id)
        version_name = self.GetNameByVersionID(version_id)
        project_issues['project'] = project_name
        project_issues['version'] = version_name
        project_issues['buglist'] = buglist

        cursor.close()
        if len(buglist) > 0 :
            return project_issues
        else:
            return None


    def GetAllProjectsIssues(self):

        all_projects_id = self.GetProjectsByVersion()
        all_pro_ver = []
        all_pro_issues = []
        for project_id in all_projects_id:
            all_pro_ver.append(self.GetLastedVesionByProjects(project_id))

        for i in all_pro_ver:
            project_issues = self.GetEachVersionIssues(i[0], i[1])
            if project_issues != None:
                all_pro_issues.append(project_issues)

        return all_pro_issues

    def getOpenId(self):
        global db
        cursor = db.cursor()
        cursor.execute('select id from issue_statuses where name = "New"')
        datas = cursor.fetchall()
        cursor.close()
        return datas[0][0]


    def GetNameByVersionID(self, version_id):
        global db
        cursor = db.cursor()
        cursor.execute('select name from versions where id = "%s"' %(version_id))
        datas = cursor.fetchall()
        cursor.close()
        return datas[0][0]

    def GetNameByProjectID(self, project_id):
        global db
        cursor = db.cursor()
        cursor.execute('select name from projects where id = "%s"' %(project_id))
        datas = cursor.fetchall()
        cursor.close()
        return datas[0][0]

    def GetOwnerByIssueID(self, issues_id):
        global db
        cursor = db.cursor()
        cursor.execute('select mail from users where id = (select assigned_to_id from issues where id = %s)' %(issues_id))
        datas = cursor.fetchall()
        cursor.close()
        return datas[0][0]


    def GetVersionCustomValueByColumn(self, version_id, column):

        id = self.GetIdFromVersionCustomFields(column)
        global db
        print 'version_id:' + str(version_id)
        cursor = db.cursor()
        cursor.execute("select value from custom_values where custom_field_id =%s and customized_id = %s and customized_type = 'Version'" %(id, version_id))
        datas = cursor.fetchall()
        cursor.close()
        return datas[0][0]

    def GetIdFromVersionCustomFields(self, column):
        global db
        cursor = db.cursor()
        cursor.execute("select id from custom_fields where name='%s' and type='VersionCustomField'" %(column))
        datas = cursor.fetchall()
        cursor.close()
        return datas[0][0]