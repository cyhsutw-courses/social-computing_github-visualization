import json
import urllib
import getpass
import sqlite3
from github import Github
from BeautifulSoup import BeautifulSoup as bsoup

GH = None

db_conn = sqlite3.connect('../db/user.db')
db_cursor = db_conn.cursor()

def download_users_and_parse(url):

    web_content = urllib.urlopen(url)
    html_data = web_content.read()
    web_content.close()

    data = bsoup(html_data).findAll('h2', attrs={'class':['user-leaderboard-list-name']})

    user_list = []
    for item in data:
        user_list.append(item.findAll('a')[0]['href'].replace('/', ''))

    with open('../output/trending-users.json', 'w') as output:
        json.dump(user_list, output)

    return user_list


def auth():
    #
    # Compose Request
    #
    uname = raw_input('Github username: ')
    passwd = getpass.getpass('Github password: ')

    gh = Github(login_or_token=uname, password=passwd, per_page=100)

    return gh


def insert_star_link(src, dst, rid):
    t = (src, dst, rid)
    db_cursor.execute('INSERT INTO star (source, target, repo) VALUES (?, ?, ?)', t)
    db_conn.commit()

def insert_cowork_link(repo, worker):
    t = (repo, worker)
    db_cursor.execute('INSERT INTO contributor (repo, worker) VALUES (?, ?)', t)
    db_conn.commit()


def insert_user(uid, username):
    t = (uid, username)
    db_cursor.execute('INSERT INTO user (id, name) VALUES (?, ?)', t)
    db_conn.commit()

def fetch_contributors(repo, user_list):
    print '\t\tfetching ' + repo.full_name
    contri = set()
    try:
        c_list = repo.get_contributors()
        for worker in c_list:
            contri.add(worker.login)

        contri = contri.intersection(user_list)

        return list(contri)
    except:
        print '==========EXCEPTION!=========='
        return list(contri)




if __name__ == "__main__":

    GH = auth()

    t_users = set()

    time_ranges = ['daily', 'weekly', 'monthly']

    print 'Loading users...'
    for time_range in time_ranges:

        url = 'https://github.com/trending/developers?since='+time_range+'&l=objective-c'
        print '\t'+url
        ulist = download_users_and_parse(url)
        t_users = t_users.union(set(ulist))


    all_users = {}
    all_users_list = set()
    all_repos = {}
    all_orgs = set()

    rate_t = GH.rate_limiting
    print '---------- API calls: ' + str(rate_t[0]) + ' / ' + str(rate_t[1]) + '----------'

    user_cnt = 1
    for uname in t_users:
        user = GH.get_user(uname)
        if user.type == 'User':
            insert_user(user_cnt, user.login)
            all_users[user.login] = {
                'id':user_cnt
            }
            all_users_list.add(user.login)
            user_cnt += 1



    print '#user = ' + str(len(all_users))

    with open('../output/user.json', 'w') as f:
        json.dump(all_users, f)

    print '=========================STAR========================='
    for login in all_users:
        user = GH.get_user(login)
        print '@' + login

        starred = user.get_starred()
        print '\tstars: '

        for star in starred:

            if star.full_name not in all_repos:
                all_repos[star.full_name] = fetch_contributors(star, all_users_list)

            print '\t\t' + star.full_name + ' => #contributors: ' + str(len(all_repos[star.full_name]))

            inter = all_repos[star.full_name]
            for tar in inter:
                if tar != login:
                    src_id = all_users[login]['id']
                    dst_id = all_users[tar]['id']
                    insert_star_link(src_id, dst_id, star.full_name)
                    print '\t\t\tlinks to ' + tar

        print '---------- API calls: ' + str(rate_t[0]) + ' / ' + str(rate_t[1]) + '----------'
        if rate_t[0] <= 800:
            print 'RUNNING OUT OF QUOTA...'
            GH = auth()

        u_repos = user.get_repos()
        print '\trepos: '

        for repo in u_repos:
            if repo.full_name not in all_repos:
                all_repos[repo.full_name] = fetch_contributors(repo, all_users_list)

            print '\t\t' + repo.full_name + ' => #contributors: ' + str(len(all_repos[repo.full_name]))

        rate_t = GH.rate_limiting
        print '---------- API calls: ' + str(rate_t[0]) + ' / ' + str(rate_t[1]) + '----------'
        if rate_t[0] <= 800:
            print 'RUNNING OUT OF QUOTA...'
            GH = auth()

    for login in all_users:
        user = GH.get_user(login)
        print '@' + login
        orgs = user.get_orgs()
        print '\torgs: '
        for org in orgs:
            print '\t\t' + org.login

            if org.login not in all_orgs:
                o_repos = org.get_repos()
                print '\t\t\trepos: '
                for repo in o_repos:
                    if repo.full_name not in all_repos:
                        all_repos[repo.full_name] = fetch_contributors(repo, all_users_list)

                    print '\t\t\t\t' + repo.full_name + ' => #contributors: ' + str(len(all_repos[repo.full_name]))

                all_orgs.add(org.login)

        rate_t = GH.rate_limiting
        print '---------- API calls: ' + str(rate_t[0]) + ' / ' + str(rate_t[1]) + '----------'
        if rate_t[0] <= 800:
            print 'RUNNING OUT OF QUOTA...'
            GH = auth()

    with open('../output/repos.json', 'w') as f:
        json.dump(all_repos, f)

    print '========================COWORK========================'



    for key in all_repos.keys():
        contributors = all_repos[key]
        for contributor in contributors:
            user_id = all_users[contributor]['id']
            insert_cowork_link(key, user_id)
            print contributor + ' => ' + key



    '''
    all_langs = {}
    all_users = []

    for uname in t_users:
        user = GH.get_user(uname)

        if user.type == 'User':

            repos = user.get_repos()
            main_lang = get_main_lang(repos)

            if main_lang == None:
                continue;

            followers = user.get_followers().get_page(0)

            if main_lang not in all_langs:
                all_langs[main_lang] = insert_lang(main_lang)
                print '#' + str(all_langs[main_lang]) + ' ' + main_lang

            if user.login not in all_users:
                all_users.append(user.login)
                userid = len(all_users)
                insert_user(userid, user.login, all_langs[main_lang])

                print 'Insert user: '+user.login

            for fl in followers:
                fl_repos = fl.get_repos()
                fl_main_lang = get_main_lang(fl_repos)
                if fl_main_lang == None:
                    continue;



                if fl_main_lang not in all_langs:
                    all_langs[fl_main_lang] = insert_lang(fl_main_lang)
                    print '#' + str(all_langs[fl_main_lang]) + ' ' + fl_main_lang

                if fl.login not in all_users:
                    all_users.append(fl.login)
                    fl_userid = len(all_users)
                    insert_user(fl_userid, fl.login, all_langs[fl_main_lang])
                    print 'Insert user: '+fl.login

                fluid = all_users.index(fl.login)+1
                uuid = all_users.index(user.login)+1
                insert_link(fluid, uuid)
                print 'Add link: ' + fl.login + ' => ' + user.login

            followings = user.get_following().get_page(0)


            for fl in followings:
                fl_repos = fl.get_repos()
                fl_main_lang = get_main_lang(fl_repos)
                if fl_main_lang == None:
                    continue;



                if fl_main_lang not in all_langs:
                    all_langs[fl_main_lang] = insert_lang(fl_main_lang)
                    print '#' + str(all_langs[fl_main_lang]) + ' ' + fl_main_lang

                if fl.login not in all_users:
                    all_users.append(fl.login)
                    fl_userid = len(all_users)
                    insert_user(fl_userid, fl.login, all_langs[fl_main_lang])
                    print 'Insert user: '+fl.login

                fluid = all_users.index(fl.login)+1
                uuid = all_users.index(user.login)+1
                insert_link(uuid, fluid)
                print 'Add link: ' + user.login + ' => ' + fl.login

'''





##
